# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 35

Date: 2026-10-03

Primary raw image:
- `N3D_DOS_v2.0_IDA.EXE`
- unpacked load-image SHA-256:
  `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`
- unpacked image size: `0x29D60 = 171,360 bytes`

Address convention:
- all addresses are unpacked-image offsets;
- raw 16-bit machine code is authoritative;
- runtime/pixel acceptance remains and separate overlay.

## Result

Pass 35 closes the next complete early-code band:

`0x15EE .. 0x2771`

as **GREEN / deep static semantics**.

Total continuous span:

**4,484 bytes**

This is the DOS planar-VGA / palette / wall-span / sprite-queue renderer front end.

The pass also repairs and large number of stale Ghidra boundaries.  Several entries that
had previously been treated as independent LOW/MEDIUM functions are ordinary
instructions or labels inside larger raw functions.

Correct raw census in this band:

- **32 real callable/intentional entries**, including four tiny no-op callbacks;
- the rest is code plus ordinary alignment NOPs;
- **13 stale function starts are removed**.

The next genuine game-owned routine begins at:

`0x2772`

and starts the resource-file I/O/loading band.

---

# 1. `0x15EE..0x1606` — `SwapDisplayPageAndProgramCrtcStart`

The routine swaps the two page/start globals:

```text
DS:012C
DS:012E
```

Then it programs VGA CRTC register:

`0x0C`

through port:

`0x3D4`

using the high address byte derived from the newly selected page.

This is the non-waiting page/start update used when and full retrace wait is not
required.

### Boundary correction

Old entry:

`0x1601`

is only the instruction:

```text
MOV DX,03D4h
```

inside this function.

It is **not** and separate routine.

**Status: YELLOW + false split -> GREEN.**

---

# 2. `0x1608..0x1636` — `SwapDisplayPageAndWaitVerticalRetrace`

This is the synchronized page-flip companion.

Flow:

1. swap `DS:012C/012E`;
2. poll VGA input-status port `0x3DA` until display-enable bit 0 clears;
3. disable interrupts;
4. program CRTC start-address high register `0x0C`;
5. re-enable interrupts;
6. poll `0x3DA` until vertical-retrace bit `0x08` becomes set;
7. return.

This is the full page-flip/retrace synchronization path used by the game scheduler.

**Status: YELLOW -> GREEN.**

---

# 3. `0x1638..0x1688` — `InitializeOrRestoreGameVideoMode`

One parameter selects two real modes.

## Mode 0 — enter game display

1. query current BIOS video mode with `INT 10h AH=0Fh`;
2. save it at `DS:3452`;
3. call the planar-VGA initializer at `0x1FC6`;
4. query video mode again;
5. require BIOS mode `13h`;
6. on mismatch enter the fatal video-mode path;
7. build the reciprocal projection table at `0x1560`.

## Mode 1 — restore previous mode

If saved mode `DS:3452` is nonzero:

```text
INT 10h AH=00h, AL=savedMode
```

Other operation values return without action.

**Status: YELLOW -> GREEN.**

---

# 4. `0x168A..0x16AE` — `UploadFullVgaPalette`

Major label correction.

The old tracker called this and single-color DAC writer.

Raw behavior:

1. select VGA DAC index `0` through port `0x3C8`;
2. output exactly:
   `0x300 = 768`
   bytes from the supplied palette pointer;
3. every byte is written to port `0x3C9`.

Therefore this uploads all:

`256 × RGB`

palette components.

**Status: old mislabel -> GREEN.**

---

# 5. `0x16B0..0x16CC` — `WriteVgaDacEntry`

The companion routine writes exactly one palette entry.

Inputs:

- palette index;
- R;
- G;
- B.

Ports:

```text
3C8h  index
3C9h  R,G,B
```

The old name `WriteVgaPaletteRange` was too broad.

**Status: GREEN.**

---

# 6. `0x16CE..0x17B2` — `BuildShadePaletteRemapTable`

This is one real function.  Old entries `16F5`, `1715` and `176A` are interior
instructions.

