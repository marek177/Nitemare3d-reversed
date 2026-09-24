# Cross-thread Nitemare 3-D reconstruction ledger

Updated: 2026-09-22

This ledger is a compact index of findings recovered across the Nitemare 3-D reverse-engineering threads. The canonical full consolidation remains:

- [`ALL_THREADS_CONSOLIDATION_2026-09-22.md`](ALL_THREADS_CONSOLIDATION_2026-09-22.md)
- [`PROJECT_FINDINGS_DELTA_2026-09-22.md`](PROJECT_FINDINGS_DELTA_2026-09-22.md) — newest same-day corrections/findings after the original consolidation

Subsystem documents remain authoritative for instruction-level evidence. Exact values are promoted only when backed by original executable/data/save evidence.

## Binary target

- NITE3W.EXE V1.10: 230,400 bytes; Win16 NE; 10 segments.
- SHA-256: `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.
- Direct imported modules: KERNEL, WING, DISPDIB, GDI, USER, KEYBOARD, COMMDLG, MMSYSTEM and SHELL.
- `joystick.drv` is dynamically referenced.
- Ghidra/IDA function/XREF counts are analysis worksets, not a final count of original game functions because runtime/MFC/library code remains mixed in.

## Original data formats

- MAP.1 has 11 supplied payloads; MAP.2 and MAP.3 have 10 each.
- Each level is 64×64×2 = 8192 bytes after a 514-byte archive header.
- Each MAP cell is `{wallByte, objectByte}`.
- E1M11 is the internal/demo map.
- Runtime world coordinates use 64 units per tile and `coord >> 6` for world-to-tile conversion.
- The supplied 11/10/10 payload counts are not treated as a proven universal MAP-format ceiling; historical MapEdit sources support a larger editor level count.
- IMG archives contain indexed image/sequence data; episode-specific identity must be preserved.
- UIF.DAT is a UI-resource container whose complete per-ID semantics remain partial.
- SND.DAT uses a 160×6-byte directory. IDs 1..15 are MIDI; the audited Windows SFX path uses raw 8-bit mono PCM at 11025 Hz.
- DEMO uses a 6-byte header followed by 8-byte timed input records.
- GAME.PAL supplies the original 256-color indexed palette.
- ENDING.FLI is 320×200; header frame count 488, with some decoders exposing a ring/repeat frame as 489.
- OBJECTS.1-3 and WALLS.1-3 are primarily editor/definition assets; runtime behavior is reconstructed from EXE/MAP/IMG/property tables and does not require those files to remain present at runtime.

## Corrected original runtime record sizes

Direct EXE indexing and USER.SAV block sizes supersede older arithmetic guesses:

| Family | Base | Capacity | Stride |
|---|---:|---:|---:|
| OBJECT | `0x6D66` | 350 | 28 B |
| GUARD | `0x93AE` | 100 | 26 B |
| door | `0x9DD6` | 64 | 22 B |
| panel | `0xA356` | 32 | 22 B |
| push | `0xA616` | 12 | 6 B |
| VEC | runtime vector pool | 1000 | 28 B |
| wall span | `0x5E88` | 50 | 20 B |
| projected sprite | `0x6270` | 100 | 18 B |

Old OBJECT=80 B, GUARD=98 B and wall-span=52 B notes are obsolete.

## MAP -> runtime object pipeline

The executable constructs two 256-entry property tables:

- wall properties at DS `0x7E94[wallByte]`;
- object properties at DS `0x7F94[objectByte]`.

Confirmed wall bits used by gameplay:

- `0x04`: hard blocking;
- `0x08`: dynamic door path;
- `0x40`: level-script/touch hook.

Confirmed object bits:

- `0x01`: instantiate runtime OBJECT;
- `0x02`: blocks movement;
- `0x04`: special/touch handler;
- `0x08`: creates GUARD.

OBJECT `+06` is the runtime class used by combat and behavior dispatch. Guard-producing OBJECTs link to GUARD entries through recovered index fields.

Additional OBJECT anchors:

- `+10/+12`: world X/Y;
- `+14/+16`: render/spatial-ordering fields, semantic PARTIAL;
- `+18`: projected/view-space vertical baseline consumed by the player->GUARD damage producer; not world Y.

A separate 4096-byte 64×64-sized runtime cell-state/visibility-like block is now a high-confidence structural target. Exact per-cell bit semantics remain PARTIAL.

## Player movement/collision

- player world X/Y at `0x4BF6/0x4BF8`;
- current tile X/Y at `0x4BF2/0x4BF4`;
- collision AABB half-extent 27 world units;
- incremental integer movement with X/Y collision tested separately, yielding wall sliding;
- separate threshold 42 exists in proximity/occupancy logic; exact role PARTIAL;
- changing tile dispatches event `0x16`.

Recovered input-mask anchors:

- `0x0002` forward;
- `0x0004` backward;
- `0x0008/0x0010` turning directions;
- `0x0020` faster/doubled movement or turn increment;
- `0x0040` increment/reset-related behavior, high-level label PARTIAL;
- `0x0080` FIRE;
- `0x0100` strafe modifier;
- `0x0200` USE/ACTION.

Important distinction: tile-change event `0x16` is a walk-over/tile-transition path and is separate from rising-edge USE input `0x0200`.

## USE / doors / panels / pushables / wall classes

- USE is rising-edge triggered and resolves one adjacent cardinal cell.
- Pushables use runtime class `0x28` and move 8×8 = 64 world units per full push.
- `WARP_L1..L4` are red/green/blue/yellow key-locked wall/passage classes, not generic teleport functions.
- `WARP_1..8` are paired stair/dumbwaiter/vertical-connection groups.
- `WARP_E1/E2` are elevator groups.
- `WARP_S1/S2` are special mirror families.
- `DOORV/H` are door orientations; locked/remote/curtain/transport variants are represented by corresponding `DOOR*` families.
- `LEVEL_UP` is a normal next-level gateway; `LEVEL_UP2` skips a level.
- `WALL_EX1/2` are exploding wall/door-related families.
- `ONE_SHOT` is the original spelling for disappearing-gargoyle definitions.
- `SPECIAL1`, `CONTROL`, `ACTIONSPOT`, `TRIGGER1/2`, `RETREAT`, `TURN`, `FLEE`, `SAFESPOT` have confirmed data uses; full runtime dispatch remains incomplete.

## GUARD runtime and AI

GUARD base `0x93AE`, stride 26, maximum 100; count global `0x7E5E`.

Direct developer diagnostics identify:

- `+06` timer;
- `+08` OBJECT slot/index;
- `+0A` strategy;
- `+0B` state;
- `+0C` nextstate;
- `+10` strength / HP;
- `+11` octant;
- `+12` resoct.

Fresh GUARD strength is initialized to `0xFF`. No class-indexed post-spawn HP initializer has been found; practical toughness is heavily influenced by class/weapon transforms and special phase logic.

The state dispatcher covers states `0x00..0x15`. State `0x15` is confirmed pain/hit reaction and returns to `next_state`.

### GUARD13 resolved: Dracula-Bat

Previous “unknown/unused GUARD13” notes are superseded.

A lethal Dracula class `0x11` path transforms the same actor in place:

```text
OBJECT+06: 0x11 -> 0x14
GUARD+10:  0xFF
GUARD+0B:  0x08
GUARD+0C:  0x02
GUARD+06:  1
sequence/frame value: 0x23
transformation event/sound request: 0x22
```

Class `0x14` is therefore the internal Dracula-Bat second phase. It scores 200 on final death. Dracula phase 1 scores 0. Normal Bat class `0x08` remains separate and scores 25.

### GUARD25 narrowed

Class `0x20`:

- strength 255;
- generic observed profile state 07 -> next 02, strategy 0;
- score 50;
- lies outside explicit resistance jump table `0x0C..0x1F`;
- no confirmed dedicated SFX or normal MAP spawn;
- best current classification is cut/unfinished/fallback, INFERRED.

### Per-GUARD score switch

| Guard | Name / role | Score |
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
| 10 | Dracula phase 1 | 0 |
| 11 | Cemetery Gargoyle | 150 |
| 12 | Garden Gargoyle | 150 |
| 13 | Dracula-Bat internal second form | 200 |
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
| 25 | unresolved/cut/fallback class | 50 |
| 26 | Dancers | default 0 path; outside normal switch |

## Combat / health / difficulty

Weapon selector `0x4C23`:

- 0 Single Shot Laser;
- 1 Magic Wand;
- 2 Silver Pistol;
- 3 Continuous Laser;
- `0xFF` none/unset.

Ammo:

- Silver `0x4C1F`;
- Laser `0x4C20`, shared by single/continuous laser;
- Wand `0x4C44`;
- ordinary pickup +20;
- forced/set value 50;
- intended threshold/display cap 100;
- Silver/Laser signed-byte quirk makes 127 the highest positive signed value in affected manual-memory/HUD paths.

Player health:

- `0x4C1D`;
- normal initialization/cap 100;
- normal lethal receiver saturates to zero and enters death state;
- Omnipotent bypasses normal damage.

Damage base:

```text
((OBJECT+18) - global_53EE) * 8 + random()%25
```

So shots-to-kill are geometry/RNG/difficulty/weapon dependent, not fixed class constants.

Special class cases:

- Penelope `0x15`: normal producer returns 0 plus separate helper side path;
- Hamerstein `0x16`: literal damage 3 only when `0x7E52 == 3`, otherwise 0, before difficulty scaling;
- Cannon `0x19`: 0;
- Ghost `0x1A`: Wand `/2`, all other weapons 0;
- Alien #1/#2: Wand 0;
- Dracula-Bat `0x14`: explicit `/8,/2,/2,/8` transform family.

Difficulty global `0x4C14`:

| value | player->enemy | enemy->player | GUARD timing |
|---:|---:|---:|---:|
| 0 | ×2 | ÷2 | slower |
| 1 | ×1 | ×1 | baseline |
| 2 | ÷2 | ×2 | faster |

Weapon jam global `0x4C2E` is script-controlled. E1M9 events `0x47` and `0x48` set/clear it; no random jam probability is supported.

## Renderer — corrected current model

The original renderer is not Wolfenstein 3-D's per-screen-column tile DDA.

```text
MAP 64x64
 -> FUN_1018_4370
 -> four calls to FUN_1018_4046 (orientations 0..3)
 -> merge compatible boundary edges
 -> VEC[1000], 28 B each
 -> distribute far pointers by VEC+07 orientation
 -> four VECLIST[333]
 -> sort horizontal lists by Y, vertical lists by X
