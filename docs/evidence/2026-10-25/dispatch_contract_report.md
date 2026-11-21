# Original dispatcher, update ordering and palette RNG contracts

## Evidence boundary

Three exact local spans of hash-pinned unpacked DOS2 image5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3 were independently length-checked with Capstone5.0.9 and iced-x86 1.21.0:0BDE:0370..03C6,0BDE:03C8..04D5,083D:1CFC..1DC8. All181 instruction lengths agree. This supports the following bounded instruction contracts; it does not close shared ownership, alternate entries, all caller invariants or callee side effects. Existing global function-boundary statuses remain UNKNOWN.

## Dispatcher0BDE:03C8

The routine first calls clock0BDE:0094 and saves its32-bit result, then clock0BDE:0018 and saves that result separately. Both scheduling gates compare unsigned32-bit words, high word first.

1. Call0BDE:00D4 with the saved clock0094 value and store its result in DS3672/3674. If threshold DS1738/173A is no greater than this sequence, call update0BDE:0370 only when DS3CD6=0. Regardless of that mode test, set threshold=sequence+1 modulo2^32 when this gate is entered.
2. Call0BDE:0114 with the same saved clock0094 value and store result in DS3676/3678. When threshold DS173C/173E is no greater than this second sequence, enter the render block. If DS3CD6!=0 and bit0 of DS4540 is set, first call update0370 with the first sequence. Then call02F8,0156,083D:1CE8,083D:1E66,0000:0AEA,07ED:0360 in that order.
3. Read clock0094 again and subtract its saved value modulo2^32. If elapsed>=65 clock0094 units, call page-swap0156:008E. Otherwise call0156:00A8. Then call input06B0:05D6, set the second threshold=sequence2+1 and set DS1734/1736 to the saved clock0018 result.
4. After either taking or skipping the render block, compare unsigned32(saved clock0018 - DS1734)>500. If true, call0BDE:0004 with1, then0, then read0018 and store it in1734/1736.

The two gates are separate and neither contains a local catch-up loop. Nested callees can have their own control flow; this statement does not prohibit reentrant dispatcher calls elsewhere. Clock0094 units here are not relabelled as wall-clock milliseconds or performance measurements.

## Ordered update0BDE:0370

The literal order is0C2B:026A,0000:0A40,04C7:12B6,083D:1DCA (forward the32-bit caller argument),083D:20D2,0000:0E50,083D:20DC,083D:1CFC(argument0),083D:05D2(argument17),083D:0C56(argument1). If lowbyte(argument)&7==0, append083D:05D2(argument16). These names identify addresses, not a claim that every OBJECT/actor mutation is understood. The routine reads its32-bit parameter at BP+6, uses FAR return without parameter cleanup, and restores BP locally. Nested register/alias side effects remain open.

## Countdown/phase palette routine083D:1CFC

The initial gates return when DS626A=2, or when DS626A=3 and signed16(DS626C+1)<10. A nonzero low byte of the parameter initializes countdown DS3634=80 and phase byte DS3636=0, then writes black to DAC indexEB and the low-byte index from DSD2F7 through0156:0150.

For parameter0, the code decrements countdown and tests its OLD value. A nonzero old countdown returns. When old countdown is zero, phase0 becomes1 with countdown3 and two palette writes whose component low bytes areFF. Phase!=0 becomes0, calls RNG0FBA:01A0 and sets countdown=(AX signed remainder240)+160; for the verified nonnegative15-bit RNG contract this is160..399. It writes both entries black and calls083D:0EA0. With repeated eligible calls the old-value countdown test gives81 calls from initial80 to the phase branch, and4 calls from3. This is local control-flow arithmetic, not a claim about real-time cadence or the visual meaning of these DAC entries.

The prior natural RNG trace at caller083D:1D5B belongs to this palette-interval branch. It is not evidence of GUARD damage RNG. State1→0029E2C0 and AX41 remain one verified natural RNG invocation; no seed was written by the test.

## Original runtime observations

Owned clean_run_c/ses-1 was continued from the prior gameplay state.34 persistent execution breakpoints covered all direct CALL sites in dispatcher03C8 and update0370, plus their entry/RETF boundaries. Each stop records registers, return stack bytes, RTC value, both sequence counters, thresholds, render counter and mode words. No guest state was written during this ledger.64 site observations contain an initial partial tail followed by two complete entry-to-RETF dispatcher observations.

Both complete observations have DS3CD6=0, execute the first update gate once and the render block once, and choose0156:008E with elapsed124 clock0094 units. The optional update0370 call from044E and optional update call03C0 are absent in these observations. At the first exit, sequence values171/173 correspond to thresholds172/174; at the next exit,172/174 correspond to173/175. These values describe this run, not a deterministic elapsed-time acceptance target.

For the second complete observation, the original entry return frame matches the frame at04D5 and SP is equal at both points. One execution step executes RETF, reaches logical0D29:16EA and increases SP by4. This identifies the active loop call at0D29:16E5. All34 measurement breakpoints were removed afterwards; the final revalidated state is stopped at154C:16EA, revision192, with no active breakpoints.

The ledger is a set of observed call-site boundaries, not a complete nested instruction trace. Debugger stops and measurement affect execution scheduling context. The nonzero mode, fast page variant, fallback reset branch and complete OBJECT/actor write ordering remain unobserved here. Paired original/remake timing, pixel and state acceptance remain OPEN.

## Reproduction and remaining work

Use the exact source/emulator hashes and local game-input manifest from the prior checkpoint. Continue the original Episode1/default-difficulty run, install the34 named sites in dispatch_callsite_ledger.json, record stopped-state registers/stack/counters, and preserve each live operation handle across waits. Observe entry-to-RETF without guest writes; compare saved FAR return bytes and SP, then step RETF to verify the actual caller. Remove only the recorded breakpoint IDs. Read-only static span verifier checks identity and code-span hashes; it is not a behavioral emulator or parity oracle.

Next: trace nested actor/object routines in the observed update order, including writes to live slot arrays and reentrant paths; exercise alternate scheduler modes and branches with original inputs; build a tick-indexed RNG ledger and a paired original/remake state+indices+DAC checkpoint. Complete Win16 runtime and global indirect-target closure remain required. Game binaries/assets, RAM/VRAM and raw original traces remain local.

