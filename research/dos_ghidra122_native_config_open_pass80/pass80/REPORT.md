# Pass80 — native config open consumes the returned path intact

Confirmed, High confidence within the stated fixtures: DOS1.7 and supplied1.8/1.9 original config-loader → prefix-helper → CRT open reaches DOS INT21/AH3D with the expected complete filename. The stack-local result in1.7 is not overwritten on this particular path before the OS request. This resolves pass79's specific pre-consumption uncertainty without asserting general pointer lifetime safety or successful file I/O. Supplied1.8/1.9 are identical binaries.

| Build | Config loader | Prefix helper | CRT open | First OS request |
|---|---|---|---|---|
| DOS1.7 |1277:0c70|1277:0c20|21d1:1c72|21d1:1ca4 INT21, AX3d00|
| Supplied1.8/1.9 |1277:0c6e|1277:0c20|21ea:1c76|21ea:1ca8 INT21, AX3d00|

## Original code behavior
CRT open pushes BP, establishes its frame and reserves four local bytes. It reads the original filename argument at BP+6 and flags at BP+8. For config flags8000h, the text-default branch is bypassed; access bits are masked with3 and AH becomes3Dh. DX is loaded directly from the filename argument. No filename copy or intervening function call occurs before this first OS request. The shallow frame does not overlap the returned1.7 string in these fixtures. The dangling local-pointer property remains, but it does not by itself imply corruption at this consumer.

## Verification
20 cases: two distinct binaries × two initial SP values (e000h,d000h) × five prefixes (empty, C:\N3D\, C:\N3D, ./data/, data path/). Original relocated MZ code executes without mocked calls from config-loader entry to the first interrupt. At the native open callsite the test captures the path pointer, then observes every memory write overlapping that string through the OS request. All20 paths match prefix + lowercase config.sav, no overlaps occur, AX is3d00h, DS is the original data segment and DX points at the same intact string. Tests stop before the OS handles the request; they do not model a filesystem or DOS return values. DS=SS, DF=0 are explicit fixture conditions. The direct spaced prefix tests concatenation, not CLI %s parsing (covered in79).

Evidence native_open_tests.json records exact EXE SHA256, SP, pointer and request registers per fixture. Fresh Ghidra12.2 exports decompile both CRT-open routines successfully and preserve original instruction bytes in TSV. Baseline58 runtime EXEs and pass76 repaired native Ghidra project are supplied in the dependency ZIP. No EXE/project mutation was needed.

## Remaining unknowns
Successful-open/error-return cleanup and CRT handle metadata, real DOS filesystem results, other prefix-helper consumers, long-prefix capacity, full startup/stack conditions and full-game parity remain unverified. Next: exercise original CRT open error and success return paths with explicitly modeled DOS responses, then enumerate other consumers.
