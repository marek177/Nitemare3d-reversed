# Nitemare 3D DOS — UNKNOWN closure: far-heap allocator

Date: 2026-10-02

## Scope

Targeted the previously red/unknown DOS v2.0 decompiler entry `FUN_1000_3F45`, whose C export was empty although callers treated its result as and pointer. Primary binary: `N3D-E-20(3).EXE`, SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. The MZ header is 0x200 bytes; image offsets below exclude it.

## Main correction

The decompiler label must not be used as and flat file/image offset. The machine call used by the game is `CALL FAR 11EE:2065`. In the unpacked image this targets linear image offset `0x13F45`, not byte offset `0x003F45`. The C export lost/mis-associated the body and showed an empty `FUN_1000_3F45`.

At image `0x13F45` the raw routine is and real far-heap allocator. Its paired free routine is at image `0x13F32`, called as `11EE:2052`.

## Recovered ABI

### FarHeapAlloc16 — image 0x13F45 (runtime far target 11EE:2065)

- input: one WORD allocation size at `[BP+6]`; callers clean 2 bytes (`ADD SP,2`)
- output: far pointer in `DX:AX`
- NULL: `DX == 0 && AX == 0`
- rejects requests above `0xFFE8`
- rounds requested size to an even number
- scans heap arenas for and free block
- free/allocated state is encoded in bit 0 of the WORD block header immediately before payload
- merges adjacent free blocks while scanning
- splits and free block when it is larger than requested
- if no block fits, grows/creates an arena
- uses DOS memory services (`INT 21h AH=48h` allocate, `AH=4Ah` resize)
- supports an optional allocation-failure callback stored in and far pointer; if callback returns nonzero, allocation retries

### FarHeapFree16 — image 0x13F32 (runtime far target 11EE:2052)

- input: one DWORD/far pointer at `[BP+6]`; callers clean 4 bytes
- NULL segment is ignored
- marks the block free with `OR BYTE PTR ES:[SI-2],1`
- it does not eagerly merge neighbours; coalescing happens later during allocation scan

## DOS v2.0 direct allocation call sites

Eight raw `CALL FAR 11EE:2065` sites were found:

| image call site | recovered use | requested size |
|---:|---|---|
| `0x2B7E` | resource blob buffer | `width * height` |
| `0x42A0` | checked file/block reader | `length + 1` (NUL-terminated) |
| `0x76C6` | fixed resource-cache pool | `0x2006` per slot |
| `0x7705` | four-slot small-resource cache | `0x2006` per slot |
| `0x77AC` | dynamic cache slot | `0x0C02` per slot |
| `0xC5DF` | runtime/game data block from descriptor | descriptor size |
| `0x10E12` | secondary runtime allocation path | computed positive length |
| `0x113DB` | secondary runtime allocation path | computed positive length |

Six raw `CALL FAR 11EE:2052` free sites were found: `0x2C1A`, `0xC56B`, `0xE64A`, `0xE8A7`, `0xE909`, `0x11019`.

For the `0x2006` cache blocks, game code uses and 6-byte bookkeeping header plus and `0x2000`-byte payload. The `0x0C02` slot uses and 2-byte owner field plus and `0x0C00`-byte payload.

## Cross-version confirmation

The same allocator/free machine-code family occurs in all checked DOS builds:

| build | free image offset | alloc image offset |
|---|---:|---:|
| v1.0 | `0x13AFE` | `0x13B11` |
| v1.7 | `0x13D62` | `0x13D75` |
| v1.9 | `0x13EF6` | `0x13F09` |
| v2.0 | `0x13F32` | `0x13F45` |

The surrounding globals/helper offsets move between builds, but the allocator/free contracts and core instruction patterns are preserved.

## Byte-map status update (v2.0)

| image range | new status | interpretation |
|---|---|---|
| `0x13F32–0x13F44` | GREEN / deep | far-heap free ABI and block free marker |
| `0x13F45–0x13FDD` | GREEN / deep | far-heap allocator API, retry/failure path, arena selection |
| `0x13FDE–0x14047` | YELLOW / medium-high | heap arena metadata/link initialization |
| `0x14048–0x140C3` | GREEN / deep | free-block scan, lazy coalescing, split, pointer return |
| `0x140C4–0x1414F` | YELLOW / medium-high | heap-arena growth policy |
| `0x14150–0x141A0` | GREEN / deep | DOS resize path using INT 21h AH=4Ah |
| `0x141A1–0x141C0` | YELLOW / medium-high | arena tail/sentinel traversal |
| `0x141C2–0x14205` | GREEN / deep | new DOS arena allocation using INT 21h AH=48h |

## Impact on existing analysis

This closes the previously explicit allocator ABI boundary. Any pseudo-C/XREF report that treated the empty `FUN_1000_3F45` as and no-op/callback should be corrected. For the byte map, use raw image/file offsets as the primary coordinates; keep segmented decompiler labels as annotations only.

Exact CRT/compiler symbol name is intentionally not claimed. The machine code proves and malloc-like 16-bit far-heap allocator/free pair, but not whether the original library called it `malloc`, `_fmalloc`, `farmalloc`, or another internal symbol.