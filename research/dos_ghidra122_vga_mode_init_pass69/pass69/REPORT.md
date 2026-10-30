# Pass 69 — planar VGA mode initialization

## Finding
Confirmed across six distinct supplied DOS binaries: initialization invokes BIOS mode13h, changes sequencer/graphics-controller addressing bits, clears both existing page segments, and changes two CRTC addressing bits. Its local register programming is now connected to the glyph and page-flip routines from passes67/68. Complete BIOS/VGA state, display scanout and DAC parity remain open. Supplied1.8/1.9 are identical.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | BIOS request AX=0013, INT10 | Original code and interrupt trace | High |
| Confirmed | Five read-modify-write register operations below | Exact IN/OUT traces for varied inputs | High |
| Confirmed | Both pages are cleared using original clear routine | CPU memory comparison across whole32KiB window | High for CPU stores |
| Confirmed | Neither CRTC0c nor0d is written here | Complete routine and callees' port trace | High for this call path |
| Inferred | Planar byte-addressed graphics setup supports prior renderer model | Sequencer/GC/CRTC bit changes and prior raster behavior | High local chain; actual post-BIOS state missing |
| Unknown | BIOS-established lower display address and complete VGA state | BIOS implementation mocked | Requires original BIOS/VGA runtime |

## Register transformations
| Register | Result from read byte v |
|---|---|
| Sequencer4 | (v & f7h) OR04h |
| Graphics controller5 | v AND efh |
| Graphics controller6 | v AND fdh |
| CRTC14h | v AND bfh |
| CRTC17h | v OR40h |

All other bits are retained from IN values. The code does not assign a complete register set. Between GC changes and CRTC changes, it calls clear(color0, page1) followed by clear(color0, page0). Each clear emits OUT word0f02h to3c4 (sequencer map mask0f), selects its segment, sets DF=0 and executes REP STOSW for8000 words. Initial supplied page globals are a000/a400 as previously established; these calls write physical CPU ranges a0000..a3e7f and a4000..a7e7f, preserving the384-byte gaps. Under a compatible VGA planar write mode/map mask, stores reach all four planes; that hardware precondition is not implemented by the flat-memory test.

The initializer does not swap or reset page globals. It neither writes CRTC0c nor0d: the lower display-start byte cannot be inferred from this routine alone. It returns DF=0 even when entered with DF=1, because of the clear routine's CLD; incoming IF is preserved by the tested original instructions (the BIOS boundary does nothing in the harness). This is not a claim about BIOS interrupt-flag side effects on real hardware.

## Locations
DOS1.0/1.1/1.2:1155:0a68. DOS1.5/1.7/supplied1.8/1.9:1156:0a66. Original clear entries and instructions are in clear_routines.json; fresh Ghidra12.2 exports include initializer bytes and C for each build. Decompiler C omits some arguments; raw pushes prove page1/page0.

## Verification
96 cases pass: six binaries × eight distinct sets of five IN bytes × incoming IF0/1. All cases enter with DF1. Original initializer and original page clear code execute. Assertions check the complete BIOS/port sequence, transformed values, both cleared ranges, untouched gaps, DS restoration and final DF/IF. BIOS INT10 is observed as AX0013 and modeled as a no-op; five VGA register reads are supplied. No VGA device, latch model, BIOS register defaults, palette or visible pixels are claimed.

## Unknowns and next test
Capture complete post-BIOS sequencer/graphics-controller/CRTC state in DOSBox-X, especially CRTC0d and addressing modes; then run original glyph drawing and page flips against real UIF assets and compare plane memory plus DAC output. Global graphics setup/callers may add configuration and remain to be traced. Overall confidence High for local instruction/I/O semantics and memory ranges, incomplete for integrated framebuffer parity.
