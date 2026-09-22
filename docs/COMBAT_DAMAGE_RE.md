# Combat damage reverse engineering

Updated: 2026-09-22
Evidence: direct 16-bit disassembly of original NITE3W.EXE V1.10 (SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`) plus cross-binding to the recovered GUARD score/death paths.

## Damage producer located

The helper called by the GUARD hit receiver is at `seg3:9FA2`. The receiver at `seg3:80F7/811C..81EF` consumes its AX return value and applies it to `GUARD+10 strength`.

The producer first computes a signed base value:

```text
base = ((OBJECT+18) - global_53EE) * 8
base += random() % 25
```

`global_53EE` is derived by the viewport setup routine at `seg3:5207..5250` and is a vertical screen/view reference. `OBJECT+18` therefore participates in projected/view-space vertical aim geometry in this damage path; it is **not** world Y (`OBJECT+12`).

Status: **VERIFIED_EXE** for arithmetic/read site and random range; exact writer-level semantic name of `OBJECT+18` remains PARTIAL.

### Consequence for “shots to kill” tables

A single fixed ammunition count is not universally valid for a class because raw damage depends on projected geometry plus `random()%25`, then class/weapon resistance and difficulty. Exact shot counts require a fixed test geometry/distance, difficulty, weapon and RNG assumption.

## Current weapon selector identified

Global byte `0x4C23` is initialized to `0xFF` and used as the active weapon selector.

- 0: Single Shot Laser
- 1: Magic Wand
- 2: Silver Pistol
- 3: Continuous fire laser
- `0xFF`: none/unset

The damage producer branches specially on weapon 1 and weapon 2; values 0 and 3 generally share the default branch in this transform.

## Enemy-class scaling matrix

The producer dispatches on `OBJECT+06 class` for classes `0x0C..0x1F`. The jump table at `seg3:9FE8` contains 20 targets. Operations below apply to the signed base **before final difficulty scaling**.

| OBJECT class | Recovered identity | Laser 0 | Wand 1 | Silver 2 | Laser 3 | Status |
|---:|---|---:|---:|---:|---:|---|
| `0x0C` | Mrs H. | /8 | /8 | /8 | /8 | VERIFIED_EXE + score binding |
| `0x0D` | Zelda | /8 | /2 | /8 | /8 | VERIFIED_EXE + score binding |
| `0x0E` | Vampira | /8 | /2 | /2 | /8 | VERIFIED_EXE + score binding |
| `0x0F` | Baddie #1 | /256 | /2 | /256 | /256 | VERIFIED_EXE + score binding |
| `0x10` | Baddie #2 | /256 | /2 | /256 | /256 | VERIFIED_EXE + score binding |
| `0x11` | Dracula phase 1 | /8 | /2 | /2 | /8 | VERIFIED_EXE + transformation binding |
| `0x12` | Cemetery Gargoyle | /4 | /4 | /4 | /4 | VERIFIED_EXE + score binding |
| `0x13` | Garden Gargoyle | /4 | /4 | /4 | /4 | VERIFIED_EXE + score binding |
| `0x14` | **Dracula-Bat phase 2 / GUARD13** | /8 | /2 | /2 | /8 | VERIFIED_EXE + direct class transform |
| `0x15` | Penelope | 0 | 0 | 0 | 0 | VERIFIED_EXE; separate helper side path |
| `0x16` | Dr. Hamerstein | special | special | special | special | VERIFIED_EXE |
| `0x17` | Tall slim robot | /4 | /256 | /4 | /4 | VERIFIED_EXE + score binding |
| `0x18` | Trashcan robot | /8 | /256 | /16 | /8 | VERIFIED_EXE + score binding |
| `0x19` | Cannon | 0 | 0 | 0 | 0 | VERIFIED_EXE + score binding |
| `0x1A` | Ghost | 0 | /2 | 0 | 0 | VERIFIED_EXE + score binding |
| `0x1B` | Goldie | /2 | /2 | /2 | /2 | VERIFIED_EXE + score binding |
| `0x1C` | Greenie | /2 | /2 | /2 | /2 | VERIFIED_EXE + score binding |
| `0x1D` | Demon | /8 | /8 | /8 | /8 | VERIFIED_EXE + score binding |
| `0x1E` | Alien #1 | /8 | 0 | /8 | /8 | VERIFIED_EXE + score binding |
| `0x1F` | Alien #2 | /4 | 0 | /4 | /4 | VERIFIED_EXE + score binding |

Important points:

- class `0x1A` is Ghost: only Magic Wand reaches `/2`; all other weapons return zero in this producer;
- Alien #1/#2 reject Magic Wand here;
- Penelope and Cannon take zero normal weapon damage in this producer;
- `/256` entries are literal arithmetic right shifts by 8, not a symbolic immunity constant; small positive values normally collapse to zero;
- class `0x20` / GUARD25 is **outside** this explicit `0x0C..0x1F` table, so no dedicated resistance branch is proven for it in this routine.

## Dracula two-phase combat path

GUARD13/class `0x14` is no longer an unknown standalone enemy. On a lethal hit to Dracula class `0x11`, the special death path transforms the same actor to class `0x14`, restores strength to `0xFF`, and resets state/timer/sequence fields for the second phase.

Recovered transition anchors:

```text
OBJECT+06: 0x11 -> 0x14
GUARD+10:  0xFF
GUARD+0B:  0x08
GUARD+0C:  0x02
GUARD+06:  1
sequence/frame-related value: 0x23
transformation event/sound request: 0x22
```

Score behavior is correspondingly two-stage:

- Dracula phase 1 (`0x11`) score: 0;
- transformed Dracula-Bat (`0x14`) final score: 200;
- normal Bat (`0x08`) remains a different class and scores 25.

This establishes two 255-strength phases rather than a separate high HP constant for Dracula.

## Hamerstein special gate

Class `0x16` does not use the projected base directly. The producer returns literal damage **3** only when global `0x7E52 == 3`; otherwise damage is zero. Final difficulty scaling still applies afterward.

The current cross-thread interpretation is that `0x7E52` participates in episode/state gating and the boss is only vulnerable under the Episode-3/special state condition represented by value 3. The numeric branch is VERIFIED_EXE; the complete narrative/script meaning of `0x7E52` remains PARTIAL.

## Difficulty scaling recovered

After class/weapon scaling, global word `0x4C14` applies:

```text
0: damage *= 2
1: unchanged
2: damage /= 2
```

The same global is used inversely in GUARD timing, and the enemy->player receiver uses the opposite damage trend. Numeric ordering is therefore easier / baseline / harder.

| difficulty | player -> enemy | enemy -> player | guard timing |
|---:|---:|---:|---:|
| 0 | x2 | /2 | slower |
| 1 | x1 | x1 | baseline |
| 2 | /2 | x2 | faster |

## Output clamp and GUARD receiver

The producer caps only the high end:

```text
if (damage > 255)
    damage = 255
```

The receiver ignores non-positive damage. For positive damage:

```text
if damage >= guard.strength:
    guard.strength = 0
    death_or_special_path()
else:
    guard.strength -= damage
    guard.resoct = 8
    pain/state_15_path()
```

Normal GUARD creation initializes strength to 255; no class-specific post-spawn HP table has been found.

## Weapon ammo pools and consumption

The fire/ammo helper at `seg3:A97C` maps selector to ammo bytes. Omnipotent (`0x4BE5 != 0`) bypasses normal consumption.

| Weapon | Selector | Ammo byte | Consumption |
|---|---:|---:|---|
| Single Shot Laser | 0 | `0x4C20` | -1 when non-zero |
| Magic Wand | 1 | `0x4C44` | -1 when non-zero |
| Silver Pistol | 2 | `0x4C1F` | -1 when non-zero |
| Continuous Laser | 3 | `0x4C20` | -1 when non-zero; shared laser pool |

Refill/pickup helper at `seg3:A9E0`:

- forced/set path: 50 (`0x32`);
- ordinary pickup: +20 (`0x14`);
- normal threshold/display cap: 100 (`0x64`).

Pickup type order differs from weapon-selector order: pickup 0 -> silver, 1 -> laser, 2 -> wand.

## Signed-byte quirk: 127 for silver/laser logic

Silver (`0x4C1F`) and Laser (`0x4C20`) use signed comparisons in audited pickup/HUD paths; Wand (`0x4C44`) uses unsigned logic there.

Consequences:

- 100 is the intended normal gameplay pickup/display cap;
- 127 (`0x7F`) is the highest positive signed-byte value for silver/laser when manually editing memory;
- 128..255 exist physically but appear negative in those signed compare/display paths;
- Wand does not share the same signed-127 semantic boundary in those routines;
- firing itself checks non-zero and decrements, so corrupted high-bit byte values can still be consumed.

Status: **VERIFIED_EXE**.

## Weapon jam is scripted, not random

The firing routine at `seg3:8B06` checks `0x4C2E`. When set it displays:

```text
Your weapon appears to be jammed!
```

Episode-1 level-9 script handling uses:

```text
event 0x47 -> set 0x4C2E = 1
event 0x48 -> clear 0x4C2E = 0
```

Both transitions invoke SFX ID `0x44` (68). No random jam probability is supported by current evidence.

## Reconstructed formula

For normal explicit class-table entries:

```text
raw = 8 * (objectProjectedBaseline - viewReferenceY) + (random() % 25)
scaled = class_weapon_transform(raw, objectClass, activeWeapon)
scaled = difficulty_transform(scaled)
damage = min(scaled, 255)

if damage <= 0:
    no strength subtraction
elif damage >= guard.strength:
    guard.strength = 0
    death/special path
else:
    guard.strength -= damage
    guard.resultOctant = 8
    pain/state path
```

The original uses signed 16-bit shifts/division behavior; this pseudocode is descriptive.

## Remaining combat targets

1. Trace the writer of `OBJECT+18` and give it a final renderer semantic name.
2. Resolve Penelope class `0x15` helper side effects completely.
3. Resolve full meaning/writers of `0x7E52` and Hamerstein vulnerability state.
4. Bind `0x4C14` numeric values to exact displayed difficulty labels.
5. Recover exact weapon cadence / continuous-fire scheduling.
6. Bind E1M9 jam events `0x47/0x48` to exact map objects/triggers.
7. Bind lethal/non-lethal paths to exact pain/death SND.DAT calls.
8. Finish GUARD25/class `0x20` reachability and determine whether it uses only fallback damage behavior or another producer path.
9. Produce empirical shots-to-kill tables only with fixed geometry/difficulty/RNG assumptions and label them as tests, not class constants.
