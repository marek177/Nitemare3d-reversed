# Nitemare 3D — PASS 023: DOS 2.0 FAR 1277:0188 per-function reconstruction

Date: 2026-11-05

## Evidence
Reused synthetic relocated DOS 2.0 expanded image, SHA-256 `ad4f4c3104475118c8c318bcb6df8748d3b8736476d90bd36c9b4a2225341d38`, reconstructed from original packed DOS2 binary in PASS018. Independently decoded *instructions* using GNU objdump i8086, but did **not** independently CPU-emulate the packed original loader, so all byte-level assertions are conditional on the reconstructed image.

### Function 1277:0188
- Image offset `0x28F8`, decoded interval `[0x28F8, 0x2A16)`, **286 bytes**, **112 instruction starts**.
- **14 syntactic basic blocks**, **8 direct branch sites**, **3 FAR call sites** (`0x29A1`, `0x29B9`, `0x29D0`) and a single `RETF` at `0x2A15`.
- Entry `C8 10 00 00 57 56` = `ENTER 10h,0; PUSH DI; PUSH SI`. Exit `5E 5F C9 CB` = `POP SI; POP DI; LEAVE; RETF`.
- Reads a cache/recompute flag at `DS:[0244]`; if nonzero, clears it, loops 16 reference triplets and scans 256 3-byte entries beginning at `DS:[4A64]`.
- For each reference, computes three squared channel differences and selects minimum using **signed 16-bit comparison** (`CMP AX,[BP-4]; JGE skip`), writing selected index byte to `DS:[3456+DX]`. Fast/cache lookup returns `AL=DS:[3456+zero_extend(low_byte(parameter))]`.
- On `DX=6` reference triplet is `(0x2A,0x15,0)`. Remaining `DX<8` use bitwise 0 or `0x2A` per channel; `DX>=8` use per-channel `0x15` or `0x3F`.
- Corrected pseudocode must explicitly maintain 16-bit wraps and signed score comparisons. Neither caller-enforced argument range nor palette source input range has been proven. The exact memory region interpretation is provisional.

### Resolved helper FAR 1FBA:010C
- Synthetic image offset `0xFCAC`; **12 bytes**, **7 instructions**.
- Exact bytes: `55 8B EC 8B 5E 06 8B C3 F7 EB C9 CB`.
- `PUSH BP; MOV BP,SP; MOV BX,[BP+6]; MOV AX,BX; IMUL BX; LEAVE; RETF`. Produces signed 32-bit `DX:AX`; caller uses AX (low 16 bits) and removes the WORD argument with `ADD SP,2`.
- Helper clobbers BX/DX and affects arithmetic flags. The three call sites use the helper's AX result to form squared-distance cost.

## What is not complete
- The bounded CFG assumes helper returns; global incoming edges and indirect aliases were not fully audited.
- Runtime verification of table contents and exact color/palette semantics was not executed.
- No Ghidra RAW pseudocode for the full function is claimed; corrected pseudocode is **newly derived from disassembly**.
- **0/19** historical global overlap warnings closed; **0** gameplay runtime tests this pass.

## Private detailed artifacts
The downloadable conversation artifact `N3D_FUNCTION_RESEARCH_PASS023.zip` contains `PASS023_INSTRUCTIONS.csv`, `PASS023_HELPER_INSTRUCTIONS.csv`, `PASS023_CFG.json`, `PASS023_DATAFLOW.json`, `PASS023_CORRECTED_PSEUDOCODE.md`, ASM outputs, `PASS023_REPORT.md` and `build_pass023.py` plus historical reports. Original expanded game binary is not published to GitHub.
