# Nitemare 3D — PASS 027: parser wrapper and diagnostic termination chain

Date: 2026-11-05

Input: statically reconstructed DOS 2.0 relocated expanded image (synthetic base `0x1000`), SHA-256 `ad4f4c3104475118c8c318bcb6df8748d3b8736476d90bd36c9b4a2225341d38`. Bytes decoded via GNU objdump i8086. This is **not** independently CPU-emulated original-loader output.

## `21EE:27E4` (image `0x146C4..0x14701`, 62 bytes)

The wrapper sets `[3CA6]=0x49`, stores its input word into `[3CA4]` and `[3CA0]`, calls `21EE:2398`, stores returned AX in `[3CA2]`, then passes three word arguments to nested scanner `21EE:0D36` and forwards the latter return AX. It exits with `RETF` at `0x14701`. The nested scanner begins at `0x12C16` with substantial format-processing logic; we have **not proven** whether it allows signed-negative numeric input.

## `1FBA:000C` (image `0xFBAC..0xFBD4`, 41 bytes)

Decoded FAR call chain `1476:0192` → `21EE:285A` → `21EE:07E0` (output) → `21EE:01EB` (shutdown), the last called with immediate argument 1. Although a trailing `LEAVE; RETF` is encoded, it does not prove normal return.

## `21EE:01EB` (image `0x120CB..0x12151`)

The entry selects `CX=0`; its shared cleanup contains an indirect callback `CALL DWORD PTR DS:[2542]` conditional on `[2544] != 0`. After the cleanup, expected balanced execution reaches `MOV AH,4Ch; INT 21h` (`0x1214A..0x1214C`), the DOS terminate service. **Nonreturn is conditional** on ordinary DOS semantics, proper stack and callback behavior; a `RETF` exists at `0x12151` for alternate or exceptional paths.

## Consequences for dynamic palette arguments

The out-of-range/error branches at `0xE3F4` and `0xE430` call `1FBA:000C`. Under the above conditions they terminate before continuing to color mapping. But successful signed `JLE 15` comparisons at `0xE3F2` and `0xE42E` do not exclude negative values. Until nested `21EE:0D36`, the format strings and calling context are fully analyzed, negative-input reachability and memory safety remain **unknown**, not established bugs.

## Audit scope

Five local ASM windows; **206 extracted instruction records**. Detailed source, per-instruction CSV and three function records are in the downloadable `N3D_FUNCTION_RESEARCH_PASS027.zip` (including `PASS027_REPORT.md`, `PASS027_INSTRUCTIONS.csv`, and `build_pass027.py`). No new gameplay runtime tests; no historical global overlap pair closed (0/19). No copyrighted original EXE/image committed.
