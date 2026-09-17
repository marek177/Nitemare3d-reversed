# USE / interaction (`inputMask 0x0200`) — NITE3W.EXE

Date: 2026-09-17

This document traces the player USE/ACTION input from the recorded/input bit to the interaction dispatcher and its major target families.

## Evidence labels

- **VERIFIED_EXE** — directly demonstrated by original executable control flow/data.
- **PARTIAL** — dispatcher family or effect is known but exact game-facing label remains unresolved.

## Rising-edge input detection

The gameplay input routine around `seg3:98ED..9AA5` reads the high-byte input bit and edge-detects it:

```asm
seg3:98F6  mov al,[0x3757]
seg3:98F9  and al,0x02
seg3:98FB  shr al,1
seg3:98FD  mov [bp-1],al
...
seg3:9A88  cmp byte [bp-1],0
seg3:9A8C  je  9A9C
seg3:9A8E  mov al,[bp-1]
seg3:9A91  cmp al,[0x012C]
seg3:9A95  je  9A9C
seg3:9A97  lcall ...:1A22
...
seg3:9AA2  mov al,[bp-1]
seg3:9AA5  mov [0x012C],al
```

Therefore demo/input mask **`0x0200`** is the USE/ACTION input, and the interaction fires only on a **rising edge**. Holding the key does not continuously retrigger it. `0x012C` is the previous USE state latch.

The final dispatcher is `seg3:1A22` (raw approximately `0x179E2`).

Status: **VERIFIED_EXE**.

## Exact target-cell selection

`seg3:1A22` does not cast a variable-distance ray. It uses the current 45-degree octant in `0x4BEC` to select exactly one adjacent cardinal MAP cell.

The signed table at DS `0x009A` is:

```text
C0 01 01 40 40 FF FF C0
```

or as signed cell deltas:

```text
[-64, +1, +1, +64, +64, -1, -1, -64]
```

The routine multiplies this delta by 2 because a MAP cell is two bytes, then adds it to current-cell pointer `0x4C10:0x4C12`.

| octant | cell delta |
|---:|---:|
| 0 | -64 |
| 1 | +1 |
| 2 | +1 |
| 3 | +64 |
| 4 | +64 |
| 5 | -1 |
| 6 | -1 |
| 7 | -64 |

Thus USE reach is **one adjacent tile**, with diagonal view octants quantized to the neighboring cardinal cell. User-facing north/east/south/west labels are intentionally omitted until the coordinate convention is fully normalized.

Status: **VERIFIED_EXE**.

## Top-level dispatcher

The target cell is classified through:

- wall-type mapping `0x8196[wallByte]`;
- wall property table `0x7E94[wallByte]`;
- object-type mapping `0x8296[objectByte]`;
- object property table `0x7F94[objectByte]`.

## Dynamic doors

If the target wall carries property bit `0x08`, USE resolves the dynamic-wall record through `seg3:1296`.

```text
DoorRuntime base   = 0x9DD6
DoorRuntime stride = 0x16 = 22 bytes
Maximum doors      = 64
```

The executable contains `Door not in map` and `MAXDOORS exceeded (%d)`.

### Lock/key/card checks

The linked OBJECT class is checked before the state transition:

- classes `0x33..0x38` test a bit in global key/lock mask `0x4C28`, with the bit index from OBJECT `+0x01`;
- classes `0x39..0x3A` test global ID-card mask `0x4C29`, again indexed by OBJECT `+0x01`;
- missing card access reaches `seg3:BCEA` and `You need a %s`;
- classes `0x3B..0x3C` reject this ordinary USE route.

`seg3:BCB6` proves the exact four-entry key-name table:

| index | key string |
|---:|---|
| 0 | Red key |
| 1 | Green key |
| 2 | Blue key |
| 3 | Yellow key |

`seg3:BCEA` uses the two-entry card-name table:

| index | card string |
|---:|---|
| 0 | Red ID card |
| 1 | Yellow ID card |

This establishes the meaning of the inventory masks independently of editor labels. The exact `0x33..0x3E` class-to-lock construction still needs the OBJECT `+01` audit before every class gets a final name.

Status: **VERIFIED_EXE**.

### Door state transition

When the interaction is permitted:

- door record `+0x14` is set to `1`;
- `seg3:188A(doorRecord, octant)` performs the transition;
- runtime state at `DoorRuntime+0x0C` is switched among the observed door states;
- states `0` and `4` are accepted by the collision passability helper;
- sound IDs around `0x25/0x26` occur on the transition path;
- linked classes `0x3D/0x3E` have an additional facing/orientation restriction.

Exact human-readable names for every numeric door state remain **PARTIAL**.

## PANEL runtime family

If the target object maps to type `3`, USE calls `seg3:12E8(targetCell)`.

Initialization `seg3:16D6..181B` creates 22-byte records at `0xA356`, maximum 32, and the executable contains `MAXPANELS exceeded (%d)`.

```text
PanelRuntime base   = 0xA356
PanelRuntime stride = 0x16 = 22 bytes
Maximum panels      = 32
```

USE writes panel record `+0x14 = 2`, plays SFX `0x27`, and updates linked panel/door-like state.

Status: **VERIFIED_EXE** for the panel runtime family; individual panel action semantics remain **PARTIAL**.

## Pushable-object path

Mapped object type `0x28` enters the push path:

1. compute the adjacent destination cell in the current octant;
2. call `seg3:21B6(targetCell, destinationCell)`;
3. find the push runtime record through `seg3:133A`;
4. reject the push if the destination carries generic blocking property bit `0x02`;
5. load signed movement deltas from the octant tables;
6. activate the push record for eight updates.

```text
DS 0x00A4: [ 0, +8, +8,  0,  0, -8, -8,  0 ]
DS 0x00AC: [-8,  0,  0, +8, +8,  0,  0, -8 ]
```

The push pool is at `0xA616`, uses 6-byte records and has maximum 12. Initialization `seg3:181C..1889` scans OBJECT class/type `0x28`; the executable contains `Push not in map` and `MAXPUSHES exceeded (%d)`.

Eight updates at eight world units produce one 64-unit tile move, agreeing with `docs/PUSHABLE_RE.md`.

Status: **VERIFIED_EXE**.

## Special wall families

### Wall types 9..12

`seg3:25F8` handles mapped wall types `9..0x0C` relative to the current level:

- type `9` produces current level +1;
- type `10` produces current level +2;
- types `11/12` return the current level through related paths.

The executable contains `This is the portal to the` and `Invalid level #`. The numeric behavior is **VERIFIED_EXE**; exact visible-feature naming of all four types remains **PARTIAL**.

### Wall-type dispatcher `seg3:277A`

The dispatcher separates mapped wall types `0x0D..0x2C` into five handler families. NE relocation-chain decoding is important here: three targets reside in **segment 4**, not segment 3.

| mapped wall type | far target | target segment | status |
|---|---:|---:|---|
| default within `0x0D..0x2C` | `1EE0` | 4 | VERIFIED_EXE |
| `0x15..0x18` | `C126` | 3 | VERIFIED_EXE |
| `0x19..0x1C` | `20CE` | 4 | VERIFIED_EXE |
| `0x1D..0x24` | `1F6A` | 4 | VERIFIED_EXE |
| `0x25..0x2C` | `2076` | 4 | VERIFIED_EXE |

### Types 0x19..0x1C — exact colored-key family

`seg4:20CE` computes `index = mappedWallType - 0x19`, looks up the corresponding name through `seg3:BCB6`, and tests bit `1 << index` in `0x4C28`.

This proves the mapping:

| mapped wall type | required key |
|---:|---|
| `0x19` | Red key |
| `0x1A` | Green key |
| `0x1B` | Blue key |
| `0x1C` | Yellow key |

The handler formats `You use the ...` when the key is present and `You need a ...` otherwise. The success helper `seg3:ACB8` only plays SFX `0x32`; it does **not** clear `0x4C28`, so this path does not consume the key.

Status: **VERIFIED_EXE**, including reusable-key behavior for this handler family.

### Types 0x25..0x2C — combination-check family

`seg4:2076` compares the target wall's raw wall-ID state against the canonical raw ID for the requested mapped wall type. On a mismatch it enters the UI/message path that references the original combination-lock text region, including:

- `What's the combination?  0000000`
- `I'm sorry, that is not\nthe correct combination.`
- stored code strings including `01532`, `080993`, and `372535`.

This is sufficient to classify `0x25..0x2C` as the **combination-check / combination-lock family**. The exact per-type code/state correspondence is still **PARTIAL**.

