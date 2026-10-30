# Pass81 — original CRT open return paths and descriptor metadata

Confirmed within synthetic DOS-response fixtures, High confidence: original DOS1.7 and supplied1.8/1.9 CRT open preserves success return handles below its unsigned limit, records descriptor flags, and closes out-of-range handles before returning ffff with errno24. Original error mapper executes unchanged. Supplied1.8/1.9 are byte-identical, hence two distinct binaries tested. This is instruction-level execution, not an actual DOS filesystem run.

| Build | Open entry | Error return | Error mapper | Limit word | Descriptor bytes | errno word | raw-error byte |
|---|---|---|---|---|---|---|---|
|1.7|21d1:1c72|21d1:05b7|21d1:05ca|DS20ec|DS20ee|DS20dc|DS20ea|
|1.8/1.9|21ea:1c76|21ea:05bb|21ea:05ce|DS2126|DS2128|DS2116|DS2124|

## Success path
For flags8000h or8008h, initial DOS open uses AX3d00. Next AX4400 queries the returned handle. Device bit80h in DL produces descriptor byte41h; this branch skips filename attributes and ignores bit8 in the input flags. For ordinary files AX4300 queries attributes; descriptor byte is 1 | (attribute bit0 ?10h:0) | (input flags bit8 ?20h:0). A successful call leaves previous errno/raw-error values unchanged. Handle0 is accepted by CRT open, even though the config-loader's separate signed>0 check skips it (pass74).

The unsigned handle comparison is strict: with explicit limit20, handles0,5,19 succeed and20 is closed via AH3e, followed by internal error AX1800. Original mapper stores raw-error low byte0 and errno24, then returns AX=DX=ffff. No descriptor slot is written on this failure. This is a CRT table-capacity failure after OS success, not a DOS open error.

## Initial DOS errors
For input flags8000h, DOS errors2,3,5,6,12,19,32 immediately use original mapper and returnffff; no IOCTL/attribute/close follows and descriptor sentinels stay intact. Fixture results for both binaries:

| DOS AX error | errno word | raw-error byte |
|---|---|---|
|2|2|2|
|3|2|3|
|5|13|5|
|6|9|6|
|12|22|12|
|19|ffff|19|
|32|ffff|32|

These values use the relocated MZ's existing DOS-version global and mapping table, without full CRT startup. In particular the mapper branches on a DOS-version byte; this table is not asserted for every real DOS version. Error19/32 ffff must not be silently replaced by a modern errno convention.

## Verification and limits
78 cases = 2 binaries × (7 initial errors + 32 success-response combinations). Success combinations cross handles0,5,19,20; ordinary/device; read-only attribute0/1; flags8000/8008. Every case executes original open, shared error-return and error mapper without mocked function calls. Only INT21 responses are modeled: open returns configured handle/error, IOCTL returns device bits, attribute request returns configured bits, close succeeds. Explicit DS=SS, DF0, SPe000; descriptor limit20 and sentinel table/error values. Tests assert exact OS request sequence, return value, restored SP, all20 descriptor bytes, error preservation and capacity error. Evidence includes exact EXE SHA256 and request registers for every case. Ghidra12.2 fresh error helper exports are included, alongside pass80 native-open exports.

Unknown: real OS behavior, failure of IOCTL/attribute/close, create/truncate/text-update modes, full startup DOS-version initialization, config read/close integration, other consumers and overall parity. Next: native config-loader read/length/close chain with modeled DOS requests, including handle0 and short reads.
