# Reconstruction status — v1.1

Date: 2026-09-23

This repository is a clean-room-style reconstruction scaffold based on the supplied Windows 3.1 executable/data plus independently documented gameplay observations. It is not the original Gray Design Associates source tree.

The canonical cross-thread/session summary is now:

- [`ALL_THREADS_CONSOLIDATION_2026-09-22.md`](ALL_THREADS_CONSOLIDATION_2026-09-22.md)
- [`UNKNOWN_SYSTEMS_AUDIT_2026-09-22.md`](UNKNOWN_SYSTEMS_AUDIT_2026-09-22.md)

Use the subsystem reports for instruction-level evidence. This status file intentionally avoids promoting uncertain field names or approximate subsystem percentages into facts.

## Completion estimate policy

The previous 2026-09-21 engineering estimate of roughly **69–71% direct binary/algorithm RE** and **86–87% broader behavioral reconstruction** is retained only as a historical working estimate. The 2026-09-22 renderer and GUARD passes resolved several major unknowns, but no new overall percentage is asserted here because a defensible final percentage requires function/range classification of the executable rather than subjective averaging.

## Strongly understood

### Platform / executable

- Win16 NE structure, 10 logical segments and direct import-module inventory.
- WinG/DISPDIB display/presentation path.
- 320×200, 8-bit indexed WinG framebuffer.
- normal 3-D viewport x=8..311, y=4..155 = 304×152, center `(160,80)`.

### Win16 MFC / memory ownership

Direct-binary relocation-aware analysis now recovers the core MFC 2.5 object/memory framework used by NITE3W: CWnd/CDC/CGdiObject/CMenu handle maps, temporary/permanent wrapper lifetime, the 16-byte CRuntimeClass format, CWnd's 0x1A-byte object size and HWND fields, the four z-order sentinel CWnd objects, and the Win16 CRT far-heap split/coalesce/grow behavior. See [`../analysis/nite3w_win16_mfc_memory_2026-09-25.md`](../analysis/nite3w_win16_mfc_memory_2026-09-25.md) and [`../src/re/Win16MfcMemory.hpp`](../src/re/Win16MfcMemory.hpp).

Modern-port guidance that separates original Win16 ABI evidence from Windows 11/x64 implementation choices is in [`WIN16_MFC_TO_X64_PORT.md`](WIN16_MFC_TO_X64_PORT.md).

### MAP / world / runtime pools

- MAP archive header 514 bytes; each level payload is 64×64×2 = 8192 bytes.
- MAP cell order `{wallByte, objectByte}`.
- supplied payload counts: E1=11, E2=10, E3=10; E1M11 is internal/demo.
- world scale: 64 internal units per tile.
- player spawn IDs 1–4 and four cardinal initial orientations.
- OBJECT records: 28 B, max 350, base `0x6D66`, count `0x7E58`.
- GUARD records: 26 B, max 100, base `0x93AE`, count `0x7E5E`.
- doors: 64×22 B; panels: 32×22 B; pushes: 12×6 B.
- vectors: max 1000×28 B.
- four orientation VECLIST arrays: each max 333 4-byte far pointers.
- visible wall spans: max 50×20 B.
- projected sprite commands: max 100×18 B.

The older OBJECT=80 B, GUARD=98 B and renderer-record=52 B estimates are superseded.

### Player movement / interaction

- 27-world-unit player collision AABB half-extent.
- incremental movement with X/Y collision resolved separately, producing wall sliding.
- USE input mask `0x0200`, rising-edge behavior and one-adjacent-cardinal-cell targeting.
- wall/object property tables at `0x7E94` / `0x7F94` with directly recovered blocking, dynamic-door, script/touch, object-presence and guard-creation bits.
- pushables use runtime class `0x28`; eight 8-unit updates move one 64-unit tile.
- colored-key order and major wall/door/warp families are mapped from executable/data evidence.

### Renderer architecture

The basic renderer architecture is now substantially resolved:

```text
MAP 64x64
 -> exposed boundary extraction
 -> merge compatible adjacent edges
 -> VEC[1000], 28 B each
 -> four orientation VECLIST[333] pointer indexes
 -> project / near-clip candidate VECs
 -> 320-entry wall-owner far-pointer table at 0x53FE
 -> coalesce equal owner runs to <=50 wall spans at 0x5E88
 -> ceiling/floor
 -> textured wall columns
 -> 320-entry wall silhouette/occlusion table at 0x58FE
 -> object projection/culling
 -> <=100 projected sprite records at 0x6270
 -> sprite draw
 -> framebuffer presentation
```

Confirmed/high-confidence renderer details include:

- MAP→VEC producer `FUN_1018_4370` / `FUN_1018_4046` with four orientation passes.
- VEC world endpoints at `+0C/+0E/+10/+12` and projected endpoint fields at `+14..+1A`.
- orientation 0/1 horizontal and 2/3 vertical boundary construction.
- four VECLIST count globals `0x697A/7C/7E/80` and bases `0x6982/0x6EB6/0x73EA/0x791E`.
- horizontal lists sorted by Y, vertical lists by X.
- per-column owner table uses 320 far pointers and supports early termination when all active viewport columns are covered.
- owner runs are coalesced to 20-byte wall-span records.
- wall column source uses 64 samples in the audited WinG path.
- sprite transparent palette index is `0x29` in the audited sprite path.
- the original renderer is not Wolfenstein 3-D's one-grid-ray-per-screen-column DDA.

The remaining renderer work is concentrated in conflict resolution, special-wall texture mapping, animation fields, alternate VGA/backend behavior and exact units/semantics of a few intermediate values rather than the basic architecture.

See [`../analysis/nite3w_renderer.md`](../analysis/nite3w_renderer.md).

### GUARD / combat

- GUARD debug semantics directly identify `strength`, `strategy`, `state`, `nextstate`, `timer`, `octant` and `resoct` fields.
- fresh GUARD strength is initialized to 255 (`0xFF`); direct writes include creation, lethal clear and non-lethal subtraction.
- state dispatcher covers `0x00..0x15`; `0x15` is confirmed pain/hit reaction and returns to `next_state`.
- original per-GUARD score switch is recovered for GUARD1..25; GUARD26/Dancers follows the default zero-score path.
- notable verified scores include Dracula 0, Demon 250, Penelope -1000 and Dr. Hamerstein 1000.
- player→GUARD damage producer and class/weapon transform matrix are substantially reconstructed.
- player health is runtime byte `0x4C1D`, normally initialized/capped at 100.
- enemy/object→player damage producer and final difficulty transform are recovered; remaining work is chiefly class/name/projectile binding.
- difficulty value `0/1/2` is constrained by three systems: player damage, enemy damage and GUARD timer scaling.
- ammo pools, normal pickup increments, signed silver/laser byte quirk and scripted weapon-jam mechanism are recovered.

### Saves / audio / resources

- `CONFIG.SAV` is 20 bytes.
- `USER.SAV` slot size is `0xD6E7 = 55,015` bytes. The 8 × 42-byte player projectile pool at `0xC403`, panel activation bytes, push array, automap raster, guard wake cache, color-remap table and shade/fill tail are mapped.
- load logic rebuilds pointers and rebases timers; save data is not a naive reusable pointer dump.
- SND.DAT directory: 160×6-byte entries; IDs 1..15 MIDI, 34..110 logical SFX range, 111 end sentinel.
- audited Windows SFX data is raw 8-bit mono PCM at 11025 Hz.
- GAME.PAL exact palette payload is known; default floor/ceiling indices are `0x0C` / `0x11`.
- ENDING.FLI header/video properties and E3M10 finale use are documented.

## Current subsystem state

The table below deliberately uses qualitative states rather than implying byte-accurate completion percentages.

