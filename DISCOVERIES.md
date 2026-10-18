# Nitemare 3D Reverse Engineering — Discoveries

Base consolidated: 2026-09-23; evidence-scoped addendum: 2026-10-17

This is the short-form master status for the reverse-engineering project. The canonical cross-thread report is [`docs/ALL_THREADS_CONSOLIDATION_2026-09-22.md`](docs/ALL_THREADS_CONSOLIDATION_2026-09-22.md); subsystem documents contain the instruction-level evidence.

## 2026-10-18 v0.46 runtime acceptance sync

The [v0.46 report](docs/V046_REMAX_RUNTIME_ACCEPTANCE_SYNC.md) synchronizes the newest original DOSBox-X evidence. PASS16 proves a natural same-scheduler PROJECTILE -> time/VGA -> INPUT boundary sequence and corrects PASS15 DS/WORLD alias attribution. GUARD PASS17–22 supplies executed alert, attack, planner, movement and collision witnesses, including state05's own movement call, state06 timer closure, and double-block RNG reflection. Controlled DOS1.2/DOS2 weapon runs now cover keyboard selection, commit/raise, mode, pistol ammo, held Multi Plasma and the shared weapon0/3 plasma pool. Shutdown tests add a non-fatal no-XMS path and configuration-reachable digital INT63 stop/IRQ-restore operations. A natural palette path also ties RNG seed 1 to timer 201 and live VGA DAC index writes. **DEMO total RNG order, active projectile FB-FE/reentry, SAVE/LOAD first-frame behavior, framebuffer/palette zero-diff, Win16 runtime and active audible DSP/DMA parity remain OPEN.**

## 2026-10-18 v0.45 weapon-switch frame ordering

The [v0.45 report](docs/V045_REMAX_WEAPON_SWITCH_FRAME_ORDER.md) closes the direct-parent ordering around weapon changes. With an active weapon, selection updates pending and optionally enters Lower but does not change current/fireMode until the HUD transition commits at position zero. Weapon selection occurs before FIRE within the same input function, so same-call FIRE still sees the old current weapon for an active-weapon switch; the no-current (`0xFF`) path is the exception because it equips immediately. The checked direct frame runs weapon/HUD update before projectile update and input. Therefore a HUD commit can be observed by FIRE later in that frame, and held Multi Plasma may fire on the commit frame if cadence is already ready. A projectile allocated by that input cannot be revisited by the already-completed direct parent projectile pass. **Nested/reentrant scheduler entries, exact wall-clock HUD timing, first projectile movement under reentry and DEMO/RNG coupling remain OPEN.**

## 2026-10-18 v0.44 weapon FIRE closure

The [v0.44 report](docs/V044_REMAX_WEAPON_FIRE_CLOSURE.md) moves the strongest weapon/cadence findings into the evidence layer. It fixes the cadence table at `[2,1,3,1]`, preserves Multi Plasma held-FIRE auto-repeat, and records the ordering that accepted cadence resets cooldown before the FIRE dispatcher. Consequently jam, invalid fireMode/action state, zero ammo, full projectile pool, or no selected weapon can reject a shot after cooldown has already been consumed. For projectile fire, the 8-slot first-free scan precedes the ammo helper, so a full pool does not spend ammo; weapons 0 and 3 share the same ammo counter. A selectedWeapon=`0xFF` cadence lookup is also preserved as an out-of-table read with build-specific initialized bytes (DOS1.2 `0x33`, DOS2.0 `0x65`, Win1.10 `0x03`). **Natural held-fire timing, weapon switching during FIRE, multi-target hitscan reachability, helper side effects and DEMO/RNG chronology remain OPEN.**

## 2026-10-18 v0.43 runtime + GUARD + renderer sync

