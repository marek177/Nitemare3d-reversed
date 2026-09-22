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