The routine uses the shade-level set:

```text
0, 4, 8, 12, 16, 20, 30, 40
```

selected through:

`DS:6278`.

For each of the 256 source palette colors at:

`DS:4A64`

it:

1. subtracts the selected shade amount independently from R/G/B;
2. clamps each component at zero;
3. scans all 256 palette entries;
4. computes nearest-color distance:

```text
abs(R-R2) + abs(G-G2) + abs(B-B2)
```

5. retains the first strict minimum;
6. stores the selected palette index in the active remap row beginning in the
   `DS:D20C` family.

This is the DOS shade/palette remap generator used by the planar renderer.

### False starts removed

```text
16F5
1715
176A
```

**Status: fragmented MEDIUM -> GREEN.**

---

# 7. `0x17B4..0x19A0` — `RunPaletteTransitionEffect`

This is the complete palette-transition/fade dispatcher.

Input mode range:

`0..9`.

It keeps and local `0x308`-byte palette workspace and uses the base palette rooted at
`DS:4A64`.

Observed transition families include:

- immediate black palette;
- progressive black -> target fade;
- target -> black fade;
- per-channel R/G/B brightening paths;
- final channel-forcing transition paths.

The fade steps use the original integer increments/decrements and repeatedly call:

- `UploadFullVgaPalette`;
- VGA status/retrace wait helpers.

The transition temporarily forces display-dirty state through `DS:3CD1` and restores
the previous value before returning.

### Inline data

The mode switch uses and 10-WORD jump table inside the function.

### False starts removed

Old entries:

```text
1921
1988
```

are interior branches of this one dispatcher.

They are not independent `FadePaletteIn` / `SetPaletteEntry` functions in V2.0.

**Status: YELLOW/false splits -> GREEN.**

---

# 8. Tiny VGA synchronization callbacks

The raw bytes after the palette dispatcher contain several deliberately tiny entries.

## `0x19A2` — `NoOpVideoCallbackA`

Single `RETF`.

## `0x19A4..0x19B5` — `WaitDisplayEnableTransition`

Polls port `0x3DA`, masking with `0x09`, and waits for the expected display-status
transition sequence.

## `0x19B6..0x19BE` — `WaitVerticalRetraceStart`

Polls port `0x3DA` until bit `0x08` is set.

### Boundary correction

Old `19BA` is the `TEST AL,08h` instruction inside this function.

## `0x19C0` — `NoOpVideoCallbackB`
## `0x19C2` — `NoOpVideoCallbackC`
## `0x19C4` — `NoOpVideoCallbackD`

Each is one `RETF`.

These callback slots are known empty behavior, not UNKNOWN code.

**Status: GREEN.**

---

# 9. `0x19C6..0x1A2C` — `FillViewportCeilingAndFloor`

Uses the currently selected planar page segment and VGA sequencer map mask.

The destination row pitch is:

`0x50 = 80 bytes`.

The viewport rectangle is derived from the caller'with X/Y/width/height.

It fills the two vertical halves using separate runtime color bytes:

```text
DS:627B
DS:627A
```

This is the DOS ceiling/floor/background fill used before wall/object drawing.

**Status: YELLOW -> GREEN.**

---

# 10. `0x1A2E..0x1B3D` — `DrawScaledPlanarColumnWithOptionalShade`

This is one raw function.

Old entries:

```text
1AE1
1B10
```

are interior instructions.

The function:

1. derives the VGA byte address from screen X/Y using 80 bytes/row;
2. chooses the sequencer plane mask from `X & 3`;
3. uses fixed-point source-step tables derived from projected height;
4. reads source texels through the supplied far bitmap pointer;
5. writes and vertical planar column;
6. in unshaded mode writes texel indices directly;
7. in shaded mode translates texels through the current palette-remap table before
   output.

This is the low-level planar wall/sprite vertical sampling writer.

**Status: YELLOW + false splits -> GREEN.**

---

# 11. `0x1B3E..0x1D3D` — `DrawScaledPlanarBitmapWithClipping`

The real entry is `1B3E`.

