# Nitemare 3D — evidence baseline PASS001, 2026-11-04

This is a fresh, reproducible baseline from dosbox-n3d(20261103-105917).zip. It does not replace or claim to merge prior PASS reports not inspected in this session.

## Results

- Inventoried 20 EXEs (including two map editors); SHA-256 for every file.
- Captured nine packed DOS loader handoffs at load segment 0x1000, retaining raw input hashes and full 512 KiB post-unpack snapshots. Five hundred twelve KiB is the capture window, not the executable's proven image extent. Snapshots retain load-base relocation values and stale loader memory, so their hash is not a canonical executable hash.
- DOS reference N3D-UNFU.exe and N3D-E-20.EXE are byte-identical. Despite its name, UNFU contains the packed loader; direct disk-offset disassembly would analyze the wrong image.
- Parsed all nine NE files, preserving code/data segments, exports, relocation source chains and import ordinal records separately from DOS. Unallocated NE segments have no disk-backed bytes; the reported zero length encodes 64 KiB but is not a disk span.
- Found 238 DOS 2.0 and 968 Win 1.10 function candidates by recursive traversal from entry/call/export/relocated immediate far-control seeds. These are not proven totals. Indirect callbacks, PUSH CS/CALL/RETF conventions, tail calls, shared blocks and overlaps require further recovery.
- Generated 1,206 individual candidate dossiers and ASM listings, 55,507 per-function instruction rows (shared instructions may occur in several dossiers), 9,886 reference-to-file byte-signature comparisons, CFG instruction graphs, local decoder register metadata and unresolved-edge records.
- Audited DOS 0201:000A (100 byte writes at stride 18) and Win NE export ordinal 1 (returns AX=0x0250) individually. 256 randomized CPU cases plus 72 cross-version loop cases passed, 328 total. No original gameplay/runtime parity claim.
- The DOS loop differs across filename-labeled builds only in two DS address immediates within the matching 16-byte template; 100 records remain constant. Full record identity remains unknown. Win ordinal 1 body is identical across all eight supplied game NE files.

## Version identity caveats

DOS 1.5 is absent by filename. Version strings have not yet been validated against release provenance. N3D-E-18.EXE and N3D-E-19.EXE have identical whole-file SHA-256; these cannot establish independent 1.8-versus-1.9 behavior differences. NITE3W.EXE duplicates NITE3W - 16.EXE; nite3w1.exe and nite3w2.exe duplicate the labeled 1.10 reference. Packed N3d.exe reaches INT 21h during the generic unpack probe and was not analyzed as a recovered image.

## Completion accounting

All 1,206 candidates remain CANDIDATE_STATIC_PARTIAL. Confirmed exhaustive functions: 0; full boundary/alias proof: 0; verified complete program CFGs: 0; original gameplay runtime-verified functions: 0. Two bodies have local semantics and isolated-emulation evidence. No percentages or invented total function counts. Unmatched signatures remain UNKNOWN_MATCH, never automatically ADDED or REMOVED. Exact-byte signatures concatenate decoded reachable bytes and do not prove whole-function layout or semantic equivalence.

| File (filename claim) | Candidate functions |
|---|---:|
|N3D-10.exe|234|
|N3D-11.exe|234|
|N3D-12.exe|235|
|N3D-E-10.EXE|234|
|N3D-E-17.EXE|236|
|N3D-E-18.EXE|238|
|N3D-E-19.EXE|238|
|N3D-E-20.EXE|238|
|N3D-UNFU.exe|238|
|NITE3W - 13.EXE|961|
|NITE3W - 16.EXE|968|
|NITE3W - 18.EXE|968|
|NITE3W -10.EXE|961|
|NITE3W.EXE|968|
|nite3w - 110.exe|968|
|nite3w1.exe|968|
|nite3w2.exe|968|

## Reproduction

Python 3 with capstone==5.0.7 and unicorn==2.1.4. Extract package preserving inputs/ beside N3D_FUNCTION_RESEARCH/. From that parent directory run:

```
python N3D_FUNCTION_RESEARCH/TOOLS/unpack_probe.py
python N3D_FUNCTION_RESEARCH/TOOLS/research.py
python N3D_FUNCTION_RESEARCH/TOOLS/verify_functions.py
python N3D_FUNCTION_RESEARCH/TOOLS/finalize_pass.py
```

The original EXEs are supplied in inputs/. Loader emulation has an instruction budget, no gameplay service emulation. No Ghidra/IDA raw output is available: hand pseudocode is labeled accordingly. EFLAGS metadata in the automated database is a decoder bitmask, not a complete instruction semantics proof. FUNCTION_DATAFLOW.json is explicitly a placeholder for full interinstruction dataflow.

## Next unresolved work

Resolve indirect calls and callback tables; verify stack-sensitive PUSH CS/near CALL/RETF paths; recover tail/shared blocks; prove each candidate boundary; establish DS provenance for the 100-record initializer; validate Win16 selector/fixup behavior in the loader; import genuine Ghidra/IDA raw decompilation; validate per-version release identities. Compare neighboring versions and classify normalized assembly only after relocation-aware correspondence is proved. Gameplay tests remain required for behavioral parity.
