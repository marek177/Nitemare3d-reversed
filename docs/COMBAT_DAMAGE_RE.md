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

The producer dispatches on `OBJECT+06 class` for classes `0x0C..0x1F`. The table below gives the operation applied to the signed base damage **before final difficulty scaling**.

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
| `0x1A` | /2 | 0 | /2 | /2 | VERIFIED_EXE |
| `0x1B` | /2 | /2 | /2 | /2 | VERIFIED_EXE |
| `0x1C` | /2 | /2 | /2 | /2 | VERIFIED_EXE |
| `0x1D` | /8 | /8 | /8 | /8 | VERIFIED_EXE |
| `0x1E` | /8 | 0 | /8 | /8 | VERIFIED_EXE |
| `0x1F` | /4 | 0 | /4 | /4 | VERIFIED_EXE |

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
5. Trace weapon fire cadence/ammo consumption and the `Your weapon appears to be jammed!` branch.
6. Follow lethal/non-lethal handlers into exact pain/death SND.DAT calls.

Renderer work remains deferred until the combat/runtime pass is complete.
