# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 33

Date: 2026-10-03

Primary unpacked image:
- `N3D_DOS_v2.0_IDA.EXE`
- image size: `0x29D60 = 171,360 bytes`
- unpacked-image SHA-256:
  `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`

Address convention:
- all addresses are offsets in the unpacked MZ load image
- raw 16-bit machine code is authoritative
- CODE and DATA/STATE/PADDING are separate byte-map classes

## Result

Pass 33 closes the complete post-code tail:

`0x1BD93 .. 0x29D5F`

as **GREEN / non-executable DATA, STATE, BSS or PADDING**.

Total span:

**57,293 bytes**

No executable bytes are promoted in this pass.

The final executable helper from pass 32 ends at:

`0x1BD92`.

AND fresh MZ-relocation audit found:

- `1,670` relocation records in the unpacked reference;
- `1,414` relocation-backed FAR CALL/JMP instructions;
- **zero** direct FAR CALL/JMP targets at or beyond `0x1BD93`.

Together with the absence of later function entries and the structural contents below,
this is strong evidence that `0x1BD93..end` is data/state, not and hidden late code
segment.

The post-code tail resolves into four main address spaces:

1. WORX tail/BSS and padding;
2. static menu-record segments;
3. the `21FD` far gameplay arena;
4. N3D/CRT DGROUP at segment `2771`.

---

# 1. `0x1BD93..0x1C07F` — WORX tail state / inter-segment padding

Length:

**749 bytes**

Observed layout:

- `1BD93..1BD9F` — zeros;
- `1BDA0..1BDA1` — relocated WORD `21FDh`;
- remainder — zero-filled.

No direct relocated FAR CALL/JMP targets land in this region.

Classification:

**GREEN DATA/STATE/PADDING**.

---

# 2. segment `1C08` — remote door/cannon menu

Segment base:

`1C08h * 16 = 0x1C080`.

The remote-controller function at image `0x9646` explicitly loads:

```text
ES = 1C08h
SI = 1000h
```

therefore menu address:

`1C08:1000 = image 0x1D080`.

## `0x1C080..0x1D07F`

Exactly `0x1000` zero bytes preceding the menu.

Classification:

**GREEN zero-initialized data/state**.

## `0x1D080..0x1D0D9`

Five active 18-byte menu records:

| Action | Text pointer | Meaning |
|---:|---|---|
| `1Bh` | `2771:14AE` | Open remote doors |
| `1Ch` | `2771:14C0` | Close remote doors |
| `1Dh` | `2771:14D3` | Enable remote cannons |
| `1Eh` | `2771:14E9` | Disable remote cannons |
| `06h` | `2771:1500` | Cancel |

The record layout is the already closed 18-byte menu structure.

## `0x1D0DA..0x1D0EB`

One all-zero 18-byte terminator record.

Thus the remote menu bank is:

`1C08:1000..106B`.

Classification:

**GREEN MENU DATA**.

---

# 3. `0x1D0EC..0x20B8F` — zero-filled inter-segment state/padding

Length:

**15,012 bytes**

This entire region is zero in the unpacked load image.

No relocation-backed FAR CALL/JMP targets enter it.

It is therefore not unresolved executable code.

Classification:

**GREEN BSS/PADDING**.

---

# 4. segment `20B9` — static menu-record bank

Segment base:

`20B9h * 16 = 0x20B90`.

The first initialized menu begins at:

`20B9:0E10 = image 0x219A0`.

The prefix:

`0x20B90..0x2199F`

is `0x0E10 = 3600` zero bytes.

Classification:

**GREEN zero-initialized menu/UI storage**.

## Exact static menu tables

Every active record is exactly:

`0x12 = 18 bytes`.

Each table is followed by one all-zero 18-byte terminator.

| Segment offset | Image range | Active rows | Recovered menu |
|---:|---|---:|---|
| `0E10` | `219A0–21A0B` | 6 | front-end main menu |
| `0E8E` | `21A1E–21A9B` | 7 | in-game main menu |
| `0F1E` | `21AAE–21B2B` | 7 | restart-at-last-save menu |
| `0FAE` | `21B3E–21B73` | 3 | episode chooser |
| `0FF6` | `21B86–21BBB` | 3 | difficulty chooser |
| `103E` | `21BCE–21C03` | 3 | configuration menu |
| `1086` | `21C16–21CC9` | 10 | LOAD-game slot rows |
| `114C` | `21CDC–21D8F` | 10 | SAVE-game editable rows |
| `1212` | `21DA2–21DFB` | 5 | hardware settings |
| `127E` | `21E0E–21E79` | 6 | cheat settings |
| `12FC` | `21E8C–21F3F` | 10 | Floor 1..10 chooser |
| `13C2` | `21F52–21F87` | 3 | Climb up/down/cancel |
| `140A` | `21F9A–21FBD` | 2 | Go down/cancel |

