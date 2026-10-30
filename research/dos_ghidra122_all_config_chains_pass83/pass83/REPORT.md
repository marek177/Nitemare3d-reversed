# Pass83 — all supplied DOS native config chains and seek failures

Confirmed with High confidence for stated fixtures: original config-loader→CRT open/length/read/close→viewport chain executes consistently across six distinct runtime MZ EXEs covering labels1.0,1.1,1.2,1.5,1.7,1.8,1.9. Supplied1.8/1.9 are byte-identical. This extends pass82 to all builds, and adds initial-position and restore-position failures. No application/CRT function call is mocked; DOS INT21 replies are synthetic, and fatal callee is stopped before entry.

## New finding: restore failure is ignored
The native length helper obtains current position (origin1), seeks end (origin2), saves that length, and restores the old position (origin0) when positions differ. An error on the initial-position query returns failure immediately; loader takes fatal branch without read/close. An error on end-seek still attempts restore, then returns failure. However an error on restore does not replace the previously obtained end length. With end length16, loader accepts the file and calls read regardless of restore error.

In the explicitly modeled restore-failure scenario, position stays at end16; the next read returns0/EOF, default16-byte config stays intact and successful close clears descriptor state. This is a conditional consequence of that OS-response/position model, not evidence that a particular DOS filesystem actually generates this sequence. The ignored restore status itself is established by original instruction execution in all six binaries.

## Cross-version results
Every build passes14 modes: normal, handle0, open failure, short reads0/1/15, read error, close error, sizes15/17/65552, end-seek error, initial-position error, restore-position error. Total84 cases. The earlier findings hold across all builds: handle0 is recorded by CRT but skipped without close by loader; non16-byte length triggers fatal boundary; ignored read result permits defaults or partially overwritten config; close error retains descriptor flag1 while setup continues.

| Build | CRT open | CRT length | CRT read | CRT close |
|---|---|---|---|---|
|1.0|219b:1d6e|219b:29ce|219b:1f10|219b:1cb2|
|1.1|21bc:1c72|21bc:290a|21bc:1e14|21bc:1bb6|
|1.2|21c2:1c72|21c2:290a|21c2:1e14|21c2:1bb6|
|1.5|21c7:1c76|21c7:290e|21c7:1e18|21c7:1bba|
|1.7|21d1:1c72|21d1:290a|21d1:1e14|21d1:1bb6|
|supplied1.8/1.9|21ea:1c76|21ea:290e|21ea:1e18|21ea:1bba|

## Evidence and reproduction
`config_chain_tests.json` records exact EXE SHA256, registers of each OS request, modeled file position, full resulting16-byte config and descriptor flag. Script asserts complete request sequence, fatal/normal return, exact config bytes and descriptor status. DS=SS, DF0, SPe000, empty prefix; initial CRT globals come from relocated MZ, no full startup asserted. Native viewport/projection/clipping runs without mocks. Descriptor base is recovered from each original open's MOV[BX+disp],CL instruction, not copied from a newer build.

24 fresh Ghidra12.2 decompilations (open/length/read/close per distinct EXE) succeed; instruction TSVs and seed addresses are included. Decompiler success is not semantic completeness. The baseline58 runtime inputs and repaired native project are available through the included pass76 dependency ZIP. Run python scripts/verify_all_native_config_chains.py with Unicorn2.1.4 after extracting dependencies and restoring included pass74/pass79 paths. Expected14 passed per build.

Unknown: actual DOS/filesystem response behavior, full startup globals, IOCTL/attribute failure, partial-transfer-on-error, create/text modes, fatal cleanup, game-visible effects and complete parity. Next: audit native config save path, then other prefix-helper consumers. Runtime OS validation remains distinct from these instruction-level experiments.
