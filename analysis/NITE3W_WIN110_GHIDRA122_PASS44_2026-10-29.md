# Win16 1.10 — Ghidra 12.2 pass44: nearest-color cache construction

## Finding
Confirmed, High: original2AAC builds16 cached palette indices using squared component distance over236 candidates, with lowest-index tie preference.67 rebuild fixtures and1072 subsequent cached queries pass with original323E square helper and no stubs. Changing the palette without setting00C4 leaves the cache unchanged locally.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Nonzero00C4 triggers a complete16-entry rebuild, cleared before looping | 2AB2..2AC1 | High |
| Confirmed | Candidate indices10..245 use236 triples starting5B9C | 2B3E..2BB1 | High |
| Confirmed | Palette components are shifted right2 before comparison | 2B49..2B88 | High |
| Confirmed | Helper323E squares its signedWORD input; scores sum3 squares | Original323E and2B96..2B9C | High |
| Confirmed | Only strictly smaller score replaces best; ties retain earliest index | 2B9E..2BA6 | High |
| Confirmed | Cache327E..328D survives palette changes while00C4 remainszero | 1072 cached queries | High |
| Unknown | Which actual palette assets and invalidation events occur in a complete frame | Not used/executed | Low |

## Behavior model
For targeti0..15, compare each candidate's three byte components shifted right2 against the following targets. Indices0..7 use component0/42 selected by bits4/2/1; target6 is special(42,21,0). Indices8..15 use component21/63 selected by the same bits. Thus target8 is(21,21,21), target15(63,63,63).

Score is sum((component-target)^2). All component values lie0..63, so score<=11907 and the initial signedWORD best32767 is sufficient. Each candidate index increases from10 through245. Strictless replacement produces deterministic lowest-index ties. Uniform palette fixtures therefore select10 for all16 targets. Cache stores BYTE indices, not RGB triples.

At return the BYTE argument indexes327E directly; this test restricts inputs0..15. No general index guard is claimed. Rebuilding occurs once per nonzero invalidation flag; a cached query does not inspect palette contents.

## Verification
EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.122 instruction comparisons before controlled selector relocation. Original2AAC executes with original323E, test code selectors2000/4000, DS=SS1048.67 palettes: uniform0,255,84 and64 deterministic random236-entry palettes(seed44). Rebuild flags cycle1/128/255. For every palette, compare all16 cache bytes, flag cleared, cache-neighbor sentinels and returned target2. Then replace source palette with zeros without invalidation and queryall16 indices; results remain cached.1139 original2AAC calls total. ReturnIP,SP,BP checked. No helper stubs or OS services.

## Implementation-ready findings
Use squared distance rather than absolute-component distance, quantize source bytes with>>2 before scoring, restrict candidates to10..245 and preserve first-match ties. Keep cache invalidation explicit; inspecting or changing palette bytes alone is not equivalent to setting00C4. This supplies the previously excluded cache-build behavior for map colors, without proving actual palette assets or full map presentation.

## Unknowns and next test
Trace writers of00C4 and actual palette load/update paths; integrate a rebuilt cache withB1A4/map output. Planar renderer and actualWin16frame parity remain open.1551 internal entries retain native decompile success;310 EXTERNAL entries separate;1401 undefined executable bytes remain unresolved.

## Confidence
High for the tested cache algorithm and local invalidation contract, limited for complete game palette lifecycle.
