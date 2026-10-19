# Nitemare 3D RE MAX v0.75 — recent-days evidence exhaustion checkpoint

**Date:** 19 October 2026

This checkpoint consolidates the distinct, evidence-backed findings discovered after the v0.56 frontier review and avoids creating duplicate releases for material already integrated elsewhere on `main`.

## Newly integrated evidence releases

- **v0.57** — DOS2 DEMO shared-RNG prefix: first 8 entries reproduced in two original runs and an 18-entry scoped chain.
- **v0.58** — DOS1.2 GUARD41 state09→state0A bounded runtime path with RNG #19.
- **v0.59** — Win16 v1.10 E1M1 SAVE→fresh restart→LOAD visual persistence witness.
- **v0.62** — complete DOS2 case-3 21-pass palette fade.
- **v0.63** — DEMO RNG prefix extended to 35 draws with reproducibility counts and scheduler-depth evidence.
- **v0.64** — DOS2 pre-first-update LOAD boundary for HP/ammo/score/X/Y/angle.
- **v0.65** — Win16 v1.10 USER.SAV yaw/X/Y causally verified by one-word mutation and original-game LOAD.
- **v0.66** — DOS2 Read_img_sequence near-heap failure branch and four-class pressure witness.
- **v0.67** — instruction-level DOS2 PCX scanline/VGA plane addressing for 63,040 captured pixel writes.
- **v0.68** — exact UIF record binding, page flip and complete mode-2 fade-in for Main Menu / Please Wait.
- **v0.69** — GUARD41 DOS1.2 post-state0A checkpoint and natural DOS2 dead-state snapshot comparison.
- **v0.70** — 12-build static formatter/LUT, true DOS1.9 unpacked provenance correction and OBJECT+0x18 anchors.
- **v0.71** — exact DOS↔Win16 GAME.PAL 236-color mapping and DOS base-loader contract.
- **v0.72** — first DOS2 DEMO RNG draw bound to actor record 42 and global update counter 58.
- **v0.73** — one natural non-unit-height transparent DOS2 VGA blit closed against the complete 2 MiB VGA snapshot.
- **v0.74** — two-slot DOS2 USER.SAV fixed-record witness; slot0 preserved byte-for-byte while slot1 is appended and loaded.

## Important evidence already integrated concurrently on main

Recent concurrent work already on `main` covers:
- the DOS1.9 indirect/depth audit and corrected `DS:4550` depth formula;
- the v0.61 IMG-textured preview/runtime audit;
- Win16 v1.8 timer-init/cleanup original-byte hazards;
- historical Win16 SFX wrapper/archive diagnostics.

These were not duplicated into new RE-MAX versions here.

## Strongest current closures

### DEMO / RNG
A deterministic original DOS2 shared-wrapper prefix is no longer a one-run observation:
- entries 1–8 reproduce in 4/4 sessions;
- entries 1–18 reproduce in 3/3 eligible sessions;
- entries 1–35 reproduce in 2/2 eligible sessions.

The depth-instrumented 35-draw route has maximum outer-scheduler depth 1 with every RNG draw at depth 1. This does not generalize to E2M10 or to all later DEMO records.

### SAVE / LOAD
DOS2 has a pre-first-update restore boundary with six exact scalar matches, and two concatenated 54,758-byte save records are observed. Win16 v1.10 has a separate 55,015-byte format with causally confirmed yaw/X/Y fields.

Cross-platform save files must therefore remain versioned/adapted; byte-compatible record layout is not assumed.

### Renderer / palette
Original DOS2 now has exact local closures for:
- complete 21-pass fade-out;
- Main Menu and Please Wait UIF asset→64,000-index VGA page matches;
- page flipping;
- complete mode-2 fade-in;
- opaque PCX scanline plane addressing;
- one natural transparent 22×96 blit preserving background;
- DOS↔Win16 palette-data remapping.

These are powerful renderer primitives, but they are still not the canonical original-vs-port gameplay framebuffer zero-diff.

### GUARD / resources
GUARD41 death/post-death evidence now spans DOS1.2 local state09/state0A execution and a natural DOS2 dead-state snapshot. Read_img_sequence near-heap failure is locally tied to `near_malloc(10*N)` and a reproducible four-distinct-class pressure case.

## Evidence that remains intentionally OPEN

The remaining high-value frontier is now dominated by proof composition rather than undiscovered core algorithms:

1. full DEMO RNG/input chronology through EOF, including any indirect/non-wrapper RNG paths;
2. natural E2M10 nested projectile-pool double visit and stale-state/ABA decision;
3. projectile→GUARD instruction-exact collision/damage/SFX for all projectile classes;
4. complete first-post-LOAD world/RNG/cache/projectile deadline chronology;
5. exact secret/remote door per-tick timing and collision interaction;
6. boss/special-state natural reachability and final outcome mappings;
7. full gameplay projection/clipping/shading and canonical 64,000-index original-vs-port zero-diff;
8. Win16 runtime event/timing/audio equivalence, including complete palette remap behavior;
9. active audio/PCM/OPL/MIDI output parity;
10. end-to-end matrix across builds, levels, difficulties and edge scenarios.

## Completion policy

No global 100% claim is made from the count of local closures. Strict complete parity requires a defined original-vs-port acceptance matrix and zero unexplained divergences in state/event ordering, framebuffer/palette output and scoped audio/timing channels.

At this checkpoint, the known high-confidence findings from the recent Library evidence set through the latest 19 October uploads have been either integrated here or identified as already present on `main`.
