# Pass96 — original CRT clock down to modeled DOS date/time requests

## Finding
Confirmed, High confidence for explicit DOS/timezone fixtures: all six distinct supplied DOS EXEs execute the original clock CRT branch and native CRT date/calendar arithmetic to produce an epoch-derived millisecond value. 432 cases pass without mocked function calls. Only DOS date/time replies are modeled. Supplied1.8/1.9 are identical. Actual OS time accuracy, timezone-environment initialization and DST rules are not established.

## Evidence / native result
The CRT structure is observed immediately after its original far return, before the clock caller consumes it:

| Offset | Verified value under fixture | Width |
|---|---|---|
|+0|Unix epoch seconds of supplied calendar datetime plus explicit timezone-seconds global, modulo2^32|u32|
|+4|DOS returned hundredths ×10|u16|
|+6|explicit timezone-seconds /60|u16 in tested positive/zero domain|
|+8|0 with DST-enable fixture0|u16|

Clock caller executes wrap32(structure[0]*1000+structure[4]) and returns DX:AX. This upgrades pass95's synthetic structure fields to native CRT-produced values, checked against an independent Python UTC calendar calculation. Integer wrap behavior remains explicit; this is not a claim of a monotonic clock.

Original DOS requests are INT21/AH2a for date and AH2c for time. Modeled date returns year in CX, month/day in DH/DL and AL weekday0; modeled time returns hours/minutes in CH/CL, seconds/hundredths in DH/DL. Native date/time wrappers and all conversion helpers execute unchanged. For tested midnight00:00:00, CRT repeats the date query after time: sequence2a,2c,2a; other tested times use2a,2c. Original code tests hour/minute bytes for this re-read. Both date replies are identical in this pass; a date-changing midnight consistency case remains untested.

## Case matrix and scope
432 cases =6 distinct EXEs ×6 calendar samples ×3 timezone-seconds values(0,3600,25200) ×4 hundredths(0,1,78,99). Calendar samples:1970-01-01 00:00:00;1994-05-01 12:34:56;1999-12-31 23:59:59;2000-02-29 01:02:03;2026-10-31 07:08:09;2038-01-19 03:14:07. These are supplied register fixtures, not an assertion that a particular DOS version supports every year as a real system date.

Timezone initialization-complete word is explicitly set1; timezone-seconds global is set per case; DST-enable word0. Original CRT initialization helper still runs and observes its completed gate, so environment parsing does not run. No location-specific timezone is inferred from a numeric offset. This distinction matters: a preliminary unconfigured probe produced a different offset, which must not be presented as the user's timezone or universally fixed CRT behavior.

Assertions cover normal return, restored SP, exact request sequence, all10 structure bytes and final wrapped32-bit millisecond result. Every case executes original clock and complete native CRT structure/conversion chain, with no patched bytes or mocked application/CRT call. DS=SS,SPe000. Only DOS interrupt replies are synthetic. Native EXE SHA256, clock/CRT/global addresses and full recovered CRT routine bytes are retained in crt_clock_tests.json.

## Ghidra and reproducibility
Source mapping starts from the preserved Ghidra12.2 counter/clock evidence and original MZ bytes. source_clocks.json contains recovered95 metadata; Capstone5.0.7 independently decodes the native CRT entry and global locations. verify_native_crt_clock.py uses Unicorn2.1.4 to execute original code and Python datetime as the independent calendar oracle. Extract included pass76 dependency and nested baseline58 dependency to baseline58/, keep pass96 evidence paths, then run the script:72 passed per distinct EXE.

Ghidra12.2 and JDK25 were restored from the supplied archives. Fresh read-only exports successfully decompile clock and CRT time routines for all6 binaries (12 functions). This also supplies the fresh clock exports missing in95. DOS1.5 required a retry after restoring the decompiler executable permission; final results are12/12 completed. Seeds, script, logs and ghidra_status.json preserve that validation. Decompiler success remains distinct from native execution and overall recovery completeness.

## Unknowns / next test
- Actual TZ environment parsing, DST transition behavior and initialized defaults: execute original timezone initializer with controlled environment records.
- Midnight/date-change race: return different dates on the first/repeated AH2a and inspect chosen epoch.
- Invalid DOS returns and OS year support: separate OS/runtime experiments.
- Cached-counter writer and monotonicity: trace all writes before using clock output as a scheduler invariant.

Overall confidence High for tested native date→CRT structure→wrapped millisecond calculation; incomplete for real OS time and complete game parity.
