# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 34

Date: 2026-10-03

Primary image:
- `N3D_DOS_v2.0_IDA.EXE`
- complete unpacked DOS V2.0 image

Address convention:
- raw image offsets are authoritative;
- old Ghidra labels are annotations only;
- runtime acceptance remains and separate overlay from static knowledge.

## Result

Pass 34 returns to the early engine core and closes the complete raw band:

`0x0000 .. 0x15ED`

as **GREEN / deep static semantics**.

Span:

**5,614 bytes**

The important correction is the function census:

- **27 real functions**
- **11 one-byte alignment NOPs**
- multiple stale LOW/WEAK Ghidra entries are interior branch/return addresses and must
  be deleted.

This pass does not add the whole 5,614-byte span to the earlier "newly promoted
RED/ORANGE/YELLOW" cumulative counter because substantial parts were already marked
GREEN in the old tracker.  It is and **boundary-normalization/continuous-closure pass**.

---

# 1. Correct raw function census

| Range | Bytes | Correct role |
|---|---:|---|
| `0000–0051` | 82 | `FindPairedWallRecordByCoordinates` |
| `0052–00A3` | 82 | `FindSpecialWallRecordByCoordinates` |
| `00A4–00FC` | 89 | `FindObjectReferenceByTile` |
| `00FE–01DF` | 226 | `FindNearestLosValidDoorRecord` |
| `01E0–01FB` | 28 | `IsWallStateIdleOrTerminal` |
| `01FC–0211` | 22 | `IsWallStateOne` |
| `0212–03FC` | 491 | `BuildPairedWallRuntimeTable` |
| `03FE–0596` | 409 | `BuildFourWaySpecialWallRuntimeTable` |
| `0598–0703` | 364 | `SetAndPropagatePairedWallState` |
| `0704–0A3F` | 828 | `HandlePlayerUse` |
| `0A40–0AE9` | 170 | `TickPairedWallAutoClose` |
| `0AEA–0DF6` | 781 | `UpdateMovingLinkedBoundaryRecords` |
| `0DF8–0E4F` | 88 | `ActivateObjectOnTile` |
| `0E50–0F73` | 292 | `TickMovingMapObjects` |
| `0F74–0FBC` | 73 | `FindPrimaryWallClassIndex` |
| `0FBE–0FF2` | 53 | `FindSecondaryWallClassIndex` |
| `0FF4–103C` | 73 | `GuardClassToRuntimeType` |
| `103E–1091` | 84 | `FindHighestPrimaryWallIndexInMap` |
| `1092–10E5` | 84 | `FindHighestSecondaryWallIndexInMap` |
| `10E6–1124` | 63 | `DecodeDoorVariantIndex` |
| `1126–11BE` | 153 | `BuildWallPropertyFlags` |
| `11C0–1261` | 162 | `BuildObjectPropertyFlags` |
| `1262–12C3` | 98 | `ResolveLevelTransitionTargetIndex` |
| `12C4–13F2` | 303 | `ChooseFreeAdjacentTile` |
| `13F4–155F` | 364 | `ResolveTeleportDestination` |
| `1560–158E` | 47 | `BuildReciprocalProjectionTable` |
| `1590–15ED` | 94 | `BuildViewAngleTables` |

Alignment NOPs:

```text
00FD
03FD
0597
0DF7
0FBD
0FF3
103D
1125
11BF
13F3
158F
```

---

# 2. False function entries removed

The following old Ghidra/audit entries are **not real function starts**:

```text
00A2
020C
04BE
0C5F
1187
11D2
1236
129A
154B
155A
```

## `00A2`

Raw bytes:

```text
00A2  LEAVE
00A3  RETF
00A4  PUSH BP
```

With old `FUN_1000_00A2` is literally the epilogue of `0052`.

Delete it.

## `020C`

Raw byte:

`RETF`

It is the first return tail of `01FC = IsWallStateOne`.

The second false branch tail continues at `020E`.

Delete old `FUN_1000_020C`.

## `04BE`

Raw instruction:

`JMP 04E3`

It is an interior branch of the real function starting at `03FE`.

The old low-confidence `FinishExplodingWallAnimation` entry is therefore not and
standalone routine.

