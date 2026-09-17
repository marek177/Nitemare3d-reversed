# Player health / enemy-to-player damage reverse-engineering report

Date: 2026-09-17
Evidence: original NITE3W.EXE V1.10, direct 16-bit segment-3 disassembly plus gameplay observations.

## Player health field recovered

Runtime byte **`0x4C1D` is player health**.

Independent executable paths converge on the same address:

- new-game/reset path `seg3:BA30` writes `0x64` (100);
- HUD path `seg3:A4CE..A502` clamps it to 100 and formats/displays it;
- health pickups test/add to it;
- enemy/projectile damage receivers subtract from it;
- death paths set it to zero;
- cheat maintenance code refills it to 100;
- debug key code can increment/decrement it directly.

Status: **VERIFIED_EXE**.

## Normal health range and 100% ceiling

The normal initialized value is exactly `0x64 = 100`.

The HUD/update path at `seg3:A4CE` performs an unsigned min-with-100 transform and writes the result back to the runtime health byte before display. In equivalent form:

```text
health = min_unsigned(health, 100)
```

Pickup handlers first test `health < 100` before adding health. Some pickup paths add a chunk first and rely on the subsequent HUD/update clamp rather than saturating the addition instruction itself. Thus a transient byte value above 100 can exist between instructions, but normal observable gameplay is forced back to 100.

This matches direct testing: there is no normal Doom-style 200% overheal.

Status: **VERIFIED_EXE** for initialization, pickup threshold and HUD/write-back clamp; **BEHAVIORAL + VERIFIED_EXE** for normal observable 0..100 gameplay.

## Health pickup amounts

At least two direct pickup/script paths are now visible:

- generic pickup branch at `seg3:1CD2..1CE3`: if health is below 100, add **20** (`0x14`);
- object/script pickup branch around `seg3:D018..D043`: if health is below 100, add `20 >> subtype/shift`;
- another branch around `seg3:D048..D064`: if health is below 100, add **30** (`0x1E`) and also awards score/time-related value `0xFA` in the adjacent logic;
- a separate dispatch case at `seg3:AC2C` directly restores health to **100** and adds `0x96` to a score/time counter.

Exact visible pickup names/items remain to be bound to these branches.

## Enemy/projectile -> player damage receiver

A direct receiver at `seg3:8C09..8C98` obtains an 8-bit damage amount from helper `seg3:A1EA` and applies it to `0x4C1D`.

Before damage is applied it checks:

- `Omnipotent` global `0x4BE5`; if enabled, damage is skipped;
- player/game state `0x46B4 == 2`; if already in that terminal/death state, damage is skipped.

The receiver uses an **unsigned lethal comparison**:

```text
if damage >= health:
    health = 0
    game/player state 0x46B4 = 2
    death transition
else:
    health -= damage
```

This is why ordinary enemy damage never underflows player health into a negative/large wrapped value. Lethal damage explicitly writes zero instead of subtracting through zero.

Status: **VERIFIED_EXE**.

A second damage path around `seg3:BEBC..BEEB` has the same saturating-to-zero structure and sets `0x46B4 = 3`, indicating a distinct death/hazard mode. Its damage byte is table-derived. Exact high-level hazard identity is still PARTIAL.

## Enemy damage producer and difficulty scaling

The helper at **`seg3:A1EA`** is an enemy/object-to-player damage producer. It:

1. derives tile-relative X/Y distance from the attacking OBJECT's `+10/+12` world coordinates and player/reference tile globals `0x4BF2/0x4BF4`;
2. calls a distance-like helper;
3. derives a base magnitude approximately as `100 / distance` (or 100 when the distance result is non-positive);
4. dispatches on attacker `OBJECT+06 class` starting at class 8;
5. applies class-specific shifts/random masks/special cases;
6. finally applies gameplay difficulty `0x4C14`.

The final difficulty transform is directly visible at `seg3:A2AF..A2C7`:

```text
0x4C14 == 0: enemy damage /= 2
0x4C14 == 1: enemy damage unchanged
0x4C14 == 2: enemy damage *= 2
```

