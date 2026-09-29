# GUARD AI reverse engineering

Updated: 2026-09-29

Evidence: original NITE3W.EXE V1.10 Win16 binary (230400 bytes), reconstructed USER.SAV writer/layout, direct 16-bit disassembly/decompilation, executable developer/debug strings, original data files and controlled gameplay/video observations.

This document supersedes earlier GUARD notes where the damage producer, state dispatcher, GUARD13 identity and score switch were still open targets.

## Fixed GUARD / OBJECT anchors

- GUARD stride: **0x1A = 26 bytes**, capacity **100**, base `0x93AE`, count `0x7E5E`.
- USER.SAV GUARD pool: `0xB43B..0xBE62`, 0x0A28 bytes = `100*26`.
- `GUARD+08` is an OBJECT slot/index; resolving `slot * 0x1C` reaches the associated 28-byte OBJECT record.
- OBJECT base `0x6D66`, stride `0x1C = 28`, capacity 350.
- `OBJECT+10/+12` are world X/Y; world-to-tile conversion uses arithmetic shift right by 6.
- `OBJECT+0C:+0E` is a map-cell far-pointer binding, not the world X/Y pair.
- `OBJECT+06` is the class used by developer diagnostics, score dispatch and combat dispatch.
- `OBJECT+18` is read by the player->GUARD damage producer as a projected/view-space vertical baseline. It is **not** world Y. Exact writer-level semantic name remains PARTIAL.

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

A direct write audit establishes:

1. normal GUARD creation writes `GUARD+10 = 0xFF`;
2. a second/special GUARD creation path also writes `0xFF`;
3. the Dracula transformation path restores `GUARD+10 = 0xFF` for the transformed second phase;
4. lethal damage normally clears `GUARD+10` to zero before death/special handling;
5. non-lethal damage subtracts from `GUARD+10`.

Equivalent normal control flow:

```text
damage = compute_damage(...)
if damage >= strength:
    strength = 0
    death_or_special_handler(...)
else if damage > 0:
    strength -= damage
    resoct = 8
    pain/state reaction
```

No class-indexed post-spawn strength initializer has been found. The strongest supported model is therefore that normal GUARD actors start at 255 and practical toughness is largely implemented in the damage producer/resistance branches and special phase logic.

**Do not publish an invented enemy->starting-HP table.**

## Player -> GUARD damage producer

The producer around `seg3:9FA2` is documented in `COMBAT_DAMAGE_RE.md`.

Its base is:

```text
base = ((OBJECT+18) - global_53EE) * 8
base += random() % 25
```

It then dispatches on `OBJECT+06`, applies weapon/class-specific divisions, zero-damage and boss-special branches, applies difficulty scaling and clamps the positive high end to 255.

This means a simple fixed “number of bullets to kill enemy X” table is not universally correct without also fixing projection/distance, RNG, weapon and difficulty.

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
| `09` | `7DEC` | lethal death/special finalization | strong |
| `0A` | `80A4` | finalized-death terminal state; no local dispatcher body | strong |
| `0B` | `80A4` | no local action in dispatcher | strong |
| `0C` | `7E54` | dormant retail branch; sequence refresh only; USE retains `I've nothing left!` | VERIFIED reachability classification |
| `0D` | `7E54` | dormant sibling branch; same sequence-refresh handler | VERIFIED reachability classification |
| `0E` | `7E6C` | conditional transition to `0F` | strong control flow |
| `0F` | `7E9E` | timer/action; transitions `10` or `0E` | strong control flow |
| `10` | `7F26` | timer; then return `0F` | strong control flow |
| `11` | `7F8E` | strategy-1 dynamic-door maneuver; then `strategy=0,state=07` | strong |
| `12` | `7FEE` | lethal wait/animation path; then `state=nextstate` (death path uses 09) | strong |
| `13` | `8038` | helper transition | PARTIAL |
| `14` | `804A` | E1M9 Radio/Dancers scripted movement state | strong/scripted |
| `15` | `807E` | confirmed pain/hit reaction; returns to nextstate | VERIFIED/strong |

Exact labels such as CHASE/ATTACK/SEARCH are intentionally not assigned to states 02..14 until movement, animation and sound XREFs close the semantics.

### State 0x0C / 0x0D reachability closure — 2026-09-29

A writer/read audit changes the status of these two states. They are **not normal active AI states in the recovered retail graph**.

For Win16, the audited 1.3, 1.6, 1.8 and 1.10 C exports all retain the same state-`0x0C` USE check, but none contains a recovered direct writer of current state `0x0C` or `0x0D`. In 1.10 the only three raw calls to the common state/sequence setter `3:762C` construct ordinary animation/death/reaction transitions; none supplies `0x0C` or `0x0D` as the new current/next state. The direct `nextState` writers likewise do not introduce either value.

