# Nitemare 3-D — all-thread reverse-engineering consolidation

Date: 2026-09-22

This document is the canonical consolidation of the Nitemare 3-D findings accumulated across the reverse-engineering chats/sessions, supplied binaries/data, IDA/Ghidra exports, save-game audits, gameplay/video audits, official documentation and reconstruction experiments.

It does **not** replace the instruction-level subsystem reports. Instead it records the newest cross-thread state, corrects superseded assumptions, and links the detailed evidence files already in this repository.

## Evidence labels

Use these labels consistently:

- `VERIFIED_EXE` — direct original executable instruction/data-flow evidence.
- `VERIFIED_DATA` — direct original MAP/IMG/WALLS/OBJECTS/SND/UIF/GAME.PAL/FLI evidence.
- `VERIFIED_SAVE_LAYOUT` — direct USER.SAV/CONFIG.SAV layout evidence.
- `BEHAVIORAL` — directly observed in original gameplay/video.
- `INFERRED` — strong reconstruction from several facts, but not yet a direct named semantic.
- `PARTIAL` — field/path exists but its full meaning is not yet resolved.
- `TODO` — open target.

Do not turn old guesses, approximate percentages or OpenNitemare3D values into original-game facts.

---

# 1. Canonical Windows binary

Primary Windows target:

- `NITE3W.EXE` / Nitemare-3D for Windows V1.10.
- size: `230400` bytes.
- Win16 NE executable, 10 NE segments.
- SHA-256: `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.
- statically linked MFC/runtime framework; no external MFC DLL import.
- direct imported modules: `KERNEL`, `WING`, `DISPDIB`, `GDI`, `USER`, `KEYBOARD`, `COMMDLG`, `MMSYSTEM`, `SHELL`.
- `joystick.drv` is referenced dynamically.

The Windows executable is used as the most legible algorithm reference. DOS versions remain important for version-diff and platform-backend comparison, but similarity is never treated as proof that two routines are byte-for-byte/source-identical.

Detailed reports:

- `docs/SAVE_LIBRARIES_IDA_REPORT.md`
- `docs/GHIDRA_IDA_CROSS_AUDIT.md`
- `docs/EXE_FUNCTION_MAP.md`
- `analysis/nite3w_exe_deep_audit_2026-09-20.md`
- `analysis/nite3w_function_map.csv`

---

# 2. Important corrections to old assumptions

These corrections must be carried forward into every port/reimplementation:

1. **OBJECT is 28 bytes, not 80 bytes.**
   - base `0x6D66`;
   - maximum 350;
   - count `0x7E58`;
   - indexing uses `index * 0x1C`.

2. **GUARD is 26 bytes, not 98 bytes.**
   - base `0x93AE`;
   - maximum 100;
   - count `0x7E5E`;
   - indexing uses `index * 0x1A`.

3. **Visible wall span records are 20 bytes, not 52 bytes.**
   - base `0x5E88`;
   - count `0x5E7E`;
   - capacity 50;
   - stride `0x14`.

4. The renderer is **not Wolfenstein 3-D one-ray-per-column grid DDA**. It is a projected wall-vector/span renderer with per-column wall ownership and sprite occlusion.

5. `MAXVECLIST=333` is not the total vector count. There are four orientation-specific arrays of 333 far pointers; the actual vector pool is `MAXVEC=1000` records × 28 bytes.

6. MAP.1/2/3 containing 11/10/10 payloads does **not** prove a universal file-format ceiling of 10 levels. Historical MapEdit sources support a larger editor `MAX_LEVELS`; the exact original runtime archive ceiling remains a separate question.

7. `WARP_L1..L4` are colored-key locked wall/passage classes, not a generic teleport family.

8. `LEVEL_UP2` is explicitly a level-skip gateway.

9. `DOORVL2/VL3` and related suffixes distinguish graphical/environment door sets, not progressively stronger lock levels.

10. `ONE_SHOT` is the correct class name in the original definitions; old `ONE_SHOOT` spelling was wrong.

---

# 3. Original MAP archive and world model

Confirmed supplied archive geometry:

- map dimensions: `64 × 64` cells;
- each cell is two bytes: `{wallByte, objectByte}`;
- each level payload: `64 * 64 * 2 = 8192` bytes;
- archive header: 514 bytes;
- MAP.1: 11 payloads;
- MAP.2: 10 payloads;
- MAP.3: 10 payloads;
- E1M11 is the internal/demo map rather than a normal playable Episode-1 level;
- runtime world scale is 64 world units per tile (`coord >> 6`).

Player starts use object IDs 1..4 for four cardinal orientations; spawn location is tile center `x*64+32, y*64+32`.

The runtime mutates map/object state. USER.SAV contains an 8192-byte mutable MAP snapshot, and a verified E1M1 save differed from the original map only in moved object bytes.

`OBJECTS.*` and `WALLS.*` are primarily editor/definition catalogs. The installed DOS runtime set can operate with `MAP`, `IMG`, `SND.DAT`, `UIF.DAT`, `GAME.PAL`, demo/BSF data while `WALLS/OBJECTS` are absent; therefore the game executable contains/derives the actual runtime tables it needs.

Historical MapEdit findings:

- 64×64 map model confirmed in Pascal sources;
- MapEdit 7.2 `MAX_LEVELS=60` is an editor capacity, not proof of the game runtime limit;
- older symbol/object tables and graph types expose additional editor-side metadata useful for decoding `WALLS.*` / `OBJECTS.*`.

Detailed format notes:

- `docs/FORMAT_NOTES.md`
- `docs/DATA_MANIFEST.md`
- `docs/DEMO_FORMAT_RE.md`

---

# 4. Runtime fixed capacities and arrays

Direct boundary checks in the original EXE establish:

| Runtime family | Capacity | Stride / record |
|---|---:|---:|
| Doors | 64 | 22 B |
| Panels | 32 | 22 B |
| Pushes | 12 | 6 B |
| Images | 70 | slot/resource table |
| Objects | 350 | 28 B |
| Guards | 100 | 26 B |
| Vectors | 1000 | 28 B |
| VECLIST per orientation | 333 | 4-byte far pointers |
| Visible wall spans | 50 | 20 B |
| Projected sprite commands | 100 | 18 B |

Important bases:

- OBJECT `0x6D66`, count `0x7E58`;
- GUARD `0x93AE`, count `0x7E5E`;
- doors `0x9DD6`;
- panels `0xA356`;
- pushes `0xA616`;
- wall-span count `0x5E7E`, array `0x5E88`;
- projected sprite queue `0x6270`.

The original error strings independently expose dedicated families: `Door not in map`, `Push not in map`, `Guard not in map`, `Object not in map`, `Vector not in map`, `MAXDOORS exceeded`, `MAXPANELS exceeded`, `MAXPUSHES exceeded`, `MAXIMAGE exceeded`, `MAXSEG exceeded`, `MAXOBJ exceeded`, `MAXGUARD exceeded`, `MAXVECLIST exceeded`, `MAXVEC exceeded`.

---

# 5. Player movement, collision and interaction

Confirmed player/world anchors:

- player world X `0x4BF6`;
- player world Y `0x4BF8`;
- current tile X/Y `0x4BF2/0x4BF4`;
- world-to-tile uses shift by 6;
- collision AABB half extent: 27 world units;
- a separate threshold of 42 world units exists in proximity/occupancy logic; exact high-level role remains `PARTIAL`.

Motion is subdivided into small integer steps and X/Y collision is handled separately, yielding wall sliding instead of an all-or-nothing diagonal rejection.

Input bits recovered from DEMO/runtime work include:

- `0x0002` forward;
- `0x0004` backward;
- `0x0008` / `0x0010` turn directions;
- `0x0020` fast/double movement/turn modifier;
- `0x0040` secondary increment/reset behavior, exact high-level label still partial;
- `0x0080` FIRE;
- `0x0100` strafe modifier;
- `0x0200` USE/ACTION.

USE is rising-edge triggered and resolves one adjacent cardinal cell.

See:

- `docs/PLAYER_COLLISION_RE.md`
- `docs/USE_INTERACTION_RE.md`
- `docs/SPECIAL_WALL_USE_RE.md`
- `docs/PUSHABLE_RE.md`

---

# 6. Doors, panels, pushes, warps and wall classes

Confirmed runtime records:

- doors: 64 × 22 B, base `0x9DD6`;
- panels: 32 × 22 B, base `0xA356`;
- pushes: 12 × 6 B, base `0xA616`;
- push class `0x28`;
- push movement: 8 updates × 8 world units = exactly one 64-unit tile.

Confirmed/strong original WALLS definition meanings:

- `WARP_L1..L4`: red/green/blue/yellow locked passage/wall families;
- `WARP_1..8`: paired stair/dumbwaiter/vertical-connection groups;
- `WARP_E1`, `WARP_E2`: elevator groups;
- `WARP_S1`: swirling mirror in Bedroom 4;
- `WARP_S2`: broken mirror / Other Side mirror;
- `DOORV`, `DOORH`: vertical/horizontal orientations of the same sliding-door family;
- `DOORVL/HL`, `VL2/HL2`, `VL3/HL3`: locked-door orientations across different graphical/environment sets;
- `DOORVI/HI`: Transportation Chamber door orientations;
- `DOORVR/HR`: remote-controlled doors;
- `DOORVC/HC`: curtain doors;
- `JAMB`: door jamb;
- `CONTROL`: numbered control panel class;
- `LEVEL_UP`: normal next-level gateway;
- `LEVEL_UP2`: skip-a-level gateway;
- `WALL_EX1`: explodable wall/door/hedge/target family;
- `WALL_EX2`: Episode-3 exploding-door variants;
- `ONE_SHOT`: disappearing gargoyle wall family;
- `SPECIAL1`: E1 kitchen fuse box + morphing chalkboard data uses;
- `ACTIONSPOT`: dancing-guard action marker;
- `TRIGGER1/2`: invisible trigger markers;
- `RETREAT`, `TURN`, `FLEE`: AI/navigation control markers;
- `SAFESPOT`: safe-combination markers.

Known safe combinations from original data/comments include `333`, `01532`, `080993`, `372535`.

Still unresolved at exact instruction/field level:

- full 22-byte door/panel layouts;
- exact `CONTROL` command-state mapping;
- exact `ONE_SHOT` activation path;
- full `SPECIAL1` dispatcher;
- complete mirror/pentagram condition state;
- exact ID-card consumption/transport-chamber logic;
- precise `REVWALL` semantics.

---

# 7. Renderer — current canonical reconstruction

The newest renderer audit supersedes the older statement that MAP→VEC and VECLIST construction were unknown.

## 7.1 High-level pipeline

```text
MAP 64x64
  -> extract exposed tile boundaries
  -> merge adjacent compatible edges
  -> VEC[0..999], 28 B each
  -> distribute pointers into 4 orientation VECLIST[333]
  -> sort horizontal lists by Y / vertical lists by X
  -> per frame: traverse candidates
  -> world->camera transform + near clipping
  -> perspective-project VEC endpoints
  -> owner[x] = winning VEC far pointer
  -> coalesce equal owner runs into <=50 wall spans
  -> fill ceiling/floor
  -> textured wall-column rasterization
  -> update per-column wall silhouette/occlusion values
  -> project/cull world objects
  -> place <=100 projected sprite commands
  -> sprite draw clipped/occluded by wall column data
  -> WinG framebuffer presentation
