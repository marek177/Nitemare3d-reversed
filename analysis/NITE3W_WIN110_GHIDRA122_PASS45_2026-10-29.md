# Win16 1.10 — Ghidra 12.2 pass45: palette cache initialization and DAC preservation

## Finding
Confirmed, High: EXE data initializes flag00C4 to1. The captured direct instruction references show only2AAC reading and clearing it. No new setter was found by that scoped audit.64 original3ACC executions preserve both this flag and all16 cache bytes while emitting the expected DAC sequence. Indirect setters and the GDI route remain unresolved.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Initial flag00C4=1 | NE10 data, EXE file2C104 | High |
| Confirmed | Captured direct references are2AB2 READ and2ABD WRITE | Native reference export | High |
| Confirmed | 3ACC emits769 byte-port writes, with source bytes shifted right2 | Original execution | High |
| Confirmed | 3ACC leaves flag00C4 and cache327E..328D unchanged |64 cases, flags0/1/80/FF | High |
| Unknown | Indirect/bulk writes that reset flag, GDI lifecycle and actual frame order | Not fully audited | Low |

## Behavior model
The initialized nonzero flag permits the first cache query to rebuild16 color indices. Original2AAC then clears the flag. Direct DAC output3ACC does not itself invalidate that cache. Thus a palette-output call must not automatically be modeled as a cache reset based solely on its purpose.

This is not proof that the cache is globally built only once. The reference export covers instruction references, not every indirect memory destination or startup/bulk copy. Actual Win16 runtime tracing is still needed to close that question. No setter is invented to fit an expected invalidation design.

## Verification
Original EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Initial flag read directly from file offset2C104 after NE10 base2C040.22 instruction encodings checked for3ACC.64 cases =4 initial flag values ×16 deterministic random768-byte palettes(seed45). TestCS2000,DS=SS1048,sourceoffset7000. No helper stubs. OUT hook records1 write(3C8,0), then768 writes(3C9,source>>2); all769 events checked. Cache16 bytes andflag unchanged,SP/BP restored. Port capture is not actual VGA hardware or displayed RGB output.

Static palette dispatcher3AF4 chooses3ACC when46B0 is nonzero, otherwise31AA. The GDI branch is not executed here, so the preservation finding is scoped to3ACC. Earlier cache-query tests already established that changing source palette bytes alone does not trigger2AAC whileflagzero; this pass adds actual initialized-state and DAC-path evidence.

## Implementation-ready findings
Initialize this cache flag from the verified data value and retain it across the recovered direct DAC routine. Keep automatic cache invalidation out of the reconstructed3ACC unless further evidence establishes it elsewhere. Direct-reference absence is a search result with limits, not proof of whole-program absence.

## Unknowns and next test
Audit indirect writes to00C4 and palette load callers, executeGDI31AA with controlled imports, then trace a real palette/cache/map sequence. Full Win16 rendering and first frame after LOAD remain open.1551 internal entries retain native decompile success;310 EXTERNAL entries separate;1401 undefined executable bytes remain unresolved.

## Confidence
High for initial byte and tested DAC preservation; limited for complete cache lifecycle.