For DOS the same residual state-`0x0C` interaction check exists in the audited exports:

| DOS build | residual state-0x0C interaction helper |
|---|---|
| 1.0 | `FUN_1000_8C46` |
| 1.7 | `FUN_1000_8F56` |
| 1.8 | `FUN_1000_90BA` |
| 1.9 | byte-identical executable to the audited 1.8 build, therefore the same code image |
| 2.0 | `FUN_1000_90C4` |

The audited DOS writer sets also contain no recovered literal current-state writer for `0x0C` or `0x0D`.

The surviving Win16 USE hook `3:AB3E` resolves a GUARD and displays **"I've nothing left!"** only when current state is `0x0C`. This is the only user-facing semantic directly tied to `0x0C`. Both `0x0C` and `0x0D` otherwise share `3:7E54`, which merely forces the normal directional/sequence refresh and does not leave the state.

**Classification:** `0x0C` and `0x0D` are **retail-dormant / legacy-compatible states** in the recovered normal graph. A crafted save, corrupted state, or an as-yet-unrecovered external memory write could still place a GUARD there, so this is not a claim that the numeric handlers are impossible to execute. The historical pre-release meaning is unknown; specifically, `0x0C` is **not** renamed corpse/loot state merely from the text.

This also explains why ordinary death does not prove `0x0C`: normal death finalization reaches state `0x0A`, while lethal player contact uses `0x0B`.

## State producer/reachability closure — 2026-09-29

The Win16 1.10 numeric state space is now closed at the producer level. All 22 values `0x00..0x15` are classified: 20 have a recovered retail producer, `0x0A/0x0B` are deliberate terminal states with no local dispatcher body, and only `0x0C/0x0D` are retained dormant handlers without a normal producer.

Important newly promoted semantics:

- `0x09` = death/special finalization entry;
- `0x0A` = ordinary finalized-death terminal state;
- `0x11` = strategy-1 dynamic-door maneuver;
- `0x12` = conditional lethal wait/animation before next state `0x09`;
- `0x14` = E1M9 Radio/Dancers scripted state;
- `0x15` = ordinary pain/reaction state.

The lethal state-setter packing is now decoded: `0x00090000` supplies `state=0,next=9`, while `0x00090012` supplies `state=0x12,next=9` when OBJECT `+0x1A > 0`. This is why state `0x12` eventually restores state `0x09` rather than representing an independent AI strategy.

Detailed evidence and the complete 22-row producer table are in `GUARD_STATE_REACHABILITY_CLOSURE_2026-09-29.md`.

**Coverage:** GUARD state-ID / producer reachability is **100% for Win16 1.10**. This does not promote the entire GUARD AI subsystem to 100%; exact state names for the remaining active AI states, attack scheduling, resource bindings and full DOS parity remain separate targets.

## Pain transition

The normal non-lethal hit path:

- subtracts positive damage from strength;
- writes `resoct = 8`;
- preserves the prior state into `nextstate`;
- sets current state to `0x15`;
- state `0x15` restores `state=nextstate` after its timing/animation work.

Strategies 3 and 5 have distinct hit behavior and remain separate targets.

## Difficulty affects GUARD timing

Global `0x4C14` participates in GUARD timing and both damage directions:

| difficulty value | player -> guard | guard/object -> player | GUARD timing |
|---:|---:|---:|---:|
| 0 | x2 | /2 | slower / timer doubled |
| 1 | x1 | x1 | baseline |
| 2 | /2 | x2 | faster / timer halved |

This establishes numeric ordering easier / baseline / harder even if final menu text binding remains separate.

## Per-GUARD score switch

The score function around `3:9F10` dispatches on `OBJECT+06` classes `0x08..0x20`, corresponding to GUARD1..25.

| OBJECT class | Guard | Name / recovered role | Score |
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
| `0x11` | 10 | Dracula phase 1 | 0 |
| `0x12` | 11 | Cemetery Gargoyle | 150 |
| `0x13` | 12 | Garden Gargoyle | 150 |
| `0x14` | 13 | **Dracula-Bat internal second form** | 200 |
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
| `0x20` | 25 | unresolved/cut or fallback class | 50 |

GUARD26/Dancers is outside the switch and follows the default zero-score path.

## GUARD13 / class 0x14 is Dracula-Bat

This is no longer an unresolved standalone identity.

The lethal Dracula class `0x11` path performs an in-place class transformation instead of ending the actor immediately:

```text
OBJECT+06: 0x11 -> 0x14
GUARD+10:  0xFF        // HP restored to 255
GUARD+0B:  0x08        // state
GUARD+0C:  0x02        // next_state
GUARD+06:  1           // timer
sequence/frame-related value: 0x23
transformation event/sound request: 0x22
```

