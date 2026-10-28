# Nitemare3D Win16 1.10 — Ghidra12.2 pass20

## Finding

Recovered exact death/reaction variant selection and executed their original RNG chain. Selection tests the high byte of frame WORDs, may choose variant7 without RNG, and otherwise consumes a variable number of RNG calls through rejection. Original generator and multiplication helper agree with a32-bit LCG model. This resolves previously stubbed behavior locally, not complete death/render/demo parity.

Input `nite3w - 110.exe`,230400 bytes,SHA256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. Ghidra12.2 PUBLIC20261016,JDK25.0.2; Unicorn2.1.4 isolated original-instruction execution.

## Selector behavior

Confirmed / High,B94E and B9B2. Both obtain descriptor near pointer from DS:[4748h+object.byte4*8]. Actor and object are supplied far pointers. Actor.byte12h is the field written8 on surviving positive damage in pass19.

| Selector | Special variant7 flag | Random availability bytes | Caller frame WORDs |
|---|---|---|---|
| B94E death | descriptor+59h | descriptor+4Bh+2*i | +4Ah+2*i |
| B9B2 reaction | descriptor+49h | descriptor+3Bh+2*i | +3Ah+2*i |

If actor.byte12h==0 and special byte!=0, return7 immediately, consuming no RNG. Otherwise call32D2, signed-divide result by7, retain remainder i. A comparison rejects i==7; this cannot occur for the generator's0..32767 domain. Return i only if its availability byte is nonzero, else repeat.

These bytes are the HIGH bytes of their corresponding WORD frame identifiers. A WORD00FFh is treated unavailable, while0100h is available. The selector does not compare the entire WORD to zero. Random path never selects7; it is restricted to residues0..6. No retry limit, fallback variant or descriptor validity check is present locally.

For an unchanged descriptor with all seven availability bytes zero and the special bypass unavailable, no random residue can satisfy the return test.42 bounded fixtures exercised that condition with controlled stub streams and stopped at the test harness limit; this does not claim that ordinary assets contain such an invalid descriptor or that an actual game hang was observed.

## Original RNG chain

Confirmed / High,1018:32D2 ->1008:6EC8 ->1008:7118. Proxy far-calls the CRT routine thenRETF. State is DWORD DS:0A90/0A92:

    next_state = (old_state * 214013 + 2531011) mod2^32
    AX = (next_state >>16) &7FFFh

Original multiplication helper executes and returnsDX:AX with RETF8; state addition propagates carry. The generator's INC BP/DEC BP stack convention is retained by execution. EXE Data10 initializes state to1, but runtime seed setter6EB0 and its callers remain outside this pass. Do not substitute default seed1 for a proved gameplay seed lifecycle.

Enumerating the possible15-bit outputs gives4682 values with remainder0 modulo7,4681 for each other remainder. This is a property of the mapping, not proof of independent or uniformly sampled runtime RNG outputs. Exact rejection counts and final state must be preserved for deterministic replay.

## Original-code validation

The harness loads the two selectors, proxy, generator and multiplication helper from original bytes, applies NE internal selector fixes and checks133 listed instructions against both relocated images and the actual emulator memory. Full instruction spans include immediate bytes of RETF8. RNG proxy is a stub for selector branch fixtures, then restored to original code with translation-cache invalidation for real-chain tests.

-7168 selector fixtures cover all128 seven-variant masks, actor timer0/1, special high-byte0/nonzero and seven cyclic starting residues, for both selectors.42 are intentionally bounded nonreturn fixtures; the rest return the expected index with exact RNG call count.
-1029 standalone original PRNG executions cover seeds0..1023 and five32-bit boundary patterns. Returned AX and full updated state match the LCG model.
-1016 selector executions use the original proxy, generator and multiply helper without RNG stubs: all127 nonempty masks, four independent starting seeds and both selectors. Selected variant, exact consumed count and final32-bit state all match the independent rejection/LCG model.

Descriptors deliberately use00FFh for rejected variants and0100h for accepted ones to test high-byte semantics. Controlled real-mode segmented memory and far returns do not constitute a full Windows runtime. No graphics, death/drop/score callbacks or full demo stream are executed.

## Ghidra and coverage

Annotated five existing functions; full native export and project save completed. Internal entries remain1551, all1551 decompilations completed;310 EXTERNAL-block entries separately tracked. Coverage unchanged:160005 instruction bytes,8282 data bytes,1401 undefined bytes. No new function entries, binary patches or padding typing. General multiplication for every operand pair was not tested; the original helper was exercised with the fixed LCG multiplier.

## Unknowns and next test

Extract actual death/reaction frame WORDs from descriptors and asset loaders, verify available-mask invariants and identify variant7 visually. Trace6EB0 seeding and save/load/demo RNG state handling. Couple these selectors and their real RNG to pass19's real kill/reaction callbacks, recording changes to actor/object fields. Full enemy death behavior, rendering and deterministic replay remain open.

## Confidence

High for bounded original-code selection, high-byte tests, RNG recurrence and exact tested rejection-state consumption. Full-game/runtime tests:0.