The [v0.43 report](docs/V043_REMAX_RUNTIME_STATIC_SYNC.md) brings the newest October 18 evidence into main. New original-runtime evidence includes a natural DOS1.2 E1M1 door USE transition (state1→2, latch0→1), a 32,768-instruction world-update trace whose 33 live records match RAM order, and a deep DOS shutdown/CRT chain through video mode restore, WORX/music stop, PIT FFFFh, interrupt/vector restoration, mouse/RTC cleanup, XMS cache release, exit-BSF processing, CRT callbacks, INT00 restore and exit code 0. Static additions include the complete local v0.80 GUARD contact-damage switch, the v0.81 OLD19/NEW26 GUARD initializer and conditional Dancers wake RNG path, the E1M9 radio lifecycle correction, and the DOS2 sprite-pixel contract. The main branch now contains the previously separate E1M9 and DOS2 sprite research branch files plus new v0.43 bounded C++ evidence tests. **DEMO total RNG chronology, full weapons/projectiles, SAVE/LOAD first-tick behavior, full door lifecycle, Win16 runtime shutdown and framebuffer/audio zero-diff remain OPEN.**

## 2026-10-18 v0.42 static sync

The [v0.42 report](docs/V042_REMAX_OCT18_STATIC_SYNC.md) folds the newest October 18 static passes into the reconstruction evidence layer. It records the 12-build incoming-damage gate-order split (DOS1.0–1.9 gate-before-calc vs DOS2/Win16 calc-before-gate), class-dependent RNG masks and feedback-timer sequencing; the SECRET fixed-32-byte SAVE/LOAD codec with only N meaningful panel states; DOS/Win door LOAD runtime-prefix preservation; corrected dynamic-wall vs class-3 pool families; 62 reclassified ambiguous writer sites and 72 direct OBJECT map-pointer update edges; the Win16 E2M10 mode-4 queue consumer order; and corrected ordinal-level NE timing import relocations. New [C++ contracts](src/re/N3DV042Oct18Closures.hpp), [Python models](tools/n3d_v042_oct18_models.py), regression tests and static-facts CSV preserve the RE-first boundary. **Global alias closure, DEMO RNG total order, full scheduler/IRQ timing, framebuffer zero-diff and live audio remain OPEN.**

## 2026-10-18 v0.41 latest static-evidence consolidation

The [v0.41 report](docs/V041_REMAX_LATEST_STATIC_CONSOLIDATION.md) rolls the newest late-17-October evidence into the public codebase. It corrects the E1M9 MAP-layer interpretation (radio mode-0 clears WALL, not OBJECT), strengthens E1M9 resource-group provenance, records the split projectile rearm clock read and its conditional torn-read witness, preserves E2M10 palette-effect-before-counter ordering, models the nested global-frame-scratch/local-epoch tail, adds the 12-build OBJECT+18 / GUARD-generation / damage correspondence, imports a bounded DOS sprite compositor contract, and centralizes original constructor/source pool limits including E3M8 SECRET 32/32 and E2M10 door controllers 60/64. The matched DOS/Win asset audit also records 20 E1M1 OBJECT-byte differences and zero alias-partition mismatches across six IMG banks. **Global runtime chronology, full alias closure, DEMO RNG total order, framebuffer zero-diff and live audio timing remain OPEN.**

## 2026-10-17 v0.40 projectile reentry / ABA narrowing

The [v0.40 report](docs/V040_REMAX_PROJECTILE_REENTRY_ABA_NARROWING.md) closes one important *negative* branch of the E2M10 reentry problem. The current slot may be revisited by a nested pool while still state 1, but a state-1 visit cannot locally run the state-2 expiry branch in the same visit. It therefore cannot become free through the standard lifecycle before the later input/FIRE allocator in that same nested scheduler invocation. The direct same-property E2M10 path also advances 20→21 and does not immediately recurse into a second wait. **Direct one-level state1→2→0→same-slot reuse is therefore excluded under the audited standard paths.** Other nested callbacks, indirect state writers, SAVE/LOAD/IRQ effects and a second pool visit that begins in state 2 remain open. New [C++ evidence](src/re/N3DV040ProjectileReentryClosure.hpp), [Python oracle](tools/n3d_v040_projectile_reentry.py) and regressions encode the bounded closure.

