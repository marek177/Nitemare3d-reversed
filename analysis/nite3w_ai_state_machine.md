# NITE3W AI state-machine audit — consolidated 2026-09-22

This file records the current GUARD state-machine reconstruction from the original NITE3W.EXE V1.10. It supersedes the early note that no numeric state handlers had been assigned and the earlier assumption that GUARD13 was an unknown class.

## Confirmed runtime record

GUARD records are 26 bytes (`0x1A`), maximum 100, base `0x93AE`, count global `0x7E5E`.

The executable's developer diagnostic string directly names:

```text
class %d, strength %d, strategy %d
state %d, nextstate %d, timer %d
octant %d, resoct %d
```

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

The old note described `GUARD+08` as a definition index. It is an OBJECT slot/index. The runtime resolves the associated 28-byte OBJECT record, and the visible/runtime class printed by diagnostics is read from `OBJECT+06`.

## Strength / HP

`GUARD+10` is confirmed strength/HP. Direct code:

- compares incoming damage with `GUARD+10`;
- clears it to zero on lethal damage before death/special handling;
- subtracts non-lethal damage;
- normal and special creation write `0xFF`;
- Dracula's phase-change path restores `0xFF` for the transformed second phase.

```text
fresh strength = 255
if damage >= strength:
    strength = 0
    death/special path
else if damage > 0:
    strength -= damage
    pain/reaction path
```

No class-indexed post-spawn strength initializer was found. Enemy-specific practical toughness is instead strongly affected by class/weapon damage transforms plus special phase logic. Do not invent per-enemy starting HP values.

## State dispatcher

The dispatcher around `3:7B55` accepts states `0x00..0x15`, giving 22 numeric states.

| State | Handler | Recovered behavior | Confidence |
|---:|---:|---|---|
| `00` | `7BA2` | animation/timer; on completion `state=nextstate` | strong |
| `01` | `7BE0` | countdown timer then state `02` | strong |
| `02` | `7BFA` | active AI/animation path with sound-type-3 call | partial semantic |
| `03` | `7C3C` | detection/transition branch | partial semantic |
| `04` | `7C86` | alternate detection/attack branch | partial semantic |
| `05` | `7CE4` | helper transition branch | partial semantic |
| `06` | `7CEC` | movement + timer; then state `03` | strong control flow |
| `07` | `7D2A` | active AI; strategy 3 separate branch | partial semantic |
| `08` | `7D7E` | movement/AI; can enter state `02` | partial semantic |
| `09` | `7DEC` | special/collision/action path | partial semantic |
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

Human-readable labels for states `02..14` remain unresolved until animation, movement, attack, sight and sound callers are bound.

## Hit/pain transition

The ordinary non-lethal path:

- `guard+0x10 -= damage`;
- `guard+0x12 = 8`;
- prior state is preserved in `nextstate`;
- current state becomes `0x15`;
- state `0x15` returns to `nextstate` after animation/timer completion.

Strategies 3 and 5 have special hit behavior and must remain separate strategy cases.

## Difficulty interaction

```text
difficulty 0 -> timer doubled / guards slower
difficulty 1 -> baseline
difficulty 2 -> timer halved / guards faster
```

Together with both damage directions this establishes numeric order 0=easier, 1=baseline, 2=harder.

## Score dispatch

The per-kill score switch is recovered for GUARD1..25. GUARD26/Dancers falls outside the switch and takes the default zero path.

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
GUARD10 Dracula phase 1      0
GUARD11 Cemetery Gargoyle 150
GUARD12 Garden Gargoyle   150
GUARD13 Dracula-Bat       200
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
GUARD25 unresolved         50
GUARD26 Dancers/default     0
```

## Dracula phase transformation: class 0x11 -> 0x14

The old TODO “reconstruct Dracula's transformation to Bat” is now partially resolved at the executable state/class level.

A lethal hit to Dracula class `0x11` does not simply terminate the actor. The special path rewrites the associated OBJECT/GUARD:

```text
OBJECT+06 = 0x14
GUARD+10  = 0xFF
GUARD+0B  = 0x08
GUARD+0C  = 0x02
GUARD+06  = 1
sequence/frame-related value = 0x23
transformation event/sound request = 0x22
```

Thus GUARD13/class `0x14` is the internal Dracula-Bat second phase rather than an unrelated unused enemy. Dracula phase 1 gives 0 score; the transformed class gives 200 on final death. Normal Bat class `0x08` remains separate and gives 25.

What remains unresolved is the complete resource/animation/sound/corpse chain around this transition, not the existence or target class of the transformation.

## GUARD25/class 0x20

Class `0x20` remains visually unidentified. Current profile:

- strength 255;
- generic observed setup state `07`, next-state `02`, strategy 0;
- score 50;
- outside explicit player-damage resistance jump table `0x0C..0x1F`;
- no confirmed dedicated alert/attack/death SFX;
- no confirmed normal MAP spawn.

Best current classification: cut/unfinished/fallback class, INFERRED. Search every writer of `OBJECT+06 = 0x20` and orphan SEQDEF/IMG/SND references before naming it.

## Definition and OBJECT indirection

GUARD state is per-instance. `GUARD+08` links to an OBJECT record, which carries class/resource/runtime information including `OBJECT+06` and world position.

```text
GUARD instance state/timers/strategy
       |
       +--> associated OBJECT slot
                |
                +--> class / world position / animation-resource state
