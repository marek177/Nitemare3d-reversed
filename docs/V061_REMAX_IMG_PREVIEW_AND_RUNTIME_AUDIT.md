# v0.61 — IMG preview integration and recent runtime evidence

## Result

The playable DDA preview now reads authentic IMG slot images instead of
placeholder wall/pushable colors. The supplied renderer patches have been
ported onto current main, retaining intervening Win16 timer/calibration work.
This preview remains an approximation of the original vector/span renderer.

- Resolve wall/object slot offsets to exact IMG frames and sample column-major
  pixels; unresolved slots retain diagnostic fallback colors.
- Render pushable sprites using source dimensions, a floor baseline and index
  `0x1F` transparency. Other GUARD/OBJECT animation integration remains open.
- Traverse nonvisual TURN/RETREAT/FLEE/SAFESPOT map classes without occluding
  the scene. Player collision behavior is unchanged.
- Sample one 64x64 face from 128x64 paired images. Orientation selection is an
  explicitly provisional video-reference heuristic, not recovered VEC logic.
- Preview background uses supplied-palette indices 7/2 from qualitative video
  reference. These are not certified DOS global fill values.
- Accept the observed 1924-byte, `3A 3C 00 1F` palette container with 768 trailing
  RGB bytes. The user identified the DOS dataset's replaced palette as derived
  from Windows. This compatibility route does not certify an original DOS
  GAME.PAL format. Valid PCX extraction remains supported; wrong size/signature
  is rejected by the existing PCX fallback.

## Additional original-runtime reports integrated

The archived renderer report records 14,102,829 CPU events across four bounded
E1M1/DEMO sessions, 117 source RGB-cache frames and 116 VGA F events. Its RGB
frames are 320x400 cache output, not 64000 indexed framebuffer bytes or one
frame per game tick. Normal gameplay F-palette hash was `7301D2E3ADFA79D5` in
three intervals; the DEMO interval had 16 palette hashes in 19 F events.
Palette writer/cause and exact original-versus-port matching remain open.

A separate DOS2 report contains two complete bounded world updates with 6412
and 6619 CPU instructions, each visiting 33 actor records. The 207-instruction
difference is localized to center-alignment branches for records 24/25:
`(X&63)==32 && (Y&63)==32`. The sessions have different ticks and RAM states;
the report does not prove that map weapons caused the divergence.

The same EXE can accompany different MAP distributions (124 additional weapon
placements across 31 levels). Record identities require EXE+MAP+IMG fingerprints.
The supplied dataset also has 17 object-layer differences between E1M3 and
E1M11 despite identical walls; they must not be treated as interchangeable
DEMO maps. The E2M10 scheduler backedge is statically present in DOS1.2 and
DOS2; natural nested pool reuse/ABA remains open.

## Validation in this integration

- GCC 13.3, C++20 Debug, SDL3 disabled: core, inspector and test targets build.
- 80 synthetic CTest cases pass, including IMG column-major/slot resolution,
  nonvisual-marker rendering, paired-face edges and palette compatibility.
- One original-data integration case is not registered without private assets.
- The exported D02 JSON ledger passes recurrence/prefix validation; four
  corrupted inputs (result, event ordering, prior state, unknown caller) fail.
- No original game, SDL window, 31-map data suite or sanitizer run was executed
  in this integration. Earlier 67/69-case and 31-map results belong to their
  archived source reports, not this checkout's validation.

Initial CTest launch found two generated binaries lacking executable permission;
restoring their local executable bits allowed both cases to pass. This was a
workspace build-output issue, not a source change.

Reproduce with CMake >=3.24:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug -DN3D_ENABLE_SDL3=OFF
cmake --build build --parallel 4
ctest --test-dir build --output-on-failure
python3 tools/verify_d02_ledger.py
```

## Remaining acceptance boundary

Full DEMO RNG/EOF, natural E2M10 nested projectile behavior, projectile-to-GUARD
combat, first post-LOAD frame, canonical framebuffer+DAC zero-diff, exact
Win16 gameplay/audio and end-to-end original-versus-port acceptance remain open.
No new whole-project completion percentage is asserted.