## 2026-10-17 v0.39 late-day static closures

The [v0.39 report](docs/V039_REMAX_LATE_STATIC_CLOSURES.md) adds bounded code/test representations for several new original-byte-backed findings: E2M10 property-0x40 normal return reaches IMPACT without DDA budget reread; E1M9 radio state-0x14 has a 112-count local lifecycle and global stop semantics; FIRE cadence precedes the weapon dispatcher with thresholds [2,1,3,1]; Cannon/class-0x19 damage is zero but still consumes the pre-dispatch RNG draw; the standard nonlethal pain path writes GUARD+0x12=8 before its direct selector calls; DOS cache/backend clock routing is split between RTC, BIOS BDA and system time; and angle normalization applies at most one ±360 correction. New [C++ contracts](src/re/N3DV039LateStaticClosures.hpp), [Python models](tools/n3d_v039_static_models.py), regressions and CI preserve the RE-first boundary. **DEMO chronology, nested IRQ/IF timing, projectile ABA, full writer/alias closure, pixel zero-diff and live audio remain OPEN.**

## 2026-10-17 v0.38 three-day consolidation

The [v0.38 consolidation](docs/V038_REMAX_THREE_DAY_CONSOLIDATION.md) promotes several 14–16 October findings into bounded, buildable reference contracts without promoting them to original-runtime proof. The new [C++ evidence header](src/re/N3DV038ThreeDayFindings.hpp) and [Python oracle](tools/n3d_v038_recent_models.py) cover the Win16 joystick post-division clamp, Magic Eye RNG draw budget, door state 4 normal-action blocking, 18-byte-versus-14-byte door/panel completion timing, class-0x16/Hamerstein damage direction and RNG ordering, signed E2M10 every-20 gating, low16 render-average truncation, initial DOS graphics/SAVE segment aliasing, and the projectile mixed-generation callback invariant. Synthetic regressions are wired into CI. **DEMO ordered RNG, nested scheduler chronology, final-tick door passability, SAVE/LOAD first-tick parity, framebuffer zero-diff and live audio timing remain OPEN.**

## 2026-10-14 v0.30 trace-verification correction

The [v0.30 differential trace report](docs/V030_REMAX_DIFFERENTIAL_TRACE_CLOSURE.md) documents an important **verifier limitation**: individually valid RNG transitions, matching final states, and matching FAST *direct* children cannot prove complete first-to-last runtime chronology. New [Python tools](tools/n3d_trace_compare.py) and [C++ evidence checks](src/re/N3DV030TraceClosure.hpp) compare ordered original/candidate records, surface the first difference, and require explicit capture-boundary attestation and the known unpacked DOS v2.0 image fingerprint for stricter provenance checks. All new fixture tests are synthetic. **No fresh original EXE disassembly or in-game runtime evidence was obtained in this version; open system confidence and project parity estimates remain unchanged.**

## 2026-10-14 v0.29 evidence-scoped addendum

The [v0.29 scheduler/trace report](docs/V029_REMAX_SCHEDULER_TRACE_AND_EDGE_CASES.md) collects recently reported **DOS v2.0 FAST direct-call ordering** (`1000:C150`), its conditional last `89A2` call, and **DEMO routing**, plus build-specific door/PUSH edge cases, an **E2M10 reentrant scheduler lead** and an **open first post-LOAD tick**. The new [C++ evidence registry](src/re/N3DV029SchedulerEvidence.hpp) and [CSV trace tool](tools/n3d_trace_audit.py) are exercised with synthetic fixtures. None of the new static reports was independently re-disassembled from original binaries in this revision, and **no original-game runtime trace or increased parity percentage is claimed**. The 2026-09-23 detailed facts below retain their original historical evidence status.

