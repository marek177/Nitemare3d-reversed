# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 33

Date: 2026-10-03

Primary image:
- `N3D_DOS_v2.0_IDA.EXE`
- complete unpacked DOS V2.0 load image
- load image size: `0x29D60 = 171,360 bytes`

Address convention:
- addresses below are unpacked MZ load-image offsets;
- raw image bytes and MZ relocation entries are authoritative;
- CODE and DATA/TABLE/STATE closure remain separate metrics.

## Result

Pass 33 resolves the **entire remaining post-code image**:

`0x1BD93 .. 0x29D5F`

Total span:

**57,293 bytes = 0xDFCD**

Classification:

- **57,293 bytes DATA/TABLE/STATE -> GREEN**
- **0 new executable code bytes**
- **no genuine executable entry exists after `0x1BD92`**

Therefore the last real executable routine in the complete DOS V2.0 load image remains:

`0x1BD4A..0x1BD92` — `DrawHexWordToTextVram`

and the executable-function census is now definitively bounded above by:

**`0x1BD92`**

Everything after that address is data, zero/BSS-style state, menu records or initialized
DGROUP data.

---

# 1. `0x1BD93..0x1BD9F` — zero state

Length: **13 bytes**

All zero.

Classification:

**STATE/DATA GREEN**

---

# 2. `0x1BDA0..0x1BDA1` — relocated WORD/segment datum

Length: **2 bytes**

Stored WORD:

`0x21FD`

The MZ relocation table contains an entry at exactly `0x1BDA0`, proving this WORD is and
relocatable segment-style datum rather than instruction bytes.

Higher-level symbolic role is not required for code classification.

Classification:

**RELOCATED DATA GREEN**

---

# 3. `0x1BDA2..0x1D07F` — zero state/BSS block

Length: **4,830 bytes**

Every byte is zero.

No executable entry or control-flow target exists inside this interval.

Classification:

**STATE/BSS GREEN**

---

# 4. `0x1D080..0x1D0D9` — remote-control menu records

Length: **90 bytes**

Exactly:

`5 × 18-byte menu records`

using the already recovered DOS menu layout:

```text
+00 WORD action
+02 WORD value
+04 BYTE selected
+05 BYTE item type
+06 DWORD callback far pointer
+0A WORD X
+0C WORD Y
+0E DWORD text far pointer
```

Rows:

| Address | Action | Type | X,Y | Text |
|---|---:|---:|---|---|
| `1D080` | `1Bh` | 1 | `100,50` | `Open remote doors` |
| `1D092` | `1Ch` | 1 | `100,65` | `Close remote doors` |
| `1D0A4` | `1Dh` | 1 | `100,80` | `Enable remote cannons` |
| `1D0B6` | `1Eh` | 1 | `100,95` | `Disable remote cannons` |
| `1D0C8` | `06h` | 1 | `100,110` | `Cancel` |

The following zero bytes beginning at `1D0DA` naturally provide the terminating
zero-record/sentinel expected by the menu walker.

This identifies the static menu used by the ID-card/remote-control interaction family.

Classification:

**MENU TABLE GREEN**

---

# 5. `0x1D0DA..0x2199F` — zero state/BSS region

Length: **18,630 bytes**

Every byte is zero.

Classification:

**STATE/BSS GREEN**

---

# 6. `0x219A0..0x21FBD` — complete static menu-template bank

Length:

**1,566 bytes**

Exactly:

`87 × 18-byte records`

The records divide into the following static tables.

## 6.1 `0x219A0` — front-end main menu

Live rows:

1. New game
2. Configure game...
3. Load game...
4. Instructions
5. Demo
6. Quit

Then zero sentinel at `0x21A0C`.

## 6.2 `0x21A1E` — in-game main menu

Live rows:

1. New game
2. Configure game...
3. Load game...
4. Save game...
5. Instructions
6. Return to game
7. Quit

Then zero sentinel at `0x21A9C`.

## 6.3 `0x21AAE` — restart-at-last-save menu

Live rows:

1. New game
2. Configure game...
3. Load game...
4. Save game...
5. Instructions
6. Restart at last save
7. Quit

Then zero sentinel at `0x21B2C`.

## 6.4 `0x21B3E` — episode/map-set menu

