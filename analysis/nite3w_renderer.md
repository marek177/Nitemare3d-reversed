# NITE3W.EXE renderer audit — consolidated 2026-09-23

This note records the current renderer reconstruction from the supplied Windows 3.1 executable. Addresses use logical NE `segment:offset` notation where available; Ghidra auto-names are retained for newly traced helpers. The authoritative target is NITE3W.EXE V1.10, SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.

## Result

The original renderer is **not** Wolfenstein 3-D's one-grid-ray-per-screen-column DDA. It is a custom 2.5D wall-vector/span renderer with per-column wall ownership and a separate projected-sprite queue.

Current reconstructed pipeline:

```text
MAP 64x64
   |
   v
extract exposed tile boundaries
   |
   v
merge adjacent compatible boundaries
   |
   v
VEC[0..999] -- 28-byte wall-vector records
   |
   v
4 x orientation-specific VECLIST[333] of far pointers
   |
   v
sort horizontal lists by Y / vertical lists by X
   |
   v
per frame:
  traverse candidate VECs
  -> world-to-camera transform
  -> near clipping
  -> perspective-project endpoints
  -> owner[x] = winning VEC pointer
  -> coalesce equal owner[x] runs into wall spans
  -> ceiling/floor
  -> textured wall-column rasterization
  -> per-column wall silhouette/occlusion values
  -> object projection/culling
  -> 100-entry projected-sprite queue
  -> sprite draw clipped by wall information
  -> 320x200 8-bit framebuffer
```

This conclusion is instruction-backed. Earlier notes that treated MAP->VEC or the four sorted lists as still unknown are superseded by the later audit below.

## Evidence policy

- **CONFIRMED / VERIFIED_EXE**: direct instruction, relocation or data-flow evidence.
- **STRONG**: several instructions establish the role but not every semantic name.
- **PARTIAL**: structure/path established, exact high-level meaning incomplete.
- **OPEN**: deliberately unresolved; no behavior invented.

---

# 1. Frame renderer call chain

Recovered frame ordering:

```text
3:D78C / Ghidra frame orchestrator
  4:3940 / FUN_1018_3940   traverse four sorted vector lists
    4:3564 / FUN_1018_3564 project/clip candidate and update owner[x]
      3:E798 / FUN_1010_E798 transform, near-clip and project VEC
  3:6266 / FUN_1010_6266   coalesce owner[x] runs into wall spans
    3:6152 / FUN_1010_6152 initialize span interpolation
  3:3DB8                   ceiling/floor backend wrapper
    3:3612                 WinG linear framebuffer fill
  3:66B0 / FUN_1010_66B0   wall-span rasterizer
    3:EBD6 / FUN_1010_EBD6 perspective/orientation mapping helper
    3:6422 / FUN_1010_6422 texture-U / special-wall helper
    3:3E44                 wall-column backend wrapper
      3:366A               WinG textured-column drawer
    3:65A6 / FUN_1010_65A6 animation/resource-side helper
  3:6348                   visible-object integration/order
  object projection path includes FUN_1010_CC7C
  3:6914 / FUN_1010_6914   projected-sprite queue consumer
    3:3F80                 sprite backend wrapper
      3:374E               WinG depth/occlusion-tested sprite drawer
```

Presentation occurs elsewhere through WinG bit/stretch-blit paths. `3:D78C` should not be described as directly importing/presenting the DIB.

---

# 2. MAP -> VEC construction

## 2.1 Four passes

`FUN_1018_4370` calls `FUN_1018_4046` four times with orientation parameters 0,1,2,3. The caller advances by `count * 0x1C`, proving the destination records are 28 bytes each.

`FUN_1018_4046` scans the 64×64 map, identifies exposed tile boundaries and emits vectors. Adjacent compatible boundaries are merged into longer vectors through the related extension helper.

The routine checks the total vector count against `0x03E8 = 1000` and reaches the original `MAXVEC exceeded` path on overflow.

## 2.2 World geometry

One tile is exactly 64 world units. Recovered orientation construction:

| Orientation | Segment |
|---:|---|
| 0 | `(x,y) -> (x+64,y)` top/horizontal edge |
| 1 | `(x,y+64) -> (x+64,y+64)` bottom/horizontal edge |
| 2 | `(x+64,y) -> (x+64,y+64)` right/vertical edge |
| 3 | `(x,y) -> (x,y+64)` left/vertical edge |

