# Scaled-column caller contract — pass 33

## Finding
The single direct scaled-column callsite identified in each of six supplied DOS images passes `rightEdge-3` as the final argument. 648 bounded original caller-loop executions verify that returned groups stay within the right edge. This resolves the local apparent overrun from pass32 for this caller's tested contract.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Last argument is record.rightEdge minus3 | V1.9 1201:063e–0644 sets BP-1a; dword push BP-1c at06d7 passes translation flag and threshold | High |
| Confirmed | Inner loop advances x by1, decrements reuse count and redraws when exhausted or texture-column result changes | V1.9 1201:06cd–06ef and06f6 | High static; constant texture input tested dynamically |
| Confirmed | Returned groups fit the supplied right edge in648 original-loop tests | caller.json, original consumer executes | High within tested contract |
| Unknown | Full projection helper behavior and outer renderer state | Two helpers mocked; fragment setup synthetic | Unresolved |

## Behavior model
At V1.9 caller 1201:04f0, the tested inner-loop portion starts0639. It initializes reuse count1, threshold=record.word6-3, previous texture column0 and x=record.word2. It updates a per-column accumulator, calculates y relative to viewport center, calls projection/texture helpers, writes a per-column value, decrements reuse count and invokes the scaled-column routine if count reaches0 or current texture column differs from previous. A draw reloads count from returned AX and remembers texture column. Each loop advances x by1 while x<=rightEdge.

The scaled-column routine groups at most4 columns and only groups when x<=rightEdge-3. Therefore x+group-1<=rightEdge under ordinary signed coordinates without threshold arithmetic overflow. Near the end it falls back to one-column draws. Unclipped paths group at most2 but caller conservatively reserves4.

The prior analytical name xLimit is refined to `groupThreshold`; it is not a strict per-column clip boundary. The observed pass32 behavior with threshold0 still stands, but a caller rightEdge3 is consistent with that value.

## Verification
`/usr/bin/python3 scripts/verify_column_caller.py` with Unicorn2.x: six images × left0..3 × lengths1..9 × dy31/32/76 =648. Original reciprocal initializer, full viewport setter, caller inner loop and scaled-column consumer execute. Two projection/texture helpers return constant2; no loader required because source pointer is prepopulated. All actual consumer arguments, x/group sequences, threshold, stack and DS are checked. This exercises stable-column reuse and count expiry; the changed-column invalidation branch is statically identified but not dynamically tested here. No full renderer, outer object traversal or VGA hardware claim.

The direct-call catalog matches physical far targets from bytes, avoiding misleading segmented alias names. Exactly one direct callsite per image found in preserved Ghidra12.2 exports; this does not exclude indirect calls. Full fragment instructions and EXE hashes in caller.json. Supplied1.8/1.9 are one image. No project database edits.

## Implementation-ready findings
Pass a grouping threshold of rightEdge-3. Preserve per-x loop accounting and count reload from returned group size. Redraw on changed texture column even before count exhaustion. Do not add a strict threshold clamp to the callee based on pass32 alone.

## Unknowns and next test
Execute changed-texture-column sequences and inspect whether early redraw safely replaces prior grouped pixels. Recover the projection helpers and caller's actual texture bounds. Signed extreme right-edge arithmetic and indirect callers remain unverified. Framebuffer/DAC and menu width limits remain open.

## Confidence
High for local ordinary-coordinate caller contract; no whole-game safety or parity assertion.
