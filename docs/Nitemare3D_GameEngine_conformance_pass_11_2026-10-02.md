# Nitemare 3D — Game Engine conformance pass 11
## Batch pixel-parity acceptance suite
Date: 2026-10-02

## Outcome

The renderer validation workload is now organized as an executable **16-group /
30-variant** acceptance suite.

The original static requirements are retained:

- all four cardinal orientations;
- near-plane and viewport clipping;
- competing wall owner/tie behavior;
- closed/intermediate/open doors;
- sprite transparency and wall occlusion;
- OBJECT flag-0x10 bypass;
- sprite overlap/slot-order behavior;
- every recovered shade level;
- animated wall/object frame boundaries;
- HUD/floor/ceiling composition.

## State provenance gate

Pass 11 adds and gate that was missing from simple image comparison:
`state.json` must match between the original and candidate captures.

By default, and state mismatch produces `STATE_MISMATCH` rather than and renderer FAIL.

This prevents camera/door/animation timing differences from contaminating the pixel
parity metric.

## Shade suite

The eight recovered remap level values are:

```text
0, 4, 8, 12, 16, 20, 30, 40
```

The suite records both the shade index `0..7` and the associated level value.

## Group coverage

- groups 01–04: cardinal geometry/projection
- group 05: near plane
- groups 06–07: horizontal clipping
- group 08: wall-owner tie
- groups 09–11: door lifecycle rendering
- groups 12–14: sprite visibility/composition
- group 15: all eight shade levels
- group 16: animation boundary + HUD/fill composition

## Batch outputs

The runner aggregates all concrete comparisons into:

- `suite_summary.csv`
- `suite_summary.json`
- `suite_summary.md`

and keeps the complete per-frame diagnostic output from the Pass-9 comparator.

## Tool verification

AND synthetic suite was initialized and tested with:

- one exact original/candidate pair -> PASS;
- one single-pixel modified pair -> FAIL;
- one intentionally mismatched state -> STATE_MISMATCH;
- missing captures -> BLOCKED.

Aggregate status and group status were checked against those outcomes.

## Current project meaning

Game Engine static core remains **100% STATIC CORE**.

Pixel parity is now:

- original capture: automated by Pass 10;
- per-frame exact compare: automated by Pass 9;
- multi-scene acceptance orchestration: automated by Pass 11.

What remains is empirical data acquisition: populate the original/candidate frame pairs
and run the suite.