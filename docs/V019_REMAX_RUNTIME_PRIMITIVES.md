# v0.19 RE MAX — runtime primitives

This pass converts another set of October 1–7 reverse-engineering findings into small, testable primitives while preserving the evidence boundary.

## Promoted as confirmed

- DOS v2.0 player collision footprint: `0x1B` world units.
- GUARD state 06 when both axes are blocked: exactly one RNG value decides the stored-axis flip; bit 0 set selects X, clear selects Y.
- GUARD planner base timer: `RNG % 8 + 8`.
- Difficulty timer scaling: Easy doubles, Medium preserves, Hard halves the base timer, yielding 16–30 / 8–15 / 4–7.
- GUARD state 13 timer: `RNG % 80 + 8` = 8–87.
- Secret-panel geometry retracts toward the opposite endpoint by 2 world units per update.
- Automap and enemy-detector energy drain intervals are 16 and 8 ticks respectively.

The implementation lives in `src/re/N3DV019RuntimePrimitives.hpp/.cpp` and is covered by `tests/v019_runtime_primitives_test.cpp`.

## Intentionally not promoted to exact runtime behavior

The following remain evidence markers rather than gameplay implementation:

- exact player sliding/axis ordering at every boundary;
- exact FAST/MAIN scheduler interleaving;
- projectile-pool-full ammo preservation (strong static evidence, still runtime verification target);
- secret-panel collision/passability transition timing;
- full RNG call ordering from DEMO seed 1;
- boss/class-specific GUARD transitions;
- renderer fixed-point rounding/clipping and final draw order.

The purpose of v0.19 is to narrow the unknown surface without converting a strong hypothesis into false 1:1 certainty.
