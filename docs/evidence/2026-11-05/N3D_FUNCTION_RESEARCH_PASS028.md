# Nitemare 3D — PASS 028: %i signed conversion and palette index path

Date: 2026-11-05

## Primary byte provenance
Source: original DOS v2.0 packed `N3D-E-20.EXE` from user-provided archive; the statically reconstructed synthetic load-base-0x1000 image is re-read from the cumulative PASS027 ZIP. It is **171,360 bytes**, SHA256 `ad4f4c3104475118c8c318bcb6df8748d3b8736476d90bd36c9b4a2225341d38`. This image is *not* independently CPU-emulated original unpacker output.

New PASS028 independently inspected **18 instruction byte anchors**, resolved two original format-string contents and decoded the scanner's actual character-dispatch table.

## Exact strings and candidate DS mapping
Two input sites use DOS 2.0 data offsets `DS:1D04` and `DS:1D3A`, each decoding as `%i`. The corresponding error-format text at `DS:1D07` and `DS:1D3D` starts `Bad color code in instr`.

The four strings align consistently with **relative data segment 0x2771** inside the relocated synthetic image:
- `DS:1D04` → image `0x29414` → `%i`
- `DS:1D07` → image `0x29417` → `Bad color code in instr...`
- `DS:1D3A` → image `0x2944A` → `%i`
- `DS:1D3D` → image `0x2944D` → `Bad color code in instr...`

This is a **four-site address/data correspondence**, not an independent runtime trace of the DS register.

## Direct signed-conversion dispatch
The `21EE:0D36` scanner enters image offset `0x12C16`. At `0x133F7` it uses `JMP WORD PTR CS:[BX+151Ch]` with index `2*(format_char-'c')`. In the actual little-endian jump table:
- `'i'` index 6 → entry CS offset `0x10C6` → image **0x12FA6**;
- `'d'` index 1 → CS offset `0x1152` → image **0x13032**.

The `%i` target explicitly initializes `DI='d'` and accepts optional sign:
```asm
12FA6: MOV DI,0064h
12FA9: CMP SI,002Dh       ; '-'
12FAC: JNE 12FB4
12FAE: INC BYTE [BP-01A4h] ; negative flag
12FB4: CMP SI,002Bh       ; '+'
```

After digit processing, the negative flag controls 32-bit two's-complement negation of the accumulated DX:AX pair:
```asm
13183: CMP BYTE [BP-01A4h],0
13188: JE 13197
1318A: NEG WORD [BP-0182h]
1318E: ADC WORD [BP-0180h],0
13193: NEG WORD [BP-0180h]
```
With non-long conversion the scanner writes the low word to the caller-supplied destination using `MOV WORD PTR ES:[BX],AX` at `0x131E0`. The string `%i` selects the signed-capable scanner path. This is **new machine-code evidence for negative-number handling**, stronger than a generic expectation based on the format character alone.

## Connection to palette calls
The two color-code callers check only signed `<=15`:
- `E3EE CMP WORD [BP-4],0Fh; E3F2 JLE E403; E405 MOV AL,[BP-4]; E409 CALL FAR 1277:0188`.
- `E42A CMP WORD [BP-6],0Fh; E42E JLE E43F; E43F MOV AL,[BP-6]; E443 CALL FAR 1277:0188`.

**Conditional counterexample:** if scanner succeeds in parsing `-1`, its low 16-bit value is `0xFFFF`, which satisfies signed `JLE 15`; then `MOV AL` yields `0xFF`. Previously decoded palette helper indexes its 16-entry mapping table using the low byte. This would access **outside that 16-entry table**, though not necessarily outside an allocated memory segment. Real runtime behavior and all error/callback paths have **not** been tested; a reachable gameplay memory violation is not proven.

## Remaining P0
1. Validate actual runtime DS at these sites and where the format strings originated.
2. Verify scanner return `AX=1` on `-1` with a controlled CPU/runtime emulation, including its input helper and all stack paths.
3. Determine whether instruction text source reaches these parsing branches with negative tokens.
4. Test `-1`, `-16`, `0`, `15`, `16` on original and remake and compare the first table lookup, no-input corruption assumptions.
5. Complete caller CFG and palette table bounds.

New DOSBox-X gameplay runtime tests: **0**; historical overlap conflicts globally closed: **0/19**; complete-function verification metrics not increased. Detailed script, byte anchors, string table, dispatch and derived test vectors are in `N3D_FUNCTION_RESEARCH_PASS028.zip`.
