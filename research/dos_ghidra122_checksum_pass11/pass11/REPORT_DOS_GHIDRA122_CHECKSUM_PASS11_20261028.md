# Checksum pass11 — original low-level open and handle flags

## Finding
Confirmed across six distinct supplied DOS EXEs: the original low-level CRT open maps explicit binary flag8000 to a handle with text bit80 clear, independent of the default text/binary setting. Explicit text flag4000 sets bit80; absent either explicit flag, default global bit80 selects binary when set. Device status and read-only attributes are tracked independently.

## Evidence
1440 targeted executions passed: 576 validator integration cases now execute original low-level open instead of the pass10 low-level-open stub, plus864 standalone low-level-open matrix cases. Both suites run original instructions exported by Ghidra12.2 in Unicorn. No new Ghidra database edit or decompiler coverage increase is claimed.

Integration chain: validator -> original fopen/slot selection/mode parser -> original low-level open -> original FILE initialization -> original lazy buffer setup -> original fread/refill/copy/low-level read. Simulated dependencies: DOS INT21 open3d00 returns handle5; IOCTL4400 reports regular file; attributes4300 reports writable; read3f returns requested input or EOF/error; malloc512 returns DS:9400 or null; fclose is bypassed. No stub bypasses fopen or low-level open. Binary handle flag1 is asserted on every DOS read. The suite retains576 cases from pass10, including CRLF/Ctrl-Z binary data, allocation success/fallback, empty input, negative requested length, short reads and persistent read errors. Twenty-four cases deliberately exhaust100000 instructions in the observed retry loop; these are bounded traces.

Standalone matrix: flags0000/4000/8000 x default global00/80 x read-only0/1 x regular/device x DOS open success/error2/error5 x returned handle5/25, across6 images =864. Maximum handle count20. Only INT21 is hooked; complete original low-level-open routine and original common return/error handling execute. Every test checks returned AX, far return/SP, handle flag byte, and unchanged sentinel on failed open or out-of-range handle. Inputs are controlled, not real DOS files/devices.

V1.9 routine21ea:1c5c; actual DOS calls include3d00 at21ea:1ca8,4400 at21ea:1cd9,4300 at21ea:1dcc. Default mode byteDS:232b, maximum handlesDS:2126 and handle flagsDS:2128+handle. Per-build entries and hashes are recorded in lowopen_matrix.json; integration locations retain all prior fopen/allocator addresses.

## Behavior model
For tested read-only open access (share0):

| Input | Handle flag result on valid success |
|---|---|
| Explicit binary8000 | Text bit80 clear regardless of default |
| Explicit text4000 | Text bit80 set regardless of default |
| Neither | Text bit80 set iff default global bit80 is clear |
| DOS IOCTL device bit80 | CRT device bit40 set; read-only flag not derived from file attributes |
| Regular file + DOS read-only attribute1 | CRT bit10 set |
| Any valid success | CRT open bit01 set |

DOS errors2/5 returnffff and preserve the handle-flag sentinel. DOS returning handle25 with configured maximum20 causes an original DOS close request and returnsffff, without publishing a handle flag. The matrix records the interrupt trace, including those close calls. It does not execute DOS itself.

For the actual validator rb path and regular writable file, the published flag is01. Combined with prior original CRT read tests, this closes the previously simulated link between rb and binary reading: control bytes CRLF/Ctrl-Z remain raw input under the tested DOS interface.

## Classification and limits
Confirmed/High: flag construction, default override, attribute/device separation, open failure and out-of-range-handle handling in the tested read-only modes. Confirmed/High within simulated DOS: full checksum chain binary path and allocation fallback. Unknown: real OS startup/global initialization, actual filesystem/device behavior, write/create/truncate/append/share modes, errors in IOCTL/attribute calls, close/free implementation and allocator internals. Full gameplay/render/tick parity remains unverified. Supplied1.8/1.9 are still one identical image.

## Reproduce and next step
Run `/usr/bin/python3 scripts/verify_checksum_lowopen.py` and `/usr/bin/python3 scripts/verify_lowopen_matrix.py` (Unicorn required). Archive includes EXEs, Ghidra instruction exports, pass7 specs and pass10 extracted call-site metadata. Next close the remaining fclose/free ownership contract and audit resource-loader allocation/seek/error behavior.
