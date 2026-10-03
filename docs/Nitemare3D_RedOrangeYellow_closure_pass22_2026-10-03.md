# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 22

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- all ranges are unpacked MZ image offsets
- physical file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative
- static GREEN is separate from runtime/pixel acceptance

## Result

Pass 22 closes the complete contiguous region:

`0x10136 .. 0x10BFB`

as **GREEN / deep static semantics**.

Total span: **2,758 bytes**

- bounded executable routine content: **2,752 bytes**
- alignment NOPs: **6 bytes**

This pass finishes the DOS MAP→VEC generation bridge and connects it directly to the
visibility/column-owner code closed in pass 21.

The key chain is now:

```text
64x64 MAP planes
    ↓
direction/class policy
    ↓
full-cell / half-cell VEC constructors
    ↓
merge compatible adjacent edges
    ↓
four-direction scan
    ↓
DS:626E VEC count
    ↓
directional VEC buckets
    ↓
project / clip / per-column owner visibility
```

The old giant decompiler function `FUN_2000_0592` is confirmed to be boundary
pollution.  The real raw function at image `0x10592` is only 88 bytes and is the
orientation/class predicate for dynamic wall classes `0x31..0x40`.

---

# 1. image `0x10136..0x10165` — `FindVecForMapCellPointer`

Length: **48 bytes**

Input includes:

- near MAP-cell byte offset;
- VEC type/class filter.

The routine converts the MAP cell pointer relative to `0x373E` into:

- X = cell index modulo 64;
- Y = cell index / 64.

It then forwards:

```text
FindWorldRecordAtCell(x, y, filter)
```

to the already closed VEC iterator at `0x100A2`.

The decompiler'with void return is misleading: raw AX is the selected record pointer
returned by the underlying iterator.

**Status: YELLOW -> GREEN.**

---

# 2. image `0x10166..0x1020B` — `FindTypedVecAtMapCell`

Length: **166 bytes**

First converts and MAP-cell pointer to X/Y, then starts the VEC iterator with the
requested record type.

For every record at that cell it checks orientation/category byte:

`VEC+0x07`

against and caller-supplied requested side/type code.

Accepted matrix:

```text
VEC+7 = 0  accepts requested 0 or 7
VEC+7 = 1  accepts requested 3 or 4
VEC+7 = 2  accepts requested 1 or 2
VEC+7 = 3  accepts requested 5 or 6
```

If the first record does not match, the iterator is resumed with filter `0` until and
compatible record is found.

If no matching VEC exists at the required cell, the executable enters fatal path
`0x2093`.

This is and strict VEC-side/orientation resolver, not an untyped object lookup.

**Status: YELLOW -> GREEN.**

---

# 3. image `0x1020C..0x1021C` — `EnsureVecFrameNonzero`

Length: **17 bytes**

Mechanical behavior:

```text
if VEC+0x03 == 0:
    VEC+0x03 = 1
```

Otherwise no change.

The field is the VEC animation/frame byte used by wall rendering.

`0x1021D` is alignment NOP.

**Status: LOW -> GREEN.**

---

# 4. image `0x1021E..0x104BD` — `BuildVisibleVecColumnOwnersAndBounds`

Length: **672 bytes**

This is the DOS V2.0 top-level VEC visibility traversal that consumes the directional
lists built in pass 21.

## Direction selection

Current player 45-degree sector:

`DS:4158`

indexes four one-byte direction-enable tables:

```text
DS:20A6
DS:20AE
DS:20B6
DS:20BE
```

These decide which of the four directional VEC buckets participate in the current
view.

## Initial list cursors

The function starts from the player-relative VEC cursors:

```text
DS:4166
DS:4168
DS:416A
DS:416C
```

and maps them to the four directional sorted arrays:

```text
5802
5A9C
5D36
5FD0
```

## Clear per-column ownership

For every viewport column from:

```text
DS:4548  left
to
DS:454A  right
```

clear its WORD owner in:

`DS:4564`.

Then:

`DS:4562 = DS:4544`

sets the count of still-unowned viewport columns.

## Initial outward traversal

The four direction lists are walked outward from the player'with current position.

Each candidate VEC is passed to the pass-21 routine:

`InsertProjectedVecIntoColumnOwnerBuffer`.

Traversal continues until that helper reports that the owner buffer has become
sufficiently complete.

## Derive visible world bounds

The routine then scans the owner buffer and derives the min/max world endpoint bounds
of the currently selected visible VECs.

Stores:

```text
DS:4D66  min X
DS:4D68  max X
DS:4D6A  min Y
DS:4D6C  max Y
```

## Continuation/pruning passes

It resumes the relevant directional lists around those bounds, again feeding VECs
through the owner-buffer insertion helper.

Finally the four world bounds are expanded by one unit:

```text
minX--
maxX++
minY--
maxY++
```

