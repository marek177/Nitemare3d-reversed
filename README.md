# Nitemare3D-Reversed — reconstruction v0.78

Nitemare3D-Reversed is an AI-assisted reverse-engineering research project and work-in-progress C++/SDL3 reconstruction of **Nitemare 3D (Nitemare-3D)**, covering the original **DOS and Windows 3.1 (Win16)** versions. It documents game data formats, rendering, gameplay logic and executable analysis, with reconstructed components and validation tools.

**Project status:** full original-versus-reconstruction gameplay and pixel-perfect parity are **not verified**. The active 3-D renderer remains a diagnostic DDA preview; recovered original rendering components have bounded verification described in the research reports. Original game assets are excluded; use your own game files.

For a starting point, see the [research consolidation](docs/RE_CONSOLIDATION_20261022_24_SK.md), [implementation acceptance matrix](docs/RE_IMPLEMENTATION_ACCEPTANCE_20261024_SK.md), [build instructions](#build) and [original data setup](#original-data). The latest update is below; the complete update history is in [updates.md](updates.md).

## Latest update

**22–24 Oct 2026 research consolidation:** [DOS/Win16 evidence and implementation map](docs/RE_CONSOLIDATION_20261022_24_SK.md) and [P0 implementation acceptance matrix](docs/RE_IMPLEMENTATION_ACCEPTANCE_20261024_SK.md). This is an evidence-bounded integration; no new original-vs-remake full-game parity is claimed.

[All previous updates → updates.md](updates.md)

Modern C++ reconstruction scaffold for the **Windows 3.1** version of Nitemare 3D.
The design goal is to preserve the original data formats and reconstructed game logic while replacing obsolete Windows 3.x display plumbing (`WING.DLL` and `DISPDIB.DLL`) with **SDL3**.

## AI assistance disclosure

This is an **AI-assisted reverse-engineering and reconstruction project**. A substantial part of the analysis, research, documentation, code generation, refactoring, and interpretation of reverse-engineered material has been produced with the assistance of **ChatGPT by OpenAI**, under the direction and review of **marek177**.

Git commit authorship therefore identifies the account that committed the files and should **not** be interpreted as meaning that every analysis, document, or line of code was written manually and independently by the repository owner. AI-generated or AI-assisted findings may contain errors, especially where original source code or symbols are unavailable, so important reverse-engineering conclusions should be independently verified against the original executable and game data.

## Reverse-engineering status

Start with the consolidation and newest delta:

- [`docs/PROJECT_FINDINGS_DELTA_2026-09-25.md`](docs/PROJECT_FINDINGS_DELTA_2026-09-25.md) — HUD/automap/menu, renderer globals, GUARD corrections, IMG/UIF HUD bank, MFC CDC anchors and runtime safety fixes
- [`docs/ALL_THREADS_CONSOLIDATION_2026-09-22.md`](docs/ALL_THREADS_CONSOLIDATION_2026-09-22.md)
- [`docs/PROJECT_FINDINGS_DELTA_2026-09-23.md`](docs/PROJECT_FINDINGS_DELTA_2026-09-23.md) — consolidated findings from all current audits
- [`analysis/nite3w_core_function_map_2026-09-23.md`](analysis/nite3w_core_function_map_2026-09-23.md) — DOS/Win16 core-function coverage map
- [`analysis/nite3w_projectile_pool_2026-09-23.md`](analysis/nite3w_projectile_pool_2026-09-23.md) — projectile record, collision, save and render details
- [`analysis/nite3w_img_seqdef_2026-09-23.md`](analysis/nite3w_img_seqdef_2026-09-23.md) — original IMG directory and sequence-bank loading, with the low-bank overlap still unresolved
- [`analysis/nite3w_guard_reaction_2026-09-23.md`](analysis/nite3w_guard_reaction_2026-09-23.md) — Win16 guard state 13 movement and state 15 hit-reaction transitions, cross-checked in 1.8
- [`docs/PROJECT_FINDINGS_DELTA_2026-09-22.md`](docs/PROJECT_FINDINGS_DELTA_2026-09-22.md) — previous cross-session corrections
- [`docs/UNKNOWN_SYSTEMS_AUDIT_2026-09-22.md`](docs/UNKNOWN_SYSTEMS_AUDIT_2026-09-22.md) — consolidated unknowns, priorities and evidence boundaries

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
- Dracula `0x11 -> 0x14` two-phase transform with HP reset;
- GUARD25/class `0x20` constrained as an unresolved/cut/fallback class rather than a known enemy;
- SND.DAT directory/PCM format, MIDI inventory;
- CONFIG.SAV physical size and USER.SAV block layout, including the 8-slot/42-byte projectile pool and wake cache;
- many doors/warps/pushables and numerous level-specific scripts.

Renderer work is moving from recovered facts into tested primitives: owner-conflict predicates, texture-U correction, span interpolation, and the linear fixed-point wall-column loop are implemented. The full scene path still needs integration and pixel comparison. Other open work includes wall-animation/resource mapping, sprite and palette details, door/panel/control records, GUARD states 02–14 and attack timing, enemy-projectile identity/behavior, enemy-to-player class binding, GUARD25, Dracula's resource/sound/corpse chain, automap byte values, BSF integrity, and remaining save/resource fields.

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

See the [renderer audit](analysis/nite3w_renderer.md) and its [2026-09-23 raw-assembly update](analysis/nite3w_renderer_2026-09-23.md). The runtime `Raycaster.cpp` remains a provisional grid-DDA viewer; it has not yet been replaced with the recovered vector/span scene renderer.

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
./build/n3d_projectile_runtime_test
./build/n3d_win16_wall_raster_core_test
./build/n3d_demo_file_test
./build/n3d_guard_facts_test
./build/n3d_v013_recovered_facts_test
./build/n3d_v014_analysis_test
./build/n3d_v015_sprite_facts_test
./build/n3d_v016_coverage_test
./build/n3d_v017_runtime_integration_test
./build/n3d_v018_evidence_test
./build/n3d_v019_runtime_primitives_test
./build/n3d_v020_verification_harness_test
./build/n3d_v021_subsystem_evidence_test
./build/n3d_v022_version_evidence_registry_test
./build/n3d_v023_cross_build_symbol_map_test
./build/n3d_v024_guard_state_graph_test
./build/n3d_v025_guard_writer_graph_test
./build/n3d_v026_guard_rng_coupling_test
./build/n3d_v027_projectile_lifecycle_test
./build/n3d_v029_scheduler_evidence_test
./build/n3d_v030_trace_closure_test
./build/n3d_v032_static_closure_test
./build/n3d_v033_push_scheduler_test
./build/n3d_v034_object_animation_evidence_test
./build/n3d_v035_rng_census_test
./build/n3d_v036_protected_hit_ordering_test
./build/n3d_v037_scheduler_catchup_test
./build/n3d_v038_three_day_findings_test
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

## Reverse-engineering toolchain

The v0.14 toolchain and analysis methodology are documented in [`docs/TOOLS_USED_V014.md`](docs/TOOLS_USED_V014.md). Not every listed tool is implied to have been used for every individual finding; executable/data evidence remains authoritative.

## Useful project-local tools

```bash
python tools/ne_inspect.py data/original/NITE3W.EXE
python tools/ne_renderer_audit.py data/original/NITE3W.EXE xrefs 'internal 3:D78C'
python tools/n3d_save_inspect.py CONFIG.SAV USER.SAV
n3d_inspect data/original
```

## Video audit coverage

Episode 1 and Episode 2 walkthrough material has durable audit coverage. Episode 3 has dedicated repository reports for E3M3, E3M4, E3M5, E3M6 and extended/finale material; where source videos contain cuts, the reports retain those limitations rather than claiming false 100% frame coverage.

E3M6 confirms the passability distinction: small/medium fire is traversable and large fire is impassable/lethal per original material. The Win16 audit now maps fire object IDs 0x3B/0x3C/0x3D to large/medium/small and confirms damage values of 100/10/2 HP per simulation update. The calibrated interval and damage-per-second remain open.

## Next engineering targets

1. Complete `wall ID/class -> flags -> handler -> renderer class` mapping.
2. Decode animated-wall sequence timing and `FUN_1010_65A6`.
3. Complete door/panel/control record/state semantics.
4. Finish GUARD state 02–14 naming plus movement/attack timing.
5. Bind enemy-to-player class transforms to visible enemies/projectiles.
6. Resolve GUARD25/class `0x20` reachability and resource identity.
7. Trace the complete Dracula `0x11 -> 0x14` sequence/sound/corpse chain.
8. Resolve the 4096-byte per-cell runtime state block and `OBJECT+14/+16/+18` semantics.
9. Integrate the recovered Win16 camera/vector/span pipeline and sprite/resource ordering into the runtime; validate it against deterministic original frames.
10. Finish wall-animation and special-resource mappings, DOS/VGA backend comparisons, BSF integrity/version-diff reconstruction, SFX/MIDI/UIF/ENDING.FLI edge cases and unresolved USER.SAV blocks.
