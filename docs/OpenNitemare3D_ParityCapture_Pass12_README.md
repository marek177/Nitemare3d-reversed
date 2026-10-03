# OpenNitemare3D — Pass 12 parity capture hook

Prepared against repository:

- `marek177/OpenNitemare3D`
- branch: `master`
- inspected commit: `b01f4b2342629ecd39f62307526568af2b6ec034`

## Why this hook exists

The Pass-11 suite expects the candidate implementation to produce:

```text
frame.idx
state.json
```

for the same normalized state as the original DOS capture.

The current OpenNitemare3D renderer stores palette indices in:

```csharp
GameWindow.frameBuffer[x, y]
```

This is exactly the right place to capture the candidate before SFML converts
indices to RGB.

The hook flattens it to:

```text
frame.idx[y*320+x]
```

which is the same canonical 64,000-byte format used by the original DOS capture
pipeline.

## Important current-renderer fact

At the inspected commit, `Player.RenderRaycaster()` is a floating-point,
Wolfenstein-style per-column DDA renderer.

The original Nitemare 3D renderer recovered by the reverse-engineering work is
a VEC -> projection/clipping -> column-owner -> span -> wall-texel pipeline.

Therefore this hook is **measurement infrastructure**, not a claim that the
current OpenNitemare3D renderer will already pass pixel parity.

A large mismatch in the first capture is expected until the original renderer
core replaces or supplements the legacy DDA path.

## Native-resolution correction

The repository's current `config.ini` uses width 640.

Current code scales `RayWidth` and `RayHeight` from that width, so a 640x400
framebuffer is not a valid byte-for-byte reference against the original
320x200 renderer.

When parity capture is enabled, the patch forces the logical GameWindow width
to 320. Existing code then derives height 200 and scale 1.

Normal execution without `--parity-capture` is unchanged.

## Apply

From the OpenNitemare3D repository root:

```bat
git apply OpenNitemare3D_ParityCapture_Pass12.patch
```

Or add `ParityCapture.cs` manually and make the two small changes shown in the
patch.

## Automatic first game frame

```bat
dotnet run -- ^
  --parity-capture "C:\N3D-PixelSuite\candidate\01_cardinal_000\base" ^
  --parity-case 01_cardinal_000/base ^
  --parity-frame 0 ^
  --parity-exit
```

`--parity-frame` is zero-based and starts counting only after the `Game` scene
is active and `Game.player` exists.

## Manual exact-state capture

For cases such as intermediate doors or sprite overlap, a frame counter is
less convenient.

Use a trigger file:

```bat
dotnet run -- ^
  --parity-capture "C:\N3D-PixelSuite\candidate\10_door_intermediate\middle" ^
  --parity-case 10_door_intermediate/middle ^
  --parity-request-file "C:\N3D-Captures\capture.request" ^
  --parity-state "C:\N3D-Captures\door_middle_override.json"
```

Navigate to the exact state, then from another console:

```bat
type nul > C:\N3D-Captures\capture.request
```

The next completed indexed game frame is captured.

## Output

```text
frame.idx                  64,000 bytes
palette_candidate.rgb8        768 bytes
state.json
manifest.json
capture.ok
```

On error:

```text
capture.error.txt
```

## Automatically generated state fields

The hook emits the Pass-11 common state:

```text
episode
level                 # zero-based, matching current OpenNitemare3D code
player_world_x
player_world_y
angle_deg
viewport_width
```

It also emits:

```text
level_one_based
viewport_height
player tile and floating-point position
rotation radians
health
direction vector
camera plane
entity count
frame number
tilemap SHA-256 signature
renderer model
```

Player world X/Y are converted using the original N3D scale:

```text
internal_world = round(tile_position * 64)
```

so a map-cell center `x + 0.5` becomes:

```text
x*64 + 32
```

## Case-specific state

Some Pass-11 fields cannot be truthfully inferred from the current legacy
OpenNitemare3D structures.

Examples include:

```text
door_geometry_signature
owner_tie_case
slot_order_signature
shade_index
dark_event_flag
```

Use `--parity-state <json>` to merge case-specific evidence.

An example file is included as:

```text
parity_state_override_example.json
```

Never fill these with guessed values just to make the suite run.

## Capture point

The Program patch captures after:

```text
Level.Update()
Entity.UpdateEntites()
GameWindow.DrawPcx()
```

and immediately before:

```text
GameWindow.DrawFrameBuffer()
```

This is deliberate. At that moment the palette-index framebuffer already
contains the gameplay render and PCX/HUD composition, but has not yet been
converted into SFML RGB pixels.

## Current display caveat

`GameWindow.DrawFrameBuffer()` currently skips index 0:

```csharp
if (i == 0) { continue; }
```

and `renderTarget` is persistent.

That can make the displayed SFML/RGB window retain an older RGB pixel where
the current indexed framebuffer contains zero.

The parity hook avoids this problem by capturing `frameBuffer` itself.
Do not use an OS screenshot as the candidate reference.

## Pass-11 integration

After candidate capture:

```bat
py n3d_pixel_suite_pass11.py run ^
  --cases Nitemare3D_pixel_suite_16groups_pass11.json ^
  --root C:\N3D-PixelSuite ^
  --parity-tool n3d_pixel_parity.py
```

The suite will reject a candidate with `STATE_MISMATCH` if required normalized
state fields differ from the original.