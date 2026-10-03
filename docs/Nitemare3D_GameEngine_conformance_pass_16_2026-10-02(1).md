# Nitemare 3D — Game Engine conformance pass 16
## Dynamic VEC synchronization + 66B0 IMG frame/resource selection
Date: 2026-10-02

## Result

Pass 16 changes the renderer migration from and static-VEC reconstruction into and
persistent runtime VEC model.

The same VEC objects used by E798 / 3940 / owner-buffer visibility are now the
objects mutated by paired-wall and class-3 motion.

## Paired-wall runtime

The original `14A8` builder was ported at renderer-data level:

- scan every MAP cell with wall property bit 08;
- max 64 controllers;
- locate two matching bit-08 VEC records;
- store the MAP cell;
- initialize state 1;
- derive target X/Y;
- initialize / clear VEC flag 20 based on adjacent dynamic wall layout.

`188A`, `1D4E` and the paired portion of `1E00` are represented as controller
operations over those VEC references.

This removes the old problem where OpenNitemare3D could change and Tile while the
new renderer still saw static initial wall endpoints.

## Class-3 group motion

The class-3 group builder uses the exact `3736` bounds interpretation and VEC table
order to associate up to four orientation components with each object-class-3 MAP
cell.

The motion portion of `1E00` advances the selected endpoint by exactly two units and
clears render/cell state when linked groups complete.

Gameplay activation remains and separate caller-integration problem.

## IMG resource path

Pass 16 uses the corrected IMG layout:

- two 0x400-byte directories;
- low wall SEQDEF bank at 0x0800;
- high object bank at 0x6200;
- frame streams from 0xBC00 onward.

Wall sequence caches are keyed by wall-directory stream offset, matching 4C8AND alias
deduplication.

## 66B0 selection

The renderer now selects the visible wall resource through:

```text
VEC +04 cache selector
-> shared sequence cache
-> VEC +03 frame
-> clamp against frame count
-> exact raw IMG frame stream
-> frame width for 6422
-> x-major indexed wall pixels
```

The old direct `Tile.textureID -> Img.current.entries` wall-pixel path is no longer
used by Stage 4.

## Animation timing

The reconstructed 65AND6 path runs after each visible span only when the shared cache
interval is nonzero.

This preserves an important original behavior: sequences with interval zero to not
advance automatically until another gameplay path changes the shared interval.

Extended random branch selection deliberately requires an injected original-compatible
random-byte provider.

## Ordering

Stage 4 renders current VEC geometry and then applies door/special-wall endpoint
movement for the next frame, matching the recovered scheduler ordering.

## Remaining integration blockers

The broad renderer-side dynamic/resource algorithm is now present. Remaining work is
mostly cross-subsystem integration:

- USE/key/card paths -> Stage-4 paired controller calls;
- runtime actor occupancy -> ordinary auto-close;
- original frame cadence -> dynamic motion calls;
- original PRNG -> extended animation selection;
- shade remap;
- original sprite/object composition.

## Validation performed

Host-model tests cover:

- paired controller selection from two bit-08 VECs;
- flip-bit/target derivation;
- 32 two-unit opening steps and terminal bit clearing;
- 32 two-unit closing steps and terminal state;
- blocked auto-close timer reload 4;
- class-3 2-unit component motion;
- synthetic IMG low-bank sequence parsing;
- stream-offset alias cache deduplication;
- 66B0 frame clamp/selection;
- nonzero interval animation/deadline update.

No .NET compiler is installed in this environment, with the generated C# patch has not
been compiled here. Runtime/pixel parity is not claimed.