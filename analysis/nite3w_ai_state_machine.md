# NITE3W AI state-machine audit — consolidated 2026-09-22

This file records the current GUARD state-machine reconstruction from the original NITE3W.EXE V1.10. It supersedes the early note that no numeric state handlers had been assigned.

## Confirmed runtime record

GUARD records are 26 bytes (`0x1A`), maximum 100, base `0x93AE`, count global `0x7E5E`.

The executable's developer diagnostic string directly names the following fields:

```text
class %d, strength %d, strategy %d
state %d, nextstate %d, timer %d
octant %d, resoct %d
```

The call-site argument order establishes:

| GUARD offset | Meaning | Status |
|---:|---|---|
| `+02` | dword timestamp/time | VERIFIED_EXE |
| `+06` | timer | VERIFIED_EXE |
| `+08` | associated OBJECT slot/index | VERIFIED_EXE |
| `+0A` | strategy | VERIFIED_EXE |
| `+0B` | state | VERIFIED_EXE |
| `+0C` | nextstate | VERIFIED_EXE |
| `+0D` | `o_id` | VERIFIED_EXE |
| `+0E` | definition/sequence lookup result | PARTIAL |
| `+0F` | sync/control boolean | PARTIAL |
| `+10` | strength / HP | VERIFIED_EXE |
| `+11` | octant | VERIFIED_EXE |
| `+12` | resoct / result-octant field | VERIFIED_EXE |
| `+13` | transition parameter | PARTIAL |
| `+14..15` | unresolved | TODO |
| `+16` | transition/control flag | PARTIAL |
| `+17..19` | unresolved | TODO |

### Important correction

The old early note described `GUARD+08` as a definition index. That was wrong. It is an OBJECT slot/index. The runtime resolves the associated 28-byte OBJECT record through the recovered object pool/indexing path. The visible/runtime class printed by the diagnostic is read from `OBJECT+06`.

## Strength / HP is now confirmed

`GUARD+10` is not merely a candidate field. Direct hit-receiver code:

- compares damage with `GUARD+10`;
- clears it to zero on lethal damage;
- subtracts non-lethal damage from it;
- normal and special GUARD creation write `0xFF`.

Therefore:

```text
fresh strength = 255
if damage >= strength:
    strength = 0
    death path
else if damage > 0:
    strength -= damage
    pain/reaction path
```

No class-indexed post-spawn strength initializer was found in the direct-write audit. Enemy-specific practical toughness is instead strongly affected by the player-weapon/class damage transform. Do not invent per-enemy starting HP values.

## State dispatcher

The dispatcher around `3:7B55` accepts states `0x00..0x15`, giving 22 numeric states.

Current branch-level map:

| State | Handler | Recovered behavior | Confidence |
|---:|---:|---|---|
| `00` | `7BA2` | animation/timer; on completion `state=nextstate` | strong |
| `01` | `7BE0` | countdown timer then state `02` | strong |
| `02` | `7BFA` | active AI/animation path with sound-type-3 call | partial semantic |
| `03` | `7C3C` | detection/transition branch | partial semantic |
| `04` | `7C86` | alternate detection/attack branch | partial semantic |
| `05` | `7CE4` | helper transition branch | partial semantic |
| `06` | `7CEC` | movement + timer; then state `03` | strong control flow |
| `07` | `7D2A` | active AI; strategy 3 has a separate branch | partial semantic |
| `08` | `7D7E` | movement/AI; can enter state `02` | partial semantic |
| `09` | `7DEC` | special/collision action | partial semantic |
| `0A` | `80A4` | no local action in dispatcher | strong |
| `0B` | `80A4` | no local action in dispatcher | strong |
| `0C` | `7E54` | shared handler with `0D` | partial semantic |
| `0D` | `7E54` | shared handler with `0C` | partial semantic |
| `0E` | `7E6C` | conditional transition to `0F` | strong control flow |
| `0F` | `7E9E` | timer/action; transition to `10` or back to `0E` | strong control flow |
| `10` | `7F26` | timer then return to `0F` | strong control flow |
| `11` | `7F8E` | movement + timer; then `strategy=0,state=07` | strong control flow |
| `12` | `7FEE` | wait for timer/animation then `state=nextstate` | strong |
| `13` | `8038` | helper transition | partial semantic |
| `14` | `804A` | long timer + periodic action | partial semantic |
| `15` | `807E` | confirmed pain/hit reaction; then `state=nextstate` | VERIFIED/strong |

The exact human-readable labels for states `02..14` remain deliberately unresolved until their animation, movement, attack, sight and sound callers are bound. Do not prematurely name every state `CHASE`, `ATTACK`, etc.

## Hit/pain transition

The non-lethal hit path provides useful state-machine evidence:

- `guard+0x10 -= damage`;
- `guard+0x12 = 8`;
- ordinary pain handling preserves the old state in `nextstate` and sets current state to `0x15`;
- handler `0x15` returns to `nextstate` after its animation/timer completion.

Strategies 3 and 5 have special hit behavior and therefore must remain explicit strategy cases rather than being flattened into one generic AI state model.

