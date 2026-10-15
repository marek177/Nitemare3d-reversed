# v0.20 RE MAX — verification harness

v0.20 does not invent the still-missing scheduler order. It adds machinery for proving it.

## What is encoded as confirmed

The DOS v2.0 timing/scheduler anchors from the October audit are now represented in code:

- IRQ8: `BCC2`
- clock path: `BE74`
- slow bucket: `BEB4`
- frame bucket: `BEF4`
- FAST tick: `C150`
- MAIN/update/render path: `C0D8`
- outer scheduler: `C1A8`

The original v0.20 registry listed 20 apparent direct RNG callsites.
**Correction v0.35 (2026-10-15):** exhaustive literal far-CALL opcode scan of
the fingerprinted DOS v2.0 image finds **22**, adding `8860` and `886C`
from the incoming-damage class dispatcher. The C++ table and trace verifier
have been corrected. See [v0.35](V035_REMAX_RNG_22_CALLSITE_CENSUS.md).
These are 22 static callsites, not a bound on dynamic draws or indirect calls.

## What remains explicitly open

`0800:0E50` is recorded only as an OBJECT-runtime candidate. The exact iteration order, timer mutation, movement/collision and deactivation semantics are not promoted to a scheduler implementation.

Likewise, v0.20 does not encode a fabricated FAST/MAIN subsystem order. Runtime traces must establish that order.

## New verification helpers

`N3DV020VerificationHarness` adds:

- validation of RNG trace entries against the exact LCG transition;
- validation that a caller belongs to the known direct-callsite set;
- scheduler-anchor classification;
- a first-divergence helper for comparing expected and observed address traces.

This is designed for DOSBox-X/AutoRE capture data:

```
caller, RNG_before, RNG_after, result
scheduler address sequence
```

The acceptance target remains:

- same seed;
- same ordered RNG callers;
- same RNG state after every call;
- same scheduler anchor sequence;
- identify the first divergent call/address instead of only comparing final state.

## Next closure step

Feed one controlled DOS v2.0 tick and the DEMO seed=1 pre-input trace into this harness. Once the observed order is repeatable, that sequence can be promoted from OPEN to CONFIRMED in a later version.

## v0.33 correction — original bytes identify `0E50` (2026-10-14)

The v0.20 hypothesis that `0E50` might be the generic OBJECT updater is **superseded**. The fingerprinted DOS v2.0 function at `0E50` iterates a six-byte PUSH record pool; Win16 v1.10 `3:2210` is instruction-identical after masking 20 differing address-operand bytes in a 292-byte routine. It updates PUSH-owned OBJECT coordinates, MAP cell links, sorted spatial indices, and decrements the PUSH countdown only on an accepted step. See [v0.33 binary proof](V033_REMAX_PUSH_SCHEDULER_BINARY_CLOSURE.md). This correction does **not** establish complete OBJECT animation iteration or total FAST/MAIN timing.
