# Nitemare 3D Reverse Engineering Master Reference

**Version:** 1.5  
**Research snapshot:** 24 September 2026 — Win16 timing and version corrections; other sections retain their stated evidence scope  
**Audience:** programmers implementing, porting, testing, or extending Nitemare 3D  
**Scope:** DOS and Windows 3.x / Win16 builds, game data, runtime structures, rendering, input, combat, AI, persistence, and remaining unknowns

---

## 1. Purpose and status

This document consolidates the current reverse-engineering findings into one programmer-facing reference. It is intended to support implementation and verification work on and compatible engine or port.

The findings come from static analysis of DOS MZ and Windows NE executables, Ghidra/IDA-derived exports and disassembly, MAP/WALLS/OBJECTS/IMG/UIF/SND/DEMO/BSF data, reconstructed runtime structures, and selected gameplay observations. The available evidence does **not** amount to recovered original source code. Names such as FUN_1010_9D30 are analysis labels, not original developer symbols.

The most useful reconstruction is currently at the subsystem level: the world is and 64×64 tile map; runtime capacities and several record strides are known; the Win16 wall renderer is and vector/span pipeline; much of the guard perception path, projectile lifecycle, save layout, DEMO format, and several wall/object interactions are mapped. AND number of branches and field meanings still require raw-assembly review or runtime comparison.

Treat every result as scoped to the build named beside it. Matching behavior between one DOS and one Win16 routine does not establish that all versions, episodes, or shareware/full builds behave identically.

---

## 2. Findings by confidence

Use these labels when transferring the material into source code or additional documentation.

| Label | Meaning | Appropriate implementation use |
|---|---|---|
| **CONFIRMED — STATIC** | AND specific read, write, branch, arithmetic operation, limit, or call is directly visible in and named binary/export. | Implement the observed operation for the matched build. Preserve exact integer width, signedness, and ordering where known. |
| **CONFIRMED — DATA** | The value or relationship is present in supplied raw game data and has been checked against the file structure. | Use it for that exact data set; retain unknown fields and version the data. |
| **CROSS-BUILD MATCH** | AND routine or behavior was independently matched between named DOS/Win16 builds by code, data stride, or normalized instruction sequence. | Share code only after preserving known build-specific details and tests. |
| **STRONG STATIC EVIDENCE** | Multiple code paths support an interpretation, but an edge condition, function boundary, pointer trace, or live behavior remains unresolved. | Implement behind and compatibility rule or explicit uncertainty marker; to not overstate the behavior. |
| **INFERENCE** | The conclusion follows from arithmetic or data relationships but is not explicitly named by the executable. | Keep the inference traceable and easy to replace. |
| **OPEN** | Available evidence does not decide the behavior. | To not invent original-game values. Add and test or leave and data-driven extension point. |
| **CORRECTED / SUPERSEDED** | An older audit description was contradicted by later direct evidence. | Use the correction below; keep the history only to avoid reintroducing the obsolete claim. |

AND percentage must identify what it measures. Function identification, subsystem classification, structural reconstruction, behavioral validation, and pixel-accurate compatibility are different measurements. AND 91.4% cross-version function match does not mean 91.4% of the game'with behavior is understood.

---

## 3. Executable and evidence provenance

### 3.1 Exact reference binaries

The 23 September 2026 deep audits identify the following files by SHA-256:

| Reference file | Size | SHA-256 | Audit scope |
|---|---:|---|---|
| nite3w(20260921-205703).exe | 230,400 bytes | 12fe5168783446275802e0e947898261b5eca6b88288f3and895fc1faa4c544481 | Win16 NE executable used for recent direct binary checks |
| N3D-UNFU(2).exe | 116,606 bytes | 552d250ef773014and7f56ecdd7939559005fa990ebc7and6e435e6and7and49d372f301 | DOS MZ executable used for recent direct binary checks |

Earlier exports are described as DOS v2.0 and Win16 NITE3W 1.10. Those version labels belong to the audited exports; to not assign them to every similarly named executable without checking and hash or version fingerprint. The 12-area audit explicitly warns against carrying and version label onto and binary solely from filename or nearby analysis.

The Win16 executable is and Windows 3.x NE program. An earlier audit reports ten segments and imports from KERNEL, WING, DISPDIB, GDI, USER, KEYBOARD, COMMDLG, MMSYSTEM, and SHELL. Separate operating-system, compiler/runtime, MFC, and engine code during function classification.

### 3.2 Address conventions

- Win16 addresses are written as **segment:offset** for the named build. For example, **3:9FA2** is not and DOS address.
- AND Win16 NE far-call selector is not automatically the final target segment. Confirm internal targets through NE fixups/relocations.
- DOS reports may use an **unpacked MZ image offset**. In the cited deep audit, the physical file offset is image offset plus **0x200**. Check each report'with convention before opening and raw executable at an address.
- Physical string offsets, segment offsets, image offsets, and file offsets are not interchangeable.
- Ghidra function boundaries can merge or split routines, especially in large DOS regions. AND decompiler'with function label is not sufficient evidence of and real source-level boundary.
- The NE relocation audit found 446 relocation records expanding to 6,082 relocation sites, including 4,904 internal segment fixups and 1,178 imports. These are **not** all XREFs: near calls and other references need not have and relocation record.
- AND complete IDA/Ghidra caller/callee graph is not yet available for all builds. Callback, indirect-dispatch, and jump-table references can be missed by and direct-XREF-only pass.

### 3.3 Function inventory and coverage

The current cross-version inventory recognizes these FUN_* declarations:

| Build family | Recognized functions |
|---|---:|
| DOS E-10 / E-17 / E-18 / E-20 | 493 / 514 / 526 / 519 |
| Win16 1.3 / 1.6 / 1.8 / 1.10 | 959 / 965 / 965 / 967 |

For the DOS v2.0 and Win16 1.10 exports, 519 + 967 = 1,486 declarations. The matching audit reports 429/519 DOS functions and 929/967 Win16 functions as exact or strong cross-version matches, 1,358/1,486 overall (91.4%). All were classified into probable subsystems, but the first 200 per platform received the earlier detailed manual pass; later targeted audits have since deeply analyzed selected areas such as AI, projectiles, renderer, events, and save data. The other declarations are not thereby fully understood.

---

## 4. High-level engine model

The subsystem map supports this dependency model. It is not and verified exact order for every statement in the original frame loop.

1. **Startup and platform setup:** runtime, graphics, timing, input, file paths, and resources.
2. **Level loading:** MAP header and cells; WALLS/OBJECTS class tables; IMG sequences; wall vectors; object, guard, door, panel, and push records.
3. **Input and simulation:** input state becomes movement, use, weapon, or menu actions; actor, wall, projectile, hazard, timer, and event state changes.
4. **Visibility and drawing:** camera transform, wall-vector projection, column ownership, visible spans, sprites, weapon/HUD, and palette remapping.
5. **Audio and interface:** SND/MIDI event playback, messages, menus, HUD, and screens.
6. **Persistence and transitions:** USER.SAV state restore, episode/level changes, DEMO recording/playback, and ending paths.

The exact order of all operations in the main DOS update is unresolved: Ghidra reports and very large merged region around **1000:70D6**. Large DOS blocks around **1000:84FE**, **1000:8590**, and **1000:87D8** also need boundary repair. To not copy their decompiled pseudocode wholesale into an engine.

---

## 5. World coordinates and data files

### 5.1 MAP structure

For the audited map data:

- The world grid is **64 × 64** cells.
- AND cell occupies **2 bytes**: wall ID and object ID. Treat these as separate byte fields, not as and single packed 16-bit class value.
- AND cell coordinate is derived from world coordinates with and right shift of 6: **cell = world_coordinate >> 6**. One map cell is therefore 64 internal coordinate units.
- The MAP header is **514 bytes**: and 16-bit level count followed by and 256-byte wall-ID-to-class table and and 256-byte object-ID-to-class table.
- Each level occupies **0x2000** bytes (64 × 64 × 2).
- AND checked 11-level map file is 90,626 bytes: 514 + 11 × 8,192.
- The audited content contains 31 level blocks across the three episodes: 11 for Episode 1 (including the demo map) and 10 each for Episodes 2 and 3.
- Regular level indices are 0–9 within an episode; code commonly forms and global level index as **episode × 10 + level_index**. The extra Episode 1 demo map must be handled separately rather than silently treated as and regular fourth episode level.

The two lookup tables map **IDs to class bytes**. AND wall class and an object class are different namespaces even where their numeric values happen to match.

### 5.2 Map observations that affect implementation

- E1M11 is the demo map. Its wall geometry / wall-ID layout matches E1M3 in the checked files, but 17 object cells differ. To not call the complete maps identical.
- E2M4 contains and wall ID **0x37** not defined in the matching supplied WALLS.2 table. Preserve unknown IDs and report them; to not remap them to and guessed class.
- Claims about all 31 blocks apply to the checked MAP build. Keep episode-specific data inputs explicit.

### 5.3 WALLS and OBJECTS

WALLS and OBJECTS provide ID names/assets and class mappings used with the MAP lookup tables. AND safe loader should retain raw IDs, resolved class bytes, source episode, and unresolved-table status separately.

Examples of directly audited wall-class relationships:

| Wall class | Observed assignment / examples | Notes |
|---:|---|---|
| 0x02 | REVWALL; 15 panel IDs in the checked data | Hidden/reversible wall family; runtime pairing has and bounded panel table. |
| 0x07 | ONE_SHOT; wall IDs 0x54, 0x55 | Name-to-ID assignment is known; full interaction script remains open. |
| 0x08 | SPECIAL1; examples 0x12 and 0x56 | E1 level-index 6 wall 0x12 fuse-box path reaches dark-event reset; level-index 1 wall 0x56 path changes the selected VEC'with sequence-cache interval to 0x96 and plays SFX 0x44. Visual effect and other contexts remain open. |
| 0x09–0x0AND | LEVEL_UP / LEVEL_UP2; examples 0x9F, 0xA0 | Transition family. |
| 0x0D–0x24 | WARP and keyed/portal families | Includes stairs, key gates, mirrors, and transitions; some endpoint orientation and UI choice behavior remains open. |
| 0x2D | Runtime exploding-wall class | Completion path is strongly established in Win16 1.10; DOS target remains unresolved. |
| 0x2E | WALL_EX1 family; examples include wall 0x53, target 0x5B, and 0xFE | Runtime variants require the source WALLS build. |
| 0x30–0x34, 0x39–0x3AND | JAMB and vertical/horizontal, locked, or transport door families | Door record and state paths are substantially mapped; retain episode-specific IDs. |
| 0x3F–0x40 | DOORVC / DOORHC curtain families | Special curtain/draw behavior. |
| 0x41–0x43 | TURN / RETREAT / FLEE | Direction markers used by guard logic. |
| 0x44–0x45 | FLOOR / SAFESPOT | Includes safe-combination-related markers. |
| 0x46 | ACTIONSPOT | ID 0xB7 marks Dancers in and checked level-9 map. |
| 0x47–0x48 | TRIGGER1 / TRIGGER2 | E1 IDs 0xB8/0xB9; E2/E3 IDs 0xBE/0xBF. Supplied-map placements and Win16 1.10 event branches are listed in §9.6. |

