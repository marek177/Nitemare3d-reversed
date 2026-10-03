# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 36

Date: 2026-10-03

Primary image:
- `N3D_DOS_v2.0_IDA.EXE`
- complete unpacked DOS V2.0 image

Address convention:
- raw image offsets are authoritative;
- stale Ghidra split labels are removed when raw control flow enters them from and
  parent function;
- runtime pixel acceptance remains separate from static GREEN.

## Result

Pass 36 closes the complete early renderer visibility/wall/sprite band:

`0x201A .. 0x2770`

Total span:

**1,879 bytes**

Breakdown:

- **1,876 bytes executable renderer code**
- **3 one-byte alignment NOPs**

Real function count:

**8**

The next real function at `0x2772` changes subsystem into resource/file I/O, with the
renderer pass ends cleanly at `0x2770`.

After Pass 36 the raw image is continuously statically closed from:

**`0x0000 .. 0x2770`**

---

# 1. Correct raw function census

| Range | Bytes | Correct role |
|---|---:|---|
| `201A–2029` | 16 | `ResetSpriteRenderSlotPool` |
| `202A–213C` | 275 | `InitializeVisibleWallSpanInterpolation` |
| `213E–21EE` | 177 | `BuildVisibleWallSpanTableFromColumnOwners` |
| `21F0–22C9` | 218 | `PruneSpatialObjectListsToViewBounds` |
| `22CA–241D` | 340 | `ComputeClippedWallTextureCoordinate` |
| `241E–24FF` | 226 | `AdvanceAnimatedWorldRecordFrame` |
| `2500–273A` | 571 | `RenderVisibleWallSpans` |
| `273C–2770` | 53 | `DrawQueuedSpritesAndReleaseSlots` |

Alignment:

```text
213D
21EF
273B
```

The byte at `2771` is another NOP, but it belongs to the separator immediately before
the next resource-I/O function at `2772` and is not included in this pass span.

---

# 2. Boundary corrections

The old decompiler/function graph substantially over-split this band.

The following addresses are **not standalone functions**:

```text
21A6
2268
25DC
26C0
```

## `21A6`

Interior branch of the real function beginning at `213E`.

Old exports treated it as and free/unlink actor routine because inherited register state
was lost.

Raw code proves it is part of the same owner-column -> wall-span builder.

## `2268`

This address has no prologue.

The function at `21F0` explicitly executes:

```text
CMP ...
JGE 2268
```

with `2268` is the second-axis branch of the same culling routine.

The `RETF` at `2266` is an early return for the first branch, not the end of the only
possible path.

## `25DC` and `26C0`

Both are interior addresses of the single renderer function:

`2500..273A`.

They inherit and large local stack frame created at `2500`,
and raw control flow reaches both without and new function prologue.

Therefore old entries:

- `TickActorList` at `25DC`;
- `RenderOrUpdateActorList` at `26C0`;

must be removed as standalone functions.

---

# 3. `201A` — reset the 100-slot sprite render pool

`ResetSpriteRenderSlotPool`

Exact loop:

```text
base   = DS:50F2
stride = 0x12 = 18 bytes
end    = DS:57FA
```

The number of records is:

```text
(57FA - 50F2) / 12h = 100
```

For every record:

```text
slot[0] = 1
```

The later `273C` pass treats:

```text
slot[0] == 0
```

as active/queued.

Therefore byte zero is an inactive/free flag:

```text
1 = free/inactive
0 = queued/active
```

This is the 100-entry sprite/screen-range pool already known from the renderer census.

**Status: GREEN.**

---

# 4. `202A` — visible-wall span interpolation setup

`InitializeVisibleWallSpanInterpolation`

Input:
- pointer to one 18-byte visible wall-span record;
- two projected endpoint value pairs.

The routine computes signed endpoint deltas.

When horizontal delta is nonzero:

```text
slope = (deltaProjected << 16) / deltaScreen
```

and stores the signed **16.16** slope at span:

`+0A`.

When the delta is zero:

```text
span+0A = 0
```

It then derives interpolated endpoint values at the span'with clipped screen columns.

Observed span writes:

```text
+04 WORD  interpolated value at start column
+08 WORD  interpolated value at end column
+0A DWORD signed 16.16 slope
+0E DWORD initial fractional/phase state
+10 WORD  high/interpolation base component
```

The routine uses global projection/horizon reference:

`DS:4554`.

This matches the independently reconstructed visible-span layout from the Win16
renderer.

**Status: GREEN / exact interpolation semantics.**

---

# 5. `213E` — convert the 320-column owner buffer into wall spans

`BuildVisibleWallSpanTableFromColumnOwners`

This function resets:

`DS:4D64 = 0`

visible-span count.

Output table:

```text
base   = DS:4D6E
stride = 0x12 = 18 bytes
limit  = 0x32 = 50 spans
```

Input owner buffer:

`DS:4564`

