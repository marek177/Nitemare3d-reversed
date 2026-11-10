# Remote doors, wall USE and DOS cross-check — 2026-09-22

Evidence: Win16 `NITE3W.EXE` 1.10 disassembly/Ghidra export (`FUN_1010_84f4`, `FUN_1010_bfd8`, `FUN_1018_27de`, `FUN_1010_188a`, `FUN_1010_1a22`, `FUN_1018_21d8`, `FUN_1018_2146`). Some far-call parameter lists still need raw assembler verification.

## Remote door path

1. USE on wall class `0x03` resolves a class-`0x03` runtime object.
2. The object's byte `+1` selects a group/card index and writes `DAT_1048_40F8`.
3. The corresponding bit in ID-card mask `DAT_1048_4C29` gates entry to the menu.
4. Menu commands `0x1E` and `0x1F` iterate 22-byte door records at `0x9DD6`, filtering runtime object classes `0x3B/0x3C` and group byte `object+1`.
5. Command `0x1E` selects door states 1/3; `0x1F` selects 0/2. Both set `door+0x14=1` before the transition helper. The helper maps 1/3 → 2 and 0/2 → 3 and uses SFX `0x25/0x26`. The display names **open** and **close** are inferred from these transitions.
6. The command toggles bit `1 << group` in `DAT_1048_51A4`, even when no matching physical door changed. This bit must not be treated as an authoritative door-state array.

Normal USE returns early for `0x3B/0x3C`, and auto-close skips these classes. Card mask and key mask are distinct (`4C29` versus `4C28`).

Movement onto a tile with wall-property bit `0x40` instead invokes `FUN_1010_bfd8`, an episode/level script dispatcher for classes `0x47/0x48`. A universal `TRIGGER → CONTROL → remote door` chain is **not established**.

## Other confirmed dispatch boundaries

- Wall `0x09/0x0A`: advance zero-based level index by 1/2.
- Wall `0x0D–0x14`: paired WARP destinations; `0x15–0x18`: special portal; `0x19–0x1C`: four color-key gates; `0x1D–0x24`: floor-selection warp; `0x25–0x2C`: handler exists, named retail use not established.
- `WARP_S1` requires all four pentagram bits (`0x0F`) before transfer to `WARP_S2`; S2 displays text without a reverse transfer.
- Wall classes `0x04`, `0x05`, `0x06`: ammo refill; conditional health +20; conditional meter +20. The +20 branches test `<100` before adding, with no visible saturation in that routine. Recreating this literally could exceed 100; confirm downstream clamp before gameplay integration.
- USE checks key mask for door classes `0x33–0x38`, card mask for `0x39–0x3A`; `0x3B–0x3C` disallow direct manual opening.

## DOS independent findings

DOS v2.0 `1000:0212` builds 64 × 18-byte paired-wall records; `1000:03FE` builds 32 × 14-byte class-3 wall records. `1000:0598` synchronizes paired-wall state and SFX `0x25/0x26`; `1000:241E` dispatches completed animation class `0x2D` to a routine near `1000:04BE`, whose exact writes remain open. See the sibling DOS repository's `docs/DOS_RUNTIME_FINDINGS_2026-09-22.md`.

The Win16 runtime object/guard strides are **28/26 bytes**; older 80/98-byte figures were incorrect. Do not equate these runtime records with 28-byte on-disk definition entries merely because sizes coincide.

## Next verification

Correct the DOS Ghidra function boundaries near `1000:00A2` and `1000:04BE`; identify the map writes at explosion completion; locate the WALLS ID for Win16 wall class `0x03`; compare remote-door state transitions during actual gameplay.


## Win16 22-byte DoorRuntime layout closure — 2026-09-28

A full field/XREF pass over the Win16 1.10 array at `DS:9DD6` now accounts for every byte in the `0x16`-byte record.

| Offset | Size | Recovered meaning | Evidence |
|---:|---:|---|---|
| `+0x00` | 4 | far pointer to moving wall/VEC component A | built by `3:14A8`; used by motion/collision/SFX paths |
| `+0x04` | 4 | far pointer to moving wall/VEC component B | same |
| `+0x08` | 4 | far pointer to the owning 2-byte MAP cell | lookup key in `3:1296`; obstruction/auto-close checks |
| `+0x0C` | 2 | controller state | states 0..4 traced |
| `+0x0E` | 2 | auto-close countdown | 32 after completed motion; retry 4 while obstructed |
| `+0x10` | 2 | world-space controller/motion anchor X | AI nearest-door lookup and movement target logic |
| `+0x12` | 2 | world-space controller/motion anchor Y | AI nearest-door lookup and movement target logic |
| `+0x14` | 1 | sound/action latch | controls open/close SFX requests; written by manual/remote activation |
| `+0x15` | 1 | unused/padding in Win16 1.10 | no direct executable XREF |

The controller states are:

| State | Behavior |
|---:|---|
| 0 | open/passable; auto-close countdown active |
| 1 | closed |
| 2 | opening |
| 3 | closing |
| 4 | corpse hold-open / disabled door; passable and ignored by normal toggle/auto-close |

Movement is two internal world units per simulation update. Completion writes state 0 or 1 and countdown `0x20`. If an open doorway is occupied when the countdown expires, the retry timer becomes 4.

The sound latch is not just an unknown flag. Manual/remote activation sets it. Opening requests runtime SFX `0x25`; closing requests `0x26`. The close path clears the latch. If the door was opened and left to auto-close, the retained latch allows the later closing sound to be requested.

The final byte at `+0x15` has no individual XREF in the Win16 1.10 executable. It is nevertheless mechanically preserved when the entire DoorRuntime array is copied through USER.SAV. Treat it as runtime-unused/padding, not as a semantic field.

The whole array is exactly:

```text
64 records * 22 bytes = 0x580 bytes
```

which matches the raw save/load transfer size.

### Platform boundary

This layout is **Win16-specific**. DOS v2.0 uses a distinct 18-byte paired-wall record. Do not project the Win16 offsets onto DOS solely because the state machine is behaviorally related.
