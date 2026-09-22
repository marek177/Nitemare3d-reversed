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

## High-priority remaining AI work

1. Assign exact semantic names to states `02..14` only after animation/sound/movement XREFs are paired.
2. Recover all strategy values and their transition differences, not only special strategies 3 and 5.
3. Trace GUARD movement writes to OBJECT X/Y to obtain exact per-class speed/cadence.
4. Recover sight/FOV/LOS/hearing and the Omnificent hostility gate.
5. Recover exact attack scheduling and enemy/projectile producer identities.
6. Bind alert/attack/pain/death sound IDs directly to original SND.DAT call sites.
7. Resolve GUARD13/GUARD25 identity/use and the separate GUARD26 dancer script.
8. Finish the unresolved tail fields of the 26-byte GUARD record.
