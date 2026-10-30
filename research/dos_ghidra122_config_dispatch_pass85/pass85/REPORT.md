# Pass85 — config save caller and configuration-reference inventory

Confirmed, High confidence for tested dispatch fixtures: each supplied distinct DOS binary has one Ghidra-recorded direct call reference to config save, in the matching menu dispatcher. Original dispatcher execution verifies its save/return conditions with UI/subdialog/save calls replaced by explicit boundary mocks. This is not an execution of real menus or persistent I/O; pass84 covers native save separately. Ghidra references are an inventory of recovered references, not proof that indirect/unrecovered callers cannot exist.

| Build | Dispatcher | Save callsite | Save target |
|---|---|---|---|
|1.0|1cdc:219e|1cdc:21ed|1273:0c4e|
|1.1|1d00:2182|1d00:21d1|1275:0c74|
|1.2|1d00:2184|1d00:21d3|1275:0c86|
|1.5|1d05:2182|1d05:21d1|1277:0cae|
|1.7|1d0f:217e|1d0f:21cd|1277:0d06|
|supplied1.8/1.9|1d25:21b2|1d25:2201|1277:0d04|

## Original dispatcher semantics
Each loop invokes a helper with argument9, then obtains a16-bit selection from a second helper. Results06h,15h,16h set its local exit byte1. Selection0eh calls one subdialog;23h calls another. Each subdialog's AL replaces the exit byte. Nonzero exits the loop, calls save once, and returns; zero loops. Unknown results do not set exit. Before its low-byte comparisons, original code compares full AX unsigned to23h, so0106h does not alias06h. Subdialog result0100h has zero AL and therefore continues. No claim is made that these numeric results are raw keyboard scancodes or any particular menu labels.

72 cases =6 distinct binaries ×12 fixtures. Cases cover06/15/16, subdialogs0e/23 with0/1,0e with0100/00ff, and unknown0106/24/00. Looping fixtures provide06 on the second selection. Tests assert render/selection count, exact subdialog path, one save, normal return and restored SP. Application dispatcher bytes execute unchanged. Five callsites are mocked: render, select, two subdialogs, save. No actual UI side effects or integration timing is asserted.

## Config field and writer inventory
Fresh Ghidra12.2 reference collection queries every byte of the16-byte config block and the save entry, then exports containing functions, decompilations and instruction bytes. `reference_index.csv` provides build,target,source,type,function,instruction; `coverage.json` reports export status. Multiple field references on REP copies reflect Ghidra's reference expansion, not separate executions. Indexed writes, immediate pointer loads and indirect accesses may be missed; zero xrefs cannot establish unused bytes.

Static evidence in supplied1.8/1.9 identifies a staged update routine1d25:1f66: it copies16 config bytes to a stack-local working copy, walks records of stride12h until record byte0==0, then copies16 bytes back. Record IDs0a/0b/0c/0d read signed word+2. Mapping below is Confirmed from original listing, not independently emulated here:

| Record ID | Magnitude byte relative to config | Enabled byte relative to config |
|---|---|---|
|0a|+04|+08|
|0b|+05|+0b|
|0c|+07|+0a|
|0d|+06|+09|

Magnitude stores low8(abs(signed16(value))); enabled is signed value>0. This is not saturation: values outside byte range truncate; -32768 remains8000h before AL truncation. Before commit the routine conditionally invokes helpers based on old/new+09 and+07, then copies the working record back and invokes further helpers. Their semantic names remain Unknown. The paired routine1d25:1ec4 populates signed record values from magnitude/enable pairs and returns low-byte acceptance status. Actual control labels and audio/device meanings require separate data/callee evidence; misleading Ghidra auto-string names are not trusted as UI labels. Cross-version field mapping beyond this cited1.8/1.9 routine has not yet been independently normalized.

## Evidence and limits
Per-case SHA256 and traces are in dispatch_tests.json. DS=SS,DF0,SPe000 fixtures. Fresh Ghidra decompilations are evidence aids; success is not full semantic recovery. Included pass76 dependency contains repaired project plus baseline runtime EXEs. To reproduce, extract nested baseline58, retain pass84 save_tests.json and pass85 refs.tsv, run python scripts/verify_config_save_dispatch.py with Unicorn2.1.4; expected12 passed per binary. ExportConfigReferences.java/seeds reproduce static inventory read-only in Ghidra12.2/JDK25.

Next: execute staged record conversion across signed boundaries, map record labels from resource data, resolve commit side-effect callees and prove whether menu acceptance invokes the staged commit before save. Full menu integration and real DOS persistence remain unverified.
