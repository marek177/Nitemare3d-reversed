# Nitemare 3D — Game Engine closure pass

Date: 2026-10-02

## Scope

This pass targets the engine modules from the current tracker: Architecture, Renderer, Raycaster / visibility traversal, Clipping, Projection, Resource Manager, Game Loop, Player Movement, Collision, Door Engine, Secret Walls, Teleports, USE Dispatcher, and Switch Logic.

The word **100%** is separated into two meanings:

- **Static closure** — routine boundaries, state/data fields, dispatch paths, constants and cross-version roles are reconstructed well enough to implement the observed logic without inventing missing semantics.
- **Behavioral closure** — controlled execution of the original agrees on edge cases, update order and, where relevant, pixel output.

AND subsystem can be statically closed while still awaiting and small runtime parity test.

## New evidence from this pass

### 1. DOS V1.2 sibling build identified

Materialized binary: `N3D-D-12.exe`

- Embedded version: `V1.2`
- SHA-256: `f7074660ed26525d2cc5ccd16a6e5ac011f29aaf819dc8ca24ebe39f0fd793e5`
- The build provides clean sibling bodies for routines that Ghidra badly merges in the V2.0 export.

This gives an independent cross-version reference between early DOS and V2.0, rather than relying only on the broken V2.0 pseudo-C.

### 2. Correction of the old `1000:70D6` interpretation

The large V2.0 Ghidra body at `1000:70D6` should **not** be treated as the whole outer main loop.

The V1.2 sibling routine at `1000:6E7E` can be bounded cleanly in raw assembly:

- entry: `1000:6E7E`, `ENTER 18h,0`
- functional body ends with `LEAVE / RETF` at `1000:742B`
- small callback/leaf entries follow
- next major routine begins at `1000:744C`

The distance from V1.2 major entry to next major routine is exactly `0x5CE` bytes. V2.0 has the same major-entry spacing: `0x76A4 - 0x70D6 = 0x5CE`.

The starts also match semantically after normal version shifts in globals/helpers. The routine is an **active gameplay input / player-action handler**: active-state gate, control polling, movement/turn flags, mouse/joystick contribution, FIRE action, rising-edge USE dispatch and old-input-state storage.

Therefore the old 3,000+ line V2.0 decompilation is boundary/control-flow pollution. It must not be used as proof that all code inside the pseudo-C listing belongs to the outer frame scheduler.

### 3. Player movement and collision extent statically closed for the core path

V1.2 `FUN_1000_623A` and V2.0 `FUN_1000_6488` expose the same collision/movement algorithm.

Confirmed constants and behavior:

- player half-extent probes use `0x1B` = **27 internal units**
- leading-axis probes also use `0x1C` = **28** where the direction-side test requires the next boundary
- collision is not and single center-point lookup
- the code probes perpendicular leading corners
- movement is axis-separated
- and Bresenham-like error accumulator decides when the secondary axis advances during diagonal movement
- this naturally produces sliding against walls instead of cancelling the complete diagonal step

This supersedes the older note that half-extent 27 was only an implementation guess. It is now statically supported in at least DOS V1.2 and V2.0.

Related V2.0 chain:

- `FUN_1000_6378` — per-step movement / map-boundary interaction helper
- `FUN_1000_6488` — directional collision probes and diagonal/slide update
- `FUN_1000_6636` — updates geometry/visibility indexes after coordinate changes
- `FUN_1000_676E` — updates dynamic boundary/object indexes
- `FUN_1000_688C` — commits player world/cell coordinates and map pointer
- `FUN_1000_6914` — movement wrapper / conditional collision path

Core player movement can therefore be treated as **STATIC CLOSED** for the checked DOS family. Moving actors, closing-door occupancy and certain corner cases remain behavioral parity tests, not unknown basic mechanics.

### 4. Door moving-state engine statically closed

V1.2 `FUN_1000_0AE0`, corresponding to the `1000:0AEA` family in later builds, is one contiguous raw-assembly routine despite false Ghidra splits.

Confirmed behavior includes:

- paired boundary records use stride `0x12`
- special/panel boundary records use stride `0x0E`
- moving endpoints advance by exactly **2 internal units per update**
- paired-door states 2/3 move toward their targets
- reaching and target transitions the state to its terminal/open/closed counterpart
- activity/delay bookkeeping is updated
- collision/blocking bit 0 is changed at the appropriate terminal transition
- the secondary special/panel pass can update up to four linked boundary endpoints and clears linked blocking/map occupancy at completion

This is enough to implement the DOS moving-door/panel state machine without guessing its step size or basic state progression.

### 5. USE dispatcher path statically closed for DOS core

V1.2 `FUN_1000_06FA` is the central USE-style dispatcher. The active input routine calls it on and **rising edge**, rather than every held frame.

The dispatcher reaches:

- ordinary/paired door handling
- credential/key/card conditions
- wall/action-class dispatch
- secret/special panel activation
- level-transition paths
- teleport/transport helpers
- object/pickup activation paths