The transformed `0x14` class then uses the score-switch value **200** when finally killed. Dracula phase 1 itself awards **0**. Normal Bat class `0x08` is a separate class and scores 25.

Current interpretation: Dracula has two 255-strength phases, with the second phase represented internally by GUARD13/class `0x14`. This is supported by the direct class writer plus HP/state reset and shared Bat-related resource/sound behavior.

## GUARD25 / class 0x20 shipped-reachability closure

Class `0x20` is now classified as an **executable-only fallback/cut slot**, not merely an unidentified retail enemy.

The complete supplied MAP/object-class inventory contains no object-class-table assignment for `0x20`, while every normal retail guard class around it is represented and class `0x21` is explicitly GUARD26/Dancers. A targeted Win16 writer audit also finds no gameplay writer `OBJECT+06 = 0x20`. The superficially similar `GUARD+06 = 0x20` write belongs to the door-maneuver timer and is unrelated to object class.

If injected, `0x20` still receives the generic guard profile: strength 255, initial state/next state 7/2, strategy 0, generic damage handling, score 50, and no dedicated recovered GUARD sound-selector branch.

This is sufficient to close **shipped reachability**: GUARD25 is not spawned or transformed into by the supplied retail game data/code graph. A hypothetical orphan/pre-release sprite identity remains historical archaeology only.

## GUARD26 / class 0x21 Dancers

GUARD26 is real shipped data rather than a fallback slot. Episode-1 object ID `0x8C` maps to class `0x21` and editor name **Dancers**, with one supplied E1 placement. It uses the special initialization profile and the E1M9 Radio/ACTIONSPOT scripted path. GUARD26 lies outside the GUARD1..25 score switch and therefore scores zero by the default path.

Detailed data evidence is in `GUARD_CLASS_INVENTORY_CLOSURE_2026-09-29.md`.

**Coverage:** shipped GUARD class/object reachability inventory is now **100%**. This does not invent a pre-release name for the unused `0x20` slot.

## Weapon/class special cases relevant to AI

Recovered combat behavior includes:

- Penelope class `0x15`: zero normal weapon damage in the audited producer and a separate helper side path;
- Dr. Hamerstein class `0x16`: damage becomes literal 3 only when global `0x7E52 == 3`, otherwise zero, before final difficulty transform;
- Cannon class `0x19`: zero damage in this producer;
- Ghost class `0x1A`: Magic Wand damages it (`/2`), other weapons return zero;
- Alien #1 `0x1E` and Alien #2 `0x1F`: Magic Wand returns zero while other weapons are reduced;
- Baddie #1/#2 classes `0x0F/0x10` use literal `/256` for non-wand weapons, usually collapsing small positive values to zero.

See `COMBAT_DAMAGE_RE.md` for the complete matrix and signed arithmetic details.

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
| `+14/+16` | 4 | render/spatial ordering fields | PARTIAL/strong |
| `+18` | 2 | projected/view-space vertical baseline used by damage producer | VERIFIED read, semantic PARTIAL |
| `+1A` | 1 | runtime byte initialized zero | TODO semantic |
| `+1B` | 1 | unresolved | TODO |

A mover resolves OBJECTs by `index*0x1C`, modifies world X/Y and updates map-cell state. Exact per-class movement speeds remain tied to state/movement dispatch.

## Dancers / special scripted GUARD behavior

GUARD26/Dancers is not another class in the GUARD1..25 switch. E1M9 data/gameplay evidence points to an ACTIONSPOT/dancing sequence with scripted behavior and class replacement. Treat it as a separate reconstruction target.

## Remaining GUARD/AI targets

1. Give exact semantic names to the remaining *reachable* partially named states (especially 02..09 and 0E..14) using original animation/movement/sound XREFs; 0C/0D are now classified as dormant.
2. Recover every `strategy` value and full transition matrix.
3. Trace movement-state writes to OBJECT X/Y and derive exact speeds/cadence.
4. Recover sight/FOV/LOS/hearing and the Omnificent hostility gate.
5. Recover exact attack intervals and projectile/melee production.
6. Bind all alert/attack/pain/death SND.DAT IDs directly from original call sites.
7. Finish GUARD25 class `0x20`: writer XREFs, SEQDEF/IMG/SND identity and reachability.
8. Reconstruct GUARD26/Dancers ACTIONSPOT script completely.
9. Finish `GUARD+00..01`, `+0E/+0F`, `+13..19` semantics.
10. Cross-bind enemy-to-player damage classes to visible GUARD names.
11. Trace the complete Dracula `0x11 -> 0x14` resource/sequence/sound chain and final corpse/removal path.
