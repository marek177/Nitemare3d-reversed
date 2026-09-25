# Project findings delta — 2026-09-25

This delta records the newest NITE3W.EXE 1.10 findings integrated into source on
2026-09-25. It deliberately separates instruction/data-backed facts from
remaining hypotheses.

## Source-of-truth code added

The code-ready constants and formulas are in:

- `src/re/Win16RecoveredFacts_2026_09_25.hpp`
- `tests/win16_recovered_facts_2026_09_25_test.cpp`

The existing MFC reconstruction was extended in:

- `src/re/Win16MfcMemory.hpp`
- `src/re/Win16MfcAddresses.hpp`

## HUD dispatcher

`Hud_Dispatch` is at internal address `3:A3B6` and accepts requests 0..25.

Confirmed request mapping:

- 0 full refresh
- 2 weapon branch
- 3 episode/level
- 4 score
- 5 health + portrait
- 7/8/9 silver/laser/wand ammo
- 12 weapon icon
- 13/14 key/card icons
- 18 decoration
- 19/20 automap energy gauges
- 21 status
- 22 coordinates
- 23 restore overlay
- 24 conditional input/mouse overlay
- 25 DOS cursor
- 1, 6, 10, 11, 15, 16, 17 are no-op requests

Health is unsigned-clamped to 100 and written back to `DS:4C1D`.

Portrait selection is:

```text
frame = 13 + (min_u(health, 100) + 9) / 10
```

So frame 13 is HP=0 and frame 23 is HP=91..100.

Confirmed HUD text destinations:

- episode/level: (50,171), width 31
- score: (50,191), width 31
- health: (7,192), width 10
- silver: (109,164), width 20
- laser: (109,177), width 20
- wand: (109,190), width 20
- coordinates: (140,192), width 19

## Automap / right HUD panel

`Automap_Dispatch` is at `3:B1A4` with requests 0..9.

Confirmed operations:

- 2 clears the full 4096-byte buffer
- 3 redraws the visible window
- 5 updates the player cell and draws the visible window
- 6 draws eligible GUARD markers
- 7 applies low-clarity noise
- 8 clears the previous player cell
- 9 draws the marker/rectangle layer

Requests 0, 1 and 4 still have only partial semantic identification.

The buffer is 64x64, one byte per cell, but is **column-major**:

```text
index = cellX * 64 + cellY
```

Visible area is 62x36 at screen (256,162)..(317,197).

Viewport origin:

```text
originX = clamp(playerCellX - 31, 0, 2)
originY = clamp(playerCellY - 18, 0, 28)
```

`DS:4C42` powers the enemy/GUARD locator layer. `DS:4C43` powers map
clarity. For clarity values 1..15 the noise branch uses:

```text
noisePoints = 500 / (power^3)
```

GUARD markers exclude GUARD state 0x0A and OBJECT classes
0x15, 0x16, 0x19 and 0x21. Locator values 1..15 blink on odd values; zero
disables the layer.

Exact buffer byte/color meanings and some priority/mode rules remain open.

## Renderer

Confirmed Win16 viewport and core arrays:

- framebuffer 320x200
- 3-D viewport 304x152 at (8,4)
- projection center Y=80
- recovered horizontal FOV about 80.99 degrees
- wall owner table: DS:53FE, 320 far pointers
- wall occlusion: DS:58FE, 320 uint16 values
- RGB palette: DS:5B7E, 256x3
- visible span count: DS:5E7E
- visibility bounds: DS:5E80..5E86
- visible spans: DS:5E88, max 50, stride 20
- projected sprites: DS:6270, max 100, stride 18
- WinG HBITMAP: DS:6978
- VEC count: DS:7E56
- OBJECT count: DS:7E58
- wall/object resource descriptor counts: DS:7E5A/7E5C
- GUARD count: DS:7E5E
- four VECLIST arrays, 333 entries each