## Difficulty interaction

The same gameplay difficulty global used by combat also changes GUARD timing:

```text
difficulty 0 -> timer doubled / guards slower
difficulty 1 -> baseline
difficulty 2 -> timer halved / guards faster
```

Together with both directions of damage scaling this strongly establishes the numeric order 0=easier, 1=baseline, 2=harder even though final menu-label setter tracing remains separate.

## Score dispatch

The per-kill score switch is recovered for GUARD1..25. GUARD26/Dancers falls outside the switch and takes the default zero-score path.

```text
GUARD1  Bat                 25
GUARD2  Frankenstein       75
GUARD3  Mummy              50
GUARD4  Skeleton          100
GUARD5  Mrs H.            250
GUARD6  Zelda             150
GUARD7  Vampira           200
GUARD8  Baddie #1         100
GUARD9  Baddie #2         100
GUARD10 Dracula             0
GUARD11 Cemetery Gargoyle 150
GUARD12 Garden Gargoyle   150
GUARD13 unknown           200
GUARD14 Penelope        -1000
GUARD15 Dr. Hamerstein   1000
GUARD16 Tall slim robot   100
GUARD17 Trashcan robot    200
GUARD18 Cannon              0
GUARD19 Ghost              25
GUARD20 Goldie            100
GUARD21 Greenie           100
GUARD22 Demon             250
GUARD23 Alien #1          250
GUARD24 Alien #2          200
GUARD25 unknown            50
GUARD26 Dancers/default     0
```

Dracula's zero is a real value in this score switch. His scripted transformation/death behavior, including the Bat relationship observed elsewhere, must be reconstructed separately instead of changing the score constant.

## Definition and OBJECT indirection

GUARD state is per-instance. `GUARD+08` links the GUARD to an OBJECT record; the OBJECT carries class/resource/runtime information, including `OBJECT+06 class` used by combat and diagnostics.

This matters when reconstructing AI:

```text
GUARD instance state/timers/strategy
       |
       +--> associated OBJECT slot
                |
                +--> class / world position / animation-resource state
```

The engine therefore separates instance AI state from class/object data rather than storing every behavioral property directly in the 26-byte GUARD.

## 2026-09-22 comparative AI audit: patrol, octants, alert states

A comparison against the public `BBQGiraffe/OpenNitemare3D` reimplementation provides several useful search fingerprints. These are **heuristics only**, not proof of original NITE3W behavior; the public port is incomplete and contains placeholders.

### Eight-direction patrol is a strong search target

The public code models eight compass directions:

```text
N, NE, E, SE, S, SW, W, NW
```

and directional patrol actors change direction from map turning-point tiles. This aligns closely with the original executable diagnostic fields `octant` and `resoct` at `GUARD+11/+12` and raises the priority of tracing all 0..7 writes and mask/range checks around these fields.

Target reverse-engineering fingerprint:

```text
MAP/WALL tile class
    -> turning-point switch
    -> value 0..7
    -> GUARD octant/result-octant
    -> movement delta lookup
```

Finding this chain could identify patrol state, direction encoding, movement vectors and a map-trigger mechanism at once.

### Patrol and chase may use different movement abstractions

The public reimplementation uses eight directions for directional patrol but only four cardinal neighbors when selecting a chase step. This must not be copied into the reconstruction until verified in the original EXE. It does, however, define a concrete test:

- inspect movement callers for whether chase candidates are 4-way or 8-way;
- compare those callers with the `octant`/`resoct` path;
- determine whether octant is visual orientation only, patrol motion, or both.

### Alert/roar candidate state

The public reimplementation uses a high-level sequence `idle -> roar/alert -> chase`, with a class-specific alert sound and a short timer. The original executable has 22 lower-level states, so a likely original alert state should be identified by behavior rather than by copying the public enum.

Search for a state handler with this signature:

```text
entry from detection/idle
    -> class-dependent sound request
    -> short timer / animation
    -> transition into active movement/chase state
```

This is now a high-value semantic assignment target for states `02..14`.

### Public health/damage code is not authoritative

The public code initializes guard health to `100` and its plasma path can directly force a `dead` state. These are implementation placeholders and conflict with the original EXE evidence that newly created GUARD strength is `255` and that weapon/class damage transformation determines practical toughness. Therefore no HP values from the public port are to be imported into this audit.

## Expanded AI reconstruction TODO

### P0 — architecture and combat

1. Complete the full 26-byte GUARD field map; resolve `+14..15` and `+17..19`.
2. Build the complete write/read XREF graph for `GUARD+0B state` and record every transition condition.
3. Recover all 22 state handlers `00..15` and assign semantic names only after evidence from movement, sound, animation and combat callers.
4. Prove the exact role of `GUARD+0C nextstate` beyond confirmed pain/state-return use; test whether it acts as a generic one-level resume-state mechanism.
5. Enumerate every strategy value and build a `strategy -> reachable states / special transitions` matrix.
6. Search for a common `SetGuardState`-style helper or data-driven state-definition table.
7. Audit state-table candidates with 22 entries or 22 pointers and look for fields resembling handler, timer, sequence, sound or next-state.
8. Trace all writes to `GUARD+10 strength`; preserve the verified initial value 255 unless new executable evidence proves class-specific replacement.
9. Recover the full player-weapon x GUARD/OBJECT-class damage transform, including immunities/resistances/special cases.
10. Test whether projectile travel time/distance or impact distance participates in the final damage calculation.
11. Fully trace difficulty scaling for both player->guard and guard->player damage plus AI timers.

