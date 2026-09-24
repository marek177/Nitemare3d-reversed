# Nitemare 3D project findings delta — 2026-09-23

This update consolidates the current executable, data, save-file, renderer, and video audits with findings already recorded in the project. It supplements rather than replaces the 2026-09-22 all-thread consolidation and subsystem reports.

## Audit coverage and limits

The current function inventory tracks **1,486 identified function definitions**: 519 from DOS N3D 2.0 and 967 from Win16 NITE3W 1.10. Cross-version matching supports 429/519 DOS and 929/967 Win16 definitions (1,358/1,486, 91.4%). This is evidence for function identity, not a percentage of understood behavior. Detailed manual body analysis still covers only the first 200 functions per platform; merged DOS ranges, damaged decompilations, and weak matches remain open.

The NE relocation pass found 6,082 relocation sites, including 4,904 internal segment fixups. Of these, 610 were assigned to a function (104 described, 462 call-target references, 44 data candidates), 20 were ambiguous, and 5,452 did not yet have an owner. The 283 mapped call edges are a partial graph, not a complete IDA/Ghidra XREF export.

DOS v2.0, Win16 1.10, and control Win16 1.8 were audited separately. Similarity across builds does not prove identical behavior; runtime verification remains outstanding where called out below.

## Player projectiles — Win16 1.10

The save block formerly left unnamed at USER.SAV +0xC403 is the player-fired projectile pool: **8 slots × 42 bytes = 336 bytes**. Each record contains 14 bytes of movement state and an embedded 28-byte OBJECT record beginning at +0x0E. State values are 0 free, 1 flight, and 2 impact animation. Field +0x0D and several embedded OBJECT bytes remain unknown.

| Record offset | Recovered meaning |
|---:|---|
| +0x00 | X-dominant-axis selector |
| +0x02 | Bresenham line error |
| +0x04 | minor-axis error increment, 2 × minor |
| +0x06 | error correction, 2 × (minor − major) |
| +0x08, +0x0A | signed X/Y step (−1 or +1) |
| +0x0C | slot state: free / flight / impact |
| +0x0E..+0x29 | embedded 28-byte runtime OBJECT |

Weapon selectors 0, 1, and 3 allocate projectiles; selector 2 uses the hitscan path. Wand flight/impact sequence offsets are 2/3; plasma offsets are 0/1. A successful projectile or hitscan firing path calls the saved guard-wake selector logic.

The movement routine executes a calibrated number of small Bresenham substeps per update. The calibration is based on measured update/render timing, so exact world-units per second and millisecond timing are not recovered. On each substep the code tests the map cell, then a guard; both X and Y differences must be at most 9 world units for a guard hit. Explodable wall property 0x10 requests event 0x29 and starts the wall OBJECT's impact sequence.

The ±20 check is a **projection/culling condition**: the embedded OBJECT is projected when abs(projectileX-playerX)>20 OR abs(projectileY-playerY)>20. It does not end the projectile or free its slot. This corrects an earlier provisional description that misread the render call as cleanup. Pool-full firing returns before the ammo helper, so no ammunition is consumed.

Damage depends on the target OBJECT's projected scale field at +0x18; FUN_1010_CC7C writes that camera-derived projection/depth-scale cache, while the damage producer combines it with the view reference and random()%25. It is not world Y and does not support a fixed shots-to-kill table without controlled geometry, weapon, difficulty, and RNG assumptions.

Detailed field and save evidence: [Win16 projectile pool audit](../analysis/nite3w_projectile_pool_2026-09-23.md). Remaining work includes exact timer units, pointer updates after each movement step, unnamed record bytes, DOS comparison, and enemy-fired projectile ownership/class bindings.

## USER.SAV and runtime state resolved in this pass

| Save range | Finding |
|---|---|
| 0xC3E3..0xC402 | 32 per-panel activation bytes copied from each panel record +0x14 |
| 0xC403..0xC552 | eight 42-byte player projectile records |
| 0xC553..0xC55A | global bytes 0x51A4..0x51AB |
| 0xC55B..0xC5A2 | 12 × 6-byte push records |
| 0xC5A3..0xD5A2 | 4096-byte automap raster/index buffer; draw/update roles are known, every byte value is not |
| 0xD5A3..0xD5E2 | 64-byte guard wake one-shot cache, keyed by a class-D / DOOR-family wall selector |
| 0xD5E3..0xD6E2 | 256-byte palette color-remap table |
| 0xD6E3, 0xD6E4 | fill-color selectors at runtime 0x7E62/0x7E63; actual framebuffer area names remain open |
| 0xD6E5..0xD6E6 | shade-level word at runtime 0x7E60; default index 2, scripted dark-event index 6 |

The shade lookup uses [0,4,8,12,16,20,30,40], then multiplies the selected value by four before reducing each RGB channel. The dark-event index therefore requests a 120-per-channel subtraction before clipping/remapping. Fill selectors are zeroed during the event. Override inputs are initialized to 0xFFFF; no non-default writer was found in the static export.

