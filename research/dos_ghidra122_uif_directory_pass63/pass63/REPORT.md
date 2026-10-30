# Pass 63 — lazy UIF directory lookup

## Finding
Confirmed: all six supplied distinct DOS binaries lazily read 192 bytes from the beginning of `uif.dat` into a dedicated segment, then return DX:AX = table_segment : ((image_id * 6) & 0xffff). There is no ID bounds check. Supplied 1.8 and 1.9 are identical binaries, represented by DOS18.

## Evidence
| Status | Claim | Location | Confidence / reason |
|---|---|---|---|
| Confirmed | One-time gate is cleared before opening the file | First CMP/MOV in exported lookup functions | High: original instructions executed |
| Confirmed | Open uses 0x8000, read requires exactly 0xc0 bytes, then close | Five far call sites per function | High: checked argument traces and injected failures |
| Confirmed | No range check; IDs 32 and 65535 return offsets 192 and 65530 | Arithmetic tail and original execution | High: boundary fixtures |
| Confirmed | A repeated successful lookup performs no further I/O | Same emulator state, second invocation | High: traces compared |
| Inferred | Directory has capacity for 32 six-byte records | Read size divided by addressing stride | High arithmetic; actual asset contents not inspected |
| Unknown | Which out-of-range IDs are reachable from normal gameplay | Caller-wide range/reachability audit pending | No invalid asset access was executed |

| DOS build | Entry | DS gate byte | Table segment |
|---|---|---|---|
| 1.0 | 1273:152a | 05fd | 2b94 |
| 1.1 | 1275:1550 | 063c | 2ba9 |
| 1.2 | 1275:1562 | 0647 | 2baf |
| 1.5 | 1277:158a | 064b | 2bb4 |
| 1.7 | 1277:1602 | 064b | 2bbe |
| 1.8/1.9 | 1277:1766 | 0678 | 2bd7 |

## Behavior model
If gate != 0: clear gate; open `uif.dat`; if handle == -1 call fatal handler; read 192 bytes into segment:0000; if count != 192 call fatal handler; close. Return far pointer segment:wrap16(id*6). A zero gate skips all file operations. The decoder from pass62 reads a word at record+0 and file offset dword at record+2; absence returns AL=0. This establishes the source of its directory pointer. Gate clearing before failure does not prove recovery behavior because fatal handlers are stopping boundaries in these tests.

## Verification
60 fixtures pass: six binaries × (cached/load for IDs 0,31,32,65535; open failure; short read). Each successful case invokes the original function twice, preserving state. Assertions cover DX:AX, gate timing, exact far-read arguments, filename, open flags, branch selection and retained table bytes. Input MZ hashes and raw instructions are included in `lookup_tests.json` and `lookup_static.json`. CRT open/close, far read and fatal handlers are mocked; original gate logic and arithmetic execute unchanged. No DOS interrupts, real UIF files, VGA or full game are executed.

## Unknowns and next test
Audit writes to the gate and all callers for initialization/reset and legal ID range. Inspect actual UIF directory/offsets to associate image IDs with assets. Resource-cache offset restoration remains separate and unresolved.

## Implementation-ready findings
Use a six-byte little-endian record (word presence/metadata, dword source offset), a 192-byte directory and lazy load gate for this call path. Preserve 16-bit arithmetic and unchecked IDs when modeling original behavior; do not reinterpret out-of-range returns as observed gameplay. Overall confidence High for local lookup semantics, unknown for complete asset validity and full-game parity.
