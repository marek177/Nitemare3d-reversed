# OpenNitemare3D — Pass 16
## Renderer Stage 4: persistent dynamic VECs + exact wall IMG frame selection

Stage 4 moves the reconstructed renderer from static wall geometry to the
original runtime data model.

## 1. Paired-wall controllers are now attached directly to VECs

`OriginalWallRuntime` ports the renderer-relevant behavior of:

```text
14A8  build paired-wall controllers
188A  toggle / propagate paired-wall state
1D4E  ordinary auto-close decision
1E00  move paired-wall VEC endpoints
```

The builder scans raw MAP cells whose generated wall property has bit `0x08`,
then finds the first two VECs in table order satisfying:

```text
VEC.flags & 0x08
VEC.X1 >> 6 == cellX
VEC.Y1 >> 6 == cellY
```

It stores references to those actual Stage-4 VEC objects.

The controller therefore no longer animates only an OpenNitemare3D `Tile`.
Its motion mutates the exact endpoints used by E798/3940 on the following frame.

### Exact paired motion

State 2 / opening:

```text
selected endpoint += 2
```

State 3 / closing:

```text
selected endpoint -= 2
```

with sign reversed when VEC flag `0x20` selects the opposite endpoint.

Both halves move together.

At terminal position:

```text
opening -> state 0, timer 32, clear VEC flag bit 0 on both halves
closing -> state 1, timer 32
```

This is the original `1E00` geometry behavior.

## 2. Exact state 4 and auto-close rules retained

The runtime exposes state 4 (`LatchedPassable`) without moving it.

`TickAutoClose()` implements the ordinary timer path:

```text
state 0 only
classes 3B/3C excluded
timer--
timer 0 + unoccupied -> state 3 + collision bits
timer 0 + occupied   -> timer 4
```

It intentionally requires a callback for the **runtime** object occupancy.

Do not feed it the static MAP object byte; guards and moving actors mutate that
runtime occupancy in the original game.

## 3. Class-3 four-way special wall groups

Stage 4 builds up to 32 class-3 groups using the original `3736/37A0` bounds
semantics.

When phase 2 is activated, `1E00` moves:

```text
orientation 0 component X1 toward X2
orientation 1 component Y1 toward Y2
orientation 2 component X1 toward X2
orientation 3 component Y1 toward Y2
```

by exactly two world units per update.

When all linked components finish, all groups sharing those VECs have render bit 0
cleared, both bytes of their MAP cell are cleared, and phase returns to 0.

The public bridge is:

```csharp
OriginalRendererStage4.ActivateClass3Wall(x, y);
```

Actual gameplay trigger wiring is still a USE/gameplay integration task.

## 4. Corrected IMG layout is now used by the renderer

Stage 4 no longer renders wall pixels from:

```text
Level.tilemap[x,y].textureID
-> Img.current.entries[textureID]
```

Instead `OriginalImgWallRuntime` opens the episode's raw `IMG.N`.

Checked layout:

```text
0000..03FF wall directory:   256 x u32
0400..07FF object directory: 256 x u32
0800..61FF low/wall SEQDEF:  256 x 90 B
6200..BBFF high/object SEQDEF
BC00..EOF frame streams
```

For each original VEC, the wall ID selects the wall-directory stream offset.

`4C8A` deduplication is reproduced:

```text
same image-stream offset -> same 8-byte-style runtime sequence cache
```

Thus aliases share the mutable interval, just like `51AE + cacheIndex*8`.

## 5. 66B0 frame selection is no longer a Tile.textureID bridge

For each visible span Stage 4 now:

1. reads VEC sequence selector `+4`;
2. gets the shared wall sequence cache;
3. clamps VEC frame `+3` to `frameCount-1`;
4. selects that exact frame in the raw IMG stream;
5. uses the frame's true width in EBD6/6422;
6. draws its x-major indexed pixels;
7. calls the reconstructed 65A6 animation update after the span.

This is the original 66B0 structure.

## 6. Wall animation update

`UpdateAfterVisibleSpan()` implements:

- deadline check;
- frame++;
- class `0x2F` loop behavior;
- class `0x07` special hold/completion behavior;
- class `0x2D` exploding-wall completion hook;
- ordinary non-extended looping;
- extended eight-branch SEQDEF logic;
- next deadline = current milliseconds + 16-bit interval.

For an extended SEQDEF that actually needs a random new branch, Stage 4 requires:

```csharp
OriginalRendererStage4.RandomByteProvider = ...;
```

No `System.Random` fallback is supplied, because substituting a different PRNG would
silently destroy deterministic parity.

## 7. SPECIAL1-compatible shared interval control

The original SPECIAL1 path can change the shared cache interval to 150.

Stage 4 exposes the same level of control:

```csharp
OriginalRendererStage4.SetWallAnimationInterval(wallId, 150);
```

Aliases that share the same IMG stream share the same cache object.

## 8. Ordering

Stage 4 renders with the current VEC geometry first and only then calls:

```text
TickPairedWallMotion()
TickClass3Motion()
```

This matches the recovered frame ordering: current geometry is rendered, then door
geometry advances for the next frame.

## 9. What remains

Stage 4 closes the major renderer-side dynamic/resource bridge, but not the entire
gameplay integration:

- central USE dispatcher still has to call Stage-4 controller APIs for every door/key
  class instead of the old partial Tile implementation;
- actor occupancy must be connected to `TickAutoClose`;
- moving-door cadence should be driven by the recovered scheduler rather than whatever
  host frame rate OpenNitemare3D happens to use;
- exact original RNG must be wired for extended SEQDEF random branches;
- shade remap is not yet connected;
- sprite/object renderer still needs the original slot/visibility implementation.

## Apply

```bat
git apply OpenNitemare3D_RendererStage4_from_master_Pass16.patch
```

Generate the exact Pass-15 renderer tables first:

```bat
py extract_nite3w_renderer_tables.py ^
  "C:\N3D\nite3w(10).exe" ^
  "C:\OpenNitemare3D\data"
```

Run:

```bat
dotnet run -- ^
  --n3d-renderer-stage4 ^
  --n3d-trig "data\N3D_TRIG_Q10.BIN" ^
  --n3d-visibility-octants "data\N3D_VISIBILITY_OCTANTS.BIN"
```

## Next target

The next pass should connect **gameplay USE + key/card policy + scheduler cadence**
to the new original wall controllers, then wire the 256-byte shade remap and original
sprite slot renderer.