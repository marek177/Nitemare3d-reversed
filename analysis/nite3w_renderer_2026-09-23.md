# NITE3W renderer: raw-assembly pass (2026-09-23)

Target: Windows 3.1 `NITE3W.EXE` v1.10, SHA-256
`12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.

This pass resolves several renderer TODOs in the 2026-09-22 audit by checking
the NE code segments directly. The executable has no original source symbols;
Ghidra's C output is useful for navigation, but the raw instructions decide
operand order, integer width, and signed comparison behavior.

## Finding: this is a vector/span renderer, not per-column grid DDA

The game extracts and merges exposed MAP boundaries into 28-byte VEC records,
sorts four orientation lists, projects and clips those segments, chooses one
owner VEC for each screen column, merges adjacent owner columns into at most 50
spans, then draws textured columns and projected sprites. The current
`src/renderer/Raycaster.cpp` remains a provisional Wolf3D-style DDA viewer; it
is not yet the recovered renderer.

## `FUN_1018_3564`: occupied owner-column decision

The eight cross-orientation replacement cases are now instruction-backed.
Each relation is a strict signed 16-bit comparison. If either comparison is
equal, or the orientations are the same, the currently stored owner remains.

| Existing owner | Candidate | Replace when |
|---:|---:|---|
| 0 | 2 | candidate `x1 > old.x1` and candidate `y1 < old.y1` |
| 0 | 3 | candidate `x2 < old.x2` and candidate `y1 < old.y1` |
| 1 | 2 | candidate `x1 > old.x1` and candidate `y2 > old.y2` |
| 1 | 3 | candidate `x2 < old.x2` and candidate `y2 > old.y2` |
| 2 | 0 | candidate `x2 > old.x2` and candidate `y2 < old.y2` |
| 2 | 1 | candidate `x2 > old.x2` and candidate `y1 > old.y1` |
| 3 | 0 | candidate `x1 < old.x1` and candidate `y2 < old.y2` |
| 3 | 1 | candidate `x1 < old.x1` and candidate `y1 > old.y1` |

The routine separately clips projected X to the active viewport and inserts a
far pointer when an owner slot is empty. The table above only models the
occupied-slot decision. `FUN_1018_3940` traverses the four sorted lists and
stops once its uncovered-column count reaches zero. `FUN_1010_6266` then
coalesces consecutive equal owners into 20-byte spans.

This resolves the previous audit's open owner-conflict question. The exact
conditions are implemented in `src/renderer/Win16WallRasterCore.hpp` and
covered by `tests/win16_wall_raster_core_test.cpp`.

## `FUN_1010_2930` and the raw initializer at `CS:2960`

`FUN_1010_2930` fills 511 entries beginning at DS `0x2482`:

```text
step[n] = floor(0x400000 / n), n=1..511
```

This is a 16.16 source-texture step for 64 texels over projected height `n`.
The C decompiler reports this helper with no parameters, although its call site
passes values; raw instructions show that the table itself only uses the loop
counter.

A second initializer starts at `CS:2960`, immediately after a separate
instruction boundary. Its caller at `CS:5259` calls selector:offset
`51cc:2960`. Ghidra's C export misses this body and misaligns the nearby
`FUN_1010_29be` entry. For each `n=1..511`, the initializer reads DS `0x53E2`,
computes `delta=max(n-DS[0x53E2],0)`, then evaluates the following operations
in this order:

```text
q = floor(((delta * 64) << 16) / n)
clippedStart16_16 = floor(q / 2)
```

The high source-texel byte is stored at `DS:0x2C7E+n`; the low word is stored
at `DS:0x2E80+2*(n-1)`. The value at `DS:0x53E2` is proven as an input to the
clipping table; its standalone semantic name still needs confirmation.

## `FUN_1010_366A`: WinG indexed wall-column loop

For the linear DIB backend, a selected texture column begins at
`texture + 64*U`. For each destination pixel, the renderer writes one palette
index, advances the destination by `0x140` (320 bytes), adds the 16-bit
fractional step to the accumulator, and advances the source pointer by the
integer step plus the carry. If palette conversion is enabled, it writes
`DAT_1048_8094[sourceTexel]` instead of the source byte.

This confirms a 16.16 sampler and the 320-byte DIB row pitch in that path. The
64-byte source stride is a property of this audited wall-column path; it does
not imply every IMG asset is 64x64.

`FUN_1010_3E44` selects this linear path when `DAT_1048_46B0 == 0`. Otherwise
it programs VGA sequencer plane selection and writes to planar memory with an
80-byte plane stride. That alternate VGA backend still needs frame-level
comparison against the WinG route.

The portable C++ core exposes the recovered sampler as
`drawWinGIndexedColumn()`. It accepts an already-selected 64-sample column and
explicit 16.16 start/step values. It is a tested low-level primitive, not a
claim that the full scene renderer has been ported.

## `FUN_1010_6422`: status

The branch structure is recoverable and the prior blanket TODO is too broad.
The routine first checks whether the screen column lies within the first/last
eight projected columns; if neither endpoint is near, or VEC flag `0x08` is
set, it returns the along-wall coordinate masked by `width-1`. Near an endpoint
it applies orientation-specific signed segment-length corrections, including
the special `renderClass == 2` handling for orientations 0 and 3. A full
class-to-wall-resource mapping and comparison renders are still required
before attaching human-readable names to all cases.

## Code and verification

- `src/renderer/Win16WallRasterCore.hpp`: 28-byte VEC view, exact owner winner
  predicates, both sampling-table initializers, and the bounded indexed-column
  loop.
- `tests/win16_wall_raster_core_test.cpp`: checks all eight owner cases,
  strict tie behavior, table values, direct/remapped column writes, and invalid
  source clipping.

The new test compiles and runs with C++20 and `-Wall -Wextra -Wpedantic`.
These checks validate the isolated routines; they do not establish pixel
parity for a complete game frame.

## What remains before claiming full renderer parity

1. Finish the `FUN_1010_6422` numerical port against original captures and map
   its special cases to every `WALLS.*` property/resource class.
2. Trace `FUN_1010_65A6` and writes to VEC `+01/+02/+03/+08` to recover exact
   animated-wall timing and frame selection.
3. Port MAP boundary extraction, four-list sorting, camera transform and
   clipping, owner coverage, span interpolation, object ordering, and both
   wall/sprite resource paths into the runtime.
4. Recover exact palette-remap inputs and resource-loader edge behavior.
5. Capture deterministic frames from the original Win16 executable with the
   same map, camera, palette, and display route; compare indexed framebuffer
   bytes, then investigate any differing columns. Repeat for the VGA path and
   DOS build where parity is claimed.

The original executable and core WALLS/OBJECTS/MAP/IMG/PAL assets are already
available in the user's Library, so no additional upload is required for this
static/code work. Exact frame comparison still requires controlled reference
captures from the original runtime. Function matching across builds helps
identify routines, but does not prove behavior or pixel parity by itself.
