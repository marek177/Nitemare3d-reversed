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

Thus USE reach is **one adjacent tile**, with diagonal view octants quantized to the neighboring cardinal cell. User-facing north/east/south/west labels are intentionally omitted here until the coordinate convention is fully normalized.

Status: **VERIFIED_EXE**.

## Top-level dispatcher

The target cell is classified through:

- wall-type mapping `0x8196[wallByte]`;
- wall property table `0x7E94[wallByte]`;
- object-type mapping `0x8296[objectByte]`;
- object property table `0x7F94[objectByte]`.

The major directly traced target families are below.

## Dynamic doors

If the target wall carries property bit `0x08`, USE resolves the dynamic-wall record through `seg3:1296`.

Door records:

```text
base   = 0x9DD6
stride = 0x16 = 22 bytes
max    = 64
```

The executable contains `Door not in map` and `MAXDOORS exceeded (%d)`.

### Lock/key/card checks

The linked OBJECT class is checked before the state transition:

- classes `0x33..0x38` test a key/lock mask through global `0x4C28` and an index derived from OBJECT `+0x01`;
- classes `0x39..0x3A` test another lock/card mask through global `0x4C29`;
- if the latter requirement is missing, `seg3:BCEA` reaches the message `You need a %s`;
- classes `0x3B..0x3C` reject this ordinary USE route.

Original executable strings include `Red key`, `Green key`, `Blue key`, `Yellow key`, `Red ID card`, and `Yellow ID card`. The exact class-to-string mapping still requires decoding of the associated pointer/index tables, so individual classes are not named here yet.

Status: **VERIFIED_EXE** for the class ranges/mask checks; exact class names **PARTIAL**.

### Door state transition

When the interaction is permitted:

- door record `+0x14` is set to `1`;
- `seg3:188A(doorRecord, octant)` performs the door transition;
- state byte/word at `DoorRuntime+0x0C` is switched among the observed door states;
- states `0` and `4` are the states accepted by the collision passability helper;
- sound IDs around `0x25/0x26` are used by the transition path;
- linked classes `0x3D/0x3E` have an additional facing/orientation restriction.

Exact user-facing labels for every numeric door state remain **PARTIAL**.

## PANEL runtime family

If the target object maps to type `3`, USE calls `seg3:12E8(targetCell)`.

That routine searches a 22-byte runtime table at `0xA356`. Initialization `seg3:16D6..181B` creates these records for mapped object type `3`, enforces a maximum of **32**, and the executable contains `MAXPANELS exceeded (%d)`.

```text
PanelRuntime base   = 0xA356
PanelRuntime stride = 0x16 = 22 bytes
Maximum panels      = 32
```

USE writes panel record `+0x14 = 2`, plays SFX `0x27`, and proceeds through the panel-linked state/action path.

Status: **VERIFIED_EXE** that this is the panel runtime family; exact per-panel action semantics are still being classified.

## Pushable-object path

Mapped object type `0x28` enters the push path:

1. compute the adjacent destination cell in the current octant;
2. call `seg3:21B6(targetCell, destinationCell)`;
3. find the push runtime record through `seg3:133A`;
4. reject the push if the destination carries generic blocking property bit `0x02`;
5. load signed movement deltas from two octant tables;
6. activate the push record for eight updates.

The signed tables are:

```text
DS 0x00A4: [ 0, +8, +8,  0,  0, -8, -8,  0 ]
DS 0x00AC: [-8,  0,  0, +8, +8,  0,  0, -8 ]
```

The push pool is at `0xA616`, uses 6-byte records and has maximum 12. Initialization `seg3:181C..1889` scans OBJECT class/type `0x28`; the executable contains `Push not in map` and `MAXPUSHES exceeded (%d)`.

This agrees with `docs/PUSHABLE_RE.md`: eight updates at eight world units produce exactly one 64-unit tile move.

Status: **VERIFIED_EXE**.

## Special wall families

### Wall types 9..12

`seg3:25F8` handles mapped wall types `9..0x0C` specially in relation to the current level number:

- type `9` derives current level +1;
- type `10` derives current level +2;
- types `11/12` follow related special paths without the same increment.

Original EXE strings include `This is the portal to the` and `Invalid level #`, strongly tying this area to level-transition / portal-like logic. Exact type-to-visible-feature naming remains **PARTIAL** until all xrefs are closed.

### Wall types 0x0D..0x2C

`seg3:277A` groups these types into special-wall handlers:

| mapped wall type | handler |
|---|---|
| default within `0x0D..0x2C` | `seg3:1EE0` |
| `0x15..0x18` | `seg3:C126` |
| `0x19..0x1C` | `seg3:20CE` |
| `0x1D..0x24` | `seg3:1F6A` |
| `0x25..0x2C` | `seg3:2076` |

The executable also contains interaction strings such as `What's the combination?  0000000`, `the correct combination.`, `Open remote doors`, and `Close remote doors`. Those strings are high-value anchors for the next xref pass, but the grouped ranges are not assigned final game-facing labels until the specific handlers are fully decoded.

Status: **VERIFIED_EXE** for dispatch ranges, **PARTIAL** for names/effects.

## Other directly observed USE branches

- mapped wall type `4`: writes `0x4C20 = 100` before the common action/sound path. Exact visible source/object name is **PARTIAL**; the effect itself is **VERIFIED_EXE**.
- mapped wall type `5`: when `0x4C22 != 0` and `0x4C1D < 100`, adds 20 to `0x4C1D`, decrements `0x4C22`, then follows common action/sound handling. **VERIFIED_EXE**, resource names **PARTIAL**.
- mapped wall type `6`: analogous, adding 20 to `0x4C21` when below 100 and consuming one `0x4C22`. **VERIFIED_EXE**, resource names **PARTIAL**.
- mapped wall type `8`: dispatches to `seg3:C0A2(targetCell)`. Exact semantics **PARTIAL**.
- object property bit `0x08`: dispatches to `seg3:AB3E(targetCell)`; the property is generated for mapped object types `0x08..0x25`. Exact family semantics **PARTIAL**.
- object types `0x26` and `0x27`: dispatch to `seg3:AD9E(targetCell, objectType)`. **VERIFIED_EXE**, exact labels **PARTIAL**.
- object type `0x29`: dispatches to `seg3:B010(targetCell)` and contains episode/level-specific logic. Exact label **PARTIAL**.

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

The important correction is that `kUseCellDelta` is not a ray length or arbitrary range: it is one exact adjacent-cardinal-cell offset selected by the 8-way octant.

## Relation to Catacomb Abyss / Wolf3D

Catacomb Abyss performs substantial wall/door/special-tile handling through movement collision (`HitSpecialTile`) rather than using the same Nitemare dispatcher. Wolf3D has a classic `Use()` front-cell action path. Nitemare's explicit rising-edge USE and one-adjacent-cell selection is therefore conceptually closer to Wolf's front-cell action model, while its property-table and runtime door/panel/push architecture is its own implementation.

No source-level identity is claimed.

## Remaining TODO before USE is 100%

- Decode `seg3:1EE0`, `1F6A`, `2076`, `20CE`, `C126` and map them to exact switch/combination/remote-door/etc. names.
- Resolve the precise semantics of mapped wall types `4..12`.
- Resolve `AB3E`, `AD9E`, `B010`, and `C0A2` to exact object/action names.
- Decode class `0x33..0x3E` lock/key/card identity tables.
- Label every dynamic-door state at runtime `+0x0C`.
- Regression-test USE against all three original demo streams, especially DEMO.3's dense `0x0200` interaction pattern.
