# Grouped-column invalidation — pass 34

## Finding
3,240 bounded original caller-loop executions confirm that changing texture columns invalidates a reused group early and produces the same final four-plane bytes as drawing each x independently. This dynamically closes the changed-column branch left static-only in pass33.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Changed texture-column result forces redraw before count expiry | V1.9 1201:06cd–06ef; controlled changing-column sequences | High |
| Confirmed | Final plane arrays equal scalar per-x sampling | All3,240 full four-plane comparisons | High for map-mask model |
| Confirmed | Threshold rightEdge-3 continues to keep drawn groups inside span | All consumer arguments/group sequences checked | High for tested coordinates |
| Unknown | Actual projection helpers generate these sequences in gameplay | Two controlled-output helper mocks | Unresolved |

## Behavior model
For each x, decrement remaining group count. Redraw if it reaches zero OR computed texture column differs from previous. On redraw reload remaining count from the original scaled-column return and remember current texture column. The earlier group may have written pixels ahead of x; subsequent changed-column redraw overwrites those future planes. Stable columns retain identical samples, so count-based reuse preserves final pixels in the tested setup.

The independent expected result draws every x separately from its own controlled texture column and fixed vertical projection. It does not reuse the original group decisions to construct the expected framebuffer. The original call sequence is additionally checked against the count/column state model.

## Verification
`/usr/bin/python3 scripts/verify_column_invalidation.py` with Unicorn2.x. Six distinct images × left0..3 × lengths1..9 × dy31/32/76 × five patterns (constant, alternating, increasing, pairs, one abrupt change) =3,240. Original reciprocal initializer, full viewport setter, caller inner loop and scaled-column consumer execute. Two projection/texture helper outputs are injected per x. Source bytes synthetic i%251; translation disabled; width304. Ordinary coordinates and valid table indices only.

Original OUT map masks update an explicit four-plane model initialized to a5. All four64KiB arrays compare against independent scalar pixel sampling, including unchanged bytes outside the span. Original consumer arguments, returned groups, caller stack and restored DS are checked. No full VGA device, scanout, DAC, timing, outer renderer traversal or actual resource textures tested. Per-case plane hashes and group traces in invalidation.json. Preserved Ghidra12.2 exports provide addresses; no project database edits. Supplied1.8/1.9 identical.

## Implementation-ready findings
Preserve early invalidation on changed column and remember the new return count; do not blindly skip the next group-size x values. Grouping is speculative replication that later changes can overwrite. Under this caller's rightEdge-3 contract and fixed tested vertical projection it yields scalar-equivalent final pixels.

## Unknowns and next test
Recover both projection/texture helpers rather than injecting their outputs. Vary per-x projected height to establish whether reuse checks also protect that dimension or whether caller constraints provide equivalence. Verify actual VGA setup before claiming hardware framebuffer parity. Menu limits remain open.

## Confidence
High for local changed-column invalidation and scalar-equivalent final plane bytes under stated constraints; no general renderer parity assertion.
