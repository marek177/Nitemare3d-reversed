# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 37

Date: 2026-10-03

Primary raw image:
- `N3D_DOS_v2.0_IDA.EXE`
- physical MZ header: `0x1C00`
- unpacked image size: `0x29D60 = 171,360 bytes`
- unpacked-image SHA-256:
  `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`

Packed-family reference:
- `N3D-E-20(3).EXE`
- SHA-256:
  `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- all ranges below are offsets in the fully unpacked DOS load image;
- physical offset in `N3D_DOS_v2.0_IDA.EXE` = image offset + `0x1C00`;
- raw 16-bit machine code is authoritative;
- static GREEN is separate from runtime/pixel acceptance.

## Result

Pass 37 closes the complete CONFIG / USER.SAV / UIF / PCX / FLI-support bridge:

`0x3390 .. 0x45CD`

as **GREEN / deep static semantics**.

Continuous span:

**4,670 bytes**

Breakdown:

- executable routine content: **4,659 bytes**
- alignment NOPs: **11 bytes**
- real routine entries: **17**

This is an important structural pass because it joins:

`0x0000..0x338F`

already GREEN from passes 34–36

directly to:

`0x45CE+`

already GREEN from the earlier FLI/game-engine closure passes.

Therefore the Nitemare-owned engine/audio-wrapper code is now one continuous statically
GREEN band from:

`0x0000 .. 0x11EE6`

The next bytes `0x11EE7..0x11EF7` are transition/padding, and standard compiler/CRT
startup begins at `0x11EF8`.

---

# 1. Correct raw function census

| Range | Bytes | Correct role |
|---|---:|---|
| `3390–33DD` | 78 | `BuildPrefixedSaveConfigPath` |
| `33DE–3472` | 149 | `InitializeDefaultsAndLoadConfigSav` |
| `3474–34AC` | 57 | `WriteConfigSav` |
| `34AE–358B` | 222 | `ReadUserSaveSlotMetadata` |
| `358C–38E4` | 857 | `WriteUserSaveSlot` |
| `38E6–3D6E` | 1161 | `ReadUserSaveSlotAndRebindRuntime` |
| `3D70–3ED4` | 357 | `LoadPcx320x200FromFile` |
| `3ED6–3F4A` | 117 | `GetUifDescriptor` |
| `3F4C–40DA` | 399 | `ShowUifPcxResourceByIndex` |
| `40DC–4160` | 133 | `ReadUifSlotPayloadExact` |
| `4162–4255` | 244 | `LoadIndexedImgFramePayload` |
| `4256–4270` | 27 | `LoadTypedIndexedImgFrame` |
| `4272–4309` | 152 | `LoadXorEncryptedBlock` |
| `430A–4344` | 59 | `CopyBytesToLinearFrameRow` |
| `4346–4482` | 317 | `DecodeSegmentedRunLengthRows` |
| `4484–453D` | 186 | `DecodeFullWidthRunLengthImage` |
| `453E–45CD` | 144 | `DecodePaletteRunStream` |

Alignment NOPs:

```text
3473
34AD
38E5
3D6F
3ED5
3F4B
40DB
4161
4271
4345
4483
```

---

# 2. `0x3390..0x33DD` — `BuildPrefixedSaveConfigPath`

Copies the NUL-terminated global path prefix at:

`DS:3CDC`

into static destination:

`DS:3466`

and appends the caller'with suffix.

Return:

`AX = 3466`.

The routine deliberately inserts **no** path separator.

Therefore:

```text
prefix "SAVE\" + "user.sav" -> "SAVE\user.sav"
prefix "SAVE"  + "user.sav" -> "SAVEuser.sav"
```

The caller is responsible for supplying and prefix with the desired separator.

This prefix applies to CONFIG/USER.SAV paths, not to all game assets.

**Status: MEDIUM -> GREEN.**

---

# 3. `0x33DE..0x3472` — `InitializeDefaultsAndLoadConfigSav`

This closes the DOS V2.0 CONFIG.SAV load path.

## DOS defaults

The routine initializes the 16-byte block:

`DS:4144..DS:4153`

with:

```text
4144 dword = 0x00000130 = 304   viewport width
4148 byte  = 50                 mouse sensitivity
4149 byte  = 50                 joystick sensitivity
414A byte  = 60                 music volume
414B byte  = 70                 SFX volume
414C byte  = 1                  mouse enabled default flag
414D byte  = 1                  music enabled
414E byte  = 1                  SFX enabled
414F byte  = 0                  joystick enabled
4150 byte  = 0                  Omniscient
4151 byte  = 0                  Omnipotent
4152 byte  = 0                  Omnifarious
4153 byte  = 0                  Omnificent
```

## File load

It builds the prefixed CONFIG filename, opens it in binary mode and requires exact file
length:

`0x10 = 16 bytes`.

AND present file with another length enters the obsolete/invalid CONFIG error path.

It then reads exactly 16 bytes into:

`DS:4144`.

The handle is closed.

Finally it always calls:

`3332 = ConfigureViewportGeometryAndProjection`.

### Important version distinction

The DOS V2.0 CONFIG block is **16 bytes**.

The previously documented 20-byte CONFIG.SAV belongs to the Win16 build and must not
be used as the DOS V2.0 file size.

**Status: YELLOW -> GREEN.**

---

# 4. `0x3474..0x34AC` — `WriteConfigSav`

Builds the same prefixed CONFIG path.

It opens/creates the CONFIG file for writing and writes exactly:

`0x10 = 16 bytes`

from:

`DS:4144`.

Then it closes the handle.

This is the persistence path reached after accepted configuration-menu changes.

**Status: YELLOW -> GREEN.**

---

# 5. `0x34AE..0x358B` — `ReadUserSaveSlotMetadata`

This closes the save-slot probe used by LOAD/SAVE menus and restart-at-last-save logic.

## DOS V2.0 slot stride

The selected slot is addressed with exact record stride:

`0xD5E6 = 54,758 bytes`.

The routine opens the prefixed USER.SAV file and seeks to:

```text
slotIndex * 0xD5E6
```

It reads the first DWORD and requires:

`0x0000D5E6`.

Invalid/missing records return:

`0xFFFF`.

## Description and scene metadata

After the sentinel:

- the next `0x29 = 41` bytes are the save-slot description;
- when the caller supplied and description destination, the bytes are copied there;
- otherwise the function seeks over them.

It then reads the two scene selector WORDs used by the menu code as:

- episode;
- zero-based level.

The routine returns their packed metadata form used by the higher-level slot chooser.

Registration/shareware constraints are also checked through the already closed BSF
capability path.

### Major format correction

The raw DOS V2.0 slot size is:

**54,758 bytes (`0xD5E6`)**

not:

**55,015 bytes (`0xD6E7`)**.

`0xD6E7` is the audited Win16 slot size.

Difference:

`0xD6E7 - 0xD5E6 = 0x101 = 257 bytes`.

This distinction must remain build-specific.

**Status: old weak metadata reader -> GREEN.**

---

# 6. `0x358C..0x38E4` — `WriteUserSaveSlot`

This is the full DOS V2.0 USER.SAV serializer.

It captures the current game clock and seeks to:

`slotIndex * 0xD5E6`.

Then it writes the slot record in and fixed order.

## Header

```text
DWORD  0x0000D5E6   format/record-size sentinel
41 B   save description
WORD   episode
WORD   zero-based level
DWORD  saved game clock
```

## Live level/gameplay blocks

The serializer then writes:

```text
0x2000  live mutable 64x64x2 MAP
0x005E  DOS V2.0 player/gameplay block
0x6D60  VEC pool, 1000 × 28 B
0x2648  OBJECT pool, 350 × 28 B
0x0A28  GUARD pool, 100 × 26 B
0x0480  paired-wall controller pool, 64 × 18 B
0x0020  compact special/panel activation-state buffer
0x0150  projectile pool, 8 × 42 B
0x0007  story/event state bytes
0x0048  push/script records, 12 × 6 B
0x1000  automap raster
0x0040  GUARD one-shot wake cache
0x0100  palette/remap/state table
```

The final small display/shade state fields complete the DOS slot to its fixed
`0xD5E6` size.

Every write result contributes to the local error state; and short/error transfer enters
the fatal save path.

The file is closed after serialization.

## Important DOS-vs-Win16 difference

The DOS paired-wall runtime records are:

```text
64 × 18 B = 0x480
```

matching the DOS runtime stride `0x12`.

The Win16 save format has and different corresponding saved-state footprint, contributing
to the overall 257-byte slot-size difference.

**Status: old decompiler-damaged save writer -> GREEN.**

---

# 7. `0x38E6..0x3D6E` — `ReadUserSaveSlotAndRebindRuntime`

This is the complete DOS V2.0 USER.SAV restore path.

It performs the inverse fixed-size transfer from the chosen `0xD5E6` slot.

## Validation

The routine verifies:

- slot sentinel `0xD5E6`;
- saved episode;
- saved level;
- exact block transfer results.

The saved scene must match the currently initialized `DS:626A/626C`.

The LOAD menu may call the level initializer first when the save belongs to and different
scene.

## Rebuild nonpersistent pointers

After loading, process pointers are reconstructed rather than trusted from disk.

### Player MAP pointer

From loaded player cell coordinates:

```text
mapOffset =
    0x373E
    + ((cellY * 64 + cellX) * 2)

