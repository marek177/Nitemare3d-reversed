# Pass 72 — source clipping offset and fraction tables

## Finding
Confirmed for six distinct supplied DOS binaries: the two clipping tables used by the vertical texture scaler are generated from its configured visible height. Their arithmetic divides before the final shift; replacing it with a product of a previously rounded reciprocal changes many entries. Supplied1.8/1.9 are identical. This is local producer/consumer evidence, not complete render parity.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Routine writes indices1..511, leaves index0 unchanged | Original execution and full-table comparison | High |
| Confirmed | Input is the same global used as clipped output-row count by scaler | Per-build global addresses in pass71/72 evidence | High |
| Confirmed | Result high-byte portion supplies source offset; low16 supplies phase | Producer stores and pass71 consumer loads | High |
| Confirmed | Divide-before-shift differs from rounded-reciprocal product | Independent comparison; H100 gives390 differing entries | High |
| Confirmed | Shift is16-bit before signed32 division | Original SHL CX / CDQ / IDIV ECX / SAR EAX | High |
| Unknown | Heights reachable through normal viewport configuration | Caller audit pending | Boundary inputs are fixtures |

## Behavior model
For each n1..511, interpret H as signed16. Compute delta=max(n−H,0) using the observed32-bit subtraction/sign branch. Form numerator=signed32(wrap16(delta*64)<<16). Divide numerator by n with signed truncation toward zero, then arithmetic-shift the quotient right1. Call this value V. Store byte_offset[n]=(V>>16)&ff and fraction[n]=V&ffff. No denominator0 entry is generated. The caller supplies existing near arrays; no allocation occurs here.

For ordinary nonnegative H in0..511, the intermediate does not overflow and the exact formula is:

`V = floor(floor(max(n-H,0) * 64 * 65536 / n) / 2)`

The source scaler then adds byte_offset[n] to its source pointer and uses fraction[n] as its initial16.16 fractional phase. This represents the source portion skipped by clipping the enlarged column to the configured visible height. Do not replace V with `floor(max(n-H,0) * floor(0x400000/n) / 2)`: for H100 that alternative differs at390 of511 indices in each build. The difference is rounding in fixed-point units, not a claim that390 screen pixels differ.

Negative and extreme height fixtures exercise 16-bit shift wrapping and signed division. They are not asserted to be valid game viewport settings. The split high portion is only a byte; exact original truncation is retained in the model.

## Locations
| DOS | Builder | H global | Byte table base | Fraction table base |
|---|---|---|---|---|
|1.0|1155:0032|439c|2d4c|2f4c|
|1.1|1155:0032|44a2|2e44|3044|
|1.2|1155:0032|44a2|2e40|3040|
|1.5|1156:0030|4472|2e12|3012|
|1.7|1156:0030|44b4|2e16|3016|
|1.8/1.9|1156:0030|4544|2e50|3050|

All table/global offsets above are relative to each build's actual DS. Exact EXE hashes and table hashes are in clip_table_tests.json. The byte array occupies512 bytes and is immediately followed by the fraction array; its final entries are not external guard space. Index0 remains unchanged in both arrays.

## Verification
60 fixtures pass: six distinct binaries × H=-32768,-1,0,1,64,100,200,511,512,32767. Every one of511 byte offsets and511 fraction words is independently checked per fixture, along with unused index0 and outer sentinel memory. Original routine executes unchanged in Unicorn; no calls, interrupts or I/O are mocked. H and table storage are synthetic. Fresh Ghidra12.2 C and full instruction exports are included. No actual texture or VGA image is rendered in this pass.

## Unknowns and next test
Trace builder callers for valid viewport heights and update order relative to scaler use. Run original builder→scaler together with real geometry, including the BP−7 stack precondition identified in pass71. Actual asset sampling, depth and framebuffer/DAC comparisons remain open. Confidence High for exact table construction and local scaler connection; incomplete for game-wide reachability and pixel parity.