Old `1B71` is interior code.

The routine consumes and bitmap/resource descriptor plus and screen rectangle and performs:

- horizontal viewport clipping against `4548/454A`;
- vertical clipping against `454C/454E`;
- per-plane VGA selection;
- 80-byte planar row addressing;
- source-column stepping;
- optional masking/transparency;
- interaction with the per-column wall visibility/depth information;
- dispatch into the low-level vertical-column writer.

This is the shared DOS projected bitmap/sprite drawing primitive.

It is also the renderer reached later by the 18-byte projected-object queue.

**Status: YELLOW -> GREEN.**

---

# 12. `0x1D3E..0x1DEB` — `BlitPlanarBitmapColumns`

Copies and far source bitmap into and selected VGA page using explicit plane masks.

It:

- chooses page `DS:012E` or `DS:012C`;
- derives byte address from X/Y;
- rotates the map mask across VGA planes;
- walks source columns/rows;
- uses the fixed 80-byte destination pitch.

This is and direct planar bitmap/blit primitive.

**Status: GREEN.**

---

# 13. `0x1DEC..0x1E33` — `PutPlanarPixel`

Major semantic correction to old `SetVgaWriteMode`.

The raw function computes:

```text
address = y*80 + x/4
plane   = 1 << (x & 3)
```

selects the requested display page, programs sequencer map mask and writes exactly one
color byte.

This is and planar pixel writer.

**Status: corrected -> GREEN.**

---

# 14. `0x1E34..0x1EA5` — `FillPlanarRectangle`

Inputs describe:

- X;
- Y;
- width;
- height;
- color;
- page.

The function writes the filled rectangle directly in unchained planar VGA memory.

It rotates/updates the sequencer plane mask as X crosses plane boundaries and advances
rows using the 80-byte pitch.

**Status: GREEN.**

---

# 15. `0x1EA6..0x1EDA` — `FillRectangleBothPages`

Thin wrapper around `FillPlanarRectangle`.

It draws the same rectangle to both display pages.

This is used by automap/UI clearing and background operations.

**Status: GREEN.**

---

# 16. `0x1EDC..0x1F23` — `DrawInsetUiRectanglePair`

The routine obtains and cached palette index through the nearest-color cache helper at
`0x28F8`, then performs two `FillPlanarRectangle` calls:

- one offset/inset rectangle;
- one caller-colored/base rectangle.

This is and two-layer UI rectangle/border primitive.

The historical UI label is less important than the fully bounded machine contract.

**Status: GREEN.**

---

# 17. `0x1F24..0x1F99` — `DrawMonochromePlanarBitmap`

This is not and display-start register setter.

The source begins with compact width/height information followed by and 1-bit bitmap.

The routine:

1. selects page `012E/012C`;
2. derives X/Y VGA address;
3. computes and starting plane mask from `X & 3`;
4. expands source bits across planar map masks;
5. writes the caller'with single color;
6. advances destination rows by `0x50`.

This is the DOS 1-bit glyph/icon rasterizer used by text/UI rendering.

**Status: old mislabel -> GREEN.**

---

# 18. `0x1F9A..0x1FC4` — `ClearPlanarPage`

Selects all four VGA planes and fills an entire 320×200 planar page.

The loop writes:

`0x1F40 = 8000 WORDs = 16000 bytes`

per plane-address space, covering:

`320*200/4`.

Caller supplies:

- fill color;
- page selector.

**Status: corrected -> GREEN.**

---

# 19. `0x1FC6..0x2019` — `InitializePlanarModeX320x200`

This initializes the DOS unchained planar VGA mode used by Nitemare-3D.

Flow:

1. BIOS `INT 10h` mode `13h`;
2. alter Sequencer Memory Mode register to disable chain-4 / configure planar access;
3. adjust Graphics Controller mode/misc registers;
4. clear both game display pages through `ClearPlanarPage`;
5. alter CRTC underline/mode-control bits for the planar 320×200 layout.

This is the game'with Mode-X-style planar setup routine.

**Status: YELLOW -> GREEN.**

---

