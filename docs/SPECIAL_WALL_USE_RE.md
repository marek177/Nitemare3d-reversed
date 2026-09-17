# Special-wall USE families — additional NITE3W.EXE decoding

Date: 2026-09-17

This supplements `docs/USE_INTERACTION_RE.md` with deeper decoding of the `seg3:277A` special-wall dispatcher, its NE cross-segment targets, and the initialized menu records in segment 7.

## NE relocation correction

The far-call target offset alone is not sufficient to identify the target segment in a Win16 NE image. Segment-3 relocation chains prove:

| dispatcher target | offset | target segment |
|---|---:|---:|
| `C126` | `C126` | 3 |
| `20CE` | `20CE` | 4 |
| `1F6A` | `1F6A` | 4 |
| `2076` | `2076` | 4 |
| `1EE0` | `1EE0` | 4 |

Status: **VERIFIED_EXE**.

## Segment-7 menu records settle three wall families

The initialized data in segment 7 contains fixed 18-byte menu records used directly by the special-wall handlers.

### Menu at segment7:`1496`

```text
Floor 1
Floor 2
Floor 3
Floor 4
Floor 5
Floor 6
Floor 7
Floor 8
Floor 9
Floor 10
```

`seg4:1F6A` walks these records with stride `0x12` and dynamically enables/disables entries. Therefore mapped wall types **`0x1D..0x24` are the floor/elevator-selection family**. **VERIFIED_EXE**.

### Menu at segment7:`155C`

```text
Climb up
Climb down
Cancel
```

`seg4:1EE0` passes this menu and uses `seg3:2334` / `seg3:2426` to decide which direction/state is currently available. Therefore mapped wall types **`0x0D..0x14` are the climb up/down family**. **VERIFIED_EXE**.

### Menu at segment7:`15A4`

```text
Go down
Cancel
```

`seg4:2076` passes this menu. Therefore mapped wall types **`0x25..0x2C` are the go-down confirmation family**. **VERIFIED_EXE**.

This is an important correction: an earlier provisional analysis associated `0x25..0x2C` with the combination prompt. The direct segment-7 menu evidence disproves that classification.

## Combination prompt actually belongs to object type `0x26`

`seg3:1A22` sends mapped object types `0x26` and `0x27` to `seg3:AD9E`.

For mapped object type **`0x26`**, the state-zero path opens the exact prompt:

```text
What's the combination?  0000000
```

The same data region contains code strings including:

```text
01532
080993
372535
```

and the failure message:

```text
I'm sorry, that is not
the correct combination.
```

Thus the **combination-input interaction is object type `0x26`**, not wall types `0x25..0x2C`. Exact visual/object identity is still **PARTIAL** until the OBJECT-definition/state audit is complete.

## Four-pentagram mask — global `0x4C45`

The object-touch dispatcher `seg3:CF60` maps OBJECT class **`0x3C`** to `seg3:D158`, which performs:

```text
0x4C45 |= 1 << OBJECT[+01]
```

The Omnifarious path sets `0x4C45 = 0x0F`. `seg3:C126` tests the same four bits and its static strings identify their order:

| bit | pentagram |
|---:|---|
| `0x01` | Red Pentagram |
| `0x02` | Green Pentagram |
| `0x04` | Blue Pentagram |
| `0x08` | Yellow Pentagram |

Therefore OBJECT class `0x3C` is the pentagram collectible class and OBJECT `+01` is its color/subtype index. **VERIFIED_EXE**.

## `0x15..0x18` — Other Side portal / mirror / four-pentagram gate

`seg3:277A` routes mapped wall types `0x15..0x18` to `seg3:C126`.

The handler builds the exact message requiring all four pentagrams before passage to the `"Other Side"`, appends the names of missing pentagrams, and has a mapped-type-`0x16` branch using:

```text
The mirror crack'd
from side to side!
```

For mapped type `0x15`, `0x4C45 == 0x0F` enters a distinct success/transition path. **VERIFIED_EXE** for the family and control flow; exact visual names of all four mapped types remain **PARTIAL**.

## `0x19..0x1C` — exact reusable colored-key gates

`seg4:20CE` calculates `index = mappedWallType - 0x19`, tests `1 << index` in colored-key mask `0x4C28`, and resolves the key name through `seg3:BCB6`:

| wall type | required key |
|---:|---|
| `0x19` | Red key |
| `0x1A` | Green key |
| `0x1B` | Blue key |
| `0x1C` | Yellow key |

It formats `You use the ...` or `You need a ...`. Success calls `seg3:ACB8`, which does not clear the key mask; keys are reusable in this handler family. **VERIFIED_EXE**.

## ID-card-controlled remote terminal — mapped wall type 3

Tracing the USE caller around `seg3:1C2D..1C46` proves that mapped **wall type 3** resolves an associated OBJECT and calls `seg4:21D8`.

`seg4:21D8`:

1. reads OBJECT `+0x01`;
2. stores it in `0x40F8`;
3. tests `1 << OBJECT+01` against ID-card mask `0x4C29`;
4. calls `seg4:2146` on success or `seg3:BCEA` for the missing-card message.

`seg4:2146` prepares segment-7 menu `15DA`:

```text
Open remote doors
Close remote doors
Enable remote cannons
Disable remote cannons
Cancel
```

and changes menu-entry enable state from globals `0x51A4` / `0x51A5` before displaying it.

Thus mapped wall type **3 is an ID-card-controlled remote doors/cannons terminal family**. **VERIFIED_EXE**.

The two ID-card strings are exactly:

```text
index 0 = Red ID card
index 1 = Yellow ID card
```

## Raw-wall variant helpers

`seg3:2334(mappedType, startingRawId)` scans raw wall IDs until `0x8196[rawId] == mappedType`.

`seg3:2426(mappedType)` scans the current 64x64 map and returns the highest raw wall ID currently used for the logical type.

These explain why several visible/state variants may share one logical wall type. **VERIFIED_EXE**.

## Scripted wall type 8 — Episode-1 special cases

`seg3:C0A2(targetCell)` handles mapped wall type 8 and explicitly branches for Episode 1 levels 2 and 7 (1-based branch logic). The E1M7 path contains:

```text
Well done!  You fixed the power!
You already fixed it!
```

Therefore type 8 includes an E1M7 power-repair interaction. The exact E1M2 user-facing action remains **PARTIAL**.

## Current exact dispatcher map

| mapped wall type | handler | classification |
|---|---|---|
| `3` | seg4:`21D8` / `2146` | ID-card remote doors/cannons terminal |
| `8` | seg3:`C0A2` | scripted Episode-1 special interaction |
| `0x0D..0x14` | seg4:`1EE0` | climb up/down menu |
| `0x15..0x18` | seg3:`C126` | Other Side portal/mirror/pentagram gate |
| `0x19..0x1C` | seg4:`20CE` | reusable colored-key gates |
| `0x1D..0x24` | seg4:`1F6A` | Floor 1..10 selector |
| `0x25..0x2C` | seg4:`2076` | Go down / Cancel |

## Remaining special-wall work

- decode the final callback/action IDs behind climb/floor/go-down menus;
- name the remaining individual visual wall variants within each family;
- complete the per-level scripted behavior for wall type 8;
- finish object type `0x26` combination state/reward logic during the OBJECT audit;
- tie the remote-terminal OBJECT `+01` values to the exact Red/Yellow ID-card-controlled variants.
