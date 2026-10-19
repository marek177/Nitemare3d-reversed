# Source appendix — DOS1.2 GUARD41 state09 through epilogue

The latest source is `evidence/2026-10-19/README_SK_20261019-192416_.md`.
It supersedes the shorter state09 capture in `README_SK_20261019-185505_.md`.

The reported original DOS1.2 interval contains 4235 executed CPU instructions,
17665 reads and 12675 writes (34575 total), ending USER_STOP at the breakpoint
`0CC6:12B2` after executing `0CC6:104C`. The epilogue instruction itself has
not executed at the stop.

- Terminal helper writes GUARD41 state `09→0A`; WORLD flags `0B→0B`.
- With `DS:40EC=1`, a side helper consumes RNG #19:
  `AEA69ED3→12DBCE4A`, result 4827, `%3=0`, selected index `0B`.
  This is not yet a specific sound or drop identity.
- WORLD class `0F` takes the common terminal-helper return. Linked WALL `BB`
  has observed property byte 0; `property & 8 == 0` takes the epilogue branch.
- No new HP, score or map-marker write occurs in this bounded interval.
- DOS1.2 and DOS2 static dispatch tables map states 0A and 0B directly to their
  common epilogues. This does not establish slot release by other subsystems.

The earlier state0→9 breakpoint sequence did not continuously trace all timer
updates. DOS2 natural GUARD41 death was not reached in the reported attempt.
Do not merge this DOS1.2 RNG #19 with the separately captured DOS2 18-entry
ledger solely because the mathematical LCG states align.

**Open:** first subsequent scheduler pass, global pool cleanup/drop writers,
DOS2 natural runtime and exact SFX mapping. This is a source-report integration;
the raw trace and original binaries have not been rerun here.
