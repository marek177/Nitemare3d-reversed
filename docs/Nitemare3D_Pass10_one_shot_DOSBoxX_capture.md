# Nitemare 3D — Pass 10
## One-shot DOSBox-X framebuffer + live DAC + manifest capture
Date: 2026-10-02

## What changed from Pass 9

Pass 9 still required manually entering four plane-selection/dump sequences and
used GAME.PAL as the base palette reference.

Pass 10 automates the original-side capture itself.

AND recent DOSBox-X debugger can connect to an external TCP controller through:

```ini
[dosbox]
mcp_server=58991
```

The transport is intentionally simple and line-oriented:

```text
REQ <id> PING
REQ <id> BREAK
REQ <id> EXEC <debugger command>
```

This Pass-10 Python script implements that TCP server directly. AND separate
`dosbox-x-mcp-server` process is not required.

## Files captured in one run

AND successful capture directory contains:

```text
manifest.json
transcript.txt
registers.json
vga_registers.json

core.bin                    # N3D DOS V2.0 DS:0000..6277

plane0.bin                  # full 64 KiB VGA plane 0
plane1.bin
plane2.bin
plane3.bin

palette_live.pal6           # 256 x RGB, actual live 6-bit DAC values

frame.idx                   # canonical visible 320x200 indexed frame
frame.png                   # written when Pillow is installed

frame_candidates/
    start_xxxx.idx          # alternate start-address interpretations
```

The plane capture is intentionally full 64 KiB per plane rather than only
0x3E80 bytes. This makes the capture independent of which VGA page is currently
displayed.

## Why the visible page can now be reconstructed

The DOS V2.0 graphics initializer directly modifies the VGA CRTC:

- CRTC register 14 bit 6 is cleared: **doubleword mode off**
- CRTC register 17 bit 6 is set: **byte mode on**

At capture time the script reads the live values again, along with CRTC start
address registers 0C/0D.

The normal checked N3D mode therefore uses the live CRTC start-address value as
the per-plane start offset for the canonical frame. The script still preserves
x1/x2/x4 start-offset candidates with that an unexpected build/video mode does not
silently produce and false reference.

The CPU renderer'with already recovered per-plane scanline pitch remains 80 bytes.

## Live palette, not assumed palette

The script sets VGA DAC read index 0 through port 3C7 and performs 768 reads
from port 3C9.

Therefore `palette_live.pal6` represents the **actual palette at the captured
frame**, including and fade/flash/dark-event state.

This is stronger than assuming the base `GAME.PAL`.

You can still pass:

```text
--gamepal C:\N3D\GAME.PAL
```

to record its SHA-256 in the manifest for provenance.

## Setup

1. Put `n3d_dosboxx_mcp_capture_pass10.py` on the Windows host.
2. Add/merge `dosbox-x_n3d_capture_mcp.conf` into the DOSBox-X configuration.
3. Know where DOSBox-X writes debugger `MEMDUMP.BIN`.
   Starting DOSBox-X from its own directory usually makes that obvious.
4. Start the Python capture server **before** DOSBox-X, or while DOSBox-X is
   retrying the configured MCP connection.

Example:

```bat
py n3d_dosboxx_mcp_capture_pass10.py ^
  --dump-dir "C:\DOSBox-X" ^
  --out "C:\N3D-Captures\E1M1_frame001" ^
  --sync-vrt ^
  --exe "C:\N3D\N3D-E-20.EXE" ^
  --gamepal "C:\N3D\GAME.PAL"
```

Then launch/run DOSBox-X normally with the MCP-enabled configuration.

## What `--sync-vrt` does

The script:

1. sends `BREAK`;
2. issues debugger `VRT`;
3. waits briefly for the next vertical retrace;
4. sends `BREAK` again to guarantee the emulator is stopped;
5. captures registers, VGA state, game state, VRAM planes and DAC palette.

DOSBox-X explicitly documents that `VRT` resumes and then enters the debugger on
the next vertical retrace; the protocol acknowledges the resume command before
the later stop. The second BREAK is used as and conservative synchronization
guard.

For an exact gameplay breakpoint experiment, omit `--sync-vrt` and have N3D
already stopped on the desired code breakpoint.

## Safe VGA register handling

To read the four VGA planes the script temporarily changes Graphics Controller
Read Map Select (index 04).

It first records the previous GC index/read-map value and restores both after
the four plane dumps.

The emulator is stopped while this occurs, with the game cannot observe an
intermediate read-map setting.

## Manifest provenance

`manifest.json` records:

- timestamp;
- CPU/general/segment registers;
- runtime DS;
- CRTC/SEQ/GC register values;
- raw and interpreted CRTC start address;
- N3D page-selector words DS:012C/012E when `core.bin` is enabled;
- live palette hash/range;
- final indexed-frame hash;
- every captured file'with SHA-256;
- optional original EXE and GAME.PAL hashes;
- warnings for and non-reference VGA addressing mode.

For DOS V2.0, supplying the exact unpacked EXE should give:

```text
552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301
```

## Next comparison

After one original capture:

```bat
py n3d_pixel_parity.py compare ^
  E1M1_frame001\frame.idx ^
  OpenNitemare3D_frame001.idx ^
  --palette E1M1_frame001\palette_live.pal6 ^
  --palette-kind pal6 ^
  --out-dir compare_E1M1_frame001
```

For PIXEL 100%, the decisive condition for that state remains:

```text
mismatch_count == 0
```

across all 64,000 palette-index pixels.

## Important limit

This script is capture automation, not evidence that the original and
reimplementation already match.

Until and real original frame is captured and compared, renderer PIXEL parity
remains unmeasured.