Totals:

- **75 active menu records**
- `75 * 18 = 1350 bytes`
- **13 zero terminator records**
- `13 * 18 = 234 bytes`

Complete initialized bank:

`0x219A0..0x21FCF`

= **1,584 bytes = 88 × 18-byte records**.

This corrects older shorthand that sometimes treated offsets such as `103E`, `1212`
or `127E` as near-DS addresses.  They are offsets inside far segment `20B9`.

Classification:

**GREEN MENU DATA/TABLE**.

---

# 5. segment `21FD` — far gameplay arena

Segment base:

`21FDh * 16 = image 0x21FD0`.

This is the zero-initialized far arena used by the runtime gameplay structures and
mutable 64×64 MAP image.

The layout fills the segment exactly up to the next static segment.

## `21FD:0000..0005`

Six bytes of arena header/scratch preceding the OBJECT pool.

Image:

`0x21FD0..0x21FD5`.

## `21FD:0006..264D` — OBJECT pool

Capacity:

`350`

Stride:

`0x1C = 28 bytes`

Size:

`350 * 28 = 9800 bytes`

Image:

`0x21FD6..0x2461D`.

## `21FD:264E..3075` — GUARD pool

Capacity:

`100`

Stride:

`0x1A = 26 bytes`

Size:

`2600 bytes`

Image:

`0x2461E..0x25045`.

## `21FD:3076..34F5` — paired-wall controllers

Capacity:

`64`

Stride:

`0x12 = 18 bytes`

Size:

`1152 bytes`

Image:

`0x25046..0x254C5`.

## `21FD:34F6..36B5` — special/four-way wall records

Capacity:

`32`

Stride:

`0x0E = 14 bytes`

Size:

`448 bytes`

Image:

`0x254C6..0x25685`.

## `21FD:36B6..36FD` — push/object-reference records

Capacity:

`12`

Stride:

`6 bytes`

Size:

`72 bytes`

Image:

`0x25686..0x256CD`.

## `21FD:36FE..373D` — GUARD area wake/latch cache

Exactly:

`64 bytes`

Image:

`0x256CE..0x2570D`.

The GUARD area-wake helper clears this whole region when invoked with `FFFFh`.

## `21FD:373E..573D` — mutable MAP image

Exactly:

```text
64 * 64 * 2 = 8192 bytes
```

One cell:

```text
byte 0 = wall ID
byte 1 = object ID / mutable occupancy
```

Image:

`0x2570E..0x2770D`.

## `21FD:573E..573F`

Two bytes of segment tail/padding.

Image:

`0x2770E..0x2770F`.

### Structural result

The full static `21FD` segment occupies:

`0x21FD0..0x2770F`

= **22,336 bytes**.

Its internal capacities fit exactly without overlap.

Classification:

**GREEN GAMEPLAY STATE/BSS**.

---

# 6. segment `2771` — N3D/CRT DGROUP initialized prefix

Segment base:

`2771h * 16 = image 0x27710`.

This segment identity is directly confirmed by far text pointers stored in the menu
records.

Examples:

```text
2771:14AE -> image 28BBE -> "Open remote doors"
2771:1C6F -> image 2937F -> "Press a key"
2771:1F02 -> image 29612 -> "user.sav"
2771:2045 -> image 29755 -> 52-byte BSF XOR key string
```

The unpacked image contains the initialized prefix:

`2771:0000..264F`

= image:

`0x27710..0x29D5F`

= **9,808 bytes**.

Runtime DS/BSS continues beyond the bytes physically initialized in the load image.

---

# 7. `2771:0000..20FB` — Nitemare-3D initialized data/string pool

Size:

`0x20FC = 8,444 bytes`.

Image:

`0x27710..0x2980B`.

This region contains N3D-owned static data including:

- file names:
  - `snd.dat`
  - `game.pal`
  - `uif.dat`
  - `config.sav`
  - `debug.txt`
  - `nite3d.bsf`
  - `n3d.exe`
  - `map.1`
  - `ending.fli`
  - `user.sav`;
- startup and diagnostic strings;
- GUARD/OBJECT/VEC overflow and error strings;
- episode/story/dialogue text;
- SAFE combinations;
- remote door/cannon menu labels;
- developer-status format strings;
- all top-level menu labels;
- hardware and cheat labels;
- Floor 1..10 / stair labels;
- save/load confirmation strings;
- renderer/VEC error strings;
- fixed N3D tables and initialized bytes referenced by gameplay.

AND particularly important initialized object is:

`2771:2045`

whose next exactly `0x34 = 52` bytes are:

`Copyright 1992, David P Gray, Gray Design Associates`

The BSF transform routine uses these 52 bytes directly as its repeating XOR key.

Classification:

**GREEN N3D STATIC DATA/TABLE/STRINGS**.

---

