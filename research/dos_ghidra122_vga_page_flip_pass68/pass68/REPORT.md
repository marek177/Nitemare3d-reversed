# Pass 68 — VGA page swap and display-start update

## Finding
Confirmed for six distinct supplied DOS binaries: two page-flip routines swap the exact segment globals consumed by the UIF glyph rasterizer and emit a CRTC register0x0c update. The synchronized variant polls VGA status and unconditionally enables interrupts after its CRTC write. This establishes the local connection from glyph destination selection to display-start programming, not full display scanout or timing parity. Supplied1.8/1.9 are identical.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Initial zero/nonzero destination segments are a400/a000 | Original MZ data, page_flip_tests.json | High |
| Confirmed | Both variants swap the segment globals | Fresh Ghidra xrefs and original execution | High |
| Confirmed | OUT word to3d4 is 0x0c + ((old_zero_segment>>8)<<4 truncated8)<<8 | Original instructions and exact port traces | High |
| Confirmed | Immediate variant preserves IF | Both initial IF states tested | High |
| Confirmed | Synchronized variant executes CLI/OUT/STI; returns IF=1 | Original instructions and runtime IF observations | High |
| Confirmed | Software swap precedes status polling | Global values at OUT, plus bounded waiting fixtures | High |
| Unknown | Real frame timing, visible scanout and lower CRTC address state | IN values mocked; other VGA configuration not executed | Requires integrated VGA run |

## Locations
| DOS | Immediate flip | Synchronized flip |
|---|---|---|
|1.0|1155:0090|1155:00aa|
|1.1|1155:0090|1155:00aa|
|1.2|1155:0090|1155:00aa|
|1.5|1156:008e|1156:00a8|
|1.7|1156:008e|1156:00a8|
|1.8/1.9|1156:008e|1156:00a8|

## Behavior model
Let Z=page_zero_global and N=page_nonzero_global. Both routines first exchange Z,N. Both program a word OUT to port3d4 with low byte0x0c (CRTC start-address high register) and high byte wrap8((old_Z>>8)<<4). They do not write CRTC register0x0d. For supplied initial Z=a400,N=a000 the first OUT is0x400c; the second flip emits0x000c and restores the original segment pair. Low segment bits are ignored in the CRTC conversion; synthetic nonaligned values demonstrate that arithmetic without claiming such values are normal.

The glyph rasterizer's argument0 therefore targets the other segment after a flip, while nonzero targets the segment just selected by this high-address write. Calling that segment visible requires the lower CRTC start byte and VGA address mode to be configured consistently, which is still an integration precondition.

Synchronized sequence: swap globals; repeatedly read port3da while bit0 is1; CLI; emit CRTC OUT; STI; repeatedly read port3da until bit3 is1; return. It does not require observing bit3 clear before set. Incoming IF is not restored. It has no timeout. In bounded fixtures stuck in either wait, the function has not returned; both globals are already exchanged. When stuck in the second wait, the CRTC write has occurred and interrupts are enabled. Immediate variant performs no IN and no interrupt-flag instruction.

## Verification
108 cases pass (18 per binary): four segment pairs × two incoming IF states × two flip variants, plus stuck first/second status waits. Each successful case executes two flips in the same memory state. Assertions check both globals, precise word OUT, IF at OUT and return, read sequences and bounded non-return behavior. The original code executes unchanged in Unicorn. Only port3da input values are mocked; OUT is observed. No DOS interrupt handlers, VGA timing or physical scanout is modeled. A bounded non-return observation supports the inspected loop; it is not an elapsed-time measurement.

## Unknowns and next test
Follow VGA initialization and writes to the CRTC low start byte/address mode; trace actual flip callers and status-driven timing with DOSBox-X. Integrate original text layout, glyph raster and page flips on real UIF assets. Pixel/DAC and whole-game parity remain open. Confidence High for local swap/I/O/IF semantics, incomplete for hardware display behavior.
