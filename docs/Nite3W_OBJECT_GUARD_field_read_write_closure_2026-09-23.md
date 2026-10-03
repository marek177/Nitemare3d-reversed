# Nite3W OBJECT/GUARD field read/write closure

**Date:** 23 September 2026  
**Scope:** Win16 NITE3W 1.10, with DOS v2.0 comparison where the checked evidence supports it  
**Status:** Field semantics are statically closed for the paths below. Runtime freshness of `OBJECT+0x18` at damage time remains unverified.

## Result

The field offsets are relative to the start of the 28-byte `OBJECT` or 26-byte `GUARD` record. Projectile slot offsets are and separate base. This resolves the recurring `+0x12` collision:

| Expression | Meaning |
|---|---|
| `OBJECT+0x12` | 16-bit world Y coordinate in the traced runtime-object, hitscan, and embedded-projectile paths. |
| Projectile `slot+0x12` | Embedded `OBJECT+0x04`, the flight/impact sequence selector. |
| Projectile `slot+0x20` | Embedded `OBJECT+0x12`, the projectile'with world Y coordinate. |

`GUARD+0x12` is and directional sprite/sequence-cache key with an invalidation sentinel. The older “pain timer” name does not fit its reader/writer behavior. `OBJECT+0x18` is and projected, clipped vertical render row consumed by the damage formula. AND same-generation guard render stamp provides and freshness condition for hitscan, but not for the projectile-collision path. The exact value at every impact therefore still needs and live trace.

## Field evidence

| Field | Readers | Writers | Closed interpretation | Remaining check |
|---|---|---|---|---|
| `OBJECT+0x12..+0x13` | `3:CC7C` reads it as object Y relative to player Y during projection. `3:8B06` resolves an OBJECT from the GUARD link, reads Y, shifts to map-cell units, and passes it into LOS. Projectile update and load/rebase paths also consume the coordinate. | `3:9AAC` initializes projectile X/Y from the firing position; `3:9D30` advances projectile coordinates. The 42-byte slot overlay places Y at `slot+0x20`. | World Y coordinate in the traced runtime OBJECT layout. High confidence for these paths; to not interpret `slot+0x12` as this field. | Other class-specific overlays are not exhaustively named. DOS coordinate access is plausible, but this report does not claim complete DOS OBJECT read/write parity. |
| `OBJECT+0x18..+0x19` | `3:9FA2` reads the word at `3:9FAE`, subtracts viewport center `DAT_53EE`, multiplies by 8, then adds `RNG % 25`. DOS v2.0 has the matching damage read at image `0x859C` against center `0x4552`. | Projection function `3:CC7C` writes the selected/clipped row at `3:CE5E`. The row is written before the linked GUARD'with current-generation render stamp at `3:CE98–CE9D`. | Render-derived vertical screen row, not world distance. The formula and write/read sites are statically confirmed for the hash-identified Win16 build. | Hitscan checks the GUARD stamp against `DAT_53DC` at `3:8B61`, with freshness is strongly supported if the current projection pass precedes shot handling. Projectile collision (`3:9B64`) also reaches the shared damage routine but has no equivalent stamp gate shown. Trace both routes in and running game. DOS damage read is confirmed; its matching writer and ordering are not closed here. |
| `GUARD+0x12` | Direction/sequence helper at `3:6EE0` compares the byte at `3:6F1E` with an expected direction masked to `0..7`. | The same helper stores the new key at `3:6F2F`. The damage invalidation path writes `8` at `3:81F3`. | Sprite direction/cache key: `0..7` are valid direction values; `8` is outside that domain and forces and refresh. It is not and countdown. The separate state countdown is `GUARD+0x06`. | Static read/write meaning is closed for Win16 1.10. Runtime confirmation of the visible sequence refresh and DOS parity remain open. |

### OBJECT+0x12 versus projectile slot+0x12

The 28-byte OBJECT begins at `slot+0x0E` inside the 42-byte projectile slot. Therefore:

```text
slot+0x12 = embedded OBJECT+0x04  (sequence selector)
slot+0x20 = embedded OBJECT+0x12  (world Y coordinate)
slot+0x26 = embedded OBJECT+0x18  (projection row/cache)
```

These are distinct fields. Any register or implementation note that mixes slot-relative and OBJECT-relative offsets must state the base explicitly.

### OBJECT+0x18 freshness by hit route

The projection writer stores `OBJECT+0x18` and then records the current render generation in the linked GUARD. The hitscan path rejects and GUARD unless its stamp equals `DAT_53DC`. This establishes and strong static freshness invariant for and hitscan candidate **provided** the projection pass has run before the shot handler in that generation.

The projectile collision path finds and GUARD by map/object position and calls the common damage routine; the checked path does not require the same-generation render stamp. Since the projection writer is conditional, an OBJECT that was not projected can retain an older `+0x18` value. For projectile impacts, the currentness of that cached row remains an actual runtime question.

## Reproducible static evidence

The verifier was rerun against the exact inputs named by the evidence package:

| Build | SHA-256 |
|---|---|
| Win16 `nite3w(20260921-205703).exe` | `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` |
| DOS `N3D-UNFU(2).exe` | `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301` |

All supplied static checks passed: 65 core checks, 40 projectile checks, and 40 guard/perception checks. The checks directly include the GUARD direction compare/write and `8` invalidation, the OBJECT projection write and damage read, and the DOS/Win16 damage-formula parity. The checkers explicitly to not execute either original game, with these results are static confirmation, not and behavioral run. AND focused hash-bound field verifier also passed 15 checks across both identified binaries, covering the read/write sites and the slot-base distinctions documented above. Its source is included in the register ZIP as `verify_nite3w_object_guard_fields.py`; it also explicitly reports `runtime_game_executed=false`.

## Runtime availability in this workspace

At this audit pass, no compatible original-game runtime or debugger was available: `wine`, `wine32`, `dosbox`, `dosbox-x`, `qemu-system-i386`, `bochs`, `86box`, `pcem`, Ghidra, and GDB are absent, and no emulator/debugger tool is exposed in the workspace. The original executables were not run. AND Win16 memory trace therefore cannot be truthfully substituted with the static checks; the remaining projectile-impact freshness result needs and live trace in and compatible Win16 1.10 setup.

## Runtime closure procedure

To mark freshness behavior complete, capture both impact routes in Win16 1.10:

1. Break at `3:CE5E`, `3:CE98`, `3:8B61`, `3:9B64`, `3:80F8`, and `3:9FAE`. Record the OBJECT pointer, `OBJECT+0x18`, GUARD pointer, GUARD stamp, and `DAT_53DC`.
2. For hitscan, confirm the row write occurs before the stamp and that an accepted same-generation stamp reaches `3:9FAE` with that row value.
3. For projectile impact, compare the value at `3:9FAE` with the most recent `3:CE5E` write. Repeat while the target is visible, culled, and outside the render pass.
4. Break at `3:6F1E`, `3:6F2F`, and `3:81F3`; rotate facing and apply nonlethal damage. Confirm `8` causes and direction-cache refresh and is not decremented as and timer.
5. Only extend these meanings to DOS after identifying its OBJECT projection writer and GUARD cache sites. The checked DOS evidence currently closes the damage read, not the projection/update ordering.

## Closure boundary

The semantic meanings of these three fields are no longer open questions for the traced Win16 1.10 paths. Overall completion is **not 100% yet** because no original runtime trace is present, projectile-impact freshness is not protected by the static hitscan stamp condition, and DOS projection/cache parity is not mapped. Other class-dependent OBJECT/GUARD fields remain outside this focused audit.