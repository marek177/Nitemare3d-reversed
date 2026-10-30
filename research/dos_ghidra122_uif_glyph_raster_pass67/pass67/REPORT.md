# Pass 67 — UIF glyph rasterizer

## Finding
Confirmed in six distinct supplied DOS binaries: glyph drawing writes an 8-bit color through VGA sequencer map masks into a planar destination. Original instruction execution matches an independent four-plane memory model for normal and boundary fixtures. This is local raster evidence, not a full VGA/DOSBox framebuffer parity result. Supplied 1.8 and 1.9 are identical binaries.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Fourth argument selects destination segment: zero vs any nonzero | Glyph assembly and page 0/1/2 fixtures | High |
| Confirmed | Header byte 0 is height; byte 1 determines row bytes | Original loops and independent pixel comparison | High |
| Confirmed | Source bitmap is consumed least-significant bit first | Planar output comparison | High |
| Confirmed | One bits write color; zero bits preserve destination planes | OUT mask/write traces and plane comparison | High within stated VGA mask model |
| Confirmed | Low color byte is used; high byte ignored | Input 0xffa7 stores 0xa7 | High |
| Confirmed | y is truncated to low 8 bits; x is unsigned16 | MUL BL and SHR AX instructions, boundary fixtures | High |
| Confirmed | No local screen clipping or padding-bit masking | x319/y199 width9 and boundary fixture outputs | High for this function |
| Unknown | Full game VGA configuration, latch behavior and displayed pixels | Hardware registers outside this routine not emulated | Requires integrated VGA test |

## Behavior model
Destination base is wrap16((y&255)*80 + (x>>2)). If draw argument4 is zero, select page_zero segment; otherwise page_nonzero segment. The function selects sequencer register 2 on port 0x3c4 and writes map masks on 0x3c5. Each source byte is rotated in a 16-bit register by x&3 and emitted as three successive mask/write pairs; the third store can overlap the first store of the next source byte. All memory stores occur, even when the low four mask bits are zero. Row destination advances by 80 bytes. Four plane bytes represent four neighboring pixels.

For valid nonzero row-byte count, the equivalent local pixel model is: for every bit set in each row's source bytes, write color_low8 at pixel x+j*8+bit, with bit 0 drawn first. All bits of the last byte are consumed, including padding beyond the nominal width. This complements the bank-loader bit reversal proven in pass65: file-byte bit order is reversed before drawing.

The row-byte calculation is `(((u8)(width+7))>>3)`, not an unbounded ceil(width/8). A zero result enters a decrement-controlled loop and consumes 256 bytes per row. Thus width0 and width249..255 consume 256 bytes per row. Height0 similarly runs 256 rows. These are synthetic boundary observations, not evidence that shipped fonts contain such dimensions. A safe modern asset reader may reject such data, but an exact original-function model must distinguish that validation from original arithmetic.

The function restores DS, SI, DI and BP via its stack epilogue. It does not restore the sequencer map mask or selected index. No meaningful return-value contract is inferred.

## Verification
162 cases pass: 27 per binary, covering all x alignments and both page choices; widths0,1,7,8,16,248,249,255; nonzero page2; zero height; right/bottom screen crossing; and x65535/y0x101. Every original destination store is checked for value/size, every OUT port/size is checked, and all 262,144 modeled plane bytes are compared with an independent bit-to-pixel implementation. Exact store counts and port counts are asserted. Original routine instructions execute unchanged, with original MZ relocations. There are no mocked calls inside the routine.

VGA OUT and destination writes are observed into a model using sequencer index2's low four map-mask bits; the CPU memory remains flat Unicorn memory. Synthetic destination segments a000/b000, glyph data and DS page globals are supplied. Other VGA registers and display scanout are not modeled. No real asset screenshots or full-game rendering are claimed.

## Locations
Exact per-build entries, destination-global offsets, original EXE hashes and output plane hashes are in glyph_raster_tests.json. Ghidra12.2 C and complete instructions are included for all six routines; C rotation expressions and prototypes are not treated as authoritative over instructions. DOS1.9 routine: 1156:09c4 through 1156:0a39.

## Unknowns and next test
Connect the page-segment globals to VGA setup and integrated text rendering; compare actual UIF glyphs and framebuffer/DAC output under the original VGA configuration. Global clipping may occur in callers and has not been excluded. Full renderer parity and asset character mapping remain open. Confidence High for local instruction semantics and modeled plane writes; incomplete for complete hardware rendering.
