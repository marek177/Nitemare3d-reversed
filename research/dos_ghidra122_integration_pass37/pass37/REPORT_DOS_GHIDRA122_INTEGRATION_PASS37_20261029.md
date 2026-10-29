# Unmocked column pipeline integration — pass37

## Finding
2,304 original-code executions connect the bounded caller loop, both helpers, reciprocal generation, full viewport setter and scaled-column drawing without callee mocks. Independent arithmetic-to-pixel reference agrees with final four-plane map-mask bytes in every case.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Original projection helper and edge helper compose into expected texture columns | Pass35/36 formulas, original caller arguments and integrated runs | High within synthetic inputs |
| Confirmed | Orientation selects distinct endpoint axes correctly | Object spans16 and24, orientations0..3; final column/pixel comparisons | High |
| Confirmed | Grouped original output equals scalar per-x arithmetic/sampling | All2,304 complete four-plane array comparisons | High for model |
| Unknown | Outer renderer produces these exact record/global combinations and valid bounds | Synthetic fragment initialization | Unresolved |

## Behavior model
The caller computes signed projected position, adds its local offset, optionally negates, applies class/orientation-specific edge corrections and width mask, then groups draws using count and texture-column invalidation. The integrated test uses zero local offset and no negation/translation, leaving those previously tested branches outside this integration scope.

Independent reference reproduces the pass35 signed32 arithmetic, pass36 edge model and pass31 scalar sampling. It draws each x separately to construct expected planes; original group decisions are checked separately. Original helpers execute normally; code hooks observe consumer arguments/return and stop at the end of the bounded loop only.

## Verification
`/usr/bin/python3 scripts/verify_column_integration.py` with Unicorn2.x. Six distinct images × left0/3 × lengths1/4/9 × dy32/76 × orientationFlag0/1 × class2/3 × object orientation0..3 × bit08 clear/set =2,304. Width304, projection coefficients100/200, local bias1234567, endpoint-axis spans16/24, texture width64, fixed height per span. Original setter supplies C/D. Source bytes synthetic i%251. No callee return or instruction skipping mocks.

Checks: all original scaled-column arguments, return group sequence and span bounds, caller SP/DS, all four64KiB model planes including unchanged bytes. Per-case hashes/groups in integration.json. Real-mode reconstruction hashes and fragment instructions included. Ghidra12.2 preserved export supplies addresses; no project database edits. Supplied1.8/1.9 share one EXE.

## Implementation-ready findings
The recovered arithmetic, edge masking, count-based grouping and column-change invalidation form a reproducibly verified local pipeline. Preserve all signed wrapping/division and edge ordering. Both helper mocks from pass34 are removed in this integration test.

## Unknowns and next test
Vary projected height per x and trace its interaction with group reuse; this test holds height fixed. Recover outer record producers and valid scale/coordinate limits. Full VGA setup, hardware scanout, DAC, original assets and whole-game framebuffer parity remain unverified. Menu viewport limits are still open.

## Confidence
High for integrated local algorithm under stated synthetic setup; no whole-renderer or gameplay parity assertion.