```

Relevant new OBJECT audit point: `OBJECT+18` is read by player->GUARD damage as a projected/view-space vertical baseline; it is not world Y.

## 2026-09-22 comparative AI audit: patrol, octants, alert states

A comparison against the public `BBQGiraffe/OpenNitemare3D` reimplementation provides search fingerprints only; it is not proof of original behavior.

### Eight-direction patrol search target

The public code models N, NE, E, SE, S, SW, W, NW. This aligns with original `octant`/`resoct` fields at `GUARD+11/+12` and motivates tracing every 0..7 write/range check.

Target fingerprint:

```text
MAP/WALL tile class
    -> turning-point switch
    -> value 0..7
    -> GUARD octant/result-octant
    -> movement delta lookup
```

### Patrol and chase may use different movement abstractions

The public reimplementation uses eight directions for directional patrol but four cardinal neighbors for chase selection. Do not copy this until verified; instead compare original movement callers and octant/resoct use.

### Alert/roar candidate state

Search original handlers for:

```text
entry from detection/idle
    -> class-dependent sound request
    -> short timer / animation
    -> transition into active movement/chase state
```

### Public health/damage code is not authoritative

The public port's 100 HP initialization conflicts with original EXE evidence for 255. No HP values from that port should be imported.

## Expanded AI reconstruction TODO

### P0 — architecture and combat

1. Complete the 26-byte GUARD field map; resolve `+14..15` and `+17..19`.
2. Build complete read/write XREF graph for `GUARD+0B state`.
3. Assign state names only after original movement/sound/animation evidence.
4. Prove complete role of `nextstate` beyond pain-return use.
5. Enumerate every strategy value and reachable-state matrix.
6. Search for a common SetGuardState-style helper or data-driven table.
7. Audit 22-entry table candidates for handler/timer/sequence/sound/next-state fields.
8. Preserve verified fresh strength 255 unless new executable evidence proves replacement.
9. Keep the recovered player-weapon x class damage matrix synchronized with AI docs.
10. Trace exact influence of projected geometry/distance on damage through `OBJECT+18`.
11. Keep difficulty scaling synchronized across both damage directions and timers.

### P1 — sensing and movement

12. Trace every read/write of octant and resoct; identify 0..7 direction encoding.
13. Find direction delta tables and movement constants.
14. Search MAP/WALL handling for patrol turning-point behavior.
15. Determine whether patrol and chase use separate movement profiles.
16. Recover collision response after failed movement.
17. Recover pursuit logic/pathfinding vs greedy steering.
18. Recover LOS trace and MAP/WALL reads.
19. Recover FOV/facing checks.
20. Recover class/strategy detection ranges.
21. Search weapon-fire/player-noise paths for hearing/alert propagation.
22. Identify AI RNG source and thresholds.
23. Recover attack decision chain.
24. Recover attack cooldown/cadence in real time.
25. Determine distant-guard sleep/deactivation behavior.
26. Determine guard-to-guard collision/overlap rules.
27. Determine shared-alert behavior.
28. Determine last-known-player behavior after LOS loss.
29. Determine AI interaction with doors, secret walls, push walls and teleports.

### P2 — reactions, animation, sound and specials

30. Enumerate every writer of pain state `0x15`.
31. Recover full death chain: dying animation, corpse/removal and conversions.
32. Bind each state to sequence/frame timing.
33. Bind alert/attack/pain/death sounds to original SND.DAT call sites.
34. **Dracula target updated:** class transform `0x11 -> 0x14` and HP/state reset are resolved; finish resource/sequence/sound/corpse semantics.
35. Reconstruct GUARD26 dancer script and class replacement mechanics.
36. Reconstruct Hamerstein boss decisions, vulnerability state, attacks and death behavior.
37. Recover profiles for Demon, Greenie, Goldie, Tall Slim Robot and Trashcan Robot.
38. Determine enemy-projectile friendly fire.
39. Recover class-specific environmental reactions/special triggers.

### P3 — hidden / unused behavior

40. Classify unreachable state IDs, strategy values and guard classes.
41. Cross-reference unused IMG sequences against guard/state definitions.
42. Cross-reference unused SND entries against AI dispatchers.
43. Search dead/debug code for AI test modes/instrumentation.
44. Determine practical active-AI limit vs 100-entry GUARD pool.
45. Search map-event code that writes state/strategy/class directly, especially dancer, Dracula morph and GUARD25 cases.

## Immediate next audit order

```text
GUARD25/class 0x20 writers
    -> orphan sequence/IMG/SND binding
Dracula 0x11->0x14 resource chain
    -> final corpse/removal path
GUARD+0B all writes/reads
    -> transition graph
    -> strategy matrix
    -> octant/resoct movement chain
    -> LOS/detection
    -> attack timing/projectiles
    -> sound/animation bindings
```

## High-priority remaining AI work

1. Assign exact semantic names to states `02..14` only after original XREF evidence.
2. Recover all strategy values and transition differences.
3. Derive exact per-class movement speed/cadence.
4. Recover sight/FOV/LOS/hearing and Omnificent hostility gate.
5. Recover exact attack scheduling and projectile identities.
6. Bind alert/attack/pain/death sound IDs to original SND.DAT call sites.
7. Resolve GUARD25 reachability/identity and GUARD26 dancer script.
8. Finish unresolved tail fields of the 26-byte GUARD record.
9. Finish Dracula-Bat resource/sound/corpse chain while preserving resolved class/HP/state facts.