The merge helper extends x2 or y2 by another 64 units according to orientation.

This is important architecturally: the map is converted into wall boundary segments first. The renderer does not perform a fresh Wolf3D-style tile DDA hit search for every screen column.

---

# 3. Recovered 28-byte VEC layout

Current strongest layout:

```text
+00  uint8   wallId
+01  int8    texture/offset-like value         PARTIAL
+02  uint8   animation auxiliary value         PARTIAL
+03  uint8   animation frame/sub-index         STRONG
+04  uint8   texture/resource set              STRONG
+05  uint8   flags
+06  uint8   renderClass
+07  uint8   orientation                       CONFIRMED, 0..3
+08  uint32  timer/runtime value               PARTIAL
+0C  int16   x1                                CONFIRMED
+0E  int16   y1                                CONFIRMED
+10  int16   x2                                CONFIRMED
+12  int16   y2                                CONFIRMED
+14  int16   screenX1                          CONFIRMED
+16  int16   projectedY1_Q4                    CONFIRMED
+18  int16   screenX2                          CONFIRMED
+1A  int16   projectedY2_Q4                    CONFIRMED
```

The projection stage overwrites the projected endpoint fields each frame.

## Flags currently visible in renderer logic

- `0x01` — active/renderable path, high confidence.
- `0x04` — special boundary/merge/render behavior; exact semantic label open.
- `0x08` — special geometric/wall behavior; exact semantic label open.
- `0x10` — masked/transparent or sprite-occlusion-related special handling; partial.
- `0x20` — **texture U flip**, high confidence from the wall raster path.

## renderClass

Values `2`, `0x3F`, `0x40` have special branches in the renderer. These must be mapped to exact `WALLS.*` classes via the property/class tables before assigning visible names.

---

# 4. Four VECLIST arrays and the 333-vs-1000 question

`FUN_1018_3430` distributes pointers to VEC records according to `VEC+07 orientation` into four far-pointer arrays.

Counts:

```text
0x697A
0x697C
0x697E
0x6980
```

Array bases:

```text
0x6982
0x6EB6
0x73EA
0x791E
```

The spacing between adjacent bases is exactly:

```text
0x534 = 1332 = 333 * 4 bytes
```

Therefore each orientation list stores up to 333 **4-byte far pointers**, not 333 VEC records.

The real vector pool remains `1000 * 28` bytes.

Sorting behavior:

- horizontal VEC lists sort by Y;
- vertical VEC lists sort by X.

This resolves the earlier `MAXVECLIST=333` mystery: it is a capacity for each orientation-specific spatial pointer index, not the total vector population.

---

# 5. Framebuffer and viewport

## WinG surface

The WinG path creates a top-down 320×200 8-bit DIB and clears exactly 64,000 bytes.

Confirmed:

- framebuffer width: 320;
- framebuffer height: 200;
- row stride: 320 bytes;
- palette-indexed pixels.

## Normal 3-D viewport

`FUN_1010_5208` derives the normal game viewport:

```text
xMin = 8
xMax = 311
width = 304

yMin = 4
yMax = 155
height = 152

centerX = 160
centerY = 80
centerY_Q4 = 1280
```

These values explain why full-screen structures are 320 entries wide while only the active 304-column 3-D region is normally traversed.

---

# 6. Per-column wall owner table at 0x53FE

Base: `0x53FE`.

Layout:

```text
320 entries * 4-byte far pointer = 1280 bytes
0x53FE + 320*4 = 0x58FE
```

`FUN_1018_3940` clears the active viewport portion and initializes the count of uncovered screen columns.

`FUN_1018_3564`:

1. projects/clips a candidate VEC;
2. computes its projected X interval;
3. visits owner slots across that interval;
4. if a slot is empty, writes the VEC far pointer and decrements the uncovered-column count;
5. if a slot is occupied, applies geometry-dependent conflict/hidden-surface logic to determine the winner.

When every active viewport column is covered, traversal can stop early. This is a major performance behavior and one of the reasons the renderer does not need a classic DDA ray for every x coordinate.

### Resolved by raw-assembly audit (2026-09-23)

