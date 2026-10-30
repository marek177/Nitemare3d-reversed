# Pass 62 — UIF screen decoder, DOS versions

Confirmed from fresh Ghidra 12.2 exports and execution of original relocated MZ instructions. The function previously labelled `resource_reload` is a UI image decoder, not a resource-table restoration routine. The surrounding `load_a` wraps screen operations; `load_b` draws loading progress UI.

## Locations

| Build | Decoder |
|---|---|
| 1.0 | 1273:15a0 |
| 1.1 | 1275:15c6 |
| 1.2 | 1275:15d8 |
| 1.5 | 1277:1600 |
| 1.7 | 1277:1678 |
| supplied 1.8 / 1.9 | 1277:17dc |

The supplied 1.8 and 1.9 executables are identical; six distinct binaries are tested. Input hashes and exact call sites are recorded in `evidence/uif_decoder_tests.json`.

## Confirmed behavior

The decoder looks up image metadata, returns AL=0 if its first word is zero, opens `uif.dat` in `rb` mode, and seeks to the dword at metadata+2. It reads a 128-byte PCX-like header. Manufacturer must be 0x0a. Its dimension rejection uses **AND**: it rejects only when BOTH ymax−ymin differs from 199 AND xmax−xmin differs from 319. One correct dimension is sufficient. Decoding still emits fixed 320×200 pixels. Header encoding, bit depth, plane count and bytes per line are not checked in this function; a deliberately inconsistent fixture was accepted.

A byte with upper bits 11 consumes a second value byte and repeats it byte&0x3f times. Other bytes are literals. A 0xc0 prefix consumes a value but emits zero pixels. Runs can cross row boundaries. Each completed 320-byte row goes to the blitter, with y increasing from 0 through 199. After the packet completing the final row, the file is closed and AL=1. AX as a whole is not a boolean ABI. Read return values are ignored at the observed call sites; malformed/truncated input behavior has not been executed here.

## Verification and limits

`python scripts/verify_uif_decoder.py` executes original decoder instructions in Unicorn with synthetic metadata and streams. Ten cases per binary: missing metadata; constant RLE; literal pattern; mixed RLE; zero-length run; bad manufacturer; only width wrong; only height wrong; both dimensions wrong; inconsistent other header fields. Every emitted row is compared byte-for-byte with an independent 64,000-byte expected image, and blit arguments, file mode, offset and error branch are asserted. Results are 60 passing cases.

Mocked boundaries: metadata lookup, CRT open/seek/read/close, fatal handler and blitter. No actual UIF asset, VGA output, palette behavior, complete startup or full-game behavior is proven. Metadata fixture uses DS=SS as in this harness. The original decoder executes unchanged, including its loops and conditional branches. Ghidra C parameter inference is evidence assistance rather than an authoritative prototype.

## Remaining frontier

Resource-table offset restoration remains unresolved: these transition calls belong to loading-screen presentation. Follow actual metadata construction and resource activation separately. Rendering output, resident audio driver behavior and overall 1:1 game parity remain open; these tests do not establish complete semantic coverage.
