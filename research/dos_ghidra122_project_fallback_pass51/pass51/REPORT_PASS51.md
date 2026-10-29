# Pass 51 — supplied Ghidra project recovery and versioned sound fallback

## Finding
Confirmed: the supplied project opens in Ghidra 12.2. The large-sound fallback differs materially: DOS1.0/1.1/1.2 replace a dynamically allocated far buffer; DOS1.5/1.7/supplied1.8–1.9 return a fixed buffer, performing transfer only for lengths <=15000. Original fallback code passed 480 isolated executions across six distinct images.

## Project evidence
Source archive: upload/ghidra-n3d(1).zip, 22,895,212 bytes, 18 program entries. CRC passed in preceding intake. Work uses a separate copy, not the uploaded archive. Ghidra first rebuilt an inconsistent index journal; project owner metadata on the working copy was changed from the recorded Windows owner to the local user. The next read-only/noanalysis run opened all 10 DOS-named program entries successfully. Language version 4.9 was upgraded in memory then discarded by read-only processing. JDK25.0.2; Ghidra12.2 PUBLIC20261016. No semantic edits, renames or reanalysis were saved.

| Program entry | Existing functions | Existing instructions |
|---|---:|---:|
| DOS1.0 |509|29417|
| DOS1.1 |518|29987|
| DOS1.2 |531|30021|
| DOS1.5 |521|30079|
| DOS1.7 |527|29899|
| DOS1.8 |539|30728|
| DOS1.9 |539|30728|

These are inventory counts, not semantic completeness. The project records identical original executable SHA256 for 1.8/1.9. Reconstruction EXEs have different whole-file hashes from original-import metadata; compare code bytes instead. Seven 112-byte fallback samples match the unrelocated reconstruction MZ payload exactly. The supplied project retains unrelocated far-call segment words despite its 0x1000 image base; relocation-sensitive xrefs cannot be assumed correct. Execution tests explicitly relocate the MZ before running, as in prior passes. Repairing the supplied project relocation model remains a separate task. Exact metadata, blocks, functions and 112-byte fallback samples are preserved in per-program TSVs. DOS2.0 and aliases were inventoried, not behaviorally analyzed in this pass. Win16 entries were not opened in this run.

## Evidence and behavior
| Status | Claim | Location | Confidence |
|---|---|---|---|
| Confirmed | Old versions release an existing non-null far pointer, request resource-length bytes, store allocator DX:AX, fatal-call on null | 1.0 1bdd:0376–03c3; 1.1 1bff:039a; 1.2 1bff:039c | High, original branches with boundary mocks |
| Confirmed | Old versions pass the allocated pointer, raw signed source offset bit pattern, and length to the transfer callee; return saved pointer | 1.0 1bdd:03c6–03e4 and version-specific instructions in JSON | High |
| Confirmed | New versions compare unsigned length to15000; <= transfers, > skips; both return fixed far pointer | 1.9 1c27:03a2–03d9; 1.5/1.7 locations in JSON | High |
| Confirmed | Transfer AX=DX=ffff does not alter fallback return pointer | Same routines, hooked transfer return | High |
| Unknown | Allocation/release implementation, fatal handler termination details, actual asset reads, and reachable oversized resources | Callee boundaries mocked | — |

480 cases: old versions 3x8 lengths x4 signed offsets x2 old-pointer states x2 allocation outcomes=384; new versions 3x8x4=96. Lengths0,8192,8193,14999,15000,15001,32768,65535. Offsets0,123,-123,INT_MIN. Allocation mock returns6000:0200 or null; previous pointer6000:0100 or null. Fatal execution stops at the handler call; no claim about its internal behavior. Modern fixed buffers differ by version and are recorded exactly in JSON. Data-transfer results deliberately set AX/DXffff; actual copying is not executed.

## Implementation-ready findings
Keep version-specific fallback policies. Older code does not use the newer 15000 guard. Newer code returns its fixed pointer even when skipping an oversized transfer; this alone does not prove a gameplay bug or that such a resource is reachable. Callers must be reproduced according to their version rather than imposing a shared allocation policy.

Next discriminating test: integrate enabled sound dispatcher, original four-slot cache and original fallback with resident-driver INT63 boundary, then replace data-transfer mocks using real SND.DAT. Full-game playback, audio output and 1:1 parity remain unverified.
