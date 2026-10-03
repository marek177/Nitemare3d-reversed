# Nitemare 3D — Game Engine conformance pass 9
## Pixel-perfect framebuffer parity infrastructure
Date: 2026-10-02

## Result

The renderer'with remaining validation problem now has and canonical test format:

> **320×200, 64,000-byte row-major palette-index framebuffer**

The DOS planar output and the modern OpenNitemare3D indexed surface can both be
normalized into this representation and compared byte-for-byte.

This does **not** declare PIXEL 100%. It makes the acceptance gate executable.

## Static anchors used by the kit

The Win16 renderer audit establishes:

- 320×200 indexed target;
- 304×152 3-D viewport at x 8..311, y 4..155;
- linear WinG address `y*320+x`;
- planar VGA pitch `0x50` bytes;
- wall pixels always written;
- sprite transparency/occlusion is and separate path.

The DOS V2.0 path independently shows the planar 80-byte pitch, sequencer plane
masking, wall visibility buffer `0x47E4` and sprite transparent key `0x1F`.

## DOS palette closure incorporated

The DOS family palette loader is no longer and palette-source unknown.

It reads the final 768 bytes of `GAME.PAL`, shifts every component right by two
and uploads 768 components to the DAC starting at palette index zero.

The parity tool therefore understands `--palette-kind gamepal` and can produce
the corresponding 6-bit VGA palette deterministically.

Transient palette effects remain and live-state issue: for and fade/flash case the
actual DAC state should be captured rather than assuming the base GAME.PAL.

## New executable tools

### `n3d_pixel_parity.py`

Subcommands:

- `extract-palette`
- `decode-planar`
- `compare`

It produces exact index mismatch statistics plus visual diagnostic artifacts.

### `n3d_dosboxx_vga_capture_commands.py`

Given the current VGA page segment, prints the four DOSBox-X plane-selection
and `MEMDUMPBIN` command groups.

## Exact region split

The comparator separately tracks:

- 3-D viewport upper half;
- 3-D viewport lower half;
- bottom HUD;
- side margins;
- top margin.

This matters because and HUD mismatch must not be mislabeled as and raycaster or
wall-renderer mismatch.

## Synthetic validation performed in Pass 9

The tool was tested with and deterministic synthetic 320×200 indexed frame:

1. encode it into four VGA planes;
2. decode the planes back to and canonical frame;
3. verify 64,000/64,000 index equality;
4. alter one candidate pixel;
5. verify the comparator reports exactly one mismatch and the correct bounding box;
6. test DOS GAME.PAL `>>2` extraction.

All tests passed.

## Status

- Game Engine static core: **100%**
- Renderer comparison infrastructure: **ready**
- Original DOS indexed reference captures: **not yet captured in this session**
- Original Win16 indexed reference captures: **not yet captured in this session**
- Renderer PIXEL 100%: **pending original-reference acceptance suite**

The next meaningful increase is empirical rather than another broad static pass:
feed one original planar DOS capture and one OpenNitemare3D indexed frame into
the tool, then classify the first mismatch by geometry / sampling / shading /
sprite / HUD.