Three rows:

- Episode 1
- Episode 2
- Episode 3

All are initially item type `6` (disabled); runtime code enables available episodes.

Zero sentinel at `0x21B74`.

## 6.5 `0x21B86` — difficulty menu

Three rows:

- Be gentle!
- I'm tough!
- Let'with party!

Zero sentinel at `0x21BBC`.

## 6.6 `0x21BCE` — configuration menu

Three rows:

- Hardware...
- Cheats...
- Done

Zero sentinel at `0x21C04`.

## 6.7 `0x21C16` — LOAD-slot row template

Ten rows.

Each:
- action `03h`;
- item type `1`;
- X = 67;
- Y = 47,60,...164;
- text pointer initially NULL.

The load-dialog code fills the text pointers/descriptions dynamically.

Zero sentinel at `0x21CCA`.

## 6.8 `0x21CDC` — SAVE-slot row template

Ten rows.

Each:
- action `04h`;
- item type `4` = editable text;
- X = 67;
- Y = 47,60,...164;
- text pointer initially NULL.

The save-dialog code populates editable slot descriptions dynamically.

Zero sentinel at `0x21D90`.

## 6.9 `0x21DA2` — hardware settings menu

Rows:

- Mouse
- Joystick
- Music
- Sound FX
- Done

The first four are item type `3` signed enable/magnitude rows.

All five carry the same callback far pointer:

`0D29:1F62`

matching the settings redraw/update callback path.

Zero sentinel at `0x21DFC`.

## 6.10 `0x21E0E` — cheat settings menu

Rows:

- Omniscient (all-knowing)
- Omnipotent (all-powerful)
- Omnificent (all-cunning)
- Omnifarious (all things)
- Done
- Cancel

The four cheat toggles are item type `2`.

Zero sentinel at `0x21E7A`.

## 6.11 `0x21E8C` — Floor 1..10 menu

Ten rows:

- Floor 1
- Floor 2
- ...
- Floor 10

All use action `17h`.

Zero sentinel at `0x21F40`.

## 6.12 `0x21F52` — climb/stair menu

Rows:

- Climb up
- Climb down
- Cancel

Zero sentinel begins at `0x21F88`.

## 6.13 `0x21F9A` — one-way/down menu

Rows:

- Go down
- Cancel

The zero-state region beginning at `0x21FBE` serves as the following terminator.

Classification of entire bank:

**MENU/TEMPLATE DATA GREEN**

---

# 7. Relocation proof for the menu/data classification

Between `0x1BD93` and the initialized DGROUP base `0x27710`, the MZ relocation table
contains exactly:

**66 relocation entries**

Their locations are confined to:

- the relocated WORD at `1BDA0`;
- segment words of text far pointers in the remote-control menu;
- segment words of menu text far pointers in the `219A0+` menu bank;
- segment words of the shared hardware-menu callback pointer.

Examples:

```text
1D090
1D0A2
1D0B4
1D0C6
1D0D8

219B0
219C2
...
21FBC
```

This is precisely what is expected for relocatable **data structures containing far
pointers**.

It is not the relocation shape of and hidden code segment.

---

# 8. `0x21FBE..0x2770F` — final zero/BSS state region

Length:

**22,354 bytes**

Every byte is zero.

No nonzero instruction island exists inside the region.

Classification:

**STATE/BSS GREEN**

---

# 9. `0x27710..0x29D5F` — initialized DGROUP

Length:

**9,808 bytes = 0x2650**

This is the initialized DOS data segment used as the game'with main DS.

The region is densely populated with:

- Nitemare 3D error/status strings;
- file/resource names;
- gameplay messages;
- story/event text;
- menu strings;
- save/load UI strings;
- renderer/resource errors;
- audio-detection/status text;
- static lookup values/tables;
- runtime path/environment constants;
- Microsoft C run-time messages.

## Representative N3D strings

Early DGROUP contains:

```text
Door not in map
Push not in map
MAXDOORS exceeded (%d)
MAXPANELS exceeded (%d)
MAXPUSHES exceeded (%d)
Wall class %d undefined
Obj class %d undefined
No objects of class %d in level
```

Resource/file strings include:

```text
snd.dat
game.pal
map.
img.
demo.
config.sav
uif.dat
debug.txt
ending.fli
nite3d.bsf
user.sav
```

Audio-status strings include:

```text
SB DSP forced on port %xH, IRQ %d
Unable to force DSP detection
SB DSP detected at IRQ %d
SB DSP not detected - defaulting to PC speaker
```

## Menu/UI strings

The text pointers used by the menu records resolve into this DGROUP, including:

```text
New game
Configure game...
Load game...
Save game...
Instructions
Return to game
Restart at last save
Episode 1
Episode 2
Episode 3
Be gentle!
I'm tough!
Let's party!
Hardware...
Cheats...
Mouse
Joystick
Music
Sound FX
Omniscient (all-knowing)
...
Floor 1
...
Floor 10
Climb up
Climb down
Go down
Cancel
```

## Microsoft C runtime identity

At DGROUP offset `0008`:

`MS Run-Time Library - Copyright (c) 1992, Microsoft Corp`

The tail contains standard Microsoft runtime messages such as:

```text
R6000 - stack overflow
R6003 - integer divide by 0
R6009 - not enough space for environment
R6002 - floating-point support not loaded
R6001 - null pointer assignment
```

The load image ends immediately after those initialized runtime data strings.

Classification:

**INITIALIZED DGROUP DATA GREEN**

---

# 10. Definitive executable end

The complete unpacked load image ends at:

`0x29D5F`

Pass 33 partitions every byte from the final executable return at `0x1BD92`
through `0x29D5F` as non-code.

There is therefore:

- no hidden code segment after `1BD92`;
- no later executable function entry;
- no reason to continue linear disassembly beyond `1BD92`;
- no remaining post-tail function census to discover.

The DOS V2.0 **highest real executable address is now closed**.

This also means any future decompiler label placed inside `1BD93..29D5F` must be treated
as data until an explicit external control-flow reference proves otherwise.

---

# 11. Byte-map impact

Pass 33 classifies:

`0x1BD93 .. 0x29D5F`

Total:

**57,293 DATA/TABLE/STATE bytes -> GREEN**

Breakdown:

| Range | Bytes | Role |
|---|---:|---|
| `1BD93–1BD9F` | 13 | zero state |
| `1BDA0–1BDA1` | 2 | relocated WORD datum |
| `1BDA2–1D07F` | 4,830 | zero/BSS state |
| `1D080–1D0D9` | 90 | remote doors/cannons menu |
| `1D0DA–2199F` | 18,630 | zero/BSS state |
| `219A0–21FBD` | 1,566 | 87 menu/template records |
| `21FBE–2770F` | 22,354 | zero/BSS state |
| `27710–29D5F` | 9,808 | initialized DGROUP |

Total:

`57,293 bytes`.

---

# 12. Closure metrics

Pass 32 executable CODE GREEN cumulative:

`75,517 bytes`

Pass 33 adds:

`0 executable bytes`

Therefore executable CODE GREEN remains:

**75,517 bytes**

Tracked DATA/TABLE/STATE GREEN after Pass 32:

`15,259 bytes`

Pass 33 adds:

`57,293 bytes`

New tracked DATA/TABLE/STATE GREEN:

**72,552 bytes**

Combined tracked GREEN classifications:

`75,517 + 72,552 = 148,069 bytes`

To **not** interpret that combined number as an executable-code percentage; code and
data remain separate overlays.

---

# 13. Consequence for remaining work

Pass 4 already closed:

`0x5342..0x59EE`

Pass 5 then begins at:

`0x59F0`

and the later passes now carry static closure continuously all the way through the
last executable byte and the remaining data image.

Therefore the forward linear closure phase is complete.

The next useful pass must jump back into the **early code core below `0x5342`** and
resolve only the still-non-GREEN subranges left there after passes 1–3.

Recommended Pass 34 procedure:

1. reconstruct the latest color map for `0x0000..0x5341`;
2. subtract every range already GREEN in passes 1–3;
3. list only remaining RED -> ORANGE -> YELLOW intervals;
4. attack the lowest-confidence genuine function body first;
5. avoid revisiting the now-closed continuous tail from `0x5342` onward.

This is the correct next direction for increasing the actual Nitemare-3D core
reverse-engineering percentage.