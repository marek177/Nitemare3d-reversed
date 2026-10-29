# Two-index DAC animation state machine — pass45

## Finding
576 original state-machine executions recover two-index black/white DAC animation and gating/countdown branches across six distinct DOS images. Original single-entry DAC writer executes; RNG and one UI-related helper are mocked. Gameplay meaning is not yet established.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | State machine updates DAC index235 and one byte-selected index | V1.9 183c:1cea–1db6; exact OUT traces | High |
| Confirmed | Mode2 bypasses; mode3 bypasses when signed16(levelWord+1)<10 | V1.9 1ced–1d05; tests mode0/2/3 and level8/9 | High within sampled values |
| Confirmed | Reset sets counter80,state0, writes both entries black, without UI call | Original branch and576-case grid | High |
| Confirmed | Post-decrement tests prior counter, so old1 becomes0 without transition | V1.9 1d32–1d3b | High |
| Unknown | Semantic mode/level names, actual cadence and UI helper effect | Synthetic state and mocked helper | Unresolved |

## Behavior model
After gating, nonzero reset argument sets counter80 and state0, writes RGB0 to both entries and returns. Otherwise save old counter, decrement word with wrap. If old counter!=0, return. If old counter==0 and state0, set state1,counter3 and write RGB255 to both entries. If old counter==0 and state nonzero, set state0, get RNG, counter=160+signed_remainder(RNG,240), write RGB0 to both entries and call UI helper.

Tests inject only nonnegative RNG0/239, confirming counter160/399. Negative RNG behavior is statically signed but not dynamically tested here. Exact calls until next transition include the old-zero check: counter3 takes four subsequent enabled invocations to transition;80 takes81. These are enabled function calls, not measured milliseconds or engine ticks. Gated calls leave state/count unchanged.

V1.9 globals: gating modeDS6268, levelWordDS626a, counterDS3632, stateDS3634, second indexDSd2f5. UI helper called at183c:1d7f only on black transition; reset bypasses it. Software palette synchronization at the UI helper is not excluded because that helper is mocked. The DAC writer alone has no such synchronization (pass44).

## Verification
Run `/usr/bin/python3 scripts/verify_dac_blink.py` with Unicorn2.x. Six images × mode0/2/3 × level8/9 × reset0/1 × counter0/1 × state0/1 × RNG0/239 =576. Original state machine and DAC callee execute. Two dependency mocks inject RNG and skip UI helper. Check exact ports, dependency ordering, timer/state, far return, SP and DS. Synthetic second index17. White values255 are emitted bytes; actual DAC hardware conversion/masking is not modeled.

Function bodies, hashes and per-case traces in blink.json. Preserved Ghidra12.2 exports used; no project database edits. Supplied1.8/1.9 identical. No whole-game animation timing, visible effect or framebuffer/DAC parity claim.

## Implementation-ready findings
Keep old-counter testing, branch-specific UI call, gates, two palette indices and per-invocation countdown. Do not translate these counters into time without tracing caller cadence.

## Unknowns and next test
Trace state-machine callers, gating-global writers and dynamic second-index producer. Recover UI helper and run original RNG chain. Establish actual invocation cadence and scene role before assigning a gameplay name.

## Confidence
High for local state transitions under stated mocks; gameplay role/cadence unresolved.
