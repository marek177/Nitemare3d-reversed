# Nitemare 3D RE MAX v0.57 — DOS2 DEMO RNG chain

**Date:** 19 October 2026

Two independent original DOS2 trace sessions now share an exactly matching first-eight-entry RNG prefix. A longer original run records eighteen shared-wrapper RNG calls from seed 1.

The first eight callsite/state/result tuples are therefore independently reproduced. Entries 9–18 are a scoped witness from one longer run and are deliberately not promoted to independently replicated status.

The observed eighteen-entry callsite sequence is:

`56A6, 85AD, A047×6, 5582×2, 56A6, 573F, 56A6×2, 85AD, 9FE3×3`.

Every entry follows the exact 32-bit LCG recurrence and 15-bit return rule. Retry loops are visible in real execution: `A047` consumes six consecutive draws and `9FE3` consumes three.

This release closes **D02-A**: exact reproducibility of the first eight shared-wrapper draws across two independent original runs. It also records **D02-B**: the first eighteen shared-wrapper draws in one original run.

Still open: independent replication of draws 9–18, any direct CRT-rand paths outside the shared wrapper census, scheduler depth for every draw, later DEMO records, EOF, Win16 correspondence, and original-vs-port differential equality.
