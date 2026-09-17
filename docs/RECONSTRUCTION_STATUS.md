# Reconstruction status — v1.0

This repository is a clean-room-style reconstruction scaffold based on the supplied Windows 3.1 executable/data plus independently documented gameplay observations. It is not the original Gray Design Associates source tree.

## Current estimate (2026-09-17)

- Direct binary/algorithm reverse engineering of `NITE3W.EXE`: **about 53–55%**; use **~54%** as the working baseline.
- Broader behavioral reconstruction using EXE + original data formats + walkthrough evidence + official documentation: **about 81–83%**; use **~82%** as the working baseline.

These percentages are engineering estimates, not byte-count coverage.

## Strongly understood

- `SND.DAT` container and PCM SFX technical format.
- MIDI technical format and 15-track inventory.
- SFX offsets, sizes and durations.
- MAP/IMG/OBJECTS/WALLS/DEMO structural formats, with only edge/reserved semantics remaining.
- Win16 NE structure and direct import-module inventory.
- WinG/DISPDIB display path and the six WinG functions used by the game plus `DISPLAYDIB` ordinal 1.
- `CONFIG.SAV` physical 20-byte format and nearly all field semantics.
- `USER.SAV` physical save-slot layout: exactly `0xD6E7` = 55,015 bytes per slot.
- Mutable 64x64 map image persisted inside `USER.SAV`.
- 320x200 8-bit target framebuffer and 304-wide 3-D viewport.
- 64 internal coordinate units per map tile.
- Q10 trigonometric behavior and important projection constants.
- Pushable object table/update logic and many door/warp/key/control-panel behaviors.
- Numerous level-specific scripts documented by the video audits.

## Central next-phase targets

| Subsystem | Current | Target |
|---|---:|---:|
| GUARD AI/state machine | ~45% | 90–95% |
| Enemy HP/speed/damage | ~25% | 90–100% |
| Weapon damage/timing | ~30% | 90–100% |
| Enemy SFX mapping | ~65% | 90–100% |
| USER.SAV gameplay fields | ~60% | 85–95% |
| 1:1 raycaster | ~60% | 85–90% |
| `NITE3W.EXE` overall | ~54% | ~68–72% |

See `docs/RUNTIME_RE_ROADMAP.md` for evidence labels, recovered anchors and extraction order.

## Major unresolved areas

- Fully traced GUARD AI state machine: LOS, hearing, reaction, movement, attack, pain/death transitions and projectile logic.
- Exact enemy HP, movement speed, reaction timing and attack damage.
- Numeric weapon damage multipliers and complete weapon timing.
- Exact 1:1 raycaster branch structure, clipping, texture sampling and special-wall cases.
- Semantic labeling of the 94-byte USER.SAV gameplay/global block and the large fixed runtime arrays.
- Complete sound-ID-to-call-site / GUARD event matrix.
- Remaining script dispatch and special-object handlers.
- Complete keyboard/debug/command-line handler.
- Full Episode/Level -> MIDI selection table and special music branches.
- `NITE3D.BSF` registration/edition/integrity algorithm.

## Episode 3 video-audit additions

E3M1 is covered across both halves. E3M4-E3M6 have dedicated audits, and E3M7-E3M9 were subsequently audited from local walkthrough material. E3M10/ending behavior was also examined. Confirmed behavioral findings include reusable colored keys, missing-key versus key-use messages, E3M9's two-floor elevator selector, and the cracked Mirror of Destiny scripted exit.

Video evidence is treated as behavioral evidence. Exact numeric combat constants are not promoted to verified values until tied to executable/data evidence.

The public repository intentionally excludes original game binaries/assets, IDA databases, source MP4s and frame-evidence images.
