# Nitemare3D-Reversed — reconstruction v0.10

**v0.10 update:** cross-thread/session findings through 2026-09-22 are consolidated in [`docs/ALL_THREADS_CONSOLIDATION_2026-09-22.md`](docs/ALL_THREADS_CONSOLIDATION_2026-09-22.md). The newest pass resolves MAP→VEC construction, the four 333-entry VECLIST indexes, the 28-byte VEC layout anchors, the 320-column owner table, 20-byte wall spans, 18-byte projected-sprite queue, viewport/projection details, GUARD score values and the 22-state dispatcher. It also records corrections to older 80-byte OBJECT / 98-byte GUARD / 52-byte render-record guesses.

Modern C++ reconstruction scaffold for the **Windows 3.1** version of Nitemare 3D.
The design goal is to preserve the original data formats and reconstructed game logic while replacing obsolete Windows 3.x display plumbing (`WING.DLL` and `DISPDIB.DLL`) with **SDL3**.

## AI assistance disclosure

This is an **AI-assisted reverse-engineering and reconstruction project**. A substantial part of the analysis, research, documentation, code generation, refactoring, and interpretation of reverse-engineered material has been produced with the assistance of **ChatGPT by OpenAI**, under the direction and review of **marek177**.

Git commit authorship therefore identifies the account that committed the files and should **not** be interpreted as meaning that every analysis, document, or line of code was written manually and independently by the repository owner. AI-generated or AI-assisted findings may contain errors, especially where original source code or symbols are unavailable, so important reverse-engineering conclusions should be independently verified against the original executable and game data.

## Reverse-engineering status

Start with the canonical consolidation:

- [`docs/ALL_THREADS_CONSOLIDATION_2026-09-22.md`](docs/ALL_THREADS_CONSOLIDATION_2026-09-22.md)

Then use the subsystem reports for instruction-level evidence:

- [`analysis/nite3w_renderer.md`](analysis/nite3w_renderer.md)
- [`docs/GUARD_AI_RE.md`](docs/GUARD_AI_RE.md)
- [`docs/COMBAT_DAMAGE_RE.md`](docs/COMBAT_DAMAGE_RE.md)
- [`docs/PLAYER_HEALTH_RE.md`](docs/PLAYER_HEALTH_RE.md)
- [`docs/PLAYER_COLLISION_RE.md`](docs/PLAYER_COLLISION_RE.md)
- [`docs/USE_INTERACTION_RE.md`](docs/USE_INTERACTION_RE.md)
- [`docs/SPECIAL_WALL_USE_RE.md`](docs/SPECIAL_WALL_USE_RE.md)
- [`docs/SAVE_LIBRARIES_IDA_REPORT.md`](docs/SAVE_LIBRARIES_IDA_REPORT.md)
- [`docs/RE_AUDIT_CHEATS_AUDIO.md`](docs/RE_AUDIT_CHEATS_AUDIO.md)

Well-understood areas now include:

- Win16/WinG platform path and 320×200 indexed framebuffer;
- normal 304×152 3-D viewport;
- MAP→boundary-vector construction;
- 1000×28-byte VEC pool;
- four orientation-specific 333-entry VECLIST pointer indexes;
- per-column owner table and wall-span coalescing;
- wall and sprite raster stages plus the 100-entry projected-sprite queue;
- MAP/archive geometry and major runtime capacities;
- OBJECT 28-byte and GUARD 26-byte record sizes;
- player collision/USE/pushable mechanics;
- player health and both directions of difficulty scaling;
- player→GUARD weapon/class damage matrix;
- GUARD score switch and 22-state dispatcher skeleton;
- SND.DAT directory/PCM format, MIDI inventory;
- CONFIG.SAV physical size and USER.SAV block layout;
- many doors/warps/pushables and numerous level-specific scripts.

The most important remaining work is no longer the basic renderer architecture. It is the exact owner-conflict geometry, special-wall/texture-U paths, wall animation timing, complete door/panel/control records, semantic names for GUARD states 02–14, guard movement/attack timing, projectile behavior, remaining enemy->player class binding, BSF integrity algorithm, and unresolved save/resource fields.

## Renderer architecture

The renderer audit corrects an important early assumption: NITE3W does **not** use Wolfenstein 3-D's one-grid-ray-per-screen-column DDA.

The recovered path is:

```text
64x64 MAP
  -> exposed boundary extraction + merging
  -> VEC[1000] (28 B each)
  -> four VECLIST[333] far-pointer indexes
  -> project/near-clip candidate vectors
  -> 320-entry wall-owner table
  -> <=50 visible wall spans (20 B each)
  -> textured wall columns + per-column wall occlusion
  -> <=100 projected sprite commands (18 B each)
  -> 320x200 8-bit framebuffer
```

See the [renderer audit](analysis/nite3w_renderer.md) for instruction-level evidence and the remaining exact-special-case TODOs.

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

The original `WING.DLL` and `DISPDIB.DLL` are not loaded by the reconstruction.

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

The `nitemare3d` executable currently displays a top-down preview of the selected original 64x64 map using the original palette. That small viewer is deliberate: it validates the modern SDL path before the original 3-D renderer is transplanted.

## Original data

Original game assets are intentionally excluded from the public repository. Copy your own game files with:

```bash
python scripts/import_original_data.py /path/to/Nitemare3D
```

## Useful tools

```bash
python tools/ne_inspect.py data/original/NITE3W.EXE
python tools/ne_renderer_audit.py data/original/NITE3W.EXE xrefs 'internal 3:D78C'
python tools/n3d_save_inspect.py CONFIG.SAV USER.SAV
n3d_inspect data/original
```

## Video audit coverage

Episode 1 and Episode 2 walkthrough material has durable audit coverage. Episode 3 has dedicated repository reports for E3M3, E3M4, E3M5, E3M6 and extended/finale material; where source videos contain cuts, the reports retain those limitations rather than claiming false 100% frame coverage.

E3M6 strengthens the fire-hazard model: small and medium fire are traversable damaging hazards while large fire is the lethal/impassable class documented by original material. Exact numeric damage/timing remains unresolved and is not invented in the source.

## Next engineering targets

1. Complete `wall ID/class -> flags -> handler -> renderer class` mapping.
2. Decode animated-wall sequence timing and `FUN_1010_65A6`.
3. Complete door/panel/control record/state semantics.
4. Finish GUARD state 02–14 naming plus movement/attack timing.
5. Bind enemy-to-player class transforms to visible enemies/projectiles.
6. Translate the exact owner-conflict rule in `FUN_1018_3564`.
7. Translate all `FUN_1010_6422` texture-U/special-wall cases.
8. Audit global `0x7E60` and remaining VEC animation/resource fields.
9. Finish BSF integrity/version-diff reconstruction.
10. Finish SFX/MIDI/UIF/ENDING.FLI semantic edge cases and unresolved USER.SAV blocks.
