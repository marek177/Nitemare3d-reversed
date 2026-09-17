# Combat damage reverse engineering

Date: 2026-09-17
Evidence: direct 16-bit disassembly of original NITE3W.EXE V1.10 (SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`).

## Damage producer located

The helper called by the GUARD hit receiver is at `seg3:9FA2`. The receiver at `seg3:80F7/811C..81EF` consumes its AX return value and applies it to `GUARD+10 strength`.

The producer first computes a signed base value:

```text
base = ((OBJECT+18) - global_53EE) * 8
base += random() % 25
```

`global_53EE` is derived by the viewport setup routine at `seg3:5207..5250` and is a vertical screen/view reference. Therefore `OBJECT+18` participates in projected-screen/aim geometry in this damage path; it must not be mislabeled as world Y (world Y is OBJECT+12).

Status: **VERIFIED_EXE** for the arithmetic and random range; exact high-level name of OBJECT+18 remains PARTIAL pending the projection writer trace.

## Current weapon selector identified

Global byte `0x4C23` is initialized to `0xFF` and weapon/UI code treats it as the active weapon selector. The executable's own command strings list four weapon choices in order:

- 0: Single Shot Laser
- 1: Magic Wand
- 2: Pistol firing silver bullets
- 3: Continuous fire laser

The damage producer branches on `0x4C23 == 1` and `== 2`; values 0 and 3 generally share the default branch for this particular damage-scaling routine.

Status: **VERIFIED_EXE** for selector behavior and weapon ordering from embedded executable strings.

## Enemy-class scaling matrix

The producer dispatches on `OBJECT+06 class` for classes `0x0C..0x1F`. The jump table at `seg3:9FE8` contains 20 targets, one for each class. The table below gives the operation applied to the signed base damage **before final difficulty scaling**.

| OBJECT class | Single Shot Laser (0) | Magic Wand (1) | Silver Pistol (2) | Continuous Laser (3) | Status |
|---:|---:|---:|---:|---:|---|
| `0x0C` | /8 | /8 | /8 | /8 | VERIFIED_EXE |
| `0x0D` | /8 | /2 | /8 | /8 | VERIFIED_EXE |
| `0x0E` | /8 | /2 | /2 | /8 | VERIFIED_EXE |
| `0x0F` | /256 | /2 | /256 | /256 | VERIFIED_EXE |
| `0x10` | /256 | /2 | /256 | /256 | VERIFIED_EXE |
| `0x11` | /8 | /2 | /2 | /8 | VERIFIED_EXE |
| `0x12` | /4 | /4 | /4 | /4 | VERIFIED_EXE |
| `0x13` | /4 | /4 | /4 | /4 | VERIFIED_EXE |
| `0x14` | /8 | /2 | /2 | /8 | VERIFIED_EXE |
| `0x15` | 0 | 0 | 0 | 0 | VERIFIED_EXE; branch also calls a separate helper |
| `0x16` | special | special | special | special | VERIFIED_EXE: damage becomes 3 only when global `0x7E52 == 3`, otherwise 0 |
| `0x17` | /4 | /256 | /4 | /4 | VERIFIED_EXE |
| `0x18` | /8 | /256 | /16 | /8 | VERIFIED_EXE |
| `0x19` | 0 | 0 | 0 | 0 | VERIFIED_EXE |
| `0x1A` | 0 | /2 | 0 | 0 | VERIFIED_EXE |
| `0x1B` | /2 | /2 | /2 | /2 | VERIFIED_EXE |
| `0x1C` | /2 | /2 | /2 | /2 | VERIFIED_EXE |
| `0x1D` | /8 | /8 | /8 | /8 | VERIFIED_EXE |
| `0x1E` | /8 | 0 | /8 | /8 | VERIFIED_EXE |
| `0x1F` | /4 | 0 | /4 | /4 | VERIFIED_EXE |

Important correction: class `0x1A` reaches `seg3:A080`, which returns zero for every weapon except weapon 1 (Magic Wand), where it performs `/2`. Earlier notes had the polarity reversed.

The `/256` entries are literal arithmetic right shifts by 8, not shorthand for immunity. For small positive base values they normally collapse to zero, but the exact signed arithmetic is retained here.

This matrix explains why all normally spawned GUARD records can start with `strength=255` yet different enemy classes have radically different practical toughness against different weapons.

## Difficulty scaling recovered

After class/weapon scaling, global word `0x4C14` applies a final multiplier:

```text
0x4C14 == 0: damage *= 2
0x4C14 == 1: damage unchanged
0x4C14 == 2: damage /= 2
```

The same global is used inversely in GUARD timing code (`seg3:78B5..78D4`): value 2 halves a guard timer while value 0 doubles it. This cross-reference strongly identifies the values as the three gameplay difficulty levels, with 0 easier, 1 normal/default, 2 harder.

Status: **VERIFIED_EXE** for the numeric scaling; difficulty labels are **strongly supported / PARTIAL** until the menu setter is tied to displayed difficulty names.

## Output clamp

The producer caps only the high end:

```text
if (damage > 255)
    damage = 255
```

The hit receiver separately ignores non-positive damage (`damage <= 0`) on the non-lethal path. Thus the effective damage accepted by the GUARD receiver is 1..255.

## Weapon ammo pools and consumption

The fire/ammo helper at `seg3:A97C` provides a direct mapping from weapon selector to ammo byte. Omnipotent (`0x4BE5 != 0`) bypasses normal consumption and reports success.

| Weapon selector | Weapon | Ammo byte | Consumption |
|---:|---|---:|---|
| 0 | Single Shot Laser | `0x4C20` | decrement by 1 when non-zero |
| 1 | Magic Wand | `0x4C44` | decrement by 1 when non-zero |
| 2 | Silver Pistol | `0x4C1F` | decrement by 1 when non-zero |
| 3 | Continuous fire laser | `0x4C20` | decrement by 1 when non-zero; shares laser pool with weapon 0 |

Status: **VERIFIED_EXE**.

The related refill/pickup helper at `seg3:A9E0` shows two useful operations:

- forced/set path sets the selected ammo pool to `0x32` = **50**;
- ordinary ammo pickups add `0x14` = **20** while checking a `0x64` = **100** threshold before the add.

The ordinary pickup type order is not the same as weapon-selector order: pickup type 0 adds to `0x4C1F` (silver), type 1 to `0x4C20` (laser), and type 2 to `0x4C44` (wand). Exact item names/graphics remain to be bound to those pickup type IDs.

## Weapon jam is a scripted level flag, not random weapon failure

The firing routine at `seg3:8B06` checks byte `0x4C2E` before performing the shot. If it is non-zero it calls the tiny message routine at `seg4:2508`, which displays the embedded string at segment-10 offset `0x1E94`:

```text
Your weapon appears to be jammed!
```

and returns without executing the normal firing path.

A direct-write audit of `0x4C2E` finds the important setter/clearer in the level-script dispatcher at `seg3:C01E..C051`. In the Episode-1 branch (`0x7E52 == 1`), when `level + 1 == 9`:

```text
script/event code 0x47 -> if not jammed: 0x4C2E = 1
script/event code 0x48 -> if jammed:     0x4C2E = 0
```

Both transitions invoke SFX ID `0x44` (decimal **68**) through the sound helper.

Therefore the jam is **not supported as a random gun-jam probability**. It is a scripted gameplay condition that blocks the common fire routine until a corresponding script event clears it. The current evidence ties the set/clear mechanism specifically to Episode 1, level 9 (1-based level number), subject to final map-event binding.

Status: **VERIFIED_EXE** for flag check, setter, clearer, event codes and SFX ID; map-object identity that emits event `0x47/0x48` is still PARTIAL.

## Reconstructed formula

For normal class-table entries:

```text
raw = 8 * (projectedY - viewReferenceY) + (random() % 25)
scaled = class_weapon_transform(raw, objectClass, activeWeapon)
scaled = difficulty_transform(scaled)
damage = min(scaled, 255)

if damage <= 0:
    no strength subtraction
elif damage >= guard.strength:
    guard.strength = 0
    death path
else:
    guard.strength -= damage
    guard.resultOctant = 8
    pain/state path
```

The arithmetic uses signed 16-bit shifts/division behavior. This pseudocode is descriptive and intentionally does not replace those signed semantics with floating-point division.

## What remains unknown

1. Map OBJECT classes `0x0C..0x1F` to the visible enemy names/sprites for all episodes.
2. Trace the writer of `OBJECT+18` to give the projected coordinate an exact semantic name.
3. Resolve the special class `0x15` helper and the meaning of global `0x7E52` used by class `0x16`.
4. Tie `0x4C14` values to the exact difficulty labels displayed by the game UI.
5. Trace exact weapon cadence / continuous-fire scheduling and bind ammo HUD/display behavior.
6. Bind the Episode-1 level-9 jam event codes `0x47/0x48` to the exact map objects/triggers.
7. Follow lethal/non-lethal handlers into exact pain/death SND.DAT calls.

Renderer work remains deferred until the combat/runtime pass is complete.
