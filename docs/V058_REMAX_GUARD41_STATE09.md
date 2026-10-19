# Nitemare 3D RE MAX v0.58 — GUARD41 state09 runtime closure

**Date:** 19 October 2026

A new bounded original DOS1.2 trace follows GUARD41 state09 from entry at `0CC6:1006` to the common dispatcher epilogue breakpoint at `0CC6:12B2`.

The executed path performs:

- WORLD flags `0x0B |= 1`, which leaves the byte unchanged;
- GUARD state `09 -> 0A`;
- WORLD class 0x0F helper dispatch;
- one additional RNG draw, now numbered #19 on this captured death path;
- RNG `AEA69ED3 -> 12DBCE4A`, result 4827, `result % 3 = 0`;
- the measured property-table branch for WALL ID BB yields zero for bit 0x08 and jumps to the common epilogue.

The trace contains 4,235 CPU instructions and 34,575 total events and ends by USER_STOP rather than size limit.

Static comparison of the SHA-pinned DOS1.2 and DOS2 executables also shows that states 0x0A and 0x0B dispatch directly to their local common epilogues in both builds. This is a local dispatcher fact, **not** proof of natural DOS2 GUARD41 death reachability.

Still open: the first following scheduler pass after state0A, later WORLD/OBJECT/pool cleanup, item-drop behavior, and natural DOS2/Win16 equivalence.
