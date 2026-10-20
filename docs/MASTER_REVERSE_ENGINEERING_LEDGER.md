# Nitemare 3D — consolidated reverse-engineering ledger

Updated: 2026-09-22

This document consolidates high-confidence findings recovered across the Nitemare 3D reverse-engineering work. It is intentionally conservative: facts established from executable/data analysis are separated from hypotheses that still require XREF/runtime confirmation.

## Renderer architecture

The original renderer is best described as a 2.5D grid-segment projected-wall renderer with per-screen-column visibility ownership. Current evidence does **not** support describing it as a classic Wolf3D one-ray-per-column DDA renderer.

Reconstructed high-level path:

```
64x64 MAP
 -> extract tile boundaries
 -> merge compatible adjacent edges
 -> VEC[0..999], 28-byte records
 -> four orientation VECLIST indexes, max 333 FAR pointers each
 -> select potentially visible vectors
 -> world-to-camera transform
 -> near clipping
 -> project segment endpoints
 -> owner[x] visibility resolution
 -> coalesce identical owner[x] runs into wall spans
 -> floor/ceiling stage
 -> textured wall rasterization
 -> per-column wall silhouette/occlusion buffer
 -> object projection/culling
 -> 18-byte render-object queue
 -> sprite drawing clipped by wall silhouette
 -> framebuffer
```

Observed main frame functions include:

- `FUN_1018_3940` — visibility/traversal and owner-buffer construction.
- `FUN_1010_6266` — owner columns to wall spans.
- `FUN_1010_3DB8` — probable floor/ceiling stage; exact behavior still under audit.
- `FUN_1010_66B0` — wall-span renderer.
- `FUN_1010_6348` — object-pass setup/ordering candidate.
- `FUN_1010_6914` — render-object command consumption / sprite stage.

## MAP -> VEC construction

`FUN_1018_4370` invokes `FUN_1018_4046` for four orientations. `4046` scans the 64x64 tile map, creates boundary edges and merges compatible adjacent edges.

Established limits and geometry:

- total VEC capacity: **1000** (`0x3E8`);
- VEC record size: **28 bytes / 0x1C**;
- tile size: **64 world units**;
- `FUN_1018_4006` extends compatible vectors by one tile (64 units).

Orientation mapping:

| value | segment |
|---:|---|
| 0 | horizontal top: `(x,y) -> (x+64,y)` |
| 1 | horizontal bottom: `(x,y+64) -> (x+64,y+64)` |
| 2 | vertical right: `(x+64,y) -> (x+64,y+64)` |
| 3 | vertical left: `(x,y) -> (x,y+64)` |

## Reconstructed VEC record

```cpp
struct N3DVector {
    uint8_t  wallId;          // +00
    int8_t   texOffset;       // +01 tentative
    uint8_t  animAux;         // +02 tentative
    uint8_t  animFrame;       // +03 likely
    uint8_t  textureSet;      // +04
    uint8_t  flags;           // +05
    uint8_t  renderClass;     // +06
    uint8_t  orientation;     // +07
    uint32_t timer;           // +08
    int16_t  x1;              // +0C
    int16_t  y1;              // +0E
    int16_t  x2;              // +10
    int16_t  y2;              // +12
    int16_t  screenX1;        // +14
    int16_t  projectedY1_Q4;  // +16
    int16_t  screenX2;        // +18
    int16_t  projectedY2_Q4;  // +1A
};
```

The endpoint and projected fields are high-confidence. Names of several metadata fields remain provisional.

Known/probable flag behavior:

- `0x01`: active/renderable — high confidence.
- `0x20`: texture-U flip — high confidence.
- `0x04`, `0x08`, `0x10`: special geometry/render/occlusion behavior; exact names remain unresolved.

Special `renderClass` values observed include `2`, `0x3F`, and `0x40`. Exact mapping to named WALLS classes must remain provisional until table/XREF correlation is complete.

## VECLIST spatial indexes

Four FAR-pointer arrays are present at approximately:

- `0x6982`
- `0x6EB6`
- `0x73EA`
- `0x791E`

Their spacing is `0x534 = 333 * 4`, proving capacity for 333 four-byte FAR pointers per orientation list. Associated counts appear around `0x697A..0x6980`.

`FUN_1018_3430` distributes VEC pointers according to orientation and sorts the lists. Horizontal lists are ordered by Y; vertical lists by X.

Therefore:

- `MAXVEC = 1000` is the real vector-record capacity;
- `MAXVECLIST = 333` is the per-orientation pointer-index capacity.

## Per-column owner buffer

Base address: approximately `0x53FE`.

It contains 320 FAR pointers:

```
0x53FE + 320 * 4 = 0x58FE
```

`FUN_1018_3940` clears the active viewport range and tracks uncovered columns. `FUN_1018_3564` projects/considers vectors and resolves which vector owns each covered screen X.