## 2026-09-23 all-audit update

The 2026-09-23 delta is consolidated in [`docs/PROJECT_FINDINGS_DELTA_2026-09-23.md`](docs/PROJECT_FINDINGS_DELTA_2026-09-23.md), with instruction-level evidence in [the core-function map](analysis/nite3w_core_function_map_2026-09-23.md), [the projectile audit](analysis/nite3w_projectile_pool_2026-09-23.md), the [USER.SAV flag audit](analysis/nite3w_user_sav_story_flags_2026-09-23.md), and the [guard wake-cache audit](analysis/nite3w_guard_wake_cache_2026-09-23.md).

New code-level anchors include the 8 × 42-byte NITE3W player projectile pool saved at 0xC403, a 20-unit per-axis OR render threshold (not a despawn rule), the 0x51A4 SECRET-panel/red-ID-card linkage, 0x51A5 Cannon AI gate, and CAUSTIC fire damage of 100/10/2 HP per simulation update. Runtime cadence/visual verification, the DOS projectile layout, and remaining USER.SAV byte semantics stay open.

## Evidence policy

Use these labels consistently:

- `VERIFIED_EXE` — direct original executable instruction/data-flow evidence.
- `VERIFIED_DATA` — direct original MAP/IMG/WALLS/OBJECTS/SND/UIF/GAME.PAL/FLI evidence.
- `VERIFIED_SAVE_LAYOUT` — direct save-file layout evidence.
- `BEHAVIORAL` — directly observed in original gameplay/video.
- `INFERRED` — strong reconstruction, but not yet direct semantic proof.
- `PARTIAL` — path/field exists but its complete meaning is unresolved.
- `TODO` — open target.

Do not promote values from OpenNitemare3D, ZDoom/GZDoom recreations, other raycasters, old chat estimates or visual similarity to original-game facts without original executable/data/runtime evidence.

## Canonical Windows target

Primary reference binary:

- `NITE3W.EXE`, Nitemare-3D for Windows V1.10;
- 230400 bytes;
- Win16 NE, 10 segments;
- SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`;
- direct imported modules: `KERNEL`, `WING`, `DISPDIB`, `GDI`, `USER`, `KEYBOARD`, `COMMDLG`, `MMSYSTEM`, `SHELL`;
- `joystick.drv` is referenced dynamically;
- MFC/runtime code is statically linked rather than imported as an external MFC DLL.

The Windows build is currently the most legible algorithm reference. DOS binaries remain important for version/platform comparison, but Windows findings are not automatically claimed to be byte-identical DOS behavior.

## Corrections that supersede older notes

These values are now directly supported and replace the old approximate record-size guesses:

- OBJECT stride is **0x1C / 28 bytes**, not 80 bytes.
- GUARD stride is **0x1A / 26 bytes**, not 98 bytes.
- visible wall span stride is **0x14 / 20 bytes**, not 52 bytes.
- the renderer is not Wolfenstein 3-D one-grid-ray-per-column DDA.
- `MAXVECLIST=333` means four orientation-specific arrays of 333 far pointers; the VEC pool itself is 1000 records.
- `WARP_L1..L4` are colored-key locked passage/wall classes, not a generic teleport family.
- `LEVEL_UP2` is a level-skip gateway.
- suffixes such as `DOORVL2/VL3` describe graphical/environment door sets, not stronger lock levels.
- original class spelling is `ONE_SHOT`, not the older `ONE_SHOOT` transcription.

## MAP archive / world model

Confirmed geometry:

- 64x64 cells;
- two bytes per cell: `{wallByte, objectByte}`;
- one level payload = 8192 bytes;
- archive header = 514 bytes;
- supplied MAP.1 has 11 payloads, MAP.2 has 10, MAP.3 has 10;
- E1M11 is the internal/demo map;
- E1M3 and E1M11 share the same local first-plane geometry/spawn fingerprint, while their object/state plane differs;
- world scale is 64 world units per tile (`coord >> 6`);
- player starts are object IDs 1..4 for four cardinal orientations;
- player spawn coordinates are tile center: `x*64+32`, `y*64+32`.

USER.SAV contains an 8192-byte mutable MAP snapshot, proving runtime map/object state is persisted rather than always recreated from a pristine MAP payload.

`WALLS.*` and `OBJECTS.*` are definition/editor catalogs. Runtime behavior needed by the executable is compiled/derived internally; installed runtime sets can operate without those editor catalogs.

Historical MapEdit 7.2 uses a 64x64 model and an editor `MAX_LEVELS=60`. That is editor capacity, not proof of the original executable's archive ceiling.

## Fixed runtime capacities

Direct boundary checks establish:

| Family | Capacity | Record/entry size |
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

Important anchors:

- OBJECT base `0x6D66`, count `0x7E58`;
- GUARD base `0x93AE`, count `0x7E5E`;
- doors base `0x9DD6`;
- panels base `0xA356`;
- pushes base `0xA616`;
- visible wall-span count `0x5E7E`, array `0x5E88`;
- projected sprite queue base `0x6270`.

## Player movement, health and input

Verified player anchors:

- world X `0x4BF6`;
- world Y `0x4BF8`;
- current tile X/Y `0x4BF2/0x4BF4`;
- health byte `0x4C1D`;
- normal health range is 0..100, initialized/clamped to 100;
- lethal normal damage writes exactly zero before death transition, preventing normal underflow;
- collision AABB half extent is 27 world units;
- movement is subdivided into small integer steps and X/Y collision is handled separately, producing wall sliding.

Difficulty global `0x4C14` is numeric easier/baseline/harder:

| value | player -> enemy | enemy -> player | GUARD timing |
|---:|---:|---:|---:|
| 0 | x2 | /2 | slower |
| 1 | x1 | x1 | baseline |
| 2 | /2 | x2 | faster |

Recovered input bits:

- `0x0002` move forward/current facing;
- `0x0004` move backward/opposite facing;
- `0x0008`, `0x0010` turn directions, or strafe directions when `0x0100` is held;
- `0x0020` doubles movement/turn increments;
- `0x0040` forces movement/turn increments to 1;
- `0x0080` FIRE;
- `0x0100` strafe modifier;
- `0x0200` USE/ACTION, edge-triggered.

## USE, doors, pushes, wall classes and scripts

USE resolves an adjacent cardinal cell and is not just a generic door-open call. The same interaction chain covers doors, switches/panels, keyed walls/passages, pushables, warps/level exits and special scripted walls.

Verified/strong families include:

- `WARP_L1..L4`: red/green/blue/yellow keyed passage families;
- `WARP_1..8`: paired stair/dumbwaiter/vertical connection groups;
- `WARP_E1/E2`: elevator groups;
- `WARP_S1/S2`: mirror-related special warps;
- `DOORV/DOORH`: vertical/horizontal sliding doors;
- `DOORVL/HL`, `VL2/HL2`, `VL3/HL3`: locked-door orientations in different environment sets;
- `DOORVI/HI`: Transportation Chamber doors;
- `DOORVR/HR`: remote-controlled doors;
- `DOORVC/HC`: curtain doors;
- `JAMB`, `CONTROL`, `LEVEL_UP`, `LEVEL_UP2`, `WALL_EX1`, `WALL_EX2`, `ONE_SHOT`, `SPECIAL1`, `ACTIONSPOT`, `TRIGGER1/2`, `RETREAT`, `TURN`, `FLEE`, `SAFESPOT`.

Push class `0x28` moves 8 updates x 8 world units = one 64-unit tile.

Known safe-combination values include `333`, `01532`, `080993`, `372535`.

Still open: exact 22-byte door/panel layouts, complete CONTROL command mapping, ONE_SHOT activation, SPECIAL1 dispatch, mirror/pentagram state, ID-card consumption/transport-chamber logic and precise REVWALL semantics.

## Renderer

The renderer is a projected vector/span pipeline:

```text
MAP 64x64
  -> exposed boundary extraction/merging
  -> VEC[1000], 28 B each
  -> 4 x VECLIST[333] orientation pointer arrays
  -> world-to-camera transform + near clipping
  -> perspective projection
  -> 320-entry column owner table
  -> <=50 visible wall spans, 20 B each
  -> wall rasterization + column occlusion/silhouette
  -> <=100 projected sprite commands, 18 B each
  -> 320x200 indexed framebuffer