mapSegment = 0x21FD
```

The player heading/DDA state is rebuilt through:

`C838 = SetHeadingAndGridRayState`.

### OBJECT MAP pointers

Every loaded 28-byte OBJECT is rebound from its saved world X/Y to the corresponding
live MAP cell.

Then:

`AF5E = BuildSortedSpatialPointerTables`

recreates the X/Y sorted OBJECT index.

### Special/panel state

The compact 32-byte save buffer is expanded back into the corresponding runtime special
records.

### Projectile MAP pointers

For all 8 projectile slots, the embedded OBJECT'with MAP pointer is recomputed from the
loaded projectile X/Y coordinates.

## Rebase animation deadlines

The save stores and clock base.

After load the routine obtains the current game clock and adjusts saved animation
deadlines relative to it.

For each relevant VEC/OBJECT deadline:

```text
if oldDeadline < savedClock:
    newDeadline = 0
else:
    newDeadline =
        oldDeadline + (currentClock - savedClock)
```

This prevents old absolute process-time values from being used unchanged.

## Finalization

The routine applies current enabled cheat effects through:

`9792`.

Then it closes the save file.

### Major boundary correction

The old Ghidra entries:

```text
3A00
3A96
```

are interior/offcut starts inside this one real load/rebind routine.

They must be deleted as standalone functions.

**Status: old fragmented/weak load cluster -> GREEN.**

---

# 8. `0x3D70..0x3ED4` — `LoadPcx320x200FromFile`

This is the DOS external PCX-like 320×200 screen loader, including the optional
`dstopen.img` path.

Flow:

1. open caller filename;
2. read exactly `0x80 = 128` bytes of PCX header;
3. require manufacturer byte `0x0A`;
4. validate 320×200 geometry:
   - X extent difference `0x13F`;
   - Y extent difference `0xC7`;
5. decode the PCX RLE stream.

## RLE

For each source byte:

```text
if (byte & 0xC0) == 0xC0:
    runLength = byte & 0x3F
    color = next byte