This reinforces the recovered MAP -> VEC -> VECLIST -> owner columns -> spans ->
wall raster -> sprite queue architecture and not a Wolf3D one-ray-per-column DDA.

## GUARD state/field corrections

Confirmed GUARD record facts:

- stride 0x1A / 26 bytes
- +02..+05 timestamp
- +06 state timer
- +08 OBJECT slot
- +0A strategy
- +0B state
- +0C next/return state
- +10 strength
- +11 octant
- +12 resultOctant
- +13/+14 signed movement X/Y used by state 0x13

Important correction: +12 is **resultOctant**, not a pain cooldown.

Confirmed/strongly identified states:

- 0x07 perception/decision
- 0x0B lethal-contact terminal
- 0x13 timed directional movement
- 0x15 pain -> return state

State-0x13 octant movement steps:

```text
0 ( 0,-8)
1 (+8, 0)
2 (+8, 0)
3 ( 0,+8)
4 ( 0,+8)
5 (-8, 0)
6 (-8, 0)
7 ( 0,-8)
```

Fields +15, +16 and +17..+19 are not fully named yet.

## IMG / UIF / HUD image bank

Confirmed IMG facts used in source:

- wall directory: 0x0000, 256 DWORD entries
- object directory: 0x0400, 256 DWORD entries
- frame header: 10 bytes
- image raster: column-major, `pixel[x * height + y]`
- audited frame stream begins at 0xBC00

For Episode-1 data, object image `0xFF` is the dynamic HUD bank with 29 frames:

- 0..3 weapons
- 4..7 keys
- 8..9 cards
- 10..12 decorations/foreground
- 13..23 HP portraits
- 24..28 larger HUD assets

UIF directory has 32 entries of 6 bytes. Slots 0..16 are populated in the
current data: 0..2 fonts and 3..16 PCX screens. Alias/unused slots and some
asset-to-HUD bindings remain unresolved.

## Menu / save UI

Menu dispatcher: `4:27DE`.

Confirmed structure:

- actions 1..40
- 14 menu tables
- 80 menu items
- 10 save slots
- empty text literal `** Empty slot **`
- save-name editor: max 40 characters and max 179 rendered pixels
- storage file: `user.sav`

The exact symbolic name of every menu action is not yet complete.

## MFC / Win16 wrapper update

Existing MFC reconstruction remains at 31 runtime-class records and four
HandleMaps. `HandleMap16` is 0x26 bytes under 2-byte Win16 packing.

New CDC facts:

- CDC object size 0x0A
- +0x04 output HDC
- +0x06 attribute HDC
- Attach writes both fields from the HDC
- Detach clears both fields
- +0x08 remains unresolved

Recovered anchors:

- CDC Attach: 1008:02E2
- CDC Detach: 1008:0316
- CDC base cleanup: 1008:0342
- CPaintDC destructor: 1008:0D0A
- deleting destructors:
  - CDC 1008:104E
  - CClientDC 1008:1070
  - CWindowDC 1008:1092
  - CPaintDC 1008:10B4

Runtime ownership/lifetime of CDC/GDI/Menu wrappers still needs an original
Windows 3.1 runtime trace before being called fully closed.

## Runtime reconstruction fixes

`LevelState` now owns copies of OBJECT/WALL definition tables instead of
retaining raw pointers supplied to `LevelState::create`. This closes the
ASan-observed dangling-definition-table failure mode when callers pass
short-lived tables.

Pushable motion now reserves its final destination while moving, so two
simultaneous pushes cannot both claim and overwrite the same target tile.

## Evidence boundary

Do not convert the following into final gameplay behavior yet:

- exact automap cell values/colors and requests 0/1/4
- exact HUD descriptor/asset binding for every operation
- GUARD +15/+16/+17..+19 semantics
- full menu action naming
- full original Win3.1 CDC/GDI/Menu ownership behavior
- final pixel parity of the modern renderer