Important optimization: when all viewport columns have an owner, visibility traversal can terminate early.

This is a visibility/depth ownership mechanism, but should not be mislabeled as a conventional numeric Z-buffer.

## Wall spans

`FUN_1010_6266` coalesces consecutive columns with the same owner vector.

- span count: `DAT_1048_5E7E`;
- span array: approximately `0x5E88`;
- record stride: **0x14 = 20 bytes**.

This corrects an older working hypothesis that the renderer record stride was 52 bytes.

Approximate record:

```cpp
struct WallSpan {
    N3DVector far* vec;    // +00
    int16_t xStart;        // +04
    int16_t yStartQ4;      // +06
    int16_t xEnd;          // +08
    int16_t yEndQ4;        // +0A
    int32_t dy_dx;         // +0C likely 16.16
    int32_t yAccumulator;  // +10
};
```

`FUN_1010_6152` prepares interpolation. `FUN_1010_66B0` advances the accumulator per screen column.

## Viewport and projection

Normal game framebuffer: **320x200**.

Observed 3D viewport is approximately:

- width 304;
- height 152;
- x range 8..311;
- y range 4..155;
- center X 160;
- center Y 80;
- center-Y Q4 value 1280.

`FUN_1010_E516` normalizes angles to 0..359 and uses 45-degree sectors.

`FUN_1010_E798` performs world-relative endpoint transformation, near clipping and perspective projection. Evidence shows real integer perspective division rather than a simple distance-to-wall-height lookup.

A near-plane/clamp value of `0x4000` is involved. Projected X can be saturated near signed +/-16383 before viewport clipping.

`FUN_1010_E4B2` derives projection constants from viewport dimensions. A reconstructed focal value for width 304 is consistent with a horizontal field of view around 81 degrees, but **81 degrees is an inference, not a discovered named constant**.

## Wall silhouette / sprite occlusion buffer

A second per-column structure starts at approximately `0x58FE` and uses two bytes per X column.

The wall renderer writes projected wall silhouette/vertical occlusion information here. Object projection checks this data at several horizontal sample positions.

This should be documented as a wall silhouette/occlusion buffer, not as a conventional Z-buffer unless future analysis proves otherwise.

## Render-object queue

A separate queue begins around `0x6270`.

- capacity: **100 records**;
- record size: **0x12 = 18 bytes**;
- initialized/free-marked by `FUN_1010_6142`;
- commands built by `FUN_1010_CC7C`;
- consumed/reset in the sprite stage associated with `FUN_1010_6914`.

Approximate record:

```cpp
struct RenderObject {
    uint8_t activeOrFree;      // +00 semantics still to name exactly
    uint8_t subtypeOrState;    // +01 tentative
    void far* worldObject;     // +02
    int16_t spriteDesc;        // +06
    int16_t screenLeft;        // +08
    int16_t screenRight;       // +0A
    int16_t screenTop;         // +0C
    int16_t screenBottom;      // +0E
    int16_t projectedBottomQ4; // +10
};
```

Queue placement is related to projected vertical/depth ordering. If suitable buckets cannot be found, the executable contains the diagnostic text **"Too many objects on screen"**.

## Wall texture rendering

`FUN_1010_66B0`:

- walks the wall-span list;
- uses VEC metadata to select texture/resource descriptors;
- uses orientation and `flags & 0x20` for texture-U direction;
- contains special branches for render classes including `0x3F` and `0x40`;
- updates the per-column wall silhouette;
- calls lower-level raster/blit logic including `FUN_1010_3E44`.

`FUN_1010_6422` is a high-confidence texture-U/wall-coordinate mapping candidate, but its exact rules remain a priority audit target.

`FUN_1010_EBD6` derives a perspective mapping value using screen-X relative to center, camera angle sector and projection/trigonometric constants.

## Important runtime record sizes and limits

Other established/working findings retained from the broader audit:

- object records: **80 bytes**; object count access observed near `3:D1EA`;
- guard records: **98 bytes**; guard count/data activity observed around `0x7E5E`;
- VEC records: **28 bytes**, max 1000;
- orientation VECLIST: max 333 FAR pointers each;
- wall-span records: **20 bytes**;
- render-object records: **18 bytes**, max 100.

The object/guard semantic field maps should continue to be maintained separately as individual offsets are confirmed.

## Enemy/guard research ledger

The guard audit must preserve distinctions between directly recovered constants, runtime observations and hypotheses. Active targets include:

- Dracula, including scripted death/transformation behavior to BAT;
- Greenie;
- Goldie;
- Demon;
- Tail Slim robot;
- Trashcan robot;
- Dr. Hamerstein and other bosses.

For each guard, continue resolving:

- HP / strength;
- movement speed;
- state machine and reaction delays;
- attack cadence;
- player damage;
- score award;
- weapon resistance/immunity;
- difficulty-dependent behavior;
- SND.DAT sound indices;
- episode/map occurrence;
- special scripted transitions.

Do **not** record an unverified Demon score of zero as fact. It remains an audit target until the score-award path/table is traced.

## Difficulty and combat

Difficulty values 1/2/3 must be audited independently for:

- guard HP or effective survivability;
- outgoing enemy damage;
- reaction/AI timing;
- spawn/content changes;
- ammunition or pickup effects.

Avoid assuming a Wolf3D/Doom-style difficulty implementation. Each multiplier/table needs executable evidence.

## Data/resource families

The reverse-engineering project tracks these original resource families:

- `MAP.1`, `MAP.2`, `MAP.3`
- `WALLS.1`, `WALLS.2`, `WALLS.3`
- `OBJECTS.1`, `OBJECTS.2`, `OBJECTS.3`
- `IMG.1`, `IMG.2`, `IMG.3`
- `SND.DAT`
- `UIF.DAT`
- `ENDING.FLI`
- `NITE3D.BSF`
- DOS/Windows executable versions and historical builds

Named WALLS classes seen in the audit include families such as WARP, DOOR, SPECIAL, ONE_SHOOT, REVWALL, CONTROL and episode-specific variants. Their exact runtime flags/render-class mapping is still being correlated.

## ENDING.FLI

The project has separately investigated the game's FLI ending animation. Decoder/editor work should account for the FLI chunk types actually encountered, including palette/color updates and frame compression/delta modes. Any editor must validate output against the original animation rather than assuming all frames are independent full images.

## SND.DAT

Earlier extraction tests showed that naive VOC extraction can produce audio that differs from known-good extraction. Adam Biser's extractor output has been used as a behavioral reference. The sound audit should therefore preserve raw offsets/lengths and encoding metadata before conversion and should not assume every apparent VOC entry is independently valid.

A separate sound-index audit exists in `analysis/snd_index_audit.csv`. The remaining goal is to map every guard/action/UI event to its exact SND.DAT index and playback parameters.

## NITE3D.BSF / version audit

BSF analysis is being performed across historical executable versions. Priority workflow:

1. locate every XREF to `nite3d.bsf`;
2. identify parent functions;
3. trace open/read/seek/close;
4. recover comparisons involving BSF and game/data files;
5. reconstruct the validation algorithm byte-for-byte;
6. compare versions 1.0, 1.7, 1.8/1.9 and 2.0.

Do not name the algorithm as a checksum, encryption or copy-protection scheme until the recovered code proves the exact semantics.

## Special walls / interaction research

Continue mapping WALLS definitions to:

```
wallId
 -> flags table (observed around 0x7E94)
 -> render-class table (around 0x8196)
 -> texture/resource descriptor (around 0x51AC)
 -> interaction handler
 -> animation/timer behavior
```

Known research targets include WARP_L*, WARP_*, WARP_E*, WARP_S2, JAMP, DOORVL/HL/VI/HI and variants, WALL_EX1, CONTROL, SPECIAL1, ONE_SHOOT and REVWALL.

Many walls appear to use short two-tick or longer animation sequences. VEC fields around +02/+03/+08 and `FUN_1010_65A6` are priority targets for confirming animation semantics.

## High-priority unresolved items

1. Fully translate `FUN_1018_3564` and its owner-column conflict/hidden-surface rules.
2. Fully translate `FUN_1010_6422` texture-U mapping.
3. Audit `FUN_1010_3E44` down to framebuffer writes, transparency, scaling and platform-specific blitting.
4. Resolve `FUN_1010_65A6` wall animation/timer behavior.
5. Resolve `FUN_1010_3DB8` floor/ceiling rendering.
6. Find every write/XREF to global `DAT_1048_7E60`; do not name it prematurely.
7. Find every write to VEC +01/+02/+03/+04/+08.
8. Build a complete WALLS wallId -> flags -> renderClass -> resource -> handler table.
9. Finish sprite-queue field semantics and rasterization.
10. Search for alternate/unused render paths, hidden graphics modes, debugging paths and dead code.
11. Establish exact guard HP/score/damage/resistance tables.
12. Establish exact SND.DAT event mappings.
13. Audit hard limits for maps, levels, guards, objects, doors, panels, pushes and rendering structures.
14. Compare executable versions for deleted/unused code, hidden cheats and behavioral changes.

## Confidence policy

Use these labels in future documentation and source comments:

- **CONFIRMED** — directly demonstrated by executable/data structure/runtime evidence.
- **HIGH** — multiple independent observations strongly support the interpretation.
- **TENTATIVE** — plausible semantic name with incomplete XREF/runtime proof.
- **UNKNOWN** — observed field/function/global whose meaning is not yet established.

This prevents hypotheses from silently becoming "facts" as the reconstruction grows.
