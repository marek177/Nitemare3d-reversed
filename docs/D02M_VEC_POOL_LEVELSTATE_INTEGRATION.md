# D02-M: stateful VEC lookup and live WALL geometry

This change applies the supplied D02-L and D02-M patch stack to the full repository. Sources read: `D02L_LEVELSTATE_GEOMETRY.patch` (Library `libfile_a122d3d0c01481918eb68fbb6fd94897`), `D02M_VEC_POOL_LOOKUP_INTEGRATION.patch` (`libfile_64f09eb30b9081918332ba8adb0e935a`) and `N3D_REMAX_D02M_VEC_POOL_LOOKUP_CLOSURE_20261020.md` (`libfile_491cc53dd4d88191a0a880b4f8d3a494`), all 2026-10-20. Local repository tests were rerun. Private original EXE/MAP/event data and the static verifier were not rerun here.

## Supported flow

`Dos20VecPoolRuntime.hpp` imports the bounded active 28-byte VEC pool from an exact 64-KiB DS snapshot: signed-count field 626E, records at 62AC, class +06, flags +05 and type +07. Counts beyond the host-supported 1000-record pool are rejected. Endpoints +0C/+0E/+10/+12 use signed SAR6, with type1 end / type2 start corrections unless flag08 is set.

Lookup 100A2 is stateful. A nonzero class resets index/near pointer and stores the class; zero advances once and resumes. Candidates match inclusive signed rectangles in pool order. **There is no bit0 eligibility filter.** The terminal class2D consumer 104BE decodes the triggering VEC, queries at its X0/Y0 and class, then continues with class zero. It clears bit0 after each match and can legitimately repeat WALL writes as 00→00 on a later event.

The bridge calls the recovered bounded class2D animation gate and updates real `LevelState` WALL cells, retaining write order, old/new bytes and optional original physical addresses. OBJECT bytes are preserved, including nonzero blocking objects on cleared WALL cells. WALL ID zero now means empty for preview rendering and collision even when the definitions file labels zero NULL. Clearing a wall does not remove an object obstacle.

Future deadlines do not advance animation; equality is due. Deadlines use unsigned 32-bit comparison and wrapping clock+interval. Descriptor and unsupported-coordinate failures are bounded host behavior, not a claim of original malformed-input compatibility. Selected geometry is validated before ordinary domain mutations. The API requires an explicitly validated terminal SPAN event; it does not synthesize original scheduler calls.

## Evidence boundary

The source report attributes 41 opcode windows and 4 call edges to SHA-pinned DOS2 static validation, and 8/8 ordered VEC/WALL writes to a private D02-K replay. Its input VEC records were synthetic records derived from recorded original bounds/type/class, not a captured full native pool. These results are source-reported and were not reproduced against original data during this GitHub integration.

Repository synthetic tests cover ordered matches at indices 9/256, reset/continue, inclusive boundaries, type corrections, DS import, repeated cleared flags, horizontal/vertical writes, invalid-trigger/geometry rollback and preservation of all 4096 OBJECT cells. No full-engine parity percentage is assigned.

The separate report `REPORT_SK(20261020-193238).md` (Library `libfile_adac21f74b2c81918d420273699e37da`) also uses the name D02-M, but concerns independent original A/B DEMO runs. It reports 275/275 input matches, later actor-local RNG routing differences and a second playback epoch at 7000 cycles. That capture is distinct from this geometry patch stack and does not validate this integration's scheduler or establish a cycles-only cause.

## Remaining work

Native VEC construction/order, SPAN-event production from BF36→2500→241E, shared cursor globals 3C92/3C94/3C96 under reentry, full scheduler timing and synchronized original-versus-port gameplay/frame/DAC parity remain open. The running main-loop DDA path is not replaced. Confidence is medium for the report-to-code evidence transfer; local synthetic integration is directly tested.

```sh
cmake -S . -B build -DN3D_ENABLE_SDL3=OFF -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug --target n3d_dos20_vec_pool_lookup_test n3d_dos20_class2d_geometry_integration_test
ctest --test-dir build -C Debug -R 'n3d_dos20_(vec_pool_lookup|class2d_geometry_integration)_test' --output-on-failure
```