The occupied-slot decision in `FUN_1018_3564` is now translated from CS 1018:3564. It has eight cross-orientation cases, each using strict signed 16-bit endpoint comparisons; ties and same-orientation cases retain the old owner. The exact old/new orientation matrix and the C++ helper are recorded in [the dated raw-assembly pass](nite3w_renderer_2026-09-23.md) and `src/renderer/Win16WallRasterCore.hpp`.

The function still has separate viewport clipping, empty-slot insertion, and owner-count logic. The recovered helper covers only the occupied-slot decision.

---

# 7. owner[x] -> wall spans

`FUN_1010_6266` scans the owner array and coalesces consecutive columns that reference the same VEC into a compact wall-span list.

Confirmed:

- span count global `0x5E7E`;
- span array base `0x5E88`;
- stride `0x14 = 20` bytes;
- maximum 50 records;
- overflow path corresponds to `MAXSEG exceeded`.

Current structural reconstruction:

```text
+00  VEC far pointer
+04  xStart
+06  endpoint/interpolation value
+08  xEnd
+0A  endpoint/interpolation value
+0C  32-bit interpolation step
+10  32-bit accumulator/current interpolation value
```

`FUN_1010_6152` initializes the deltas/divisions. `FUN_1010_66B0` increments the accumulator by the step for each screen X. The high/current word is used in Q4-like projected wall geometry.

The raw-assembly port of the 20-byte span layout and `FUN_1010_6152` initializer is in `src/renderer/Win16WallRasterCore.hpp` (`WallSpanRecord` and `initializeSpanInterpolation()`). It reproduces signed 16.16 slope division, span-endpoint interpolation and the starting accumulator. The isolated cases are covered by the dedicated CMake test; the coalescer and camera/projection path still have to feed this record in the runtime.

This corrects older notes that speculated a 52-byte renderer record.

---

# 8. Projection and clipping

## View angle

`FUN_1010_E516(angle)`:

- normalizes angle to 0..359;
- uses 45-degree sectors (`0x2D`);
- updates direction/trig globals around `0x4C46/0x4C48`.

## Dynamic projection constants

`FUN_1010_E4B2` computes projection-related globals around:

```text
0x3A6A
0x3A6E
0x3A72
0x3A76
```

It uses integer constants including `0x5000`, `0x2EE0`, `0x8340`; `0x3A72` is derived by shifting another projection value by 4.

For the normal 304-pixel viewport, one recovered focal-like term is approximately 178 pixels. If interpreted through a conventional pinhole model this corresponds to roughly 81 degrees horizontal FOV. That angle is a mathematical reconstruction, **not** a literal named `FOV=81` constant in the binary.

## VEC endpoint projection

`FUN_1010_E798(VEC*)`:

- subtracts player/camera world coordinates from both endpoints;
- applies integer camera rotation using the recovered direction components;
- performs near clipping/interpolation;
- saturates/project-clamps extreme X cases;
- writes projected endpoint fields `+14..+1A`.

Near-plane/clamp anchor: `0x4000`.

A segment with only one endpoint behind/too near is clipped rather than simply rejected.

Vertical projection uses a Q4-like result around `centerY_Q4`; horizontal projection uses the recovered focal-like term and `centerX`.

---

# 9. Second per-column table at 0x58FE

Base: `0x58FE`.

Layout:

```text
320 entries * 2 bytes
```

The wall rasterizer writes one value per drawn screen column. Sprite/object projection and sprite drawing read this table for occlusion decisions.

The previous shorthand name `depth buffer` is useful descriptively but can be misleading. The table stores a projected wall silhouette/height/occlusion quantity used in screen-space comparisons; current evidence does **not** justify describing it as a conventional metric distance Z-buffer.

`FUN_1010_CC7C` samples it around multiple horizontal points of a projected object during culling/insertion.

---

# 10. Wall rasterization

`FUN_1010_66B0` iterates the 20-byte spans.

Recovered behavior includes:

- read VEC `+04` as an index into a descriptor table around `0x51AC`;
- read VEC `+03` as frame/sub-index inside another resource descriptor level;
- lazy-load resource if a graphics pointer is null via the image/resource loader path;
- use VEC orientation and flag `0x20` to choose U direction;
- special mapping changes for `renderClass 0x3F/0x40`;
- call `FUN_1010_EBD6` to derive a perspective/orientation wall mapping parameter;
- call `FUN_1010_6422` for texture-U / special-wall column selection;
- update `0x58FE[x]`;
- call lower-level wrapper `3:3E44` as texture-column/draw jobs change.