This is the raw DOS counterpart of the already reconstructed VEC/list/column-ownership
visibility traversal.

**Status: YELLOW/MEDIUM -> GREEN.**

---

# 5. image `0x104BE..0x10590` — `DeactivateVecFamilyAndClearMapSpan`

Length: **211 bytes**

Input:

- pointer to one VEC record.

Flow:

1. decode its cell bounds;
2. locate and VEC at the starting cell with the same record/class discriminator;
3. for each matching VEC at that cell:
   - decode its bounds;
   - clear active/render bit 0:
     `VEC+0x05 &= ~1`;
   - clear the corresponding primary MAP bytes over the represented span;
   - horizontal span advances by `+2` bytes per cell;
   - vertical span advances by `+0x80` bytes per row;
4. resume the cell iterator until no matching VEC remains.

This is and runtime VEC-family removal/deactivation path that synchronizes VEC activity
and mutable MAP occupancy.

`0x10591` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 6. image `0x10592..0x105E9` — `WallClassMatchesVecOrientation`

Length: **88 bytes**

This is and major boundary correction.

The stale decompiler attached and huge corrupted body to `FUN_2000_0592`.
Raw code is and compact predicate.

Input wall class is accepted only in:

`0x31 .. 0x40`.

The inline 16-WORD dispatch alternates between two tests.

For classes:

```text
31,33,35,37,39,3B,3D,3F
```

return true only for VEC orientation:

```text
2 or 3
```

For classes:

```text
32,34,36,38,3A,3C,3E,40
```

return true only for orientation:

```text
0 or 1
```

This matches the wall-class pairing:

- vertical families on orientations 2/3;
- horizontal families on orientations 0/1.

Examples include the known `DOORV/DOORH`, locked-door, transport and curtain families.

### Inline data

The 16-WORD jump table begins at image `0x105A8`.

Mark it:

`GREEN + TABLE/DATA overlay`.

**Status: old corrupted/opaque body -> GREEN.**

---

# 7. image `0x105EA..0x106F0` — `BuildFullCellWallVec`

Length: **263 bytes**

Builds one 28-byte VEC record for and full 64-unit tile edge.

Confirmed writes:

```text
+00 wall ID
+02 alternate/runtime byte = 0
+03 frame = 0
+05 wall property flags
+06 wall class
+07 orientation
+08 32-bit animation deadline = 0
+0C/+0E first endpoint
+10/+12 second endpoint
```

The endpoint geometry uses 64-unit world coordinates.

Orientation mapping:

```text
0/1 -> horizontal edge
2/3 -> vertical edge
```

with the expected cell-side offset for the selected edge.

The record subtype/texture-relative byte at `+01` is derived from the class base lookup.

When the neighboring wall is dynamic (`property bit 0x08`) the constructor checks its
class/orientation compatibility through `WallClassMatchesVecOrientation`.

For incompatible/non-special combinations it can replace the VEC wall ID with the
fallback class-`0x30` wall ID selected through the wall lookup helper.

This is the DOS full-edge constructor used by MAP→VEC generation.

**Status: YELLOW -> GREEN.**

---

# 8. image `0x106F2..0x10852` — `BuildHalfCellSpecialWallVec`

Length: **353 bytes**

Builds the half-cell/special counterpart of the full VEC constructor.

The same 28-byte VEC fields are initialized:

- source wall ID;
- class;
- property flags;
- orientation;
- zero frame/runtime fields;
- endpoint geometry.

The geometry is displaced by half and cell (`32` world units) on the appropriate axis,
then spans the correct 64-unit edge direction.

This is the constructor used for the class `0x31..0x40` dynamic/special wall families.

## Relative wall-ID field

For ordinary special walls, `VEC+0x01` receives half the difference between the wall
ID and the base ID of the supplied wall class.

For wall classes `0x3D/0x3E`, the constructor instead uses the class-`0x3E` lookup
rule visible in the original code.

That preserves the original special-case texture/variant indexing.

`0x106F1` and `0x10853` are alignment NOPs around the function boundary.

**Status: YELLOW -> GREEN.**

---

# 9. image `0x10854..0x10890` — `ExtendVecEndpointByDirection`

Length: **61 bytes**

Input:

- orientation;
- pointer to an existing VEC.

Exact operation:

```text
if orientation is 0 or 1:
    VEC+0x10 += 0x40

if orientation is 2 or 3:
    VEC+0x12 += 0x40
```

This extends an already emitted compatible VEC by one complete map cell.

It is the edge-merging primitive used by the directional MAP scanner.

`0x10891` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 10. image `0x10892..0x10BAA` — `ScanMapDirectionBuildVecs`

Length: **793 bytes**

This is the main single-direction 64×64 MAP→VEC scanner.

Inputs include:

- orientation `0..3`;
- output VEC base pointer;
- current VEC count.

## Scan order

