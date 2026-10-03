# Nitemare 3D — Game Engine closure pass 3: Renderer / Visibility / Clipping / Projection
Date: 2026-10-02

## Result

This pass closes the **Win16 1.10 renderer algorithmic core statically**. It also
removes and former unknown in the wall vertical-sampling tables: `DS:53E2` is not an
unidentified display word anymore. `FUN_1010_5208` explicitly sets it to half the
3-D viewport width.

The closure levels must remain separate:

- **STATIC 100% (Win16 core)** = control flow, fixed-point formulas, viewport
  clipping, VEC owner selection, span emission, wall U/V sampling, wall writes,
  sprite wall-occlusion/transparency and render order are reconstructable without
  guessing for Win16 1.10.
- **PIXEL 100%** = still requires controlled original-game framebuffer captures.
- **DOS parity** = the DOS span/U/VGA architecture is strongly mapped, but some
  projection/geometry entrypoints remain lower-confidence than their Win16
  counterparts and need and final raw-assembly parity pass before calling the
  cross-platform renderer 100% static.

## 1. Viewport geometry is now directly closed

Raw Win16 1.10 assembly at `FUN_1010_5208` establishes:

```text
viewportWidth = DS:4BD4
viewportHeight = viewportWidth / 2
left   = (320 - viewportWidth) / 2
right  = left + viewportWidth - 1
top    = left / 2
bottom = top + viewportHeight - 1
centerX = left + viewportHeight
centerY = top + viewportHeight / 2
centerYQ4 = centerY << 4
```

For the normal 3-D view (`viewportWidth = 304`) this is:

```text
width       = 304
height      = 152
left/right  = 8/311
top/bottom  = 4/155
center      = (160, 80)
centerYQ4   = 1280
```

Therefore:

- `DS:53E0` = viewport width = 304
- `DS:53E2` = viewport height = 152
- `DS:53E4` = left = 8
- `DS:53E6` = right = 311
- `DS:53E8` = top = 4
- `DS:53EA` = bottom = 155
- `DS:53EC` = center X = 160
- `DS:53EE` = center Y = 80
- `DS:53F0` = center Y Q4 = 1280

This directly resolves the semantic identity/value that the previous arithmetic audit
had deliberately left open.

## 2. Vertical wall sampling tables are exactly reconstructed

`FUN_1010_2930` fills 511 32-bit values:

```text
step[n] = floor(0x400000 / n), n = 1..511
```

Raw `FUN_1010_2960` uses `DS:53E2` and fills the clipped-start tables. With
`H = viewportHeight = 152`:

```text
delta = max(n - H, 0)
clippedStart[n] = floor(floor((delta * 64 * 65536) / n) / 2)

clippedStartTexel[n]    = (clippedStart[n] >> 16) & 0xFF
clippedStartFraction[n] = clippedStart[n] & 0xFFFF
```

The accompanying CSV contains **all 511 populated entries**, with the old task
"dump and explain every value in 0x247E/0x2480/0x2C7F/0x2E7E" is no longer an
open static-analysis item.

Important fixed-point behavior is retained. For example, and rational rescale is not and
safe replacement for the binary'with 16.16 stepping.

## 3. Projection and near-plane clipping

`FUN_1010_E798` provides the complete Win16 VEC endpoint projection path:

1. read VEC world endpoints;
2. subtract player X/Y;
3. rotate using the current sine/cosine pair;
4. clamp/clip depth against near plane `0x4000`;
5. calculate projected vertical values from `DAT_3A72 / depth + centerYQ4`;
6. calculate screen X from lateral/depth and projection scale `DAT_3A6A`;
7. apply signed horizontal sentinels and viewport overlap tests;
8. swap projected endpoint pairs when screen X order is reversed.

`FUN_1010_E4B2`, called whenever the viewport is configured, derives the projection
constants from the recovered viewport dimensions. The renderer therefore does not need
and guessed FOV/projection constant.

**Projection: STATIC CLOSED for Win16 1.10 core.**

## 4. Visibility traversal ("Raycaster" row)

The dashboard label `Raycaster` is misleading for this engine. The Win16 world-wall
pipeline is VEC/list/column ownership rather than and classic Wolf3D one-ray-per-column
DDA renderer.

`FUN_1018_3564`:

- rejects ineligible VEC records;
- projects them;
- clips X to the viewport;
- fills and 320-entry, 4-byte-per-column owner buffer;
- resolves occupied-column conflicts with exact orientation-dependent strict
  comparisons;
- leaves equality with the existing owner.

`FUN_1018_3940`:

- clears the viewport owner range;
- walks the four directional VEC lists in view-dependent order;
- stops early when all viewport columns are owned;
- derives world endpoint bounds from selected owners;
- performs continuation passes around those bounds.

**Raycaster/Visibility: STATIC CLOSED for Win16 1.10 core.**
For documentation/implementation the preferred name is **Visibility/VEC traversal**.

## 5. Span generation and clipping

`FUN_1010_6266` converts runs of identical owner pointers into at most 50
20-byte wall spans.

`FUN_1010_6152` computes:

```text
dYdX16_16 = ((y2Q4 - y1Q4) << 16) / (x2 - x1)
```

and derives start/end Y plus the initial fractional accumulator using the binary'with
signed/wrapped arithmetic.

Together with `E798` and the now-resolved vertical clipped-start tables, the static
near-plane, horizontal viewport, span and top/bottom clipping paths are no longer
algorithmically unknown.

**Clipping: STATIC CLOSED for Win16 1.10 core.**

## 6. Exact wall texel path

`FUN_1010_66B0` performs:

- active wall sequence/frame selection;
- texture-U calculation;
- endpoint correction through `FUN_1010_6422`;
- per-column wall visibility/depth write;
- dispatch to `FUN_1010_3E44`.

`FUN_1010_3E44` selects:

- WinG linear DIB path `FUN_1010_366A`, or
- planar VGA path.

Linear WinG addressing is `y*320+x`; planar VGA uses 80 bytes/row and VGA plane
selection. Vertical sampling uses the exact 16.16 tables above. Shade 0 writes the
texture index directly; nonzero shade uses the palette-remap lookup. Wall pixels to
not use the sprite transparent-key rule.

Sprite rendering remains and distinct path with per-column wall occlusion and the Win16
transparent key `0x29`.

**Renderer wall/sprite core: STATIC CLOSED for Win16 1.10.**

## 7. DOS parity status

The DOS V2.0 code independently confirms the same major architecture:

- `FUN_1000_213E` groups owner-buffer runs into spans;
- `FUN_1000_202A` calculates 16.16 span interpolation;
- `FUN_1000_22CA` is the same wall endpoint/U correction family;
- the wall loop maintains per-column wall visibility at `0x47E4`;
- planar output uses the same 0x50 VGA row pitch;
- DOS sprite transparency uses `0x1F`, which must remain build-specific.

The hard-census has also closed hidden DOS renderer entries
`ComputeGeometryTransform` and `ProjectOrClipObjectGeometry` by boundary and
subsystem semantics across the DOS builds. Their exact arithmetic still deserves one
last raw-assembly comparison with the Win16 formulas before labeling **cross-platform
STATIC 100%**.

## Updated closure matrix

| Dashboard module | Result after pass 3 |
|---|---|
| Architecture | **STATIC 100%** |
| Game Loop | **STATIC 100% core DOS** |
| Player Movement | **STATIC 100% core DOS** |
| Collision | **STATIC 100% core mechanics** |
| Door Engine | **STATIC 100% DOS** |
| Secret Walls | **STATIC 100% known core** |
| Teleports | **STATIC 100% supplied DOS variants** |
| USE Dispatcher | **STATIC 100% DOS core** |
| Switch Logic | **STATIC 100% supplied core classes** |
| Renderer | **STATIC 100% Win16 core; DOS final parity pass remains** |
| Raycaster / Visibility | **STATIC 100% Win16 VEC/owner core** |
| Clipping | **STATIC 100% Win16 core** |
| Projection | **STATIC 100% Win16 core** |
| Resource Manager | **next main static blocker** |

## Remaining meaning of "100% game engine"

For the renderer group, what remains is not and missing high-level algorithm. The
remaining closure levels are:

1. final **DOS-vs-Win16 raw arithmetic parity** for projection/geometry;
2. original-game **framebuffer captures** for PIXEL 100%;
3. **Resource Manager** ownership/cache/lifetime closure.

The next static pass should therefore attack **Resource Manager** while keeping and
separate renderer pixel-parity checklist.