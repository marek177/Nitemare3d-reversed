# Pass84 — native CONFIG.SAV save path across supplied DOS builds

Confirmed, High confidence for explicit synthetic DOS responses: all six distinct supplied EXEs execute the same tested config-save behavior. Labels1.8/1.9 share one identical binary. Original save function, path helper where present, CRT open/create/truncate/write/close and error helpers execute unchanged. No function call is mocked. DOS INT21 replies are modeled, so actual filesystem damage or game-visible behavior is not asserted.

| Build | Save entry | CRT write | Config block |
|---|---|---|---|
|1.0|1273:0c4e|219b:1ffa|DS3f9c|
|1.1|1275:0c74|21bc:1efe|DS40a2|
|1.2|1275:0c86|21c2:1efe|DS40a2|
|1.5|1277:0cae|21c7:1f02|DS4072|
|1.7|1277:0d06|21d1:1efe|DS40b4|
|supplied1.8/1.9|1277:0d04|21ea:1f02|DS4144|

## Original behavior
Save passes packed words filename,8301h,0080h to CRT open (32-bit PUSH immediate00808301h supplies flags and creation mode). Existing file opens via AX3d01, then AX4400 queries device bits. For modeled ordinary file, native CRT issues AH40 with CX0 (truncate at current position) before querying attributes AX4300 and returning the handle. The application requires signed handle>0, issues one16-byte CRT write directly from the config block, then closes. It checks neither returned write count nor close status; no retry or fatal call occurs in tested branches.

A zero or7-byte application write or DOS error5 still leads to close and normal return. A modeled error on the initial zero-length truncate request is ignored by this original CRT branch: attribute query,16-byte application write and close still follow. Close error likewise leaves normal application return. The in-memory config block remains unchanged for every fixture.

Handle0 is especially distinct: native CRT open already issues the zero-length truncate request and attributes query, then the application's signed>0 test skips payload write and close. Thus the request sequence permits a file to be truncated before save ignores handle0. This is a confirmed instruction-level sequence; actual DOS consequences require a real OS response and filesystem test.

Initial open error5 returns without create/write/close. Initial missing-file error2 enters original creation helper and AH3c, then closes the created handle and reopens via AX3d01 before querying attributes, writing16 and closing. Creation failure stops before application write; reopen failure stops after create/close/reopen. Both return normally at the application boundary. The modeled successful create/reopen path verifies both filenames remain config.sav, including1.7's stack-local path pointer.

## Verification
66 cases =6 binaries ×11 modes: existing,handle0,open error,short0,short7,write error,close error,create success,create error,reopen error,truncate error. Tests assert exact request sequence, operation handles, path strings, exact16-byte payload at native DOS write, modeled transferred prefix, unchanged full config block and restored SP. All cases reach original return. Existing-file traces request [3d,44,40(CX0),43,40(CX16),3e]; handle0 stops after43. Create success requests [3d,3c,3e,3d,43,40,3e]. AL residuals on AH-based requests are retained in evidence, not assumed operation IDs.

Fixture DS=SS,DF0,SPe000,empty prefix; CRT initial globals from relocated MZ, no full startup. No real host file is opened or overwritten. OS model does not independently implement persistent file position/size; transferred-byte evidence is the configured response model and observed payload, not a filesystem snapshot. Error responses set carry and AX5 (initial missing AX2); successful IOCTL/attributes indicate regular non-read-only file. Same handle5 is used for create/reopen fixtures, handle0 only in its dedicated existing-file case.

Fresh Ghidra12.2 exports successfully decompile save+write in each binary (12 exports). Exact byte listings, EXE SHA256 per test and original request registers included. Ghidra C may merge flags/mode into one32-bit constant; original stack words govern ABI. Decompilation success does not prove full recovery.

## Reproduce and unknowns
Extract included pass76 dependency and nested baseline58 dependency to baseline58/. Keep included pass74 config metadata and pass79 locations paths. Run python scripts/verify_native_config_save.py with Unicorn2.1.4:11 passed per binary. Included Ghidra script/seeds target pass76/project N3D_Runtime54/inputs, readOnly/noanalysis.

Unknown: device/text write branches, changing paths/long prefixes, real DOS create/truncate semantics, descriptor0 allocation during actual startup, callsite timing of save, full error reporting elsewhere, config field meanings and game/runtime parity. Next trace save callers and field writers to determine when settings persist and which UI controls map to the16-byte record.