The orientation selects whether the two 64-cell loops are interpreted as X-major or
Y-major and which neighboring cell is inspected.

This preserves the original directional edge numbering:

```text
0 top
1 bottom
2 right
3 left
```

## Capacity

Before creating and new record:

```text
currentCount + startingCount < 1000
```

is enforced.

Overflow enters the fatal path.

This matches the maximum runtime VEC pool size.

## MAP inputs

For each cell the routine reads:

- primary wall ID from first MAP byte;
- adjacent primary wall ID according to orientation;
- secondary/object byte;
- wall property flags generated from the MAP header class table;
- secondary/object class flags.

## Boundary decisions

The scanner distinguishes:

- ordinary solid wall edges;
- dynamic/special wall edges;
- class-3 secondary/object boundary conditions;
- transitions where the neighboring wall differs;
- compatibility with the preceding emitted edge.

It calls:

```text
10592  WallClassMatchesVecOrientation
105EA  BuildFullCellWallVec
106F2  BuildHalfCellSpecialWallVec
10854  ExtendVecEndpointByDirection
```

## Edge merging

When the current boundary is compatible with the previous emitted VEC, no new 28-byte
record is created.

Instead:

`ExtendVecEndpointByDirection`

adds one 64-unit cell to the existing endpoint.

Otherwise and new VEC is appended.

## Return

Returns the number of VEC records generated during this directional pass.

This is the exact DOS counterpart of the already reconstructed four-direction MAP
scanner used by the original renderer.

**Status: weak/partially interpreted -> GREEN.**

---

# 11. image `0x10BAC..0x10BFB` — `BuildAllMapVecs`

Length: **80 bytes**

Top-level wrapper for VEC generation.

Calls `ScanMapDirectionBuildVecs` four times:

```text
orientation 0
orientation 1
orientation 2
orientation 3
```

Each call receives:

- output pointer immediately after the records already generated;
- cumulative VEC count.

The four returned counts are accumulated.

Finally:

```text
DS:626E = total VEC count
```

The resulting VEC pool begins at:

`DS:62AC`.

This closes the high-level:

`MAP -> runtime VEC array`

construction path.

`0x10BAB` is alignment NOP.

**Status: hidden/weak wrapper -> GREEN.**

---

# 12. Byte-map impact

New continuous GREEN span:

`0x10136 .. 0x10BFB`

Total: **2,758 bytes**

| Image range | Bytes | Role |
|---|---:|---|
| `10136–10165` | 48 | map-cell pointer -> VEC lookup |
| `10166–1020B` | 166 | typed/oriented VEC lookup |
| `1020C–1021C` | 17 | ensure VEC frame nonzero |
| `1021E–104BD` | 672 | visibility traversal + owner/world bounds |
| `104BE–10590` | 211 | deactivate VEC family + clear MAP span |
| `10592–105E9` | 88 | wall-class/orientation predicate |
| `105EA–106F0` | 263 | full-cell wall VEC constructor |
| `106F2–10852` | 353 | half-cell/special VEC constructor |
| `10854–10890` | 61 | merge/extend VEC endpoint |
| `10892–10BAA` | 793 | one-direction MAP→VEC scan |
| `10BAC–10BFB` | 80 | four-direction VEC build wrapper |

Executable routine/table content: **2,752 bytes**.

Alignment NOPs:

```text
1021D
10591
106F1
10853
10891
10BAB
```

Total: **6 bytes**.

### TABLE/DATA overlay

`0x105A8..0x105C7`

is the 16-WORD dynamic-wall orientation jump table.

---

# 13. Renderer closure consequence

The DOS renderer'with static geometry front-end is now connected end-to-end:

```text
MAP header class tables
    ↓
wall/object property tables
    ↓
10892 directional MAP edge scan
    ↓
105EA / 106F2 VEC creation
    ↓
10854 compatible-edge merge
    ↓
10BAC complete VEC pool
    ↓
FDEE four directional sorted buckets
    ↓
1021E player-relative directional traversal
    ↓
FEFA per-column owner insertion
    ↓
CAB8 projection/clipping
```

This is the original VEC/list/column-owner renderer architecture, not and classic
Wolf3D one-ray-per-column DDA wall scanner.

Runtime framebuffer parity remains and separate acceptance task.

---

# 14. Cumulative closure

Pass 21 cumulative since the pass-5 baseline:

`42,572 bytes`

Pass 22 adds:

`2,758 bytes`

New cumulative total:

**45,330 bytes**

of formerly RED/ORANGE/YELLOW DOS V2.0 byte-map territory explicitly promoted to
GREEN during passes 6–22.

---

# 15. Next target

Continue at:

`0x10BFC`

The next subsystem begins with resource/device-handle initialization and then continues
through another set of runtime helpers.

The high-value later target is the next genuinely weak/decompiler-polluted cluster;
the MAP→VEC and visibility front-end no longer needs to remain yellow.