## WinG wall-column core

`3:366A` is the linear framebuffer column drawer. Structural pseudocode:

```c
source = texture + (texture_x << 6); // 64 samples in audited path
dest = framebuffer + y * 320 + x;
while (pixels--) {
    *dest = translated ? translation[*source] : *source;
    dest += 320;
    fraction += fraction_step;
    source += integer_step + carry(fraction);
}
```

This proves 64-sample column source organization for this raster path. It does not prove that every IMG resource is 64×64.

## 16.16 sampler tables (raw-assembly pass)

`FUN_1010_2930` initializes 511 increments as `floor(0x400000 / n)`, giving a 16.16 source-texture step for each projected height n. A second initializer at CS 1010:2960, called from CS:5259, fills the clipped-start byte/fraction tables at DS:0x2C7F and DS:0x2E80. Its exact divide-then-shift order and address formulas are documented in [the dated raw-assembly pass](nite3w_renderer_2026-09-23.md). The word at DS:0x53E2 is an input; its standalone semantic label remains open.

The new `src/renderer/Win16WallRasterCore.hpp` implements these tables, texture-U correction and WinG indexed-column stepping. DOS E-20 `FUN_1000_1560` and `FUN_1000_1590` independently use the same step and clipped-start formulas at build-specific addresses. The column function operates on an already-selected texture column and does not replace the full scene renderer.

---

# 11. Ceiling/floor

`3:3DB8` is a backend wrapper; its WinG branch reaches `3:3612`.

The linear fill uses the same 320-byte row stride and fills the viewport with palette-indexed ceiling/floor values.

Recovered default palette indexes:

- floor: `0x0C`;
- ceiling: `0x11`.

These values are also serialized at the tail of USER.SAV.

Open question: whether every original rendering mode/level uses only solid fills or whether alternate environment paths can change this behavior beyond palette selection.

---

# 12. Projected object/sprite queue at 0x6270

The sprite/object pass uses a separate fixed array:

- base `0x6270`;
- 100 records;
- stride `0x12 = 18` bytes.

`FUN_1010_CC7C` performs projection/culling and builds queue commands. Recovered stores support a layout containing:

```text
+00 active/free marker
+02 world-object pointer/reference
+06 sprite/resource descriptor
+08 screenLeft
+0A screenRight
+0C screenTop
+0E screenBottom
+10 projectedBottomQ4 / ordering value
```

Some field names remain PARTIAL because exact pointer/descriptor types are still being refined.

Queue placement is based on a projected screen/depth-like bucket derived from vertical position. If the preferred slot is occupied the code searches nearby slots. If no slot can be found the executable emits:

```text
Too many objects on screen
```

`FUN_1010_6914` scans all 100 18-byte records, lazy-loads sprite resources if needed, draws active commands through `3:3F80 -> 3:374E`, and resets/free-marks them.

## Sprite transparency

The audited WinG sprite drawer treats palette index `0x29` as transparent and skips writes for that sample.

This transparency value belongs to the recovered runtime sprite raster path; separate archive/export tools must not automatically assume every image type has identical transparency rules.

---

# 13. Special walls, animation and global 0x7E60

## FUN_1010_6422

The branch structure is now recovered from the executable: it bypasses endpoint correction for columns away from both projected ends or when VEC flag `0x08` is set; near endpoints it applies orientation-dependent signed segment-length corrections, including a special `renderClass == 2` path for orientations 0 and 3. The exact branch summary is in [the dated raw-assembly pass](nite3w_renderer_2026-09-23.md).

DOS E-20 `FUN_1000_22CA` independently reproduces the same endpoint, orientation and render-class branch family. The remaining uncertainty is the mapping from these numeric classes/flags to all named WALLS resources and pixel-level outcomes, which needs original-frame comparisons.

## FUN_1010_65A6