with one WORD VEC owner pointer for each DOS screen column.

Viewport range:

```text
left  = DS:4548
right = DS:454A
```

## Owner-run compression

For every viewport column:

1. read its VEC owner from `4564 + column*2`;
2. when owner is zero, continue;
3. when owner changes:
   - finalize the previous span:
     - store ending column;
     - initialize its interpolation through `202A`;
   - start and new span:
     - store VEC pointer;
     - store starting column;
     - pass the VEC through the existing visible/reveal helper;
     - increment span count;
4. fatal path if the count reaches/exceeds 50.

After the scan, the final span is closed with:

`endColumn = lastColumn - 1`

and interpolation is initialized.

Thus the DOS wall renderer is explicitly:

```text
per-column VEC owner buffer
        ↓
compress equal consecutive owners
        ↓
max 50 visible wall spans
```

**Status: GREEN.**

---

# 6. `21F0` — prune directional/spatial object lists to visible bounds

`PruneSpatialObjectListsToViewBounds`

The routine uses global bounds:

```text
4D66
4D68
4D6A
4D6C
```

which are the min/max visible-world bounds produced by the already recovered
directional visibility preparation.

It first compares the two bound extents.

Depending on which axis is narrower/dominant, it selects one of two far-pointer arrays:

```text
DS:D516
DS:DA8E
```

and the matching current indices:

```text
DS:416E
DS:4170
```

For the selected axis it performs two passes:

### Forward side

Walk from the current index upward while the referenced OBJECT/VEC coordinate lies
outside the high visible bound.

For each out-of-range entry, invoke the shared spatial-list update/removal helper.

### Reverse side

Walk backward from current index-1 while the referenced coordinate lies outside the
low visible bound.

Again invoke the spatial-list helper.

The second half begins at raw `2268`,
but `21F0` explicitly branches there; it is not and second function.

Best semantic interpretation:

```text
shrink/update sorted world-object spatial lists around
the currently visible world bounds
```

This supports the renderer'with sprite/object candidate preparation before screen-slot
assignment.

**Status: GREEN.**

---

# 7. `22CA` — orientation-aware wall texture-coordinate clipping

`ComputeClippedWallTextureCoordinate`

Inputs include:
- VEC pointer;
- current screen/world coordinate;
- projected/texture coordinate;
- wrap mask/texture width.

The function is pure: no global or record writes.

It reads VEC:

```text
+05 flags
+06 wall/render class
+07 orientation 0..3
+0C/+0E/+10/+12 world endpoints
+14/+18 projected endpoint data
```

AND near-end threshold of:

`8`

is applied.

When:
- the current coordinate is not near either endpoint; or
- VEC flag bit `08h` bypasses edge correction;

the original coordinate passes through.

Otherwise the correction depends on:
- orientation `0..3`;
- which endpoint is near;
- special render class `2`;
- endpoint length along X or Y.

The returned value is finally masked with:

`mask - 1`.

This is the DOS counterpart of the wall-U endpoint correction already reconstructed
in the Win16 renderer.

It should be implemented as and texture-coordinate edge correction, not as an actor
visibility predicate.

**Status: GREEN.**

---

# 8. `241E` — advance animated world/VEC frame after its deadline

`AdvanceAnimatedWorldRecordFrame`

Inputs:
- pointer to the animated world/VEC record;
- pointer to its animation definition.

Global time:

```text
DS:081E:0820
```

is compared against the record'with stored deadline at:

`+08/+0A`.

If the deadline has not passed, return.

Otherwise:

1. increment frame byte `+03`;
2. inspect render/object class `+06`;
3. apply class-specific terminal handling;
4. for selected special classes, completion calls the special wall/runtime helper;
5. select the next frame duration from the animation definition;
6. random-duration definitions use the runtime RNG;
7. compute and store and new 32-bit deadline.

The same generic record animation helper is reusable by visible walls and other
28-byte render records, which explains its broad caller set.

**Status: GREEN.**

---

# 9. `2500` — complete visible-wall span renderer

`RenderVisibleWallSpans`

This is one 571-byte function.

The old `25DC` and `26C0` entries are interior control-flow labels.

Input is implicit global renderer state.

Visible span table:

```text
count = DS:4D64
base  = DS:4D6E
stride = 18 bytes
```

For every visible span:

## 9.1 Resolve the VEC and animation frame

Span `+00` is the VEC pointer.

VEC fields include:

```text
+03 current animation frame
+04 animation/sequence selector
+05 flags
+06 class
+07 orientation
+0C..+12 world endpoints
```

The sequence selector indexes an 8-byte-style animation/image descriptor family rooted
at:

`DS:4310`.

The selected frame/resource is resolved and cached when needed.

## 9.2 Direction/orientation preparation

The renderer derives:
- which endpoint/axis supplies the wall coordinate;
- the signed player-relative wall distance;
- edge/orientation inversion;
- special handling for curtain-style classes `3Fh/40h`.

