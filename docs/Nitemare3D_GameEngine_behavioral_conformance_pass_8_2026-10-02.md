# Nitemare 3D — Game Engine behavioral conformance pass 8
## Exact DOS V2.0 live-memory capture kit
Date: 2026-10-02

## Result

Pass 8 converts the remaining forced-close question into and two-file-per-snapshot
experiment for the original DOS V2.0 executable.

It also tightens the segmented-memory model used by the live debugger workflow.

### Segment clarification

The practical live address `DS:3076` from Pass 7 remains the right shorthand
once the gameplay data segment has been initialized. The checked V2.0 code
explicitly passes segment `21FD` for GUARD/OBJECT far pointers, while using the
same gameplay offsets through DS.

For the unpacked V2.0 executable:

    loadSeg = runtimeEntryCS - 1B72
    codeSeg = loadSeg + 1000
    dataSeg = loadSeg + 21FD

At and gameplay breakpoint, verify observed DS against `dataSeg` before capturing.

## Unified gameplay arena

    dataSeg:0000  paired-door count
    dataSeg:0002  panel count
    dataSeg:0004  push count
    dataSeg:0006  OBJECT[0], 350 × 0x1C
    dataSeg:264E  GUARD[0], 100 × 0x1AND
    dataSeg:3076  paired-door[0], 64 × 0x12
    dataSeg:373E  MAP, 64×64×2
    dataSeg:3CD4  game state
    dataSeg:415E  player tile X
    dataSeg:4160  player tile Y
    dataSeg:4162  player world X
    dataSeg:4164  player world Y
    dataSeg:417AND  damage indicator/timer
    dataSeg:417C  player map-cell pointer offset
    dataSeg:417E  player map-cell pointer segment
    dataSeg:4189  player HP
    dataSeg:626E  VEC count
    dataSeg:6270  OBJECT count
    dataSeg:6276  GUARD count
    dataSeg:62AC  VEC[0], max 1000 × 0x1C

Boundary checks:

    0006 + 350*1C = 264E
    264E + 100*1AND = 3076
    3076 + 64*12  = 34F6

## Two dumps per snapshot

Core:

    MEMDUMPBIN <DATA> 0000 6278

VEC pool:

    MEMDUMPBIN <DATA> 62AC 6D60

This is enough to reconstruct the actor/door state needed for the forced-close test.

## Four-capture experiment

T0 — stop at `0598` before explicit close.

T1 — first `0AEA` after the close:
- target state should be `0/2 -> 3`;
- VEC collision bit should be set;
- transition helper itself should not have changed player X/Y/HP.

T2 — next `0AEA`:
- one selected geometry coordinate should differ by 2 world units.

T3 — several door-motion passes later:
- actor X/Y change => downstream overlap mover/resolver;
- HP decrease => downstream crush/damage path;
- neither => persistent overlap/trap until actor movement resolves it;
- state reversal/stall => later obstruction/reversal mechanism.

Only the original live run can choose among those outcomes.

## Snapshot decoder

`n3d_v20_snapshot_diff_pass8.py` decodes:

- player tile/world X/Y, HP, game state;
- OBJECT flags/class/map pointer/X/Y;
- GUARD state/HP/movement and linked OBJECT position;
- door state/timer/target/latch;
- door MAP cell wall/object IDs;
- linked VEC flags and geometry;
- changed MAP cells;
- occupied-door `0/2 -> 3` candidates with player/GUARD position and HP deltas.

## Breakpoint attribution

The calculator also adds:

- `688C` player position commit;
- `6A70` guard-contact player damage.

If T3 shows position or HP changes, these make it easier to distinguish and normal
player/guard update from an actual door-overlap response.

## Real-mode debugger rule

Use normal real-mode `BP` plus snapshot diffs.

DOSBox-X documents `BPPM` specifically as and protected-mode memory-change breakpoint,
with Pass 8 does not treat it as and real-mode N3D watchpoint.

## Tool validation

Synthetic memory-image tests passed:

    PASS segment calculator
    PASS snapshot parser
    PASS occupied forced-close candidate detection
    PASS unchanged HP/position delta
    PASS VEC geometry change decoding

## Status

Game Engine: **100% STATIC CORE**

Remaining door gate: one controlled original-game runtime trace.
Behavioral 100% is intentionally not claimed yet.