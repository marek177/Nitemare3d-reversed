# Nitemare3D Win16 1.10 — Ghidra12.2 pass22

## Finding

Executed the original post-load deadline-repair fragment in8192 controlled cases. Confirmed exact unsigned deadline comparison, signed array counts and modulo32 adjustment. The fragment leaves the complete336-byte projectile pool and4-byte RNG state unchanged. This is original-fragment verification with a supplied stack frame and clock stub, not a full save-file load or first-frame test.

Input `nite3w - 110.exe`,230400 bytes,SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Ghidra12.2 PUBLIC20261016,JDK25.0.2; Unicorn2.1.4.

## Original fragment and behavior

Confirmed / High,1010:5AF4..5B80 inside574C. CallsD6C6 once, stores returned DX:AX as nowClock in locals, then visits two28-byte record arrays. Counts are signed WORDs DS:7E56 and7E58. Nonpositive counts skip their array.

| Array | Base | Deadline field |
|---|---|---|
| First |1040:0006 | record+8 DWORD |
| Second |1040:6D66 | record+8 DWORD |

Each visited record uses unsigned32 comparison with savedClock at entry frame BP-1Eh:

    if oldDeadline < savedClock:
        newDeadline =0
    else:
        newDeadline =(oldDeadline + nowClock - savedClock) mod2^32

Equality takes adjustment, so oldDeadline==savedClock becomes nowClock, including old0/saved0. Older values become0 rather than nowClock. There is no saturating cap on adjustment and no elapsed-time wrap-safe comparison. Extreme clock fixtures characterize the literal arithmetic, not ordinary uptime reachability.

First loop temporarily changes DS to1040. Its repeated count read uses SS:7E56, then it restores DS with PUSH SS/POP DS. The harness therefore supplies DS=SS, matching this fragment's data/stack-group convention. Ignoring that instruction detail would produce a different second-loop environment.

## Original-code test setup

The harness loads original EXE bytes, applies internal NE selector fixes and compares44 instruction encodings with the Ghidra listing. For controlled real-mode memory it relocates only the test code selector to2000, keeping original data selectors and DS=SS=1048. This separates code from the supplied record/stack fixtures; it is not a reconstruction of Windows protected-mode descriptor tables.

Entry BP frame and record arrays are supplied by the harness. The D6C6 call is a RETF stub returning selected nowClock in DX:AX; its unrelated global clock writes are excluded. Execution stops before5B81's B128 call. No instructions of the comparison/addition loops are stubbed.

8192 cases combine eight values for oldDeadline, savedClock and nowClock with each array count-1,0,1,2. Values include0,1,FFFFh,10000h,7FFFFFFFh,80000000h,FFFFFFFEh andFFFFFFFFh. Adjacent records use distinct deadlines. Assertions compare complete84-byte array fixtures, so nondeadline bytes and the sentinel beyond the visited records must remain intact. Returned DS, unchanged SP, one clock call and arrival at the stop point are also checked.

All336 bytes at DS:4C4A and all4 bytes at DS:0A90 were marked before each run and checked unchanged afterwards. This confirms pass21's local projectile/RNG asymmetry for the executed fragment. It does not prove that earlier loader code, B128, later callers or the first game update leave them unchanged.

## Boundary examples

| Old deadline | Saved clock | Now clock | New deadline |
|---|---|---|---|
| 0 | 1 | any tested value |0 |
| savedClock | savedClock | nowClock |nowClock |
| FFFFFFFFh | FFFFFFFEh |1 |2 |
| 10000h | FFFFh |0 |1 |

The projectile deadlines remain governed by their stored values until other code changes them; this fragment does not apply the above formula to them. Combining this with9E20's absolute clock comparison still requires real load/caller traces before asserting an actual animation jump or delay.

## Ghidra and coverage

Added verified fragment evidence to574C, completed full native export and saved the project. Internal functions remain1551, all1551 decompilations completed;310 EXTERNAL-block entries tracked separately. Coverage remains160005 instruction bytes,8282 data bytes,1401 undefined bytes. No EXE changes, new functions or padding classification.

## Unknowns and next test

Execute the complete loader with real save bytes and I/O, then include B128 and the next dispatcher call. Capture both record-array counts, real segment conventions, clock values and projectile deadlines. Trace actual seed changes across all callers and check the first rendered frame. Malformed counts, invalid pointers, partial reads and complete first-frame/RNG restoration parity remain unresolved. Full-game runtime tests:0.

## Confidence

High for the bounded original deadline-repair instructions and unchanged marked regions. Full save/load and runtime consequences remain open.
