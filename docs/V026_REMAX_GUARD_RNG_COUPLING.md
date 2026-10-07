# v0.26 RE MAX — GUARD RNG/state coupling

v0.26 binds the known DOS v2.0 RNG callsites to GUARD/animation consumers only where the current evidence supports the association.

## Confirmed couplings

### 0x2478 — animation variant

The animation path uses `RNG & 7` with a rejection loop. This is important because one animation decision can consume a variable number of draws and shift the shared RNG stream.

### 0x525E — GUARD state 06 blocked-axis decision

When both axes are blocked:

- exactly one RNG draw is consumed;
- bit 0 set -> flip stored X direction;
- bit 0 clear -> flip stored Y direction;
- no second movement commit is performed.

### 0x58A7 — GUARD state 13 timer

Exactly one RNG draw feeds:

`timer = RNG % 80 + 8`

giving 8..87.

## Strong but not fully closed

The planner cluster:

- `5666`
- `56A6`
- `573F`

is bound to GUARD planner/timer-direction logic with STRONG confidence. The precise per-call consumer/order remains a runtime-trace target.

`85AD` is bound to damage/pain ordering with STRONG confidence, but its exact branch consumer remains to be closed by trace.

## Unassigned direct callsites

All other known direct DOS v2.0 RNG callsites remain explicitly `Unassigned / OPEN`.

They are preserved in the same 20-entry table so future traces can promote them one at a time without changing the callsite census.

## Why this matters for DEMO parity

The RNG stream is shared across AI, animation, damage and other systems. A single extra draw changes every later result.

The closure criterion remains:

1. start from DEMO seed 1;
2. record every direct RNG caller in order;
3. validate state_before/state_after/result;
4. bind the consumer;
5. identify the first unexpected/missing draw.

v0.26 provides the static coupling registry needed for that comparison.
