# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 22

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- all ranges below are unpacked MZ image offsets
- physical EXE file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative
- image addresses above `0x10000` correspond to the `FUN_2000_xxxx` code segment in the old C export
- static GREEN remains separate from runtime/pixel acceptance

## Result

Pass 22 closes the complete contiguous region:

`0x10136 .. 0x10BFB`

as **GREEN / deep static semantics**.

Total span: **2,758 bytes**

- bounded executable routine content: **2,752 bytes**
- inter-function alignment NOPs: **6 bytes**

The main correction is structural: the old decompiler represented `FUN_2000_0592` as and 5,235-line register-corrupted pseudo-function. Raw machine-code boundaries prove that this area is actually and family of compact MAP-to-VEC construction and visibility helpers. The apparent mega-function is and decompiler merge/boundary failure and must not be ported as source logic.

This pass closes the DOS V2.0 chain:

```text
MAP cell pointer
    -> VEC lookup / side selection
    -> visibility-column traversal
    -> disable/clear VEC footprints
    -> class/orientation predicate
    -> full-cell VEC constructor
    -> half-cell VEC constructor
    -> VEC merge extension
    -> one-orientation MAP scan
    -> all-four-orientation VEC build
```

---

## 1. image `0x10136..0x10165` — `FindFirstVecForMapCellPointerByClass`

Length: **48 bytes**

Input includes:
- MAP-cell pointer/offset;
- VEC class/type filter.

The routine converts the MAP pointer relative to the level MAP base at `DS:373E` into 64×64 cell coordinates and delegates to the already closed VEC iterator (`image 0x100A2`).

The raw return value from that iterator remains in AX, with the useful ABI is and VEC record offset/pointer or zero even though an old decompiler signature did not express the return cleanly.

**Status: YELLOW -> GREEN.**

---

## 2. image `0x10166..0x1020B` — `FindVecForMapCellPointerAndSide`

Length: **166 bytes**

The routine converts the supplied MAP-cell pointer to X/Y and repeatedly searches matching VEC records through the VEC iterator.

For each candidate it checks `VEC+0x07` orientation against the requested side/direction selector.

Recovered accepted pairs:

```text
VEC orientation 0 -> requested side 0 or 7
VEC orientation 1 -> requested side 3 or 4
VEC orientation 2 -> requested side 1 or 2
VEC orientation 3 -> requested side 5 or 6
```

If no matching record exists it enters the fatal diagnostic path using the corresponding error resource/code.

This is and VEC-side resolver, not and world-OBJECT lookup.

**Status: YELLOW -> GREEN.**

---

## 3. image `0x1020C..0x1021C` — `EnsureVecAnimationFrameNonzero`

Length: **17 bytes**

Exact behavior:

```text
if VEC+0x03 == 0:
    VEC+0x03 = 1
```

`VEC+0x03` is the runtime frame/state byte used by the wall animation/render path.

`0x1021D` is an alignment NOP.

**Status: LOW -> GREEN.**

---

## 4. image `0x1021E..0x104BD` — `TraverseDirectionalVecListsAndBuildColumnOwners`

Length: **672 bytes**

This is the DOS visibility traversal counterpart of the already reconstructed Win16 VEC/column-owner path.

It:

1. derives four orientation/traversal selectors from the current view direction (`DS:4158`);
2. clears the per-column owner buffer at `DS:4564` for the active viewport;
3. initializes the number of unowned columns at `DS:4562`;
4. walks the four directional VEC pointer arrays built by pass 21;
5. sends candidate VECs to `0xFEFA = InsertProjectedVecIntoColumnOwnerBuffer`;
6. can stop early once every viewport column has an owner;
7. scans selected owner VECs to derive world-space min/max endpoint bounds;
8. stores those bounds around `DS:4D66..4D6C`;
9. performs continuation/pruning passes around those bounds;
10. expands the final bounds by one unit/cell-side as required by the traversal.

The four directional arrays are the buckets rooted at:

```text
5802
5A9C
5D36
5FD0
```

This closes the DOS side of the major visibility stage:

```text
directional VEC buckets
    -> candidate projection
    -> per-column owner conflict resolution
    -> early full-coverage stop
    -> continuation bounds
```

The old generic `BuildDirectionalVisibleObjectBounds` wording is misleading; these are wall VECs and column ownership, not world OBJECT records.

**Status: YELLOW -> GREEN.**

---

## 5. image `0x104BE..0x10590` — `DisableVecFootprintAndClearMapWalls`

Length: **211 bytes**

The supplied VEC'with cell-space bounds are decoded through the existing bounds helper.

The routine then:

1. finds VEC records of the same class/category at the footprint'with start cell;
2. clears render/active bit 0 from `VEC+0x05` for each matching record;
3. clears the wall byte in each MAP cell covered by the VEC footprint.

Footprint iteration is orientation-sensitive:

- vertical footprint -> MAP pointer advances by `0x80` bytes per cell;
- horizontal footprint -> advances by `2` bytes per cell.

