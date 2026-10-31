# Pass100 — original TZ initializer, getenv and complete CRT clock

Confirmed, high confidence under modeled startup-environment and DOS replies:204 cases pass across all six distinct supplied DOS EXEs. Supplied1.8/1.9 are identical. Each case begins with initialization gate0, original relocated MZ data and a controlled near environ pointer table. Original clock→ftime→initialization gate→TZ parser→getenv/string/atoi/arithmetic helpers→calendar/DST all execute, with no application/CRT call mock or patched instructions. Only startup environment memory and DOS INT21 date/time replies are fixtures.

## Verified behavior
The native image defaults are timezone_seconds28800 and DST-enable1 in every distinct EXE. Missing TZ and TZ= preserve them; the gate still becomes1. Thus a tested January sample produces epoch+28800, while the July sample produces epoch+25200 after the native DST subtraction. This explains the preliminary unconfigured summertime offset seen in pass96; it does not identify a user's location.

A nonempty TZ string uses three leading characters as the standard name, followed by an optional sign and decimal hours, optional :minutes and :seconds. The parsed numeric offset adds to local-calendar epoch; a leading minus negates the complete offset. The remaining suffix's first byte is stored as a word in the DST-enable global: EST5EDT yields69 (ASCII E), CET-1CEST yields67 (ASCII C), rather than Boolean1. No suffix yields0. Any tested nonempty suffix, even a comma, enables the fixed native DST predicate; no rule-string parser is established. Name-copy behavior is visible statically but full destination buffers were not asserted.

|TZ fixture|timezone seconds|DST-enable word|
|---|---:|---:|
|missing / empty|28800|1|
|UTC0|0|0|
|EST5|18000|0|
|EST5EDT|18000|69|
|CET-1CEST|-3600|67|
|ABC+5:30:45DEF|19845|68|
|ABC-5:30:45DEF|-19845|68|
|ABC0:00:01|1|0|
|ABC23:59:59DEF|86399|68|

The 17 fixtures also include ABC0:30, ABC+0, ABC5:, ABC5::, ABC5:30:59XYZ, ABC5:30:59, and ABC-23:59:59DEF. Empty minute/second fields in these explicit examples contribute zero. No broad malformed-input safety or compatibility claim follows.

After the first native clock completes, each case overwrites environment text with TZ=ZZZ9ZZZ and calls the original initialization gate again. Offset and DST-enable remain unchanged and the gate stays1. The first gate invocation increments the word even for missing/empty TZ, so later environment changes do not cause automatic reparsing.

## Matrix / oracle / evidence
204 =6 EXEs ×17 TZ fixtures ×2 dates(1994-01-01 and1994-07-01 at12:34:56.78). The environment table includes a nonmatching OTHER entry before TZ, exercising native getenv scanning. Missing TZ ends that table after OTHER. Actual process startup's construction of environ is not exercised; its recovered near pointer global is populated by the fixture.

Assertions compare parsed offset/sign/units to a separate Python numeric-string oracle; DST global to suffix ASCII; all10 CRT structure bytes to independent epoch arithmetic; timezone minutes to signed division truncated toward zero; final clock to wrapped32 milliseconds; normal return, stack, DOS request sequence and one-shot gate state. Full cases, hashes, globals, original Ghidra12.2 C/instruction exports, seeds, Java script and logs are preserved. Fresh decompilation succeeds for initializer and getenv in all6 builds:12/12 functions. Pass97 provides gate/DST/calendar exports.

Run python scripts/verify_native_tz_initializer.py from this archive root. Requires Unicorn2.1.4 and Capstone5.0.7. Original input EXEs, baseline specs and pass96 provenance are included for this execution. Ghidra project dependency is in the preceding pass97–99 artifact; runtime binaries are not bundled.

## Remaining unknowns
Actual DOS startup/environment allocation, all TZ malformed/overflow inputs, names beyond the three copied bytes, true system clock behavior, cached-counter writers/scheduler callers and complete game parity remain unverified. Native-time fixture coverage is not a recovery percentage.
