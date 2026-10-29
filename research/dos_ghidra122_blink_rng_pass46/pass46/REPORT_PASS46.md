# Original RNG integration and companion wrapper — pass46

## Finding
576 state-machine tests now execute the original RNG wrapper,CRT generator,multiplication helper,DAC writer and companion wrapper without callee mocks. The downstream companion dispatcher is configured disabled through its original enable flag. Complete enabled dispatch/audio effects remain unresolved.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | RNG state update is (seed*0x343fd+0x269ec3) modulo2^32; result=(state>>16)&7fff | V1.9 wrapper1fb7:0194,CRT21ea:31fc–3223 and original multiply callee; dynamic seed checks | High |
| Confirmed | Only black transition consumes RNG in tested state grid | State machine plus before/after seed comparisons | High |
| Confirmed | Companion pushes dword20000 and word42 then calls gated dispatcher | V1.9 wrapper183c:0ea6–0eb6 ->1c27:03da | High |
| Confirmed | Disabled dispatcher returns before downstream effects | V1.9 DS414e=0; original branch executes | High for disabled path |
| Inferred | Companion likely requests sound rather than UI rendering | Gated dispatcher and call context | Medium; enabled backend not executed |

## Behavior model
Original RNG outputs are nonnegative0..32767, so the animation's signed remainder equals ordinary remainder for original generator results. Black duration remains160+(rand()%240). State is consumed only on that transition; resets,white transitions,countdown-only and gated calls leave RNG state unchanged.

The previous pass's analytical label UI helper is retired: exact wrapper behavior is dispatch(0x42,0x20000). Do not interpret that label as proven UI work. With dispatcher enable0, wrapper and dispatcher execute and return normally. No implementation code is skipped by hooks; hooks observe RNG/UI-named sites inherited from the test harness only. Enabled dispatcher effects and semantic ID meaning remain TBD.

## Verification
`/usr/bin/python3 scripts/verify_dac_blink_original_rng.py` with Unicorn2.x. Same576-case grid as pass45, but two injected RNG-return choices are replaced with initial32-bit seeds0/239 and original computation. Independent LCG oracle checks seed mutation and returned-dependent countdown. Exact DAC port events, dependency observations,timer/state,far return,SP/DS checked. Companion dispatcher enable byte0 set as explicit setup.

All six distinct supplied images tested;1.8/1.9 identical. Exact per-version RNG state addresses,original instructions and disabled-dispatch flag in original_rng.json. Ghidra12.2 preserved exports used; no project database edits. No original enabled audio backend,complete VGA device,scene timing or whole-game parity claim.

## Implementation-ready findings
Use original RNG sequence and consume it only on the black-transition branch. Keep reset/countdown/gating independent of RNG. Preserve the companion request on that branch; do not assume its behavior from the prior provisional UI name.

## Unknowns and next test
Trace enabled dispatcher backend,meaning of request42 and caller cadence. Direct V1.9 animation callsites include1bda:03a2(argument0) and1d25:16ce(argument1); these are static leads, not proof of tick timing. Establish scene role before assigning animation semantics.

## Confidence
High for original RNG integration and disabled companion path; enabled effects and cadence unresolved.
