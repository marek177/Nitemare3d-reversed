# Map palette lookup regeneration — pass42

## Finding
30 scenarios (1,050 original accessor calls) recover sixteen target RGB colors, nearest-index selection, first-index tie handling and dirty-flag caching across six distinct DOS images. Complete accessor and squared-difference helper execute with no mocks; this closes the palette-regeneration arithmetic bypassed in pass41.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Regeneration searches all256 RGB entries for each of16 targets | V1.9 1277:0188–02a5 | High |
| Confirmed | Distance is sum of component-difference squares, not absolute differences | Original helper1fb7:0100 uses IMUL BX; dynamic oracle | High |
| Confirmed | Strictly smaller signed16 score replaces winner; ties retain first | V1.9 0270–0278 | High |
| Confirmed | Dirty nonzero clears flag and regenerates; dirty0 reuses existing indices | Source mutation/cache tests, flagsff/01/00 | High |
| Unknown | Full palette-source update path and actual DAC equivalence | Synthetic source palettes; no VGA/DAC execution | Unresolved |

## Behavior model
Targets0..7 use RGB component42 for bits4/2/1, else0, with target6 special(42,21,0). Targets8..15 use63 for set RGB bits,21 otherwise. For each target scan source palette indices0..255 in order. Candidate score is signed16 of sum((component-target)^2). Initialize best32767; replace only when score<best. Store winning index byte in sixteen-entry lookup.

For intended six-bit components0..63, squared sum<=11907, so ordinary squared Euclidean nearest color matches the implementation. Explicit eight-bit probes verify16-bit sum wrap and signed comparison; generic unbounded distance is not equivalent outside the six-bit domain. No claim that eight-bit source values are normal gameplay inputs.

After regeneration return lookup[low8(argument)], not a newly measured DAC color. Argument256 returns lookup0. Out-of-range low-byte indices beyond15 were not exercised. The accessor's relevant return is AL; upper AX is not assigned a semantic guarantee.

V1.9 source palette DS4a62, lookupDS3454, dirtyDS0244. Other builds' addresses/hashes in palette.json. Target2 selected at duplicate source index3 rather than200+2 in tie fixture, verifying first-index behavior. All-zero palettes choose index0 for all targets.

## Verification
`/usr/bin/python3 scripts/verify_map_palette.py` with Unicorn2.x. Six images × five fixtures: exact targets with duplicate/tie, grayscale, deterministic random six-bit, zeros and deterministic random eight-bit. Per scenario: dirtyff regeneration;16 cached reads; argument256 low-byte test; replace source with zeros then16 cached reads; dirty01 regeneration.35 calls each,60 total regenerations. Check all16 output indices, dirty reset, AL, far return, SP and DS. Complete original callee chain without mocks.

Source palette hashes, target triples and output lookups recorded. No real palette assets, map display consumer, DAC writes, scanout or full scene tested. Ghidra12.2 preserved exports provide addresses; no project database edits. Supplied1.8/1.9 identical.

## Implementation-ready findings
Separate semantic16-color target IDs from actual current-palette indices. Preserve first-index ties and dirty-controlled cache invalidation. Palette mutation requires the matching dirty flag to change lookup. Implement signed16 distance behavior if accepting raw byte palettes beyond6-bit domain.

## Unknowns and next test
Trace writers of source palette and dirty flag, then run map notification with regeneration enabled. Establish map display interpretation and actual palette loading/DAC path. Other dispatcher modes and whole-game framebuffer parity remain open.

## Confidence
High for lookup regeneration/cache behavior under tested palettes; hardware and real-game palette lifecycle unresolved.
