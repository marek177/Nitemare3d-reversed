# Nitemare 3-D cross-session master index

Updated: 2026-09-23

This file indexes findings accumulated across the Nitemare 3-D reverse-engineering conversations. The detailed canonical report is ALL_THREADS_CONSOLIDATION_2026-09-22.md.

The unresolved-system register is maintained in
[`UNKNOWN_SYSTEMS_AUDIT_2026-09-22.md`](UNKNOWN_SYSTEMS_AUDIT_2026-09-22.md)
and `src/re/UnknownSystemsAudit.hpp`.

## Evidence policy
Use VERIFIED_EXE, VERIFIED_DATA, VERIFIED_SAVE_LAYOUT, BEHAVIORAL, INFERRED, PARTIAL and TODO. Do not promote old guesses or approximate percentages into original-game facts.

## Corrections
- OBJECT record: 28 B, capacity 350; older 80 B hypothesis is superseded.
- GUARD record: 26 B, capacity 100; older 98 B hypothesis is superseded.
- Visible wall span: 20 B, capacity 50; older 52 B hypothesis is superseded.
- Renderer is a projected MAP-boundary VEC/span renderer with per-column ownership, not Wolf3D one-ray-per-column DDA.
- VEC: 28 B, capacity 1000. Four orientation VECLISTs contain 333 far pointers each.
- WARP_L1..L4 are colored-key locked passage families.
- ONE_SHOT is the recovered spelling.
- MAP payload counts do not prove a universal ten-level runtime limit.

## Renderer
Framebuffer is 320x200 indexed. Normal 3-D viewport is 304x152 at x=8..311, y=4..155, center=(160,80).

Pipeline:
MAP 64x64 -> boundary extraction/merge -> VEC[1000] -> four VECLIST[333] -> transform/near clip -> project -> owner[320] -> wall spans -> floor/ceiling and walls -> per-column wall occlusion -> object projection -> sprite queue -> framebuffer.

Important anchors: owner table 0x53FE; wall occlusion 0x58FE; wall span count 0x5E7E; wall spans 0x5E88, stride 20; projected sprite queue 0x6270, stride 18, capacity 100. Tile scale is 64 world units.

VEC orientation: 0 top, 1 bottom, 2 right, 3 left. High-confidence offsets: wallId +00, flags +05, renderClass +06, orientation +07, endpoints +0C/+0E/+10/+12, projected fields +14..+1A. Flag 0x20 flips texture-U direction. Fields +01/+02/+03/+04/+08 remain partial.

Remaining renderer targets: complete camera/vector/span scene integration, FUN_1010_3E44 lower wall blitter, exact wall-animation/resource mapping, VEC flag semantics, and full WALLS-to-render-class coverage. The 2026-09-23 raw-assembly audit resolved the occupied-column owner rules, texture-U corrections, fixed-point sampling/interpolation and animation update control flow.

## Runtime
Known capacities: doors 64x22 B; panels 32x22 B; pushes 12x6 B; objects 350x28 B; guards 100x26 B; vectors 1000x28 B; wall spans 50x20 B; projected sprites 100x18 B.

Player world X/Y are 0x4BF6/0x4BF8; tile X/Y 0x4BF2/0x4BF4; world-to-tile is shift-right 6. Collision uses axis-separated movement/sliding. USE is input bit 0x0200. Push movement is 8 updates x 8 units = one tile.

DEMO record is 8 bytes: event byte, input mask, pad, 32-bit timestamp. Important masks: 0x0002 forward, 0x0004 backward, 0x0008/0x0010 turn, 0x0020 fast modifier, 0x0040 unit-increment behavior, 0x0080 fire, 0x0100 strafe modifier, 0x0200 USE. Command-line -r enables recording.

## GUARD and combat
GUARD record is 26 B. Normal creation initializes strength to 255. Dispatcher states are 0x00..0x15; 0x15 is confirmed pain/hit reaction. Do not invent per-enemy starting HP without new executable evidence.

Verified score switch: Bat 25; Frankenstein 75; Mummy 50; Skeleton 100; Mrs H. 250; Zelda 150; Vampira 200; Baddie1 100; Baddie2 100; Dracula 0; Cemetery Gargoyle 150; Garden Gargoyle 150; GUARD13 unknown 200; Penelope -1000; Dr. Hamerstein 1000; Tall slim robot 100; Trashcan robot 200; Cannon 0; Ghost 25; Goldie 100; Greenie 100; Demon 250; Alien1 250; Alien2 200; GUARD25 unknown 50. GUARD26/Dancers follows the default zero-score path. Dracula's zero score is separate from scripted Dracula-to-Bat behavior.

Weapons: 0 single-shot laser, 1 magic wand, 2 silver pistol, 3 continuous laser. Ammo: silver 0x4C1F, laser 0x4C20, wand 0x4C44. Difficulty global 0x4C14 controls damage and guard timing; exact transforms are documented in COMBAT_DAMAGE_RE.md.

## Data/resources
Continue auditing MAP, IMG, OBJECTS, WALLS, SND.DAT, UIF.DAT, ENDING.FLI, GAME.PAL, DEMO, BSF and save files. E1M3 and E1M11 share the same local first-plane geometry/spawn fingerprint but differ in second-plane bytes, making them useful demo-matching controls.

SND.DAT/VOC extraction must be compared with original playback. ENDING.FLI has 488 frames and uses COLOR_64, BRUN, LC, BLACK and COPY chunks; editing must preserve delta-frame semantics.

## 2026-09-23 projectile, save and hazard update

- Player-fired NITE3W projectiles use 8 × 42-byte records at USER.SAV +0xC403; +0x0E embeds a 28-byte OBJECT. The ±20 check controls projection only, not lifetime.
- USER.SAV +0xC553 stores flags 0x51A4–0x51AB; 0x51A4 is the SECRET-panel linked-wall bit (red ID-card bit 0 required), and 0x51A5 gates Cannon AI.
- USER.SAV +0xD5A3 is the 64-byte one-shot guard wake cache keyed by a class-D wall selector. +0xD5E3 is the palette remap table; +0xD6E5 mirrors shade index 0x7E60 (default 2, dark event 6).
- CAUSTIC fire IDs 0x3B/0x3C/0x3D apply 100/10/2 HP per simulation update; calibrated seconds/DPS remain open.

See [the 2026-09-23 all-audit delta](PROJECT_FINDINGS_DELTA_2026-09-23.md).

## Open targets
1. Complete camera/vector/span integration and deterministic pixel comparison.
2. Remaining special-wall/resource mapping and lower raster/backend paths.
3. Wall-animation/resource mapping and unresolved VEC field semantics.
4. Shade override bounds and runtime presentation at 0x7E60.
5. WALLS ID -> flags -> renderClass -> resource -> handler map.
6. Door/panel/control layouts and special scripts.
7. GUARD states 02..14, movement, attack timing and perception.
8. Enemy attack/projectile identity and SND mappings; the NITE3W player projectile pool and guard-hit test are now structurally mapped.
9. GUARD25 identity and GUARD26 dancer script.
10. DEMO.2/3 origin across all preserved maps.
11. BSF integrity/version algorithm.
12. Hidden/deleted/unused code, cheats, alternate paths and runtime limits.
13. UIF/SND/FLI edge cases and unresolved save blocks.

The current end-to-end priority chain is GUARD AI → sequence event →
projectile/weapon → collision → damage → death → score/drop/morph. Unknowns
must remain labelled rather than being promoted to HP, speed or immunity facts.

When a finding changes, update the canonical consolidation, subsystem report, clean-room fact header and regression test together.