```

Important renderer facts:

- framebuffer 320x200, 8-bit indexed, 64000 bytes;
- normal 3-D viewport x=8..311, y=4..155, size 304x152, center `(160,80)`;
- VEC creation scans MAP exposed boundaries for orientations 0..3 and merges compatible adjacent edges;
- four VECLIST counts are at `0x697A/0x697C/0x697E/0x6980`;
- list bases are `0x6982/0x6EB6/0x73EA/0x791E`;
- owner table base `0x53FE`, 320 x 4-byte far pointers;
- wall silhouette/occlusion table base `0x58FE`, 320 x 2-byte values;
- wall-span array base `0x5E88`, capacity 50;
- projected sprite queue base `0x6270`, capacity 100.

Do not describe the `0x58FE` table as a conventional metric Z-buffer unless later evidence proves those units.

## OBJECT / GUARD runtime model

OBJECT:

- 28-byte stride, capacity 350;
- `+05` flags, with `0x08` selecting GUARD creation;
- `+06` class;
- `+07` GUARD index for guard objects;
- `+0C:+0E` map-cell far-pointer binding;
- `+10/+12` world X/Y;
- `+14/+16` render/spatial ordering fields (semantic naming partial);
- `+18` projected/view-space vertical baseline used by player->GUARD damage calculation; it is not world Y.

GUARD:

- 26-byte stride, capacity 100;
- `+08` OBJECT slot/index;
- `+0A` strategy;
- `+0B` state;
- `+0C` nextstate;
- `+0D` object/definition id;
- `+06` timer;
- `+10` strength/HP;
- `+11` octant;
- `+12` result octant.

Normal GUARD creation initializes strength to 255. No class-specific post-spawn HP table has been found; practical toughness is largely created by weapon/class damage transforms and special phases.

The state dispatcher accepts exactly 22 states (`0x00..0x15`). State `0x15` is the confirmed pain/hit reaction. States `02..14` are intentionally not overnamed until movement/attack/animation/sound XREFs close their semantics.

## Guard class/score findings

The score switch covers OBJECT classes `0x08..0x20`:

| Class | Role | Score |
|---:|---|---:|
| 0x08 | Bat | 25 |
| 0x09 | Frankenstein | 75 |
| 0x0A | Mummy | 50 |
| 0x0B | Skeleton | 100 |
| 0x0C | Mrs H. | 250 |
| 0x0D | Zelda | 150 |
| 0x0E | Vampira | 200 |
| 0x0F | Baddie #1 | 100 |
| 0x10 | Baddie #2 | 100 |
| 0x11 | Dracula phase 1 | 0 |
| 0x12 | Cemetery Gargoyle | 150 |
| 0x13 | Garden Gargoyle | 150 |
| 0x14 | Dracula-Bat phase 2 / GUARD13 | 200 |
| 0x15 | Penelope | -1000 |
| 0x16 | Dr. Hamerstein | 1000 |
| 0x17 | Tall slim robot | 100 |
| 0x18 | Trashcan robot | 200 |
| 0x19 | Cannon | 0 |
| 0x1A | Ghost | 25 |
| 0x1B | Goldie | 100 |
| 0x1C | Greenie | 100 |
| 0x1D | Demon | 250 |
| 0x1E | Alien #1 | 250 |
| 0x1F | Alien #2 | 200 |
| 0x20 | unresolved/cut/fallback GUARD25 | 50 |

GUARD26/Dancers is outside this switch and follows a separate scripted path.

### Dracula -> Bat

Dracula phase 1 (`class 0x11`) transforms in place on its lethal path:

- OBJECT class `0x11 -> 0x14`;
- GUARD strength reset to `0xFF`;
- state `0x08`, nextstate `0x02`;
- timer `1`;
- sequence/frame-related value `0x23`;
- transformation event/sound request `0x22`.

Thus the strongest current model is two 255-strength Dracula phases. Normal Bat class `0x08` is a different class.

GUARD25/class `0x20` remains visually unidentified and is best treated as unresolved/cut/fallback, not given an invented enemy name.

## Combat / weapons

Active weapon selector `0x4C23`:

- 0 Single Shot Laser;
- 1 Magic Wand;
- 2 Silver Pistol;
- 3 Continuous Laser;
- `0xFF` none/unset.

Ammo:

- silver `0x4C1F`;
- laser `0x4C20` (shared by weapon selectors 0 and 3);
- wand `0x4C44`.

Normal pickup/display cap is 100. Silver/laser audited paths use signed comparisons, making 127 the highest positive signed-byte edited value before 128..255 appear negative in those compare/display paths.

Player->GUARD base damage producer:

```text
base = ((OBJECT+18) - global_53EE) * 8
base += random() % 25
```

It then applies class/weapon-specific transforms and difficulty. Therefore a universal fixed "shots to kill" table is not valid without fixing geometry/projection, RNG, weapon and difficulty.

Important weapon/class cases:

- Ghost (`0x1A`) is damaged by Magic Wand in the audited producer while the other weapons return zero;
- Alien #1/#2 reject Magic Wand there;
- Penelope and Cannon return zero normal weapon damage in that producer;
- Baddie #1/#2 reduce non-wand values by literal arithmetic `/256`;
- Hamerstein returns literal damage 3 only when global `0x7E52 == 3`, otherwise zero, before difficulty scaling.

Weapon jam is scripted, not a recovered random probability. E1M9 event `0x47` sets jam state `0x4C2E`; event `0x48` clears it.

## DEMO format

All supplied demos begin with the 6-byte header representing WORDs `(10,5,20)`.

Each event is an 8-byte packed record:

```text
byte  eventByte
word  inputMask
byte  pad
dword timestamp
```

DEMO.1 has 203 records, DEMO.2 271, DEMO.3 286. DEMO.1 is behaviorally associated with the attract-mode E1M11 setup. DEMO.2/3 origin levels remain unproven and should be tested against all 31 preserved maps rather than assumed from their numeric suffixes.

`NITE3W.EXE -r` enables recording. No direct command-line playback switch has yet been confirmed.

## SND.DAT / audio

Audio work must be validated against original in-game playback, not just against whether an extracted VOC/WAV opens in a media player. Current targets include:

- exact DAT directory interpretation;
- Windows PCM versus DOS VOC differences;
- SFX identity mapping;
- guard alert/attack/pain/death SFX binding;
- MIDI inventory/level usage;
- failing or incorrectly decoded VOC entries.

The current reverse repo contains dedicated audio/cheat audit material; do not replace it with older extractor assumptions.

## CONFIG.SAV / USER.SAV

CONFIG.SAV is exactly 20 bytes. Confirmed fields include viewport width, output dimensions, mouse/joystick scaling, MIDI/SFX volumes, enable flags and four cheat flags (Omniscient, Omnipotent, Omnifarious, Omnificent).

USER.SAV uses fixed records of `0xD6E7 = 55015` bytes. Major blocks include:

- header/slot metadata;
- episode and zero-based level index;
- saved tick/time base;
- 8192-byte mutable MAP snapshot;
- 94-byte gameplay/global block;
- fixed-capacity runtime arrays;
- fill-color selectors `0x7E62/0x7E63` and shade-level word `0x7E60` (default index 2, dark-event index 6);
- 8 × 42-byte player-projectile pool, 64-byte guard wake cache, 256-byte color-remap table, and 4096-byte automap raster/index buffer.


The physical record layout is recovered; semantic labeling of every field is still incomplete.

## ENDING.FLI

Analyzed ENDING.FLI contains 488 frames. Relevant chunk types include `COLOR_64`, `BRUN`, `LC`, `BLACK`, `COPY`.

Correct editing must preserve palette state and delta-frame dependencies. Treating every frame as an independent bitmap can corrupt later frames.

## BSF / executable-version audit

Version comparison targets include 1.0, 1.7, 1.8, 1.9 and 2.0. The important unresolved BSF task is to resolve all XREFs to `nite3d.bsf`, identify parent functions, follow open/read/seek/close and reconstruct the verification/comparison algorithm byte-for-byte across versions.

## Highest-value remaining targets

1. Complete semantic naming for GUARD states 02..14 and all strategy values.
2. Recover exact guard movement/attack cadence, LOS/FOV/hearing and enemy-projectile production; the player projectile pool and player-fire path are now mapped.
3. Bind all enemy alert/attack/pain/death SND.DAT IDs directly.
4. Finish special-wall/resource/renderClass mapping and lower raster/backend details; owner-conflict geometry and current texture-U corrections are documented.
5. Complete animated-wall/resource timing and remaining VEC field semantics; the animation update control flow is mapped.
6. Finish 22-byte door/panel/control record semantics and SPECIAL1/ONE_SHOT/REVWALL details.
7. Refine the geometric units of player->GUARD `OBJECT+18` (writer `FUN_1010_CC7C` identified) and bind enemy->player classes to visible attackers.
8. Finish BSF integrity/version-difference algorithm.
9. Resolve remaining USER.SAV byte semantics and validate shade override bounds/runtime effect at `0x7E60`.
10. Complete DOS-vs-Windows backend/behavior comparison and feed only verified shared behavior into ports.

## Detailed reports

Start with:

- [`docs/ALL_THREADS_CONSOLIDATION_2026-09-22.md`](docs/ALL_THREADS_CONSOLIDATION_2026-09-22.md)
- [`docs/UNKNOWN_SYSTEMS_AUDIT_2026-09-22.md`](docs/UNKNOWN_SYSTEMS_AUDIT_2026-09-22.md)
- [`analysis/nite3w_renderer.md`](analysis/nite3w_renderer.md)
- [`docs/GUARD_AI_RE.md`](docs/GUARD_AI_RE.md)
- [`docs/COMBAT_DAMAGE_RE.md`](docs/COMBAT_DAMAGE_RE.md)
- [`docs/PLAYER_HEALTH_RE.md`](docs/PLAYER_HEALTH_RE.md)
- [`docs/PLAYER_COLLISION_RE.md`](docs/PLAYER_COLLISION_RE.md)
- [`docs/USE_INTERACTION_RE.md`](docs/USE_INTERACTION_RE.md)
- [`docs/SPECIAL_WALL_USE_RE.md`](docs/SPECIAL_WALL_USE_RE.md)
- [`docs/DEMO_FORMAT_RE.md`](docs/DEMO_FORMAT_RE.md)
- [`docs/SAVE_LIBRARIES_IDA_REPORT.md`](docs/SAVE_LIBRARIES_IDA_REPORT.md)
- [`docs/RE_AUDIT_CHEATS_AUDIO.md`](docs/RE_AUDIT_CHEATS_AUDIO.md)

This file intentionally summarizes the current verified model. Exact offsets, disassembly excerpts, confidence boundaries and test material belong in the linked subsystem reports.