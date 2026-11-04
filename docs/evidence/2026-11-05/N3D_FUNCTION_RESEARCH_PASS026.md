# Nitemare 3D — PASS 026: DOS 2.0 dynamic color-index argument provenance

Date: 2026-11-05

## Evidence and exact byte provenance
Continued from `PASS025`. Re-read expanded DOS 2.0 image SHA-256 `ad4f4c3104475118c8c318bcb6df8748d3b8736476d90bd36c9b4a2225341d38` and directly checked **20 instruction-byte anchors** with GNU objdump i8086. The expanded image was statically reconstructed from original packed EXE, not independently CPU-emulated.

## Dynamic FAR call at 0xE409
- `E3D8 LEA AX,[BP-4]` supplies a parse-result address to `E3E3 CALL FAR 21EE:27E4`.
- `E3EB DEC AX / E3EC JNE E3F4` branches to a diagnostic path on non-success.
- `E3EE CMP WORD [BP-4],000F`; `E3F2 JLE E403` permits signed values **<=15**, without a local lower-bound test.
- The fallback at `E3F4` invokes `1FBA:000C`; its return/non-return behavior is **unknown**.
- `E405 MOV AL,BYTE [BP-4]`; `E408 PUSH AX`; `E409 CALL FAR 1277:0188`; `E40E ADD SP,2`.

## Dynamic FAR call at 0xE443
- `E414 LEA AX,[BP-6]` supplies another parse-result address to `E41F CALL FAR 21EE:27E4`.
- `E427 DEC AX / E428 JNE E430` checks the parser return.
- `E42A CMP WORD [BP-6],000F`; `E42E JLE E43F` again imposes only a **signed upper bound**.
- The fallback invokes diagnostic `1FBA:000C` at `E437`; its effect is unresolved.
- `E43F MOV AL,BYTE [BP-6]`; `E442 PUSH AX`; `E443 CALL FAR 1277:0188`; `E448 ADD SP,2`.

## Additional route to 0xE443
`E44E PUSH 8`; `E450 JMP E443` reaches the **same call instruction** with an immediate, proven-in-range index 8, bypassing the register-sourced `PUSH AX`.

The local control-flow dispatch preceding these paths includes byte-specifier checks `0x62`, `0x63`, and `0x64`, consistent with format-specifier handling. Full producer semantics are provisional.

## Consequences
- Two register-sourced call locations do **not** mean only two possible argument-producing paths: `E443` has an additional constant-8 entry path.
- Neither `JLE` check alone proves `0 <= input <= 15`. If parsing accepts negative input, its low byte may lie outside the 16-entry mapped-index table; **runtime memory violation is not proven** because parser and diagnostic behavior remain unknown.
- The color-mapper's low-byte lookup is documented in PASS023; do not confuse a potentially uncontrolled upper AX byte with the actual indexing byte.
- All these are machine-byte *local* paths, not a global callgraph reachability proof.

## Status
- 20 exact byte anchors directly verified.
- Original gameplay runtime tests: **0** this pass.
- Globally closed Ghidra overlap conflicts: **0/19**.
- No whole function marked complete.

The conversation artifact `N3D_FUNCTION_RESEARCH_PASS026.zip` includes `PASS026_MACHINE_ANCHORS.csv`, `PASS026_ARGUMENT_DATAFLOW.csv`, `PASS026_ANCHORED_I8086.asm`, `PASS026_REPORT.md`, `PASS026_SUMMARY.json`, and `pass026_build.py` plus cumulative prior reports. Original proprietary game binaries were **not** committed.