```

Four VECLIST groups are separate; they must not be collapsed into one 333-entry list.

Per-frame structures:

- owner table `0x53FE`: 320×4-byte far pointers;
- wall occlusion/silhouette table `0x58FE`: 320×2-byte values;
- owner runs coalesce to <=50 20-byte spans at `0x5E88`;
- projected objects use <=100 18-byte records at `0x6270`;
- sprite transparency uses palette index `0x29` in audited WinG path.

## DEMO

Record layout:

`eventByte:u8, inputMask:u16, pad:u8, timestamp:u32`.

DEMO is timed input playback, not absolute positions. `-r` enables recording. DEMO.1 matches E1M11 behavior; DEMO.2/3 origin remains open.

## USER.SAV / CONFIG.SAV

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
- `0xC403` unresolved 336-byte runtime block;
- `0xC55B` 72-byte push pool = 12×6;
- `0xD6E3` floor palette index;
- `0xD6E4` ceiling palette index;
- `0xD6E5` runtime/render environment word corresponding to `0x7E60`, exact semantic open.

CONFIG.SAV is 20 bytes.

## BSF / version audit

Audited DOS shareware BSF versions include 1.0, 1.7, 1.8, 1.9 and 2.0, with Windows/full variants distinct. Six `nite3d.bsf` XREFs remain the direct IDA target: identify parent functions, trace file I/O and reconstruct the exact byte-by-byte verification algorithm.

Current evidence does not support serial-number, CD or online DRM claims.

## Hidden/special content and quirks

- E1M11 is the internal/demo level.
- GUARD13 is now resolved as Dracula-Bat second phase; do not list it as unused.
- GUARD25 remains unresolved/cut/fallback.
- GUARD26 Dancers is a separate scripted family.
- remote-door/cannon commands, special mirrors, pentagram conditions, scripted weapon jam and disappearing gargoyle definitions are present.
- undefined wall `0x37` exists in supplied E2M4 at `(61,54)` and should be preserved/documented as an original data quirk until proven otherwise.
- a prior audit identified a VECLIST boundary/off-by-one memory-overwrite quirk; reconstruction should document original behavior rather than depend on corruption.
- no Quake-style developer console has been established.

## Current high-value unknowns

1. GUARD25 `0x20` reachability/identity and orphan resource binding.
2. Complete Dracula `0x11 -> 0x14` resource/sound/corpse chain.
3. Final semantic writer trace for OBJECT `+14/+16/+18`.
4. 4096-byte cell-state block bit meanings.
5. Hamerstein gate global `0x7E52` complete semantics.
6. Enemy attack cadence/projectiles and enemy->player class mapping.
7. `ONE_SHOT`, `REVWALL`, `CONTROL`, `SPECIAL1`, mirror/pentagram dispatch.
8. BSF six-XREF verification algorithm.
9. Remaining SND.DAT state/class sound bindings.

## Evidence discipline

Use: `VERIFIED_EXE`, `VERIFIED_DATA`, `VERIFIED_SAVE_LAYOUT`, `BEHAVIORAL`, `INFERRED`, `PARTIAL`, `TODO`.

Do not promote guessed enemy HP/speed/state names/sound identities, wall meanings, exact FOV labels, platform-source identity or approximate completion percentages into verified facts.

The final 95–100% EXE claim requires byte/function/range classification.


## 2026-09-25 Win16 MFC / memory synchronization

The current repository now contains the relocation-aware Win16 MFC reconstruction and its modern compatibility layer. Canonical entry point: `docs/WIN16_MFC_RE_SUMMARY.md`. Static artifacts cover `CRuntimeClass16`, 31 runtime classes, CWnd layout/vtable/lifecycle anchors, HWND/HDC/HGDIOBJ/HMENU HandleMaps, evidence levels and explicit coverage states. Runtime validation remains separately tracked and requires the Win3.1 debugger checklist/capture template. The modern C++20 layer now includes `HandleRegistry`, `NativeHandleWrapper`, `WindowWrapper`, `WindowRegistry`, nested/RAII temporary scopes and the recovered z-order mapping. Historical 16:16 pointers, NE fixups and raw MFC object layouts are evidence only and are not reproduced as the x64 ABI.
