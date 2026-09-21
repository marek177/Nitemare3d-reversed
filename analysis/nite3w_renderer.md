# NITE3W.EXE renderer audit

This note records the renderer path recovered from the supplied Windows 3.1
executable.  Addresses use logical NE `segment:offset` notation; file offsets
refer to the executable with SHA-256
`12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.

## Result

The original renderer is **not** Wolfenstein 3-D's one-grid-ray-per-screen-column
DDA.  It is a software vector/span renderer:

1. project candidate wall-vector endpoints;
2. traverse four pre-sorted vector lists front-to-back;
3. assign a winning wall pointer to each viewport column;
4. coalesce adjacent equal owners into wall spans;
5. interpolate and texture-map the spans one vertical column at a time;
6. draw sorted objects/sprites with a per-column depth test; and
7. present the completed 8-bit WinG bitmap.

This conclusion is instruction-backed.  It does not identify how the tile map
is converted into the four vector lists; that producer path remains open.

## Evidence policy

- **CONFIRMED**: direct instruction, relocation or data-flow evidence.
- **STRONG**: several instructions establish the role, but a field or branch
  still lacks a final semantic name.
- **OPEN**: deliberately unresolved; no behavior is invented for it.

## Recovered call chain

```text
3:D78C frame renderer
  4:3940 traverse four sorted vector lists
    4:3564 project/clip candidate and fill column-owner table
      3:E798 transform and project vector endpoints
  3:6266 coalesce column owners into wall spans
    3:6152 initialize span interpolation
  3:3DB8 -> 3:3612 clear ceiling/floor in the WinG framebuffer
  3:66B0 rasterize wall spans
    3:EBD6 derive wall texture coordinate
    3:6422 special-wall/orientation clipping helper
    3:3E44 -> 3:366A draw one textured wall column
  3:6348 visible-object ordering/integration
  3:6914 iterate projected objects
    3:3F80 -> 3:374E draw a depth-tested sprite

confirmed presentation boundary elsewhere in the caller-side path
  3:30E2 / 3:32FE WinG stretch/blit calls
