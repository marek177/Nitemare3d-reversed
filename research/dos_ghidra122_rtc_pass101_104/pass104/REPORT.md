# Pass104 — native RTC interrupt between cached counter word loads

## Finding
Confirmed, High for controlled instruction interleavings: all six distinct supplied DOS EXEs can return a mixed cached counter value when the original RTC ISR runs between the low16 and high16 loads. Original counter and ISR execute, including native context save/restore and IRET; no application/CRT function is mocked. This proves a possible instruction ordering, not its observed frequency on DOS hardware.

## Evidence
counter_interrupt_tests.json preserves144 cases and exact interruption address. The original counter/ISR Ghidra exports and byte hashes are in pass101 and pass95 provenance. For supplied1.8/1.9, counter1bda:0098 reads low at00aa and high at00ad; ISR1bc8:0006 increments cached376d:081e with a single32-bit INC.

## Behavior model
The RTC-mode reader has no CLI/snapshot/retry around its pair of word loads. At a controlled boundary, the verifier stops before the selected reader instruction, constructs a hardware-style IP/CS/FLAGS stack frame, clears IF/TF, executes the original ISR, and lets original IRET resume the reader. CMOS status40h is a fixture. It then calls the reader again without another interrupt.

144 =6 builds ×8 counters ×3 placements(before low, between words, after high). Counter values0,1,FFFEh,FFFFh,1234FFFFh,7FFFFFFFh,FFFFFFFEh,FFFFFFFFh cover carries and wrap. Before-low returns incremented value; after-high returns prior value. Between words returns (new_cache&FFFF0000h)|(old_cache&FFFFh). In24 cases this result equals neither the old nor new counter. The next uninterrupted read returns the actual incremented cache.

|Old cache|After ISR|Return between loads|Next read|
|---|---|---|---|
|0000FFFFh|00010000h|0001FFFFh|00010000h|
|1234FFFFh|12350000h|1235FFFFh|12350000h|
|7FFFFFFFh|80000000h|8000FFFFh|80000000h|
|FFFFFFFFh|00000000h|0000FFFFh|00000000h|

Thus a subsequent read can decrease by65535 after the transient mixed value. This is not a claim that the ISR's own32-bit increment is torn; the problem is the separate consumer loads.

## Implementation-ready findings
An exact instruction-interleaving emulator must allow this read pair to observe a rollover between words. A modern atomic snapshot would change this corner behavior; whether it is required in a remake's user-visible compatibility model depends on actual timing/reachability evidence. Do not present this fixture as observed gameplay jitter or a confirmed cause of a specific bug.

## Unknowns and next test
Actual IRQ placement/frequency and whether gameplay callers can observe/propagate the transient require DOSBox-X or hardware traces with breakpoints on these loads and cached writes. Other readers using dword operations or repeated snapshots require separate analysis. No real OS run occurred in this pass.

## Confidence
High for byte-exact controlled native counter→ISR→IRET→counter execution; incomplete for real-world occurrence and whole-game consequences.