## `0C5F`

Raw instruction:

`CMP AX, ES:[0000]`

It is inside the real `0AEA..0DF6` moving-boundary state machine.

This directly repairs the old weak 5,000-line-style decompiler split.

## `1187`

Interior conditional branch inside `1126 = BuildWallPropertyFlags`.

## `11D2` and `1236`

Both are interior instructions inside:

`11C0 = BuildObjectPropertyFlags`.

## `129A`

Interior `MOV AX,SI` return branch inside `1262`.

## `154B`

Interior output-coordinate write inside `13F4`.

## `155A`

Shared failure-return tail of `13F4`.

Neither is and separate function.

---

# 3. `0000` and `0052` — exact runtime table lookups

## `0000` — `FindPairedWallRecordByCoordinates`

Scans the paired/moving-wall table:

- base `DS:3076`;
- stride `0x12 = 18 bytes`;
- count from the paired-wall runtime count;
- compares record coordinates at `+04/+06`.

Returns the far record pointer when found.

On failure it enters the common fatal/error reporter.

## `0052` — `FindSpecialWallRecordByCoordinates`

Scans:

- base `DS:34F6`;
- stride `0x0E = 14 bytes`;
- compares fields `+08/+0A`.

This is the second wall/special-boundary runtime lookup.

Both are read-only searches except for fatal error reporting on an impossible miss.

**Status: GREEN.**

---

# 4. `00A4` — object-reference lookup

`FindObjectReferenceByTile`

Scans the six-byte object-reference table at:

`DS:36B6`.

Each reference contains an OBJECT index.

The target OBJECT uses the corrected DOS V2.0 stride:

`0x1C = 28 bytes`.

Coordinates are compared against OBJECT fields:

`+12/+14`.

This closes the old object-reference helper without any 0x50-byte-record ambiguity.

**Status: GREEN.**

---

# 5. `00FE` — nearest usable/visible door selector

`FindNearestLosValidDoorRecord`

This routine was missing from the old high-level function list even though strategy-1
GUARD movement depends on it.

Input includes and world-object/actor pointer.

It:

1. converts actor coordinates `+10/+12` to 64-unit cells;
2. scans the 18-byte paired-wall/door table at `3076`;
3. computes Manhattan distance from the actor to each candidate boundary;
4. keeps only and candidate closer than the current best;
5. calls the bounded map-visibility/passability helper for the actor->candidate path;
6. stores the best valid far pointer;
7. returns NULL when none is acceptable.

This is the nearest LOS/passability-valid door/boundary selector consumed by the FLEE
strategy closed in Pass 4.

**Status: GREEN.**

---

# 6. `0212` — paired-wall runtime-table construction

`BuildPairedWallRuntimeTable`

Scans the 64×64 map and creates at most:

`0x40 = 64`

paired-wall runtime records.

Properties:

- output base `3076`;
- output stride `0x12`;
- VEC stride `0x1C`;
- searches VEC pairs for map cells carrying dynamic wall property bit `08h`;
- stores the two VEC references and cell/boundary state;
- applies orientation bit `20h` where required;
- fatal path on capacity/pairing errors.

This is the producer of the table consumed by:

- USE;
- auto-close;
- moving wall update;
- nearest-door steering.

**Status: GREEN.**

---

# 7. `03FE` — four-way/special-wall table builder

Real function:

`03FE..0596`

The old decompiler incorrectly split this function at `04BE`.

The routine constructs the special-wall runtime records used by the multi-component
moving/destructible wall family.

Static behavior includes:

- scanning map/VEC state;
- resolving component VECs through the normal VEC lookup;
- storing the special-wall record in the 14-byte table;
- validating capacity and required components;
- initializing component state/flags;
- handling the final setup path that the stale decompiler exposed as and fake
  "FinishExplodingWallAnimation" function.

The important correction is structural:

**there is one real function at `03FE`, not separate `03FE` and `04BE` routines.**

**Status: GREEN.**

---

# 8. `0598` — paired wall state propagation

`SetAndPropagatePairedWallState`

The already-known state machine is confirmed as one bounded raw function.

It:

- checks global transition lock;
- examines current state;
- selects next state for open/close/toggle;
- optionally plays SFX `25h/26h`;
- updates linked VEC collision/render flags;
- searches adjacent related wall records;
- propagates the transition.

Numeric states include:

`0,1,2,3,4`.

**Status: GREEN.**

---

# 9. `0704` — complete USE dispatcher

`HandlePlayerUse`

This is the large central player USE/action function.

The raw boundary is exactly:

`0704..0A3F`.

It dispatches:

- paired doors/walls;
- locked/key/card interactions;
- object activation;
- teleports/warps;
- level/stair transition selectors;
- special wall classes;
- context messages and effects.

Important: there is no hidden separate function between `0704` and `0A40`.

**Status: GREEN.**

---

# 10. `0A40` and `0AEA` — moving wall runtime

## `0A40` — `TickPairedWallAutoClose`

Walks paired-wall records and counts down open-wall timers.

When the auto-close condition is met:
- transitions the wall toward closing;
- restores render/collision state;
- retries when blocked.

## `0AEA` — `UpdateMovingLinkedBoundaryRecords`

This is the real large moving-wall state machine.

Old `0C5F` is an interior address.

The routine:

- scans the 18-byte paired-wall records;
- advances opening/closing VEC endpoints by exactly `2` world units;
- uses VEC flag `20h` to select/reverse the endpoint side;
- updates terminal states and timers;
- clears render/collision bit 0 when opening completes;
- invokes object/render update helpers when transitions complete;
- then scans the 14-byte special-wall table;
- updates linked four-component wall geometry;
- clears component VEC bits and map-cell bytes when the special transition completes.

This is the exact raw function behind the earlier `UpdateMovingLinkedBoundaryRecords`
hard-census classification.

**Status: RED/ORANGE boundary corruption -> GREEN.**

---

# 11. `0DF8` and `0E50` — active map-object runtime

## `0DF8` — `ActivateObjectOnTile`

Looks up the corresponding six-byte object reference.

If inactive and the map property allows activation:
- captures current actor/player position into the reference;
- marks it active;
- calls the object activation/effect helper.

## `0E50` — `TickMovingMapObjects`

Walks active six-byte movement-reference records.

For every active moving OBJECT:

- applies signed X/Y delta to OBJECT `+16/+18`;
- computes destination map cell;
- preserves/updates map occupancy;
- calls the object/render-order update helper;
- decrements movement lifetime/timer.

The object stride is the corrected:

`0x1C = 28 bytes`.

**Status: GREEN.**

---

# 12. Wall/object class table builders

## `0F74` — `FindPrimaryWallClassIndex`

Searches the 256-byte wall class table, starting from and supplied ID and wrapping.

## `0FBE` — `FindSecondaryWallClassIndex`

Companion lookup for the second class/table family.

## `0FF4` — `GuardClassToRuntimeType`

Maps the relevant class range to the internal runtime guard/type code.

## `103E` / `1092`

Find the highest referenced primary/secondary wall IDs in the current map.

## `10E6` — `DecodeDoorVariantIndex`

Converts and door/wall class occurrence to its class-relative variant/index.

**Status: GREEN.**

---

# 13. `1126` — exact wall-property table

The entire `1126..11BE` body is one function.

For each of 256 wall IDs with class `c`:

```text
bit 04 : c = 01..30
bit 10 : c = 2E..2F
bit 08 : c = 31..40
bit 01 : set when (bit04 | bit08) != 0
bit 02 : c = 01..40
bit 40 : c = 47..48
```

Result is stored in the runtime wall-property table.

Old `1187` is only an interior conditional branch.

**Status: GREEN / exact.**

---

# 14. `11C0` — exact object-property table

The entire `11C0..1261` body is one function.

For object class `c`:

```text
bit 01 : c = 06..3D
bit 02 : c = 08..2D
bit 04 : c = 2F..3D
bit 08 : c = 08..25
bit 20 : c = 2A
bit 40 : c = 04
```

Old `11D2` and `1236` are interior instructions, not function entries.

This is the exact property table used by movement/collision and MAP->VEC generation.

**Status: GREEN / exact.**

