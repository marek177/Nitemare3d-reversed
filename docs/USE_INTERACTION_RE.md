# USE / interaction (`inputMask 0x0200`) — NITE3W.EXE

Date: 2026-09-17

Closure update: 2026-09-28 — re-audited against Win16 1.10 assembly/decompiler output, retail OBJECTS/WALLS class tables, and reconstructed segment-7 menu records.

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

Door-linked classes are now joined to the retail wall-class dictionaries:

| class | retail family | USE access rule |
|---:|---|---|
| `0x31` | DOORV | ordinary vertical sliding door |
| `0x32` | DOORH | ordinary horizontal sliding door |
| `0x33` | DOORVL | colored-key locked V, environment set 1 |
| `0x34` | DOORHL | colored-key locked H, environment set 1 |
| `0x35` | DOORVL2 | colored-key locked V, environment set 2 |
| `0x36` | DOORHL2 | colored-key locked H, environment set 2 |
| `0x37` | DOORVL3 | colored-key locked V, environment set 3 |
| `0x38` | DOORHL3 | colored-key locked H, environment set 3 |
| `0x39` | DOORVI | ID-card/transport-chamber V |
| `0x3A` | DOORHI | ID-card/transport-chamber H |
| `0x3B` | DOORVR | remote-controlled V; direct USE rejected |
| `0x3C` | DOORHR | remote-controlled H; direct USE rejected |
| `0x3F` | DOORVC | curtain V family |
| `0x40` | DOORHC | curtain H family |

No audited retail wall-class table assigns `0x3D` or `0x3E`; those numeric gaps must not be given invented retail door names.

Classes `0x33..0x38` test colored-key mask `0x4C28`; classes `0x39..0x3A` test ID-card mask `0x4C29`. The bit index comes from linked OBJECT `+0x01`. Classes `0x3B..0x3C` reject the ordinary door route. Door record `+0x14` is set to 1 before `seg3:188A` performs the transition. The audited direct door and remote-terminal USE paths test credentials but do not clear the key/card masks.

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

### `0x0D..0x14` — climb menu and exact callbacks

`seg4:1EE0` passes segment-7 menu `0x155C`:

```text
Climb up
Climb down
Cancel
```

The handler uses `seg3:2334`/`2426` to determine which direction is currently possible.

The segment-7 records and central action dispatcher close the callbacks:

- **Climb up** = action `27 / 0x1B` -> `seg3:2800(+1)`;
- **Climb down** = action `28 / 0x1C` -> `seg3:2800(-1)`;
- **Cancel** = generic action `25 / 0x19`, not action 29.

This corrects an older menu-model label in which action 29 was called StairCancel. **VERIFIED_EXE**.

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

The number of active floor records is derived from the raw wall variants associated with the logical wall type. `seg4:1F6A` writes each enabled menu record's `+02` value as:

```text
targetRawWallId - currentRawWallId
```

Action `26 / 0x1A` walks the selected floor record and passes that signed value to `seg3:2800`. `seg3:2800` finds the destination raw-wall variant in the current map, selects an available neighboring cell, commits the player at tile center (`x*64+32, y*64+32`) and sets the resulting cardinal facing. **VERIFIED_EXE**.

### `0x25..0x2C` — go-down confirmation

`seg4:2076` passes segment-7 menu `0x15A4`:

```text
Go down
Cancel
```

Its exact callbacks are:

- **Go down** = action `29 / 0x1D` -> `seg3:2800(-1)`;
- **Cancel** = action `25 / 0x19`.

Thus action 29 is a real descend operation, not a cancel action. This also corrects an earlier provisional classification: **`0x25..0x2C` are not the combination-lock family.** **VERIFIED_EXE**.

## Combination input — object type `0x26`, not wall `0x25..0x2C`

Mapped object types `0x26` and `0x27` dispatch through `seg3:AD9E`. For mapped object type **`0x26`**, the state-zero branch opens the exact prompt:

```text
What's the combination?  0000000
```

The data segment also contains code strings such as `01532`, `080993`, `372535` and the failure text `I'm sorry, that is not the correct combination.`

Retail OBJECTS data identifies mapped object type **`0x26` as SAFE**. The six SAFE subtypes correspond to the four colored keys and two ID cards.

The state/reward chain is now decoded:

1. SAFE state 0 opens the combination editor.
2. On a correct combination, callback `seg3:AD00` writes `OBJECT+03 = subtype + 2` and plays the open/activation SFX request.
3. A subsequent USE reaches `AD9E`; for SAFE it calls reward helper `ABFC(state + 4)`, i.e. reward code `subtype + 6`.
4. Codes `6..9` set Red/Green/Blue/Yellow key bits; codes `10..11` set Red/Yellow ID-card bits.
5. The object is then set to state 1. Further USE follows the empty-container message path.

