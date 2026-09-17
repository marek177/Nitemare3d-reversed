# Nitemare-3D Runtime Reverse-Engineering Roadmap

Date: 2026-09-17

This file is the central status table for the next runtime-engine reverse-engineering phase. Percentages are engineering estimates, not byte-count coverage.

## Evidence labels

- **VERIFIED_EXE** — directly supported by `NITE3W.EXE` / IDA-level binary evidence.
- **VERIFIED_DATA** — directly supported by original game data/save formats.
- **BEHAVIORAL** — observed in gameplay/video evidence.
- **INFERRED** — strong reconstruction hypothesis, still requiring direct binary confirmation.
- **TODO** — not yet established.

## Central status table

| Subsystem | Current | Target after next phase | Main missing evidence |
|---|---:|---:|---|
| GUARD AI / state machine | ~45% | 90–95% | LOS, hearing, reaction, movement, attack, pain/death transitions, projectile dispatch |
| Enemy HP / speed / damage | ~25% | 90–100% | exact per-type constants/tables and damage call sites |
| Weapon damage / timing | ~30% | 90–100% | damage routine, multipliers, cooldown/fire timing, alternate fire/event branches |
| Enemy SFX mapping | ~65% | 90–100% | complete GUARD -> alert/attack/pain/death sound matrix |
| USER.SAV gameplay fields | ~60% | 85–95% | semantic labels for 94-byte global block and fixed runtime arrays |
| 1:1 raycaster | ~60% | 85–90% | complete branch graph, clipping, texture sampling and special-wall cases |
| NITE3W.EXE direct binary/algorithm RE | ~54% | ~68–72% | AI/combat, raycaster, save semantics, debug/keyboard and remaining scripts |

## Already established anchors

### Save/runtime state

- `USER.SAV` slot size is exactly `0xD6E7` = 55,015 bytes. **VERIFIED_EXE**
- Current mutable map image begins at save offset `0x35` and is `0x2000` = 8192 bytes (64x64 x 2 bytes/cell). **VERIFIED_EXE / VERIFIED_DATA**
- Compact gameplay/global state block is `USER.SAV+0x2035`, size `0x5E` = 94 bytes. Individual fields remain to be named. **VERIFIED_EXE**
- Large runtime arrays follow at `0x2093`, `0x8DF3`, `0xB43B`, `0xBE63`, etc. Their physical sizes are known; class/field semantics are still incomplete. **VERIFIED_EXE**
- The save/load path restores raw runtime blocks, rebuilds pointers and rebases timers. **VERIFIED_EXE**

### Renderer

- Original renderer is not a Wolf3D-style textbook grid DDA reconstruction. Existing RE evidence points to a custom vector/line-segment textured-column pipeline. **VERIFIED_EXE / INFERRED for remaining branch semantics**
- Known anchors include a 320-entry column-hit/far-pointer structure and a 320 x 16-bit depth buffer; full clipping/sampling semantics remain to be traced. **VERIFIED_EXE**
- Target framebuffer is 320x200 8-bit; 3-D viewport width is 304 in the recovered configuration/default path. **VERIFIED_EXE**

### Map/runtime behavior

- MAP levels are 64x64, two bytes per cell, with an 8192-byte level payload after the container header. **VERIFIED_DATA**
- `OBJECTS.1-3` and `WALLS.1-3` are editor-side definitions and must not be treated as runtime object tables. **VERIFIED_DATA / behavioral project constraint**
- E1M11 is a demo/internal map and is not part of the normal 10-level Episode 1 progression. **VERIFIED_DATA / BEHAVIORAL**

## Next extraction order

1. **GUARD AI + combat constants**
   - identify guard record stride/capacity and candidate fields;
   - trace spawn -> idle -> detect -> chase -> attack -> pain -> death;
   - recover exact HP, movement, reaction and attack/damage constants;
   - attach SFX IDs to each transition.

2. **1:1 raycaster**
   - complete ray/intersection branch graph;
   - establish near-plane and viewport clipping;
   - recover texture-column coordinate calculation;
   - document door/special-wall rendering;
   - verify sprite depth/occlusion behavior.

3. **USER.SAV runtime semantics**
   - correlate runtime globals/arrays with the save write/read call sites;
   - label player HP/ammo/weapons/inventory/coordinates/angle/timers;
   - identify guard/projectile/object record arrays;
   - document pointer fixups and timer rebasing.

4. **Keyboard/debug/command-line**
   - trace keyboard handler xrefs and all cheat/debug branches;
   - distinguish documented cheat flags from hidden developer hotkeys;
   - recover command-line edition/debug switches where present.

5. **MIDI selection + BSF/edition**
   - finish Episode/Level -> MIDI table and special branches;
   - trace `NITE3D.BSF`, edition/registration and integrity checks.

## Video audit status carried into this phase

Episode 3 walkthrough coverage is now substantially better than the earlier baseline: E3M1 is covered across both halves, E3M4-E3M6 have dedicated audits, and E3M7-E3M9 were subsequently audited. E3M10/ending behavior was also examined. Video observations are useful for state transitions and timings, but exact numeric HP/damage/speed values remain **INFERRED/TODO** until tied to executable evidence.

## Implementation rule

Do not encode guessed combat constants as final game logic. New reconstructed source should retain the evidence label in comments until a value is verified. Prefer structures that allow later replacement of inferred values without changing public interfaces.

### Planned source modules

- `src/game/GuardSystem.hpp/.cpp` — state machine and per-guard runtime state.
- `src/game/CombatSystem.hpp/.cpp` — weapon/enemy damage and timing.
- `src/game/RuntimeSaveState.hpp/.cpp` — semantic representation of recovered USER.SAV blocks.
- renderer additions should extend the existing `src/renderer` implementation rather than introduce a second incompatible renderer.

## Completion criterion for this phase

The phase is considered complete when a guard can be traced from original map/object spawn through detection, movement, attack, damage reception and death with every important transition linked to an EXE routine/constant or explicitly marked behavioral/inferred; and when the renderer's per-column intersection -> clipping -> texture sampling -> depth/occlusion path is documented sufficiently for a deterministic clean-room reimplementation.
