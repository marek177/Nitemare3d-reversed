# Grouped projected-height approximation — pass38

## Finding
432 unmocked original inner-loop runs confirm that texture-column reuse does not invalidate on changed projected height alone. 222 cases differ from independently drawing each x with its own height; all432 agree exactly with an independent model of original grouped drawing. This refines pass37's fixed-height scalar equivalence.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Group reuse checks remaining count and texture column, not projected y | V1.9 1201:06cd–06ef, changing original record accumulator | High locally |
| Confirmed | Group can replicate first column's y to following x whose own y differs | Original unmocked chain; witness below | High |
| Confirmed | Final model-plane bytes differ from per-x-height scalar output in222/432 cases | Full four-plane comparisons; max648 differing bytes in sampled case | High for map-mask model |
| Unknown | Frequency and visible effect under actual gameplay records/assets | Synthetic record/coefficient setup | Unresolved |

## Behavior model
The caller reads the high word of a32-bit record accumulator into fixed-height local, adds record increment to the accumulator, derives y=center+(fixedHeight>>4), and computes texture column. If count remains nonzero and texture column is unchanged, no new draw occurs even if y changed. Already emitted replicated columns retain the prior draw's height/sampling.

V1.9 witness: left0,right3, initial fixedHeight527, increment1 per x; texture columns[4,4,4,4]. Draw groups(x,count,column,y): (0,2,4,112),(2,1,4,113),(3,1,4,113). x1 therefore retains y112 although its individual y is113. There are44 differing plane bytes against scalar output. First difference plane1 offset3680: original165(a5 initial fill), scalar15. This is a modeled-plane byte witness, not a screenshot or actual VGA scanout capture.

## Verification
`/usr/bin/python3 scripts/verify_column_height.py` with Unicorn2.x: six images × left0..3 × lengths4/9/20 × initial fixed heights527/1231 × increments0/1/16 =432. Width304, orientationFlag0, class3, orientation1, flags08, coefficients32767/32767, bias0, endpoint spans16/24, texture width64. Both original helpers execute; no callee mocks. Record accumulator update is original code. Source bytes i%251; no translation.

Two independent references serve distinct purposes: grouped reference checks exact original group arguments and all four64KiB arrays; scalar reference draws every x with its own computed y and records differences without treating them as emulator failures. All zero-increment controls have zero scalar differences. Per-case original planes, difference counts and first witnesses in height.json. CPU registers/stack and group sequence checked as in pass37.

Scoped VGA map-mask model only; no complete hardware, DAC, scanout, timing or gameplay reachability proof. Ghidra12.2 preserved exports supply addresses; no project database edits. Supplied1.8/1.9 are one identical image.

## Implementation-ready findings
For faithful local parity retain the grouping approximation: invalidate on texture-column change or count expiry, not automatically on y change. A mathematically finer per-x renderer can differ from original pixels. Pass34/37 scalar equivalence applies to their constant-height setup, not general sloped spans.

## Unknowns and next test
Trace accumulator/increment producers and actual scene records to determine reachable slopes. Compare grouped pixel output using actual texture assets and real VGA setup. Establish whether any other caller flags suppress grouping on particular surfaces. Menu limits remain open.

## Confidence
High for local approximation and synthetic plane differences; actual gameplay prevalence unknown.
