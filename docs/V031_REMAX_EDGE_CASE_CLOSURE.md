# v0.31 RE MAX — PUSH safety and four edge-case trace contracts

Date: 2026-10-14. Incremental update after v0.30; **no new original CPU
capture is provided**. This version does not claim to close 1:1 runtime
behavior or increase any parity percentage.

## Changes actually made

1. `LevelState::tickPushables()` now preserves position, remaining steps and
   existing map cells if the destination becomes occupied/solid after a push
   starts, or if its mapped source object has disappeared. It no longer blindly
   overwrites the destination when crossing a cell boundary. This is a **modern
   reconstruction safety fix**, backed by a data-free regression fixture; it
   is not a runtime reproduction of original Win16 collision timing.
2. `tests/pushable_blocked_test.cpp` exercises mid-push occupancy, blocked
   wall followed by resume, a foreign object with the same ID, and source
   mutation. The existing original-data `pushable_test.cpp` remains opt-in.
3. `tools/n3d_edge_trace_compare.py` compares *raw ordered observations* of
   four single-entity scenarios: PUSH, door auto-close, projectile pool and
   secret-panel VEC retraction. It reports the first different record/field,
   missing/extra records, malformed headers and noncontiguous sample indices.
   There is **no sorting, resynchronization, guessed state transition, or
   auto-promotion to verified runtime behavior**.
4. Eleven Python tests use exclusively synthetic captures, including unknown
   projectile state bytes. Tests and the new C++ test are wired to CI on
   Windows and Linux.

## Build-specific evidence — *not* new original traces

| Probe | Strongest previous evidence | Still unverified |
| --- | --- | --- |
| PUSH block/resume | DOS v2.0 reported static `0DF8`/`0E50` and Win16 8 × 8-unit push record | Exact per-tick obstruction checks and cross-build parity |
| Door blocked auto-close | DOS v2.0 reported static `1000:0A40` re-arms retry=4 | Real timer write, callback order, state-4 paired-door version difference |
| Full projectile pool | Win16 `1010:9AAC` checks free slot before ammo helper; pool is 8 × 42 bytes | Actual last-ammo result, all-slot lifecycle timing, DOS v2.0 difference |
| Secret panel | DOS v2.0 retraction toward opposite VEC endpoint in 2-unit steps | First passable/collidable tick, completion and interaction interleaving |

Status is unchanged from v0.19/v0.27/v0.29: **PUSH block/retry = reported
static**, **Win16 full-pool ammo preservation = strong**, **2-unit secret
retraction = confirmed geometric primitive**, and **runtime timeline = open**.

### Snapshot CSV layouts

The first column `step` is a **normalized consecutive observation ordinal**
starting at zero, *not* an inferred CPU tick number. Record one watched entity
at a single chosen boundary per observation. A recorder must establish its
start and end from observed original execution; the tool cannot infer missing
unlogged CPU calls. Decimal and `0x` integer fields are accepted.

**PUSH** — at the entry/exit of each attempted update and at the crossing:

```csv
step,push_id,x,y,remaining,blocked,old_cell_object,destination_cell_object
0,24,672,672,8,0,24,0
1,24,680,672,7,0,24,0
```

Capture a normal full eight successful steps, then a separate fixture with a
blocker inserted after three steps and subsequently removed. The `blocked`
field is the measured collision result, not guessed from unchanged position.

**Door** — observe the close attempt and next tick(s), including paired door:

```csv
step,door_id,state,timer,blocked,pair_state
0,4,3,1,0,3
1,4,3,4,1,3
```

Do not transfer state-4 DOS v1.2 behavior to v2.0 or Win16 by offset alone.

**Projectile pool** — preserve **all eight raw state bytes**, before and after
FIRE, in slot order. Each 16-character `slot_states_*` token encodes 8 bytes
(2 hex digits per slot); unknown bytes such as `FF` are retained, not silently
renamed. `allocated_slot=-1` means no allocation observed.

