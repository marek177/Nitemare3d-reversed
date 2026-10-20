> Historical source report supplied with the D02-N patch. This bulk integration reruns public synthetic tests only; the original EXE audit and private pool acceptance were not rerun. Current scope: [bulk update](BULK_UPDATE_20261020.md).

# Nitemare 3D — D02-N: original DOS2 VEC producer, four-pass reconstruction

**Date:** 20 October 2026. **Evidence:** verified SHA-bound original DOS2 opcodes + C++20 bounded reconstruction over synthetic MAP/DS-property fixtures. This pass did **not** execute a new original DOSBox-X gameplay session and does **not** demonstrate 592/592 original pool or framebuffer parity.

## Original executable identity

Original user's `N3D-UNFU.exe`: 116,606 B, SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`. `MZ` header = 512 B. All addresses in this report denote offsets in its **unpacked MZ load image**, not emulator CS:IP or Windows NE offsets. The original EXE is not distributed.

## A. Newly connected original creation and sorting call graph

```
0x32E2  scene initialization
  0x3304 CALL FAR 0FD9:0E1C -> 0x10BAC build VEC pool
    0x10BB5 -> 0x10892 orientation 0; destination DS:62AC
    0x10BC8 -> 0x10892 orientation 1; destination += count0 * 28
    0x10BDB -> 0x10892 orientation 2; destination += (count0+count1) * 28
    0x10BEE -> 0x10892 orientation 3; destination += prior count * 28
    0x10BF6 MOV DS:[626E], SI  (total active VEC count)
  0x3309 CALL FAR 0FD9:005E -> 0xFDEE group and sort VEC pointers
    per-type counters DS:57FA,57FC,57FE,5800
    near-pointer arrays DS:5802,5A9C,5D36,5FD0
    array capacity 333 pointers each
    comparison callback 0xFDA6, external sort via FAR 11EE:3090
```

The original sorted-pointer arrays from the archived v0.68 snapshot contained `148/144/152/148` VECs (592 total). That snapshot has **not** been reproduced by the new MAP producer model; it is a later acceptance target, not today's success claim.

The SHA-gated original-image verifier checks **59 opcode windows and 10 CALL targets**. Among 15 literal `6E 62` count-field references in the image, it finds exactly one direct absolute `MOV DS:[626E], SI`, at `0x10BF6`. Indirect/aliased writes remain unenumerated.

## B. Original 0x10892 per-orientation scan

Each of the four passes traverses a `64×64` map with `2` bytes per cell. In orientation 0/1, the inner loop increments X; in 2/3, it increments Y. Before reading neighbouring map data, an out-of-bounds neighbour skips the current cell. The neighbour direction depends on VEC orientation:

| VEC orientation | Neighbour delta | Axis extended by 0x10854 |
|---|---|---|
| 0 | (0, −1) | end X `VEC+0x10 += 64` |
| 1 | (0, +1) | end X `VEC+0x10 += 64` |
| 2 | (+1, 0) | end Y `VEC+0x12 += 64` |
| 3 | (−1, 0) | end Y `VEC+0x12 += 64` |

The current WALL byte comes from `ES:373E + 2*(y*64+x)`, current OBJECT from `ES:373F + 2*(y*64+x)`; the original code uses `ES=21FD` in this bounded path. It reads adjacent-wall and adjacent-object cells, wall properties at `DS:D00C + wallID`, wall classes at `DS:D30E + wallID`, and object classes at `DS:D40E + objectID`.

The normal edge/merge path checks wall property `0x04`, neighbour property `0x04`, property-bit `0x08` differences, property `0x10`, and class-3 neighbouring objects. It may create a fresh 28-byte VEC through `0x105EA`, extend the immediately previous segment through `0x10854`, or skip an interior face.

## C. Original separate door path

When the ordinary `WALL_PROPERTY&0x04` path is not taken, `0x10592` allows door classes `0x31..0x40` in these orientations:

- odd class IDs (31,33,…,3F): **2 or 3**;
- even class IDs (32,34,…,40): **0 or 1**.

This result is independently checked against all 16 code-segment jump-table entries. `0x106F2` constructs special centered door geometry with half-tile (`32`) offsets; some classes also use a distinct resource ordinal mapping.

## D. Implemented bounded code and confidence

`src/game/Dos20VecProducer.hpp` implements:

- strict orientation pass order 0→1→2→3, 64×64 traversal, neighbour selection;
- regular VEC creation and extend-by-64 merging;
- special centered door VEC creation, orientation gate and class-dependent ordinal;
- capacity-check failure before writing more than 1,000 VECs;
- optional import of exact `DS:D00C`, `DS:D30E`, `DS:D40E` lookup tables from a private 65,536-byte DOS DS snapshot;
- per-orientation near-pointer grouping, max 333 each, and exact **primary** 0xFDA6 comparison with `0` on equal keys; no guessed secondary tie ordering;
- interoperable 28-byte `vecpool::RawVec` output consumed by existing `Dos20VecPoolRuntime`.

Original `F7:0004` class-first-resource mapping remains caller-provided, not guessed. The `0x106BC–0x106EB` wall property-bit `0x08` remap branch is explicitly rejected as unsupported; malformed/wrapping original geometry and unchecked runtime shared-alias effects remain open. Normal C++ zero-initialization of unused 28-byte fields is not claimed bytewise original-pool parity.

**DO NOT** replace the active game update, SDL/DDA renderer or original VEC producer for all maps based only on these bounded tests.

## E. Executed verification

| Verification | Result | Boundary |
|---|---|---|
| DOS2 original opcode audit | 59/59 PASS | original static only |
| Direct original edges | 10/10 PASS | original static only |
| Door dispatch class table | 16/16 PASS | original static only |
| Original count-field direct absolute writer census | 1 identified at `0x10BF6` | not alias-exhaustive |
| Python verifier unit tests | 4/4 PASS | includes private original fingerprint check |
| GCC C++20 producer regression | PASS | synthetic map and DS fixtures |
| Clang C++20 producer regression | PASS | synthetic map and DS fixtures |
| VEC producer→existing pool lookup integration | PASS | synthetic isolated-wall fixture |
| Complete original E1M1 VEC pool `592/592` | **OPEN** | raw snapshot and fully bound resource lookup needed |
| Original full VEC sorted pointer order | **OPEN** | original external qsort ties unmodeled |
| Original clean-room framebuffer + palette zero diff | **OPEN** | whole-engine, timed run required |

Original artifacts, proprietary binaries, original MAP/IMG and large raw CPU traces have not been distributed.

## F. Next D02-O evidence gate

Capture or recover the **original 64KiB DS snapshot** at a pre-VEC and post-VEC checkpoint with matching original MAP.* and resource definitions. Derive `DS:D00C`, `DS:D30E`, `DS:D40E`, and `F7:0004` class-first resource mappings, then compare **each 28B VEC in original order**. Close the bit08 resource remap and renderer/door exceptions before enabling the full producer in the live engine. Finally reproduce the original external sort tie behavior and test synchronized original-vs-clean-room MAP→VEC→SPAN→WALL→framebuffer on the same clock tick.

**Current global 1:1 parity percentage: unchanged.** No GitHub mutation was executed in this pass.
