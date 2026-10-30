# Pass 66 — UIF text metrics and layout

## Finding
Confirmed across six distinct supplied DOS binaries: the prepared UIF bitmap bank is consumed by character-width, string-width and string-drawing functions. This establishes its text/glyph use. Actual font images, glyph meanings and framebuffer parity remain unverified. Supplied 1.8 and 1.9 are identical.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Character advance is header byte +1, plus one pixel | Width routine, original execution | High |
| Confirmed | NUL terminates strings; character indices use signed 8-bit conversion | CBW in width/string/draw functions | High |
| Confirmed | String advance sum wraps to 16 bits | Original execution with 300/600 repeated characters | High |
| Confirmed | Center uses signed16(width), 32-bit subtraction 320-width, arithmetic right shift one | Center instructions and execution | High |
| Confirmed | x=-1 selects centered drawing; other x values are used directly | Draw function and mocked blitter arguments | High |
| Confirmed | Each character emits one glyph blit, advances x by width+1 | Exact per-character traces | High |
| Unknown | High-byte characters are valid gameplay input | Injected tests prove arithmetic, not reachability | Caller/asset audit pending |

## Behavior model
The current bank selects a 512-byte block of 128 four-byte far glyph pointers. Character bytes are sign-extended: pointer index = bank*128 + signed8(character). Bytes 128..255 therefore index before the selected bank's 128 entries. The functions contain no local range check. The tests initialize these additional pointer slots deliberately; they do not prove valid original assets for them.

A glyph's second header byte is its pixel width, supported by horizontal advance width+1 and the packed byte-count formula recovered in pass65. String width is the sum of these advances modulo 65536. Center position is low16(floor((320 - signed16(width))/2)); unlike a usual unsigned or non-wrapping layout calculation, a wrapped negative width can yield a large positive center. Input strings are far pointers. The string-width function switches DS to the string segment during reads and restores DS from SS; fixtures use the original compiler convention DS=SS on entry.

Drawing uses x=-1 as a sentinel to call the original centering routine. For each nonzero byte it forwards x,y, a color word, a fourth draw parameter and the far glyph pointer to the glyph blitter. The low color byte is the supplied byte; its high byte retains the character's sign-extension (0x00 or 0xff). The tests verify this actual argument behavior without assigning semantics to the blitter's fourth parameter. x advances with 16-bit wrapping. The lower-level blitter and VGA output remain untested here.

## Locations
DOS1.9: character width 1d25:0012; string width 1d25:0034; center 1d25:007c; draw string 1d25:009a; glyph blit call 1d25:00e9. Per-build entries and center instruction bytes are in text_metrics_tests.json; full direct-reference/caller exports are in each xrefs.tsv. Input hashes and current-bank/pointer-table globals are preserved in the included pass65 metadata.

## Verification
156 cases pass (26 per distinct binary): six character widths including 128/255; five strings (empty, ASCII, signed-byte boundary, 300/600 repeated characters), each tested for width, center, explicit-x drawing and centered drawing. Every blit argument and position is checked; original width/string/center/draw instructions execute unchanged. Only the glyph blitter is mocked. Synthetic glyph headers and pointer tables are used. No actual assets, font rasterization or full startup are claimed.

## Unknowns and next test
Follow the glyph blitter to establish bit orientation, pixel writes, clipping, colors and the fourth draw parameter. Inspect real UIF banks to confirm glyph mapping and valid character ranges. Trace bank-preparation callers for legal bank IDs and segment initialization. Confidence High for measured local text layout; renderer parity remains open.
