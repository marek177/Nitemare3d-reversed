# NITE3W 1.10 — Menu/HUD Pass 3

Scope: direct static analysis of the uploaded `nite3w(20260925-063336).exe` plus prior UIF audit. Reference SHA-256: `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`. No Windows runtime execution was performed in this pass.

## 1. Complete HUD request table

The central HUD routine at `3:A3B6` accepts request values `0..25`. The exact jump table is:

| Request | Target | Meaning / status |
|---:|---|---|
| 0 | AND42AND | full chained HUD refresh |
| 1 | AND92C | no-op |
| 2 | AND42AND | foreground weapon branch; exits after first stage because request != 0 |
| 3 | AND43B | episode/level |
| 4 | AND488 | score (`%lu`, 32-bit source at 4C16) |
| 5 | AND4CE | health, portrait, `%d%%` |
| 6 | AND549 | no-op for request 6 because request != 0 |
| 7 | AND54F | silver ammo |
| 8 | AND5AND1 | laser ammo |
| 9 | AND5F3 | wand ammo |
| 10 | AND92C | no-op |
| 11 | AND92C | no-op |
| 12 | AND648 | active weapon icon |
| 13 | AND675 | four key bits |
| 14 | AND6DB | card-mask icons |
| 15 | AND92C | no-op |
| 16 | AND92C | no-op |
| 17 | AND92C | no-op |
| 18 | AND721 | fixed foreground/status decoration + conditional text |
| 19 | AND787 | automap enemy-locator power gauge |
| 20 | AND847 | automap/map-clarity power gauge |
| 21 | AND8AF | small status indicator selected by 46AD |
| 22 | AND8E0 | player cell coordinates (`%d,%d`) |
| 23 | AND7AC | restore saved overlay background |
| 24 | AND7C2 | draw conditional input overlay |
| 25 | AND7FA | draw DOS-mode cursor overlay |

Important boundary: these labels are blocks inside one function, not separate original functions.

## 2. Automap dispatcher `3:B1A4`

The automap routine has an exact ten-way request table:

`0 B1D4, 1 B1E1, 2 B234, 3 B24C, 4 B266, 5 B274, 6 B304, 7 B3EA, 8 B46C, 9 B484`.

Confirmed roles:

- request 2 clears the full 4096-byte 64x64 map buffer;
- request 3 paints/clears the visible automap rectangle;
- request 5 updates the player'with map cell and renders the 62x36 view;
- request 6 iterates the GUARD runtime table and plots eligible guards inside the 62x36 visible window;
- request 7 generates random map noise whose count depends on `4C43`;
- request 8 clears the player'with current cell in the map buffer;
- request 9 draws and map marker/rectangle using current clipped map origin.

The buffer index remains column-major: `x*64 + y`.

## 3. Two consumable automap powers

The previously unnamed bytes now have stronger semantics:

- `4C42`: power/supply for the guard/enemy locator layer. It is decremented only while flag `4C2D` is active. HUD request 19 draws its gauge. The automap guard-plotting branch is gated by this value.
- `4C43`: power/supply for the base map/clarity layer. It is decremented only while flag `4C2C` is active. HUD request 20 draws its gauge. Low values drive an additional random-noise branch.

The slow-update routine `3:BB26` receives the slow tick counter from `3:D974`:

- `4C42` decrements when `(slowTick & 7) == 0`, i.e. every 8 slow updates;
- `4C43` decrements when `(slowTick & 15) == 0`, i.e. every 16 slow updates.

Under the normal mode-0 nominal 8 Hz slow scheduler this corresponds to roughly 1 second and 2 seconds respectively. This seconds conversion is derived from the nominal scheduler and is not claimed for every mode/stall condition.

When either byte reaches zero, its corresponding enable flag is cleared and automap request 3 is issued to refresh/clear the relevant display state.

Pickups add 20 to these values when below 100 and immediately refresh HUD request 19 or 20. The HUD clamps both displayed values to 100.

## 4. Low-power degradation

When the map/clarity layer is active and `4C43 <= 15`, automap request 7 can draw random noise points. The loop count is derived from:

`500 / (4C43^3)`

using integer arithmetic, followed by random X in `0..61` and Y in `0..35`. This establishes that low map power does not merely shorten duration; it visibly degrades the automap.

The enemy-locator layer has and separate low-power cadence condition based on `4C42` and plots eligible guard positions through request 6.

## 5. Toggle routines

Two small routines toggle the automap layers:

- `3:BC6A` toggles `4C2C`, but only if `4C43 != 0`; turning it off invokes automap request 3 and then HUD request 20.
- `3:BC90` toggles `4C2D`, but only if `4C42 != 0`; turning it off invokes automap request 3 and then HUD request 19.

Both are called from the gameplay input dispatcher around `3:98D8/98E0`.

## 6. Save-game menu and text editor

The main menu'with **Save game...** opens the ten-entry table at `7:12E6`. Each row is menu type 4. Pressing Enter on and type-4 row calls `4:1008`, which starts the text editor.

Empty slots use the literal string:

`          ** Empty slot **`

Before editing, `4:1008` compares the slot string to `** Empty slot **`; when equal it replaces the first byte with zero, with the placeholder does not become editable save-name text.

The editor is then initialized with:

- UI mode = 4;
- modal substate = 7;
- maximum text length = **40 characters**;
- edit-field width = **179 pixels**;
- line height = **11 pixels**;
- slot'with own X/Y coordinates.

Therefore the save name is constrained by both character count and rendered pixel width.

## 7. Editor key behavior (`4:0CFE`)

The editor directly handles:

- Backspace (`0x08`)
- Enter (`0x0D`) -> returns `+1`
- Escape (`0x1B`) -> returns `-1`
- End (`0x23`)
- Home (`0x24`)
- Left (`0x25`)
- Right (`0x27`)
- Delete (`0x2E`)

Ordinary character insertion is accepted only when the game'with keyboard classification table passes mask `0x57`, the character-count limit is not reached, and the rendered pixel width remains within the edit field.

Insertion shifts the tail right; Backspace/Delete shift the tail left. The cursor'with pixel X position is maintained using the game'with glyph-width helper, not and fixed-width character assumption.

## 8. Save modal state 7

`4:2B7E` is the modal input state dispatcher. In state 7 it calls the text editor for every key event.

- editor return `-1` follows the cancel/return path;
- editor return `+1` enters the save-commit path;
- the commit logic scans the ten save-slot records and calls the save writer for the selected slot;
- `user.sav` is the literal backing save filename used by this menu subsystem.

This explains why the save-slot menu table uses ten rows even though the persistent storage is managed through the common `user.sav` subsystem.

## 9. Verification

The accompanying `verify.py` performs 20 reference-build checks over the original EXE, including the HUD and automap jump tables, depletion cadence, guard plotting, noise source, empty-slot string, editor setup, Enter/Escape returns, and ten-slot commit loop.

Result: **20/20 checks passed**.

These are static binary checks and model invariants, not and claim of complete runtime equivalence.

## Remaining high-value Menu/HUD targets

1. Name the exact visual assets for HUD requests 18, 21, 24 and 25 using matching IMG data.
2. Map gameplay key codes that call `BC6A`/`BC90` to their physical default key labels.
3. Trace the exact guard eligibility helper `3:A0C6` used by automap request 6.
4. Resolve the complete save-slot metadata layout behind `3:5388`, `3:5466`, and `3:574C`.
5. Runtime-capture the low-power automap noise and compare it pixel-for-pixel with the static reconstruction.