# 8. `2771:20FC..264F` — Microsoft C runtime initialized data

Size:

**1,364 bytes**.

Image:

`0x2980C..0x29D5F`.

The boundary is strongly marked by literal:

`_C_FILE_INFO=`

at:

`2771:20FC`.

The region contains Microsoft 1992 runtime initialized state/tables and strings,
including:

- stream/file-info state;
- character/type and formatting tables;
- environment/shell names such as:
  - `COMSPEC`
  - `.bat`
  - `.exe`
  - `.com`
  - `%PATH`
  - `command.com`;
- Microsoft runtime message catalog:
  - `!<<NMSG>>`
  - `R6000 - stack overflow`
  - `R6003 - integer divide by 0`
  - `R6009 - not enough space for environment`
  - `R6002 - floating-point support not loaded`
  - `R6001 - null pointer assignment`.

This is compiler/runtime data, not unrecognized N3D gameplay.

Classification:

**GREEN CRT DATA/TABLE/STRINGS**.

---

# 9. Direct-transfer proof that the tail contains no hidden code

The unpacked MZ header contains:

**1,670 relocation records**.

AND fresh relocation-aware scan identifies:

**1,414 FAR CALL/JMP instructions**

whose relocated segment words are present in the table.

Number whose target linearizes to:

`>= 0x1BD93`

and remains inside the load image:

**0**.

This does not mean every byte sequence after `1BD92` is incapable of looking like an
8086 instruction.  Data naturally contains opcode-like bytes.

It means there is no relocation-backed direct far control-transfer into the region,
while its actual byte layout independently resolves as BSS, menu records, gameplay
arena, strings and CRT tables.

Therefore it should not be colored RED merely because and linear disassembler can invent
instructions there.

---

# 10. Byte-map impact

Pass 33 newly enumerates:

**57,293 bytes**

as GREEN DATA/STATE/BSS/PADDING.

Breakdown:

| Range | Bytes | Classification |
|---|---:|---|
| `1BD93–1C07F` | 749 | WORX tail state/padding |
| `1C080–1D0EB` | 4,204 | remote-menu segment + zero storage |
| `1D0EC–20B8F` | 15,012 | zero BSS/padding |
| `20B90–2199F` | 3,600 | menu-segment zero prefix |
| `219A0–21FCF` | 1,584 | 18-byte static menu records |
| `21FD0–2770F` | 22,336 | far gameplay arena |
| `27710–2980B` | 8,444 | N3D initialized DGROUP |
| `2980C–29D5F` | 1,364 | Microsoft CRT initialized DGROUP |

Total:

**57,293 bytes**.

No executable code is counted in this pass.

---

# 11. Updated tracked GREEN totals

From pass 32:

- executable CODE GREEN cumulative:
  **75,517 bytes**
- tracked DATA/TABLE/STATE GREEN:
  **15,259 bytes**

Pass 33 adds:

- DATA/STATE/BSS/PADDING:
  **57,293 bytes**

New tracked DATA/TABLE/STATE GREEN:

**72,552 bytes**

Combined tracked GREEN bytes:

```text
75,517 + 72,552 = 148,069 bytes
```

out of the fully unpacked:

`171,360-byte`

load image.

Tracked GREEN share:

**86.41%**

Still not explicitly reclassified in this cumulative ledger:

```text
171,360 - 148,069 = 23,291 bytes
```

or:

**13.59%**.

This 23,291-byte remainder is now the correct target for the next fresh byte-level
RED/ORANGE/YELLOW recensus.  It should not be confused with the older
116,094-byte packed-image census.

---

# 12. Main structural correction from Pass 33

The final DOS load-image organization is now substantially clearer:

```text
00000 ...              N3D game code + CRT + WORX code
...
1BD92                   last recovered executable helper
1BD93 ...               non-code tail
1C08:1000               remote door/cannon menu
20B9:0E10..1421         static menu bank
21FD:0000..573F         far gameplay arena
2771:0000..264F         initialized N3D/CRT DGROUP
29D60                   end of unpacked load image
```

With any future Defraggler-style byte map should use separate fills/overlays for:

- GREEN executable code;
- GREEN initialized data/table;
- GREEN BSS/state;
- GREEN padding;
- runtime-validation status.

To not show the 57,293-byte post-code tail as RED simply because it is not executable.

---

# 13. Next target

Perform and **fresh exact recensus of the remaining 23,291 bytes** against all closure
passes.

The next pass should output:

- exact RED byte count;
- exact ORANGE byte count;
- exact YELLOW byte count;
- number of contiguous ranges in each color;
- start/end address of every remaining non-GREEN range;
- whether each range is:
  - game code,
  - CRT,
  - WORX,
  - data/table,
  - padding,
  - or and stale decompiler-boundary artifact.

That will finally replace the old approximate color counts with and current
post-pass-33 census.