# Nitemare 3D — Pixel-perfect framebuffer parity kit
Date: 2026-10-02

## Goal

This kit converts the final renderer validation task into a deterministic
byte/pixel comparison instead of screenshot eyeballing.

The checked renderer facts are:

- output is 320×200 indexed color;
- the 3-D viewport is 304×152 at x=8..311, y=4..155;
- DOS planar VGA uses 80 bytes per scanline per plane;
- Win16 WinG uses one byte per pixel with a 320-byte scanline;
- DOS sprite transparency key is 0x1F in the checked V2.0 path;
- Win16 sprite transparency key is 0x29 in the checked 1.10 path.

A zero-mismatch indexed comparison is stronger than an RGB screenshot match:
two different palette indices can produce similar colors, but they are not the
same original renderer output.

## 1. DOS VGA capture

The game maintains two VGA page selectors around DS:012C/012E and swaps them in
the present routine. The planar pixel writers use the selected page, 80-byte
scanline pitch and VGA map masks.

For the first run, capture both page candidates if there is any doubt about
which one is currently visible.

In DOSBox-X debugger:

1. Break immediately after a present/VBL point or use `VRT`.
2. Inspect the two words at gameplay `DS:012C`.
3. For a chosen page segment, select each VGA read plane through Graphics
   Controller register 4 and dump 0x3E80 bytes.

Commands for plane 0:

    OUTP 3CE 04
    OUTP 3CF 00
    MEMDUMPBIN <PAGESEG> 0000 3E80

Repeat with read-map values 01, 02 and 03, renaming each `MEMDUMP.BIN` before
the next dump.

`n3d_dosboxx_vga_capture_commands.py` prints the complete command sequence.

Example:

    py n3d_dosboxx_vga_capture_commands.py --page-seg A000

The debugger supports `INP/OUTP`, `MEMDUMPBIN` and `VRT`; use `HELP` to confirm
the commands in the installed DOSBox-X build.

## 2. Decode DOS planes to a canonical frame

    py n3d_pixel_parity.py decode-planar ^
        --plane0 plane0.bin ^
        --plane1 plane1.bin ^
        --plane2 plane2.bin ^
        --plane3 plane3.bin ^
        --output-index original.idx ^
        --output-png original.png ^
        --palette GAME.PAL --palette-kind gamepal

The canonical `original.idx` is exactly:

    320 * 200 = 64,000 bytes

in normal row-major order:

    pixel[y*320+x]

The planar conversion is:

    plane = x & 3
    offset = y*80 + (x >> 2)

If a capture contains a full 64-KiB VGA plane rather than a page-relative
0x3E80 dump, pass `--offset 0x...`.

## 3. Palette

For the supplied DOS family, the original palette loader:

1. seeks to 768 bytes before EOF in `GAME.PAL`;
2. reads 768 bytes;
3. stores each component after `>>2`;
4. uploads all 256 RGB triples to VGA DAC ports 3C8/3C9.

Extract the exact base 6-bit palette with:

    py n3d_pixel_parity.py extract-palette GAME.PAL game_dos.pal6

During ordinary non-fade/non-flash scenes, this gives the exact base DAC data
loaded by the game.

For palette fades, hit flashes or another transient palette state, a live DAC
capture is still preferable. DOSBox-X's video debug overlay `RPAL` exposes the
hardware palette state; a later automation pass can capture those 768 DAC
components directly through ports 3C7/3C9 if required.

## 4. OpenNitemare3D reference output

Add a debug-only renderer hook that writes the final 320×200 **palette-index**
surface before conversion to RGBA/SDL texture:

    frame.idx  = 64,000 raw index bytes

Do not compare a scaled window screenshot if the indexed buffer is available.
Do not apply bilinear filtering, interpolation or color management.

Also record:

- EXE/data hashes used by the original;
- episode/level;
- player world X/Y and angle;
- current door states/timers;
- object/guard runtime state if relevant;
- render width/shade setting;
- frame/tick number.

## 5. Exact compare

    py n3d_pixel_parity.py compare original.idx open_n3d.idx ^
        --palette GAME.PAL --palette-kind gamepal ^
        --out-dir compare_frame_001

Outputs:

    summary.json
    mismatch_mask.png
    viewport_mismatch_mask.png
    outside_viewport_mismatch_mask.png
    index_difference.png
    rgb_difference.png             (when palette/RGB is available)
    overlay_50_50.png              (when palette/RGB is available)
    row_mismatches.csv
    column_mismatches.csv

The report includes:

- exact frame hashes;
- mismatched pixel count and percentage;
- first mismatch coordinate/index pair;
- mismatch bounding box;
- mismatch counts split into viewport/HUD/margins;
- most common index substitutions;
- optional RGB error metrics.

## 6. Interpretation ladder

### A. Geometry mismatch
Typical shape:
- broad vertical edges in mismatch mask;
- long runs in column_mismatches.csv;
- same general texture colors but shifted boundaries.

Investigate projection, clipping, owner/tie rules or door geometry.

### B. Texture-U/V mismatch
Typical shape:
- wall silhouette aligns;
- mismatches occur mainly inside wall spans;
- repeated index substitutions/striping.

Investigate U correction, 16.16 V sampling and clipping-start tables.

### C. Shade/palette mismatch
Typical shape:
- geometry and texture pattern align;
- large regions differ by repeatable palette substitutions.

Compare shade index/remap table and active DAC palette separately.

### D. Sprite transparency/occlusion mismatch
Typical shape:
- mismatches localized around sprites;
- wall background beneath transparent pixels differs;
- specific vertical sprite columns are missing/extra.

Check DOS key 0x1F, wall visibility 0x47E4, VEC flag 0x10 and slot order.

### E. HUD-only mismatch
If `viewport_mismatch_mask.png` is empty while
`outside_viewport_mismatch_mask.png` is not, the 3-D renderer can be treated
separately from HUD/UI composition.

## 7. Acceptance matrix

Use at least these deterministic cases:

1. empty corridor / cardinal direction;
2. all four camera orientations;
3. near-plane wall;
4. exact left/right viewport boundary;
5. equal/tie wall-owner case;
6. ordinary closed door;
7. several intermediate door positions;
8. fully open door;
9. sprite fully visible;
10. sprite wall-occluded;
11. transparent sprite edge;
12. VEC flag-0x10 bypass case;
13. overlapping sprites / slot-order tie;
14. every active shade level;
15. animated wall/object frame boundaries;
16. floor/ceiling and HUD-only reference frame.

For every case preserve the raw `.idx`, palette state, state manifest and hashes.

## 8. Definition of PIXEL 100%

For a specific build/data/state combination:

    original indexed frame == reconstructed indexed frame

means all 64,000 palette indices match byte-for-byte.

RGB equality alone is useful diagnostics but is weaker than indexed equality.

Renderer **PIXEL 100%** should only be marked after the required acceptance
cases pass on the original binaries, not merely because the comparison tool
itself passes synthetic tests.