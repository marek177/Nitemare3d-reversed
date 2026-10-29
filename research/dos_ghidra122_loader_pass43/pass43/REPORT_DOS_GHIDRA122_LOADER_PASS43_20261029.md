# game.pal loading and DAC output — pass43

## Finding
48 original loader-chain tests recover palette-tail seeking,8-to6-bit conversion,exact DAC events and cache lifecycle. Original loader, DAC writer and nearest-color regeneration execute; file services are mocked. The loader does not set dirty before its lookup call.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | V1.9 opens game.pal and seeks -768 from end | String DS0245;1277:02a6–02dd; seek args captured | High |
| Confirmed | Reads768 individual bytes, shifts each memory byte right2 and ignores read count | V1.9 02f2–0313; prefix-read experiments | High under file mocks |
| Confirmed | DAC output is byte0 at3c8 then768 component bytes at3c9 | Original writer1156:012a–014e; exact OUT comparisons | High for port trace |
| Confirmed | Dirty0 keeps prior16 lookup bytes despite palette replacement; dirty1 regenerates | Original lookup chain, all48 cases | High |
| Confirmed | V1.9 initial image dirty byte is1 | Reconstructed EXE data DS0244 | High static |
| Unknown | Later source-palette/dirty writers and full startup/DAC device state | Not traced completely | Unresolved |

## Behavior model
Open palette file. Seek offset-768,origin2(end). For i0..767 call read(handle,palette+i,1), ignore returned count, shift destination byte right2. Call original DAC writer with source pointer, then lookup accessor0, then close. Thus selected data is the last768 bytes, not necessarily a whole-file palette from offset0.

A failed mocked read leaves preexisting destination byte165, which becomes41 after shift. This occurs once per destination; it is not repeated shifting of a single byte. The loop still performs all768 calls and emits all768 DAC components. Tests simulate successful seek with0 return; actual error paths/fatal handling are outside this pass.

Dirty lookup cache remains independent of hardware output. DAC writes always occur on successful loader path; nearest-color cache regenerates only if its prior dirty flag was nonzero. Initial V1.9 image byte1 supports the first-load expectation but does not prove every later palette reload invalidates it. No automatic stale-cache gameplay defect is claimed.

## Verification
`/usr/bin/python3 scripts/verify_palette_loader.py` with Unicorn2.x. Six images × initial dirty0/1 × available prefix lengths0/1/767/768 =48. Original loader and both callees execute. Mocks cover open(handle3),seek,read(prefix then0/no memory write),close. Captures exact read arguments, palette bytes, all769 OUT events, lookup indices, dirty reset, close occurrence, far return/SP/DS. Source bytes deterministic(i*37+11)&255; destination initiallya5; lookup initiallya5.

This verifies CPU port writes, not complete VGA/DAC behavior, actual files or framebuffer. Exact bodies/hashes in loader.json; Ghidra12.2 preserved exports used; no project database edits. Supplied1.8/1.9 identical.

## Implementation-ready findings
Implement file-tail selection, per-byte >>2 conversion, DAC event ordering and independent dirty cache semantics. A hardened reader may reject short input, but doing so changes this local original path. Keep initial dirty state distinct from runtime invalidation.

## Unknowns and next test
Trace all palette-source and dirty-flag writers, including aliases/indirect access. Verify DAC setter callers and palette fade/change paths, then real game.pal asset and startup sequence. DAC scanout and full-game parity remain unresolved.

## Confidence
High for loader-chain behavior under file mocks; actual DOS file errors, device state and complete lifecycle unknown.
