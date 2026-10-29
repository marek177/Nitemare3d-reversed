# Span notification map side effects — pass41

## Finding
The span preparation notification is a mode-dispatched map writer. 192 complete mode0 executions verify coordinate extraction and map writes;66 preparation scenarios then pass with original notification and interpolation, removing pass40's notification mock. Palette regeneration is bypassed by dirty flag0, not a code hook.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Notification mode0 reads color lookup2, extracts object coordinates and writes map bytes | V1.9 dispatcher183c:1442, mode0 target1470; lookup1277:0188, coords1fd5:02b2 | High |
| Confirmed | Map address is x*64+y, endpoint coordinates signed-shifted6 | Mode0 code and full4096-byte comparisons | High |
| Confirmed | Flags08 selects one-cell write using color lookup1 and segment global | V1.9 1499–14c5; cell-map DS2562 | High |
| Confirmed | Normal branch writes half-open axis segments using lookup2 into fixed far map | V1.9 179e–1808; map2c04:0000 | High |
| Inferred | Side effect marks map visibility/reveal state | Called when preparing visible spans, map writes and palette-related values | Medium; complete map display chain not traced |

## Behavior model
Mode0 first obtains lookup color2 from the original palette accessor (dirty0 skips regeneration). Coordinate extractor maps object words+0c/+0e/+10/+12 to x0,y0,x1,y1 via signed SAR6. Unless flags08 is set: orientation2 replaces both x endpoints with x0-1; orientation1 replaces both y endpoints with y0-1.

For flags08, coordinates stay unadjusted and writer stores lookup1 at x0*64+y0 through segment stored in DS2562. Otherwise it writes lookup2 into a fixed far4096-byte map: if x0==x1, vary y in[y0,y1); otherwise vary x in[x0,x1) at fixed y0. Zero-length segment writes nothing. Artificial diagonal endpoints follow the second path; this is not proof diagonal geometry is valid gameplay input. The function returns far map pointer DX:AX even on the single-cell branch (V1.9 2c04:0000).

## Verification
Run `/usr/bin/python3 scripts/verify_span_map_effect.py` first, then `/usr/bin/python3 scripts/verify_span_prepare_unmocked.py` with Unicorn2.x.192 tests: six images × orientations0..3 × flags0/08 × horizontal/vertical/zero/diagonal endpoints. Complete dispatcher mode0, coordinate extractor and palette accessor execute; compare entire cell/line maps plus far return, DS/SP. Synthetic lookup0..15 and dirty0.

66 follow-up ownership-run scenarios execute original preparation, producer and notification with no callee mocks; fatal hook only stops immediately before its handler. These synthetic owners have zero coordinate endpoints, so notification paths are exercised but lines empty; nonempty writes are established by the192 isolated cases. Count/records/failure boundary match pass40. Palette dirty branch, other dispatcher modes and complete scene traversal remain untested.

Exact per-build addresses/hashes and function bodies in map_effect.json; preparation evidence in preparation.json. Ghidra12.2 preserved exports used; no project database edits. Supplied1.8/1.9 are identical.

## Implementation-ready findings
Span preparation has a map side effect; do not model its notification as a universal no-op. Preserve x-major64 stride, half-open segments, flags08 cell path and orientation coordinate adjustments. Treat visibility/reveal naming as inferred until map display consumers are traced.

## Unknowns and next test
Trace palette regeneration and map display consumer, then distinguish visibility/color meanings. Exercise preparation with nonzero coordinate endpoints and actual scene owners. Other dispatcher modes, real VGA/DAC and menu limits remain open.

## Confidence
High for mode0 map writes and unmocked preparation under stated setup; medium for visibility semantics.
