# GUARD AI reverse engineering

Date: 2026-09-17
Evidence: original NITE3W.EXE Win16 binary (230400 bytes), reconstructed USER.SAV writer/layout, and direct 16-bit disassembly of the GUARD routines.

## Fixed record and save-array anchors

The executable contains the diagnostics `Problem with guard: state=%d, next_state=%d, o_id=0x%x`, `Guard not in map`, `No seqdef defined for guard` and `MAXGUARD exceeded (%d)`.

GUARD iteration advances by **0x1A = 26 bytes**. USER.SAV stores **0x0A28 = 2600 bytes** at `0xB43B`; `0x0A28 / 0x1A = 100`, identifying a fixed persisted pool of **100 GUARD records**.

Evidence: **VERIFIED_EXE + VERIFIED_SAVE_LAYOUT**.

## Second-pass field recovery

The spawn/initialization routine computes `guard = GUARD_BASE + guard_index * 0x1A` and performs the following writes. Other GUARD loops use the same stride and fields.

| Offset | Width | Recovered role | Evidence/status |
|---:|---:|---|---|
| `+0x00` | 2 | sequence/definition-derived value; exact semantic still pending | VERIFIED access, semantic PARTIAL |
| `+0x02` | 4 | GUARD timestamp/time value | **VERIFIED_EXE**: zeroed on spawn; compared with global game tick |
| `+0x06` | 2 | state/countdown timing value | **VERIFIED_EXE**: initialized/assigned by transitions, including `1` and `0x70` |
| `+0x08` | 2 | runtime object slot/index | **VERIFIED_EXE**: multiplied by `0x1C` to address the corresponding object record |
| `+0x0A` | 1 | behavior/state-control byte | VERIFIED role, enum meaning pending |
| `+0x0B` | 1 | `state` | **VERIFIED_EXE** diagnostic |
| `+0x0C` | 1 | `next_state` | **VERIFIED_EXE** diagnostic |
| `+0x0D` | 1 | `o_id` | **VERIFIED_EXE** diagnostic |
| `+0x0E` | 1 | object/definition lookup result | VERIFIED_EXE; exact table semantic pending |
| `+0x0F` | 1 | derived GUARD/object synchronization boolean | VERIFIED_EXE role |
| `+0x10` | 1 | sentinel-backed target/sequence-related field | VERIFIED_EXE access; initialized to `0xFF`, exact meaning pending |
| `+0x11..0x12` | 2 | unknown | TODO |
| `+0x13` | 1 | transition parameter | VERIFIED_EXE access; observed explicit value `3` in a scripted transition |
| `+0x14..0x15` | 2 | unknown | TODO |
| `+0x16` | 1 | transition/control flag | VERIFIED_EXE access; explicitly set by transition code |
| `+0x17..0x19` | 3 | unknown | TODO |

This means **19 of the 26 byte positions are now structurally accounted for by direct executable accesses**, although several still have intentionally conservative names. Exact HP/speed/direction semantics are not being guessed into those fields.

## Key disassembly anchors

### Object linkage

Multiple GUARD loops perform the equivalent of:

```text
object_offset = guard[+0x08] * 0x1C
object = OBJECT_BASE + object_offset
```

The same object record is then read at offsets including `+0x10/+0x12`, which are shifted right by 6 in world/map calculations. Thus GUARD position is strongly linked through `guard.objectSlot` to the associated **28-byte object record**, rather than necessarily duplicating X/Y directly in the 26-byte GUARD record.

This is important: the original target list `X/Y -> HP -> direction...` should not assume X/Y live inside GUARD. Current EXE evidence points to **GUARD +0x08 -> OBJECT record -> object X/Y**.

### Timing

The GUARD loop compares the dword at `+0x02` against the game's global time/tick value. The word at `+0x06` is separately changed by state transitions. Therefore there are at least two distinct timing concepts in each guard: an absolute/relative tick-like dword and a state/countdown word.

### State transitions

Observed executable transitions include direct writes such as:

```text
state = 7
next_state = 2
transitionFlag = 1
```

and another scripted branch changes a guard to state `0x14`, stores a definition-derived next state, sets the timing word to `0x70`, and writes transition parameter `3`.

Numeric state names remain intentionally unresolved until each dispatch target is traced to behavior.

## Revised recovery targets

| Target | Status after second pass |
|---|---|
| GUARD stride/capacity/save location | VERIFIED |
| GUARD -> object linkage | **VERIFIED** (`+0x08`, object stride `0x1C`) |
| position X/Y | **PARTIAL**: obtained through associated object record; exact object offsets observed in movement/render calculations |
| state / next_state / o_id | VERIFIED |
| GUARD timestamp | **VERIFIED `+0x02` dword** |
| state/countdown timer | **VERIFIED `+0x06` word** |
| behavior/transition flags | PARTIAL (`+0x0A,+0x0F,+0x10,+0x13,+0x16`) |
| sequence/definition linkage | PARTIAL (`+0x00,+0x0E` and object definition tables) |
| HP | TODO: trace damage receiver/death transition |
| speed/direction | TODO: trace movement routine and object-coordinate delta generation |
| reaction delay | PARTIAL: likely represented through recovered timing/state machinery; exact use per state pending |
| attack interval | TODO: trace attack states and timestamp updates |
| enemy damage | TODO: trace player-damage call sites |
| alert/attack/pain/death SFX | TODO: bind state dispatch branches to SND.DAT calls |

## Consequence for Goals 2-5

The next binary pass should follow the object record referenced by `+0x08` and the state-dispatch routines rather than searching the GUARD record blindly for X/Y. The highest-value xrefs are now:

1. writes/subtractions that cause transition to death state -> recover **HP and weapon damage**;
2. object `X/Y` update routines reached from GUARD states -> recover **direction and movement speed**;
3. `+0x02/+0x06` writes in detection/attack states -> recover **reaction delay and attack interval**;
4. sound-play calls inside those same dispatch targets -> recover **alert/attack/pain/death SFX IDs**.

No numeric HP/damage/speed constant should be promoted to VERIFIED until those call sites are traced.
