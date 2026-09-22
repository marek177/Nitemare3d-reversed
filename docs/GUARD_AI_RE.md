# GUARD AI reverse engineering

Updated: 2026-09-22

Evidence: original NITE3W.EXE V1.10 Win16 binary (230400 bytes), reconstructed USER.SAV writer/layout, direct 16-bit disassembly/decompilation, executable developer/debug strings, original data files and controlled gameplay/video observations.

This document supersedes the earlier GUARD note where the damage producer, state dispatcher and score switch were still open targets.

## Fixed GUARD / OBJECT anchors

- GUARD stride: **0x1A = 26 bytes**, capacity **100**, base `0x93AE`, count `0x7E5E`.
- USER.SAV GUARD pool: `0xB43B..0xBE62`, 0x0A28 bytes = `100*26`.
- `GUARD+08` is an OBJECT slot/index; resolving `slot * 0x1C` reaches the associated 28-byte OBJECT record.
- OBJECT base `0x6D66`, stride `0x1C = 28`, capacity 350.
- `OBJECT+10/+12` are world X/Y; world-to-tile conversion uses arithmetic shift right by 6.
- `OBJECT+0C:+0E` is a map-cell far-pointer binding, not the world X/Y pair.
- `OBJECT+06` is the class used by the developer diagnostic, score switch and combat dispatch.

Evidence: **VERIFIED_EXE + VERIFIED_SAVE_LAYOUT**.

## Developer diagnostic unlocks GUARD semantics

NITE3W contains:

```text
class %d, strength %d, strategy %d
state %d, nextstate %d, timer %d
octant %d, resoct %d
```

The call site establishes:

| Field | Meaning | Status |
|---|---|---|
| `OBJECT+06` | class | VERIFIED_EXE |
| `GUARD+10` | strength / HP | VERIFIED_EXE |
| `GUARD+0A` | strategy | VERIFIED_EXE |
| `GUARD+0B` | state | VERIFIED_EXE |
| `GUARD+0C` | nextstate | VERIFIED_EXE |
| `GUARD+06` | timer | VERIFIED_EXE |
| `GUARD+11` | octant | VERIFIED_EXE |
| `GUARD+12` | resoct | VERIFIED_EXE |

## Current GUARD layout

| Offset | Width | Meaning | Status |
|---:|---:|---|---|
| `+00` | 2 | sequence/definition-derived value | PARTIAL |
| `+02` | 4 | timestamp/time value | VERIFIED_EXE |
| `+06` | 2 | timer | VERIFIED_EXE |
| `+08` | 2 | OBJECT slot/index | VERIFIED_EXE |
| `+0A` | 1 | strategy | VERIFIED_EXE |
| `+0B` | 1 | state | VERIFIED_EXE |
| `+0C` | 1 | nextstate | VERIFIED_EXE |
| `+0D` | 1 | o_id | VERIFIED_EXE |
| `+0E` | 1 | definition/sequence lookup result | PARTIAL |
| `+0F` | 1 | synchronization/control boolean | PARTIAL |
| `+10` | 1 | strength / HP | VERIFIED_EXE |
| `+11` | 1 | octant | VERIFIED_EXE |
| `+12` | 1 | resoct / result-octant field | VERIFIED_EXE |
| `+13` | 1 | transition parameter | PARTIAL |
| `+14..15` | 2 | unresolved | TODO |
| `+16` | 1 | transition/control flag | PARTIAL |
| `+17..19` | 3 | unresolved | TODO |

## Strength initialization and damage receiver

A direct write audit found:

1. normal GUARD creation writes `GUARD+10 = 0xFF`;
2. a second/special GUARD creation path also writes `0xFF`;
3. lethal damage clears `GUARD+10` to zero;
4. non-lethal damage subtracts from `GUARD+10`.

Equivalent verified control flow:

```text
damage = compute_damage(...)
if damage >= strength:
    strength = 0
    death_handler(...)
else if damage > 0:
    strength -= damage
    resoct = 8
    pain/state reaction
```

No class-indexed post-spawn strength initializer has been found. The strongest supported model is therefore that normal GUARD actors start at 255 and class/weapon-specific practical toughness is largely implemented in the damage producer/mitigation branches.

