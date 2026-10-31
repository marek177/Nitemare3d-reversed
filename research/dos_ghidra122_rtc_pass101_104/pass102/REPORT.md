# Pass102 — native RTC installation and removal

## Finding
Confirmed, High under modeled device/DOS interfaces:96 complete lifecycles pass, each with five original RTC setup calls, across six distinct EXEs. Original CMOS helpers and DOS getvect/setvect wrappers execute unchanged. Inputs are controlled CMOS/PIC state, DOS vector replies/effects and initial active flag0; no application/CRT function is mocked.

## Evidence
rtc_lifecycle_tests.json preserves all input states, each stage snapshot, exact18-event port trace,3 vector operations, original hashes and per-build active/saved-vector globals. Static functions/bytes and fresh Ghidra12.2 exports are in pass101. Each lifecycle executes install0, install0 again, remove1, remove1 again, unsupported2. Matrix per build:regA20h/70h ×regB00h/FFh ×PIC00h/FFh ×initialIF0/1 =16.

## Behavior model
Install(arg0) when inactive: CLI; read CMOSA; replace its low nibble with6 while retaining high nibble; save INT70 vector via original DOS35h helper; set it to the recovered ISR via original DOS25h helper; read/OR40h/write CMOSB; read CMOSC; read/clear bit0/write slave PIC maskA1h; set active1; STI. The test confirms the exact original handler segment/offset installed by each build.

Remove(arg1) when active: CLI; read/OR1/write PIC maskA1h; read/clear40h/write CMOSB; restore saved INT70 vector; set active0; STI. It does not restore the old CMOSA value. It clears periodic enable even if it was initially set, and masks PIC IRQ8 even if initially unmasked. This is not full previous hardware-state restoration. The saved interrupt vector is restored exactly.

Repeated install/remove calls skip all I/O and vector operations and preserve entry IF. The real transition paths finish with IF1 even when entry IF0. Unsupported argument2 also performs no tested I/O/vector/state changes. Return-value semantics for all unsupported arguments are not established here. Cached counter remains12345678h throughout all five calls; this setup helper does not reset it.

## Implementation-ready findings
Keep separate active flag, saved far vector, CMOS rate configuration and cached time. Preserve install/remove guards and original partial teardown behavior for emulation. Rate nibble6 and periodic-enable bit40h are confirmed; no external oscillator/divider timing was measured, so this report does not assert milliseconds or measured IRQ frequency.

## Unknowns and next test
Actual device availability, NMI behavior, PIC cascade configuration outside this helper, BIOS interactions and asynchronous IRQ delivery remain unknown. Cross-mode caller reachability and complete startup/shutdown are not established by calling this helper directly.

## Confidence
High for exact helper/device-interface sequences under fixture replies. Real DOS interrupt delivery remains outside scope.
