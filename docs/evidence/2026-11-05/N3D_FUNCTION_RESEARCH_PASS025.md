# Nitemare 3D — PASS 025: DOS20 palette call argument and stack audit

Date: 2026-11-05

## Evidence basis
The synthetic relocated DOS2 expanded image from PASS018 was re-read, SHA-256 `ad4f4c3104475118c8c318bcb6df8748d3b8736476d90bd36c9b4a2225341d38`. 70 exact machine-byte occurrences of `9A 88 01 77 12 83 C4 02` were classified from preceding argument bytes. Original packed EXE SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.

**New precise result:** Of 70 raw candidates, **68 have directly encoded low-word argument indices in [0,15]**: 36 `6A imm8` (sign-extended 16-bit PUSH) and 32 `66 68 imm32` (32-bit PUSH, low WORD contains index). Other 2 are `PUSH AX` at image offsets `0xE409` and `0xE443`; their low-byte range is not proven globally.

All 32 four-byte `PUSH` immediate values have **high word 0x0001**. Do not describe the call itself as consuming all four bytes: `CALL FAR 1277:0188` returns and caller removes **2 bytes**. The remaining high word is used as part of subsequent call argument expressions on examined straight-line paths.

## Three local stack-balance witnesses

### 0x83D8–0x83EF
```asm
83D8: 66 68 01 00 01 00  PUSH DWORD 00010001
83DE: 9A 88 01 77 12     CALL FAR 1277:0188
83E3: 83 C4 02           ADD SP,2
83E6: 50                 PUSH AX
83E7: 9A 3A 0A 56 11     CALL FAR 1156:0A3A
83EC: 83 C4 04           ADD SP,4
```
Extra argument depth progression (bytes): 0→4→2→4→0, assuming FAR calls return with their own return addresses balanced.

### 0x83F9–0x841A
`PUSH DWORD 0001000E`, palette FAR call, `ADD SP,2`, then `PUSH AX; PUSH DS; PUSH 139E; PUSH DWORD 0028FFFF; CALL FAR 1D29:0116; ADD SP,12`. Extra argument depth returns to zero.

### 0x8A38–0x8A67
`PUSH DWORD 00010000`, first palette call, `ADD SP,2`, `PUSH AX; PUSH 0B`, second palette call, `ADD SP,2`, `PUSH AX`, additional address/data arguments, `CALL FAR 1D29:024C; ADD SP,10h`. Again extra argument depth returns to zero.

These are **local byte-decoded straight-line examples**, not complete alternate-edge or runtime stack verification. Raw matches must still be established as executable CFG call sites.

## Open blockers
- Exact origins/constraints of `AL` from local `[BP-4]` and `[BP-6]` before the two `PUSH AX` calls at `0xE409/0xE443`.
- Global CFG reachability of the 70 pattern matches, and nested-callee side effects.
- Full cross-version instruction diff and original runtime parity tests.
- All 19 historical overlap conflicts remain globally unresolved.

Reproducible artifacts in `N3D_FUNCTION_RESEARCH_PASS025.zip`: `PASS025_CALLSITE_ARGUMENT_AUDIT.csv`, `PASS025_STACK_TRACES.csv`, three actual local objdump ASM files, `PASS025_SUMMARY.json`, `PASS025_REPORT.md`, and `pass025_build.py`. Original copyrighted binaries are not committed to GitHub.