# 20. `0x201A..0x2029` — `MarkProjectedObjectQueueFree`

Walks the 100-entry projected-object/sprite queue:

```text
base   = DS:50F2
stride = 0x12 = 18 bytes
count  = 100
```

and writes:

`entry[0] = 1`

to every slot.

This is the queue reset/free-state initializer.

**Status: GREEN.**

---

# 21. `0x202A..0x213D` — `InitializeProjectedWallSpan`

This is the exact fixed-point span-interpolation builder already known from the
renderer audit.

It initializes one projected wall/span descriptor from two screen endpoint values.

Key output includes:

- first/last X;
- first/last projected vertical value;
- signed 16.16:

```text
dYdX = ((y2 - y1) << 16) / (x2 - x1)
```

- integer/fractional interpolation state;
- base value relative to projection horizon `DS:4554`.

This is and **wall span record**, not and runtime actor record.

**Status: corrected -> GREEN.**

---

# 22. `0x213E..0x21EE` — `BuildProjectedWallSpanTable`

Scans the per-column VEC owner buffer beginning at:

`DS:4564`

across the viewport.

Whenever owner identity changes, it emits one projected span descriptor to the span
array beginning near:

`DS:4D6E`

and initializes it through `InitializeProjectedWallSpan`.

The span count is bounded to:

`0x32 = 50`.

This is the owner-buffer -> wall-span conversion stage.

### Boundary correction

Old entry:

`21A6`

is an interior instruction/label inside this function.

It is **not** and separate renderer allocation/free routine.

**Status: YELLOW + false split -> GREEN.**

---

# 23. `0x21F0..0x22C9` — `QueueWorldObjectsInsideVisibleBounds`

This routine bridges wall visibility bounds to the projected-object queue.

It compares the currently visible world rectangle:

```text
DS:4D66..4D6C
```

against the player-relative X/Y sorted OBJECT pointer arrays:

```text
DS:D516
DS:DA8E
```

using cursors:

```text
DS:416E
DS:4170
```

It chooses the narrower axis span and walks outward only while objects remain inside
the visible bounds.

Every accepted OBJECT is passed to:

`0xB2D4 = ProjectAndQueueWorldObjectSpan`.

Thus this function is the culling/collection bridge:

```text
visible wall bounds
 -> sorted OBJECT lists
 -> project qualifying world objects
 -> append projected 18-byte draw records
```

**Status: MEDIUM -> GREEN.**

---

# 24. `0x22CA..0x241D` — `CorrectWallTextureCoordinateAtVecBounds`

This is the exact wall-endpoint/texture-coordinate correction family.

Inputs include:

- VEC pointer;
- current projected screen X;
- candidate texture coordinate;
- caller mask/width limit.

The routine examines:

- VEC projected X fields `+14/+18`;
- world endpoint fields `+0C/+0E/+10/+12`;
- orientation `+07`;
- class/type `+06`;
- special flag bit `+05 & 08`.

It applies orientation/class-specific endpoint correction at the left/right edge and
returns the result masked by:

`limit - 1`.

This is the DOS counterpart of the exact wall texture-U edge correction used by the
wall pixel path.

**Status: YELLOW -> GREEN.**

---

# 25. `0x241E..0x24FF` — `AdvanceWallOrObjectAnimationFrame`

Timestamped animation update.

It compares the 32-bit engine clock `DS:081E/0820` with record deadline `+08/+0A`.

When due it performs **one** animation step only; it does not catch up multiple overdue
frames.

It handles special cases including:

- class `0x2D` exploding-wall completion;
- class `0x2F`;
- class `0x07`;
- table-driven alternate animation selection using the game RNG.

The next absolute deadline is:

`currentTime + sequenceInterval`.

This matches the already closed DOS animation timing model.

**Status: GREEN.**

---

# 26. `0x2500..0x273A` — `RenderProjectedWallSpans`

Major boundary repair.

The real raw function begins at:

`0x2500`

with one stack frame and ends at:

`0x273A`.

Old entries:

```text
25DC
26C0
```

