# Nitemare 3D DOS v2.0 — Orange/Yellow byte-map closure, pass 1

Date: 2026-10-03

## Scope

Primary raw binary: `N3D-E-20(3).EXE`

- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`
- MZ header: `0x200` bytes
- image offset = file offset - `0x200`

The goal is to convert orange/yellow byte-map blocks into deep/static semantic knowledge from raw 16-bit machine code, rather than trusting polluted Ghidra pseudo-C boundaries.

## 1. Correction: 59F0 is GUARD runtime, not a generic entity scheduler

The V2.0 pseudo-C boundary around `1000:59F0` is polluted. Raw DOS 1.9 disassembly independently establishes the real family:

- `1000:59F0` = `UpdateGuardState(guard, object)`
- 22-state dispatcher, state byte `GUARD+0x0B`, values `0x00..0x15`
- `1000:5F26` = `UpdateAllGuards()`
- GUARD stride = `0x1A` (26 bytes)
- `1000:5F66` = set current GUARD state to `0x0B`
- `1000:5F74` = player-to-GUARD damage / lethal-nonlethal / pain-death transition path

Therefore the 26-byte records previously described only as a generic runtime-action pool should be classified as **GUARD records**.

### Byte-map consequence

Rows/ranges that were orange only because normalized V2.0 pseudo-C was weak should not remain orange when raw sibling assembly closes the behavior.

Recommended knowledge colors:

- `59F0` family: ORANGE -> GREEN (static semantics deep; runtime acceptance is separate)
- `5F26`: YELLOW -> GREEN
- `5F66`: YELLOW -> GREEN
- `5F74`: ORANGE -> GREEN

## 2. Heap allocator: all three remaining yellow subranges closed

Prior byte map already had the far-heap allocator/free family mostly green but retained three yellow ranges. Raw disassembly of the exact V2.0 binary resolves all three.

### A. image `0x13FDE–0x14047` — arena initialization and list insertion

#### `0x13FDE–0x14011`: initialize arena descriptor

Raw behavior:

- computes `arenaEnd = BX + AX`, stores it at `arena+0x04`;
- installs terminal sentinel `0xFFFE` two bytes before the arena end;
- stores sentinel pointer at `arena+0x0A`;
- subtracts `0x16` bytes of arena/header overhead;
- creates the first free block at `arena+0x14`;
- records the current segment at `arena+0x00`;
- initializes both scan/current pointers `arena+0x06` and `arena+0x08` to the first free block;
- clears link/metadata words `arena+0x0C..+0x12`.

Best semantic name: `InitHeapArenaDescriptor`.

#### `0x14012–0x14047`: link arena into heap list

Raw behavior:

- handles empty-list insertion directly;
- otherwise loads the previous tail via a far pointer;
- writes the old tail's forward link to the new arena (`+0x0C/+0x0E`);
- writes the new arena's back-link to the old tail (`+0x10/+0x12`);
- updates list first/current/tail-style far pointers.

Best semantic name: `LinkArenaIntoHeapList`.

**Status:** YELLOW -> GREEN.

### B. image `0x140C4–0x1414F` — arena growth policy

The previously vague “growth policy” is now decoded.

1. Requires growable flag bit 0 at `arena+0x02`.
2. Calls the tail-block locator (`0x141A1`).
3. If the last real block is already free, subtracts its available size from the extra requirement so that block can be reused.
4. Adds the current arena end.
5. Reads preferred growth granularity from stack/runtime global `SS:0x2344`.
6. Normalizes/uses a power-of-two alignment, with special handling for `0x2000`.
7. Rounds the desired new end upward using `(need + alignment - 1) & ~(alignment - 1)`.
8. Calls the DOS resize helper (`0x14150`).
9. If the preferred-granularity resize fails, retries with 16-byte granularity.
10. On success, converts the old sentinel into a new free tail block, writes a new `0xFFFE` sentinel at the enlarged end, and updates arena metadata.

Best semantic name: `GrowHeapArena`.

**Status:** YELLOW -> GREEN.

### C. image `0x141A1–0x141C0` — tail/sentinel traversal

Raw behavior:

- begins from `arena+0x08` scan cursor;
- if that cursor already equals `arena+0x0A` sentinel, restarts at first block `arena+0x06`;
- reads each block header;
- `0xFFFE` terminates the scan;
- otherwise advances by the even-size portion of the header (`header & 0xFFFE`);
- on sentinel, returns the address of the last real block header immediately preceding it.

Best semantic name: `FindLastHeapBlockBeforeSentinel`.

**Status:** YELLOW -> GREEN.

## 3. Heap byte-map update

| Image range | Old | New | Meaning |
|---|---|---|---|
| `0x13F32–0x13F44` | GREEN | GREEN | far-heap free |
| `0x13F45–0x13FDD` | GREEN | GREEN | far-heap allocation entry/retry/arena selection |
| `0x13FDE–0x14047` | YELLOW | **GREEN** | arena init + arena-list linking |
| `0x14048–0x140C3` | GREEN | GREEN | free-block scan/coalescing/split/return |
| `0x140C4–0x1414F` | YELLOW | **GREEN** | grow policy + alignment/fallback |
| `0x14150–0x141A0` | GREEN | GREEN | DOS resize (`INT 21h AH=4Ah`) |
| `0x141A1–0x141C0` | YELLOW | **GREEN** | last-block/sentinel traversal |
| `0x141C2–0x14205` | GREEN | GREEN | allocate new DOS arena (`INT 21h AH=48h`) |

Newly promoted in this pass: **278 bytes YELLOW -> GREEN**.

The continuous allocator subsystem `0x13F32–0x14205` is **724 bytes** and can now be treated as GREEN/DEEP for static semantics. The exact historical C-runtime symbol names remain unknown, but the machine behavior and ABI are sufficiently reconstructed for implementation.

## 4. Important color-map rule discovered

A weak Ghidra normalized match must not automatically make a byte range orange.

There are at least three independent reasons for yellow/orange:

1. **semantic unknown** — real reverse-engineering work remains;
2. **decompiler-boundary corruption** — raw machine code may already be clear;
3. **runtime-conformance gap** — static algorithm is known, but live original-game timing/pixel/order has not yet been captured.

For the Defraggler-style map the cleanest representation is therefore:

- base fill = STATIC KNOWLEDGE (red/orange/yellow/green);
- border/dot overlay = RUNTIME VALIDATION (unverified/partially verified/accepted).

This prevents already-closed gameplay/engine code from looking orange solely because one pseudo-C export or runtime acceptance test is weak.

## 5. Next orange/yellow targets

Highest-value next raw passes:

1. stale LOW/MEDIUM rows whose labels come from the polluted V2.0 pseudo-C boundaries;
2. remaining heap/CRT/support blocks outside `0x13F32–0x14205` that are still semantically unnamed;
3. renderer/runtime-integration yellows where the algorithm is known but exact mutable VEC/resource synchronization still needs a raw parity/acceptance pass;
4. original-runtime acceptance overlays for gameplay ordering/timing, without downgrading already closed static semantics.