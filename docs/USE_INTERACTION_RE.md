# USE / interaction (`inputMask 0x0200`) — NITE3W.EXE

Date: 2026-09-17

This document traces the player USE/ACTION input from the recorded/input bit to the interaction dispatcher and its major target families.

## Evidence labels

- **VERIFIED_EXE** — directly demonstrated by original executable control flow/data.
- **PARTIAL** — dispatcher family or effect is known but exact game-facing label remains unresolved.

## Rising-edge input detection

The gameplay input routine around `seg3:98ED..9AA5` reads the high-byte input bit and edge-detects it. Demo/input mask **`0x0200`** is therefore USE/ACTION, triggered only on a rising edge; `0x012C` is the previous-use latch. The final dispatcher is `seg3:1A22`.

Status: **VERIFIED_EXE**.

## Exact target-cell selection

`seg3:1A22` does not cast a variable-distance ray. It selects one adjacent cardinal MAP cell from current octant `0x4BEC` using DS table `0x009A`:

```text
[-64, +1, +1, +64, +64, -1, -1, -64]
```

The value is multiplied by two because each MAP cell is two bytes and added to current-cell pointer `0x4C10:0x4C12`. Diagonal view octants are quantized to the adjacent cardinal cell.

Status: **VERIFIED_EXE**.

## Main classification inputs

The selected cell is classified through:

- `0x8196[wallByte]` — mapped/logical wall type;
- `0x7E94[wallByte]` — wall property bits;
- `0x8296[objectByte]` — mapped/logical object type;
- `0x7F94[objectByte]` — object property bits.

## Dynamic doors

Wall property bit `0x08` selects the dynamic-door path. Runtime doors are found through `seg3:1296`:

```text
DoorRuntime base   = 0x9DD6
DoorRuntime stride = 0x16 = 22 bytes
Maximum doors      = 64
```

Door-linked OBJECT classes `0x33..0x38` test colored-key mask `0x4C28`; classes `0x39..0x3A` test ID-card mask `0x4C29`. The bit index comes from OBJECT `+0x01`. Classes `0x3B..0x3C` reject the ordinary door route. Door record `+0x14` is set to 1 before `seg3:188A` performs the transition. Runtime door state `+0x0C` values 0 and 4 are the states accepted by the collision passability helper.

Exact inventory strings recovered directly from the executable:

| index | colored key | ID card |
|---:|---|---|
| 0 | Red key | Red ID card |
| 1 | Green key | Yellow ID card |
| 2 | Blue key | — |
| 3 | Yellow key | — |

Thus `0x4C28` is the four-colored-key mask and `0x4C29` is the two-ID-card mask. **VERIFIED_EXE**.

## Wall type 3 — remote-control terminal

A correction from direct call-chain tracing: in `seg3:1A22`, mapped **wall type 3** reaches a lookup and then far-calls `seg4:21D8`.

`seg4:21D8` reads OBJECT `+0x01`, stores it in `0x40F8`, tests `1 << index` against ID-card mask `0x4C29`, and either:

- calls `seg4:2146` when the required card is present; or
- calls `seg3:BCEA(index)` to display the missing-card message.

`seg4:2146` prepares the segment-7 menu at `15DA`, whose exact actions are:

```text
Open remote doors
Close remote doors
Enable remote cannons
Disable remote cannons
Cancel
```

It enables/disables entries from runtime state (`0x51A4`, `0x51A5`) before invoking the menu.

Therefore mapped wall type **3 is an ID-card-controlled remote doors/cannons terminal family**. **VERIFIED_EXE**.

## PANEL runtime family

Mapped object type 3 follows a separate path through `seg3:12E8(targetCell)` and a 22-byte runtime table:

```text
PanelRuntime base   = 0xA356
PanelRuntime stride = 0x16 = 22 bytes
Maximum panels      = 32
```

USE writes panel record `+0x14 = 2`, plays SFX `0x27`, and updates linked runtime state. Do not confuse this object-type-3 PANEL family with wall-type-3 remote terminal above. **VERIFIED_EXE**.

## Pushable-object path

Mapped object type `0x28` enters `seg3:21B6`. The destination is rejected by generic blocking property bit `0x02`; movement deltas come from octant tables:

```text
DS 0x00A4: [ 0, +8, +8,  0,  0, -8, -8,  0 ]
DS 0x00AC: [-8,  0,  0, +8, +8,  0,  0, -8 ]
```

Push pool: base `0xA616`, stride 6, max 12. Eight updates at eight units move exactly one 64-unit tile. **VERIFIED_EXE**.

## Special wall dispatcher `seg3:277A`

