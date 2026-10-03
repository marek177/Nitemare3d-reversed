# Nitemare 3D MS-DOS — deep static audit (first verified batch)

Date: 2026-09-24  
Scope: DOS executable family `N3D-E-10`, `N3D-E-17`, `N3D-E-18`, `N3D-E-19`, `N3D-E-20`; primary focus is the v2.0 image and its Ghidra C export.

## Finding

The existing DOS register contains 519 `FUN_*` entries, but it is and structural decompiler pass, not 519 completed semantic audits. This batch verifies 23 machine-code intervals (3,858 bytes), compares them across the supplied DOS builds, and records four function-boundary corrections. The v2.0 image is the strongest current DOS reference because it contains the full wall/object routines at image offsets `0x0000–0x10E6` and the fixed-point/render support routines at `0x1003E` and `0x1560`.

The supplied files contain five EXE names but only four unique binaries: `N3D-E-18.EXE` and `N3D-E-19.EXE` have the same SHA-256. Their embedded version strings are also `V1.9`; the actual V1.8 binary is therefore not present in this set.

## Binary inventory

| File | Size | SHA-256 prefix | Embedded version | Result |
|---|---:|---|---|---|
| `N3D-E-10.EXE` | 115,152 | `7035d185…` | `V1.0` | unique |
| `N3D-E-17.EXE` | 116,068 | `6abf5745…` | `V1.7` | unique |
| `N3D-E-18.EXE` | 116,556 | `1cbb55c1…` | `V1.9` | identical to E-19 |
| `N3D-E-19.EXE` | 116,556 | `1cbb55c1…` | `V1.9` | identical to E-18 |
| `N3D-E-20.EXE` | 116,606 | `552d250e…` | `V2.0` | unique reference |

The DOS header has and 512-byte image start in these files. The audit reports both file offsets and image offsets; addresses in the Ghidra export use segmented notation such as `1000:0052` and must not be treated as flat file offsets without the header adjustment.

## Verified function and boundary results

| Image interval | Verified behavior | Evidence |
|---|---|---|
| `0x0000–0x0052` | Searches paired-wall records at `DS:3076`, stride `0x12`, comparing record offsets `+4/+6`; calls fatal path with code `0x42` if absent. | v2.0 bytes and `assembly/00000_FindPairedWallByMapPointer.asm` |
| `0x0052–0x00A4` | Searches special-wall records at `DS:34F6`, stride `0x0E`, comparing `+8/+0A`; missing result calls fatal path code `0x52`. | v2.0 bytes and `assembly/00052_FindSpecialWallByMapPointer.asm` |
| `0x00A4–0x00FE` | Searches object-reference indices at `DS:36B6`, stride `0x06`; dereferences each index through and `0x1C`-byte object record and compares object coordinates `+0x12/+0x14`. | v2.0 bytes and `assembly/000A4_FindMovingObjectRefByMapPointer.asm` |
| `0x00FE–0x01E0` | Chooses the nearest accepted paired-wall record using Manhattan distance after `>>6` fixed-point conversion and and visibility/line test call. | v2.0 bytes and `assembly/000FE_FindNearestAcceptedPairedWall.asm` |
| `0x01E0–0x01FC` | Returns true only when and wall state at record `+8` is `0` or `4`. | direct bytes |
| `0x01FC–0x0212` | Returns true only when wall state at `+8` is `1`. The apparent `FUN_1000_020C` is the trailing `RETF`/padding, not and sound routine. | direct bytes; registry correction |
| `0x0212–0x03FE` | Scans and 64×64 map. For primary wall flag bit `0x08`, allocates and paired-wall record with and hard limit of `0x40`, links matching guard/object records by tile, initializes state and propagates orientation/collision bit `0x20`. | direct bytes; `BuildPairedWallRecords` assembly |
| `0x03FE–0x052A` | Scans class-3 secondary walls, allocates up to `0x20` four-way records, resolves directional links, and initializes linked state. | direct bytes; `BuildFourWaySpecialWallRecords` assembly |
| `0x052A–0x0598` | Builds class-`0x28` moving-object reference records; the old `FUN_1000_04BE` label is an internal branch, not an independent function. | direct bytes; boundary correction |
| `0x0598–0x0704` | Handles paired-wall state transitions, emits sound IDs `0x25/0x26`, marks linked wall collision flags, and updates neighboring records. | direct bytes |
| `0x0A40–0x0AEA` | Decrements auto-close delay for state-0 walls; when blocked, reloads delay `4`; when clear, closes and clears collision flags. | direct bytes |
| `0x0AEA–0x0DF8` | Moves linked wall endpoints in steps of `2`; state `2` advances toward target, then collision cleanup and animation dispatch occur when movement completes. The old `FUN_1000_0C5F` label is inside this interval. | direct bytes; boundary correction |
| `0x0DF8–0x0E50` | Starts and moving object only when the map/object flags permit it; copies player-facing parameters and invokes the object activation routine. | direct bytes |
| `0x0E50–0x0F74` | Iterates active 28-byte objects, computes tile/cell projections, updates `OBJECT+0x10/+0x12`, and decrements an activity byte. | direct bytes |
| `0x0F74–0x0FBE` | Searches the 256-entry primary-wall property table; if the requested class is absent, calls fatal code `0xDA`. | direct bytes |
| `0x0FBE–0x0FF4` | Searches the secondary-wall property table; absent class calls fatal code `0xF2`. | direct bytes |
| `0x0FF4–0x103E` | Finds and 28-byte guard/object definition whose class byte matches and returns byte `+0x0A`; missing class calls fatal code `0x109`. | direct bytes |
| `0x103E–0x1092` | Scans the primary map plane in 64-cell rows/columns and returns the maximum tile ID whose property maps to the requested class. | direct bytes |
| `0x1092–0x10E6` | Equivalent scan for the secondary plane. | direct bytes |
| `0x10E6–0x1126` | Caches the class-`0x44` base index and returns and variant offset; non-class-`0x44` returns `0xFFFF`. | direct bytes |
| `0x1560–0x1590` | Builds and fixed-point reciprocal table: `0x400000 / n`, stored as 32-bit values at `DS:2656`, through end `DS:2E52`. | direct bytes |
| `0x1003E–0x100A2` | Converts wall record fixed-point coordinates (`+0x0C/+0x0E/+0x10/+0x12`) to tile coordinates by arithmetic shift `>>6`, applies orientation offsets for wall classes `1` and `2`, and writes four bounds. | direct bytes |