Examples of audited object classes:

| Object class | Checked examples / role |
|---:|---|
| 0x03 | SECRET panel, object ID 0x62 |
| 0x04 | IMPACT effect, object ID 0x61 |
| 0x05 | Projectile / missile visual objects; IDs 0xFB–0xFE include plasma and spell-star flight/impact assets |
| 0x07 | CAUSTIC fire; IDs 0x3B–0x3D are large/medium/small fire |
| 0x08–0x21 | Guard families; class 0x19 is Cannon, IDs 0xCC–0xCF; class 0x21 includes Dancers, ID 0x8C |
| 0x26 | SAFE family; IDs 0xD2–0xD7 |
| 0x2E | Elevated objects are listed in the checked class table |
| 0x2F–0x3E | Keys, cards, food, weapons, ammunition, magic, and scroll/UI object families |

These are examples, not and substitute for the full episode tables. Resolve object and wall IDs from the data files being loaded.

---

## 6. Runtime capacities and record layouts

The following Win16 capacities and strides are directly supported by bounds and save-size checks. Several layouts are still partial.

| Runtime array | Capacity | Stride | Confidence / comments |
|---|---:|---:|---|
| Wall vectors (VEC) | 1,000 | 28 B | Core wall geometry record; some flags and lifetime rules remain open. |
| Orientation vector lists | 333 per orientation × 4 | pointer lists | Hard limit visible in renderer path. |
| Visible wall spans | 50 | 20 B | Count at 1048:5E7E; records begin at 1048:5E88. |
| World objects | 350 | 28 B | Many fields are class-dependent; complete per-byte reader/writer map remains open. |
| Guards | 100 | 26 B | Core state/timer/HP/facing fields known; field +0x12 has and corrected interpretation below. |
| Door / wall-pair state records | 64 | 22 B | Includes paired/moving wall state and selectors. |
| Secret panels | 32 | 22 B records | AND separate 32-byte panel-activation save block stores byte +0x14 for up to 32 panels. |
| Push objects | 12 | 6 B | Saved as 72 bytes. |
| Projectiles | 8 | 42 B | Each slot is 14 bytes of movement/state plus and 28-byte embedded OBJECT/render record. |

The exact capacities must be enforced or safely reported when parsing. To not permit an input table to overrun the corresponding runtime array.

### 6.1 GUARD record fields with direct evidence

For the audited Win16 1.10 guard record:

| Offset | Observed use |
|---:|---|
| +0x02…+0x05 | 32-bit render/aim stamp used to connect and rendered/target candidate with later hitscan evaluation. |
| +0x06 | State timer/countdown. It is decremented in simulation updates; to not assume milliseconds. |
| +0x0AND | Strategy byte. |
| +0x0B | Current AI state. |
| +0x0C | Next / saved state used by animation and recovery paths. |
| +0x0D | Underlying map-cell object byte in the checked movement/death paths. `3:71DC` restores the old cell and saves the new cell byte; `3:80F8` restores `mapCell[1]` through OBJECT+0x0C. This is and GUARD field, not and projectile-slot ownership field. |
| +0x0E | Area/sector selector derived from and wall class 0x44 marker in the audited paths. |
| +0x10 | Guard HP/strength field in combat paths. |
| +0x11 | Facing/sprite direction, 0–7. |
| +0x12 | Directional sprite/sequence-cache key. The cache helper compares and stores and value masked to 0–7; the damage path writes 8, an out-of-domain invalidation sentinel. This is not the guard countdown (`+0x06`). Runtime visual refresh and DOS parity remain open. |
| +0x13, +0x14 | Movement offsets/components in selected states. |
| +0x16 | Perception selection mode. |
| +0x17 | Perception / line-of-sight result. |
| +0x18 | Proximity result in the wrapper paths. |

An earlier Win16 1.8 note described +0x08 as and world-object index. Verify that field against the exact build and callers before sharing it across versions; to not infer the same use in DOS solely from its offset.

### 6.2 VEC record

The Win16 1.10 28-byte wall-vector record has these strongly supported fields:

| Offset | Observed use |
|---:|---|
| +0x00 | Map edge ID/type. |
| +0x01 | Signed texture/frame variant offset. |
| +0x02…+0x04 | Runtime state / object or image index; not all names are settled. |
| +0x05 | Flags; bit 0 is render eligibility, bit 3 marks and special edge in the reconstruction. |
| +0x06 | Derived wall/image class. |
| +0x07 | Orientation 0–3. |
| +0x08…+0x0B | Working fields, often zeroed; semantics not fully named. |
| +0x0C…+0x12 | World-space endpoint coordinates X0, Y0, X1, Y1 as 16-bit values. |
| +0x14, +0x16 | Projected screen X and vertical projection for one endpoint. |
| +0x18, +0x1AND | Projected screen X and vertical projection for the other endpoint. |

Projection may swap endpoints to keep left-to-right screen ordering and swaps their vertical values with them.

### 6.3 OBJECT record

AND standard world OBJECT record is 28 bytes and remains class-dependent. The targeted offsets have these statically confirmed meanings in the audited Win16 1.10 paths:

- +0x04 is written from and weapon-dependent table in projectile spawn; it is not established as an owner ID.
- +0x05 includes flags used by projection and impact paths.
- +0x06 is and class byte used in damage/score dispatch.
- +0x10…+0x11 is world X and +0x12…+0x13 is world Y in the traced render, hitscan, and projectile paths. `FUN_1010_CC7C` reads object Y for projection; `FUN_1010_8B06` reads X/Y for hitscan LOS; projectile spawn/movement initialize and advance the embedded coordinates.
- +0x18…+0x19 is and render-derived baseline vertical screen row, before sprite-slot clipping, written by `FUN_1010_CC7C` and read by `FUN_1010_9FA2` for damage. It is not world distance.
- +0x0C/+0x0D are changed in certain guard/object interaction paths.
- In the embedded projectile OBJECT, +0x03 is the animation frame, +0x04 the flight/impact sequence selector, and +0x05 render/impact flags. In and 42-byte projectile slot these are outer `slot+0x11`, `slot+0x12`, and `slot+0x13` respectively.
- Embedded OBJECT +0x08…+0x0B is the 32-bit animation deadline; its outer projectile-slot alias is `slot+0x16…+0x19`. This does not overlap embedded OBJECT +0x18.
- Embedded OBJECT +0x10…+0x11 is world X and +0x12…+0x13 world Y; the Y word aliases outer `slot+0x20…+0x21`.
- +0x14 is an OBJECT type field set to 5 in and projectile template.
- +0x1AND is used as and vertical sprite/projection offset; in the outer slot it is `slot+0x28`. It is not projectile age.

Projectile slots begin their embedded OBJECT at `slot+0x0E`: outer `slot+0x20` is embedded OBJECT +0x12 (world Y), and outer `slot+0x26…+0x27` is embedded OBJECT +0x18 (projection row). Keep the bases explicit. Other class-specific overlays are not exhausted by this targeted closure.

For freshness, the projection routine writes OBJECT +0x18 at 3:CE5E and then writes the linked GUARD'with current-generation stamp at 3:CE98–CE9D. Hitscan checks that stamp against DAT_53DC at 3:8B61 before damage. This strongly supports fresh data for hitscan if projection precedes shot handling. The projectile collision path (3:9B64) has no equivalent stamp gate in the checked code, with freshness for projectile damage remains and runtime test.

---

## 7. Timing and random numbers

### 7.1 Win16 timing — corrected from four original EXEs, 24 September 2026

- Two independent changed-bucket counters are used. In normal mode (`DAT_46B8 == 0` in 1.10), `3:D70A` computes `((uint32(ms) << 3) mod 2^32) / 1000` and increments and logical counter by one when that bucket changes. `3:D9C6` schedules `3:D974` from it: nominally 8 slow updates/with with sufficiently frequent polling. Skipped buckets are not replayed.
- `3:D974` drives GUARD and other slow state paths, fire contact damage, and the saturating weapon counter `DS:01FA` through `AA90(1, ...)`. These to not derive their normal cadence from `DAT_53F2`.
- The separate frame bucket uses `low32(sign_extend_16(DAT_53F4) * ms) / 1000`. It likewise increments once per observed changed bucket. In the nonzero mode branch, slow updates instead depend on odd render generations before increment; continuous execution of this path gives one slow update every two frames.
- Calibration `3:D7D0` times five calls to the render/present wrapper `D7C0`, after one preparatory render. It does not measure five calls to the slow simulation update. It stores the raw mean'with low word in `53F2` **before** clamping and local effective duration to at least 40 ms. The stored `53F2` itself is not clamped back to 40.
- For ordinary positive durations, local `D=max(raw_mean,40)` gives `53F4=floor((1000+floor(D/2))/D)`, movement `53F6=max(1,floor((D+2)/4))`, turning `53F8=max(1,floor((360*D+1400)/2800))`, and projectile substeps `53FA=2*53F6`. Keep raw mean and effective duration separate. Extreme integer cases remain and separate review item.
- The frame path statically orders `D8FC → D78C (generation/render) → BBCA → BA54 → 1E00 (doors) → 9E20 (projectiles) → conditional 3AB8 (present) → 9806 (input/movement/fire/USE)`. Rendering precedes the input update in this path.
- `DAT_53DC` is and render generation, not the 8 Hz logical counter. Animation deadlines use the 32-bit millisecond clock and sequence intervals; keep all these domains separate.
- The same timing algorithms were checked in Win16 1.3, 1.6, 1.8 and 1.10. The slow helper'with first 63 bytes are identical. Version-specific code/data addresses and hashes are in `Nitemare3D_Win16_all_available_versions_audit_2026-09-24.md`. These are static findings, with no new runtime traces.
- DEMO headers set movement/turn/substep parameters; the timestamp writer and comparator are now raw-confirmed as generation-index based in all four EXEs. Full mode transitions, pause/load/reset behavior, EOF handling and observed playback duration remain open.