Thus SAFE combinations are not an abstract prompt only: their reward dispatch is directly tied to key/card inventory bits. **VERIFIED_EXE + VERIFIED_DATA**.


## Object type `0x27` — TRUNK reward state machine

Retail OBJECTS data identifies class `0x27` as **TRUNK**. Known variants are labeled for Health, Ammo, Eyes, Balls and Red key.

`seg3:AD9E` implements a two-step open/take flow:

- on state 0, it writes `OBJECT+03 = subtype + 2` and requests SFX `0x32`;
- on the next USE, it passes that state directly to `seg3:ABFC`, then sets state 1;
- state 1 displays the exact text **"It's empty!"**.

The reward helper maps codes:

| code | effect |
|---:|---|
| 2 | HP = 100; score +150 |
| 3 | refill laser to 100; also refill silver/wand ammo when those weapons are owned; score +100 |
| 4 | `0x4C43 = 100` (Magic Eye charge) |
| 5 | `0x4C42 = 100` (Crystal Ball charge) |
| 6..9 | Red/Green/Blue/Yellow key bit |
| 10..11 | Red/Yellow ID-card bit |

Because TRUNK uses `reward = subtype + 2`, its retail subtype labels line up with Health, Ammo, Eyes, Balls and Red key. **VERIFIED_EXE + VERIFIED_DATA**.

## Object type `0x29` — ACTION / Radio

Retail Episode-1 OBJECTS data identifies mapped type `0x29` as **ACTION**, with object ID `0x45` named **Radio**.

`seg3:B010` only acts when episode = 1 and zero-based level index = 8 (**E1M9**). It calls `seg3:AE56(0)`, whose exact on-screen string is:

```text
Let's find some dance music!
```

The path plays runtime SFX request `0x45`, changes the targeted ACTIONSPOT-associated guards to scripted state `0x14` with timer `0x70`, and switches their runtime resource/class presentation for the dance sequence. A later `AE56(1)` path restores the affected actors to the normal movement/state path.

Status: **VERIFIED_EXE + VERIFIED_DATA** for the Radio identity, E1M9 gate and script transition.

## Guard-family USE hook `seg3:AB3E`

When USE targets an object whose property table marks it as a GUARD-family runtime object, `seg3:AB3E` resolves the GUARD record. It displays:

```text
I've nothing left!
```

only when `GUARD+0x0B == 0x0C`.

The condition and text are **VERIFIED_EXE**. The 2026-09-29 writer audit now classifies GUARD state `0x0C` as a **retail-dormant / legacy-compatible state**: its handler and this USE text survive, but no normal writer was recovered in Win16 1.3/1.6/1.8/1.10 or DOS 1.0/1.7/1.8(=1.9)/2.0. Its sibling `0x0D` is likewise dormant and shares the same sequence-refresh handler. This closes the shipped-game reachability question without inventing a historical name such as corpse/loot state.

## Wall type 8 — scripted Episode-1 interactions

`seg3:C0A2(targetCell)` handles mapped wall type 8. It has explicit Episode-1 branches for levels 2 and 7 (1-based branch logic). The E1M7 branch contains:

```text
Well done!  You fixed the power!
You already fixed it!
```

Retail WALLS data identifies the two Episode-1 SPECIAL1 visuals involved here:

- **E1M2 / wall ID 0x56 — Office - Morphing chalkboard.** The USE path finds the linked runtime render/sequence object, writes `0x96` to its per-resource timer/state slot, and requests runtime SFX `0x44`.
- **E1M7 / wall ID 0x12 — Kitchen - Fuse box.** This is the power-repair path with the success/already-fixed text and event-state updates.

Therefore E1M2 is no longer an unnamed wall-type-8 action; it is the morphing-chalkboard SPECIAL1 case. **VERIFIED_EXE + VERIFIED_DATA**.

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

The 2026-09-28/29 closure passes resolve the former menu-callback, SAFE/TRUNK/Radio, retail door-class, E1M2 SPECIAL1 and GUARD-state-0x0C reachability TODOs. Remaining work is narrower:

- finish any class-specific visual/event side effects that occur after the already-recovered door/panel/warp state changes;
- regression-test the complete USE matrix against original runtime/demo trajectories, including repeated-use, blocked, credential-missing, moving-door, floor/stair and scripted-level edge cases.

Until those runtime-parity checks are complete, USE is not marked 100%.