### P1 — sensing and movement

12. Trace every read/write of `GUARD+11 octant` and `GUARD+12 resoct`; identify direction encoding and 0..7 transforms.
13. Find direction delta tables and fixed-point/cardinal/diagonal movement constants.
14. Search the original MAP/WALL handling for 8-way patrol turning-point behavior.
15. Determine whether patrol and chase use separate movement algorithms/profiles.
16. Recover collision response after failed movement: retry axis, choose alternate octant, randomize, stop, or invoke special action.
17. Recover exact pursuit logic toward the player; determine whether there is pathfinding or greedy/local steering only.
18. Recover LOS trace and all MAP/WALL reads used by guard detection.
19. Recover FOV/octant-facing checks and whether enemies can detect behind themselves.
20. Recover detection distance/range thresholds by class/strategy.
21. Search weapon-fire/player-noise paths for guard alert propagation or hearing logic.
22. Identify the AI RNG source and thresholds used for attack, movement, direction changes, reaction delays or sound variation.
23. Recover exact attack decision chain: visibility, distance, strategy, timer, RNG and class gates.
24. Recover attack cooldown/cadence and convert timer units into real game-time units.
25. Determine whether distant guards sleep/deactivate or whether all active guards receive every AI tick.
26. Determine guard-to-guard collision rules and whether guards can block or overlap each other.
27. Determine whether guards share alerts or whether detection is entirely per-instance.
28. Determine whether chase preserves a last-known player position after LOS is lost.
29. Determine how doors, secret walls, push walls and teleporters affect guard movement and state.

### P2 — reactions, animation, sound and specials

30. Keep state `0x15` bound to pain/hit reaction, but enumerate every writer of `0x15` to exclude broader interrupt semantics.
31. Recover death-state chain: lethal hit, dying animation, corpse/removal and any state/resource conversion.
32. Bind each state to exact animation/sequence data and frame timing.
33. Bind alert/attack/pain/death sounds to original SND.DAT call sites and separate abstract sound request IDs from final SND indexes.
34. Reconstruct Dracula's special death/transformation path to Bat without altering the confirmed zero score constant.
35. Reconstruct GUARD26 dancers as a possible scripted/event actor path and identify class replacement mechanics.
36. Reconstruct Dr. Hamerstein boss-specific decisions, timings, attacks and death behavior.
37. Recover complete behavioral profiles for Demon, Greenie, Goldie, Tall Slim Robot and Trashcan Robot.
38. Determine enemy-projectile friendly-fire behavior and whether one guard can damage another.
39. Recover any class-specific environmental reactions or special wall/event triggers.

### P3 — hidden / unused behavior

40. Classify zero-XREF or unreachable state IDs, strategy values and guard classes.
41. Cross-reference unused IMG sequences against guard/state definitions for cut animations or enemies.
42. Cross-reference unused SND.DAT entries against AI/sound dispatchers for cut alert/attack/death behavior.
43. Search dead/debug code for developer AI modes, test guards, forced-state controls or instrumentation.
44. Determine the hard maximum number of active guards and whether the 100-entry GUARD pool is also the practical active-AI limit.
45. Search for map-event code that writes guard state/strategy/class directly, especially around dancer and transformation cases.

## Immediate next audit order

The highest-yield sequence is now:

```text
GUARD+0B all writes/reads
    -> transition graph
    -> common SetState/state-table search
    -> strategy matrix
    -> octant/resoct movement chain
    -> patrol turning-point map switch
    -> LOS/detection
    -> damage matrix + distance/difficulty transforms
    -> sound/animation bindings
```

The purpose of the TODO is not to force labels onto unknowns. Each item should move from `UNKNOWN` -> `PARTIAL` -> `VERIFIED_EXE` only when supported by original executable/data evidence.

## High-priority remaining AI work

1. Assign exact semantic names to states `02..14` only after animation/sound/movement XREFs are paired.
2. Recover all strategy values and their transition differences, not only special strategies 3 and 5.
3. Trace GUARD movement writes to OBJECT X/Y to obtain exact per-class speed/cadence.
4. Recover sight/FOV/LOS/hearing and the Omnificent hostility gate.
5. Recover exact attack scheduling and enemy/projectile producer identities.
6. Bind alert/attack/pain/death sound IDs directly to original SND.DAT call sites.
7. Resolve GUARD13/GUARD25 identity/use and the separate GUARD26 dancer script.
8. Finish the unresolved tail fields of the 26-byte GUARD record.
