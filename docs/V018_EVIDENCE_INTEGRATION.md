# Nitemare 3D reconstruction v0.18 — evidence integration

v0.18 promotes the October 1–7, 2026 reverse-engineering findings into source code while keeping build-specific facts separate from unresolved hypotheses.

## Promoted facts

- DOS v2.0 player world coordinates: `DS:4162/4164`.
- Player movement chain: `6914 -> 6488 -> 6378 -> 688C`.
- DOS v2.0 projectile/effect pool: base `DS:41B6`, 8 slots, `0x2A` bytes each.
- DOS v2.0 GUARD pool: base `DS:264E`, stride `0x1A`.
- Weapon cadence thresholds: `[2,1,3,1]`.
- Exact shared RNG formula:
  `state = state * 214013 + 2531011`,
  result `(state >> 16) & 0x7fff`.
- 20 direct DOS v2.0 RNG callsites are encoded for audit/regression use.
- Secret-panel record: base `34F6`, 14-byte record with four VEC references, MAP pointer and runtime state.
- Renderer anchors: SPAN count/pool/stride, OWNER table, VEC count/pool.
- Scheduler anchors: FAST `C150`, outer scheduler `C1A8`, MAIN `C0D8`.

## Corrections carried forward

The following older assumptions are intentionally not encoded as universal facts:

- `3:4BF6/4BF8` are not universal player X/Y addresses.
- `7E5E`, `6EC8`, and `9806` are build-specific.
- A `+0x50` loop stride must not be treated as an OBJECT record stride.
- `70D6` is not promoted as the OBJECT scheduler.
- Secret panels are represented as segmented VEC retraction, not a rigid Wolf3D-style pushwall.

## Still open

v0.18 does not claim closure for:

- exact FAST/MAIN runtime interleaving;
- RNG chronology from DEMO seed 1 through the first gameplay input;
- player sliding edge ordering;
- secret-panel passability on every movement tick;
- GUARD class/boss overrides;
- projectile stale-cache behavior;
- pixel-perfect renderer rounding/clipping/order.

Those remain runtime-verification targets rather than hard-coded behavior.
