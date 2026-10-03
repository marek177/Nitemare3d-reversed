# OpenNitemare3D — Pass 13
## Stage-1 migration from floating DDA to Nitemare 3D VEC/owner/span renderer

Prepared against the inspected `marek177/OpenNitemare3D` master line.
This is an opt-in migration stage, not a claim of pixel parity.

## What is ported with instruction-backed semantics

`OriginalRendererCore.cs` ports the already recovered low-level renderer core:

- 320×200 target / 304×152 viewport;
- viewport origin 8,4 and center 160,80;
- projection-constant builder;
- VEC record semantic fields;
- visible-span record semantic fields;
- `FUN_1018_3564` owner conflict matrix;
- `FUN_1010_6152` signed 16.16 span interpolation;
- `FUN_1010_6422` texture-U endpoint correction;
- `FUN_1010_2930` + `1010:2960` wall sampling/clipping tables;
- indexed wall-column writer;
- `FUN_1018_33BA` orientation-list sort rule;
- original capacities: 1000 VEC, 333/list, 50 spans.

These parts are intentionally kept separate from the current game's DDA code.

## Stage-1 OpenNitemare3D integration

`OriginalRendererExperimental.cs` adds an opt-in wall path:

```text
current Level.tilemap
    -> axis-aligned boundary VECs
    -> merge compatible 64-unit edges
    -> four sorted orientation lists
    -> player-outward traversal
    -> project/clip bridge
    -> 320-entry owner buffer
    -> original owner conflict test
    -> contiguous spans
    -> original 16.16 interpolation
    -> original vertical sample tables
    -> indexed wall columns
```

Enable:

```bat
dotnet run -- --n3d-renderer-stage1
```

For parity capture, use it together with the Pass-12 native 320×200 hook.

Optional stats:

```bat
dotnet run -- ^
  --n3d-renderer-stage1 ^
  --n3d-renderer-stats "C:\N3D-Captures\renderer_stage1.json"
```

## Why this is not yet the final original renderer

Three high-value integrations remain deliberately marked as bridge code.

### 1. MAP/WALLS -> VEC special policy

Original vector creation consults recovered wall property/class tables
equivalent to `7E94 / 8196 / 8296`.

Current OpenNitemare3D `Tile` does not expose those original table bytes.
Stage 1 therefore treats:

```text
tile.obstacle && textureID >= 0
```

as an opaque wall and extracts its external tile boundary.

This is sufficient to migrate simple opaque room geometry onto the VEC/owner/span
pipeline, but it is not correct for every door, curtain, half-wall, special or
dynamic class.

### 2. Full E798 clipping/traversal

The low-level projection constants and owner matrix are known.

Stage 1 clips wall endpoints against the same recovered near depth `0x4000`, but
does so directly in transformed camera space.

The original `E798` contains build-specific integer/cardinal branches. Those will
be ported in the next stage after the simple-room path is measurable.

### 3. Perspective wall-U / EBD6

Stage 1 gets the wall intersection geometrically, then applies the exact recovered
`6422` endpoint correction.

The original `EBD6` perspective mapping is not yet a literal instruction-for-
instruction C# port.

## What changes visibly now

When stage 1 is enabled:

- the old per-column grid DDA wall search is bypassed;
- the viewport background uses recovered original defaults:
  - ceiling index `0x11` (17)
  - floor index `0x0C` (12);
- simple walls are selected through a VEC owner buffer and grouped into spans;
- sprites are intentionally not yet drawn by this stage.

The missing sprites are deliberate. Reusing the legacy zBuffer sprite renderer on
top of the new wall ownership model would mix two incompatible visibility systems.

## Recommended first measurements

Use Pass 12 + Pass 13 for the simple wall-only acceptance cases first:

- cardinal 0/90/180/270;
- near-plane;
- left/right viewport clipping;
- wall-owner tie;
- closed static wall geometry.

Do not use the sprite/shade/animated-door groups as a Stage-1 success criterion.

## Capacity checks

Stage 1 enforces:

```text
VEC             <= 1000
orientation list <= 333 each
visible spans    <= 50
```

Matching the recovered original runtime bounds.

## Apply

```bat
git apply OpenNitemare3D_RendererStage1_Pass13.patch
```

The patch is independent of Pass 12, but for 320×200 indexed comparison it is
recommended to use both.

If `GameWindow` is not logical 320×200, the experimental renderer refuses to
activate and falls back to the existing legacy DDA renderer.

## Next migration pass

Stage 2 should wire the real MAP/WALLS property/class tables into VEC generation,
then replace the camera-space clipping bridge with the literal recovered E798
integer/cardinal behavior.

Only after that should the original sprite slot/occlusion path be attached.