**Do not publish an invented `enemy -> starting HP` table.**

## Player -> GUARD damage producer is now recovered

The producer around `seg3:9FA2` is documented in detail in `COMBAT_DAMAGE_RE.md`.

It derives a geometry/projected base, adds `random()%25`, dispatches on `OBJECT+06` class, applies weapon/class-specific divisions/zero/special branches, applies difficulty scaling, then clamps the high end to 255.

Therefore the previous GUARD-AI TODO "find the damage producer" is obsolete. The remaining combat issue is exact visible-enemy binding for every class/special branch and attack cadence, not the existence of the damage transform.

## State dispatcher — states 0x00..0x15

The dispatcher around `3:7B55` accepts exactly 22 numeric states.

| State | Handler | Recovered behavior | Semantic status |
|---:|---:|---|---|
| `00` | `7BA2` | animation/timer; then `state=nextstate` | strong |
| `01` | `7BE0` | timer countdown; then `02` | strong |
| `02` | `7BFA` | active AI/animation with sound-type-3 path | PARTIAL |
| `03` | `7C3C` | detection/transition branch | PARTIAL |
| `04` | `7C86` | alternate detection/attack branch | PARTIAL |
| `05` | `7CE4` | helper transition | PARTIAL |
| `06` | `7CEC` | movement + timer; then `03` | strong control flow |
| `07` | `7D2A` | active AI; strategy 3 special branch | PARTIAL |
| `08` | `7D7E` | movement/AI; may enter `02` | PARTIAL |
| `09` | `7DEC` | special/collision action | PARTIAL |
| `0A` | `80A4` | no local action in dispatcher | strong |
| `0B` | `80A4` | no local action in dispatcher | strong |
| `0C` | `7E54` | shared handler | PARTIAL |
| `0D` | `7E54` | shared handler | PARTIAL |
| `0E` | `7E6C` | conditional transition to `0F` | strong control flow |
| `0F` | `7E9E` | timer/action; transitions `10` or `0E` | strong control flow |
| `10` | `7F26` | timer; then return `0F` | strong control flow |
| `11` | `7F8E` | movement + timer; then `strategy=0,state=07` | strong control flow |
| `12` | `7FEE` | wait for timer/animation; then `state=nextstate` | strong |
| `13` | `8038` | helper transition | PARTIAL |
| `14` | `804A` | long timer + periodic action | PARTIAL |
| `15` | `807E` | confirmed pain/hit reaction; returns to nextstate | VERIFIED/strong |

The numeric control flow is now known, but exact names such as `CHASE`, `ATTACK`, `SEARCH`, etc. must not be assigned to states 02..14 until their movement/animation/sound behavior is fully paired.

## Pain transition

The normal non-lethal hit path:

- subtracts positive damage from strength;
- writes `resoct = 8`;
- preserves the prior state into `nextstate`;
- sets current state to `0x15` for the pain/hit reaction;
- handler `0x15` restores `state=nextstate` after its timing/animation work.

Strategies 3 and 5 have distinct hit behavior and therefore remain important strategy-specific cases.

## Difficulty affects GUARD timing

Global `0x4C14` participates in GUARD timing as well as both damage directions:

```text
0 -> timer doubled / slower guard behavior
1 -> baseline
2 -> timer halved / faster guard behavior
```

Combined with recovered damage scaling:

| difficulty value | player -> guard | guard/object -> player | GUARD timing |
|---:|---:|---:|---:|
| 0 | x2 | /2 | slower |
| 1 | x1 | x1 | baseline |
| 2 | /2 | x2 | faster |

This strongly establishes the numeric order easier / baseline / harder.

## Per-GUARD score switch

The score function around `3:9F10` dispatches on `OBJECT+06` classes `0x08..0x20`, corresponding to GUARD1..25.

