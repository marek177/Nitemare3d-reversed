# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 35

Date: 2026-10-03

Primary image:
- `N3D_DOS_v2.0_IDA.EXE`
- complete unpacked DOS V2.0 image

Address convention:
- raw image offsets are authoritative;
- old Ghidra labels are annotations only;
- inline tables are marked separately from executable instructions.

## Result

Pass 35 closes the complete early VGA/palette/blitter band:

`0x15EE .. 0x2019`

Total span:

**2,604 bytes**

Classification inside the span:

- **2,568 bytes executable instructions/stubs**
- **20 bytes inline palette-effect jump table**
- **16 bytes inter-function alignment NOPs**

The band contains:

- **20 substantive graphics/display routines**
- **4 one-byte `RETF` leaf/no-op stubs**
- **10 stale Ghidra function starts removed**

After this pass the raw image is continuously GREEN from:

`0x0000 .. 0x2019`

with TABLE/PADDING overlays where appropriate.

---

# 1. Function census

| Range | Bytes | Correct role |
|---|---:|---|
| `15EE–1606` | 25 | `SwapPlanarDisplayPageImmediate` |
| `1608–1636` | 47 | `SwapPlanarDisplayPageSynchronized` |
| `1638–1688` | 81 | `SetOrRestorePlanarVideoMode` |
| `168A–16AE` | 37 | `UploadFullVgaPalette` |
| `16B0–16CC` | 29 | `SetVgaPaletteEntry` |
| `16CE–17B2` | 229 | `BuildNearestPaletteRemap` |
| `17B4–19A0` | 493 | `RunPaletteTransitionEffect` |
| `19A2` | 1 | no-op far stub |
| `19A4–19B5` | 18 | `WaitForVgaDisplayEnableEdge` |
| `19B6–19BE` | 9 | `WaitForVgaRetraceStart` |
| `19C0` | 1 | no-op far stub |
| `19C2` | 1 | no-op far stub |
| `19C4` | 1 | no-op far stub |
| `19C6–1A2C` | 103 | `FillPlanarRectangleTwoTone` |
| `1A2E–1B3D` | 272 | `BlitScaledPlanarImageRows` |
| `1B3E–1D3C` | 511 | `DrawClippedPlanarSprite` |
| `1D3E–1DEB` | 174 | `BlitPlanarImageBlock` |
| `1DEC–1E33` | 72 | `DrawPlanarPixel` |
| `1E34–1EA5` | 114 | `FillPlanarRectangle` |
| `1EA6–1EDA` | 53 | `FillPlanarRectangleBothPages` |
| `1EDC–1F23` | 72 | `CompositePlanarRectangleDraw` |
| `1F24–1F99` | 118 | `BlitMonochromePlanarBitmap` |
| `1F9A–1FC4` | 43 | `ClearPlanarPage` |
| `1FC6–2019` | 84 | `InitializePlanarMode13DoubleBuffer` |

Alignment NOPs:

```text
1607
1637
1689
16AF
16CD
17B3
19A1
19A3
19BF
19C1
19C3
19C5
1A2D
1D3D
1EDB
1FC5
```

---

# 2. False function starts removed