```

This is a 2.5D vector/segment renderer, not a BSP engine and not Wolf3D's direct per-screen-column tile DDA.

## 7.2 MAP -> VEC producer

`FUN_1018_4370` invokes `FUN_1018_4046` four times for orientations 0..3.

`FUN_1018_4046` scans the 64×64 map, detects exposed wall boundaries and merges adjacent compatible edges. It enforces `MAXVEC=1000` and indexes VEC records by `0x1C`.

Orientation geometry:

- 0: `(x,y) -> (x+64,y)` top horizontal edge;
- 1: `(x,y+64) -> (x+64,y+64)` bottom horizontal edge;
- 2: `(x+64,y) -> (x+64,y+64)` right vertical edge;
- 3: `(x,y) -> (x,y+64)` left vertical edge.

A helper extends compatible vectors by one 64-unit tile.

## 7.3 VEC layout

28-byte record; high-confidence layout:

```text
+00 wallId
+01 texture/offset-like byte                 PARTIAL
+02 animation auxiliary byte                PARTIAL
+03 animation frame/subindex                STRONG
+04 texture/resource-set index              STRONG
+05 flags
+06 renderClass
+07 orientation 0..3                        VERIFIED_EXE
+08 dword timer/runtime value               PARTIAL
+0C x1                                      VERIFIED_EXE
+0E y1                                      VERIFIED_EXE
+10 x2                                      VERIFIED_EXE
+12 y2                                      VERIFIED_EXE
+14 projected screenX1                      VERIFIED_EXE
+16 projected Y1 / scale-like Q4 value      VERIFIED_EXE
+18 projected screenX2                      VERIFIED_EXE
+1A projected Y2 / scale-like Q4 value      VERIFIED_EXE
```

Known/strong flag uses:

- `0x01`: active/renderable path;
- `0x04`: special boundary/merge behavior — semantic name open;
- `0x08`: special geometry/wall behavior — semantic name open;
- `0x10`: masked/transparent/sprite-occlusion-related special behavior — partial;
- `0x20`: texture-U flip — high confidence.

`renderClass` values `2`, `0x3F`, `0x40` receive special renderer branches; exact WALLS names must remain separately mapped from property/definition tables.

## 7.4 Four VECLIST arrays

Counts:

- `0x697A`, `0x697C`, `0x697E`, `0x6980`.

Pointer-list bases:

- `0x6982`, `0x6EB6`, `0x73EA`, `0x791E`.

List spacing is `0x534 = 333 * 4`, proving 333 far pointers per orientation list.

Horizontal VEC lists are sorted by Y; vertical lists are sorted by X.

## 7.5 Viewport and per-column structures

Frame buffer:

- 320×200;
- 8-bit indexed;
- 64,000-byte WinG DIB.

Normal 3-D viewport:

- x 8..311;
- y 4..155;
- 304×152;
- center `(160,80)`;
- center Y Q4 = `1280`.

Column owner table:

- base `0x53FE`;
- 320 entries;
- 4-byte far pointer each;
- exactly ends at `0x58FE`.

Wall silhouette/occlusion table:

- base `0x58FE`;
- 320 × 2-byte values;
- written by wall rasterization and read by sprite/object occlusion;
- do not call it a conventional metric Z-buffer unless a later audit proves those units.

Visibility traversal can stop early when every active viewport column has an owner.

## 7.6 Wall spans

`FUN_1010_6266` converts owner runs to records at `0x5E88`:

- stride `0x14 = 20` bytes;
- count at `0x5E7E`;
- capacity 50.

The span stores a VEC pointer, X endpoints, projected endpoint/interpolation values and a 32-bit increment/accumulator used across columns.

## 7.7 Projection

`FUN_1010_E516` normalizes view angle to 0..359 and uses 45-degree sectors.

`FUN_1010_E798`:

- subtracts player world coordinates from VEC endpoints;
- performs integer camera transform using recovered direction/trig globals;
- near-clips segment endpoints instead of simply discarding a segment with one endpoint behind;
- writes projected X and Q4 vertical values into VEC `+14..+1A`.

Near-plane/clamp constant: `0x4000`.

Dynamic projection globals are prepared by `FUN_1010_E4B2` around `0x3A6A/0x3A6E/0x3A72/0x3A76`. A conventional interpretation of the recovered normal viewport constants gives an approximately 81-degree horizontal FOV; this is a mathematical reconstruction, not a literal named `FOV=81` setting in the executable.

## 7.8 Wall and sprite raster paths

Frame chain:

```text
3:D78C / corresponding Ghidra frame orchestrator
  -> 4:3940 visibility traversal
  -> 3:6266 owner->span coalescing
  -> 3:3DB8 ceiling/floor
  -> 3:66B0 wall rasterization
  -> 3:6348 object integration/order
  -> 3:6914 sprite-command consumption
