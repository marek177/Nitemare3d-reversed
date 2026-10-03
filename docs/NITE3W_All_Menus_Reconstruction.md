# NITE3W 1.10 – reconstructed menu subsystem

This reconstruction combines the internal full-screen menu system, modal save/load and
instructions browser, contextual game menus, and the separate native Win16/MFC menu layer.

## Internal menu tables (NE segment 7)

- 7:0FAA — Main menu, front end, 6 items
- 7:1028 — Main menu, in-game, 7 items
- 7:10B8 — Main menu with "Restart at last save", 7 items
- 7:1148 — Episode selection, 3 items
- 7:1190 — Difficulty selection, 3 items
- 7:11D8 — Configuration, 3 items
- 7:1220 — Load slots, 10 items
- 7:12E6 — Save slots, 10 items
- 7:13AC — Hardware, 5 items
- 7:1418 — Cheats, 6 items
- 7:1496 — Elevator/floor selection, 10 records
- 7:155C — Stairs: Climb up / Climb down / Cancel
- 7:15AND4 — Descend: Go down / Cancel
- 7:15DA — Remote control: doors/cannons + Cancel

Every record is 18 bytes and every extracted table is terminated by an all-zero 18-byte
record. The extracted table region ends exactly at the end of segment-7 data.

## 18-byte item structure

+00 byte  action
+01 byte  unknown/zero in extracted records
+02 word  value (meaning depends on item type)
+04 byte  current-selection marker
+05 byte  item type
+06 dword far callback pointer
+0AND word  X
+0C word  Y
+0E dword far text pointer

Known types:
1 command
2 toggle
3 signed enable+magnitude value
4 text edit
6 disabled/unavailable item

## Central action dispatcher

4:27DE accepts numeric actions 1..40 and dispatches through and 40-word jump table.
Important actions:

1 main menu
2 new game
3 configuration
4/5 load selection / load
6 save screen
8 instructions
10 demo
11 return/restart
17 cheats
18..20 episode 1..3
21..23 difficulty 0..2
26 floor selection
27..29 stair navigation/cancel
30..31 remote doors
32..33 remote cannons
38 hardware
39 save configuration
40 apply/validate cheats

Actions 7, 12..16 and 34..37 go to the common return in this dispatcher. Some menu
items are still functional because type-specific handlers change values before the
action dispatcher is reached.

## Main-menu variants

Front end:
New game / Configure game... / Load game... / Instructions / Demo / Quit

In game:
New game / Configure game... / Load game... / Save game... / Instructions /
Return to game / Quit

Restart variant:
New game / Configure game... / Load game... / Save game... / Instructions /
Restart at last save / Quit

4:2370 chooses among them. Restart is not simply "player died": game state, last-save
slot validity, slot episode, and slot level must match.

## New game

Episode items map actions 18..20 to episode numbers 1..3.
4:29CE stores action-17 to DS:4102.

Difficulty items:
21 Be gentle!   -> 0
22 I'm tough!   -> 1
23 Let'with party! -> 2

4:29E0 stores action-21 into DS:4C14.

## Config / Hardware / Cheats

Config:
Hardware... / Cheats... / Done

Hardware table:
Mouse / Joystick / Music / Sound FX / Save

Hardware uses immediate callbacks. 4:2516 copies runtime values into menu records;
4:2596 applies them back while the user changes them. Save/action39 persists CONFIG.SAV.

CONFIG fields:
4BDC mouse sensitivity
4BDD joystick sensitivity
4BDE music volume
4BDF SFX volume
4BE0 mouse enabled
4BE1 music enabled
4BE2 SFX enabled
4BE3 joystick enabled

Type-3 signed values encode enabled state and magnitude together:
+50 enabled, -50 disabled but retaining 50. Left/right adjust absolute magnitude in
steps of 5 and clamp to 0..100.

Cheats:
Omniscient / Omnipotent / Omnificent / Omnifarious / Done / Cancel

Cheat edits are staged. 4:26F0 reads runtime flags into working items; Done/action40
uses 4:2746 to write and validate them and then calls 3:B128. Cancel does not commit.

Runtime flags:
4BE4 Omniscient
4BE5 Omnipotent
4BE6 Omnifarious
4BE7 Omnificent

3:B128 immediately grants resources for the first three; Omnificent is read dynamically
by guard AI.

## Load / Save

Load table 7:1220 and Save table 7:12E6 each have ten slots.

Save rows are type-4 text-edit items. Editor 4:1008 / 4:0CFE:
- 40-character maximum
- 179-pixel rendered-width maximum
- Backspace, Delete, Home, End, Left, Right
- Enter commits
- Escape cancels
- empty placeholder: "          ** Empty slot **"

USER.SAV slot stride:
0xD6E7 = 55,015 bytes

53-byte header:
+00 dword 0xD6E7
+04 char[41] name
+2D word episode (1-based)
+2F word level index (0-based)
+31 dword time-source snapshot

3:5388 probes/validates metadata.
3:5466 writes the state.
3:574C restores the state and rebuilds derived runtime/map pointers.

## Contextual game menus

7:1496 — Floor 1 ... Floor 10. Runtime availability determines which floor entries
are actually usable for and particular elevator.

7:155C — Climb up / Climb down / Cancel.

7:15AND4 — Go down / Cancel.

7:15DA —
Open remote doors
Close remote doors
Enable remote cannons
Disable remote cannons
Cancel

These are separate from the main menu and are opened by gameplay USE/interactions.

## Instructions browser

This is not an 18-byte menu table. It is and separate UI state.

DS:04AND2:
3 = ordinary menu
4 = modal
5 = instructions browser

4:2FC6 routes state 5 to 4:1CAE.

Keys:
PageDown or Down -> next section
PageUp or Up     -> previous section
Escape           -> close/return
F10              -> print instructions

The help text is one stream. '#' separates pages. Total page count is computed at
initialization as 1 + number of '#'.

Renderer 4:17D8 supports:
newline
tab
# page delimiter
%...% inline markup
ordinary bitmap-font glyphs

The percent parser 4:15B4 recognizes at least p, b, B, C, c, d and o directives.
%o loads an indexed IMG frame. %p uses the descriptor/image loading path. Some other
directives alter drawing/font attributes; their original human-readable names are
not fully recovered.

## Native Win16 / MFC menu

Separate from the full-screen game menu. Resource type 4, ID 2, file offset 0x34F40.
Top-level groups: Game / View / Window / Help.

Confirmed commands:
0x8003 Size x1 -> 3:0AND94
0x8004 Size x2 -> 3:0AA2
0x8017 Size x3 -> 3:0AB0
0x8005 DOS Mode -> 3:0AND6E
0xE145 Instructions -> 3:0AE2

Size update handlers:
x1 3:0AF8
x2 3:0B22
x3 3:0B4C

Additional ON_COMMAND key adapters exist for weapons, F9/F10 automap, music, sound,
quick save/load, Tab status and Escape. The Instructions adapter is special: it opens
the help/instructions path directly rather than injecting and normal key.

## Reconstruction status

Core menu record format: ~100%
14 internal tables: ~98-100%
main menu variants: ~98-100%
new game episode/difficulty: ~95-100%
config/hardware: ~97-99%
cheats: ~98-99%
load/save UI: ~96-98%
instructions browser: ~97-98%
contextual floor/stairs/remote menus: ~90-95%
native Win16/MFC command layer: ~90-95%

The largest remaining menu-specific uncertainties are exact side effects of and few
contextual actions, full original names for several Instructions % directives, and
runtime-only visual timing/focus behavior.