The 64-byte guard wake cache is reset on a new level and restored by USER.SAV load. After a successful player shot, the current nonzero last-seen class-D wall selector is marked once; strategy-0 guards on that selector in states 7/8 receive a random 0–7 update timer and enter state 1. It has no distance, line-of-sight, or sound-attenuation test in this handler. The supplied WALLS data yields sparse selector values 0–62; selector 0 is a no-op. Runtime behavior for repeated selectors and the design reason for grouping by door-wall ID remain open.

## USER.SAV 0x51A4..0x51AB flag meanings

- 0x51A4 is a bit for the linked wall state of a SECRET panel. The supplied MAP/OBJECTS data uses class 0x03, object ID 0x62, channel 0. The panel requires ID-card mask bit 0, identified as the red card (object ID 0x09). Commands 0x1E/0x1F update linked class-0x3B/0x3C wall-pair records. SAFE object IDs 0xD2..0xD7, class 0x26, use a separate combination routine.
- 0x51A5 initializes to 1 and is toggled by panel commands 0x20/0x21. It gates Cannon class 0x19, object IDs 0xCC..0xCF, through AI states 0x0E..0x10; the enabled path can deal player damage after a perception check.
- 0x51A6 is a level-event stage/latch with 0/1/2 behavior. It also affects one class-0x16 damage branch. Distinguish this from the other-direction Hamerstein weapon damage: player-to-class-0x16 weapon damage is separately gated by 0x7E52.
- 0x51A7/0x51A8 latch Episode 1 index-9 trigger branches; 0x51A8 is read by a later escape/death path.
- 0x51A9 is written at the end of a timed Episode 2 index-9 collision script; 0x51AA is written by class-0x16 GUARD state 9. No later direct functional reader was found for either in the Win16 export.
- 0x51AB selects shade mode 6, zeroes the fill selectors, and makes the shared wall-pair state helper return early. Its duration and visible scene effect still need runtime observation.

See the full [USER.SAV event/AI flag audit](../analysis/nite3w_user_sav_story_flags_2026-09-23.md).

## Fire damage recovered from the executable

Object class 7 (CAUSTIC) uses a three-byte damage table indexed by supplied OBJECTS order:

| Object ID | Fire size | Damage per simulation update | E3M6 passability |
|---:|---|---:|---|
| 0x3B | Large | 100 HP | Impassable/lethal per original documentation and video audit |
| 0x3C | Medium | 10 HP | Passable |
| 0x3D | Small | 2 HP | Passable |

The values are direct Win16 1.10 executable/data findings. They are damage per simulation update, not DPS; DAT_53F2 is calibrated at runtime, so a fixed seconds conversion is not claimed. The [E3M6 video audit](VIDEO_AUDIT_E3M6.md) independently confirms visible passability and exposure behavior, not the numeric values.

## Renderer and interaction audits carried forward

The 2026-09-23 renderer assembly pass confirms the Win16 occupied-column ownership rules, texture-U corrections, 16.16 wall-column sampling, 16.16 span interpolation, and wall-animation update control flow. DOS E-20 independently confirms the shared texture-U/animation formulas and the sampler arithmetic. The complete vector/span scene path, special-wall/resource map, sprites/palette details, and original-frame pixel comparison remain open.

Across video and static interaction audits, preserve the already documented facts: colored key inventory persists; stair selection has three options; E3M6 has a changeable chest score and a multi-section fire route; and its completion screen reports Level 6, 18 enemies remaining, 2 panels not found, 0 bonus, score 25675. The E3M6 walkthrough does not alone prove numeric fire damage. Episode-specific content remains in the existing per-level video audit reports.

## Code and confidence updates

The C++ reference model now exposes the projectile record layout and tests its size, slot states, weapon routing, hit tolerance, and render-only ±20 threshold. The fire model exposes the executable-derived object ID mapping and per-update damage, separate from behaviorally audited passability. RecoveredRuntime.hpp names the save blocks and shade fields. UnknownSystemsAudit.hpp no longer treats the 336-byte pool as an unknown record.

Static Win16 statements here are not automatically DOS behavior. Projectiles' calibrated speed, event timing, scene pixels, unknown record bytes, save/load side effects beyond tested copies, and unresolved story text remain open.


## 2026-09-25 Win16 MFC / memory synchronization

The current repository now contains the relocation-aware Win16 MFC reconstruction and its modern compatibility layer. Canonical entry point: `docs/WIN16_MFC_RE_SUMMARY.md`. Static artifacts cover `CRuntimeClass16`, 31 runtime classes, CWnd layout/vtable/lifecycle anchors, HWND/HDC/HGDIOBJ/HMENU HandleMaps, evidence levels and explicit coverage states. Runtime validation remains separately tracked and requires the Win3.1 debugger checklist/capture template. The modern C++20 layer now includes `HandleRegistry`, `NativeHandleWrapper`, `WindowWrapper`, `WindowRegistry`, nested/RAII temporary scopes and the recovered z-order mapping. Historical 16:16 pointers, NE fixups and raw MFC object layouts are evidence only and are not reproduced as the x64 ABI.