### Types 0x1D..0x24

`seg4:1F6A` enumerates raw wall variants belonging to a mapped wall type using `seg3:2334` / `seg3:2426`, builds a menu/state table, and consults inventory/card-related state. Its exact game-facing role is not yet fully named and remains **PARTIAL**.

### Default 0x0D..0x14 family

`seg4:1EE0` also uses the wall-variant lookup helpers `seg3:2334` / `seg3:2426` and updates wall-related runtime/display state. Exact labels remain **PARTIAL**.

### Types 0x15..0x18

`seg3:C126` is the only one of these five families that remains in segment 3. It builds text/state based on bitfield `0x4C45` and routes through additional level/special-wall logic. Exact names remain **PARTIAL**.

The executable also contains `Open remote doors` and `Close remote doors`; these remain xref anchors rather than prematurely assigned handler names.

## Other directly observed USE branches

- mapped wall type `4`: plays SFX `0x2B`, writes `0x4C20 = 100`, then follows the common action path. Effect **VERIFIED_EXE**, visible source name **PARTIAL**.
- mapped wall type `5`: when `0x4C22 != 0` and `0x4C1D < 100`, adds 20 to `0x4C1D`, decrements `0x4C22`, and follows common action handling. **VERIFIED_EXE**, resource names **PARTIAL**.
- mapped wall type `6`: analogous, adding 20 to `0x4C21` when below 100 and consuming one `0x4C22`. **VERIFIED_EXE**, resource names **PARTIAL**.
- mapped wall type `8`: dispatches to `seg3:C0A2(targetCell)`. It contains explicit Episode-1 level-specific branches; exact visible semantic **PARTIAL**.
- object property bit `0x08`: dispatches to `seg3:AB3E(targetCell)`; the property is generated for mapped object types `0x08..0x25`. Exact family semantics **PARTIAL**.
- object types `0x26` and `0x27`: dispatch to `seg3:AD9E(targetCell, objectType)`. **VERIFIED_EXE**, exact labels **PARTIAL**.
- object type `0x29`: dispatches to `seg3:B010(targetCell)` and contains episode/level-special behavior. Exact label **PARTIAL**.

## Wall-variant lookup helpers

Two helpers explain several of the special-wall handlers:

- `seg3:2334(type, startingRawId)` scans raw wall IDs until `0x8196[rawId] == type`;
- `seg3:2426(type)` scans the current 64x64 map and returns the highest raw wall ID currently used for that mapped type.

This confirms that multiple raw wall graphics/states can share one logical mapped wall type and that some USE handlers cycle or compare those raw variants rather than simply toggling a binary wall flag.

Status: **VERIFIED_EXE**.

## Reconstructed high-level USE skeleton

```cpp
void UsePressed()
{
    if (!RisingEdge(useCurrent, usePrevious))
        return;

    Cell* target = currentCell + kUseCellDelta[octant];

    if (wallFlags[target->wall] & 0x08) {
        UseDynamicDoor(target);
        return;
    }

    DispatchSpecialWall(target);
    DispatchSpecialObject(target);
}
```

The key correction is that `kUseCellDelta` is not a ray length: it is one adjacent-cardinal-cell offset selected by the 8-way octant.

## Relation to Catacomb Abyss / Wolf3D

Catacomb Abyss performs substantial wall/door/special-tile handling through movement collision (`HitSpecialTile`) rather than using the same Nitemare dispatcher. Wolf3D has a classic front-cell `Use()` path. Nitemare's explicit rising-edge USE and adjacent-cell selection is conceptually closer to Wolf's front-cell action model, while the property-table plus door/panel/push runtime architecture is its own implementation.

No source-level identity is claimed.

## Remaining TODO before USE is 100%

- Fully name `seg4:1EE0`, `seg4:1F6A`, and `seg3:C126` from their final UI/action xrefs.
- Resolve exact per-type code/state mapping for combination family `0x25..0x2C`.
- Resolve precise semantics of mapped wall types `4..12`.
- Resolve `AB3E`, `AD9E`, `B010`, and `C0A2` to exact object/action names.
- Complete the `0x33..0x3E` door-class audit using OBJECT `+01` and key/card indices.
- Label every dynamic-door state at runtime `+0x0C`.
- Regression-test USE against all three original demo streams, especially DEMO.3's dense `0x0200` pattern.