NE relocation-chain decoding proves the target segments:

| mapped wall type | target | segment | exact decoded UI/function family |
|---|---:|---:|---|
| `0x0D..0x14` | `1EE0` | 4 | **Climb up / Climb down / Cancel** |
| `0x15..0x18` | `C126` | 3 | Other Side portal / mirror / four-pentagram gate |
| `0x19..0x1C` | `20CE` | 4 | Red/Green/Blue/Yellow-key gates |
| `0x1D..0x24` | `1F6A` | 4 | **Floor 1..Floor 10 selector** |
| `0x25..0x2C` | `2076` | 4 | **Go down / Cancel** confirmation |

The first, fourth and fifth classifications come from the actual segment-7 menu records, not from string proximity.

### `0x0D..0x14` — climb menu

`seg4:1EE0` passes segment-7 menu `0x155C`:

```text
Climb up
Climb down
Cancel
```

The handler uses `seg3:2334`/`2426` to determine which direction is currently possible. **VERIFIED_EXE**.

### `0x15..0x18` — pentagram / Other Side family

`seg3:C126` tests four-pentagram mask `0x4C45`. Exact bit order:

| bit | pentagram |
|---:|---|
| `0x01` | Red |
| `0x02` | Green |
| `0x04` | Blue |
| `0x08` | Yellow |

OBJECT class `0x3C` sets `0x4C45 |= 1 << OBJECT+01`, proving it is the pentagram collectible class. The handler contains the portal message requiring all four pentagrams and mapped type `0x16` has the exact message `The mirror crack'd from side to side!`. **VERIFIED_EXE**.

### `0x19..0x1C` — reusable colored keys

`seg4:20CE` computes `index = mappedWallType - 0x19`, tests `1 << index` in `0x4C28`, and formats either `You use the <key>` or `You need a <key>`.

```text
0x19 Red key
0x1A Green key
0x1B Blue key
0x1C Yellow key
```

The success path does not clear the key mask, so these keys are reusable in this family. **VERIFIED_EXE**.

### `0x1D..0x24` — elevator/floor selector

`seg4:1F6A` builds/filters segment-7 records beginning at `0x1496`. The menu is exactly:

```text
Floor 1
Floor 2
...
Floor 10
```

The number of active floor records is derived from the raw wall variants associated with the logical wall type. **VERIFIED_EXE**.

### `0x25..0x2C` — go-down confirmation

`seg4:2076` passes segment-7 menu `0x15A4`:

```text
Go down
Cancel
```

This corrects an earlier provisional classification: **`0x25..0x2C` are not the combination-lock family.** Direct segment-7 menu decoding supersedes that earlier interpretation. **VERIFIED_EXE**.

## Combination input — object type `0x26`, not wall `0x25..0x2C`

Mapped object types `0x26` and `0x27` dispatch through `seg3:AD9E`. For mapped object type **`0x26`**, the state-zero branch opens the exact prompt:

```text
What's the combination?  0000000
```

The data segment also contains code strings such as `01532`, `080993`, `372535` and the failure text `I'm sorry, that is not the correct combination.`

Therefore the combination-input mechanism belongs to **object type `0x26`**. Its precise visual/object name remains PARTIAL until OBJECT definitions and state fields are tied together. **VERIFIED_EXE** for the prompt/type association.

## Wall type 8 — scripted Episode-1 interactions

`seg3:C0A2(targetCell)` handles mapped wall type 8. It has explicit Episode-1 branches for levels 2 and 7 (1-based branch logic). The E1M7 branch contains:

```text
Well done!  You fixed the power!
You already fixed it!
```

Thus wall type 8 includes the E1M7 power-repair interaction. E1M2 exact user-facing role remains **PARTIAL**.

## Wall-variant helpers

- `seg3:2334(mappedType, startingRawId)` scans raw wall IDs until `0x8196[rawId] == mappedType`.
- `seg3:2426(mappedType)` scans the current 64x64 map and returns the highest raw wall ID used for that mapped type.

Several raw graphical/state variants may therefore share one logical wall type. **VERIFIED_EXE**.

## High-level reconstruction

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

    DispatchMappedWallType(target);
    DispatchMappedObjectType(target);
}
```

## Remaining TODO before USE is 100%

- finish exact action/state callbacks behind the climb, floor and go-down menus;
- name mapped object types `0x26`, `0x27`, `0x29` and `AB3E` family from OBJECT data;
- complete door class `0x33..0x3E` mapping and door-state labels;
- finish E1M2 wall-type-8 special action;
- regression-test all interactions against the demo streams, especially DEMO.3.