The instruction-level state update is reconstructed in the [2026-09-23 raw-assembly pass](nite3w_renderer_2026-09-23.md). It compares the 32-bit game clock at DS `0x0096` with the deadline at VEC `+08`; when due, it increments frame `+03`, applies special behavior for render classes `0x07`, `0x2D`, and `0x2F`, and either wraps through the descriptor frame count or selects among an eight-entry sequence using `FUN_1018_32D2() & 7`. It schedules the next deadline as current clock plus the descriptor interval at `+02`.

The descriptor row is 8 bytes at `0x51AC + textureSet*8`; observed fields are frame count at `+00`, interval at `+02`, and sequence-table offset at `+04`. DOS E-20 `FUN_1000_241E` independently has the same timed update and sequence selection, with its class-`0x2D` helper at `FUN_1000_04BE`. The remaining task is to map every row to its WALLS asset and trace the repeated `FUN_1018_3C0C` side effect.

## Global 0x7E60

`FUN_1010_66B0` reads runtime word `0x7E60`; under certain conditions it can be zeroed for horizontal orientations. USER.SAV serializes a corresponding word at `0xD6E5`.

Possible meanings considered during audit include environment, door displacement, scroll/texture shift, or other special wall motion. None is sufficiently proven to publish as final. The correct next step is a full write-XREF audit.

---

# 14. Original renderer limits and structures

| Item | Value | Status |
|---|---:|---|
| framebuffer | 320×200, 64,000 B | CONFIRMED |
| normal 3-D viewport | 304×152 | CONFIRMED |
| VEC record | 28 B | CONFIRMED |
| total VEC capacity | 1000 | CONFIRMED |
| VECLIST capacity | 333 pointers per orientation | CONFIRMED |
| owner entry | 4-byte far pointer | CONFIRMED |
| owner entries | 320 | CONFIRMED |
| wall occlusion entry | 2 B | CONFIRMED |
| wall occlusion entries | 320 | CONFIRMED |
| wall span | 20 B | CONFIRMED |
| wall span capacity | 50 | CONFIRMED |
| projected sprite record | 18 B | CONFIRMED |
| projected sprite capacity | 100 | CONFIRMED |
| wall texture-column height | 64 samples | CONFIRMED for WinG wall path |
| sprite transparent index | `0x29` | CONFIRMED for audited sprite path |

---

# 15. Comparison with released id-era source code

Similarity is useful for orientation, not proof of source identity.

| Engine | Visibility discovery | Relationship to NITE3W |
|---|---|---|
| Catacomb Abyss | boundary-ray / wall-list style | useful structural comparison for wall lists/spans; NITE3W's four VECLIST + owner table is different |
| Hovertank 3-D | traced wall chain/list | broad family resemblance, different data structures and traversal |
| Wolfenstein 3-D | per-screen-column tile-grid DDA | direct counterexample to NITE3W's recovered vector-list traversal |

Reference source trees previously used for comparison:

- Catacomb Abyss `C4_DRAW.C`, `C4_TRACE.C`;
- Hovertank 3-D `HOVDRAW.C`;
- Wolfenstein 3-D `WL_DR_A.ASM`.

Do not describe Nitemare 3-D as a simple Wolf3D renderer clone.

---

# 16. Current highest-value open renderer targets

1. Map the recovered `FUN_1010_65A6` descriptor rows, VEC `+01/+02` data and `FUN_1018_3C0C` side effect to visible wall resources.
2. Map every `WALLS.* wall ID -> flags/property -> renderClass -> texture descriptor -> renderer branch` and validate the special `FUN_1010_6422` cases against source assets.
3. Port MAP boundary extraction, four-list traversal and camera projection/near clipping, then wire the recovered owner, span-interpolation and column-sampling primitives into the runtime.
4. Finish sprite/object ordering, masked-wall interaction, palette-remap generation inputs and resource-loader edge behavior.
5. Compare the alternate VGA planar backend and DOS renderer against the WinG path where behavior is expected to match.
6. Capture deterministic frames from the original executable using the same map, camera, palette and display route; compare 64,000 indexed pixels per frame and resolve the differences.

The owner decision, basic sampler tables and linear indexed-column loop are now instruction-backed and have a standalone C++ reference implementation. The playable `Raycaster.cpp` is still a provisional grid-DDA renderer; the new code is not yet a full scene-renderer port. Full pixel parity remains unverified until original-runtime captures are compared.
