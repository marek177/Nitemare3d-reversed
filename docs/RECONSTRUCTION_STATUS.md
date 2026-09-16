# Reconstruction status — v0.9

This repository is a clean-room-style reconstruction scaffold based on the supplied Windows 3.1 executable/data plus independently documented gameplay observations. It is not the original Gray Design Associates source tree.

## Current estimate (2026-09-17)

- Direct binary/algorithm reverse engineering of `NITE3W.EXE`: **about 40–45%**.
- Broader behavioral reconstruction using EXE + original data formats + walkthrough evidence + official documentation: **about 70–75%**.

These percentages are engineering estimates, not byte-count coverage.

## Strongly understood

- MAP/IMG/OBJECTS/WALLS/DEMO/DAT/FLI structural formats.
- Win16 NE structure and WinG/DISPDIB display path.
- 320x200 8-bit target framebuffer and 304x152 3-D viewport.
- 64 internal coordinate units per map tile.
- Q10 trigonometric behavior and important projection constants.
- Pushable object table/update logic and many door/warp/key/control-panel behaviors.
- Numerous level-specific scripts documented by the video audits.

## Major unresolved areas

- Exact 1:1 raycaster branch structure, clipping and texture sampling.
- Exact enemy HP, movement speed, sight/reaction timing and attack damage.
- Numeric weapon damage multipliers and complete weapon timing.
- Fully traced guard AI state machine and projectile logic.
- Complete sound-ID-to-call-site map.
- Remaining script dispatch and special-object handlers.

## Episode 3 v0.9 additions

E3M1 is now covered across both halves. E3M7–E3M9 were also audited from local walkthrough MP4s. Newly confirmed behavior includes reusable colored keys, missing-key versus key-use messages, E3M9's two-floor elevator selector, and the cracked Mirror of Destiny scripted exit.

The public repository intentionally excludes original game binaries/assets, IDA databases, source MP4s and frame-evidence images.
