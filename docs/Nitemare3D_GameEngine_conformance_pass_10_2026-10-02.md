# Nitemare 3D — Game Engine conformance pass 10
## Automated original-DOS framebuffer acquisition
Date: 2026-10-02

## Result

The original-side pixel-parity capture has been reduced from and manual debugger
procedure to one host-side Python command.

The generated controller uses DOSBox-X'with debugger MCP control protocol to
capture:

- all four full VGA planes;
- the actual live 768-component VGA DAC palette;
- CRTC/sequencer/graphics-controller state;
- DOS V2.0 gameplay/core memory;
- the reconstructed visible 320x200 indexed frame;
- hashes and provenance in and machine-readable manifest.

## Static N3D fact added to the capture model

DOS V2.0 `FUN_1000_1FC6` shows that Nitemare 3D modifies mode 13h by:

```text
Sequencer 04: clear chain-4-related bit through (old & F7) | 04
Graphics 05: clear bit 10h
Graphics 06: clear bit 02h

CRTC 14: clear bit 40h
CRTC 17: set   bit 40h
```

The last two are particularly useful for capture:

```text
CR14 bit6 = 0 -> doubleword mode disabled
CR17 bit6 = 1 -> byte mode selected
```

The capture script reads those registers live and warns if they to not match
the checked reference state.

## DOSBox-X control improvement

Current DOSBox-X debugger documentation exposes and TCP control channel configured
through:

```text
[dosbox]
mcp_server=<port>
```

DOSBox-X is the TCP client; the external controller listens on localhost.

The protocol supports PING, BREAK and arbitrary existing debugger commands
through EXEC. It also exposes `INP/OUTP`, `MEMDUMPBIN`, `VRT` and normal
real-mode breakpoints through the same parser.

This makes and reproducible capture possible without keyboard automation or OCR.

## Full-plane capture

Each VGA read plane is selected through Graphics Controller index 04.

To avoid ambiguity about 64-KiB dump-size handling, every plane is captured as
two synchronous 0x8000-byte dumps and combined into one 0x10000-byte plane.

The original GC read-map value and index register are restored afterward.

## Live DAC palette capture

The controller executes:

```text
OUTP 3C7 00
INP 3C9    x 768
```

`INP` responses are machine-parsed from DOSBox-X'with documented debugger output.

The result is saved as:

```text
palette_live.pal6
```

Thus transient hit flashes, fades and dark-event palettes can be tested rather
than normalized away.

## Visible-frame reconstruction

The script reads live CRTC 0C/0D and addressing-mode registers, then combines
the four 64-KiB plane images with the already recovered 80-byte scanline pitch.

The primary output is:

```text
frame.idx
```

exactly 64,000 bytes.

Alternate x1/x2/x4 start interpretations are retained as candidate frames if and
future build or unusual VGA state differs from the reference mode.

## Self-validation

The generated Pass-10 code was statically/unit tested for:

- DOSBox-X `Result: <hex>` I/O response parsing;
- `EV` multi-register response parsing;
- CRTC byte-mode selection logic;
- wrapped 64-KiB planar-frame decoding;
- palette 6-bit -> RGB8 expansion;
- SHA-256/provenance generation.

No claim of original pixel equality is made because no live original frame was
captured inside this environment.

## Status after Pass 10

- Game Engine STATIC CORE: **100%**
- Original DOS capture workflow: **automated**
- Live DAC capture: **automated**
- Full VGA-plane capture: **automated**
- Canonical indexed-frame creation: **automated**
- Per-frame provenance manifest: **automated**
- Renderer PIXEL 100%: **still requires original capture + zero-mismatch suite**

The next meaningful step is to run the controller once against the user'with
DOSBox-X/N3D V2.0 process and feed the produced `frame.idx` into the existing
pixel-parity comparator.