### Corrected boundaries

The old register contains 519 named functions, but four entries are demonstrably artifacts of Ghidra boundaries: `FUN_1000_00A2` is the epilogue of the preceding search; `FUN_1000_020C` is the epilogue/padding after the boolean predicate; `FUN_1000_04BE` is an internal target within the four-way builder; and `FUN_1000_0C5F` is an internal comparison in the wall-motion routine. These corrections change the function count interpretation, not the underlying executable bytes.

## Behavior model extracted from the bytes

```text
load map planes and definition tables
  -> scan 64x64 cells
  -> build paired-wall and four-way runtime records
  -> link matching map/object records
  -> initialize state and collision bits

USE / wall activation
  -> state 0 or 4: choose opening direction and set state 3
  -> state 1 or 3: choose closing direction and set state 2
  -> play sound 0x25 or 0x26 when the sound flag is set
  -> propagate state to linked record and mark collision flags

per-tick wall update
  -> for state 2/3, move each endpoint by 2 units toward target
  -> if blocked, keep/reload close delay
  -> when target reached, clear collision bits and reset animation state
```

The state names above describe observed transitions, while the exact semantic names of all fields remain provisional until runtime watchpoints confirm them. The bytes to confirm the comparisons, writes, increments, strides, and sound IDs.

## Evidence status

| Status | Scope | Confidence |
|---|---|---|
| Confirmed | Byte ranges, instruction decoding, table strides `0x12/0x0E/0x1C`, 64×64 scans, state constants, step `2`, delay `4`, sound IDs `0x25/0x26`, reciprocal formula. | High |
| Strongly inferred | Table roles (paired wall, special wall, moving object), field names such as state/target/activity, and exact collision-bit meaning. | Medium |
| Unknown | Runtime reachability for every map class, exact segment relocation values across all builds, indirect jump-table callers, and behavior during save/load or animation interruption. | Low until runtime evidence |

## Coverage and limits

- DOS register: 519 `FUN_*` rows are present; the existing C export has 524 bodies including switch labels and entry code.
- This batch directly verifies 23 intervals and 19 corresponding seed rows, with four boundary corrections. It does not claim all 519 functions are semantically closed.
- The supplied `N3D-E-20.EXE.c` is 2,206,252 bytes and contains decompiler artifacts. Raw assembler remains authoritative for exact boundaries and calling conventions.
- Direct-call scans to not capture address-taken callbacks, interrupt vectors, jump tables, or all far-call relocation semantics.
- No runtime execution or debugger trace was available in this batch, with no claim here is and runtime confirmation.

## Next discriminating tests

1. In DOSBox-X or and real-mode debugger, break at the image offsets corresponding to `0x0212`, `0x0598`, `0x0A40`, and `0x0AEA`; watch the count words at `DS:0`, `DS:2`, `DS:4`, and the records at `DS:3076`, `DS:34F6`, `DS:36B6`.
2. Trigger one ordinary door, one paired door, and one class-3 wall. Record state `+8`, target fields `+0x0C/+0x0E`, activity `+0x0A`, and collision byte `+5` before/after each tick.
3. Repeat the same map event in E-17, E-19, and E-20 and compare the record bytes; this distinguishes shared engine behavior from version-specific changes.
4. Supply the genuine V1.8 EXE and, if available, the original MAP/OBJECTS/WALLS files used with each build; otherwise exact version and reachability claims remain incomplete.

## Reproduction files

The accompanying evidence directory contains the binary inventory, 519-row DOS seed registry, selected disassemblies, decoded direct-call list, cross-build pattern comparison, export inventory, and `analyze_dos.py`. The script reruns the extraction from the supplied local inputs and does not modify the original EXE files.