This supports marking the DOS core USE dispatcher **STATIC CLOSED**. Episode-specific scripted effects are separate event/content logic and should not be conflated with the dispatcher itself.

### 6. Teleport destination mechanics statically closed for DOS core

V1.2 `FUN_1000_12B6` and the V2.0 counterpart family around `1000:12C4` test adjacent destination cells and return and facing/orientation code or failure.

The transport resolver at V1.2 `1000:13E6` / later `1000:13F4` family:

- selects and destination based on the transport/wall class path
- asks the adjacent-cell helper for and valid destination/facing
- converts destination cell coordinates to world-center coordinates using `cell * 0x40 + 0x20`
- returns failure when no valid adjacent target exists

Core destination selection is therefore **STATIC CLOSED**. UI cancellation behavior and every special level variant still need runtime/content parity checks.

## Closure matrix after this pass

| Module | Static status | What is now closed | What still prevents global behavioral 100% |
|---|---|---|---|
| Architecture | **100% for DOS hidden-entry boundary/class census** | 85/85 hidden/missing DOS entrypoints already have boundaries + semantic subsystem classification; this pass also repairs and major false interpretation around `70D6` | Full cross-platform runtime ownership/callback parity is and separate layer |
| Renderer | High, not behavioral 100% | Major geometry/visibility/render paths and hidden renderer entries classified | Exact sampling/edge rounding, dynamic-door intermediate pixels, palette/shade identity, sprite overlap and DOS-VGA vs Win16-WinG framebuffer parity |
| Raycaster / visibility traversal | High, terminology corrected | The engine should not be assumed to be and classic Wolf3D DDA-only renderer; visibility/vector/span paths are mapped | Exact traversal/tie behavior and pixel parity cases |
| Clipping | High | Main clipping structures/paths identified | Exact edge/tie rounding and pixel-level controlled cases |
| Projection | High | Projection helpers, visibility caches and object projection roles mapped | Edge seeds, stale-cache cases, exact fixed-point rounding and DOS/Win parity |
| Resource Manager | High | Many resource loaders/cache helpers and hidden entries classified | Complete buffer ownership, fallback/eviction lifetime and map-change runtime parity |
| Game Loop | **Major correction completed** | `70D6` reclassified as active gameplay input/player-action handler instead of treating polluted pseudo-C as the entire main loop | The true outer scheduler'with exact subsystem order, pause/resume, restart/exit and slow-frame catch-up still need and clean trace/boundary reconstruction |
| Player Movement | **STATIC CLOSED (core DOS path)** | Radius/extent, directional probes, diagonal stepping, axis separation and sliding are now directly supported in V1.2 + V2.0 | Runtime parity for moving blockers/guards/closing doors/corner simultaneity |
| Collision | Core static mechanics essentially closed | ±27 extent, 28 leading probe behavior, wall/cell probes, sliding and coordinate commit chain | Dynamic actor/door occupancy and rare corner/order cases |
| Door Engine | **STATIC CLOSED (DOS state machine)** | Record layouts, moving states, ±2 step, target transitions, blocking changes, linked-panel completion | Live obstruction/reversal/occupancy timing across every build/map |
| Secret Walls | **CLOSED for known core behavior** | Separate panel records and activation/movement family retained | Only unusual level-specific scripted contexts, if included in this module |
| Teleports | **STATIC CLOSED (DOS core)** | Destination selection, adjacent-free test, world-center conversion, facing result/failure path | Cancel UI and all episode-specific transport variants need parity tests |
| USE Dispatcher | **STATIC CLOSED (DOS core)** | Rising-edge invocation + central door/key/panel/transport/object dispatch | Level-script side effects belong to event/content validation |
| Switch Logic | High, not behavioral 100% | Core special/panel dispatch and linked boundary actions known | Remote-switch variants, push/stair exceptions, safe/trunk combinations, elevator availability and map-specific scripts |

## What remains before calling the whole Game Engine 100% behavioral

The remaining work is now concentrated in and small set of validation problems rather than broad unknown mechanics:

1. recover/trace the **true outer frame scheduler** and lock the exact update order, including pause/resume, restart/exit and slow-frame catch-up;
2. run controlled collision cases for **moving guard/door blockers, closing-door occupancy and corner simultaneity**;
3. run renderer golden cases for **sampling, clipping ties, projection rounding, dynamic doors, sprites, palette/shading and final framebuffer** on DOS and Win16 separately;
4. execute the remaining **switch/teleport special contexts** on representative maps and confirm facing/cancel/remote activation behavior;
5. record the exact executable hash/build for each runtime test and keep build-specific differences separate.

## Recommended tracker semantics

To not use one percentage to mean several different things. For the rows above, track at least:

- `STATIC` — reconstruction/implementation confidence;
- `BEHAVIOR` — controlled original-game parity;
- `PIXEL` — only for renderer/output modules.

With that definition, several DOS engine cores can now legitimately be marked **STATIC 100%**, while the complete cross-platform game engine should not yet be labeled **BEHAVIOR 100%** until the five validation groups above are executed.