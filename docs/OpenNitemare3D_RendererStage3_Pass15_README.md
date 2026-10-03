# OpenNitemare3D — Pass 15
## Renderer Stage 3: exact EBD6 texture-U + exact 3940 visibility traversal

Stage 3 removes the two broad wall-renderer bridges explicitly left after Pass 14.

## 1. Exact EBD6 perspective wall coordinate

The checked Win16 1.10 wall loop calls:

```text
EBD6(
    orientation,
    screenX,
    current span accumulator high word,
    perpendicular-coordinate * selected Q10 trig coefficient
)
```

Then the caller:

1. adds the orientation-dependent local wall offset;
2. conditionally negates it;
3. runs the exact `6422` endpoint correction;
4. masks by texture width.

`OriginalTextureUExact.cs` ports this entire chain.

The original `4BF0` selector is reconstructed exactly from:

```text
(1 << octant) & 0x99
```

Thus the EBD6 divisor is:

```text
octants 0,3,4,7 -> cosine
octants 1,2,5,6 -> sine
```

while the perpendicular pre-product uses the opposite trig coefficient, just as
the original 66B0 caller does.

This replaces Stage 2's floating geometric inverse-wall intersection.

## 2. Exact 3940 visibility traversal

`OriginalVisibilityExact.cs` ports both the index semantics from `87B6` and the
actual traversal in `3940`.

Initial sorted-list indices are the first vector whose:

```text
Y1 >= playerY   for orientation 0/1
X1 >= playerX   for orientation 2/3
```

The initial pass interleaves exactly:

```text
orientation 0 forward
orientation 1 backward
orientation 2 backward
orientation 3 forward
```

and stops as soon as the original 3564 behavior has assigned all 304 viewport
columns.

It then derives the world bounds of the selected owners and performs the exact four
continuation loops:

```text
ori0 while vec.Y2 < maxY
ori1 while vec.Y1 > minY
ori2 while vec.X1 > minX
ori3 while vec.X2 < maxX
```

Finally it stores the ±1 expanded bounds corresponding to original `5E80..5E86`.

## 3. Exact orientation-enable octant tables

3940 does not simply traverse all four lists every frame.

It reads four 8-byte tables indexed by the current 45-degree octant:

```text
DS:04C6 orientation 0
DS:04CE orientation 1
DS:04D6 orientation 2
DS:04DE orientation 3
```

Pass 15 therefore adds a second exact binary artifact:

```text
N3D_VISIBILITY_OCTANTS.BIN
```

Do not guess these flags.

Extract both renderer tables from the checked Win16 1.10 executable:

```bat
py extract_nite3w_renderer_tables.py ^
  "C:\N3D\nite3w(10).exe" ^
  "C:\OpenNitemare3D\data"
```

This emits:

```text
N3D_TRIG_Q10.BIN             1440 B
N3D_VISIBILITY_OCTANTS.BIN     32 B
renderer_tables_manifest.json
```

The extractor verifies the known EXE SHA-256 unless explicitly overridden.

## Enable Stage 3

```bat
dotnet run -- ^
  --n3d-renderer-stage3 ^
  --n3d-trig "data\N3D_TRIG_Q10.BIN" ^
  --n3d-visibility-octants "data\N3D_VISIBILITY_OCTANTS.BIN"
```

For parity captures, combine this with the Pass-12 raw indexed-frame hook or merge
the capture changes into the same build.

## What is now exact in the static wall-selection/coordinate path

```text
MAP header class tables
 -> wall/object property generation
 -> 4046 map scan
 -> 3D54/3E82 VEC construction
 -> 4006 merges
 -> 33BA orientation sorting
 -> 87B6 player-relative list indices
 -> 3940 initial/continuation traversal
 -> E798 projection/clipping
 -> 3564 owner conflicts
 -> 6266-style owner run grouping
 -> 6152 span interpolation
 -> EBD6 wall perspective coordinate
 -> 6422 endpoint U correction
 -> 2930/2960 vertical sampling tables
```

## Still not a full pixel-perfect renderer

The broad **static geometry/visibility/U bridges are removed**, but integration
work remains before claiming pixel parity:

- runtime moving-door/panel code must mutate the Stage-3 VEC endpoints rather than
  only OpenNitemare3D Tile state;
- original IMG sequence/frame selection in `66B0` must replace the current direct
  `Tile.textureID` bridge for every special/animated wall class;
- shade remap must be wired;
- sprite/object renderer must use the original slot + wall-visibility path;
- final low-level vertical writer wrapper should be validated against captured
  original frames.

So Stage 3 is the point where the wall renderer's *selection and perspective-U*
architecture is no longer DDA-derived, but runtime resource/dynamic composition is
still incomplete.

## Apply from clean master

```bat
git apply OpenNitemare3D_RendererStage3_from_master_Pass15.patch
```

The patch includes the Pass-14 prerequisite C# files plus the new Stage-3 files.

## Next engineering target

The highest-value next pass is now **dynamic VEC synchronization**:

- paired/moving doors,
- special walls / panels,
- VEC bit/state changes,
- original 66B0 frame/resource selection.

That will let intermediate door frames enter the exact Stage-3 visibility renderer
rather than remaining static MAP-header geometry.