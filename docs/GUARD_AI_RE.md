# GUARD AI reverse engineering

Date: 2026-09-17
Evidence: original NITE3W.EXE V1.10 Win16 binary (230400 bytes), reconstructed USER.SAV writer/layout, and direct 16-bit disassembly.

## Fixed GUARD anchors

- record stride: **0x1A = 26 bytes**
- capacity: **100**
- USER.SAV GUARD pool: **0xB43B..0xBE62**, 0x0A28 bytes
- `+0x0B state`, `+0x0C next_state`, `+0x0D o_id`
- `+0x08` is a runtime OBJECT slot/index; EXE multiplies it by **0x1C**

Evidence: **VERIFIED_EXE + VERIFIED_SAVE_LAYOUT**.

## 28-byte OBJECT record: new verified linkage

Direct disassembly of the level/object initialization path proves a fixed **0x1C = 28-byte** runtime OBJECT record. The object pool is walked with `add ...,0x1C`; GUARD code resolves its associated object with `guard[+0x08] * 0x1C`.

The initialization path writes the following object fields:

| OBJECT offset | Width | Role | Status |
|---:|---:|---|---|
| `+0x00` | 1 | object/map ID | VERIFIED access |
| `+0x01` | 1 | subtype/variant-like value | PARTIAL semantic |
| `+0x02` | 1 | signed animation/render offset component | PARTIAL semantic |
| `+0x03` | 1 | signed animation/render offset component | PARTIAL semantic |
| `+0x04` | 1 | definition-table ID | VERIFIED access |
| `+0x05` | 1 | flags; bit **0x08** selects GUARD creation | **VERIFIED_EXE** |
| `+0x06` | 1 | runtime object type/class | VERIFIED access |
| `+0x07` | 1 | GUARD index for guard objects | **VERIFIED_EXE**: assigned from current GUARD count |
| `+0x08` | 4 | runtime value initialized to zero | semantic TODO |
| `+0x0C` | 2 | map-cell far-pointer offset | **VERIFIED_EXE** |
| `+0x0E` | 2 | map-cell far-pointer segment | **VERIFIED_EXE** |
| `+0x10` | 2 | **world X** | **VERIFIED_EXE** |
| `+0x12` | 2 | **world Y** | **VERIFIED_EXE** |
| `+0x14..0x19` | 6 | unknown | TODO |
| `+0x1A` | 1 | runtime byte initialized to zero | VERIFIED write; semantic TODO |
| `+0x1B` | 1 | unknown | TODO |

### Why +0x10/+0x12 are X/Y

This is now stronger than the previous PARTIAL classification. A runtime routine resolves an object by index and computes:

```text
dy = object[+0x12] - playerY
dx = object[+0x10] - playerX
angle = direction_function(dx, dy)
```

Other object/guard routines use the same fields for world/map calculations. Therefore `OBJECT+0x10` and `OBJECT+0x12` are promoted to **VERIFIED_EXE world X/Y**.

`OBJECT+0x0C:+0x0E` are a separate far pointer to the object's map cell. GUARD lookup code compares an input far pointer against these two words, so these must not be confused with X/Y coordinates.

## GUARD field recovery

| Offset | Width | Recovered role | Status |
|---:|---:|---|---|
| `+0x00` | 2 | sequence/definition-derived value | PARTIAL |
| `+0x02` | 4 | timestamp/time value | VERIFIED_EXE |
| `+0x06` | 2 | state/countdown timing value | VERIFIED_EXE |
| `+0x08` | 2 | runtime OBJECT slot/index | **VERIFIED_EXE** |
| `+0x0A` | 1 | behavior/state-control | PARTIAL |
| `+0x0B` | 1 | state | VERIFIED_EXE |
| `+0x0C` | 1 | next_state | VERIFIED_EXE |
| `+0x0D` | 1 | o_id | VERIFIED_EXE |
| `+0x0E` | 1 | object/definition lookup result | PARTIAL |
| `+0x0F` | 1 | GUARD/object synchronization boolean | PARTIAL |
| `+0x10` | 1 | sentinel-backed target/sequence-related field | PARTIAL; initialized 0xFF |
| `+0x11..0x12` | 2 | unknown | TODO |
| `+0x13` | 1 | transition parameter | PARTIAL |
| `+0x14..0x15` | 2 | unknown | TODO |
| `+0x16` | 1 | transition/control flag | PARTIAL |
| `+0x17..0x19` | 3 | unknown | TODO |

## Capacity path independently verified

During object initialization, when object flag bit `0x08` indicates a guard, the executable compares the current GUARD count against literal **0x64 (100)** before creating the guard. The same branch references `MAXGUARD exceeded (%d)` and stores the current guard index into `OBJECT+0x07` before incrementing the count.

This independently confirms the 100-record capacity inferred from USER.SAV.

## Goals 2-5: next xrefs

The coordinate part of the chain is now solved:

`GUARD+0x08 -> OBJECT[index] -> OBJECT+0x10 X / +0x12 Y`.

Remaining high-value targets are:

1. trace writes to `OBJECT+0x10/+0x12` from GUARD state handlers -> **direction + movement speed**;
2. find subtraction/comparison that selects pain/death state -> **enemy HP + weapon damage routine**;
3. trace GUARD `+0x02/+0x06` updates in detection/attack states -> **reaction delay + attack interval**;
4. bind sound-play calls in those handlers -> **alert/attack/pain/death SND.DAT IDs**;
5. identify remaining GUARD bytes and OBJECT `+0x14..+0x1B` without guessing.

No HP, speed or damage number is promoted until direct executable evidence is found.
