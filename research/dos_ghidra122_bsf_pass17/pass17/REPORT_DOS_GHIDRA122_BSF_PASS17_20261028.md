# BSF pass17 — generic page viewer recovery, navigation and ownership

## Finding
Recovered one previously unowned generic BSF viewer function per distinct DOS image. Original code forwards its second word argument to BSF dispatch (modes3/5 tested), counts '#' page markers, navigates using key codes50h/48h, and releases the original far buffer once on ESC exit. Leading/repeated marker behavior is pointer-based and differs from a naive string split.

## Evidence
480 passing executions:8 inputs x modes3/5 x5 key sequences x6 images. Inputs: empty,A,A#B#C,#A,A##B,A#B#,real decoded mode3 resource,real decoded mode5 resource. Each sample is exercised with both injected dispatch modes to separate mode forwarding from input content. Key sequences:ESC;down/ESC;down/down/ESC;down/up/ESC;up/ESC.

Original full viewer control flow, marker scans, navigation and original far free execute in Unicorn. Dispatch pointer, key source, page-renderer and UI/formatting dependencies are mocked. Optional D/print branch is not selected. This proves pointer/page selection and release behavior under injected dependencies, not rendered pixels, keyboard hardware, DOS output or whole-game UI reachability. Buffers at5000:0200 have a synthetic80a5 header; original far free turns it into81a5. Tests assert dispatch mode, every renderer argument (far pointer,current page,total), exact key consumption, one free of the original pointer, far return/SP and DS restoration.

V1.9 entry1d25:144c; dispatch1d25:146b; initial renderer1d25:14c3; navigation renderer1d25:1561; key input1d25:14e4; free1d25:161b. The routine was present in pass7's unowned instruction inventory, not in the function table. Pass15 static caller catalog has17 direct references to its six build-specific entries. V1.9 callers include pushed dword00030010 (style16,mode3) at16af:06a6 and1d25:287c, and00050010 (style16,mode5) at1d25:1731. These references prove direct calls/arguments, not all runtime preconditions.

Exact per-build entries, call sites, hashes and renderer traces are in evidence/bsf_viewer.json. The original stock instruction bytes are unchanged by testing.

## Behavior model
Entry arguments: style wordSP+4,BSF mode wordSP+6. Initial page1; total word starts1 and increments for each '#' before NUL. Save original pointer for release. Initial renderer receives(original pointer,1,total).

Down key50h: scan starting one byte after current page pointer. If a later '#' is found before NUL, new pointer is one byte after it and page number increments, then renderer is called. Otherwise retain pointer/page. Up48h: if at original pointer, retain state; otherwise begin two bytes before current pointer, scan backward to '#' or original start, advance past marker unless at original start, decrement page number and render. ESC1bh exits through cleanup and original far free. Alternate49h/51h keys and D44h branch are statically present but not independently tested here.

Consequences directly tested: total includes leading/repeated/trailing markers. For '#A', total2 but down from original start finds no later marker and stays on page1. For 'A##B', down selects the second '#' as page pointer (empty page); another down skips that current marker and finds no later marker, so it does not reach B through another down. Trailing marker can select an empty final page. These quirks must be preserved if exact behavior is desired.

## Ghidra12.2 changes
Copied pass16 projects into pass17/projects. Created `BrowseBsfPages` at each call-backed unowned entry; added analytical void signature with two ushort arguments and evidence comments. Names are analyst labels, not original symbols. Existing function entries remain; exactly one new entry per image. Instruction address/byte inventory hashes match before/after. All6 new target stock C decompilations complete. No global decompiler-count rerun or complete semantic coverage claim. Eight previously unresolved candidate seeds remain retained.

Audit includes new function/body, creation flag, old/new function counts, invariant hashes, C and Ghidra logs. The six additions extend the prior3468-entry candidate inventory to3474; this is a function-table count, not a parity percentage.

## Confidence and next test
Confirmed/High for tested viewer navigation/ownership and Ghidra recovery. Unknown: actual page rendering/line parsing, UI state effects, D/print branch, alternate keys, malformed unterminated data, pointer wrap in this larger viewer, and runtime caller preconditions. Supplied1.8/1.9 remain identical. Next inspect/render helper and test line parsing separately, then integrate one actual BSF dispatch/load/view/free chain without pointer injection.

## Reproduce
`/usr/bin/python3 scripts/verify_bsf_viewer.py` (Unicorn). Inputs: pass7 specs/EXEs/instruction exports/decoded mode3+5 resources and pass15 recovered caller/free metadata. `python scripts/run_pass17_recovery.py` recreates project updates from pass16 with Ghidra12.2/JDK25 at configured paths. Updated projects are supplied in archive.