are interior branches of this same renderer.

The routine iterates prepared wall-span records, resolves the active VEC wall
sequence/frame and then, per projected column:

- advances the 16.16 projected vertical interpolation;
- computes wall texture U;
- calls `CorrectWallTextureCoordinateAtVecBounds`;
- resolves texture/frame data;
- uses the original vertical sampling tables;
- writes visibility/depth information for sprite occlusion;
- dispatches pixels through the planar scaled-column writer;
- applies shade remapping when selected;
- advances active wall animation where required.

This is the main DOS wall-span rendering loop.

It is the planar counterpart of the already statically closed Win16 wall renderer.

### False starts removed

```text
25DC
26C0
```

**Status: YELLOW/fragmented -> GREEN.**

---

# 27. `0x273C..0x2770` — `DrawQueuedProjectedObjects`

Processes exactly 100 projected-object queue entries:

```text
base   = DS:50F2
stride = 0x12
count  = 100
```

For each entry whose byte 0 indicates pending drawing:

1. resolve the queue'with resource/descriptor pointer at `+06`;
2. if its resident resource pointer is still NULL, call:
   `0x7B58 = AcquireDynamicRoundRobinCacheSlot`;
3. draw the prepared record through:
   `0x1B3E = DrawScaledPlanarBitmapWithClipping`;
4. mark queue byte 0 as processed/free (`1`).

This closes the wall -> object ordering:

```text
render wall spans
 -> use wall visibility/depth buffer
 -> draw queued projected objects/sprites
```

`0x2771` is alignment NOP.

**Status: GREEN.**

---

# 28. Corrected function map

The real callable/intentional entries in `15EE..2771` are:

```text
15EE
1608
1638
168A
16B0
16CE
17B4
19A2
19A4
19B6
19C0
19C2
19C4
19C6
1A2E
1B3E
1D3E
1DEC
1E34
1EA6
1EDC
1F24
1F9A
1FC6
201A
202A
213E
21F0
22CA
241E
2500
273C
```

Total:

**32 real entries**.

Definitively remove these stale starts:

```text
1601
16F5
1715
176A
1921
1988
19BA
1AE1
1B10
1B71
21A6
25DC
26C0
```

Total removed:

**13 false/interior entries**.

---

# 29. Renderer architecture now closed across the early band

After passes 34 and 35, the game-owned early renderer flow is:

```text
projection tables
    ↓
planar VGA init / page flip / DAC
    ↓
shade-remap table
    ↓
MAP -> VEC construction
    ↓
VEC directional traversal
    ↓
per-column owner buffer
    ↓
owner runs -> projected wall spans
    ↓
wall texture-U / vertical sampling
    ↓
planar wall columns
    ↓
visible world-object projection queue
    ↓
planar sprite/object draw
```

This is the recovered Nitemare-3D renderer architecture.

Pixel-perfect acceptance is still and separate runtime capture/comparison task.  It does
not justify keeping these statically bounded bytes yellow.

---

# 30. Byte-map impact

Continuous GREEN-CODE band:

`0x15EE .. 0x2771`

Size:

**4,484 bytes**

Combined with Pass 34:

```text
0x0000 .. 0x2771
```

is now one continuous statically GREEN early-engine code band.

Because many functions in this interval were already MEDIUM/HIGH or GREEN in older
trackers, Pass 35 deliberately does not add all 4,484 bytes to the historical
"newly RED/ORANGE/YELLOW -> GREEN" cumulative number.

The accurate next color-count update requires and fresh byte-level census after all
boundary deletions.

---

# 31. Next target

Continue at:

`0x2772`

The next early band contains:

- cached indexed resource-file reads;
- exact checked read/seek helpers;
- the 16-color nearest-palette cache at `28F8`;
- GAME.PAL loading/normalization;
- episode/resource-directory setup;
- block decode/decompression;
- higher-level IMG/UIF resource loading.

The two old entries `28F8/28FE` are especially worth normalizing because one is and real
palette-cache routine and the second is an alternate/mis-modeled entry with and bad
decompiler prototype.