```

`3:3DB8`, `3:3E44` and `3:3F80` select between the WinG linear-buffer
implementation and a VGA-oriented fallback.  The arrows above show the WinG
path.  The WinG imports establish the final presentation boundary; the diagram
does not claim that `3:D78C` directly calls those import sites.

## Function anchors

| Address | File offset | Recovered role | Confidence | Decisive evidence |
|---|---:|---|---|---|
| `3:2F36` | `0x18EF6` | Create WinG DIB and retain pixel selector | CONFIRMED | writes width 320 and height -200, calls `WinGCreateBitmap`, stores returned bits selector at data `0x51A0`, clears `0x3E80` dwords = 64,000 bytes |
| `3:3612` | `0x195D2` | Linear framebuffer ceiling/floor fill | CONFIRMED | address is `y*320+x`; fills top with data byte `0x7E63`, bottom with `0x7E62`; row stride `0x140` |
| `3:366A` | `0x1962A` | Textured vertical wall-column drawer | CONFIRMED | texture pointer advances by `texture_x << 6`; destination advances by 320; fixed-point source step uses `ADD`/`ADC`; alternate path uses `XLAT` |
| `3:374E` | `0x1970E` | Scaled/depth-tested sprite drawer | CONFIRMED | reads depth at `0x58FE + 2*x`; palette index `0x29` skips the framebuffer write; vertical destination step is 320 |
| `3:3DB8` | `0x19D78` | Ceiling/floor backend wrapper | CONFIRMED | WinG branch calls `3:3612` |
| `3:3E44` | `0x19E04` | Wall-column backend wrapper | CONFIRMED | WinG branch calls `3:366A`; called by `3:66B0` |
| `3:3F80` | `0x19F40` | Sprite backend wrapper | CONFIRMED | WinG branch calls `3:374E`; called by `3:6914` |
| `3:6152` | `0x1C112` | Initialize a wall-span's interpolants | CONFIRMED | computes endpoint deltas/divisions and writes span fields `+0x06`, `+0x0A`, `+0x0C`, `+0x10`, `+0x12` |
| `3:6266` | `0x1C226` | Coalesce per-column owners into wall spans | CONFIRMED | scans far pointers at `0x53FE + 4*x`, emits `0x14`-byte records at `0x5E88`, enforces maximum `0x32` |
| `3:6348` | `0x1C308` | Visible-object ordering/integration | STRONG | operates between wall-span creation and sprite rasterization; exact record semantics are not all named |
| `3:6422` | `0x1C3E2` | Wall/special-wall clipping helper | STRONG | branches on wall type/orientation and can suppress a column; exact names for all cases remain open |
| `3:66B0` | `0x1C670` | Wall-span rasterizer | CONFIRMED | loops `0x14`-byte records, advances a 32-bit interpolant per x, updates depth table, calls texture-coordinate and column-draw routines |
| `3:6914` | `0x1C8D4` | Projected-sprite pass | CONFIRMED | scans 100 records at `0x6270` with stride `0x12` and calls `3:3F80` |
| `3:D78C` | `0x2374C` | Frame renderer/orchestrator | CONFIRMED | ordered far calls connect traversal, span build, clear, walls, object integration and sprites |
| `3:E516` | `0x244D6` | Set view angle and direction components | CONFIRMED | normalizes degrees to 0..359, divides by 45 for octant, stores trig results at `0x4C46/0x4C48` |
| `3:E798` | `0x24758` | Transform/near-clip/project a wall vector | CONFIRMED | subtracts view X/Y, applies direction components and near clip `0x4000`, writes projected endpoint fields `+0x14..+0x1A` |
| `3:EBD6` | `0x24B96` | Wall texture-coordinate helper | STRONG | selects direction component from wall orientation and combines screen x, projection constants and a 16.16 wall coordinate |
| `4:3564` | `0x287C4` | Candidate-vector projector/column owner | CONFIRMED | calls `3:E798`, clips projected endpoints to viewport and fills empty entries at `0x53FE + 4*x` |
| `4:3940` | `0x28BA0` | Front-to-back vector traversal | CONFIRMED | clears column owners and walks four far-pointer lists until the uncovered-column count reaches zero |

## Framebuffer and raster evidence

### WinG surface

`3:2F36` writes a 320-pixel width and negative 200-pixel DIB height before
`WinGCreateBitmap`.  A negative DIB height makes the bitmap top-down.  The
returned pixel selector is saved at data offset `0x51A0`, then `REP STOSD`
clears `0x3E80 * 4 = 64000` bytes.  The wall, sprite and background writers all
load this same selector and use a 320-byte row stride.  The recovered surface
is therefore a 320x200, linear, 8-bit indexed framebuffer.

### Textured wall column

The core of `3:366A` is equivalent to the following structural pseudocode:

```c
source = texture + (texture_x << 6); // 64-byte column
dest = framebuffer + y * 320 + x;
while (pixels--) {
    *dest = translated ? translation[*source] : *source;
    dest += 320;
    fraction += fraction_step;
    source += integer_step + carry(fraction);
}
```

This proves a 64-sample, column-major source layout for this path.  It does not
prove that every IMG resource is 64x64.

### Sprite transparency and depth

`3:374E` compares each sampled byte with `0x29` and omits the write on equality.
It also indexes a word table at `0x58FE + 2*x` before drawing a column.  That
same table is updated by `3:66B0`, which makes it the wall-depth/projected-height
buffer used for sprite occlusion.  Exact units remain open.

## Visibility traversal and recovered structures

`4:3940` does not read a tile map for every screen x.  It clears a table of far
pointers over the viewport, then consumes four ordered candidate lists:

| Pointer list | Count | Initial-index global |
|---|---:|---:|
| `0x6982` | `0x697A` | `0x4BFA` |
| `0x6EB6` | `0x697C` | `0x4BFC` |
| `0x73EA` | `0x697E` | `0x4BFE` |
| `0x791E` | `0x6980` | `0x4C00` |

The view octant at `0x4BEC` selects traversal direction/state.  `4:3564`
projects each candidate, clamps its screen interval and installs its pointer
only where the per-column owner is still empty.  `3:6266` subsequently groups
runs of identical pointers into at most 50 wall-span records.

Recovered capacities/strides:

| Item | Value | Confidence |
|---|---:|---|
| framebuffer | `320 * 200` bytes | CONFIRMED |
| wall texture-column height | 64 samples | CONFIRMED for `3:366A` |
| transparent sprite palette index | `0x29` | CONFIRMED |
| column-owner entry | 4-byte far pointer | CONFIRMED |
| depth entry | 2 bytes per x | CONFIRMED |
| wall-span record | `0x14` bytes | CONFIRMED |
| wall-span capacity | 50 | CONFIRMED |
| projected-sprite record | `0x12` bytes | CONFIRMED |
| projected-sprite pass capacity | 100 | CONFIRMED |

## Comparison with released id Software-era sources

| Engine | Visibility discovery | Wall draw organization | Relationship to NITE3W |
|---|---|---|---|
| Catacomb Abyss | `TraceRay` traces boundary rays through the tile map; `FollowWalls` builds a wall list | `DrawVWall` walks projected wall spans and records per-column height/source information | Closest structural comparison after visibility discovery: wall endpoints/spans and per-column texture work.  NITE3W's four-list owner-table traversal is different. |
| Hovertank 3-D | `TraceRay` finds boundary walls; `FollowWalls` constructs the visible wall chain | draws a wall list rather than casting every screen column independently | Same broad wall-list lineage, but not the same NITE3W traversal or data structures. |
| Wolfenstein 3-D | `AsmRefresh` computes a ray for each `pixx` and alternates horizontal/vertical grid DDA tests against `tilemap` | hit routines immediately finish the column | Direct counterexample: the recovered NITE3W frame path has no per-column grid DDA or `tilemap[x,y]` lookup. |

Similarity is not treated as identity.  The comparison sources explain the
family resemblance, while the NITE3W executable remains authoritative.

Primary comparison sources:

- [Catacomb Abyss `C4_DRAW.C`](https://github.com/CatacombGames/CatacombAbyss/blob/master/C4_DRAW.C)
  and [`C4_TRACE.C`](https://github.com/CatacombGames/CatacombAbyss/blob/master/C4_TRACE.C);
- [Hovertank 3-D `HOVDRAW.C`](https://github.com/FlatRockSoft/Hovertank3D/blob/master/HOVDRAW.C); and
- [Wolfenstein 3-D `WL_DR_A.ASM`](https://github.com/id-Software/wolf3d/blob/master/WOLFSRC/WL_DR_A.ASM).

## Open questions

- construction and lifetime of the four sorted vector lists;
- exact semantic names for every wall-vector and `0x14`-byte span field;
- every special-wall branch in `3:6422`;
- exact units stored in the word depth table at `0x58FE`;
- palette-translation table selection in the alternate `3:366A` path;
- exact ordering contract between `3:6348` and the 100-entry sprite pass; and
- the VGA fallback paths behind the three renderer wrappers.

## Reproducing the audit

`tools/ne_renderer_audit.py` preserves logical NE addresses and expands the
non-additive relocation chains used by this Win16 linker.  Examples:

```bash
python tools/ne_renderer_audit.py NITE3W.EXE disasm 3 0x366a 0x374e
python tools/ne_renderer_audit.py NITE3W.EXE xrefs 'internal 3:366A'
python tools/ne_renderer_audit.py NITE3W.EXE xrefs 'import WING'
```

The executable is intentionally not stored in this repository.