| Subsystem | State after 2026-09-22 consolidation |
|---|---|
| Win16 NE / imports / presentation | strong |
| MAP archive/world scale | strong |
| player movement/collision | strong |
| USE/interactions | strong with special-class gaps |
| OBJECT physical record | strong size/base/capacity; many field semantics partial |
| GUARD physical record | strong core fields; tail fields partial |
| GUARD state machine | dispatcher/handlers mapped; exact semantic state names and timing still partial |
| GUARD score | strong / direct switch evidence |
| player→enemy damage | strong arithmetic/matrix; some visible-name binding partial |
| enemy→player damage | strong producer/difficulty; class/projectile binding partial |
| player health/death | strong normal path; alternate hazard/death path partial |
| weapon cadence | partial |
| doors/panels/controls | physical records/capacities strong; state fields/dispatch partial |
| pushables | strong core movement/table behavior |
| renderer architecture | strong |
| renderer VEC/VECLIST | strong core construction/geometry; animation/resource fields partial |
| wall owner/conflict | owner table strong; occupied-slot winner mathematics partial |
| wall texture/special cases | partial |
| sprite projection/queue | strong structure; exact field labels/order edge cases partial |
| USER.SAV physical layout | strong |
| USER.SAV semantic fields | partial |
| SND.DAT container/PCM | strong |
| exact SFX semantic map | partial |
| MIDI usage table | partial |
| UIF.DAT semantics | partial |
| BSF integrity/registration | partial |
| debug/keyboard paths | partial-to-strong depending command |

## Ghidra / IDA cross-audit context

A prior cross-audit counted approximately 1,067 unique Ghidra `FUN_*` candidates, 4,984 `LAB_*` labels, 829 `DAT_*` symbols, roughly 4,666 CALL/CALLF occurrences, about 10,958 XREF blocks and approximately 308 external API symbols. These are analysis-workset counts, **not** the final number of original game functions: static runtime/MFC/library code and imperfect auto-function boundaries remain mixed in.

The important improvement since that audit is that the producer of the four renderer vector lists is no longer an open architectural question. MAP boundary extraction, VEC construction, orientation indexing and the four sorted VECLIST arrays are now traced. Likewise, enemy→player damage is no longer wholly unresolved; its producer/difficulty transform are known while visible attacker binding remains incomplete.

## Major unresolved areas

The complete machine-readable target register is available in
`src/re/UnknownSystemsAudit.hpp`; it distinguishes verified anchors from
hypotheses and TODOs.

1. Complete OBJECT field semantics, especially the remaining animation/projection/runtime fields.
2. Complete GUARD field tail and give exact high-level names to states 02..14.
3. Recover guard movement speed, reaction delay, attack interval and full LOS/hearing behavior.
4. Map all enemy/projectile classes to the recovered player-damage branches.
5. Calibrate projectile substep speed/time and resolve enemy-projectile identity/ownership; player-pool layout, impact state and <=9-unit guard hit tolerance are now mapped.
6. Decode complete door/panel/control 22-byte records and remote-door/cannon state machines.
7. Complete numeric wall-class dispatcher and `WALLS.*` secondary attribute-bit layout.
8. Complete animated-wall/resource mapping and sequence timing beyond the recovered `FUN_1010_65A6` update control flow.
9. Integrate the full camera/vector/span scene path and compare deterministic frames with the original.
10. Finish `FUN_1010_6422` special-wall cases and lower raster/backend paths; owner-conflict math and texture-U corrections are now mapped.
11. Verify shade-level override bounds/runtime presentation (`0x7E60` / USER.SAV `0xD6E5`) and exact fill-region semantics for `0x7E62/0x7E63`.
12. Finish remaining USER.SAV semantic blocks/timer rebasing.
13. Finish exact SFX event and MIDI level/menu call-site maps.
14. Reconstruct `NITE3D.BSF` integrity algorithm across version variants.
15. Complete final byte/function/range classification of the executable.

## Comparison rule

Catacomb Abyss, Hovertank 3-D, Wolfenstein 3-D and related released source trees are comparison material only. Similarity is not treated as identity unless the original Nitemare executable demonstrates matching control flow, constants and data representation.

## Repository constraint

The public repository intentionally excludes original game binaries/assets, IDA databases, source MP4s and frame-evidence images.