---

# 15. `1262` — level-transition target selector

`ResolveLevelTransitionTargetIndex`

Input selector is primarily in the range:

`9..12`.

The routine starts from current level/index:

`DS:626C`.

Observed branches:

- selector `9`: runs transition/display setup and returns current+1;
- selector `10`: runs the same setup and returns current+2;
- selector `12`: delegates to the dynamic menu/list selector;
- other values return current value unchanged.

Old `129A` is and return branch inside this function.

**Status: GREEN.**

---

# 16. `12C4` — free adjacent tile selection

`ChooseFreeAdjacentTile`

Tries four adjacent map cells in and fixed order.

For each candidate it rejects:

- current player cell;
- wall-property bit `02h`;
- object-property bit `02h`.

Returns direction/result codes:

```text
0
2
1
3
```

for successful alternatives and:

`FFFFh`

when all four neighbors are blocked.

The function updates the caller-supplied X/Y variables while probing.

**Status: GREEN.**

---

# 17. `13F4` — complete teleport/warp destination resolver

Real function:

`13F4..155F`

There are no functions at `154B` or `155A`.

Behavior:

1. validate warp/transition class in `0Dh..2Ch`;
2. select the appropriate destination/menu helper based on class band;
3. obtain the target wall/object ID;
4. for selected classes derive destination coordinates directly from the source cell;
5. otherwise scan the 64×64 map for the target ID;
6. call `ChooseFreeAdjacentTile`;
7. on success write:
   - destination X center = cell*64 + 32;
   - destination Y center = cell*64 + 32;
   - output direction code;
8. return `AL=1`.

Failure paths converge at interior label:

`155A`

and return `AL=0`.

Thus:

- `154B` = ordinary coordinate-output instruction;
- `155A` = shared failure tail;
- neither is and separate function.

**Status: GREEN.**

---

# 18. Renderer-table initialization

## `1560` — `BuildReciprocalProjectionTable`

Builds and 32-bit reciprocal table beginning at `DS:2656`.

Core formula:

```text
table[i] = 0x400000 / i
```

for the bounded table range.

## `1590` — `BuildViewAngleTables`

Builds screen-row/view-angle projection tables from viewport height `DS:4546`.

It computes clamped signed numerators, fixed-point divisions and stores both:
- WORD projection value;
- associated high-byte lookup.

This is the bridge into the VGA/palette/renderer helper family beginning at `15EE`.

**Status: GREEN.**

---

# 19. Function-count correction

Old audit entries inside this band:

- expected/claimed function labels: more than 27 due to decompiler splits;
- real raw functions: **27**.

Definitively delete these stale starts:

```text
00A2
020C
04BE
0C5F
1187
11D2
1236
129A
154B
155A
```

This removes:
- two fake empty/no-op functions;
- one fake exploding-wall function;
- one fake large moving-wall entry;
- three property-table split functions;
- one fake resource/level callback;
- two fake teleport-tail functions.

---

# 20. Byte-map consequence

The whole early band:

`0x0000..0x15ED`

can now be displayed as:

**GREEN-CODE**

with 11 alignment-NOP overlay bytes.

The next genuine function starts at:

`0x15EE`

and begins the VGA/palette/display helper family.

Because many bytes in `0000..15ED` were already GREEN before Pass 34, this pass does
not blindly add all 5,614 bytes to the prior "newly promoted" cumulative metric.

Instead the measurable improvement is:

- continuous raw boundary closure;
- ten false function starts removed;
- the previously weak `04BE` and `0C5F` families absorbed into their real parent
  routines;
- exact wall/object property table boundaries restored;
- teleport tail split repaired.

---

# 21. Next target

Continue at:

`0x15EE`

The next early-core band contains:

- VGA status/retrace helpers;
- palette upload/remap/fade logic;
- planar VGA rectangle/image blitters;
- scaled masked sprite/wall drawing;
- display-mode helpers.

The old audit still contains several weak entries in this neighborhood:

```text
1601
16F5
1715
176A
1921
1988
19BA
1AE1
1B10
```

Raw-boundary repair should be able to remove several more false starts and close the
graphics family as the next contiguous GREEN band.