# Nitemare-3D Runtime Reverse-Engineering Roadmap

Date: 2026-09-17

This file is the central roadmap toward a source-level reconstruction of `NITE3W.EXE`. Percentages below are engineering estimates, not byte-count coverage. The final percentage will be replaced by the function/range audit in step 14.

## Evidence labels

- **VERIFIED_EXE** — directly supported by `NITE3W.EXE` / IDA-level binary evidence.
- **VERIFIED_DATA** — directly supported by original game data/save formats.
- **VERIFIED_SAVE_LAYOUT** — exact save-file physical layout.
- **BEHAVIORAL** — observed in original gameplay/video.
- **INFERRED** — strong reconstruction hypothesis requiring more binary confirmation.
- **PARTIAL** — important behavior is known but not all subcases/labels are closed.
- **TODO** — not yet established.

## Current working status

| Subsystem | Current | Important remaining work |
|---|---:|---|
| Player collision / passability | **~85–90%** | residual wall-property meanings, door state names, side effects, trajectory regression |
| USE / interaction `0x0200` | **~80–85%** | remaining special-wall handler names, combination subtypes, special objects |
| OBJECT 28-byte runtime record | ~50–55% | especially `+14..+1B` and complete read/write xrefs |
| GUARD runtime record | ~78% | residual control/transition bytes |
| GUARD movement | ~35–40% | exact speed, octant->delta, collision/fallback |
| GUARD AI / state machine | ~55–60% | complete transition graph, attack/projectile/reaction logic |
| Enemy strength / damage receiver | ~95–100% | mostly naming/integration; fresh GUARD strength 255 is verified |
| Weapon -> enemy damage | ~90–95% | integrate remaining special branches |
| Player damage / death | ~35% | enemy->player producer, difficulty, death/restart flow |
| Weapon cadence | ~40–50% | timing/held-fire/continuous laser |
| Enemy pain/death + SFX | ~55–70% | exact class/state/SND matrix |
| USER.SAV physical layout | ~95–100% | physical record essentially solved |
| USER.SAV gameplay semantics | ~65–68% | remaining runtime arrays/global block meanings |
| Level/script engine | ~45% | complete event/opcode dispatcher |
| Keyboard/debug/CLI | ~60% | remaining developer keys/switches |
| MIDI/music selection | ~40% | exact selectors and demo special path |
| SND.DAT runtime/cache | ~60% | cache/runtime call-site semantics |
| NITE3D.BSF | ~30–40% | registration/edition/integrity algorithm |
| Renderer/raycaster | ~45–50% | traversal, clipping, texture columns, sprites/depth |
| WinG/display backend | ~70% | mostly integration/detail |
| `NITE3W.EXE` direct algorithm RE | **~63–65% working estimate** | steps 3–14 below |

The headline EXE number remains deliberately conservative. It will not be called 95–100% until step 14 classifies the executable code space by bytes/functions.

## Newly closed anchors: player collision

Detailed evidence is in `docs/PLAYER_COLLISION_RE.md`.

- movement/collision core: `seg3:8604`;
- post-move commit: `seg3:8A20`;
- player AABB half-extent: **27 world units**;
- one tile: **64 world units**;
- movement uses one-unit Bresenham-like major/minor stepping;
- axis components are tested separately, naturally producing wall sliding;
- wall properties are precomputed at `0x7E94[wallByte]`;
- object properties are precomputed at `0x7F94[objectByte]`;
- wall bit `0x04` hard-blocks, wall bit `0x08` enters dynamic-door passability, wall bit `0x40` invokes a script-touch hook;
- object bit `0x02` blocks; object bit `0x04` invokes touch/pickup handling;
- door runtime table: `0x9DD6`, stride 22, maximum 64.

These are **VERIFIED_EXE**.

The collision architecture is structurally closer to Catacomb Abyss's separate-axis/special-touch design than to Wolf3D's full-vector `ClipMove` fallback, but Nitemare's exact one-unit stepping/property tables are different. This is a comparison, not a source-copy claim.

## Newly closed anchors: USE / interaction

Detailed evidence is in `docs/USE_INTERACTION_RE.md`.

- `inputMask 0x0200` is rising-edge USE/ACTION;
- previous-state latch: `0x012C`;
- dispatcher: `seg3:1A22`;
- USE selects exactly **one adjacent cardinal cell**, quantized from the 8-way octant;
- exact cell-delta table: `[-64,+1,+1,+64,+64,-1,-1,-64]`;
- dynamic doors, key/card gates, panels and pushables have been directly separated;
- key-name order is exactly Red, Green, Blue, Yellow;
- card-name order is Red ID card, Yellow ID card;
- mapped wall types `0x19..0x1C` are exactly Red/Green/Blue/Yellow-key interaction families and do not consume the key in this handler;
- mapped wall types `0x25..0x2C` are tied to the combination-check / combination-lock path;
- panel runtime: `0xA356`, stride 22, maximum 32;
- push runtime: `0xA616`, stride 6, maximum 12.

