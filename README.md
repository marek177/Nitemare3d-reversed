# Nitemare3D-Reversed — reconstruction v0.9

**v0.9 update:** extended Episode 3 audit covers complete E3M1 plus E3M7–E3M9, including reusable colored keys, the two-floor E3M9 elevator selector and the cracked Mirror of Destiny exit.

Modern C++ reconstruction scaffold for the **Windows 3.1** version of Nitemare 3D.
The design goal is to preserve the original data formats and reconstructed game
logic while replacing obsolete Windows 3.x display plumbing (`WING.DLL` and
`DISPDIB.DLL`) with **SDL3**.

Version **0.7** retains the reconstructed menu/Instructions/cheat work and adds durable walkthrough audits through Episode 2 level 6, including elevator, stair-warp, container, pushable, locked-door and transportation-chamber evidence. This is **not yet a complete game**. The first build is intentionally focused on
verified file formats, executable archaeology, and a runnable SDL presentation
layer so subsequent raycaster/gameplay work has a trustworthy base.


## Reverse-engineering status

Current estimate (2026-09-17): about **40–45% of `NITE3W.EXE` has been directly reverse-engineered at the binary/algorithm level**, while the broader behavior of the game is approximately **70–75% reconstructed** when original data formats, walkthrough evidence and official documentation are included.

Well-understood areas include the Win16/WinG display path, 320x200 indexed framebuffer, 304x152 3-D viewport, map/archive formats, core projection constants, many doors/warps/pushables and numerous level-specific scripts. Major unresolved areas are exact enemy HP/speed/reaction/damage, numeric weapon multipliers, a fully traced guard AI state machine and a 1:1 reconstruction of every raycaster branch.

See `docs/RECONSTRUCTION_STATUS.md`, `docs/EXE_FUNCTION_MAP.md` and the video-audit reports for evidence and confidence levels.

## Current runtime architecture

```text
original MAP / IMG / GAME.PAL / definitions
                 |
                 v
      reconstructed C++ loaders
                 |
                 v
      8-bit indexed framebuffer
                 |
                 v
        palette -> ARGB8888
                 |
                 v
               SDL3
```

The original `WING.DLL` and `DISPDIB.DLL` are not loaded.

## Build

### Inspector only (no SDL dependency)

```bash
cmake -S . -B build -DN3D_ENABLE_SDL3=OFF
cmake --build build
./build/n3d_inspect data/original
```

### Windows 11 + SDL3

With SDL3 installed through vcpkg:

```powershell
vcpkg install sdl3:x64-windows
cmake -S . -B build `
  -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake
cmake --build build --config Release
build\Release\n3d_inspect.exe data\original
build\Release\nitemare3d.exe --data data\original --episode 1 --level 1
```

Or configure with `-DN3D_FETCH_SDL3=ON` if you want CMake to fetch SDL3.

The `nitemare3d` executable currently displays a top-down preview of the selected
original 64x64 map using the original palette. That small viewer is deliberate: it
validates the modern SDL path before the original 3D raycaster is transplanted.

## Original data

For this working bundle the supplied original files may be present under
`data/original`. They are ignored by git. For a clean/public repository, copy your
own game files with:

```bash
python scripts/import_original_data.py /path/to/Nitemare3D
```

## Useful tools

```bash
python tools/ne_inspect.py data/original/NITE3W.EXE
n3d_inspect data/original
```

See `docs/FORMAT_NOTES.md`, `docs/RECONSTRUCTION_STATUS.md`, and `docs/MENU_INSTRUCTIONS_CHEATS.md`.

## Next engineering target

The next major module should be the original raycaster: identify the NITE3W.EXE
functions that consume MAP wall IDs and IMG frame/sequence data, document their
segment:offset addresses, then port their fixed-point math and wall-column loop
without changing behavior.


## v0.3 menu / Instructions / cheats

The uploaded reference capture was converted into a persistent audit under
`docs/MENU_INSTRUCTIONS_CHEATS.md` and structured data under
`analysis/menu_instructions_cheats.json`. Evidence contact sheets and source MP4s are intentionally kept out of the public repository.

`Cheats...` remains visible for the Episode-1 demo/shareware edition, but the
original executable's complete-trilogy check rejects it, clears the four cheat
flags, and shows the registration message. The reconstructed `CheatSystem`
preserves that gate.


## v0.4 Episode 1 video audit

Added durable E1M3-E1M10 walkthrough audit and machine-readable level-mechanic manifests. Highlights include E1M6 explodable-wall behavior, E1M7 global power failure/fuse-box restoration, E1M8 WARP_7 three-choice stair/warp UI, E1M9 080993 safe/yellow-key and radio/dancing-guard action system, and E1M10 scripted episode finale.

## v0.5 E1M6 completion + Episode 2 audit

E1M6 is now covered by both walkthrough halves. Added E2M1-E2M6 video/MAP audit. Video-confirmed additions include the `Floor 1 / Floor 2` elevator selector, `Climb up / Climb down / Cancel` stair-warp UI, persistent trunk open states with contained Pentagram pickups, Transportation Chamber level exits, and additional destructible-wall behavior. MAP manifests record Episode 2 locked-door variants, WARP_E/WARP_1/2/5/7/8 networks, PUSH boxes/tombstones and ID-card placements. E2M5 is now complete: part 2 confirms the WARP_5 stair selector, Transportation Chamber -> LEVEL_UP transition, and the Level 5 completion statistics.


## v0.6 E2M5 completion

Added the missing E2M5 part 2 walkthrough audit. The new part 1 upload was SHA-256-identical to the previous source. Part 2 directly confirms the WARP_5 `Climb up / Climb down / Cancel` selector, the Transportation Chamber Door 1 -> `LEVEL_UP` sequence with green transition, and final Level 5 statistics (22 enemies remaining, 1 panel not found, score 16850). The video still does not show an explicit ID-card-use message at the chamber, so that requirement remains separated as MAP/OBJECTS evidence.


## v0.7 E2M7-E2M10 completion

Added durable walkthrough/MAP audit through the end of Episode 2. New directly video-confirmed behavior includes the E2M7 four-floor `WARP_E1` elevator selector (`Floor 1` through `Floor 4`), the E2M8/E2M9/E2M10 five-option remote-control terminal (`Open remote doors`, `Close remote doors`, `Enable remote cannons`, `Disable remote cannons`, `Cancel`), and the E2M10 scripted plasma-core finale. E2M10 has no `LEVEL_UP` cell; completion follows the plasma-core destruction sequence and Episode 2 ending message. See `docs/VIDEO_AUDIT_E2M7_E2M10.md` and `analysis/video_audit_e2m7_e2m10.json`.
## v0.9 Episode 3 extended audit

This revision adds full video audit material for E3M1 (part 1 combined with the previously audited part 2), E3M7, E3M8 and E3M9. Important newly confirmed behavior includes persistent/reusable colored keys, missing-key vs. key-use messages, E3M9's two-floor elevator selector, the cracked Mirror of Destiny scripted exit, and completion statistics for E3M7–E3M9. See `docs/VIDEO_AUDIT_E3_EXTENDED.md` and `analysis/video_audit_e3_extended.json`.