```

Wall path uses `FUN_1010_EBD6` + `FUN_1010_6422` for perspective/orientation/texture-U work and `FUN_1010_3E44 -> 3:366A` for the WinG column blitter.

The wall texture-column source path is 64 samples high. VEC flag `0x20` affects U direction; render classes `0x3F/0x40` also alter special mapping logic.

Projected sprite queue:

- base `0x6270`;
- 100 records;
- stride `0x12 = 18` bytes;
- `FUN_1010_CC7C` projects/culls and inserts records;
- if no bucket/neighbor slot is free the original emits `Too many objects on screen`;
- `FUN_1010_6914` consumes the queue.

Sprite transparency in the recovered WinG path uses palette index `0x29`.

Highest-value renderer TODOs now are **not** basic architecture. They are:

1. complete camera/vector/span scene integration and original-frame pixel comparison;
2. finish special-wall/resource cases in `FUN_1010_6422`;
3. complete lower wall-column blitter/alternate VGA path in `FUN_1010_3E44` and callees;
4. finish wall-animation/resource mapping beyond the recovered `FUN_1010_65A6` update flow;
5. validate alternate floor/ceiling modes in `FUN_1010_3DB8`;
6. validate shade override bounds and runtime output for `0x7E60`;
7. all writes to VEC `+01/+02/+03/+04/+08`;
8. class-by-class WALLS -> property flags -> renderClass -> texture descriptor mapping.

See the updated `analysis/nite3w_renderer.md`.

---

# 8. GUARD record, AI state machine and score

## 8.1 GUARD record

Verified 26-byte layout anchors:

```text
+02 dword timestamp/time
+06 timer
+08 associated OBJECT slot/index
+0A strategy
+0B state
+0C next_state
+0D o_id
+0E definition lookup result                  PARTIAL
+0F sync/control boolean                      PARTIAL
+10 strength / HP
+11 octant
+12 resoct / result-octant field
+13 transition parameter                      PARTIAL
+16 transition/control flag                   PARTIAL
```

Fresh normal GUARD creation writes `strength = 0xFF` (255). Direct write audit found normal/special creation writes of 255, lethal clear to 0 and non-lethal subtraction. Do not invent separate per-enemy initial HP values without new evidence.

## 8.2 State dispatcher

The dispatcher accepts states `0x00..0x15` (22 states). State `0x15` is the confirmed pain/hit reaction state and returns to `next_state` after its animation/timer logic.

Current handler map:

| State | Handler | Current recovered role |
|---:|---:|---|
| 00 | 7BA2 | animation/timer then `state=next_state` |
| 01 | 7BE0 | timer countdown then 02 |
| 02 | 7BFA | active AI/animation with type-3 sound path |
| 03 | 7C3C | detection/transition branch |
| 04 | 7C86 | alternate detection/attack branch |
| 05 | 7CE4 | helper transition |
| 06 | 7CEC | movement + timer then 03 |
| 07 | 7D2A | active AI; strategy 3 has a special branch |
| 08 | 7D7E | movement/AI; can enter 02 |
| 09 | 7DEC | special/collision action |
| 0A/0B | 80A4 | no local action in dispatcher |
| 0C/0D | 7E54 | shared handler |
| 0E | 7E6C | conditional transition to 0F |
| 0F | 7E9E | timer/action; 10 or 0E |
| 10 | 7F26 | timer then back to 0F |
| 11 | 7F8E | movement + timer then `strategy=0,state=07` |
| 12 | 7FEE | wait for timer/animation, then `state=next_state` |
| 13 | 8038 | helper transition |
| 14 | 804A | long timer + periodic action |
| 15 | 807E | confirmed pain/hit animation, return to next_state |

High-level names for states 02..14 remain intentionally conservative.

## 8.3 Score table

The score function uses internal class/type values corresponding to GUARD1..25. Verified points:

| Guard | Name | Score |
|---:|---|---:|
| 1 | Bat | 25 |
| 2 | Frankenstein | 75 |
| 3 | Mummy | 50 |
| 4 | Skeleton | 100 |
| 5 | Mrs H. | 250 |
| 6 | Zelda | 150 |
| 7 | Vampira | 200 |
| 8 | Baddie #1 | 100 |
| 9 | Baddie #2 | 100 |
| 10 | Dracula | 0 |
| 11 | Cemetery Gargoyle | 150 |
| 12 | Garden Gargoyle | 150 |
| 13 | unknown / apparently unused identity | 200 |
| 14 | Penelope | -1000 |
| 15 | Dr. Hamerstein | 1000 |
| 16 | Tall slim robot | 100 |
| 17 | Trashcan robot | 200 |
| 18 | Cannon | 0 |
| 19 | Ghost | 25 |
| 20 | Goldie | 100 |
| 21 | Greenie | 100 |
| 22 | Demon | 250 |
| 23 | Alien #1 | 250 |
| 24 | Alien #2 | 200 |
| 25 | unknown / apparently unused identity | 50 |
| 26 | Dancers | default 0 path; outside the score switch |

Dracula's score being zero is therefore real in the score switch; his scripted behavior/death transformation must be analyzed separately rather than "correcting" the score to a guessed value. The gameplay/script evidence indicates Dracula can transform into a Bat, whose own score value is 25.

E1M9 contains the special GUARD26 dancer sequence; this is not a normal score-switch enemy family and requires its own script/AI reconstruction.

Detailed GUARD docs:

- `docs/GUARD_AI_RE.md`
- `analysis/nite3w_guard_record.md`
- `analysis/nite3w_ai_state_machine.md`

---

# 9. Combat, weapons and difficulty

Active weapon selector at `0x4C23`:

- 0 Single Shot Laser;
- 1 Magic Wand;
- 2 Silver Pistol;
- 3 Continuous Laser;
- `0xFF` none/unset.

Ammo globals:

- Silver `0x4C1F`;
- Laser `0x4C20` shared by weapons 0 and 3;
- Wand `0x4C44`.

Verified ammo behavior:

- ordinary pickup increment 20;
- forced/set value 50;
- intended gameplay threshold/display cap 100;
- Silver/Laser contain a real signed-byte comparison/display quirk: 127 is the highest positive signed-byte value before 0x80..FF become negative to those paths;
- Wand uses unsigned comparison in the audited cap path.

Player health:

- global `0x4C1D`;
- initialized/capped to 100;
- normal lethal damage saturates to zero and enters death state instead of underflowing;
- Omnipotent bypasses normal damage.

Player -> GUARD damage producer:

- derives a signed geometry/projected-base value;
- adds `random()%25`;
- dispatches on enemy/object class;
- applies literal class/weapon shifts/divisions, including `/2`, `/4`, `/8`, `/16`, `/256`, zero-damage branches and special branches;
- final high-end clamp 255;
- exact matrix is preserved in `docs/COMBAT_DAMAGE_RE.md`.

Difficulty global `0x4C14` is independently constrained by three systems:

| Value | Player -> enemy | Enemy -> player | GUARD timers |
|---:|---:|---:|---:|
| 0 | ×2 | ÷2 | slower / doubled |
| 1 | ×1 | ×1 | baseline |
| 2 | ÷2 | ×2 | faster / halved |

Thus value ordering is easier / baseline / harder even if exact menu wording remains to be tied to its setter.

Weapon jam:

- global `0x4C2E`;
- firing path blocks when nonzero and displays `Your weapon appears to be jammed!`;
- Episode-1 level-9 script events `0x47`/`0x48` set/clear the jam;
- both transitions call SFX ID 68;
- there is no evidence that this is a random gun-jam probability.

See:

- `docs/COMBAT_DAMAGE_RE.md`
- `docs/PLAYER_HEALTH_RE.md`

---

# 10. Cheats, debug keys and developer diagnostics

Official four cheat modes:

- Omniscient — automap/monster-map power support; F9/F10 remain explicit toggles;
- Omnipotent — all weapons, infinite ammo maintenance, invulnerability;
- Omnificent — enemies generally ignore player until hostile action/fire;
- Omnifarious — grants collectible puzzle/access items including weapons, keys, ID cards and Pentagrams.

Confirmed/common key paths include:

- 1..4 weapon selection;
- F2/F3 music/SFX controls;
- F4/F5 quick load/save;
- F9/F10 wall/enemy automap toggles;
- TAB status/debug-related screen path;
- Alt+Enter behavior in Windows build;
- Shift-plus health/debug regeneration/increment behavior has executable support, though exact branch-to-physical-key labeling should remain conservative where not fully traced.

No Quake-style text console was found. Developer/debug infrastructure includes `debug.txt`, runtime vector/object/guard statistics and diagnostic strings such as class/strength/strategy/state/nextstate/timer/octant/resoct.

`CONFIG.SAV` is 20 bytes and includes settings/cheat state fields under ongoing semantic mapping.

See `docs/RE_AUDIT_CHEATS_AUDIO.md` and `docs/MENU_INSTRUCTIONS_CHEATS.md`.

---

# 11. SND.DAT, MIDI and audio

Direct parse of the Windows SND.DAT:

- fixed directory: 960 bytes = 160 records × 6 bytes;
- record: `{uint16 length, uint32 offset}` little-endian;
- ID 0: IBK instrument bank;
- IDs 1..15: Standard MIDI Type 1;
- IDs 16..33: reserved/empty;
- IDs 34..110: 77 logical SFX IDs, 72 containing PCM data;
- empty SFX placeholders: 62,72,75,76,77;
- 69/70 alias one PCM block;
- 73/74 alias one PCM block;
- entry 111 is the zero-length end sentinel whose offset equals archive size;
- remaining directory slots are unused/zero.

Original SFX playback format from `WAVEFORMAT`:

- PCM;
- mono;
- 11025 Hz;
- 8 bit;
- 1-byte block align.

This is why a generic VOC interpretation/extractor can sound wrong for the Windows archive. The original Windows runtime uses MCI/MIDI and waveaudio, while old DOS variants may use different sound-resource encodings.

Current semantic SFX mapping is incomplete and must keep secondary labels separate from direct EXE xrefs. The repository's `analysis/snd_index_audit.csv` is the container/index source of truth.

---

# 12. UIF.DAT, IMG.*, GAME.PAL and ENDING.FLI

## GAME.PAL

The canonical palette is the 768-byte 256×RGB PCX-style palette payload. Recovered defaults include:

- floor palette index `0x0C`;
- ceiling palette index `0x11`.

These indices are also stored at the tail of USER.SAV.

## IMG.1/2/3

Prior archive work established indexed image/sequence content and original episode-specific identity. Known resource work includes 64×64 and 128×64 wall/door/animated assets; 128×64 often represents two adjacent 64-wide variants in source material, but each runtime renderer assumption must be tied to the exact resource path rather than generalized to every image.

The renderer's recovered wall-column core consumes 64-sample texture columns for the audited path.

## UIF.DAT

UIF is a fixed directory/container of UI-oriented images/resources. Complete per-ID semantic binding remains unfinished; do not assume unused entries are definitely dead until original call sites are audited.

## ENDING.FLI

Original finale asset:

- FLIC/FLI family;
- 320×200;
- header reports 488 frames;
- FFmpeg can expose 489 decoded frames because of ring/repeat-frame behavior;
- nominal timing about `70/9` fps (~7.78 fps), around 62.7 seconds from header timing.

The E3M10 video audit confirms the original FLI follows the boss/finale flow; editorial captions added by walkthrough videos are not part of the original asset.

Open issue: exact FLI ring-frame/chunk compatibility in the custom editor must preserve original chunk semantics rather than merely matching decoded frame count.

---

# 13. DEMO format

Confirmed:

- 6-byte header;
- 8-byte records;
- record structure: `eventByte:u8, inputMask:u16, pad:u8, timestamp:u32`;
- playback stores timed inputs, not absolute player positions;
- `-r` enables recording in the audited build family;
- supplied DEMO.1 matches E1M11 demo behavior.

DEMO.2/.3 origin/episode meaning must not be guessed solely from suffix numbers.

---

# 14. USER.SAV / CONFIG.SAV

USER.SAV slot size: `0xD6E7 = 55,015` bytes.

Important offsets:

- `0x0004` description;
- `0x002D` episode;
- `0x002F` zero-based level;
- `0x0031` saved tick;
- `0x0035` mutable 8192-byte MAP;
- `0x2035` 94-byte gameplay/global block;
- `0x2093` 28,000-byte vector pool = 1000×28;
- `0x8DF3` 9,800-byte object pool = 350×28;
- `0xB43B` 2,600-byte GUARD pool = 100×26;
- `0xBE63` 1,408-byte door pool = 64×22;
- `0xC403` 336-byte player-projectile pool = 8 × 42-byte records;
- `0xC55B` 72-byte push array = 12×6;
- `0xD6E3` floor palette byte;
- `0xD6E4` ceiling palette byte;
- `0xD6E5` 16-bit shade-level index mirroring runtime `0x7E60`; default index 2, scripted dark mode index 6; shade table `[0,4,8,12,16,20,30,40]`.

Important unresolved save regions also include smaller auxiliary blocks and a 4096-byte state/visibility-like block. Loading performs pointer reconstruction and timer rebasing; the save is not a naive dump where every stored pointer remains valid.

CONFIG.SAV is 20 bytes.

See `docs/SAVE_LIBRARIES_IDA_REPORT.md`.

---

# 15. BSF / registration / version-diff findings

The game contains registration/shareware strings such as `Registered Software`, `UNREGISTERED SHAREWARE!`, `Registered to:`, `Distributed by:` and complete-trilogy/shareware gating.

`NITE3D.BSF` participates in an integrity/registration-style check and the executable contains `%s corrupted`-style failure text. Current evidence does **not** support claims of serial-number, CD or online DRM.

Audited BSF variants/sizes from version-comparison work:

### DOS shareware

- 1.0: 14,741 B
- 1.7: 15,513 B
- 1.8: 15,513 B
- 1.9: 15,800 B
- 2.0: 15,792 B

### Windows shareware

- 1.3: 14,896 B
- 1.6: 15,447 B
- 1.8: 15,437 B

### Full

- DOS full: 10,250 B
- Windows full: 10,370 B

Version-diff observations:

- DOS 1.7 and 1.8 are effectively identical from offset `0x10` onward in the audited BSF set;
- DOS 1.9/2.0 share a large common body;
- Windows 1.6/1.8 share a large common body;
- DOS vs Windows BSF payloads are substantially different, so platform identity must be preserved.

Exact byte-by-byte BSF verification algorithm and all six `nite3d.bsf` xref parent functions remain a dedicated reverse-engineering target.

---

# 16. Hidden, unused and special content

Known or strongly indicated special/hidden content:

- E1M11 is an internal/demo map and should not be treated as a normal Episode-1 progression level.
- GUARD13 and GUARD25 have score-switch entries but their final visible identity/use remains unresolved.
- GUARD26 Dancers is a special script/AI family and is outside the normal GUARD1..25 score switch.
- E1M9 radio/action-spot dancer sequence is scripted; dancers can transition into ordinary enemy actors in gameplay.
- exploding-wall families include dedicated runtime/error paths.
- one-shot disappearing gargoyles are present in definition data.
- special mirror/Other Side progression and four-pentagram conditions exist.
- remote-door and remote-cannon command strings exist.
- weapon-jam events are scripted.
- an undefined wall `0x37` was found in supplied E2M4 data at `(61,54)` and should be treated as an original data quirk until proven otherwise.
- prior tests also found a `MAXVECLIST` off-by-one/two-byte overwrite quirk in the original path; compatibility work should document rather than casually reproduce memory corruption.

The executable has many debug/diagnostic strings and branches, but no evidence yet supports a hidden full developer console.

---

# 17. Episode/video audit state

Durable repository reports cover Episode 1/2 material and substantial Episode 3 behavior, including dedicated reports for E3M3/E3M4/E3M5/E3M6 and the extended/finale work.

Important E3 findings include:

- remote-door/control behavior evidence;
- reusable colored keys in video evidence;
- pushable tombstones as a general mechanic;
- fire hazard categories;
- Mirror of Destiny / Other Side progression;
- E3M10 dedicated finale path: stairs/navigation -> trigger -> Penelope + Dr. Hamerstein encounter -> victory popup -> `ENDING.FLI` -> final completion screen.

Where a walkthrough contains cuts/overlays, the video report must keep those coverage limitations explicit.

---

# 18. External source comparison policy

Released id Software-era code is useful for orientation and naming patterns but not proof of Nitemare 3-D implementation identity.

Useful comparisons include:

- Catacomb 3-D / Catacomb Abyss wall-list lineage;
- Hovertank 3-D wall tracing/list construction;
- Wolfenstein 3-D input, doors, pushwalls and contrasting per-column DDA;
- Blake Stone and other Wolf-derived projects for entity/game-loop comparison.

The recovered NITE3W renderer remains authoritative where it differs.

---

# 19. Highest-priority unresolved work after this consolidation

## P0 — blocks 1:1 gameplay reconstruction

1. Full wall-class numeric dispatcher: `wall ID/class -> flags -> handler`.
2. Animated-wall sequence timing: distinguish frame count, sequence ID and tick delay; decode `FUN_1010_65A6`.
3. Door/panel/control 22-byte field semantics and trigger/remote-door state machine.
4. Complete GUARD states 02..14 with exact animation/sound/action names.
5. Guard movement speed/cadence and full attack timing.
6. Enemy-to-player class table mapped to visible names and projectile/melee identities.
7. Player projectile pool/record, impact state, guard collision tolerance and render culling are mapped. Remaining: calibrated movement/time units, enemy-projectile identity/ownership, and DOS cross-check.
8. Exact special mirror/pentagram/finale state variables.

## P1 — renderer fidelity

1. full camera/vector/span integration and deterministic original-frame comparison.
2. remaining `FUN_1010_6422` special-wall/resource mapping.
3. `FUN_1010_3E44` / `3:366A` lower blitter and alternate translation/VGA behavior.
4. shade override bounds and exact floor/ceiling fill regions for `0x7E60` / `0x7E62` / `0x7E63`.
5. VEC animation/resource fields `+01/+02/+03/+04/+08`.
6. exact `0x58FE` unit semantics.
7. masked walls/curtains/grates and sprite occlusion interaction.

## P1 — file formats/save

1. complete MAP 514-byte header/directory semantics;
2. full `WALLS.*` secondary attribute-column bit layout;
3. full `OBJECTS.*` attribute-code grammar;
4. sequence-definition format/timing/events;
5. remaining USER.SAV semantics and pointer reconstruction (the `0xC403` projectile pool is resolved);
6. timer rebasing details.

## P2 — resource/audio/UI

1. exact remaining SFX event map from EXE xrefs;
2. MIDI ID -> menu/level table;
3. UIF per-ID semantics;
4. exact ENDING.FLI ring-frame/chunk writer compatibility;
5. joystick calibration/dead-zone/scaling;
6. platform differences among DOS/Windows SND/IMG resource variants.

---

# 20. Source-of-truth document map

Use this consolidation as the entry point, then drill down:

- `docs/CROSS_THREAD_RE_LEDGER.md` — earlier cross-thread ledger.
- `analysis/nite3w_renderer.md` — renderer architecture and instruction anchors.
- `docs/GUARD_AI_RE.md` — GUARD layout/AI/hit receiver.
- `docs/COMBAT_DAMAGE_RE.md` — player-to-GUARD damage matrix, ammo, jam.
- `docs/PLAYER_HEALTH_RE.md` — health and enemy-to-player damage.
- `docs/PLAYER_COLLISION_RE.md` — collision/movement.
- `docs/USE_INTERACTION_RE.md` — USE behavior.
- `docs/SPECIAL_WALL_USE_RE.md` — special walls/keys/cards.
- `docs/PUSHABLE_RE.md` — pushable mechanics.
- `docs/DEMO_FORMAT_RE.md` — DEMO format.
- `docs/SAVE_LIBRARIES_IDA_REPORT.md` — save layout + Win16 libraries.
- `docs/RE_AUDIT_CHEATS_AUDIO.md` — cheats + SND.DAT/MIDI/SFX.
- `docs/VIDEO_AUDIT_*` — gameplay/video behavior.
- `src/game/RecoveredRuntime.hpp` — compile-time values that are safe to expose to reconstruction code.

Any future finding should update this file only after its subsystem report/evidence has been captured, so the master ledger remains conservative rather than becoming another speculation list.



---

## 2026-09-23 projectile/save/hazard addendum

The current findings are summarized in [PROJECT_FINDINGS_DELTA_2026-09-23.md](PROJECT_FINDINGS_DELTA_2026-09-23.md). This supersedes earlier open-list entries that described USER.SAV +0xC403 as unknown and treated the projectile ±20 render check or shade index as unresolved. The 2026-09-23 update maps the player projectile pool, fire damage-per-update values, SECRET-panel/Cannon flags, guard wake cache, automap buffer roles, color remap table, and shade lookup. Runtime timings, other-build differences, scene equivalence, and residual save-field semantics remain open.
