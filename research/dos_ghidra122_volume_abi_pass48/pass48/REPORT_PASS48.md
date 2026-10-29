# Volume backend ABI and interrupt request — pass48

216 original backend executions resolve pass47's argument-width question. Both volume components are read as bytes, so retained high argument bytes have no effect in this backend. Complete wrapper,original stack allocator,generic request wrapper and CRT interrupt marshalling execute; actual INT63 driver is replaced by an observation boundary that leaves registers unchanged.

Confirmed (High): V1.9 volume wrapper20bc:0540–058a reads byte BP+6 and byte BP+8,zero-extends each,shifts first by4 and ORs second. It does not apply0f masks. It invokes generic request20bc:0000 with command21 and packed value. Captured driver request: INT63,AX2100,BX=((left&255)<<4)|(right&255),CX0,DX0. Exact per-build entries,bodies and EXE hashes in volume.json.

Confirmed (High): input256 truncates to0;ffff truncates to255. For left/right38,packed BX0266,not a clean pair of four-bit components. This matters because dispatcher volume255 can calculate38 (pass47). Driver interpretation/clamping of this packed value is Unknown; do not infer hardware stereo levels from wrapper arithmetic alone.

Run `/usr/bin/python3 scripts/verify_backend_volume.py` with Unicorn2.x. Six distinct images × left/right values0/1/15/38/256/65535=216. Check exact interrupt register tuples,far return,SP and restored DS. Stackf800 permits original stack allocation. No callee-skipping mocks; INT63 handler itself does not execute. Supplied1.8/1.9 identical. Ghidra12.2 preserved exports used; no project database edits.

Implementation-ready: backend byte-width semantics resolve high-byte uncertainty from pass47. Preserve byte truncation,shift/OR packing and request registers; avoid assuming nibble clamp. Backend-dependent synchronization and actual driver output remain unresolved.

Next test: identify resident INT63 handler/driver interface and test request21 interpretation,then busy/stop/play requests and actual sample output. Whole audio,hardware and gameplay parity remain open. Confidence High for ABI/request construction,Unknown for driver behavior.
