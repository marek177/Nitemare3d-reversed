# Nitemare 3D RE MAX v0.52 — DOS v2.0 random-event timer runtime closure

**Date:** 19 October 2026

## Scope

This pass records one fully bounded original DOS v2.0 RNG consumer inside the timed/random-effects substep of the measured top-level update order.

It does not claim a complete RNG ledger or the origin of the seed value.

## Minimal original-runtime trace

A breakpoint-first run starts at the random timer branch with:
- phase byte = 1;
- countdown = 0xFFFF;
- shared RNG state = 1.

The complete local trace then executes:
1. phase `1 -> 0`;
2. RNG wrapper call;
3. RNG state `0x00000001 -> 0x0029E2C0`;
4. return value `41`;
5. countdown `0xFFFF -> 201`.

The exact consumer is therefore:

`160 + (41 % 240) = 201`.

The bounded minimal trace contains 43 CPU instruction events and 17 memory-write events and stops at the configured post-branch PC.

## Independent longer witness

A separate longer trace beginning at the RNG wrapper records:
- 805,890 instructions;
- 181,126 memory-write events;
- the same state transition and return value;
- countdown sequence `201 -> 200 -> 199`;
- global tick progression `85 -> 86 -> 87 -> 88`.

The longer capture is intentionally truncated by its size limit, so it is not a full-game trace.

## Position in the measured top-level update

The previously measured top-level update calls the actor-list traversal at callsite `0x037D` and the timed/random-effects routine at callsite `0x039E`.

The observed RNG timer consumer belongs to the `0x039E` substep and therefore follows the actor traversal in that measured direct order.

This does not imply that every RNG consumer in the engine occurs there.

## Still open

- the runtime writer that initialized the shared RNG state to 1 in this normal E1M1 path;
- all other direct and indirect RNG consumers;
- complete RNG ordering across GUARD/projectile/renderer/audio/DEMO;
- cross-build DOS/Win16 equivalence;
- full timing and framebuffer parity.

No proprietary executable or raw original trace is added to the repository.