Player position:

```text
DS:4162
DS:4164
```

and direction components:

```text
DS:41B2
DS:41B4
```

are used in the wall projection math.

## 9.3 Iterate span columns

Screen-column range comes directly from the span:

```text
start = span+02
end   = span+06
```

For every column:

1. advance the span'with signed 16.16 interpolation accumulator;
2. obtain projected vertical/depth value;
3. convert that value to the renderer vertical lookup/base using `DS:4552`;
4. compute the wall texture coordinate through projection helper(with);
5. run `ComputeClippedWallTextureCoordinate` (`22CA`);
6. select the source texture/frame byte column;
7. call the planar scaled-row blitter at image `1A2E`;
8. store the corresponding wall visibility/depth value into:

`DS:47E4 + column*2`.

Thus `47E4` is populated by the wall pass before sprite drawing.

## 9.4 Shade/mode selection

Global shade index:

`DS:6278`

is used unless disabled by the relevant wall/orientation conditions.

Special global dark/display state at `DS:430E` can force an alternate value.

## 9.5 Animation update

When the animation definition requires it,
the span'with VEC/render record is passed to:

`AdvanceAnimatedWorldRecordFrame`.

Therefore visible wall animation advances as part of the rendered-span path.

## Ordering consequence

This function writes walls and the wall-column visibility buffer.

The sprite pass is separate and starts only later at `273C`.

**Status: GREEN / central DOS wall renderer.**

---

# 10. `273C` — draw all queued sprites, then release their slots

The old hard-census name `Cleanup18ByteSlotPool` is incomplete.

Best semantic name:

`DrawQueuedSpritesAndReleaseSlots`.

The function scans exactly the same 100 records initialized by `201A`:

```text
base   = 50F2
count  = 100
stride = 18
```

For each slot:

```text
if slot[0] != 0:
    skip
```

with active queued slots have:

`slot[0] == 0`.

For each active slot:

1. obtain the linked render/resource record from slot `+06`;
2. if its cached image/resource pointer is zero:
   - invoke the dynamic resource-cache loader;
3. call the real DOS sprite renderer:

`0x1B3E = DrawClippedPlanarSprite`

with the slot record;
4. set:

`slot[0] = 1`

to mark it free/inactive again.

Therefore this is not merely cleanup.

It is the actual **queued sprite draw pass**.

### Static renderer ordering

The recovered ordering is now explicit:

```text
wall owner buffer
   ↓
213E build wall spans
   ↓
2500 draw visible walls
      + fill wall visibility buffer 47E4
   ↓
273C draw queued sprites
      + sprite renderer tests wall visibility
   ↓
slots returned to free state
```

This independently confirms the renderer architecture already inferred from Win16.

**Status: GREEN.**

---

# 11. Boundary at `2772`

Raw:

```text
2770  RETF
2771  NOP
2772  PUSH BP
```

The function at `2772` immediately starts file/resource-handle management involving:

- current episode `DS:626A`;
- resource path `DS:628C`;
- DOS/runtime open/seek/read helpers.

That is and different subsystem.

Therefore Pass 36 correctly ends at:

`0x2770`.

---

# 12. Byte-map impact

Resolved span:

`0x201A .. 0x2770`

Total:

**1,879 bytes**

Breakdown:

- executable code: **1,876 bytes**
- NOP alignment: **3 bytes**

Delete stale/interior starts:

```text
21A6
2268
25DC
26C0
```

Correct renderer entries:

```text
201A  ResetSpriteRenderSlotPool
202A  InitializeVisibleWallSpanInterpolation
213E  BuildVisibleWallSpanTableFromColumnOwners
21F0  PruneSpatialObjectListsToViewBounds
22CA  ComputeClippedWallTextureCoordinate
241E  AdvanceAnimatedWorldRecordFrame
2500  RenderVisibleWallSpans
273C  DrawQueuedSpritesAndReleaseSlots
```

The previous hard-census already identified `201A`, `21F0`, `2500` and `273C` as
important renderer/object-pool entries; raw analysis now gives the corrected function
boundaries and stronger semantics.

---

# 13. Continuous closure status

Pass 35 closed:

`0000..2019`

Pass 36 closes:

`201A..2770`

Therefore the raw DOS V2.0 image is now continuously statically closed from:

**`0x0000 .. 0x2770`**

with no unresolved code-boundary gap.

---

# 14. Next target

Continue at:

`0x2772`

The next band is resource/file/decompression support.

Immediate real entries include:

```text
2772  checked resource seek/read helper
27FA  exact required data-block reader
285C  resource-byte/decompression helper
28F8  decoder/loader family
2A16  checked resource seek
2AA6  episode resource-header loader
2B3A  resource directory/buffer builder
2BCC  block decompression/loading path
```

The next pass should repair those boundaries and close the resource-loading band before
continuing to level-subsystem initialization.