These are **VERIFIED_EXE** except where the detailed document explicitly says `PARTIAL`.

## Fixed 14-step extraction order toward 95–100%

1. **Player collision/passability** — finish the small remaining side effects/state labels and trajectory regression.
2. **USE `0x0200`** — finish remaining special-wall/object subfamilies.
3. **OBJECT `+14..+1B`** — complete all read/write/xrefs for the 28-byte runtime record.
4. **GUARD movement** — speed, octant->delta, collision, blocked fallback.
5. **GUARD AI state machine** — strategy/state/nextstate/timer, detection, attack, projectiles, reactions.
6. **Player damage/death** — all damage producers, difficulty, health receiver, death/restart flow.
7. **Weapons** — cadence/cooldown/ammo/fire state for all four weapons.
8. **Pain/death + SND.DAT** — exact enemy transition and sound mapping.
9. **Enemy identity** — runtime class `0x0C..0x1F` -> OBJECT/IMG/map/sprite/enemy identity.
10. **Level/script engine** — complete event/opcode dispatcher; preserve known anchors such as `0x16`, `0x47`, `0x48`.
11. **USER.SAV semantics** — assign every persisted runtime block to its exact globals/structures.
12. **Subsystems** — debug/keyboard, command line, MIDI, SND runtime/cache, BSF/edition/integrity.
13. **Renderer** — view transform, vector/wall traversal, clipping, texture-column sampling, sprite/depth/occlusion.
14. **Final EXE audit** — classify every executable code range as `RECONSTRUCTED_GAME`, `KNOWN_FRAMEWORK`, `COMPILER_RUNTIME`, `THUNK`, `DATA`, or `UNKNOWN`, and calculate real byte coverage.

## Comparison sources

For movement/collision, interaction, actor AI and renderer mathematics, compare in this order:

1. original Nitemare `NITE3W.EXE` — authoritative target;
2. Catacomb Abyss public source — high-value structural comparison;
3. Wolfenstein 3-D public source — secondary lineage/algorithm comparison.

A similarity label is not promoted to “identical” unless control flow/constants/data representation actually match.

## Save/runtime anchors

- `USER.SAV` slot size: exactly `0xD6E7` = 55,015 bytes. **VERIFIED_EXE**
- mutable map image at save offset `0x35`, size `0x2000` = 8192 bytes. **VERIFIED_EXE / VERIFIED_DATA**
- gameplay/global block at `USER.SAV+0x2035`, size `0x5E`. **VERIFIED_EXE**
- save/load restores raw runtime blocks, rebuilds pointers and rebases timers. **VERIFIED_EXE**

## Demo/attract anchors

- DEMO is recorded input, not absolute position playback;
- `-r` enables recording;
- supplied demo records are 8 bytes after the 6-byte header;
- E1M11 is an internal/demo map and normal progression does not expose it;
- the origin search for DEMO.2 and DEMO.3 must remain open to all 31 preserved maps or an older/deleted map.

See `docs/DEMO_FORMAT_RE.md`.

## Implementation rule

Do not encode guessed constants as final game logic. New reconstructed source must retain evidence labels/comments until values are verified. Prefer structures that can replace partial semantics without changing public interfaces.

## Completion criterion

The project reaches the 95–100% claim only after the final function/range audit shows that essentially all executable game code is either reconstructed or deliberately classified as framework/compiler/thunk/data, with any remaining `UNKNOWN` ranges explicitly quantified and listed.


## 2026-09-25 Win16 MFC / memory synchronization

The current repository now contains the relocation-aware Win16 MFC reconstruction and its modern compatibility layer. Canonical entry point: `docs/WIN16_MFC_RE_SUMMARY.md`. Static artifacts cover `CRuntimeClass16`, 31 runtime classes, CWnd layout/vtable/lifecycle anchors, HWND/HDC/HGDIOBJ/HMENU HandleMaps, evidence levels and explicit coverage states. Runtime validation remains separately tracked and requires the Win3.1 debugger checklist/capture template. The modern C++20 layer now includes `HandleRegistry`, `NativeHandleWrapper`, `WindowWrapper`, `WindowRegistry`, nested/RAII temporary scopes and the recovered z-order mapping. Historical 16:16 pointers, NE fixups and raw MFC object layouts are evidence only and are not reproduced as the x64 ABI.
