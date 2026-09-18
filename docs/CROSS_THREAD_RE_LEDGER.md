# Cross-thread Nitemare 3-D reconstruction ledger

Date: 2026-09-18

This ledger consolidates reverse-engineering results recovered across the Nitemare 3-D work threads. It is intentionally conservative: exact values are only promoted when backed by original executable/data/save evidence. See subsystem documents for disassembly details.

## Binary target

- NITE3W.EXE V1.10: 230,400 bytes; Win16 NE; 10 segments.
- SHA-256: `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.
- Imports observed across KERNEL, WING, DISPDIB, GDI, USER, KEYBOARD, COMMDLG, MMSYSTEM and SHELL; joystick.drv is dynamically involved.
- A whole-EXE sweep produced roughly 688 candidate function entries. This is an audit workset, not a final function count.

## Original data formats

- MAP.1 has 11 payloads; MAP.2 and MAP.3 have 10. Each level is 64x64x2 = 8192 bytes after the 514-byte archive header. E1M11 is the internal/demo map.
- Each MAP cell is interleaved `{wallByte, objectByte}`.
- Runtime world coordinates use 64 units per tile and `coord >> 6` for world-to-tile conversion.
- IMG archives use indexed image/sequence data; prior archive work confirmed raw indexed graphics and sequence-definition tables. Keep episode-specific IMG identity separate.
- UIF.DAT is a 32-entry UI/PCX-oriented container in the recovered data analysis.
- SND.DAT is a 160-entry sound/music container in the recovered data analysis; runtime SND-ID-to-event mapping is still being completed.
- DEMO files use a 6-byte header followed by 8-byte timed input records.
- GAME.PAL contains the 768-byte palette payload used by the original indexed renderer.
- OBJECTS.1-3 and WALLS.1-3 are primarily editor-definition assets; runtime gameplay is driven by MAP/IMG/EXE structures rather than requiring these editor files.

## MAP -> runtime object pipeline

The executable constructs two 256-entry property tables:

- wall properties at DS `0x7E94[wallByte]`;
- object properties at DS `0x7F94[objectByte]`.

Confirmed wall bits used by movement:
- `0x04`: hard blocking;
- `0x08`: dynamic door path;
- `0x40`: level-script/touch hook.

Confirmed object bits:
- `0x01`: instantiate runtime OBJECT;
- `0x02`: blocks movement;
- `0x04`: special/touch handler;
- `0x08`: creates GUARD.

The MAP object byte passes through definition/class lookup before OBJECT creation. OBJECT is 28 bytes; `OBJECT+05` receives the property flags and `OBJECT+06` the runtime class. `OBJECT+01` is a class-relative variant index.

## Player movement/collision

Main anchors:
- `seg3:8AAC`: movement caller;
- `seg3:8604`: incremental movement/collision;
- `seg3:84F4`: leading-edge MAP passability;
- `seg3:8A20`: player position/tile commit.

Confirmed globals:
- `0x4BF6`: player world X;
- `0x4BF8`: player world Y;
- `0x4BF2`: current tile X;
- `0x4BF4`: current tile Y;
- `0x4C10:0x4C12`: current MAP-cell far pointer.

Player collision is an AABB with half-extent 27 world units. Motion is integer/Bresenham-like one-unit stepping; X/Y components are collision-tested separately, giving natural wall sliding. A separate proximity/occupancy path uses threshold 42 world units; its exact gameplay role remains PARTIAL.

Changing tile dispatches event `0x16`.

## USE / doors / panels / pushables

- Input `0x0200` is rising-edge USE/ACTION.
- USE resolves one adjacent cardinal cell from player orientation.
- Dynamic doors: max 64, runtime stride 22, original table base `0x9DD6`.
- Panels: max 32, stride 22.
- Pushables: runtime class `0x28`, max 12, stride 6.
- Push movement is 8 steps x 8 world units = one 64-unit tile.
- Verified gameplay includes red/green/blue/yellow key-gated families and Red/Yellow ID-card gates.
- Wall families `0x19..0x1C` map to Red/Green/Blue/Yellow key interaction families.
- Wall families `0x25..0x2C` enter the combination-lock/check path.
- Teleports, special walls and combination subtypes remain under exact opcode/class audit; do not assign guessed names.

## OBJECT runtime

Base `0x6D66`, stride `0x1C`, maximum 350.

Known:
- +00 object/map ID;
- +01 class-relative variant;
- +02/+03 signed render/animation components (PARTIAL semantic);
- +04 definition-table ID;
- +05 property flags copied from `0x7F94`;
- +06 runtime class;
- +07 GUARD index for guard-producing objects;
- +08..+0B initialized runtime value, semantic TODO;
- +0C:+0E MAP-cell far pointer;
- +10 world X;
- +12 world Y;
- +14..+19 still incomplete; +18 participates in damage/projection geometry;
- +1A initialized zero;
- +1B TODO.

## GUARD runtime

Base `0x93AE`, stride 26, maximum 100; count global `0x7E5E`. `GUARD+08` is an OBJECT slot/index and resolves as `0x6D66 + index*0x1C`.

Known fields:
- +02 dword timestamp/time;
- +06 timer;
- +08 OBJECT slot/index;
- +0A strategy;
- +0B state;
- +0C nextstate;
- +0D o_id;
- +0E definition lookup result (PARTIAL);
- +0F sync/control boolean (PARTIAL);
- +10 strength;
- +11 octant;
- +12 resoct;
- +13 transition parameter (PARTIAL);
- +16 transition/control flag (PARTIAL).

Fresh GUARD strength is initialized to `0xFF`. Damage receiver has explicit lethal clear/death handling and nonlethal subtraction/reaction handling. Per-enemy HP values must not be invented.

## Combat/weapons

Weapon selector `0x4C23`:
0 Single Shot Laser; 1 Magic Wand; 2 Silver Pistol; 3 Continuous Laser; `0xFF` no weapon/unset state.

Confirmed damage core includes a geometry-derived base plus `random()%25`, class/weapon divisors, difficulty scaling, and clamp to 255. The exact class/weapon divisor matrix is documented in `COMBAT_DAMAGE_RE.md`.

Ammo:
- SSL uses `0x4C20`;
- Wand uses `0x4C44`;
- Silver Pistol uses `0x4C1F`;
- Continuous Laser uses `0x4C20`;
- Omnipotent `0x4BE5` bypasses consumption;
- ordinary pickup +20, forced/set value 50, threshold 100.

Weapon jam global: `0x4C2E`. Script event `0x47` sets jam and `0x48` clears it. Firing path anchor: `seg3:8B06`.

## DEMO

Record layout:
`eventByte:u8, inputMask:u16, pad:u8, timestamp:u32`.

Known input bits include:
- `0x0002` forward;
- `0x0004` backward;
- `0x0020` doubles movement increment;
- `0x0040` increment 1;
- `0x0080` FIRE;
- `0x0100` strafe modifier;
- `0x0200` USE/ACTION.

DEMO is input playback, not stored absolute positions. `-r` enables recording. The supplied DEMO.1 matches E1M11 behavior; DEMO.2/3 origins must remain open rather than being guessed from episode numbering.

## Player spawn

The map scan identifies the player start from the object layer. IDs 1..4 encode the four orientations:
- 1 -> 0 degrees;
- 2 -> 90;
- 3 -> 180;
- 4 -> 270.

Spawn position is tile center: `x*64+32, y*64+32`.

## USER.SAV / CONFIG.SAV

USER.SAV slot size is exactly `0xD6E7` = 55,015 bytes. Important offsets:
- +0x0004 description;
- +0x002D episode;
- +0x002F zero-based level;
- +0x0031 saved tick;
- +0x0035 8192-byte mutable MAP;
- +0x2035 0x5E-byte gameplay/global block;
- +0xB43B 0x0A28-byte GUARD block = 100*26.

The remaining persisted blocks and rebasing behavior are tracked in `SAVE_LIBRARIES_IDA_REPORT.md`.

CONFIG.SAV is 20 bytes. Recovered settings include viewport/window dimensions, mouse/joystick sensitivity, MIDI/SFX volume, enable toggles and the four Omni cheat toggles. See the save/config documentation before changing semantics.

## Renderer/runtime limits

Recovered original limits include:
- segments 50;
- images 70;
- objects 350;
- guards 100;
- vectors 1000;
- orientation-list capacity 333;
- doors 64;
- panels 32;
- pushables 12.

Renderer evidence indicates a custom vector/line-segment textured-column path with indexed framebuffer and depth/column structures; do not replace it with textbook Wolf3D DDA merely because movement/data concepts are related. Catacomb Abyss and Wolf3D are comparison sources, not identity claims.

A prior audit also found a MAXVECLIST off-by-one two-byte overwrite in the original and an undefined wall 0x37 occurrence at E2M4 (61,54). Preserve original quirks only when compatibility requires them; document rather than silently relying on memory corruption.

## Evidence discipline

Use: `VERIFIED_EXE`, `VERIFIED_DATA`, `VERIFIED_SAVE_LAYOUT`, `BEHAVIORAL`, `INFERRED`, `PARTIAL`, `TODO`.

Do not promote approximate progress, guessed enemy identity, HP, damage, speed, state names, SND identities, wall meanings or renderer lineage to VERIFIED without direct evidence.

The final 95-100% EXE claim requires byte/range classification, not an engineering estimate.