The following old tracker/Ghidra entries are interior instructions of larger real
routines:

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
```

## `1601`

This is the `MOV DX,03D4h` instruction inside the function beginning at `15EE`.

It is not `ReadVgaStatusPort`.

## `16F5`

Immediately follows the shade-level table setup inside `16CE`.

No new prologue exists.

## `1715`

Interior clamp branch inside `BuildNearestPaletteRemap`.

## `176A`

Interior absolute-distance calculation inside the same palette-remap function.

## `1921`

AND `CALL 168A` instruction inside the palette-effect dispatcher.

It is not and standalone `FadePaletteIn`.

## `1988`

Interior control flow immediately before the dispatcher restores the base palette.

Not and standalone palette-entry setter.

## `19BA`

The `TEST AL,08h` instruction inside the function starting at `19B6`.

## `1AE1`

Interior plane-mask branch of the scaled planar blitter beginning at `1A2E`.

## `1B10`

Interior fixed-point source-advance instruction in `1A2E`.

## `1B71`

Interior instruction in the real sprite blitter beginning at `1B3E`.

The hard-closure address `1B3E` is the correct function start.

---

# 3. `15EE` — immediate page swap

`SwapPlanarDisplayPageImmediate`

The routine swaps the two page-state WORDs:

```text
DS:012C
DS:012E
```

It then programs VGA CRTC register:

`0Ch`

using the newly selected page/start-address value.

There is no vertical-status synchronization in this entry.

**Status: GREEN.**

---

# 4. `1608` — synchronized page swap

`SwapPlanarDisplayPageSynchronized`

Again swaps `012C` and `012E`.

Additional behavior:

1. poll VGA input-status port `3DAh` until display-enable bit 0 is clear;
2. disable interrupts;
3. program CRTC register `0Ch`;
4. enable interrupts;
5. poll `3DAh` until vertical-retrace bit `08h` becomes set.

Thus DOS V2.0 has both an immediate page swap and and status-synchronized page swap.

**Status: GREEN.**

---

# 5. `1638` — set/restore VGA mode

`SetOrRestorePlanarVideoMode(mode)`

Input is one WORD.

## Mode 0 — initialize game VGA mode

1. query current BIOS video mode with:

`INT 10h / AH=0Fh`;

2. save it in:

`DS:3452`;

3. call `InitializePlanarMode13DoubleBuffer`;
4. query BIOS mode again;
5. require mode:

`13h`;

6. on mismatch enter the fatal/error path;
7. rebuild reciprocal projection table through `1560`.

## Mode 1 — restore prior BIOS mode

If saved mode `3452` is nonzero:

`INT 10h / AH=00h`

restores it.

Other mode values are no-ops.

**Status: GREEN.**

---

# 6. VGA DAC primitives

## `168A` — `UploadFullVgaPalette`

This is not and single-color writer.

It writes exactly:

`0x300 = 768`

component bytes through:

```text
3C8h = starting DAC index 0
3C9h = RGB component data
```

Therefore it uploads the entire 256-entry VGA palette.

## `16B0` — `SetVgaPaletteEntry`

Inputs:

- palette index;
- R;
- G;
- B.

Writes the requested index to `3C8h`,
then three component bytes to `3C9h`.

**Status: GREEN.**

---

# 7. `16CE` — nearest-color shade/remap table

`BuildNearestPaletteRemap`

This one function absorbs the stale starts `16F5`, `1715` and `176A`.

The function contains the exact shade-level list:

```text
0
4
8
12
16
20
30
40
```

The selected level is indexed by:

`DS:6278`.

Palette data starts at:

`DS:4A64`.

For every one of 256 source palette entries:

1. subtract the selected shade amount from R/G/B;
2. clamp every component at zero;
3. scan the 256 palette entries;
4. compute distance as:

```text
abs(Rc - Rt) +
abs(Gc - Gt) +
abs(Bc - Bt)
```

5. retain the palette index with minimum distance;
6. write the selected index into the remap table rooted at:

`DS:D20C`.

This is an exact nearest-color remapping algorithm, not and vague palette transform.

**Status: GREEN / deep.**

---

# 8. `17B4` — ten-mode palette-effect dispatcher

`RunPaletteTransitionEffect(mode)`

The function temporarily sets:

`DS:3CD1 = 1`

and restores its prior value before return.

Base/current palette is:

`DS:4A64`.

The mode is dispatched through and **10-WORD jump table** at image:

`17DA..17ED`.

The code segment used by this routine has linear base `0x1560`,
with the table resolves exactly to:

| Mode | Target | Behavior |
|---:|---:|---|
| 0 | `198D` | upload/restore base palette |
| 1 | `17EE` | upload all-black palette immediately |
| 2 | `1808` | fade from black toward base palette |
| 3 | `1872` | fade base palette down toward black |
| 4 | `18BA` | ramp RGB component 0 upward |
| 5 | `18BA` | ramp RGB component 1 upward |
| 6 | `18BA` | ramp RGB component 2 upward |
| 7 | `192C` | flash/maximize RGB component 0 then restore |
| 8 | `192C` | flash/maximize RGB component 1 then restore |
| 9 | `192C` | flash/maximize RGB component 2 then restore |

## Fade-in

Starts with 768 zero bytes.

In steps of `3`, each palette component moves upward until it reaches the base palette.

Each step waits for VGA retrace and uploads the whole 768-byte temporary palette.

## Fade-out

Copies the base palette and performs 21 iterations,
subtracting 3 from every component while clamping at zero.

## Modes 4–6

Select one RGB component offset and run up to 63 retrace-synchronized steps,
incrementing the selected component for all 256 palette entries until it reaches `3Fh`.

## Modes 7–9

Select one RGB component,
set that component to `3Fh` in all 256 entries,
upload once,
wait for retrace,
then restore the base palette.

This closes the full DOS palette-effect machine.

**Status: GREEN.**

### Inline table overlay

`17DA–17ED` is **20 bytes of TABLE data inside the function span**.

It must not be disassembled as instructions.

---

# 9. VGA timing helpers

## `19A2`

One-byte:

`RETF`

No-op far stub.

## `19A4` — `WaitForVgaDisplayEnableEdge`

Polls `3DAh`.

First waits until:

`(status & 09h) != 1`

then waits until:

`(status & 09h) == 1`.

This synchronizes to and display-status edge.

## `19B6` — `WaitForVgaRetraceStart`

Polls `3DAh` until:

`status & 08h != 0`.

## `19C0`, `19C2`, `19C4`

Three one-byte `RETF` stubs separated by NOP alignment bytes.

No direct near-call xrefs were found in the checked load image; retain them as known
leaf/no-op code rather than UNKNOWN functions.

**Status: GREEN.**

---

# 10. `19C6` — two-tone planar rectangle fill

`FillPlanarRectangleTwoTone`

Uses planar VGA pitch:

`0x50 = 80 bytes`.

All four planes are enabled.

The requested vertical region is split into two equal halves.

Upper half is filled with:

`DS:627B`.

Lower half is filled with:

`DS:627A`.

This is and direct planar framebuffer background/fill primitive.

**Status: GREEN.**

---

# 11. `1A2E` — scaled planar image-row blitter

`BlitScaledPlanarImageRows`

This one real function absorbs the stale starts:

`1AE1` and `1B10`.

It:

- clips against viewport/display globals around `4546/454C/454E/4552`;
- computes destination planar address as:

`y*0x50 + x/4`;

- rotates VGA plane mask according to X alignment;
- uses the reciprocal/projection tables from the `1560/1590` family;
- advances source through fixed-point integer/fractional stepping;
- optionally maps source pixels through table:

`DS:D20C`;

- writes vertically through the planar 80-byte pitch.

The function returns and small plane/coverage-style count used by callers.

**Status: GREEN.**

---

# 12. `1B3E` — clipped planar sprite renderer

`DrawClippedPlanarSprite`

The correct function entry is `1B3E`, not old `1B71`.

This is the high-value sprite/output blitter.

Static behavior includes:

- obtains image/frame dimensions and source pointer from the render/sprite structures;
- clips horizontally and vertically against the current viewport;
- computes fixed-point horizontal/vertical source stepping;
- programs VGA sequencer plane masks while stepping screen X;
- uses planar destination pitch `0x50`;
- treats source palette byte:

`0x1F`

as transparent;
- consults the per-column wall/visibility buffer at the renderer visibility area;
- the object/render flag `0x10` provides the already recovered wall-comparison bypass;
- does not write and new wall-depth value into the visibility buffer.

This is the DOS planar counterpart of the sprite transparency/occlusion path used by
the renderer.

**Status: GREEN / deep static semantics.**

---

# 13. `1D3E` — planar rectangular image block

`BlitPlanarImageBlock`

Inputs include:
- source far pointer;
- X/Y;
- source row stride;
- width/height;
- page selector;
- transparency value.

The routine rotates through VGA plane masks and copies columns down the 80-byte planar
pitch.

Transparency behavior:

- negative transparency parameter -> copy every source byte;
- nonnegative parameter -> skip source bytes equal to that value.

**Status: GREEN.**

---

# 14. Basic planar drawing primitives

## `1DEC` — `DrawPlanarPixel`

Rejects Y >= 200.

Selects the requested VGA page,
computes:

`y*80 + x/4`

selects the plane from `x&3`,
and writes one color byte.

## `1E34` — `FillPlanarRectangle`

Rejects zero width/height.

Computes planar start address and fills the requested rectangular region with one color,
rotating plane masks as X crosses planar groups.

## `1EA6` — `FillPlanarRectangleBothPages`

Thin composite wrapper calling `FillPlanarRectangle` once for each of the two display
pages.

## `1EDC` — `CompositePlanarRectangleDraw`

Combines and small helper-derived color/value with two `FillPlanarRectangle` calls to
draw nested/offset planar rectangles.

Its machine behavior is fully bounded even though the original UI-level design name is
not encoded in the function.

**Status: GREEN.**

---

# 15. `1F24` — monochrome/bit-mask planar bitmap blit

`BlitMonochromePlanarBitmap`

Uses:
- far source bitmap pointer;
- destination X/Y;
- color byte;
- selected display page.

It reads compact source row/width information,
then interprets source mask bytes as VGA plane masks.

For each set plane group it writes the supplied solid color into the corresponding
planar destination bytes.

This is and 1-bit/plane-mask style bitmap primitive, not and CRTC display-start setter.

**Status: GREEN.**

---

# 16. `1F9A` — clear one complete planar page

`ClearPlanarPage`

The function:

1. enables all four VGA planes with sequencer value:

`0F02h`;

2. selects page segment from `012C/012E`;
3. duplicates the caller color into AX;
4. executes:

`REP STOSW`

for:

`0x1F40 = 8000 words`.

That fills:

`16,000 bytes per plane`

which across four planes represents the complete:

`320 × 200 = 64,000 pixel`

page.

The old `ProgramCrtcRegister` label is incorrect.

**Status: GREEN.**

---

# 17. `1FC6` — planar Mode 13h / double-buffer initialization

`InitializePlanarMode13DoubleBuffer`

Sequence:

1. BIOS:

`INT 10h / AX=0013h`;

2. reprogram sequencer memory-mode register `04h`;
3. reprogram graphics-controller mode register `05h`;
4. reprogram graphics-controller miscellaneous register `06h`;
5. clear both page buffers through `ClearPlanarPage`;
6. modify CRTC registers:
   - `14h`;
   - `17h`.

This converts ordinary BIOS Mode 13h into the unchained planar layout used by the DOS
renderer and prepares both display pages.

The function ends at:

`0x2019`.

**Status: GREEN.**

---

# 18. Byte-map impact

Resolved continuous early graphics band:

`0x15EE .. 0x2019`

Total:

**2,604 bytes**

Breakdown:

- executable instructions/stubs: **2,568 bytes**
- inline jump table: **20 bytes**
- alignment NOPs: **16 bytes**

### Delete stale starts

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
```