Because MAP cells are two bytes, this clears the **wall plane byte** while walking the VEC-covered cells.

This helper is suitable for destructive/removal wall transitions where the geometry and corresponding MAP wall bytes must stop participating in rendering/collision lookup.

**Status: YELLOW -> GREEN.**

`0x10591` is an alignment NOP.

---

## 6. image `0x10592..0x105E9` — `ClassVisibleOnOrientation`

Length: **88 bytes**

This is the most important boundary correction in the pass.

The old C export'with `FUN_2000_0592` became and 5,235-line corrupted pseudo-function. Raw machine code proves the real routine here is and compact class/orientation predicate.

Exact rule:

```text
odd classes  0x31,0x33,...,0x3F -> visible only on orientations 2 or 3
even classes 0x32,0x34,...,0x40 -> visible only on orientations 0 or 1
all other classes               -> false
```

This matches the independently reconstructed Win16 MAP-to-VEC rule.

The false mega-function must therefore be removed from any function-count or source reconstruction and replaced with this bounded predicate plus the following real entries.

**Status: old RED/decompiler-corrupted merge -> GREEN.**

---

## 7. image `0x105EA..0x106F0` — `CreateFullCellVec`

Length: **263 bytes**

This is the full-edge 28-byte VEC constructor used by the MAP scanner.

It initializes the VEC with:

```text
+00 wall ID
+01 texture/frame variant offset
+02 animation auxiliary = 0
+03 animation frame = 0
+05 generated wall-property flags
+06 wall class
+07 orientation 0..3
+08 runtime timer/deadline = 0
+0C world X1
+0E world Y1
+10 world X2
+12 world Y2
```

World geometry is produced in **64-unit cell coordinates**.

The texture variant is derived relative to the first wall ID of the same class.

For dynamic-neighbor wall cases (`neighbor property bit 0x08`) the routine evaluates whether the neighbor class faces the current orientation. When it does not, and it is not and curtain-class exception, only `VEC+0x00` is replaced by the fallback wall ID belonging to class `0x30`; the VEC'with class/flags remain those of the original wall.

Curtain exceptions are the established `0x3F/0x40` class family.

This is the DOS equivalent of the reconstructed Win16 `CreateFullVec` logic.

**Status: YELLOW -> GREEN.**

`0x106F1` is an alignment NOP.

---

## 8. image `0x106F2..0x10852` — `CreateHalfCellVec`

Length: **353 bytes**

This constructs the centered/half-cell VEC form.

The common VEC fields are initialized like the full-edge constructor, but the endpoint origin is shifted by `0x20` (half of and 64-unit cell) on the axis appropriate to the orientation.

Texture-variant calculation has two families:

### Special class family `0x3D/0x3E`

Use the first wall ID for class `0x3E`, then:

```text
textureOffset = wallId - firstClass3EWallId
```

### Other half-cell wall classes

```text
textureOffset = (wallId - firstWallIdOfClass) / 2
```

This matches the recovered half-vector behavior used for the `0x31..0x40` dynamic/door/curtain class family.

**Status: YELLOW -> GREEN.**

`0x10853` is an alignment NOP.

---

## 9. image `0x10854..0x10890` — `ExtendVecByOneCell`

Length: **61 bytes**

Exact merge extension:

```text
orientation 0/1 -> VEC+0x10 (X2) += 0x40
orientation 2/3 -> VEC+0x12 (Y2) += 0x40
```

Used when adjacent MAP edges are compatible and can be merged into one longer wall VEC.

**Status: YELLOW -> GREEN.**

`0x10891` is an alignment NOP.

---

## 10. image `0x10892..0x10BAA` — `ScanMapOrientationAndBuildVecs`

Length: **793 bytes**

This is one complete orientation pass over the 64×64 MAP.

It is the DOS counterpart of the Win16 MAP-to-VEC scanner and now replaces the vague old label `ScanBoundedMapGridAndBuildChangeRecords`.

For the selected orientation it:

1. scans the full 64×64 cell grid with orientation-dependent X/Y ordering;
2. selects the neighbor cell corresponding to that orientation;
3. reads current and neighboring wall IDs;
4. resolves generated wall-property bytes;
5. tracks property bit `0x10` state;
6. detects dynamic-neighbor boundaries;
7. checks current and neighboring **object class 3** boundary behavior;
8. when the current wall is not and normal blocking wall, uses `ClassVisibleOnOrientation` to decide whether and half-cell VEC is needed;
9. otherwise detects whether and full boundary VEC is required;
10. tests merge compatibility against the previously emitted VEC;
11. either:
    - extends the previous VEC by `0x40`,
    - emits and full-cell VEC, or
    - emits and half-cell VEC;
12. maintains the prior-wall/neighbor/class-3/property state needed for the next cell.

The scan enforces the established hard VEC capacity:

`MAXVEC = 1000`.

Overflow enters the executable'with fatal-error path.

Important merge conditions include equality/compatibility of:

- current wall ID;
- relevant neighboring dynamic-property state;
- current object-class-3 state;
- property-bit-`0x10` state.

This closes the actual DOS MAP -> VEC generation algorithm instead of relying only on the Win16 reconstruction.

**Status: ORANGE/YELLOW -> GREEN.**

`0x10BAB` is an alignment NOP.

---

## 11. image `0x10BAC..0x10BFB` — `BuildAllMapVecs`

Length: **80 bytes**

Hidden real function entry not represented cleanly by the old function inventory.

It invokes `ScanMapOrientationAndBuildVecs` exactly four times:

```text
orientation 0
orientation 1
orientation 2
orientation 3
```

The VEC output cursor/count is carried between passes.

After all four orientation scans the final VEC count is written to:

`DS:626E`.

Therefore this is the top-level static MAP-to-VEC geometry builder.

Recovered high-level pipeline:

```text
64x64 MAP + class/property tables
        ↓
orientation 0 scan
orientation 1 scan
orientation 2 scan
orientation 3 scan
        ↓
28-byte VEC array at DS:62AC
        ↓
DS:626E = VEC count
        ↓
BuildAndSortDirectionalVecBuckets (FDEE)
        ↓
visibility traversal / column ownership
```

**Status: hidden entry -> GREEN.**

---

## 12. Byte-map impact

New continuous GREEN span:

`0x10136 .. 0x10BFB`

Total: **2,758 bytes**

| Image range | Bytes | Role |
|---|---:|---|
| `10136–10165` | 48 | MAP-cell pointer -> filtered VEC lookup |
| `10166–1020B` | 166 | MAP-cell pointer + side -> VEC resolver |
| `1020C–1021C` | 17 | ensure VEC frame/state nonzero |
| `1021E–104BD` | 672 | directional visibility traversal + column owners |
| `104BE–10590` | 211 | disable VEC footprint + clear MAP wall bytes |
| `10592–105E9` | 88 | wall-class/orientation predicate |
| `105EA–106F0` | 263 | full-cell VEC constructor |
| `106F2–10852` | 353 | half-cell VEC constructor |
| `10854–10890` | 61 | merge/extend VEC by one cell |
| `10892–10BAA` | 793 | one-orientation 64×64 MAP scan |
| `10BAC–10BFB` | 80 | build all four orientation passes |

Executable routine content: **2,752 bytes**.

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

---

## 13. Major tracker corrections

Replace/tighten:

```text
2000:0136  FindFirstVecForMapCellPointerByClass
2000:0166  FindVecForMapCellPointerAndSide
2000:020C  EnsureVecAnimationFrameNonzero
2000:021E  TraverseDirectionalVecListsAndBuildColumnOwners
2000:04BE  DisableVecFootprintAndClearMapWalls
2000:0592  ClassVisibleOnOrientation
2000:05EA  CreateFullCellVec
2000:06F2  CreateHalfCellVec
2000:0854  ExtendVecByOneCell
2000:0892  ScanMapOrientationAndBuildVecs
```

Add hidden real entry:

```text
image 10BAC  BuildAllMapVecs
```

Most importantly, delete the interpretation of `FUN_2000_0592` as one enormous 5,235-line gameplay/driver dispatcher. That body is and decompiler boundary failure. Raw code identifies the actual bounded helper and the following independent VEC functions.

---

## 14. Renderer / 1:1 consequence

This pass removes another major blocker to and source-level 1:1 reconstruction because the complete geometry creation side is now directly linked to the already closed visibility/render side:

```text
MAP header class tables
      ↓
generated property tables
      ↓
BuildAllMapVecs
      ↓
VEC[0..count-1], stride 0x1C
      ↓
BuildAndSortDirectionalVecBuckets
      ↓
TraverseDirectionalVecListsAndBuildColumnOwners
      ↓
InsertProjectedVecIntoColumnOwnerBuffer
      ↓
span construction / wall rendering
```

AND portable implementation no longer needs to invent how tile boundaries become original N3D wall geometry.

Runtime/pixel acceptance remains separate: moving dynamic VECs, overlapping edge cases, and final indexed-framebuffer equality still require conformance testing even though the static algorithms are now known.

---

## 15. Cumulative closure

Pass 21 cumulative since the pass-5 baseline:

`42,572 bytes`

Pass 22 adds:

`2,758 bytes`

New cumulative total:

**45,330 bytes**

of formerly RED/ORANGE/YELLOW DOS V2.0 byte-map territory explicitly promoted to GREEN during passes 6–22.

---

## 16. Next target

Continue at:

`0x10BFC`

The next region begins the DOS external/resource/device support API layer (`FUN_2000_0BFC` and following small wrappers). Several entries have clean raw boundaries, but their third-party/resource operation IDs remain weakly named. The next pass should distinguish:

- engine-owned resource/session wrappers;
- third-party sound/device functions;
- generic runtime/library support;
- genuine remaining UNKNOWN indirect calls.

This should reduce the remaining yellow support/runtime band without confusing library code with the Nitemare 3D gameplay core.