# Nitemare3D-Reversed — reconstruction v0.9

**v0.9 update:** extended Episode 3 audit covers complete E3M1, E3M6 and E3M7–E3M9, including reusable colored keys, the two-floor E3M9 elevator selector, the cracked Mirror of Destiny exit, and E3M6 fire-hazard behavior. E3M3–E3M5 remain the outstanding full Episode-3 walkthrough audits.

Modern C++ reconstruction scaffold for the **Windows 3.1** version of Nitemare 3D.
The design goal is to preserve the original data formats and reconstructed game logic while replacing obsolete Windows 3.x display plumbing (`WING.DLL` and `DISPDIB.DLL`) with **SDL3**.

## AI assistance disclosure

This is an **AI-assisted reverse-engineering and reconstruction project**. A substantial part of the analysis, research, documentation, code generation, refactoring, and interpretation of reverse-engineered material has been produced with the assistance of **ChatGPT by OpenAI**, under the direction and review of **marek177**.

Git commit authorship therefore identifies the account that committed the files and should **not** be interpreted as meaning that every analysis, document, or line of code was written manually and independently by the repository owner. AI-generated or AI-assisted findings may contain errors, especially where original source code or symbols are unavailable, so important reverse-engineering conclusions should be independently verified against the original executable and game data.

## Reverse-engineering status

The project separates direct executable reverse engineering from behavior reconstructed from original data, walkthrough evidence and original documentation. See `docs/RECONSTRUCTION_STATUS.md`, `docs/EXE_FUNCTION_MAP.md`, `docs/SAVE_LIBRARIES_IDA_REPORT.md`, and the video-audit reports for evidence and confidence levels.

Well-understood areas include the Win16/WinG display path, 320x200 indexed framebuffer, 304x152 3-D viewport, map/archive formats, SND.DAT container and PCM format, CONFIG.SAV physical layout, USER.SAV physical block layout, many doors/warps/pushables and numerous level-specific scripts. Major unresolved areas are exact enemy HP/speed/reaction/damage, numeric weapon multipliers, a fully traced guard AI state machine, all hidden keyboard/debug paths and a 1:1 reconstruction of every raycaster branch.

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
./build/n3d_pushable_test
./build/n3d_menu_cheat_test
./build/n3d_hazard_test
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

The `nitemare3d` executable currently displays a top-down preview of the selected original 64x64 map using the original palette. That small viewer is deliberate: it validates the modern SDL path before the original 3D raycaster is transplanted.

## Original data

Original game assets are intentionally excluded from the public repository. Copy your own game files with:

```bash
python scripts/import_original_data.py /path/to/Nitemare3D
```

## Useful tools

```bash
python tools/ne_inspect.py data/original/NITE3W.EXE
python tools/n3d_save_inspect.py CONFIG.SAV USER.SAV
n3d_inspect data/original
```

## Video audit coverage

Episode 1 and Episode 2 walkthrough material has durable audit coverage. Episode 3 currently has durable coverage for **E3M1, E3M2, E3M6, E3M7, E3M8, E3M9 and E3M10/Ending**. The remaining full walkthrough audits are **E3M3, E3M4 and E3M5**.

E3M6 directly strengthens the fire-hazard model: small and medium fire are traversable damaging hazards while large fire is the lethal/impassable class documented by the original material. Exact numeric damage/timing remains unresolved and is not invented in the source. See `docs/VIDEO_AUDIT_E3M6.md` and `src/game/HazardSystem.hpp`.

## Next engineering targets

The highest-value remaining targets are the original guard AI/HP/damage paths, exact weapon damage/timing, the remaining raycaster branches, keyboard/debug command paths, MIDI level-selection table, registration/BSF checks, and the semantic fields inside USER.SAV runtime blocks.
