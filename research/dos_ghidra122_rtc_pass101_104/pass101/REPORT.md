# Pass101 — recovered RTC ISR and counter writer

## Finding
Confirmed, High: all six distinct supplied DOS EXEs contain an RTC ISR which increments the same cached32-bit value returned by the counter wrapper in RTC mode. The ISR entry was absent from the old instruction audit. It was recovered from original bytes, explicitly disassembled/created as a function in a temporary read-only Ghidra12.2 session, and executed through IRET. Supplied1.8/1.9 are identical.

|DOS label|RTC ISR|Cached u32|RTC setup|
|---|---|---|---|
|10|1b7f:0006|3360:07a2|1b7f:0078|
|11|1b9f:000e|3395:07e2|1b9f:0080|
|12|1ba0:0000|339b:07ec|1ba0:0072|
|15|1ba8:0006|374a:07f0|1ba8:0078|
|17|1bb2:0002|3754:07f0|1bb2:0074|
|18|1bc8:0006|376d:081e|1bc8:0078|

## Evidence
|Status|Claim|Source/location|Confidence|Reason|
|---|---|---|---|---|
|Confirmed|ISR performs inc dword ptr [cached], wrap32|irq_locations.json, per-build ISR+0x0d|High|Original bytes plus576 native cases|
|Confirmed|Counter in nonzero mode returns this value|Original counter export, irq_tests.json consumer|High|Each ISR case followed by unmodified consumer execution|
|Confirmed|No previous ISR call and no status-bit guard in this handler|Whole ISR bytes/ports in irq_locations.json|High|Native entry→IRET and exact I/O trace|
|Unknown|Real interrupt rate, lost/queued interrupts and observed game jitter|No DOSBox/physical IRQ timing measurement in this pass|Low|Only controlled entry/CMOS fixtures executed|

## Behavior model
The ISR pushes32-bit general registers, DS and ES, installs the game's relocated DS, clears DF, increments cached32 once, selects CMOS registerC via OUT70h, reads71h, emits EOI20h to slaveA0h then master20h, restores context and returns via IRET. The input status byte is ignored: fixtures00h andFFh both increment exactly once. The old vector is not chained by this handler. No cached reset occurs here.

576 cases =6 EXEs ×8 counter values ×6 FLAGS frames ×2 CMOS replies. Values cover16-bit carry and full32-bit wrap. Assertions check exact4-byte increment, all seven general-register values, restored DS/ES, stack, FLAGS, exact port sequence, and then native counter return in RTC mode. The second step calls the actual wrapper with mode!=0, so the CRT clock branch is not entered. Registers/memory at IRQ entry, interrupt stack frame and CMOS input are fixtures. This is native instruction emulation, not full DOS gameplay or proof of asynchronous hardware scheduling.

## Ghidra recovery and limits
Old cache_refs.json is a literal text scan of prior audit instructions, not a complete read/write inventory: it misses the ISR and contains an old misdecoded instruction. Fresh Ghidra exports recover5 functions per build: ISR, RTC setup, CMOS read/write and cached reader. Newly created entry metadata is retained; the source project is not permanently mutated. C decompilation of the ISR carries a stack-frame warning and does not faithfully display IRET semantics, so original instructions and native execution control the claims. Ghidra xrefs may also omit an inferred DS reference even when the decompiler renders the matching global; xref count is not behavioral completeness.

## Implementation-ready findings
In RTC mode, counter means cached interrupt count; do not silently label this verified milliseconds. Preserve u32 increment/wrap and raw return behavior for compatibility. The exact runtime frequency requires separate platform evidence. Input status-bit filtering and previous-vector chaining must not be invented as original behavior.

## Unknowns and next test
Original RTC initialization/lifecycle is verified in pass102. Reader atomicity is tested by controlled native ISR interleaving in pass104. Higher-level whole-frame scheduling and real OS/hardware timing remain unknown.

## Confidence
High for the original handler→cached value→counter return chain under explicit fixtures; incomplete for real-time delivery and gameplay parity.
