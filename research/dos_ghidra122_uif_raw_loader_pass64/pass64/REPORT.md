# Pass 64 — UIF raw loader and gate lifecycle

## Finding
Confirmed in six distinct DOS builds: the UIF directory record is `u16 byte_length; u32 file_offset`, not merely a presence flag. A second consumer loads the requested raw bytes to a caller-supplied far destination. This refines pass62/63 terminology: the screen decoder treats zero length as absence; it does not use the length to bound image decoding.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | Raw loader uses record word as exact byte count | Fresh Ghidra exports, raw_loader_tests.json | High; original instructions executed |
| Confirmed | Gate initial byte is 1 in every supplied MZ | caller_audit.json, MZ DS offset | High; direct bytes |
| Confirmed | Ghidra has only gate read and zero-write in lookup | Per-build xrefs.tsv | High within defined references |
| Unknown | No possible indirect/aliased gate writes anywhere | Whole-program indirect writes not excluded | Explicit limitation |
| Confirmed | Two direct lookup consumers: image decoder and raw loader | xrefs.tsv lookup rows | High for direct references |

## Locations
| DOS | Raw loader |
|---|---|
| 1.0 | 1273:1730 |
| 1.1 | 1275:1756 |
| 1.2 | 1275:1768 |
| 1.5 | 1277:1790 |
| 1.7 | 1277:1808 |
| supplied 1.8/1.9 | 1277:196c |

The raw loader opens uif.dat with 0x8000, rejects any signed-negative handle (tested 0x8000), invokes the original lookup, seeks to record+2 with origin zero, reads record+0 bytes into the supplied far pointer, rejects a count mismatch, then closes. Seek status is ignored. Zero length still follows open/seek/read/close. Count comparison is bit-exact, including 32768 and 65535. A successful mock read does not prove DOS can transfer every such length in every memory layout.

## Verification
48 passing cases: six binaries × lengths 0,1,127,32768,65535; short read; negative open; failed seek. The original raw loader and original cached directory lookup both execute. Only open, seek, far-read, close and fatal boundaries are mocked. Far destination and exact arguments are asserted. No payload transfer or OS/VGA behavior is claimed. Fresh Ghidra 12.2 exports include all direct lookup/decoder callers and gate references, plus full caller instruction bodies.

## Caller frontier
For DOS1.9, fullscreen decoder direct callers are 1476:01f1, 1d25:0413, 1d25:07f6, 1d25:16a1, 1d25:16b0. The latter UI paths explicitly push IDs 3 and 5; the wrapper 1d25:0404 forwards its parameter. Therefore this pass does not close all legal-ID reachability: forwarded parameters require upstream tracing. No blanket claim that IDs are always within 0..31 is justified. Ghidra C omits some argument pushes due to prototype inference; instruction contexts are retained in caller_audit.json.

## Implementation-ready findings
Preserve a six-byte packed little-endian directory entry, unsigned length and offset, original unchecked lookup arithmetic, caller-provided far destination, exact-count validation and signed-negative open failure test. Gate reset during normal play was not found among direct xrefs, but indirect writes remain possible. Actual UIF assets, image-ID mapping, complete renderer output and resource-cache restoration remain unresolved. Overall confidence High for these local semantics, incomplete for game-wide reachability.