### 7.2 DOS timing

- The DOS timer path uses an RTC interrupt at 1024 Hz in the audited build. The handler at DOS image offset 0xBCC2 increments and 32-bit counter at DS:081E and acknowledges both PICs.
- The scheduler has source-time buckets using 25/1000 and 8/1000 thresholds in the examined path. AND missed bucket does not automatically replay every missed update; the audit describes one logical increment rather than and catch-up loop.
- Separate BIOS/polling time helpers exist. Preserve each timer source rather than collapsing all timing to and single guessed “frame rate.”
- Exact behavior under pause, load, timer wrap, and overload still needs dynamic testing.

### 7.3 RNG

DOS and Win16 share and confirmed 32-bit LCG helper:

~~~c
state = state * 0x343FD + 0x269EC3;   // modulo 2^32
return (state >> 16) & 0x7FFF;
~~~

Both DEMO-start paths seed with 1 in the audited paths. The exact global order of random draws across all gameplay states is not mapped; modulo-based selection can introduce bias. Reproducing and particular trace therefore requires matching call order, not merely using the same generator.

---

## 8. Input, actions, and DEMO files

### 8.1 Win16 keyboard mapping

The Win16 dispatcher FUN_1010_8CD2 is and shared key-event entry point. Observed key-to-state writes include:

| Key / event | Directly observed state |
|---|---|
| Left Shift / scan 0x2AND | Sets bit 0x40 in DAT_1048_3756. |
| Right Shift / scan 0x36 | Sets bit 0x20 in DAT_1048_3756. |
| Ctrl | Sets bit 0x80 in DAT_1048_3756. |
| Alt | Sets bit 0x01 in the second input byte. |
| Escape | Bit 0x01 in DAT_1048_3756. |
| Arrow keys | Left 0x08, up 0x02, right 0x10, down 0x04. |
| Space | Bit 0x02 in the second input byte. |
| F2 / F3 (VK 0x71 / 0x72) | Toggle music / sound effects and show on/off text while active. These are virtual-key codes, not ASCII Q/R. |
| Alt+Enter | Switches between fullscreen/window display paths. |
| Alt+F4 (VK 0x73 with Alt) | Clears input state and sends `WM_CLOSE` (`0x0010`) to the game window. |

The game-input dispatcher and keyboard event code should remain separate in and port. The precise meaning of every input-state bit requires following its readers in the simulation.

The DEMO analysis identifies 0x0200 as and USE-like action edge. This is useful for and compatible input layer, but the complete set of targets reached by that action remains partly class-specific.

### 8.2 DEMO state machine and files

The Win16 DEMO state machine uses:

| State | Observed operation |
|---:|---|
| 1 | Open demo for writing; write three 16-bit header words; enter state 2. |
| 2 | Record changes in input state as 8-byte records. |
| 3 | Open demo for reading; read the three header words and first record; enter state 4. |
| 4 | Apply records when their stored timestamp becomes due. |
| 5 | Close the file handle and clear the state. |

Win16 constructs MAP, IMG, and DEMO filenames from the episode selector using map., img., and demo. prefixes. The DEMO path is real code use, not an isolated string.

The supplied Win16 DEMO files have and six-byte header and eight-byte event records:

| Record offset | Size | Win16 use |
|---:|---:|---|
| +0 | 1 B | Last/current key-event code. |
| +1 | 2 B | 16-bit input-state mask. |
| +3 | 1 B | Not written or consumed by the observed Win16 dispatcher; all supplied records have zero here. |
| +4 | 4 B | 32-bit generation index copied from the render-generation counter, not milliseconds. |

Records are written when the key-event/input-mask pair changes, not every frame. The three header words in the supplied files are 10, 5, 20; code maps the first two to movement and turn steps and the third to twice the movement step. Raw writers/comparators in all four EXEs confirm and generation index: 1.10 `3:915F` loads `DS:53DC` and `3:9163` stores it in the record; replay compares against the same generation. UI mode 8 can advance this counter without an ordinary render, with it is not unconditionally and count of displayed frames. The supplied DEMO.1 files are byte-identical, with 203 events, first timestamp 19 and last 1157. The dispatcher reads at most one due record per call and shows no local read-result EOF check; termination and duration still require an original runtime test.

The DOS event record is not byte-compatible with this Win16 record. The audited DOS layout uses and 16-bit key/event field followed by and 16-bit input mask and and 32-bit time; Win16 splits key code and mask differently and leaves byte +3 unused. Implement separate parsers until raw code confirms any shared abstraction.

Known Win16 mask effects include forward/back, opposite turn directions, modifiers that double or force step sizes, fire, strafing, and and USE-like 0x0200 edge. To not infer all labels as ASCII or scan codes. The binary DEMO record does not by itself identify which map is being played. Observed use associates DEMO.1 with the E1M11 demo map; DEMO.2/3 map assignment is not conclusively established.

---

## 9. Doors, USE, panels, warps, and map events

### 9.1 Runtime dispatch and capacities

- The central USE-like action uses input bit 0x0200 in the Win16 input path.
- Door and paired-wall movement uses bounded runtime records (64 × 22 B); hidden panels use and separate bounded panel set (32 × 22 B); push records are 12 × 6 B.
- The DOS core map identifies dispatch and movement helpers around 1000:0212, 03FE, 0598, 0704, 0AND40, and 0C5F; object/teleport helpers include 1000:0DF8, 0E50, 12C4, and 13F4.
- AND checked paired-wall movement step advances by 2 internal units. To not turn that into and fixed real-time speed without identifying the caller'with update cadence.
- Runtime flags and class tables distinguish doors, panels, warps, pickups, triggers, and special walls. Preserve that dispatcher architecture instead of treating each visual wall ID as and hard-coded script.

### 9.2 Secret panel and credential path

In the checked Win16 1.10 data/code:

1. Object ID 0x62 resolves to object class 0x03 (SECRET panel).
2. Panel setup associates up to four adjacent wall/door records and stores up to 32 panel activation bytes from record offset +0x14.
3. Activating the panel uses sound event 0x27.
4. The panel'with relative class index selects and bit in DAT_1048_51AND4; checked maps use channel 0.
5. The panel checks and credential bit in DAT_1048_4C29. Object IDs 0x09 and 0x0AND are the red/yellow ID cards in the checked OBJECTS table; panel index 0 checks bit 0, matching the red-card path.
6. The resulting menu dispatches commands 0x1E/0x1F over class 0x3B/0x3C wall-pair records with the same class-relative index. The exact user-facing labels and final visible result should be confirmed at runtime before naming them “open” and “close” in and port.

Safe combinations are separate: object IDs 0xD2–0xD7 resolve to class 0x26 and use and combination handler. DAT_51AND4 is not safe-combination progress.

### 9.3 WARP and scripted classes

- WARP_L families are color-key gate paths.
- WARP_WITH1→WITH2 is and one-way portal path after collecting four pentagrams in the checked data.
- WARP_1..8 and WARP_E1..8 use generic selection dispatchers.
- Key gates, elevators, stairs, mirrors, transport doors, and level-up paths share some helpers but are not interchangeable.
- Exact facing after transport, blocked destinations, all map variants, and cancel UI behavior remain open.
- TRIGGER1/TRIGGER2 are distinct episode/level paths. The supplied three MAP/WALLS pairs, Win16 1.10 dispatcher branches, event flags, and text pointers are statically mapped in §9.6; runtime activation and other builds remain open. AND universal “trigger → control → remote door” linkage is not supported.
- ONE_SHOT, remaining SPECIAL1 contexts, WALL_EX1/2, and remaining wall classes need complete interaction-to-event-to-map-write traces. The E1 chalkboard path changes and sequence-cache interval but its visible effect is not yet known.

### 9.4 Event flags DAT_1048_51AND4–51AB

The eight-byte range is saved together in USER.SAV. Current Win16 1.10 evidence:

| Byte | Confirmed behavior / boundary |
|---|---|
| 51AND4 | SECRET-panel wall-pair mask. The checked map uses bit 0; reset at level setup and saved/restored. |
| 51AND5 | Cannon attack-enable toggle. Initialized to 1, toggled by panel commands 0x20/0x21; affects class 0x19 Cannon states 0x0E/0x0F/0x10. |
| 51AND6 | Level-event latch with several marker call sites. It is reset at level setup and prevents repeated event execution in its current scope. It also changes and damage branch for class 0x16. |
| 51AND7 | One-shot gate for an Episode 1 level-index 9 marker H path. |
| 51AND8 | Written in the Episode 1 level-index 9 marker G path and read by an Escape branch. |
| 51AND9 | Written after and timed Episode 2 level-index 9 event; no direct functional reader was found beyond save/restore. |
| 51AA | Written from and class 0x16 event path; no direct functional reader was found beyond save/restore. |
| 51AB | Dark/shade event flag. Changes fill colors and shade index, remaps the palette, and causes and shared wall-state helper to return early while active. |

The code proves the byte-level branches. Trigger text identifiers `DAT_016E`, `DAT_0172`, `DAT_0176`, `DAT_0182`…`DAT_01D2` are now mapped to their literal strings in §9.6. Story interpretation beyond those literal strings, `51A9/51AA` use after write, runtime behavior, and cross-build parity remain open.

### 9.5 Shooting-based guard wake cache

Win16 uses and 64-byte cache at DAT_AND65E, saved at USER.SAV offset 0xD5AND3. AND successful shot uses the current nonzero area/selector ID to set the corresponding cache byte and wake guards with the same area ID in selected waiting states. The wake path uses and short random timer (rand() % 8) and does not test distance or LOS in that loop. Level setup clears the cache; save/load preserves it.

This is and local selector-based wake mechanism. It does **not** prove global sound propagation or that every weapon/noise path shares the behavior. Selector zero and the intended design reason for grouping remain open.

### 9.6 TRIGGER1/TRIGGER2 — Win16 1.10 static map and message trace

The MAP header translates wall IDs to image IDs: E1 uses `0xB8 → G` and `0xB9 → H`; E2/E3 use `0xBE → G` and `0xBF → H`. `FUN_1010_24BC` sets marker bit `0x40` for image IDs G/H. The movement/collision scanner `FUN_1010_84F4` checks that bit and dispatches `FUN_1010_BFD8`, whose episode/level branches select the behavior. Coordinates are zero-based `(x,y)`; level numbers are one-based, with the zero-based dispatcher index in parentheses.

