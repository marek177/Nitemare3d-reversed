# V089: instrumented SDL preview frame capture

An opt-in `--preview-trace path.csv` flag is now wired to the actual `src/main.cpp` SDL preview update/render loop. The header-only helper is `src/re/N3DPreviewFrameTrace.hpp`.

CSV columns: `frame,push_tick,x,y,angle,input,pushables,moving`. These are **remake preview**, not DOS state; frame is the loop iteration, push_tick counts calls to `tickPushables`, x/y are tile coordinates, angle is radians, and input uses preview-local bits (forward=1, backward=2, left turn=4, right turn=8, left strafe=16, right strafe=32, actionPressed=64). Do not interpret these as DOS DS:3F50 bits. A row is captured after preview movement and push updates but before rendering, one row per preview frame.

Example (with locally supplied original data): `nitemare3d --episode 1 --level 1 --preview-trace /tmp/n3d-preview.csv`

**Evidence boundary:** This trace is **not compatible** with V088 `n3d.gameplay-state.v1`; the preview player is still advanced through wall-clock frame `dt`, not proven original DOS tick ordering. Neither original executable nor game data are uploaded. Unimplemented HP/weapon/guard/projectile fields are deliberately not invented.

Next work: extract original instruction-aligned KEYSTATE → rotation/translation → XY commit and replace/augment current frame-based movement with a separately validated fixed-tick simulation. Compare those authentic snapshots with V088 before making a parity claim.