### Correct high-value entries

```text
16CE  BuildNearestPaletteRemap
17B4  RunPaletteTransitionEffect
1A2E  BlitScaledPlanarImageRows
1B3E  DrawClippedPlanarSprite
1D3E  BlitPlanarImageBlock
1F9A  ClearPlanarPage
1FC6  InitializePlanarMode13DoubleBuffer
```

---

# 19. Continuous closure status

Pass 34 closed:

`0000..15ED`

Pass 35 closes:

`15EE..2019`

Therefore the early image is now continuously statically closed from:

**`0x0000 .. 0x2019`**

without any RED/ORANGE function-boundary gaps.

As with Pass 34, not all 2,604 bytes are counted as newly promoted bytes because many
were already medium/high confidence in the old tracker.

The improvement is:
- exact raw boundaries;
- stale weak entries eliminated;
- palette-effect state machine fully decoded;
- planar Mode-13 double-buffer setup bounded;
- high-value sprite/blitter starts corrected.

---

# 20. Next target

Continue at:

`0x201A`

The next band begins the renderer'with 18-byte screen/visible-record pool and visibility
preparation helpers.

Initial raw entries include:

- `201A` — mark all 18-byte slots inactive;
- `202A` — interpolation/slope setup for one visible span/record;
- `213E` and `21F0` — visibility/list culling/update helpers;
- later weak boundaries around the old `2500` family.

The next pass should continue the same process:
1. recover raw boundaries;
2. remove stale split entries;
3. bind fields to the already-known 18-byte visible/render records;
4. close the renderer visibility list band before moving into resource/file code.