```csv
step,fire_pressed,weapon,ammo_before,ammo_after,allocated_slot,slot_states_before,slot_states_after
0,1,0,10,10,-1,0101010101010101,0101010101010101
```

Fill the pool, attempt FIRE, then separately free a slot and FIRE again.
Record which instruction wrote ammo, not just HUD display after a tick.

**Secret panel** — coordinates are VEC endpoints in the selected build's
internal units. `blocking` is the observed collision property:

```csv
step,panel_id,x0,y0,x1,y1,blocking
0,1,100,50,110,50,1
1,1,102,50,110,50,1
```

Trace VEC endpoint writes, map occupancy and player collision in the same
logical update; two-unit geometry alone does **not** prove passability timing.

### Strict comparison

```sh
python tools/n3d_edge_trace_compare.py push orig-push.csv port-push.csv
python tools/n3d_edge_trace_compare.py door orig-door.csv port-door.csv
python tools/n3d_edge_trace_compare.py projectile orig-pool.csv port-pool.csv
python tools/n3d_edge_trace_compare.py panel orig-panel.csv port-panel.csv

python -m unittest discover -s tests -p "test_n3d_edge_trace_compare.py" -v
cmake -S . -B build -DN3D_ENABLE_SDL3=OFF
cmake --build build --target n3d_pushable_blocked_test
ctest --test-dir build -R '^n3d_pushable_blocked_test$' --output-on-failure
```

By default exact matching captures report `trace_match_unsealed`; this is
**not** accepted original parity evidence. To require recorder declarations,
provide **both** envelopes and `--require-boundaries`. Each JSON envelope must
have `schema`, `scenario`, `build`, `row_count`, `csv_sha256`, distinct `begin` /
`end` markers and `closed: true`:

```json
{
  "schema": "n3d-edge-trace-envelope-v1",
  "scenario": "push",
  "build": "dos-v2.0",
  "row_count": 2,
  "csv_sha256": "<sha256-of-the-raw-CSV>",
  "begin": "first_push_update",
  "end": "after_second_update",
  "closed": true
}
```

A matching envelope verifies its own CSV digest and declared boundaries only.
A user-supplied `closed:true` assertion **does not independently prove** that
all original CPU events were captured. Preserve raw debugger logs, the exact
original EXE SHA-256, entry/return breakpoints and the test map/save. Verify
DOS v2.0 original fingerprint independently using the v0.30 tool (171,360
unpacked bytes, canonical SHA), and never reuse DOS addresses for Win16.

The tool deliberately does **not** implement claimed original rules such as
"blocked always freezes PUSH", "full pool never consumes ammo", or "secret
panel becomes passable at step N". Those are hypotheses to distinguish via
original-vs-port ordered traces, not validator assumptions.

## Remaining runtime proof before a 1:1 promotion

- Original DOS v2.0 and/or Win16 captures for all four scenarios, with
  executable hash and observed update boundaries, plus reproducible independent
  runs on the same build.
- PUSH: prove location and remaining-step writes on a truly blocked substep.
- Door: prove actual retry write to 4 and its NEXT scheduling, including paired
  door and version-specific early return.
- Projectile: prove pool-full ammo behavior, state reuse and next-update
  movement without relying on a matching final HUD display.
- Panel: log the **first passable tick** and the write order of VEC, MAP and
  collision property, not only the final panel position.
- Multi Plasma, FB–FE missiles, general `0800:0E50` OBJECT scheduling,
  E2M10 nested special branch, RNG chronology and renderer pixel parity all
  remain open.

## Separate HP correction

The normal **Win16 100 HP cap is already documented as verified** in
`docs/PLAYER_HEALTH_RE.md` (initialization, pickup checks, and a HUD-path
unsigned clamp writing the value back). Rare transient/debug branches still
need tests, but the normal 100-HP ceiling should not be relabeled UNKNOWN.