| OBJECT class | Guard | Name | Score |
|---:|---:|---|---:|
| `0x08` | 1 | Bat | 25 |
| `0x09` | 2 | Frankenstein | 75 |
| `0x0A` | 3 | Mummy | 50 |
| `0x0B` | 4 | Skeleton | 100 |
| `0x0C` | 5 | Mrs H. | 250 |
| `0x0D` | 6 | Zelda | 150 |
| `0x0E` | 7 | Vampira | 200 |
| `0x0F` | 8 | Baddie #1 | 100 |
| `0x10` | 9 | Baddie #2 | 100 |
| `0x11` | 10 | Dracula | 0 |
| `0x12` | 11 | Cemetery Gargoyle | 150 |
| `0x13` | 12 | Garden Gargoyle | 150 |
| `0x14` | 13 | unknown / apparently unused identity | 200 |
| `0x15` | 14 | Penelope | -1000 |
| `0x16` | 15 | Dr. Hamerstein | 1000 |
| `0x17` | 16 | Tall slim robot | 100 |
| `0x18` | 17 | Trashcan robot | 200 |
| `0x19` | 18 | Cannon | 0 |
| `0x1A` | 19 | Ghost | 25 |
| `0x1B` | 20 | Goldie | 100 |
| `0x1C` | 21 | Greenie | 100 |
| `0x1D` | 22 | Demon | 250 |
| `0x1E` | 23 | Alien #1 | 250 |
| `0x1F` | 24 | Alien #2 | 200 |
| `0x20` | 25 | unknown / apparently unused identity | 50 |

GUARD26/Dancers is outside the switch and follows the default zero-score path.

### Dracula clarification

The user's suspicion that Demon should not be zero was correct: Demon is **250**. Dracula's **0**, however, is directly present in the score switch and should be preserved. Dracula's scripted death/transformation relationship with Bat is a separate behavior path; Bat itself scores 25.

### Penelope clarification

Penelope's `-1000` is a real signed score result and is consistent with a protected/neutral-role penalty. That interpretation is descriptive; exact story/AI conditions should still come from the script/state audit.

## 28-byte OBJECT layout relevant to GUARD AI

| Offset | Width | Role | Status |
|---:|---:|---|---|
| `+00` | 1 | object/map ID | verified access |
| `+01` | 1 | subtype/variant-like value | PARTIAL |
| `+02/+03` | 2 | signed render/movement/animation components depending class | PARTIAL |
| `+04` | 1 | definition/resource-table ID | strong/partial semantic |
| `+05` | 1 | flags; `0x08` selects GUARD creation | VERIFIED_EXE |
| `+06` | 1 | class | VERIFIED_EXE |
| `+07` | 1 | GUARD index for guard objects | VERIFIED_EXE |
| `+08` | 4 | runtime value initialized zero | TODO semantic |
| `+0C:+0E` | 4 | map-cell far pointer/binding | VERIFIED_EXE |
| `+10` | 2 | world X | VERIFIED_EXE |
| `+12` | 2 | world Y | VERIFIED_EXE |
| `+14..19` | 6 | render/projection/runtime fields | PARTIAL/TODO |
| `+1A` | 1 | runtime byte initialized zero | TODO semantic |
| `+1B` | 1 | unresolved | TODO |

A separate mover resolves OBJECTs by `index*0x1C`, modifies world X/Y and updates map-cell state. It proves mutable integer world positions; final per-GUARD speed must still be tied to the specific state/movement dispatch.

## Dancers / special scripted GUARD behavior

GUARD26/Dancers is not just another class in the GUARD1..25 score switch. Data and gameplay evidence point to an E1M9 action-spot/dancing sequence with its own scripted behavior. Treat it as a separate reconstruction target rather than forcing it into the normal score/class matrix.

## Remaining GUARD/AI targets

1. Give exact semantic names to states 02..14 by following animation, movement and sound XREFs.
2. Recover every `strategy` value and its complete transition differences.
3. Trace movement-state writes to OBJECT X/Y and derive exact movement speeds/cadence.
4. Recover sight/FOV/LOS/hearing and the Omnificent perception/hostility gate.
5. Recover exact attack intervals and projectile/melee production.
6. Bind all alert/attack/pain/death SND.DAT IDs directly from original call sites.
7. Resolve GUARD13 and GUARD25 identity/use.
8. Reconstruct GUARD26/Dancers action-spot script completely.
9. Finish `GUARD+00..01`, `+0E/+0F`, `+13..19` semantics.
10. Cross-bind the enemy-to-player damage class table with these visible GUARD names.
