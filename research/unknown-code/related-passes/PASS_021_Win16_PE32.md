# Nitemare 3D Win16 1.10 — Pass 21 (Windows PE32 migration)

## Direct findings from origin

- SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.
- NE CODE2 base: `0xE8A0`; offsets below are *segment-relative*.
- `2:5AB0` starts a routine whose first instructions establish BP frame and normalize size zero to one.
- In the routine, `2:5AC7` is `9A 5D 5B 00 00` (`CALL FAR 0000:5B5D`) and `2:5ADF` is `9A 85 5B 00 00` (`CALL FAR 0000:5B85`) **as stored on disk**.
- `2:5AD3` is a loader-relocated import CALL (Win16 `LocalAlloc`, `KERNEL` ordinal 5).
- The two suspicious calls are *in the straight-line path*, before/after `LocalAlloc`, whenever execution reaches `5AC3` through the regular entry. This makes them relevant, not stray `9A` byte matches.
- `2:5AE4` tests allocation result; `2:5AE8 JNE 5B01` skips retry on success. `2:5AF6 CALL FAR [DS:094A]` invokes a user-supplied callback if present. `2:5AFF JNE 5AC3` loops for another attempt when callback returns nonzero.
- The apparent targets `2:5B5D` and `2:5B85` are the second bytes of `CALL FAR` instructions at `2:5B5C` and `2:5B84` respectively. Without runtime modification, the stored targets would decode in the middle of operands.
- Neither suspicious caller's immediate operand has a matching *direct* NE relocation or a standard internal selector fixup chain in the audited tables.

## Key limit

The disk bytes and conventional NE fixups do **not** establish the effective runtime targets. Do not assert self-modifying code or translate `5B5D`/`5B85` as function labels without a Win16 runtime trace. An alternate or custom fixup mechanism remains possible. Our previous 72/72 Windows PE32 diagnostic success validates only that experimental test harness, not this unknown Win16 behavior.

## Next runtime test on a real Win16 environment

1. Break at `CS=CODE2`, `IP=5AC7` and `5ADF`; record `CS:IP`, actual five instruction bytes, `SS:SP`, `DS`, `AX`, `BP`, and effective target selector:offset after the call.
2. Set write watchpoints on `CODE2:5AC8–5ACB`, `CODE2:5AE0–5AE3` and (to test target-code patching) `CODE2:5B5D–5B60`, `CODE2:5B85–5B88`.
3. On failure log `DS:[094A]` (offset) and `DS:[094C]` (selector), then trace whether callback requests a retry.
4. Compare pre-call bytes to original disk bytes after NE loader fixups. Resolve any custom writer before replacing these calls in ASM32.

## Outputs

- `n3d_pass21_analyze.py`: independent reproducible audit
- `n3d_pass21_audit.json`: annotated site records and raw reference candidates
- `n3d_pass21_sites.csv`: compact call site inventory
- `pass21_code2_5a90_5bb0.bin`: relevant executable slice, offset origin `0x5A90`

No new PE32 executable was built in Pass 21 because the two unknown call targets must not be guessed.