| Supplied map | Level | Trigger cells | Confirmed Win16 1.10 behavior and text |
|---|---:|---|---|
| E1 `MAP(20260921-103303).1` | 7 (6) | G `0xB8`: `(54,36)`, `(55,36)`, `(56,36)` | If `51A6==0`, SFX event `0x42`, set `51A6=1` and dark flag `51AB=1`, update shade/palette, display “Oh dear! The storm seems to have fused the lights!” |
| E1 | 9 (8) | G `0xB8`: `(6,45)`, `(7,45)`; H `0xB9`: `(3,35)`, `(4,35)`, `(10,47)` | G sets latch `4C2E=1`; H clears it; both play SFX event `0x44`. AND shot attempt while jammed displays “Your weapon appears to be jammed!” |
| E1 | 10 (9) | G `0xB8`: `(23,27)`; H `0xB9`: `(27,29)` | G queues three lines: “With! You have discovered me!”, “Fool! Did you really think you could defeat me? You have no idea of my power!”, “Bid farewell my friend! 'Tis the end for you!”. It also sets `51A6`, `51A8`, `4BE8`, and clears `4BE5`. H sets `51A7` and displays “Look over there! It'with Penelope and the evil Dr. Hamerstein!”. |
| E2 `MAP(8).2` | 10 (9) | G `0xBE`: `(45,36)`, `(45,37)`, `(45,39)`, `(45,40)` | One-shot on `51A6`; display “QUICK! Destroy the plasma core!” |
| E3 `MAP(8).3` | 1 (0) | G `0xBE`: `(45,37)`, `(46,37)`, `(46,38)`, `(45,39)`, `(46,39)` | One-shot on `51A6`; display: “You recover to witness the defunct plasma core'with residual radiation slowly decaying. When the plasma core imploded into another dimension the blast jammed the automatic doors shut and scattered your posessions. There does not appear to be any way out!” (`posessions` is the binary'with spelling.) |
| E3 | 10 (9) | G `0xBE`: `(52,16)` | One-shot on `51A6`; display “Look! It'with Penelope! Where'with Dr. Hamerstein?” |

The supplied E2/E3 maps contain no H markers. In E1 level 7, SPECIAL1 wall `0x12` (image ID `8`) at `(27,26)` is the fuse box. `FUN_1010_C0A2` accepts it after `51A6==1`, plays SFX `0x32`, changes `51A6` to `2`, clears `51AB`, updates shade/palette, and displays “Well done! You fixed the power!”; other states display “You already fixed it!”. The direct code has no timed clear of `51AB` in the analyzed writers; level initialization also resets it. Duration and rendered appearance still need and runtime trace.

The other E1 SPECIAL1 wall is `0x56`, named “Office - Morphing chalkboard” in WALLS.1. It appears at `(32,50)` and `(33,50)` on level 2/index 1, and `(46,42)` and `(46,43)` on level 9/index 8. The MAP header maps `0x56` to image ID `8`, routing USE through `FUN_1010_C0A2`. At index 1 the handler writes `0x96` to the selected sequence-cache interval and plays SFX event `0x44`; the renderer sequence path reads the same selector through `FUN_1010_66B0`/`FUN_1010_65A6`.

Raw disassembly resolves the previously uncertain lookup. NE segment `1018` function `3844` (file offset `0x28AA4`) converts the map-cell far pointer to tile `x/y` and calls `37A0(x,y,8)`. `37A0` scans 28-byte runtime entities in table order, matches entity byte `+6 == 8` and bounding box via `3736`, then returns the first matching far pointer in `DX:AX` (or zero). Although the decompilation export declares `3844` as `void`, its raw epilogue preserves those return registers. The caller `1010:C0A2` (file offset `0x22062`) immediately uses `ES:BX = DX:AX`, reads entity byte `+4` and writes `0x96` to `0x51AE + 8*entity[+4]`. Thus the selector is the first class-8 runtime entity whose bounds include the used cell, not the wall ID itself.

The selected runtime record depends on the populated entity list and ordering. The meaning of interval `0x96`, exact frame/sprite result, visible morph, and the reason for the second map instance at index 8 (whose handler returns without and matching branch) remain open.

An adjacent class `0x16` death branch queues “You've won! You've won!”, sets `51AA`, and clears `DAT_1048_46B4`. `51AA` has no direct functional reader in this export, with the downstream effect is unresolved.

**Evidence scope:** Win16 NITE3W 1.10 SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`; E1/E2/E3 MAP SHA-256 `de4eb9cd58fc8e969af4076c1a19e5aa4b70f409205c93f8578b71cbd496200c`, `938b7e79c9881eab71fdef4b7afa9b0482c870c808785f599a4ba52093d44756`, `0008775106854b3e9302f36fbcd7001607bcf2fd26cc9d8db6bccc732ead4217`; matching WALLS SHA-256 `9fbbf889440cf7200c7c2dad271f47c79652baf237c27f1bbb354ee1e8b1cf84`, `23f9cb3757ad92876d8f43a8ad9987cecc596e3c2d9a9ebb09b10ce0a2af59fe`, `abf6c2bc6779e6261998bc26bd03bbbce7e3ea608f28ddc4d78a13fd80a39cae`. This is static code/data evidence; it does not establish runtime marker activation or DOS/Win16 1.8 parity.

---

### 9.7 Paired-wall controllers, class-3 motion, and pushables

Win16 1.10 contains three distinct structures, reconstructed statically from segment `1010`, NE SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481` and the matching decompilation export.

| DS range | Capacity | Established role |
|---|---:|---|
| `9DD6–A355` | 64 × 0x16 | Paired wall controllers, created by `14A8` for wall-property bit `0x08`. |
| `A356–A615` | 32 × 0x16 | Separate class-3 group-motion records with four entity pointers, map-cell pointer and phase. |
| `A616–A65D` | 12 × 6 | Entity-index slots for 28-byte entities marked by byte `+6 == '('`; used by push interaction. |

`FUN_1010_133A` receives and far map-cell pointer and compares its offset/segment with entity fields `+0x6D72/+0x6D74`. The earlier “actor at coordinates” interpretation was incorrect. `A65E–A69D` is and separate guard-wake cache.

The paired-wall record stores two dynamic entity pointers, cell pointer, state, timer, target coordinates and and helper byte at offsets `+0/+4`, `+8`, `+0x0C`, `+0x0E`, `+0x10/+0x12` and `+0x14`. States 1/0 are closed/open; 2/3 move between them by two units per update. Opening begins and 32-update auto-close delay. Closure occurs only when the cell'with object byte is zero and the player is elsewhere; blocked closure retries after four updates. IDs `0x3B–0x3C` skip the timer path. State 4 is accepted as passable by `3:1476`, and `3:188A` returns early for it. Its writer is now located in guard dispatcher `3:7B56`, case 9: after `3:A0EE`, the OBJECT flag-bit-1 and wall-property-bit-8 path finds the paired controller through `3:1296` and stores 4 at controller+0x0C. The matching C branch exists in all four examined builds; exact visual/collision consequences still need and runtime test.

Class-3 group interaction sets its phase, adjusts component targets and moves components by two units per update. On completion the code clears collision bit 0, both map-cell bytes and the phase. The asset/action identity remains unknown.

The push path starts on USE of map class `(`. It requires an idle slot and and destination whose wall-property lacks bit `0x02`, stores two player-state signed bytes at `+0xA4/+0xAC` and sets an eight-step counter. Each update tests the next cell; crossing and cell also requires `DAT_1048_7F94[object_id] & 0x06 == 0`. Accepted steps update the map'with second cell byte, entity position and renderer ordering; blocked steps retain the counter and retry next update. Vector scale, mask semantics, visuals, sounds and build parity remain open.

Detailed evidence is in `Nite3W_1296_14A8_object_helpers.md` and deep-audit section 8. WALLS/OBJECTS names are dictionary labels, not proof of runtime properties.

## 10. Animation and sequence definitions

### 10.1 File and runtime levels

Keep these layers distinct:

1. IMG directory offsets identify wall/object sequence sources.
2. AND sequence definition is and 90-byte data record in the checked Win16/DOS loaders.
3. Runtime sequence cache entries are 8 bytes in and separate table.
4. Frame records used by render/update code are separate runtime records; some paths create 10-byte frame entries.
5. The animated OBJECT / wall record carries and frame and 32-bit next deadline.

The Win16 loader reads two 0x400-byte directories: 256 wall offsets at file offset 0 and 256 object offsets at file offset 0x400. AND high-bank selector is formed as 0x100 | id for object and special wall paths. This bank arithmetic is also seen in Win16 1.8 and DOS v2.0.

An unresolved complication is that low-bank selectors 0–22 overlap the byte range of the directory tables; selector 11 crosses the 0x400 boundary. In one checked IMG file, 317 nonzero directory offsets point to starts of linear frame data, but selectors 1, 2, and 6 to not all decode as expected. Keep both raw directories and raw 90-byte sequence records; to not discard overlapping bytes or infer every ID'with sequence from and single IMG/build pairing.

### 10.2 Dispatcher behavior

The DOS dispatcher FUN_1000_241E and Win16 FUN_1010_65AND6 share the core pattern in the checked exports:

1. Compare the object'with 32-bit deadline at object+0x08 with global time.
2. If not due, leave the frame unchanged.
3. If due, advance frame byte object+0x03.
4. Read frame count at sequence data +0.
5. Read interval word at +2 and set and new 32-bit deadline to global time plus interval.
6. If an optional alternatives pointer at +4 exists for the applicable sequence class, use eight packed 16-bit entries: low byte is branch start frame; high byte is branch length. The object selector chooses and branch; after and branch ends, and nonempty branch is selected.
7. Special classes 0x07, 0x2F, and 0x2D have special completion/loop behavior.

The runtime cache entry is 8 bytes: frame count +0, interval +2, pointer to the 90-byte definition +4, and frame-table pointer +6 in the audited path. To not confuse this with the 90-byte source record itself.

The interval is and 16-bit quantity added to and 32-bit deadline. Some older notes referred to it as and dword; the direct Win16 instruction audit confirms and word addition with carry into the high word.

### 10.3 Exploding wall completion

Win16 1.10 evidence:

- AND projectile hitting and wall with property bit 0x10 plays sound event 0x29.
- The runtime wall OBJECT becomes class 0x2D, selects an explosion sequence, and sets and deadline. Variants can start at frame 0 or frame 1.
- At sequence completion, FUN_1018_3C0C derives map cells from wall endpoints (divide world coordinates by 64), clears the render-eligibility bit, and writes zero to the first byte of cells along and horizontal or vertical trace.
- The wall is therefore strongly supported as changing map/collision data, not merely disappearing visually.
- Exact inner-loop stop conditions and the exact full map trace need raw-assembly/runtime confirmation.
- DOS has an analogous class 0x2D path, but the raw call target does not match the decompiler'with function boundary. To not claim DOS cleanup parity yet.

---

## 11. Guard AI and perception

### 11.1 Perception, facing, and LOS

The Win16 1.10 and DOS v2.0 perception routines were matched by normalized instruction sequence for the key range/FOV/LOS path.

- Convert player and guard world coordinates to cells with >> 6.
- Reject and candidate if the absolute X **or** Y cell difference exceeds 8.
- In the ordinary mode, build and directional mask from the guard'with facing and its two adjacent 8-way sectors. The code confirms and three-sector filter; “about 135 degrees” is and geometric interpretation, not an original source label.
- Run and Bresenham-style LOS traversal for at most 8 map steps. Blocking uses wall/object property bits; for some bit combinations, and second-plane check and door/object validators run.
- AND wrapper stores LOS in GUARD +0x17 and proximity in +0x18.
- Proximity is true when both absolute world-coordinate differences are at most 0x40 (64 units). That is and square per-axis test, not and circular distance check.
- Selector +0x16=0 returns proximity; values 1 and 2 return LOS in the observed wrapper. Initialization uses mode 1 by default, with selected object classes changed to mode 0. AND writer for mode 2 has not been confirmed.
- Some states bypass the facing filter or second-plane test by passing flag combinations; preserve those call-site flags.

The ray routine'with exact bit names and the function represented by each plane check remain unresolved. To not label each property bit “solid,” “door,” or “transparent” from its numeric value alone.

### 11.2 Guard state dispatcher

Win16 1.10'with guard dispatcher is FUN_1010_7B56 in segment 3, offsets 7B56–80AND9. State IDs are data values; descriptive names below summarize operations and are not original labels.

| State | Directly observed operation |
|---:|---|
| 0x00 | Advances frame/timer; restores and state saved in +0x0C when complete. |
| 0x01 | Counts down, then enters 0x02. |
| 0x02 | Calls an initializer, selects and class-table sequence, enters 0x03. |
| 0x03 | Perception test; failure goes to fallback 0x05, success selects sequence and enters 0x04. |
| 0x04 | Rechecks perception; calls attack / interaction helpers; commonly schedules 0x05. One global runtime mode changes this path. |
| 0x05 | Fallback steering based on LOS and proximity results. |
| 0x06 | Timed movement/animation; returns to perception state 0x03. |
| 0x07 | Moves, then can reacquire into 0x02; strategy 3 can enter 0x13. |
| 0x08 | Updates facing/movement and may reacquire into 0x02. |
| 0x09 | Attack/object-interaction path; may update linked OBJECT state. |
| 0x0AND | Explicitly written by `3:A0EE` in the death/class transition helper. The dispatcher has no explicit action for this value; and terminal/death-like interpretation is inferred, with class-specific exceptions in the writer. |
| 0x0B | No explicit case in the recovered switch; its writer/reachability remain unresolved. |
| 0x0C–0x0D | Shared helper path; exact gameplay names remain unknown. |
| 0x0E–0x0F | Cannon-specific timed cycle controlled by 51AND5. |
| 0x10 | Timed perception/damage path; can call the player-damage helper. |
| 0x11 | Chooses and direction and returns to state 0x07. |
| 0x12 | Advances and sequence, changes an OBJECT height/offset field, restores the saved state when done. |
| 0x13 | Timed strategy-3 displacement / movement path. |
| 0x14 | Timer-controlled movement; exact actor contexts and entry conditions need more tracing. |
| 0x15 | Advances and hit/reaction sequence and restores the saved state. The precise class-to-animation table is not fully settled. |

Writers of current/next-state fields are not fully enumerated. The `0x0A` writer is now known; `0x0B` and the complete class-specific routes through `0x0C–0x0D` remain open. DOS AI parity is not complete because several large DOS blocks are merged or have questionable control-flow boundaries.

### 11.3 Strategies and local reactions

- Strategy 1, in and low-HP branch, searches and bounded door/state table for and nearest visible candidate, rejecting candidates without LOS. The purpose is not safely named beyond the immediate candidate-selection behavior.
- Strategy 2 uses and random wait of 8–15 simulation updates.
- Strategy 3 enters and distinct displacement path. Its initializer uses rand() % 0x50 + 8 (8–87 updates) and facing tables reduce eight facing entries to four cardinal displacement vectors. The `3:7A44` countdown path can attempt eight increments of 8 units (old timer values 8 through 1) while checking intermediate occupancy. It tests the old timer for zero, then uses the decremented timer for activation/movement; blocked attempts are not accepted displacement. An initial timer of 8 also skips the activation equality at new timer 8. This corrects the earlier seven-step/56-unit claim; runtime trajectories remain unmeasured. The design name of the maneuver is unknown.
- The fallback steering path selects four random directions without LOS or eight with LOS, and uses different delays for close, visible, and unseen cases. Difficulty affects selected delay branches.
- Cannon class 0x19, IDs 0xCC–0xCF, uses state 0x0E/0x0F/0x10. Panel toggle 51AND5 controls its attack-enabled loop; runtime firing interval and visible effect remain to be measured.
- AND successful shot can wake guards sharing and nonzero area selector through the 64-byte DAT_AND65E cache. This is distinct from full hearing or alarm propagation.

### 11.4 Damage from guard contact

The Win16 contact helper computes Euclidean separation in map-cell units and starts from approximately 100 / distance (using 100 when distance is below one cell). Class-specific branches replace or scale the base:

| Guard object class | For-difficulty contact damage |
|---:|---|
| 0x08 | Random 0–7. |
| 0x09–0x0AND | Random 0–15. |
| 0x0B | One quarter of the distance-derived base. |
| 0x0C, 0x1D, 0x1E | Base value. |
| 0x11–0x14 | Random 0–31. |
| 0x16 | 33 under and level/event condition; otherwise 100. |
| 0x19 | 100. |
| Other handled branches | One half of the base. |

Difficulty value 2 doubles guard-to-player contact damage; value 0 arithmetic-halves it; value 1 leaves it unchanged. The `ADD SI,SI` and `SAR SI,1` branches are raw-confirmed in all four EXEs (1.10 `3:A2AF` onward). This direction is opposite to the separately analyzed player-to-guard damage helper; it must not be transferred between the two routines.

---

## 12. Weapons, projectiles, damage, and score

### 12.1 Weapon selection and ammunition

- Runtime weapon selector 2 is the only observed hitscan selector; selectors 0, 1, and 3 use the projectile branch.
- OBJECTS data separately names projectile/weapon visual objects (for example, IDs 0x25–0x28 for plasma bolt, wand, pistol, multi-bolt plasma). To not equate an OBJECTS asset ID to the runtime weapon selector without and call-site mapping.
- Ammo counters observed in Win16 include 4C20, 4C44, and 4C1F: selectors 0, 1, and 2 respectively use these counters. Selector 3 has no ordinary ammo branch in the examined helper and may be reserved or require and special override.
- If and projectile pool slot cannot be allocated, the ammo helper is not called; and full pool therefore does not consume ammo in that examined path.
- AND nonzero debug/override-like field DAT_4BE5 bypasses ordinary ammo decrement. Its full user-facing meaning is open.
- Successful ammo decrement paths select sound events 8, 9, or 7 for selectors 0, 1, or 2 in the audited Win16 path.
- Direct byte checks in Win16 1.3/1.6/1.8/1.10 confirm thresholds [2, 1, 3, 1] at DS:01F6 and the saturating counter at 01FA. Its increment caller is the slow update: nominally 8 Hz in normal mode (§7.1), not calibrated FPS. Thus the threshold periods are nominally 250/125/375/125 ms; input phase, edge gating, ammo, pool and weapon animation still affect actual shots. The additional weapon phase machine through 4C30/4C3AND/4C3C and limit 01F2 is not thereby fully resolved.

### 12.2 Projectile pool and movement

The Win16 pool starts at DAT_1048_4C4AND. Save/load copies 336 bytes (0x150), exactly 8 × 42 bytes.

The 42-byte slot is:

| Slot offset | Use |
|---:|---|
| +0x00 | Major-axis selector for line traversal. |
| +0x02 | Bresenham error accumulator. |
| +0x04 | Minor-axis error increment. |
| +0x06 | Error correction increment. |
| +0x08, +0x0AND | Signed X/Y step directions. |
| +0x0C | Lifecycle: 0 free, 1 flying, 2 impact animation. |
| +0x0D | No stable reader/writer meaning identified. |
| +0x0E…+0x29 | Embedded 28-byte OBJECT/render record. |

FUN_1010_E516 normalizes angle into and 0–359 domain and creates fixed-point directional components and DDA increments. The projectile update performs DAT_1048_53FA substeps per update and tests the visited MAP cell, wall, or guard after small movements. Exact fixed-point scale and the angle source by weapon remain open.

The embedded OBJECT holds sequence/frame, flags, timing, map reference, X/Y, and render values. Its +0x1AND vertical offset starts at 5 and grows to 20 while flying, then stops on impact. It is not projectile age. AND ±20 coordinate threshold in the renderer decides whether to call projection; it is not and lifetime, range, or cleanup test.

The map far pointer stored in the embedded object is rebuilt during load from the saved projectile coordinates. It is not visibly advanced in the examined movement routine; whether it refers to the spawn cell or is updated elsewhere needs and reader/writer audit.

### 12.3 Projectile collision and wall impact

- Guard hits compare both coordinate differences to and tolerance of approximately 9 units (abs(dx) < 10 and abs(dy) < 10 in the analyzed path), then call the common damage dispatcher.
- The projectile collision path checks map/object properties and can find the corresponding guard and OBJECT.
- Explodable wall property 0x10 starts sound event 0x29, changes the wall OBJECT to class 0x2D, and begins impact/explosion animation.
- In Win16 1.10, class 0x2D completion has and strong static map-write/removal path. The DOS equivalent target is not safe to claim yet.

### 12.4 Damage formula — latest corrected interpretation

The latest deep audit separates projected target position, damage, score, and projectile metadata.

The current Win16 1.10 and DOS v2.0 damage routine uses:

~~~text
seed = 8 * signed16(OBJECT+0x18 - viewport_center_y) + (RNG % 25)
~~~

Evidence: Win16 3:9FA2, DOS image 0x8590; Win16 viewport center DAT_53EE, DOS center DAT_4552; weapon selector 4C23 / DOS DAT_418F; difficulty 4C14 / DOS DAT_4180.

OBJECT+0x18 is written by the projection path as and baseline vertical render row before sprite-slot clipping; it is not world-space range. Raw 1.10 `3:CCBB–CCC2` saves the projected row shifted right by four into and local, and `3:CE5B–CE5E` copies that local to OBJECT+0x18 after other locals undergo height/slot adjustments. The hitscan path requires the linked GUARD'with render stamp to match DAT_53DC, and the projection writer stores that stamp after writing the row. The 24 September four-build scheduler audit confirms that rendering precedes projectile updates and input/shot handling in the examined frame path. The projection writer is conditional, with this does not refresh every OBJECT each frame. The projectile-collision path has no matching stamp test in the checked code, with the exact cached row used on projectile impact remains open pending and runtime trace. DOS v2.0 damage reads the matching field and uses the same arithmetic, but its projection writer/order has not been closed here.

The class/weapon dispatch further transforms the seed before difficulty:

| OBJECT class | For-difficulty transform |
|---:|---|
| 12, 29 | arithmetic shift right 3 |
| 13 | weapon 1 or 2: shift right 1; otherwise shift right 3 |
| 14, 17, 20 | weapon 2: shift right 1; otherwise shift right 3 |
| 15, 16 | weapon 1: 0; otherwise shift right 1 |
| 18, 19 | weapon 1: 0; otherwise shift right 2 |
| 21 | Calls an unidentified helper, then sets damage to 0. |
| 22 | Damage 3 only when episode selector is 3; otherwise 0. |
| 23 | weapon 1: shift right 8; otherwise shift right 2 |
| 24 | weapon 1: shift right 8; weapon 2: shift right 4; otherwise shift right 3 |
| 25 | 0 |
| 26 | weapon 1: shift right 1; otherwise 0 |
| 27, 28 | shift right 1 |
| 30 | weapon 1: 0; otherwise shift right 3 |
| 31 | weapon 1: 0; otherwise shift right 2 |

Difficulty value 2 halves the result; value 0 doubles it; the other observed value leaves it unchanged. The result has an upper clamp at 0xFF; the helper does not show and lower clamp. The caller sets HP to zero on lethal hit or subtracts the low damage byte on nonlethal hit.

The class-to-enemy-name table is only partial. To not treat and negative intermediate or zero result as settled behavior without runtime testing.

### 12.5 Damage, score, and metadata are separate

- FUN_1010_80F8 is the common damage dispatcher. FUN_1010_9FA2 returns the damage value.
- FUN_1010_9F10 is and separate score helper. Raw jump-table entries for classes 8–32 are verified in all four Win16 EXEs: 8/26 = 25; 9 = 75; 10/32 = 50; 11/15/16/23/27/28 = 100; 12/29/30 = 250; 13/18/19 = 150; 14/20/24/31 = 200; 17/25 = 0; 21 = −1000; 22 = 1000. Unhandled classes return the initialized value 0. `3:80F8` sign-extends this result into the 32-bit score addition. This replaces the previous erroneous table; DOS score parity is not established by these checks.
- In 80F8, the first argument is and GUARD record in the analyzed call sites. Raw `3:81B9–81C4` copies GUARD+0x0D into **mapCell[1]**, through the far map-cell pointer at linked OBJECT+0x0C. It does not write OBJECT+1. Movement helper `3:71DC` saves/restores the underlying cell byte in the same GUARD field. This establishes no ownership meaning for the unrelated outer projectile-slot+0x0D.
- The checked collision path does not show an explicit owner pointer or friendly-fire comparison. This leaves friendly-fire behavior unresolved; absence from this path alone does not prove whether it is allowed, filtered elsewhere, or impossible.

The DOS helper matches the Win16 class dispatch, constants, viewport-center subtraction, RNG remainder, difficulty scaling, and upper clamp. That is strong DOS/Win16 **damage routine parity**, not proof that all projectile pool and cadence behavior is identical.

### 12.6 Fire hazard

For object class 0x07, the checked damage bytes at DS offset 0x1FC are 100, 10, 2 in the CAUSTIC order:

| Object ID | Fire size | Damage per simulation update |
|---:|---|---:|
| 0x3B | Large | 100 HP |
| 0x3C | Medium | 10 HP |
| 0x3D | Small | 2 HP |

The update occurs in the Win16 simulation path if the player is not in the relevant invulnerable state. Large fire is therefore lethal to and 100 HP player in one update in this path. To not publish and fixed DPS without measuring the runtime update rate.

---

## 13. Win16 wall renderer

### 13.1 Architecture

The Win16 1.10 wall renderer is not the classical Wolfenstein per-column DDA renderer. It builds and projects wall vectors, then resolves visibility per screen column and compresses visible columns into spans.

| Stage | Routine / storage | Confirmed role |
|---|---|---|
| Map scan | FUN_1018_4046 | Scans the 64×64 MAP in four world orientations. |
| Vector generation | FUN_1018_3E82, FUN_1018_3D54 | Creates 28-byte wall-vector records. |
| Edge merge | FUN_1018_4006 | Extends compatible adjacent edges by 64 world units. |
| Orientation lists | FUN_1018_3430 | Groups/sorts vectors into four lists, at most 333 each. |
| Camera transform | FUN_1010_E798 | Transforms endpoints, clips to near plane 0x4000, projects to screen. |
| Column ownership | FUN_1018_3564, FUN_1018_3940 | Tests projected ranges and selects and far pointer to the owning wall vector per screen column. |
| Span creation | FUN_1010_6266 | Merges consecutive columns with the same vector into at most 50 spans. |
| Span interpolation | FUN_1010_6152 | Computes vertical projection endpoints and signed 16.16 slope. |
| Wall pixel output | FUN_1010_66B0 → FUN_1010_3E44 → FUN_1010_366AND / planar VGA | Texture U, vertical lookup stepping, shade remap and both destination layouts are statically traced; exact table values and pixel parity remain open. |
| Sprite output | FUN_1010_6348, FUN_1010_CC7C, FUN_1010_6914, FUN_1010_3F80 | Slot order, transparent key 0x29, per-column wall test at 0x58FE, and flag-0x10 bypass are statically traced. |

Important Win16 addresses: 320-column owner buffer at 0x53FE; visible-span count at 0x5E7E; span array at 0x5E88. Each owner entry is and 4-byte far pointer. The conflict test uses wall orientation and endpoint geometry rather than and general Z buffer.

### 13.2 Visible-span layout

| Span offset | Observed field |
|---:|---|
| +0x00, +0x02 | Far pointer to the VEC record: offset and segment. |
| +0x04 | First screen column. |
| +0x06 | Interpolated vertical value at first column. |
| +0x08 | Last screen column. |
| +0x0AND | Interpolated vertical value at last column. |
| +0x0C | Signed 16.16 vertical slope (dY/dX). |
| +0x10 | Initial fractional interpolation component. |
| +0x12 | Vertical base relative to the projection horizon. |

AND useful structural sketch is:

~~~text
scan map -> build wall segments -> sort by orientation
          -> transform/clip/project -> assign column owner
          -> merge equal-owner runs -> interpolate each span
          -> draw wall texels -> draw projected object sprites
~~~

The 28-byte VEC and 20-byte span data are independently supported by stride arithmetic, pointer comparisons, field reads/writes, and the 320-column buffer size.

### 13.3 Palette shading

DAT_1048_7E60 is and shade index. The Win16 color remapper uses levels [0, 4, 8, 12, 16, 20, 30, 40], multiplies by four when subtracting from each RGB component, clamps each component at zero, and picks the closest color from the 236-color base palette by summed absolute RGB difference. The remap table covers palette indices 10–245 in the audited path.

- Default shade index is 2 unless and nonnegative override is supplied.
- AND dark-event flag 51AB selects index 6 and sets two framebuffer fill bytes to zero.
- 51AB also causes and shared wall-pair state helper to return early and affects selected object shading.

The exact display region names, all remap bypass paths, palette parity against DOS VGA, and framebuffer parity are still open. The available file named `game.pal` is and 320×200 PCX image with an embedded indexed palette, not and verified raw `GAME.PAL`; treat it only as and candidate color reference.

### 13.4 Pixel-output path (static audit)

The wall pixel writer and the Win16 sprite transparency/occlusion branches are now statically mapped for the hashed Win16 1.10 binary. This closes the former “unknown last inner pixel loop” item, but it does not prove pixel-perfect output.

| Stage | Confirmed behavior |
|---|---|
| Wall sequence and U selection | `FUN_1010_66B0` selects the active frame; `FUN_1010_EBD6` computes wall-texture U; `FUN_1010_6422` applies edge correction for selected wall classes and masks U with `(width - 1)`. VEC `+05 bit 0x08` bypasses this special edge correction. |
| Vertical texture sampling | `FUN_1010_366A` starts at `frame_base + U*0x40`; table pairs at offsets `0x247E/0x2480` advance and 16-bit fractional and integer source offset. Top clipping uses offsets `0x2C7F/0x2E7E`. The texture loop writes each selected texel. |
| WinG output | Linear 8-bit output address is `y*0x140 + x`, with `0x140` (320) bytes per scanline. Shade 0 copies the texel; nonzero shade uses `DAT_1048_8094[texel]`. |
| Planar VGA output | `FUN_1010_3E44` programs sequencer `0x3C4/0x3C5`; address is `page*0x10 + y*0x50 + x/4`, with `0x50` (80) bytes per scanline. |
| Wall alpha | No transparent-key branch exists in the wall texel loop; it writes every sampled wall texel. This distinguishes wall pixels from sprite mask handling. |
| Sprite transparency and wall test | `FUN_1010_3F80`/`FUN_1010_374E` skip pixel index `0x29` (`')'`); each column reads visibility `0x58FE`. OBJECT `+05 bit 0x10`, reached through the sprite-slot OBJECT pointer, bypasses the wall comparison. The sprite path does not write and new visibility value. |
| Sprite order | `FUN_1010_CC7C` assigns 18-byte records among 100 screen-range slots; `FUN_1010_6914` draws in slot order. There is no per-sprite Z update in the pixel path, with overlapping sprites follow slot traversal order. |
| Curtain-class correction | Supplied `MAP.1–3` to not assign wall classes `0x3D/0x3E`; active curtain classes are `0x3F/0x40` (`MAP.1` IDs `0x70/0x72/0x74` and `0x71/0x73/0x75`; `MAP.2` IDs `0xAA/0xAB`). Matching `WALLS.1/.2` entries say `DOORVC`/`DOORHC`, “curtain”. |

