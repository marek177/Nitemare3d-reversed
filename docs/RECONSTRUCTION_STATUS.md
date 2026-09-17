# Reconstruction status — v1.0

This repository is a clean-room-style reconstruction scaffold based on the supplied Windows 3.1 executable/data plus independently documented gameplay observations. It is not the original Gray Design Associates source tree.

## Current estimate (2026-09-17)

- Direct binary/algorithm reverse engineering of `NITE3W.EXE`: **about 63–65%** working estimate.
- Broader behavioral reconstruction using EXE + original data formats + walkthrough evidence + documentation: **about 85–86%** working estimate.

These percentages are engineering estimates, not byte-count coverage. The final 95–100% claim will be based on the function/range audit, not on a subjective subsystem average.

## Strongly understood

- Win16 NE structure, 10 segments and direct import-module inventory.
- WinG/DISPDIB display path.
- `CONFIG.SAV` 20-byte format and nearly all field semantics.
- `USER.SAV` physical save-slot layout: `0xD6E7` = 55,015 bytes.
- mutable 64x64x2 MAP image persisted in the save.
- MAP/IMG/OBJECTS/WALLS/DEMO structural formats, with remaining semantic edges explicitly tracked.
- player spawn IDs 1–4 and four initial orientations.
- world scale: 64 internal units/tile.
- player movement/collision core: 27-unit AABB half-extent, incremental major/minor stepping, wall/object property tables, dynamic-door passability and natural axis sliding.
- USE `0x0200`: rising-edge behavior, one-adjacent-cell targeting, door/key/card/panel/push dispatcher families.
- exact colored-key order Red/Green/Blue/Yellow and ID-card names Red/Yellow from executable pointer tables.
- `0x19..0x1C` colored-key special-wall family; this handler does not consume the key.
- combination-lock family `0x25..0x2C` identified; exact per-type code/state mapping remains partial.
- GUARD record core, GUARD->OBJECT linkage and fresh strength initialization to 255.
- player->enemy weapon damage matrix and difficulty transform substantially reconstructed.
- weapon ammo stores/consumption/pickups and scripted jam mechanism.
- pushable runtime table/update path.
- 320x200 8-bit target framebuffer, 304-wide 3-D viewport, Q10 trig/projection anchors.

## Current subsystem table

| Subsystem | Current |
|---|---:|
| Player collision / passability | ~85–90% |
| USE / interaction | ~80–85% |
| OBJECT 28-byte record | ~50–55% |
| GUARD record | ~78% |
| GUARD movement | ~35–40% |
| GUARD AI/state machine | ~55–60% |
| Enemy strength / damage receiver | ~95–100% |
| Weapon -> enemy damage | ~90–95% |
| Player health/damage/death | ~35% |
| Weapon cadence | ~40–50% |
| Enemy pain/death + SFX | ~55–70% |
| USER.SAV physical layout | ~95–100% |
| USER.SAV gameplay semantics | ~65–68% |
| Level/script dispatcher | ~45% |
| Debug/keyboard/CLI | ~60% |
| MIDI/music selection | ~40% |
| SND.DAT runtime/cache | ~60% |
| NITE3D.BSF | ~30–40% |
| Renderer/raycaster | ~45–50% |
| `NITE3W.EXE` overall direct RE | **~63–65%** |

See `docs/RUNTIME_RE_ROADMAP.md` for the fixed 14-step route to the final audit.

## New dedicated RE documents

- `docs/PLAYER_COLLISION_RE.md` — exact movement/collision stepping, AABB, property bits, door passability, Catacomb/Wolf comparison.
- `docs/USE_INTERACTION_RE.md` — exact USE edge trigger, adjacent-cell table, key/card/door/panel/push/special-wall dispatcher.
- `docs/COMBAT_DAMAGE_RE.md` — player-to-enemy damage producer/matrix.
- `docs/PLAYER_HEALTH_RE.md` — player health evidence/status.
- `docs/GUARD_AI_RE.md` — GUARD runtime state evidence.
- `docs/DEMO_FORMAT_RE.md` — demo record/playback and spawn/first-room forensics.

## Major unresolved areas

- finish OBJECT `+14..+1B` and complete OBJECT read/write xref map;
- GUARD movement speed/octant/collision and full AI transition graph;
- enemy->player damage and death/restart flow;
- weapon cadence/held fire/continuous-laser timing;
- exact pain/death/SND matrix and enemy class identities `0x0C..0x1F`;
- complete level/script opcode/event dispatcher;
- remaining USER.SAV semantic labels;
- keyboard/debug/CLI, MIDI selector and `NITE3D.BSF`;
- exact renderer traversal/clipping/texture/sprite/depth path;
- final byte/function classification of all executable code.

## Comparison rule

Catacomb Abyss is now the primary public source comparison for collision/movement/AI lineage, with Wolfenstein 3-D as the secondary comparison. Similarity is not treated as identity unless the original Nitemare executable demonstrates matching control flow/constants/data representation.

## Repository constraint

The public repository intentionally excludes original game binaries/assets, IDA databases, source MP4s and frame-evidence images.
