# Pass 65 — UIF packed bitmap bank preparation

## Finding
Confirmed: the sole direct raw-UIF-loader caller identified by Ghidra prepares banks with 128 far-pointer slots and reverses each bitmap payload byte in place. This is consistent with a font/bitmap glyph bank, but exact asset identities and dimension names remain unconfirmed without actual UIF data and drawing consumers.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | One defined direct raw-loader call site per build | Fresh Ghidra 12.2 xrefs.tsv | High for direct references; indirect calls not excluded |
| Confirmed | Low byte selects current bank, loaded gate, data position and pointer block | Caller instructions and bitmap_bank_tests.json | High; original execution |
| Confirmed | Full 16-bit argument is forwarded as UIF ID | Original call arguments, including 0x0101 | High; injected argument, not gameplay reachability |
| Confirmed | Data offset bank*1200, pointer block bank*512, 128 slots | Executed instructions and pointer comparisons | High |
| Confirmed | Slots 1..127 parse two header bytes and reverse payload bits | Original caller plus original bit-reversal helper | High; independent byte expectations |
| Inferred | The bank represents bitmap glyphs/fonts | 128 pointers, packed bit counts, in-place bit reversal | Medium; downstream rendering and assets pending |

## Locations
| DOS | Bank preparation | Bit reversal helper |
|---|---|---|
| 1.0 | 1cdc:016a | 1f67:00d0 |
| 1.1 | 1d00:016e | 1f89:00c8 |
| 1.2 | 1d00:0170 | 1f8f:00c8 |
| 1.5 | 1d05:016e | 1f94:00c6 |
| 1.7 | 1d0f:016a | 1f9d:00d2 |
| supplied 1.8/1.9 | 1d25:016e | 1fb7:00c6 |

All DS globals and fixed data segments, input hashes, exact instructions and xrefs are preserved in evidence. 1.8/1.9 are identical supplied binaries.

## Behavior model
Write current_bank = id & 255 before checking loaded[bank]. If loaded is nonzero, return without rebuilding pointers or transforming data. Otherwise set loaded[bank]=1 before raw load(id, data_segment:wrap16(bank*1200)). Slot 0 receives the bank base pointer; parsing starts at base+2 for slot 1. For each slot 1..127, store pointer to its two-byte header, calculate n = header[0] * ((header[1]+7)>>3), reverse the bit order of each of the n following bytes, then advance by n+2. Pointer entries are four-byte offset/segment pairs. Header and initial two bytes are not transformed. The helper reverses bit significance within a byte, rather than reversing byte order.

No local bounds check against the 1200-byte bank spacing or UIF length is present in the observed body. This does not establish malformed assets or invalid IDs in normal play. Passing 0x0101 demonstrates that bank selection uses 1 while the raw loader receives ID 257; legal caller inputs still require upstream analysis.

## Verification
48 cases pass: six distinct binaries × IDs 0,1,2,0x0101 × initially cached/uncached. Each case invokes the function twice. Synthetic banks include zero-length payloads, 1/8/9/16-bit width-like second bytes and varied payloads; 128 exact far pointers, payload bit reversal, header preservation, cache gate timing and raw load arguments are asserted. Cached fixtures preserve sentinel pointer tables and payload bytes. Second calls preserve output, preventing double bit reversal.

Original bank preparation and original bit-reversal helper execute unchanged in Unicorn. The raw-loader call is mocked to supply a synthetic bank; DS=SS, and the segment-global used for second header-byte reads is explicitly initialized to the fixed bank segment. This is a harness precondition, not proof of its full-game initialization. No real UIF, VGA output or complete font renderer has been tested.

## Unknowns and next test
Trace the bank-preparation callers and pointer-table consumers to establish reachable IDs, glyph index mapping and visual orientation. Verify actual UIF record sizes against 1200-byte bank spacing, determine initial two-byte meaning, and follow the data-segment global initializer. Complete game parity remains open. Overall confidence High for local transformation and cache semantics; Medium for font interpretation.
