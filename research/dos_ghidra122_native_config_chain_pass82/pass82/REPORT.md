# Pass82 — original config-loader/CRT/DOS request chain

Confirmed, High confidence in explicit synthetic DOS fixtures: DOS1.7 and supplied1.8/1.9 original configuration loader executes native filename helper, open, length, read, close and viewport setup. No function calls in this chain are mocked. Only DOS INT21 responses are supplied by the harness; fatal callee is a stop boundary. This extends pass74, whose CRT operations were function mocks, and pass80/81's open-only coverage. Supplied1.8/1.9 are identical; two distinct binaries tested.

| Build | Loader | CRT length | CRT read | CRT close | 16-byte config |
|---|---|---|---|---|---|
|1.7|1277:0c70|21d1:290a|21d1:1e14|21d1:1bb6|DS40b4|
|1.8/1.9|1277:0c6e|21ea:290e|21ea:1e18|21ea:1bba|DS4144|

## Native request sequence
For ordinary handle5: AX3d00 opens config.sav; AX4400 queries device flags; AX4300 reads attributes. Length then requests AH42 with origin1/current, origin2/end and origin0/restore. In these fixtures current position is0, end16. Read requests AH3f, CX16, DS:DX pointing directly at the config block. Close requests AH3e. The original viewport/projection/clipping chain runs after close, without mocks. Tests inspect AH for read/close because AL contains prior values (observed close AX3e10 after a16-byte read).

## Findings
- Handle0: CRT open succeeds and records descriptor flag1. Loader's signed>0 check skips length/read/close, keeps defaults and runs setup. Descriptor0 remains recorded as open. This confirms the cross-function mismatch seen separately in74/81, not a new claim about real OS handle allocation.
- Initial DOS open failure: defaults remain and setup runs; no further DOS calls.
- Length15,17 or65552: loader reaches fatal call before read/close. The65552 case tests full DX:AX comparison against16, rather than low-word-only acceptance. Fatal handler behavior is not executed; no permanent resource leak claim is made.
- End-seek error: original length helper still restores previous position with a third seek, then loader reaches fatal before read/close. Error from length is not accepted as16.
- Short reads0,1,15: loader ignores returned count. Native read writes only the configured prefix; remaining bytes retain defaults. One byte40h replaces default width0130h low byte, producing0140h=320. Zero-byte read retains304.
- DOS read error5, no supplied bytes: native CRT returns failure; loader still closes and runs setup using defaults.
- DOS close error5: loaded16 bytes remain active and setup still runs. Native CRT descriptor byte remains1. Successful close clears it to0.

## Evidence and fixture limits
24 cases = 2 distinct binaries ×12 modes: normal, handle0, missing, short0/1/15, read error, close error, sizes15/17/65552, end-seek error. Assertions cover exact DOS operation sequence, fatal/normal completion, full16-byte resulting config block and descriptor flag. Per-case evidence records SHA256 and DOS request registers. DS=SS, DF0, SPe000, initial empty prefix. Native CRT initial globals are taken from relocated MZ; full CRT startup is not simulated. DOS replies model a regular binary file and valid operations; actual filesystem, device semantics, concurrent changes and partial-transfer-on-error are unverified.

Fresh Ghidra12.2 decompilations succeed for length/read/close in both binaries; exact instruction listings included. Ghidra C has imperfect interrupt/register modeling (e.g. declared16-bit length return), so full32-bit behavior claims rely on original instruction execution and observed loader branches. The pass76 dependency ZIP contains repaired native project and baseline runtime EXEs.

Unknowns: length initial-seek failure, restore-seek failure, IOCTL/attribute failure, read partial transfer plus error, nonbinary modes, full fatal cleanup, other versions' native chains, real DOS/runtime game behavior and complete parity. Next: extend these native CRT chains to remaining DOS versions and inspect error branches rather than assuming one shared ABI.