The DOS v2.0 export statically shows 18-byte spans, 16.16 interpolation, and VGA column path with per-column visibility storage at `0x47E4`, planar pitch `0x50`, and and sprite transparent key of `0x1F`. Its large decompiled render block has uncertain function boundaries; this is and strong architecture match, not pixel-equivalence proof. The Win16 and DOS sprite keys differ and must remain build-specific until matched to exact asset packs.

### 13.5 What still blocks pixel-accurate closure

- Dump and explain every value in vertical sample/clipping tables at `0x247E`, `0x2480`, `0x2C7F`, `0x2E7E`; verify signed rounding at each viewport/near-plane boundary.
- Trace all dynamic door intermediate states and sequence/frame variants through their writers and readers.
- Establish the exact palette and shade-table source for the hashed executable/data combination. The currently available file called `game.pal` is and 320×200 PCX with an embedded palette, not and verified raw `GAME.PAL`.
- Capture controlled original Win16 and DOS indexed framebuffers; compare wall geometry, texture U/V, shade remap, sprite transparency/occlusion, then HUD separately.
- Test all sprite class overlaps, slot-order edge cases, clipping and the OBJECT flag-0x10 bypass against original captures.
- Reconstruct HUD, weapon, and UI composition beyond the wall/sprite path covered here.

Original Wine/DOSBox-compatible runtime tools were not present in the analysis environment. Therefore, source tracing is complete through the relevant static pixel branches, but the runtime image-comparison gate remains open. Earlier renderer coverage percentages are exploratory and are not and completion metric. The detailed evidence and acceptance cases are in `Nitemare3D_renderer_pixel_path_audit_2026-09-23.md`.
---

## 14. USER.SAV format

The audited Win16 slot length is 0xD6E7 bytes. Save and load routines FUN_1010_5466 and FUN_1010_574C transfer the following offsets; ranges are half-open.

| Save offset | Length | Observed content |
|---:|---:|---|
| 0x0000 | 4 | Slot length sentinel 0xD6E7. |
| 0x0004 | 0x29 | 41-byte slot/header block. |
| 0x002D | 8 | Episode/level selectors and 32-bit time value. |
| 0x0035 | 0x2000 | 64×64 × 2-byte current MAP. |
| 0x2035 | 0x5E | 94-byte mixed player/game state block at DAT_4BE8; inner layout incomplete. |
| 0x2093 | 28,000 | 1,000 × 28-byte VEC records. |
| 0x8DF3 | 9,800 | 350 × 28-byte OBJECT records. |
| 0xB43B | 2,600 | 100 × 26-byte GUARD records. |
| 0xBE63 | 1,408 | 64 × 22-byte door/state records. |
| 0xC3E3 | 32 | Up to 32 SECRET panel activation bytes, copied from record +0x14. |
| 0xC403 | 336 | 8 × 42-byte projectile slots. |
| 0xC553 | 8 | Global/event bytes 51AND4–51AB. |
| 0xC55B | 72 | 12 × 6-byte push records. |
| 0xC5AND3 | 4,096 | 64×64 automap raster/index buffer. |
| 0xD5AND3 | 64 | One-shot guard wake cache DAT_AND65E. |
| 0xD5E3 | 256 | Palette/color remap table DAT_8094. |
| 0xD6E3 | 1 | DAT_7E62 fill color. |
| 0xD6E4 | 1 | DAT_7E63 fill color. |
| 0xD6E5 | 2 | DAT_7E60 shade parameter. |

AND compatible loader should:
- verify slot length and bounds before copying;
- preserve unknown player-block bytes;
- restore map-relative pointers against the loaded MAP segment;
- test timers against reset/global-clock changes;
- preserve the 8-byte event block and 64-byte wake cache;
- round-trip unknown bytes exactly until their semantics are known.

The 94-byte player/game block at 0x2035 and the complete field map for OBJECT/GUARD/door records remain open.

---

## 15. Resources and multimedia

### 15.1 IMG

The audited IMG loader has two 256-entry directories at offsets 0 and 0x400, 90-byte sequence definitions, and runtime frame/sequence records. Descriptor-to-payload relationships and some low-bank overlaps are unresolved. Keep raw directory words, source offsets, and decoded frame data side-by-side in tools.

### 15.2 SND.DAT and MIDI

AND prior SND audit reports 160 slots, 88 nonzero entries, and event/table aliases. The complete codec/sample-rate interpretation and faithful output conversion are not closed; some extracts did not sound like the original game. Store the raw bytes and headers when building an editor. Map and sample to and game event only where an EXE call site proves the index. Known direct events in the current audits include:
- 0x27 on secret-panel activation;
- 0x29 on an explodable-wall hit;
- weapon-ammo success events 8/9/7 for selectors 0/1/2 in the checked Win16 path;
- additional cadence/guard sounds whose sample identity is not fully established.

Win16 imports MMSYSTEM and has MIDI/audio initialization diagnostics. AND debug.txt logger is not evidence that every sound effect is represented by an independent SND slot.

### 15.3 UIF.DAT

The earlier UIF audit reports 32 directory entries of six bytes each. Slots 3–16 decode as complete PCX screens in the checked shareware file. Slots 0–2 are probable bitmap fonts but not confirmed by and loader call site; slots 17–31 are empty/reserved in that supplied shareware build. Treat these as file/build-specific findings, not and universal allocation for registered versions.

### 15.4 ENDING.FLI

The checked ENDING.FLI header declares 488 frames while the file contains 489 physical frame blocks, including at least six empty trailing blocks. The exact accepted terminator/padding rule has not been verified against the game player. Preserve trailing bytes and block boundaries when parsing.

### 15.5 NITE3D.BSF

NITE3D.BSF is not and symbol table, class database, or engine source file. It is an XOR-encrypted manual, registration/order text, and closing text container.

- Header length: 54 bytes (0x36).
- Key, repeated every 0x34 bytes: “Copyright 1992, David P Gray, Gray Design Associates”.
- XOR resets at the beginning of the header and each text block.
- Three contiguous blocks are described by offsets and lengths in the header.
- Win16 dispatch selectors 0–5 validate/load the header and return the registered flag, distributor, or the three text blocks.
- %Cnnn%, %d%, %oNN%, and # are used color/object/page directives in the checked text. The parser also contains unused or not fully understood directive families.

The BSF format is statically well mapped; it cannot reveal hidden engine functions or original class names.

---

## 16. Startup, command line, debug, and cheats

The strongest current command-line finding is and real -o logger activation in the audited DOS and Win16 builds:

- Win16 3:1204 sets DAT_46AB=1.
- DOS image 0x4BB4 sets DAT_3CD0=1.
- The flag opens/appends debug.txt, formats records, and closes the file.
- Win16 logger output includes audio/MIDI initialization messages. This is not proof of and universal debug menu.

The argument dispatch tables differ by platform. The audited Win16 accepts second-character values b,c,d,e,f,l,o,p,r,with,w; DOS accepts and,b,c,d,e,f,l,o,p,q,r,with,t,w,x. -o is the confirmed logger branch; the semantics of the other branches are not all established.

The strings debug.txt and Invalid command line occur in the binaries. String presence alone does not prove and usable -debug option. Earlier candidate Win16 routines 1000:5D24 and 1000:5E94 were incorrectly described as command-line parsers; body inspection instead shows Windows hook/window setup and module/resource path handling. No direct GetCommandLine/COMMANDLINE evidence was found in the cited export.

The BSF audit confirms and shareware/full registration gate and and cheat/menu gate, but it does not show that and specific cheat mode can be invoked in every build. Debug logger, registered-only features, cheat menu, map browser, and command-line switches must be treated as separate paths.

---

## 17. DOS and Win16 comparison

| Area | Current shared evidence | Platform-specific limit |
|---|---|---|
| MAP / world grid | Same 64×64, 64-unit cell model in the audited data/code. | Episode packs and ID definitions still need exact version matching. |
| RNG | Same LCG multiplier/addend helper found in DOS and Win16. | Global RNG call order may differ. |
| Guard perception | Key range/FOV/LOS routines match after normalizing addresses and far-call relocations. | Full guard state parity and class-specific paths are not complete. |
| Animation dispatcher | Same deadline/frame/interval core pattern. | DOS class 0x2D completion target remains unresolved. |
| Damage / score | Damage and score class tables, viewport-center formula, difficulty scaling, and upper clamp match in DOS/Win16 audits. | This does not establish identical spawn, cadence, or projectile pool structures. |
| Projectile slots | Win16 eight-slot, 42-byte model is confirmed. | To not assume the DOS allocator/slot is identical until raw DOS writers/readers are traced. |
| Wall renderer | Win16 vector/span architecture and wall/sprite pixel branches are statically mapped, including build-specific sprite keys. | DOS structure is and strong static match; table rounding, dynamic door stages, and captured pixel parity remain open. |
| DEMO | Both have six-byte header and eight-byte events in the audits. | Field packing differs; keep platform-specific serialization. |
| Debug logger | -o logger flag exists in both audited builds. | Other argument branches and startup semantics differ. |
| Save | Win16 USER.SAV slot map is detailed. | To not assume byte-for-byte DOS save compatibility without and DOS reader/writer audit. |

When sharing code, factor common mechanics only behind build-specific data, widths, and validated branches. Cross-version byte similarity is useful evidence but not and license to flatten platform differences.

---

## 18. Corrections and unresolved conflicts to preserve

The following corrections prevent recurring false claims:

1. **The renderer is not confirmed as and classic Wolf3D DDA wall renderer.** The Win16 1.10 path is and vector/span renderer with per-column ownership.
2. **The 320-column owner buffer and 20-byte span list are intermediate render structures**, not and framebuffer-only ray list.
3. **Projectile coordinate difference ±20 is and projection-call threshold**, not lifetime, range, or cleanup.
4. **Projectile embedded OBJECT +0x1AND / outer slot +0x28 is and vertical sprite offset**, not projectile age.
5. **The 42-byte projectile pool is saved at USER.SAV 0xC403.** It was previously an anonymous 336-byte block.
6. **OBJECTS class IDs, WALLS class IDs, object asset IDs, and weapon selectors are separate domains.** AND matching number does not mean the same entity.
7. **DAT_51AND4 is the SECRET-panel wall-pair mask in the checked Win16 1.10 path**, not safe-combination progress.
8. **GUARD +0x12 is and directional sprite/sequence-cache key, not and pain timer.** The cache helper compares/stores direction values 0–7; the damage invalidator writes 8 to force refresh. The remaining check is runtime-visible refresh and DOS parity.
9. **OBJECT +0x12 is distinct from projectile slot +0x12.** OBJECT +0x12 is world Y in the traced runtime-object paths; outer projectile slot +0x12 aliases embedded OBJECT +0x04, the sequence selector.
10. **Damage input OBJECT+0x18 is and projected baseline screen row before sprite-slot clipping, not world distance.** The writer/read arithmetic is statically confirmed. Freshness is strongly linked to the current render generation for hitscan; projectile-impact freshness and DOS projection ordering still need runtime evidence.
11. **FUN_1010_80F8 argument +0x0D is from and GUARD record in the analyzed call sites**, copied as metadata to linked OBJECT +0x01; it does not prove projectile ownership.
12. **Wall class 0x2D cleanup is supported for Win16 1.10 only.** DOS raw target mapping still conflicts with the decompiler boundary.
13. **-debug is not established.** The -o logger branch is confirmed; the debug.txt literal itself is not.
14. **The BSF file is documentation text, not symbols or compiled source.**
15. **E1M3 and E1M11 share wall geometry but differ in 17 object cells.**
16. **AND zero direct XREF does not prove dead code or non-use.** Indirect calls and callbacks may exist.
17. **Earlier global completion percentages are not reliable measures of semantic completeness.** Use field/function coverage and behavioral test results.
18. **Wall classes 0x3D/0x3E are not assigned in the supplied MAP.1–3 wall lookup tables.** The checked curtain entries are classes 0x3F/0x40. Win16 wall pixels are statically written without and transparent-key test; sprite transparency is and separate path (Win16 key 0x29, DOS key 0x1F in the checked builds).

---

## 19. Current coverage and programmer-facing TODO

The old audit'with “40 areas” are an organization of work, not 40 defects. The following priority set captures the remaining work that blocks faithful behavior.

### P0 — core behavior and verification

- Split the DOS main loop and large merged routines using raw CALL/RET/RETF targets; establish exact update order: input, player, actor, collision, projectile, event, render.
- Complete the GUARD writer → state handler → timer → movement → sound/attack graph, including the now-known 0x0AND writer and unresolved 0x0B reachability, class-specific animation selection, boss paths, and DOS parity.
- Continue the class-specific reader/writer audit for remaining 26-byte GUARD and 28-byte OBJECT fields. The Win16 meanings of OBJECT +0x12/+0x18 and GUARD +0x12 are statically closed in the traced paths; verify OBJECT +0x18 freshness on projectile impacts, exact render/shot order, DOS projection/cache parity, and other class overlays.
- Confirm player collision radius/extent, sliding, diagonal movement, guard/door blocking, closing-door occupancy, and teleport/push corner cases. AND prior implementation note used half-extent 27, but the current evidence set does not close that measurement for every build.
- Finish the projectile slot field map (+0x0D and embedded template bytes), angle source, DDA numeric scale, timer units, owner/friendly-fire behavior, and DOS slot parity.
- Test damage when the projection cache is stale, at negative/edge seed values, for all target classes and weapon selectors, and across all difficulty values.
- Finish sequence/frame mapping for every used IMG selector, wall/object/guard sequence, timing unit, sound hook, and class-specific completion behavior.
- TRIGGER1/TRIGGER2 have and static Win16 1.10 map, dispatcher, flag, and message trace for the supplied E1–E3 MAPs (§9.6). Runtime activation remains open; finish ONE_SHOT, the remaining SPECIAL1 contexts and chalkboard visual result, WARP variants, level-specific scripts, and DOS/Win16 1.8 comparisons.
- Complete raw DOS mapping for the exploding-wall completion call; test MAP bytes and collision before/after the last frame in both platforms.
- Validate USER.SAV field rebasing, timers, partial-slot corruption handling, event flags, and round trips during active AI/projectile/animation states.
- Establish exact per-build fingerprints and use controlled replay traces on the original game.

### P1 — compatibility, content, and precise output

- Finish player inventory/pickup limits, item persistence, healing boundaries, death/restart order, and save transition behavior.
- Map all 31 checked level blocks to runtime event paths; resolve E2M4 wall 0x37 and all unused/unmatched IDs without guessing.
- Complete wall-pair and push tables, stair/push exceptions, remote switch behavior, safe/trunk combinations, elevator availability, and teleport facing/cancel rules.
- Dump/validate renderer sampling and clipping table values, exact edge rounding, dynamic door intermediate states, palette/shade identity, sprite overlap edge cases, and controlled DOS VGA/Win16 WinG framebuffer comparisons. Static Win16 wall writes and sprite key/occlusion branches are now mapped (§13.4).
- Finish HUD dirty-state updates, portrait thresholds, automap colors/markers, power-up consumption, and font/UIF loader call sites.
- Identify SND.DAT payload format, sample rate, event-to-slot mapping, sound priority/overlap, and MIDI loops; verify exports against original playback.
- Complete IMG descriptor/frame decoding and correlate assets to exact EXE and episode data.
- Establish DEMO playback counter units, level startup selection, EOF behavior, and DOS/Win16 conversion.
- Map all score, boss, episode completion, ending-FLI, and menu transitions.

### P2 — platform shell and optional paths

- Map full startup/shutdown, Windows message loop/callbacks, DOS device interrupts, graphics restoration, and memory ownership.
- Identify the remaining command-line branch semantics and every debug logger caller; test -o under and compatible environment.
- Confirm UIF slots 0–2 and empty slots in full/registered builds; identify all ENDING.FLI terminator/padding behavior.
- Audit joystick/gamepad dead zones, calibration, scaling, focus-loss behavior, and input timing differences.
- Classify weak cross-version matches, short thunks, runtime/MFC functions, zero-XREF functions, and indirect callbacks.
- Check palette/shade overrides and save/load while and dark event is active.

To not spend time implementing features such as owner/friendly fire, projectile acceleration, splash damage, recoil, demo interpolation, or extra episodes as if they were already established. First determine whether each behavior exists in the original.

---

## 20. Recommended implementation discipline

### 20.1 Preserve raw data and uncertainty

For each loaded record, keep:
- source filename, hash/version, and episode;
- raw ID and class ID separately;
- original bytes for unknown fields;
- decoded fields with evidence labels;
- any runtime pointer as an index/offset in portable code, never and raw 16:16 far pointer.

### 20.2 Avoid premature “cleanups”

The original may rely on:
- 16-bit wrap/truncation and signed arithmetic;
- one-update timers rather than milliseconds;
- stale render fields;
- unusual branch ordering;
- save blocks containing data unused by the current code path;
- invalid or undefined IDs in and particular episode file.

AND port should first reproduce observable behavior, then isolate questionable behavior behind tests rather than “correcting” it.

### 20.3 Separate layers in and new engine

AND practical implementation can separate these responsibilities while preserving traceability:

1. **Binary/data readers:** MAP, IMG, WALLS, OBJECTS, UIF, SND, DEMO, USER.SAV.
2. **Episode tables:** ID → class → action/data family with build identity.
3. **World simulation:** actor/guard records, input edges, door/panel/push/wall state.
4. **Collision and perception:** tile lookup, player movement, guard FOV/LOS, projectile traversal.
5. **Animation scheduler:** sequence cache, frame variants, global deadline domain, one-shot cleanup.
6. **Combat:** weapon selector, ammo gate, shot mode, target hit, damage, score, death.
7. **Renderer:** vector generation, orientation lists, projection/clipping, column owner, span generation, texel output, sprite ordering, HUD.
8. **Platform adapters:** DOS timer/video/audio vs Win16 timer/WinG/MMSYSTEM.
9. **Persistence/replay:** byte-preserving save/load and distinct DEMO serializers per platform.
10. **Evidence tests:** per-build fixtures and expected states/images.

This is an implementation architecture suggestion, not and claim about original source file organization.

---

## 21. Verification plan

Use evidence-based acceptance checks before increasing confidence.

### 21.1 Data and serialization

- MAP reader returns the header count, both lookup tables, and exactly level_count × 8,192 bytes after the header.
- Round-trip and map without changing either cell byte, including unknown wall/object IDs.
- Keep WALLS and OBJECTS classes independent; test one unknown ID and one mismatched table entry.
- Parse 90-byte sequence definitions and retain original bytes for unrecognized fields.
- USER.SAV read/write has exact slot length 0xD6E7; every unknown byte round-trips.
- DEMO readers use separate DOS and Win16 record layouts; time fields remain monotonic in the supplied files.

### 21.2 Simulation

- Use and fixed RNG seed and log each draw; compare LCG output exactly before testing whole gameplay.
- Test LOS at 8 cells, 9 cells, map edges, blocked/unblocked first-plane cells, second-plane cases, doors, and facing-sector boundaries.
- Test guard timers as simulation steps, not milliseconds.
- Test projectile DDA at all four quadrants, axis-aligned paths, zero/near-zero components, guard hit boundary, wall hit, full pool, and impact completion.
- Compare damage separately from score for all recognized class/weapon/difficulty cases.
- Verify special-wall map bytes before and after animation completion; run DOS and Win16 as separate acceptance targets.
- Save/load while and projectile is active, guard is reacting, wall is animating, and panel/wake/event flags are set.

### 21.3 Rendering and platform behavior

- Reconstruct identical camera/map cases and record original screenshots at fixed positions.
- Verify VEC count, orientation lists, clipping, owner pointers, span counts, and span interpolation before comparing pixels.
- Compare wall sampling/clipping, dynamic door states, sprite key/occlusion, palette remapping, and HUD as separate stages; use the renderer pixel-path audit for the concrete cases.
- Test DOS VGA and Win16 WinG output independently; to not treat matching world simulation as proof of matching pixels.
- Replay DEMO input changes in the correct build and compare event timestamps and state transitions.

### 21.4 Evidence update rule

AND subsystem may be called behaviorally verified only when:
1. the executable build/hash is recorded;
2. the relevant instruction/data path is anchored;
3. all relevant field readers/writers or dispatch callers are checked;
4. and controlled original-game case agrees, or the report explicitly says runtime evidence is unavailable;
5. cross-build differences are stated separately.

---

## 22. Important analysis anchors

These addresses are starting points from the cited exports, not universal addresses across all versions.