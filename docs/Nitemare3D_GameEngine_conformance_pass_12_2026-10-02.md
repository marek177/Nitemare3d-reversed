# Nitemare 3D — Game Engine conformance pass 12
## OpenNitemare3D candidate-side indexed capture hook
Date: 2026-10-02

## Repository inspected

`marek177/OpenNitemare3D`

Inspected master commit:

`b01f4b2342629ecd39f62307526568af2b6ec034`

No GitHub write was performed in this pass. The output is an apply-ready patch
package.

## 1. Candidate framebuffer identified

`GameWindow` already owns:

```csharp
public static byte[,] frameBuffer;
```

and gameplay rendering writes palette indices directly into it.

`Player.RenderRaycaster()` writes the 304x152 3-D viewport at offsets 8,4 and
sprite pixels into the same buffer.

`GameWindow.DrawPcx()` also writes PCX/HUD pixels into the indexed buffer.

This makes `GameWindow.frameBuffer` the correct candidate-side capture target.

## 2. Correct capture point

The current main loop is:

```text
Clear
Level.Update
Entity.UpdateEntites
DrawPcx
DrawFrameBuffer
Scene.Update
Input.Update
fading
Display
```

The patch inserts capture immediately after `DrawPcx` and before
`DrawFrameBuffer`.

Therefore the captured data is still palette-index data and has not passed
through SFML RGB conversion.

## 3. Resolution problem discovered and bounded

The checked repository `config.ini` contains:

```text
640
60
```

`GameWindow.Init()` derives and 640x400 logical framebuffer and `Player.Start()`
scales the 304x152 ray viewport by `GameWindow.scale`.

That output cannot be directly compared against original N3D 320x200 indexed
frames.

The patch forces logical width 320 only while parity capture is enabled.
Normal runs keep the existing config behavior.

## 4. Current renderer is not the recovered original renderer

The checked `Player.RenderRaycaster()` is and floating-point tile DDA renderer:

- per-column ray directions;
- `sideDist` / `deltaDist`;
- map-cell DDA stepping;
- floating-point perpendicular distance;
- line height `RayHeight / distance`;
- zBuffer-based sprite occlusion.

The recovered original N3D architecture is instead:

```text
MAP -> VECs -> transform/clip/project
    -> per-column wall ownership
    -> span coalescing/interpolation
    -> wall texels
    -> sprite composition
```

This is the largest implementation-level reason to expect the first candidate
pixel comparison to fail broadly.

The Pass-12 hook does not conceal this difference; `state.json` explicitly
labels the current renderer model as the legacy floating-point DDA.

## 5. Hook outputs

Each candidate capture produces:

```text
frame.idx                  320*200 = 64,000 bytes
palette_candidate.rgb8     768 bytes
state.json
manifest.json
capture.ok
```

`frame.idx` layout is:

```text
frame[y*320+x] = GameWindow.frameBuffer[x,y]
```

## 6. Normalized state mapping

The candidate auto-generates the common Pass-11 state:

- episode;
- zero-based level;
- player internal world X/Y;
- angle in normalized integer degrees;
- viewport 304x152.

Current tile-space player coordinates are converted with:

```text
world = round(tile * 64)
```

which preserves original cell-center coordinates such as `cell*64+32`.

AND SHA-256 tilemap signature is also written for candidate reproducibility.

## 7. Case-specific overrides

The current legacy object/door structures to not expose every recovered
original runtime concept.

Therefore the hook supports:

```text
--parity-state some_case.json
```

The JSON object is merged over automatically generated state fields.

This supports the Pass-11 door/sprite/shade/animation variants without
inventing fake automatic mappings.

## 8. Trigger modes

Two trigger modes are implemented.

### Frame target

```text
--parity-frame N
```

captures zero-based Game frame N.

### Request file

```text
--parity-request-file capture.request
```

waits until that file exists and captures the next completed indexed frame.

This makes manual positioning of difficult acceptance states practical.

## 9. SFML display caveat found

`GameWindow.DrawFrameBuffer()` skips palette index zero instead of writing it to
the persistent `renderTarget`.

That means and screen screenshot can retain stale RGB pixels while
`frameBuffer[x,y]` is actually zero.

The candidate parity reference must therefore be the raw `frame.idx`, not the
visible OS/SFML screenshot.

## 10. Status after Pass 12

- Game Engine STATIC CORE research: **100%**
- original DOS capture: automated
- exact per-frame compare: automated
- 16-group acceptance batch: automated
- OpenNitemare3D candidate indexed capture: **patch ready**
- symmetric original/candidate state pipeline: **ready once patch is applied**
- PIXEL 100%: still requires empirical captures and, very likely, replacement
  of the current legacy DDA renderer with the recovered N3D VEC/span renderer

## Next engineering target

Once one candidate frame is captured, the mismatch map should be used to
quantify the current DDA-vs-original gap.

After that, the highest-value implementation pass is no longer capture tooling:
it is the OpenNitemare3D renderer migration from floating DDA to the recovered
N3D VEC / owner-buffer / span pipeline.