else:
    runLength = 1
    color = byte
```

Pixels are accumulated into one 320-byte row.

Each completed row is sent to the display/framebuffer path.

Exactly 200 rows are produced.

The stream is closed.

Return:

```text
1  success
0  file could not be opened
```

### Boundary correction

Old entry:

`3DDE`

is an interior error/validation branch, not and standalone fatal function.

**Status: YELLOW -> GREEN.**

---

# 9. `0x3ED6..0x3F4A` — `GetUifDescriptor`

This resolves and long-standing false-function cluster.

The routine lazily loads the UIF directory.

## UIF directory

Exactly:

`0xC0 = 192 bytes`

are read into:

`DS:1BDB`.

That is:

`32 × 6-byte descriptors`.

Descriptor layout:

```text
+0 WORD   length
+2 DWORD  absolute file offset
```

The lazy-load flag is:

`DS:0678`.

The UIF source filename/path comes from the string state near:

`DS:0679`.

Return:

```text
DS:1BDB + slotIndex*6
```

as the descriptor pointer.

This directly matches the confirmed UIF.DAT architecture:

- slots 0–2: bitmap fonts;
- slots 3–16: 320×200 PCX screens;
- slots 17–31: empty/reserved.

### Major boundary corrections

Delete old standalone entries:

```text
3F1E
3F32
3F45
```

They are interior instructions of this routine.

Most importantly, old `FUN_1000_3F45`, once listed as an empty/no-op callback, is not and
function at all.

**Status: RED/LOW false boundaries -> GREEN.**

---

# 10. `0x3F4C..0x40DA` — `ShowUifPcxResourceByIndex`

Input:

`UIF slot index`.

It obtains the six-byte descriptor through `GetUifDescriptor`.

If descriptor length is zero:

`return 0`.

Otherwise:

1. open UIF.DAT;
2. seek to descriptor absolute offset;
3. read the 128-byte PCX header;
4. validate `0x0A` manufacturer and 320×200 geometry;
5. decode PCX RLE;
6. render all 200 rows;
7. close the source.

Return:

`1` on successful display.

This is the indexed screen path used by the UI/menu resources.

**Status: YELLOW -> GREEN.**

---

# 11. `0x40DC..0x4160` — `ReadUifSlotPayloadExact`

Generic raw UIF slot reader.

Flow:

1. open UIF.DAT;
2. get the indexed six-byte descriptor through `3ED6`;
3. seek to its absolute source offset;
4. read exactly descriptor length bytes into caller far destination;
5. report fatal error on open/short transfer;
6. close.

This is the DOS counterpart of the generic UIF raw-slot loader used by the bitmap-font
path.

It explains how UIF slots 0–2 are consumed without PCX decoding.

**Status: YELLOW -> GREEN.**

---

# 12. `0x4162..0x4255` — `LoadIndexedImgFramePayload`

This is an indexed IMG frame-stream loader.

It opens the current:

`DS:628C = img.N`.

The caller selector/index is transformed into and 4-byte directory-entry position.

The routine reads the selected 32-bit frame-stream source offset and requires it to be
nonzero.

Then it seeks to that source stream.

To select and later frame, it skips the requested number of preceding frame records:

```text
10-byte frame descriptor
+
width * height pixel payload
```

For the final selected frame it calls:

`2B3A = LoadImageFrameDescriptorAndPixels`.

The IMG file is closed afterward.

### Boundary correction

Old pseudo-functions:

```text
4206
4246
```

are interior paths of this routine.

**Status: YELLOW -> GREEN.**

---

# 13. `0x4256..0x4270` — `LoadTypedIndexedImgFrame`

Thin wrapper around the indexed IMG frame loader.

It first maps the caller'with resource/type selector through the existing wall/resource
class lookup family, then invokes:

`4162 = LoadIndexedImgFramePayload`.

The high-level historical source name is not required; the mechanical ABI is bounded.

**Status: MEDIUM -> GREEN.**

---

# 14. `0x4272..0x4309` — `LoadXorEncryptedBlock`

This is the generic allocated encrypted/text-block loader used by BSF.

Flow:

1. open caller filename;
2. allocate:
   `length + 1`
   bytes through the recovered far heap;
3. seek to caller-supplied 32-bit file offset;
4. read exactly `length` bytes;
5. write:
   `buffer[length] = 0`;
6. close the source;
7. call:
   `FD52 = XorTransformBufferWithChecksum`
   over exactly `length` bytes;
8. return the allocated far pointer.

The transform uses the known repeating 0x34-byte key and returns the for-transform XOR
checksum.

### Boundary correction

Old `4278` is just an interior instruction and must not remain and function entry.

**Status: YELLOW -> GREEN.**

---

# 15. `0x430A..0x4344` — `CopyBytesToLinearFrameRow`

Exact row-copy primitive.

Destination:

```text
framebuffer + y*0x140 + x
```

where:

`0x140 = 320`.

Copies exactly caller `length` bytes from the source buffer.

This is shared by the FLI row decoders.

`0x4345` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 16. `0x4346..0x4482` — `DecodeSegmentedRunLengthRows`

This is FLI chunk-type `0x0C` / segmented-delta row decoding.

The routine reads the row interval and then processes packet counts for each affected
row.

Packet control values distinguish:

- literal source-byte runs;
- repeated-color runs.

Decoded fragments are copied into the 320-pitch framebuffer through:

`430A = CopyBytesToLinearFrameRow`.

Only the affected row segments are written.

The raw function ends at `0x4482`.

`0x4483` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 17. `0x4484..0x453D` — `DecodeFullWidthRunLengthImage`

This is FLI chunk-type `0x0F`.

It decodes exactly:

`200`

rows.

Each row is reconstructed into and:

`320-byte`

line buffer.

The signed run-control byte selects between:

- repeated following color;
- literal byte sequence.

Every completed row is copied at X=0 through the 320-pitch row-copy helper.

This is the full-frame RLE path.

**Status: YELLOW -> GREEN.**

---

# 18. `0x453E..0x45CD` — `DecodePaletteRunStream`

This is FLI palette chunk-type `0x0B`.

The routine:

1. reads packet count;
2. maintains the current palette index;
3. applies each packet'with skip count;
4. reads packet entry count;
5. interprets count byte `0` as:
   `256 entries`;
6. reads RGB triplets;
7. sends each color to the low-level VGA palette setter.

The next function at:

`0x45CE`

is the already-green FLI chunk dispatcher.

Therefore the entire FLI decode chain is now contiguous:

```text
430A row copy
4346 segmented rows
4484 full-frame RLE
453E palette packets
45CE chunk dispatcher
462C frame dispatcher
4682 FLI player
```

**Status: YELLOW -> GREEN.**

---

# 19. False/stale function starts removed

Delete these entries from the corrected DOS V2.0 function inventory:

```text
3A00
3A96
3DDE
3F1E
3F32
3F45
4206
4246
4278
```

They are interior/offcut starts produced by bad decompiler boundary recovery.

This pass is particularly important because `3F45` was previously treated as and
mysterious empty callback, while raw code proves it is simply an instruction inside the
UIF descriptor accessor.

---

# 20. Byte-map impact

Continuous GREEN band added:

`0x3390 .. 0x45CD`

Size:

**4,670 bytes**

Routine content:

**4,659 bytes**

Alignment:

**11 bytes**

No unresolved inline jump table remains in this span.

Together with the surrounding passes:

```text
00000–338F   early engine/resource code       GREEN
3390–45CD    CONFIG/SAVE/UIF/PCX/FLI support GREEN
45CE–10135   gameplay/menu/renderer core      GREEN
10136–10BFB  MAP->VEC / visibility bridge     GREEN
10BFC–11EE6  DOS audio-driver wrapper layer   GREEN
```

Thus:

**`0x0000..0x11EE6` is now continuously statically GREEN for the game-owned engine and
its resident-audio wrapper interface.**

Compiler/CRT code beginning at `0x11EF8` is classified separately and has already been
handled in the later runtime closure passes.

---

# 21. Format corrections produced by this pass

## DOS CONFIG.SAV

```text
size = 16 bytes
runtime block = DS:4144..4153
```

To not apply the Win16 20-byte CONFIG layout to DOS V2.0.

## DOS USER.SAV slot

```text
slot size / sentinel = 0xD5E6 = 54,758 bytes
```

To not apply the Win16 `0xD6E7 = 55,015` slot stride to DOS V2.0.

The difference is:

`257 bytes`.

## UIF.DAT

Directory:

```text
32 × 6 B = 0xC0 bytes
WORD length
DWORD absolute offset
```

This is now tied directly to the DOS EXE loader.

---

# 22. Next target

The game-owned executable band up through `0x11EE6` is now statically continuous.

The next useful task is **not** to keep walking already-classified compiler CRT
linearly.

The highest-value next action is and fresh byte-level recensus of the full unpacked
`0x29D60` image, separating:

- N3D-owned GREEN code/data;
- standard CRT/runtime GREEN;
- alignment/data tables;
- any genuinely remaining RED/ORANGE/YELLOW islands.

That recensus can finally answer the user'with earlier question with exact current
RED/ORANGE/YELLOW byte counts and number of remaining ranges, instead of extrapolating
from the stale for-closure color map.