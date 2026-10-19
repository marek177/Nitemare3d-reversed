# Nitemare 3D RE MAX v0.63 — DOS2 DEMO RNG35 + scheduler depth

Four independent original DOS2 DEMO sessions now support an increasingly long reproducible shared-RNG prefix:

- first 8 draws: identical in 4/4 sessions;
- first 18 draws: identical in 3/3 eligible sessions;
- first 35 draws: identical in 2/2 eligible sessions.

No sorting or row realignment is used: callsite, before/after 32-bit state and 15-bit result match by ordinal.

The first draw is callsite 0x56A6, seed 1 to state 0x0029E2C0, result 41. The 35th draw is callsite 0x9FE3, state 0x2D128B23 to 0x074D495A, result 1869.

The executed route contains retry bursts at A047 (six calls in one selector invocation) and at 9FE3, including one observed accepted selector after fifteen draws.

One depth-instrumented original run records 103 outer-scheduler entries and 102 returns before trace cutoff, no unmatched exits, maximum scheduler depth 1, and all 35 RNG draws at scheduler depth 1.

This closes D02-C for the captured route. It does not close the full DEMO RNG chronology to EOF, indirect/non-shared RNG paths, E2M10 reentry, or original-vs-port parity.