This is the exact inverse of the already recovered player-to-GUARD damage transform:

| Difficulty value | Player -> enemy | Enemy -> player | GUARD timing |
|---:|---:|---:|---:|
| 0 | x2 | /2 | slower (timer doubled) |
| 1 | x1 | x1 | baseline |
| 2 | /2 | x2 | faster (timer halved) |

Therefore the semantic ordering **0 = easier, 1 = baseline/normal, 2 = harder** is now supported by three independent gameplay effects. Exact menu text labels remain to be tied to the setter, but the numeric behavior is **VERIFIED_EXE**.

This directly confirms the gameplay observation that enemies cause more damage on higher difficulty.

## Enemy class transforms in the player-damage producer

The `A1EA` class dispatch contains multiple distinct transforms. Confirmed branch operations include:

- arithmetic `/2` and `/4` reductions of the distance-derived base;
- random damage branches using RNG masks `& 7`, `& 15`, and `& 31`;
- a special class branch around `A298` which yields either **33 (`0x21`)** or **100 (`0x64`)** depending on episode/global state (`0x7E52` and `0x51A6`);
- classes outside the dispatch range fall through to the shared final difficulty transform.

The complete class-number -> visible enemy-name table is still pending, so these values are not yet assigned speculative monster names.

Status: **VERIFIED_EXE** for arithmetic; enemy-name binding TODO.

## Why 0% behaves unusually

The main damage receiver explains a large part of the observation:

- lethal damage writes health to **exactly zero** and switches `0x46B4` to state 2;
- once `0x46B4 == 2`, the same receiver skips subsequent damage entirely;
- another main-loop path at `seg3:DC44` explicitly tests `health == 0` while processing game-state transitions.

Therefore `0%` is not treated as ordinary live health that continues decreasing. It is a sentinel/terminal health value coupled to a death/game-state transition. This accounts for the apparent "no more HP subtraction at 0" behavior.

There may still be cheat/debug edge cases capable of producing a visually odd zero-health state without the normal transition, so those paths remain under audit.

Status: **VERIFIED_EXE** for normal lethal receiver behavior; cheat-created zero-health edge case PARTIAL.

## Cheat/debug interactions

`Omnipotent` is runtime byte `0x4BE5`. The player damage receiver checks it directly and skips damage while it is active.

A periodic cheat-maintenance routine around `seg3:B137` writes **100** to:

- silver ammo `0x4C1F`;
- laser ammo `0x4C20`;
- player health `0x4C1D`;
- wand ammo `0x4C44`;

when Omnipotent is enabled. The stronger adjacent cheat path around `B169..B18D` also sets health/ammo and other inventory globals.

Separately, debug/input code around `seg3:988C..98AB` directly increments or decrements `0x4C1D` when modifier bit `0x40` in `0x3756` is held. The exact physical key-name binding for those two branches is still being tied to the keyboard table, so this report does not yet claim which branch is Shift+`+` versus Shift+`-` solely from the raw branch location.

Status: **VERIFIED_EXE** for health writes and modifier requirement; exact key label binding PARTIAL.

## Save-game target

Now that `0x4C1D` is verified as player health, the USER.SAV writer/loader can be traced specifically for this byte. The physical save slot already contains a 94-byte compact gameplay/global block at offset `0x2035`; exact saved offset of health remains the next save-semantic target.

## Remaining health/combat work

1. Decode the full `A1EA` attacker-class jump table and map classes to visible enemies.
2. Identify the second `0x46B4 = 3` damage/death path (hazard/projectile/environment semantics).
3. Bind debug increment/decrement branches to exact keyboard combinations and reproduce the Shift+`+` edge behavior.
4. Locate `0x4C1D` in the USER.SAV 94-byte gameplay block and verify load/save restoration.
5. Trace death transition calls and associated SFX/animation/message behavior.
6. Continue into weapon cadence, GUARD pain/death SFX and full GUARD state machine.
