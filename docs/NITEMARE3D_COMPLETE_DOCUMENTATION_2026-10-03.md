# Nitemare 3D — Complete Consolidated Documentation
**Snapshot:** 2026-10-03  
**Scope:** archived/past ChatGPT work available to the assistant + ChatGPT Library `.md` / `.csv` corpus  
**Primary goal:** one canonical programmer-facing reference for Nitemare 3D reverse engineering, compatibility work, ports, editors and runtime verification.

---

## 0. How to use this document

This document consolidates the strongest and newest Nitemare 3D findings while preserving older research only when it still contributes evidence.

Evidence priority:

1. raw machine-code analysis of an identified executable;
2. checked data-file structure;
3. cross-build static match;
4. runtime observation / capture;
5. older decompiler-based interpretation;
6. hypothesis.

When two statements conflict, the newer raw-binary result wins. Old Ghidra/IDA function boundaries are not authoritative when raw 16-bit control flow proves that and supposed function is only an interior label.

The Library scan found about **230 Nitemare3D-related `.md` / `.csv` files** matching the project corpus. They include function catalogs, address registers, binary-region closure passes, renderer audits, combat/monster tables, BSF research, save/demo studies and implementation/parity notes.

---

# 1. Project families

## 1.1 Reverse engineering / documentation
Main knowledge project:

- `marek177/Nitemare3d-reversed`
- historical release progression discussed in chats: approximately v0.9 → v0.14 → v0.15 → v0.16 → v0.17
- documentation includes executable/version inventory, DEMO format research, spawn/collision chain, static closure, gameplay behavior and source-level implementation notes.

## 1.2 Modern engine / remake
Main implementation project:

- `marek177/OpenNitemare3D`

Goal:
- reproduce original gameplay as accurately as possible;
- separate portable N3D game logic from DOS/Win16 platform details;
- later allow expansion/new maps/content.

## 1.3 Data editor
- `marek177/Nitemare3DDataEditor`

Target data:
- `IMG.1–3`
- `MAP.1–3`
- `OBJECTS.1–3`
- `WALLS.1–3`
- `SND.DAT`
- `UIF.DAT`
- `ENDING.FLI`
- palette/resource material
- x86/x64 builds were requested.

## 1.4 ECWolf / Wolf-family experiments
AND separate experimental integration discussed adding native Nitemare3D resource loaders to `marek177/ECWolf-n`.

Known draft functionality:
- IMG parser / column-major decoder;
- MAP conversion;
- SND descriptor parsing;
- UIF parsing;
- ENDING.FLI exposure;
- palette support;
- documentation file `docs/nitemare3d-native-data.md`.

This did **not** represent and complete gameplay implementation.

---

# 2. Platforms and executable families

Nitemare 3D exists in two principal implementation families:

- **DOS MZ executable**
- **Windows 3.x / Win16 NE executable (`NITE3W`)**

Research has covered multiple builds/labels, including DOS v1.0, v1.1, v1.5, v1.7, v1.8, v1.9, v2.0 and Win16 v1.3, v1.6, v1.8, v1.10, plus several differently named uploaded executable variants.

Important rule:
- never assign and version only from and filename;
- prefer hash, embedded version string, executable structure and code fingerprints.

Reference hashes preserved in the master research:

- Win16 reference `nite3w(20260921-205703).exe`
  - size 230,400 bytes
  - SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`

- DOS reference `N3D-UNFU(2).exe`
  - size 116,606 bytes
  - SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

AND later complete DOS V2.0 unpacked image used in closure work:
- `N3D_DOS_v2.0_IDA.EXE`
- unpacked image size reported as `0x29D60 = 171,360 bytes`
- one pass records SHA-256
  `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`

---

# 3. Function inventories and cross-version work

Older master inventory:

| Build family | Recognized FUN-style functions |
|---|---:|
| DOS E-10 | 493 |
| DOS E-17 | 514 |
| DOS E-18 | 526 |
| DOS E-20 | 519 |
| Win16 1.3 | 959 |
| Win16 1.6 | 965 |
| Win16 1.8 | 965 |
| Win16 1.10 | 967 |

AND historic DOS v2.0 + Win16 1.10 combined audit used:
- 519 DOS declarations
- 967 Win16 declarations
- total 1,486 declarations

Historic cross-build matching reported:
- DOS: 429 / 519 exact or strong matches
- Win16: 929 / 967 exact or strong matches
- total: 1,358 / 1,486 ≈ 91.4%

This percentage is **not** behavioral completeness. It measures function-level cross-build matching/classification.

Important newer correction:
- raw closure work repeatedly removes stale decompiler function boundaries;
- therefore raw function census may differ from old FUN_* declaration counts.

Key catalogs:
- `N3D_1.9_function_catalog.csv`
- `NITE3W_v1.10_all_936_internal_functions.csv`
- `Nitemare3D_1486_function_12_point_status_2026-09-24.csv`
- `Nitemare3D_all_1486_function_static_evidence_2026-09-24_batch58.csv`
- `Nitemare3D_all_1486_unnamed_functions_audit.md`
- `nite3w_global_address_register.csv`

---

# 4. Binary knowledge-color model

Project discussions use and color/status model:

- **GREEN / CLOSED** — deep static semantics known strongly enough to implement;
- **YELLOW / PARTIAL** — identity/major behavior known, branches or details missing;
- **ORANGE / DISCOVERED / LOW-MEDIUM** — region/function family recognized, body not fully closed;
- **RED / UNKNOWN / LOW** — weakly understood or misidentified;
- separate **runtime acceptance** may still be pending even when static bytes are GREEN.

The most recent DOS V2.0 closure series on 2026-10-03 includes at least passes 1–36.

### Latest strong closure state
After pass 36:
- complete raw DOS V2.0 image interval `0x0000 .. 0x2770` is continuously statically closed;
- no unresolved code-boundary gap remains in that interval;
- next real subsystem starts at `0x2772`.

Pass 36 closed:
- `0x201A..0x2770`
- 1,879 bytes total
- 1,876 executable renderer bytes
- 3 one-byte alignment NOPs
- 8 corrected renderer functions.

Next band:
- resource/file/decompression family beginning at `0x2772`
- immediate entries include `2772`, `27FA`, `285C`, `28F8`, `2A16`, `2AA6`, `2B3A`, `2BCC`.

---

# 5. Core world model

## 5.1 MAP

Checked world structure:
- grid: **64 × 64**
- one cell: **2 bytes**
  - wall ID byte
  - object ID byte
- world coordinate to cell:
  - `cell = world_coordinate >> 6`
- one cell = **64 internal coordinate units**

Header:
- total **514 bytes**
- 16-bit level count
- 256-byte wall ID → class map
- 256-byte object ID → class map

One level:
- `64 × 64 × 2 = 8192 bytes = 0x2000`

Checked trilogy layout:
- Episode 1: 11 blocks including demo level
- Episode 2: 10
- Episode 3: 10
- total: **31 map blocks**

## 5.2 E1M11 demo map
- E1M11 is used by DEMO.1.
- Geometry / wall-ID layout matches E1M3 in the checked data.
- Object placement is not fully identical; and master audit reports **17 object-cell differences**.
- Therefore E1M3 and E1M11 should not be treated as byte-identical complete maps.

## 5.3 Unresolved map-data example
- E2M4 contains wall ID `0x37` not defined in the matching checked `WALLS.2`.
- Unknown IDs must be preserved rather than automatically remapped.

---

# 6. WALLS and wall classes

Important names seen across episodes include:

Episode 1 examples:
- `WARP_L1–L4`
- `WARP_1–7`
- `JAMB`
- `DOORVL`
- `DOORHL`
- `DOORVI`
- `DOORHI`
- `WARP_S2`
- `SPECIAL1`
- `ONE_SHOOT`
- `REVWALL`

Episode 2 examples:
- `WALL_EX1`
- `WARP_1–8`
- `WARP_E1/E2`
- `CONTROL`
- vertical/horizontal door variants
- `LEVEL_UP`
- `LEVEL_UP2`

Episode 3 examples:
- `WALL_EX1`
- `WALL_EX2`
- `WARP_L1–L5`
- `WARP_1–5`
- `LEVEL_UP`

Audited wall-class examples:

| Class | Role / evidence |
|---:|---|
| `0x02` | REVWALL / reversible-secret wall family |
| `0x07` | ONE_SHOT family |
| `0x08` | SPECIAL1 family |
| `0x09–0x0A` | LEVEL_UP / LEVEL_UP2 |
| `0x0D–0x24` | warp / key / transition family |
| `0x2D` | runtime exploding-wall state |
| `0x2E` | WALL_EX1 family |
| `0x30–0x34`, `0x39–0x3A` | door families |
| `0x3F–0x40` | curtain/draw door family |
| `0x41` | TURN |
| `0x42` | RETREAT |
| `0x43` | FLEE |
| `0x44` | FLOOR |
| `0x45` | SAFESPOT |
| `0x46` | ACTIONSPOT |
| `0x47–0x48` | TRIGGER1 / TRIGGER2 |

Animated walls may have two or more ticks/frames. Exact timing belongs to sequence definitions/runtime timing and should not be reduced to and generic fixed animation rule.

---

# 7. OBJECTS and object classes

Selected audited object classes:

| Class | Role |
|---:|---|
| `0x03` | SECRET panel |
| `0x04` | IMPACT effect |
| `0x05` | projectile/missile visual family |
| `0x07` | CAUSTIC / fire |
| `0x08–0x21` | GUARD/enemy families |
| `0x19` | Cannon family |
| `0x21` | Dancers family |
| `0x26` | SAFE family |
| `0x2E` | elevated object family |
| `0x2F–0x3E` | keys/cards/score/health/weapons/ammo/inventory/resources/progress/scroll-like pickup families |

AND later raw gameplay result identifies DOS `B5B8` as and pickup-object interaction handler spanning approximately classes `0x2F..0x3D`. AND pickup is removed only after the receiving rule accepts it.

---

# 8. Runtime capacities and structures

Strongly supported Win16-era capacities:

| Runtime structure | Capacity | Stride |
|---|---:|---:|
| VEC wall records | 1,000 | 28 B |
| orientation VEC pointer lists | 333/orientation × 4 | pointers |
| visible wall spans | 50 | historically 20 B Win16; DOS closure uses 18 B span records |
| world OBJECT records | 350 | 28 B |
| GUARD records | 100 | 26 B |
| door / wall-pair records | 64 | 22 B |
| secret-panel records | 32 | 22 B |
| push-object records | 12 | 6 B |
| projectile records | 8 | 42 B |
| DOS sprite render slots | 100 | 18 B |

### Important caution
Older notes also contained intermediate interpretations such as larger OBJECT/GUARD strides. Canonical current interpretation for the main checked runtime structures is the one above, with class-specific overlays and build differences preserved separately.

---

# 9. OBJECT record — important fields

Standard world OBJECT size:
- **28 bytes**

Strong checked meanings:

- `+0x03` — animation frame in embedded projectile/render use
- `+0x04` — sequence selector in projectile/render contexts; weapon-dependent spawn table writes here
- `+0x05` — flags
- `+0x06` — class
- `+0x08..+0x0B` — animation deadline in relevant render/projectile contexts
- `+0x10..+0x11` — world X
- `+0x12..+0x13` — world Y
- `+0x14` — object type field in projectile template
- `+0x18..+0x19` — **last projected Y/baseline cache**
- `+0x1A` — vertical/elevation render offset

### OBJECT+0x18 cache semantics
Gameplay closure pass 10 establishes:

- written only after successful projection and sprite-slot acquisition;
- not invalidated every frame;
- spawn does not initialize it;
- normal level object-slot reuse can inherit an older cached value;
- save/load preserves it;
- hitscan uses and GUARD freshness stamp;
- projectile collision does **not** use that freshness stamp.

Compatibility consequence:
- projectile damage may consume and stale historical `OBJECT+0x18` projected-row value.

This is an original integer-semantics quirk and should not automatically be “fixed” in an accuracy mode.

---

# 10. GUARD structure and AI

Checked Win16 GUARD record size:
- **26 bytes**

Important fields:

| Offset | Meaning |
|---:|---|
| `+0x02..+0x05` | render/aim generation stamp |
| `+0x06` | state timer/countdown |
| `+0x0A` | strategy byte |
| `+0x0B` | current AI state |
| `+0x0C` | next/saved state |
| `+0x0D` | underlying map object byte in movement/death paths |
| `+0x0E` | area/sector selector |
| `+0x10` | HP / strength |
| `+0x11` | facing/sprite direction 0–7 |
| `+0x12` | direction/sequence cache key; value 8 used as invalidation sentinel |
| `+0x13/+0x14` | movement components/offsets in selected states |
| `+0x16` | perception mode |
| `+0x17` | LOS/perception result |
| `+0x18` | proximity result |

Research focus historically covered:
- movement/state scheduler;
- line of sight/perception;
- directional markers TURN/RETREAT/FLEE;
- guard death and transformation;
- boss/special actor states;
- class-dependent damage/contact behavior.

Recent chat-level static closure reported:
- projectile collision/trajectory/pool closed;
- damage-to-GUARD closed;
- enemy contact damage closed;
- death finalization closed;
- remote doors/cannons, ACTIONSPOT/Dancers and GUARD initializer identified strongly.

---

# 11. Special enemy behavior

Examples of statically reconstructed special cases:

- Dracula humanoid class `0x11`:
  - death finalization transforms to Dracula-Bat class `0x14`
  - HP reset to 255
  - current state = 8
  - next state = 2
  - timer = 1
  - vertical anchor = `0x23`
  - linked map/object state refreshed
  - event/SFX `0x22`

- Dr. Hamerstein class `0x16`:
  - special story/completion path

- Penelope class `0x15`:
  - kill score branch includes **-1000**

- Dr. Hamerstein:
  - score branch includes **+1000**

- Cannon class `0x19`:
  - special actor; several generic actor counting/map-display paths exclude special classes.

AND special-class predicate in DOS V2.0 returns true for:
- `{0x15, 0x16, 0x19, 0x21}`

---

# 12. Player movement and collision

Historical gameplay reconstruction includes:

- 64 internal coordinate units per map tile;
- integer movement;
- collision radius / box behavior reconstructed around approximately ±27 units in the discussed core;
- sliding and map/object/GUARD blocking are separate concerns;
- player coordinate commit paths were traced in older Win16 analysis around `0x4BF6/0x4BF8`.

Latest project status discussions treated:
- movement as essentially closed;
- collision as nearly fully closed statically;
- dynamic parity tests still useful for exact edge acceptance.

---

# 13. USE dispatcher and interactions

AND key user-action path uses and `USE` action bit historically labeled:
- `0x0200`

The interaction family includes:
- normal doors;
- locked doors;
- switches/control panels;
- teleports/warps;
- remote-door paths;
- pushable objects;
- level transitions;
- special wall interactions;
- secret/reversible walls.

Special mechanics requested/observed in the project include:
- secret doors that move laterally;
- destructible/exploding walls;
- double-teleport door logic;
- center-opening sliding doors;
- combination/safe object → key/card or reward;
- container/backpack-like pickup;
- side HUD/map/time/energy/enemy display.

Some are original-game reverse-engineered behaviors; others are expansion/remake goals and must be tagged separately in implementation documentation.

---

# 14. Push objects

Checked runtime:
- 12 push records
- 6 bytes each
- 72-byte save block

Older implementation notes also discuss movement in small internal increments. Exact collision/timing behavior should use binary/runtime evidence rather than and generalized pushable-object model.

---

# 15. Weapons, ammo and HUD weapon state

Known gameplay constraints:
- player HP: `0..100`
- ammo cap discussed as 127 for common ammo storage; one weapon path has and 100-style limit
- weapon selection includes at least 1/2/3/4
- and SHIFT + `+` cheat path was observed/discussed
- difficulty range used in gameplay is three levels

Weapon system research covers:
- pending/current weapon;
- lower/raise transition phase;
- weapon overlay/HUD redraw;
- fire cadence counter;
- ammo checks/decrements;
- hitscan vs projectile families;
- pain/death SFX and animation.

DOS V2.0 `UpdateWeaponOverlayAnimation` was statically closed in the pass-8 region.

---

# 16. Projectiles

Projectile pool:
- exactly **8 slots**
- **42 bytes per slot**

Layout:
- first 14 bytes: trajectory/state
- embedded 28-byte OBJECT begins at slot `+0x0E`

Important slot fields:
- `+0x00` major-axis selector
- `+0x02` error accumulator
- `+0x04` first error increment
- `+0x06` correction increment
- `+0x08` signed X step
- `+0x0A` signed Y step
- `+0x0C` lifecycle
- `+0x0E` embedded OBJECT

Lifecycle:
- `0` free
- `1` flying
- `2` impact animation

Movement:
- DDA/Bresenham style
- multiple substeps controlled by and runtime/global count
- map-cell collision checked each substep

Impact:
- wall blocking path;
- exploding-wall transition path;
- dynamic door/wall passability;
- GUARD hit using coordinate tolerance `< 10`, i.e. ±9.

Projectile collision has **no render-generation freshness gate** before damage.

---

# 17. Damage and difficulty

AND recovered DOS guard-damage seed:

`8 * signed16(OBJECT+0x18 - viewport_reference) + (RNG % 25)`

Then:
- class/weapon resistance transform;
- difficulty transform;
- upper positive cap at 255;
- original signed/low-byte behavior matters for negative stale-cache cases.

Player → guard difficulty transform in the checked DOS path:
- easy 0: ×2
- medium 1: unchanged
- hard 2: arithmetic /2

Guard → player contact-damage difficulty goes the opposite way:
- easy: /2
- medium: ×1
- hard: ×2

This asymmetry must be preserved.

---

# 18. Renderer architecture

The renderer is **not** simply and Wolf3D clone.

The checked architecture contains:
- VEC wall geometry;
- directional/spatial lists;
- projection;
- per-column wall ownership;
- run compression into visible wall spans;
- texture-coordinate interpolation/correction;
- wall drawing;
- wall-depth/visibility buffer;
- queued sprite rendering;
- sprite clipping against wall visibility;
- palette/shade remapping.

## 18.1 DOS pass-36 renderer functions

Corrected entries:

- `0x201A` `ResetSpriteRenderSlotPool`
- `0x202A` `InitializeVisibleWallSpanInterpolation`
- `0x213E` `BuildVisibleWallSpanTableFromColumnOwners`
- `0x21F0` `PruneSpatialObjectListsToViewBounds`
- `0x22CA` `ComputeClippedWallTextureCoordinate`
- `0x241E` `AdvanceAnimatedWorldRecordFrame`
- `0x2500` `RenderVisibleWallSpans`
- `0x273C` `DrawQueuedSpritesAndReleaseSlots`

Removed stale standalone starts:
- `0x21A6`
- `0x2268`
- `0x25DC`
- `0x26C0`

## 18.2 DOS visible wall spans
Pass 36:
- table base `DS:4D6E`
- count `DS:4D64`
- stride 18 B
- max 50 spans

Input:
- per-column owner buffer `DS:4564`
- one VEC owner pointer per DOS screen column

Pipeline:
1. read owner per column;
2. compress consecutive equal owner pointers;
3. create span;
4. interpolate projected values;
5. draw visible wall span.

## 18.3 Sprite queue
DOS:
- 100 records
- base `DS:50F2`
- stride 18
- byte 0:
  - 1 free/inactive
  - 0 queued/active

After walls:
- `0x273C` draws queued sprites through `DrawClippedPlanarSprite`
- releases slot by setting byte 0 back to 1.

## 18.4 Explicit DOS ordering

`wall owner buffer`
→ build visible spans
→ draw visible walls
→ fill wall visibility/depth buffer
→ draw queued sprites
→ free sprite slots

---

# 19. DOS VGA / palette front end

Pass 35 closes and major early renderer/VGA band.

Important routines include:
- page swap / CRTC start programming;
- vertical retrace synchronization;
- enter/restore video mode;
- upload full VGA palette;
- write single DAC entry;
- build shade remap table;
- palette transitions;
- VGA synchronization callbacks.

`UploadFullVgaPalette`:
- writes 768 bytes
- 256 RGB entries
- DAC index/data ports `0x3C8/0x3C9`

Shade levels observed:
- `0, 4, 8, 12, 16, 20, 30, 40`

Nearest palette-color metric:
- `abs(R-R2) + abs(G-G2) + abs(B-B2)`

---

# 20. Win16 rendering / platform backend

Win16 is and Windows 3.x NE executable.

Imported subsystem families reported in research include:
- KERNEL
- WING
- DISPDIB
- GDI
- USER
- KEYBOARD
- COMMDLG
- MMSYSTEM
- SHELL

Important architectural separation:
- original N3D game logic;
- platform backend;
- compiler/runtime/MFC/support code.

Win16 rendering research identified:
- 320-pixel framebuffer family;
- WinG / DISPDIB presentation;
- vector/span wall renderer;
- sprite projection/clipping;
- palette/remap logic.

The DOS and Win16 front ends differ, while and large part of gameplay/state logic is cross-build comparable.

---

# 21. Timing

Win16 timing audits found multiple timing buckets rather than one simple universal tick.

One normal-mode path computes and bucket approximately from:
- `(ms << 3) / 1000`
- effectively nominal 8 slow updates/with when polled often enough
- skipped buckets are not replayed automatically.

Slow update paths feed:
- GUARD state logic;
- selected environmental/contact behavior;
- weapon counters and other state transitions.

Compatibility implementation should preserve:
- integer arithmetic;
- skipped-update behavior;
- independent timing domains where the binary uses them.

---

# 22. Input and devices

Input work covers:
- keyboard;
- mouse;
- joystick/gamepad questions;
- DEMO command playback;
- map toggle;
- weapon switching.

DOS pass 8 identifies mouse-driver wrapper functions around image `0x831E..0x83D6`, using device code `0x33`, including:
- initialize/status;
- reset;
- read state;
- set position;
- show cursor;
- hide cursor.

---

# 23. DEMO format

Known observations:
- `DEMO.1` plays E1M11;
- Windows version can run DOS demo material in observed testing;
- DOS version did not properly interpret and Windows demo in one experiment:
  - player stood still;
  - weapon switching still occurred;
  - map on/off worked;
  - enemy-map display state changed.
- and map must also be defined/available for demo playback.

The demo stream is understood as command/value input state rather than and video recording.

Research goals included mapping:
- forward/backward;
- turning;
- fire;
- use;
- weapon changes;
- map actions;
- timing/cadence;
- spawn/angle/collision fingerprints.

Recent status discussions rated DEMO highly understood statically, but authoritative timing/parity still benefits from live capture.

---

# 24. USER.SAV / save system

Save research has mapped large persistent runtime blocks.

Important result:
- full OBJECT blocks are saved;
- load rebuilds/rebases selected pointer/time fields;
- `OBJECT+0x18` cached projection value is preserved.

Known saved structures include:
- objects;
- guards;
- doors/wall-pairs;
- secret-panel activation state;
- push objects;
- projectiles;
- player/inventory/progression state;
- timing/deadline-related fields with post-load rebasing where required.

Relevant source:
- `Nitemare3D_save_animation_closure_2026-09-23.md`

---

# 25. BSF protection / registration

`nite3d.bsf` is not only text data. It also participates in DOS protection/registration behavior.

Confirmed DOS v1.9 dispatcher:
- selector `0..5`

Semantics:
- `0` read/decode/validate header and verify files
- `1` return registration/non-null state
- `2` distributor field
- `3` load/decrypt HELP/manual block
- `4` load/decrypt order/exit/purchase block
- `5` load/decrypt Episode-1 ending/transition block

Header size:
- **54 bytes**

Cipher/checksum:
- header/body XOR decoding with and 52-byte key family;
- checksum based on XOR accumulation;
- generic file checksum seed `0x7B`.

Protection behavior:
- EXE checksum always checked in the audited path;
- shareware additionally checks `MAP.1`;
- registered/full skips the shareware MAP.1 protection branch.

Registration state gates:
- access to later episodes;
- higher-episode save loading;
- cheat path;
- purchase/order UI behavior.

Key documents:
- `BSF_EXE_PROTECTION_RE_v2.md`
- `BSF_WIN16_RE_v3.md`
- `BSF_PROTECTION_RE_v4.md`
- `BSF_PROTECTION_RE_v5.md`
- `BSF_sample_inventory_v3.csv`

---

# 26. IMG format

Known IMG work:
- 10-byte header in the implementation work discussed;
- column-major pixel organization in checked loaders;
- image/sequence definitions connect graphics to walls, objects, enemies, HUD and effects.

Deep sequence-definition work exists:
- `Nitemare3D_SEQDEF_hlbkova_analyza_01_IMG1_wall_00-0F.md`
- `Nitemare3D_SEQDEF_hlbkova_analyza_02_IMG1_wall_10-1F.md`
- `Nitemare3D_SEQDEF_vsetky_IMG.csv`

AND safety document exists:
- `IMG_REBUILD_SAFETY.md`

Palette remains important because project notes originally lacked `GAME.PAL` in some supplied sets.

---

# 27. SND.DAT and audio

Research includes:
- MIDI;
- VOC;
- raw PCM handling;
- sound-event mapping;
- enemy SFX;
- weapon/impact/event sounds;
- Windows MMSYSTEM backend.

An experimental resource loader treated:
- SND descriptors as 6-byte entries;
- raw PCM conversion target as 8-bit mono WAV around 11025 Hz.

Important caution:
- earlier editor attempts produced audio that did not always sound identical to the original game;
- VOC parsing/export bugs were reported;
- therefore audio conversion must be validated against original playback.

Key source:
- `Nitemare3D_SND_DAT_detailna_mapa_Win16_2026-09-23.md`

---

# 28. UIF.DAT

UIF work covers:
- UI graphics/resources;
- possible embedded/related PCX-style assets;
- MIDI/VOC/resource references in experimental tooling;
- menu/HUD reconstruction.

Menu/HUD source family:
- `NITE3W_Menu_HUD_analyza_2026-09-25.md`
- `NITE3W_Menu_HUD_BINARNY_rozbor_2026-09-25.md`
- `NITE3W_Menu_HUD_Pass2...Pass7`
- `NITE3W_HUD_audit_2026-09-25.md`
- `NITE3W_All_Menus_Reconstruction.md`

---

# 29. ENDING.FLI

Project notes:
- `ENDING.FLI`
- **488 frames**
- observed chunk families:
  - `COLOR_64`
  - `BRUN`
  - `LC`
  - `BLACK`
  - `COPY`

Editor goals:
- export/import PNG/JPG/BMP;
- decode and reconstruct FLI frames correctly.

Older implementation work had reading/rebuild problems, with exact frame/chunk preservation should be tested before claiming bit-identical editing.

---

# 30. Video-based behavioral audit

AND video evidence corpus was analyzed for gameplay behavior.

Project status notes mention Episode 3:
- M1/M2/M7/M8/M9/M10 completed
- M3/M6 under analysis
- M4/M5 missing at that time

Library sources:
- `Nitemare3D_video_audit_2026-09-23.md`
- `Nitemare3D_video_event_index_2026-09-23.csv`
- `Nitemare3D_video_inventory_2026-09-23.csv`
- `E3M6_VIDEO_AUDIT.md`

Video evidence is behavioral support, not and substitute for raw code when exact integer/state semantics matter.

---

# 31. Current implementation-readiness view

Recent archived-chat status discussions around 2026-10-02 used approximately:

| Area | Reported status |
|---|---:|
| Player/movement | 100% |
| Collision | 99% |
| Doors / secret walls / USE / teleports | 100% |
| Renderer | 99% |
| Game loop | 94% |
| DEMO | 97% |
| USER.SAV | 93% |
| GUARD AI | 91% |
| Weapons | 90% |
| Projectiles | 88% |
| Death | 79% |
| Pain | 81% |
| Combat | 73% |
| Damage | 72% |
| OBJECT runtime | 71% |
| Runtime AI | 71% |
| Enemy state machine | 69% |
| Actor scheduler | 68% |
| Physics | 66% |
| Pathfinding | 64% |
| Engine scheduler | 63% |

These were project-state estimates, not byte-weighted proof.

The 2026-10-03 DOS closure passes improved static understanding further, especially:
- combat;
- projectile handling;
- damage/death;
- HUD/weapon;
- VGA/palette;
- renderer boundaries.

To not mechanically combine these older percentages with the pass-36 byte closure into one mathematically “exact” total.

---

# 32. Areas that still need runtime capture

Even with strong static closure, runtime capture remains useful for exact parity in:

- scheduler cadence and skipped-tick behavior;
- object-slot reuse and timing;
- selected GUARD state transitions;
- pathfinding corner cases;
- collision edge cases;
- projectile stale-cache scenario;
- door/panel animation timing;
- DEMO timing and platform differences;
- renderer pixel acceptance;
- save/load deadline timing;