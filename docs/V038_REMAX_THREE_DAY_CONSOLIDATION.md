# Nitemare 3D RE MAX v0.38 — consolidation of 14–16 October 2026 findings

**Date:** 17 October 2026  
**Scope:** selected high-value findings from the previous three research days that were not yet represented together in the public reconstruction code.  
**Evidence boundary:** this release combines SHA-bound original-machine-code findings, isolated arithmetic/state models and existing repository work. It **does not add a new original DOSBox-X/OTVDM gameplay trace, framebuffer zero-diff or audio zero-diff**, so it does not promote end-to-end 1:1 parity.

## 1. What was already merged during the three-day window

The repository already received a large sequence of evidence-scoped updates before v0.38:

- v0.31–v0.33: PUSH obstruction safety, original static closures, and proof that DOS `0E50` is the 6-byte PUSH updater rather than a generic OBJECT scheduler;
- v0.34: render-coupled OBJECT animation paths and DEMO pre-render generation gating;
- v0.35: corrected DOS v2.0 direct RNG census to 22 literal callsites;
- v0.36: cross-version protected-hit/RNG ordering for DOS 1.0/1.7/1.9/2.0;
- v0.37: local DOS v2.0 scheduler catch-up and DEMO FAST gate semantics;
- WORX v0.13–v0.16: progressively deeper original-byte-backed DMA/MIDI/stream routing, ending with the `3A67` MIDI route, `58F8` MPU-401 sender and `5F3E` stream header/router shells.

v0.38 concentrates on recent findings that were still scattered across research reports or only model-tested outside the main N3D evidence layer.

## 2. Win16 joystick calibration difference — v1.8 versus v1.10

For the audited Win16 v1.8 and v1.10 builds, joystick sensitivity is read from `DS:4BDD` and used as the first unsigned `DIV CX` divisor during recalibration. v1.10 adds a 10-byte post-division clamp absent in v1.8: after `OR AX,AX`, signed `JG` keeps positive values; otherwise the stored quotient becomes 1. Thus raw 0 and `0x8000..0xFFFF` are clamped to 1 only when the recalibration branch runs.

**Open:** sensitivity 0 is still unguarded before the first DIV and the cached shortcut path can bypass the new clamp; live reachability is not proven.

## 3. Magic Eye / automap RNG consumption

The Win16 automap dispatcher case 7 consumes the shared RNG stream according to Magic Eye charge `E`:

```text
dots = floor(500 / E^3)
direct RNG calls = 2 * dots
```

For `E=1` this is 500 dots / 1000 direct RNG draws; `E=7` gives 1 dot / 2 draws; `E=8..15` gives zero; local `E=0` arithmetic divides by zero. This is a major DEMO-determinism constraint because the correct LCG is insufficient if map-effect draws occur at a different phase or are omitted.

The same audit narrows the 4096-byte segment-6 state to the automap/map-marking family and confirms SAVE/LOAD interaction without assigning every marker byte a final semantic name.

## 4. Rare door state 4

A GUARD/special path writes door controller state 4. Independent Win16 paths show that state 4 is skipped by ordinary state-2/state-3 motion and explicitly causes an interaction routine to return. Bounded conclusion: **state 4 blocks normal USE and normal movement for that door record until another writer changes it.**

**Open:** natural retail-map reachability, especially mid-motion `2/3 -> 4`, and the complete writer/reactivation census.

## 5. 18-byte door controller versus 14-byte four-VEC record

The two controller families do not finalize on the same update. The 18-byte door moves an endpoint by ±2 and re-tests equality in the same call, so the final movement step can complete immediately. The 14-byte four-VEC record writes state 2 again whenever any coordinate moved; cleanup occurs only on a later call where no coordinate moves. For a bounded `0 -> 4` example, the ordinary door completes on call 2 while the four-VEC cleanup runs on call 3.

## 6. Hamerstein / class 0x16 damage direction and RNG ordering

For the audited DOS v2.0 and Win16 v1.10 builds, normal player-to-GUARD class-`0x16` damage is episode-gated: episode 3 starts from damage 3, other episodes from 0, followed by the existing difficulty transform. Therefore the normal player-weapon path gives zero damage to class 0x16 in E1M10 for all three difficulties.

The opposite class16-to-player amount uses `(episode==3 || storyStage!=0) ? 100 : 33`, then Hard doubles and Easy halves it.

Crucially, the GUARD-hit producer consumes RNG **before** class dispatch overwrites class16 damage to 0 or 3. Early-rejecting an immune hit before the RNG call would shift the shared stream.

## 7. E2M10 timing: signed event gate and raw calibration divisor

The 20th-event gate uses signed `IDIV 20` semantics on the wrapped 16-bit counter, not unsigned `%20`; e.g. `0xFFEC` is signed -20 and is a multiple of 20. Win16 also stores the low 16 bits of the raw render-time average before a separate local clamp and the E2M10 path divides by that raw value, so a raw low word of zero remains a local divide-error condition. These are static/model findings, not observed retail crashes.

## 8. SAVE/graphics 4 KiB initial alias

A corrected DGROUP audit replaced an older false lead. For DOS v1.2 and v2.0 the initial graphics 4 KiB segment equals the fixed SAVE buffer segment at link time: `0x1BDC` and `0x1C08` respectively. This proves the initial alias only; later indirect reassignment remains runtime-open.

## 9. Nested scheduler and mixed projectile-generation lead

Recent analysis narrows two P0 runtime questions: a nested scheduler can overwrite a global FRAME/bucket scratch sample before the parent writes its later gate/deadline, and projectile collision callback entry can observe pre-commit stored X/Y and flying state together with an already-updated line-error field. This mixed-generation state means a nested update is not guaranteed to retrace the identical projectile substep.

## 10. New v0.38 code

- `src/re/N3DV038ThreeDayFindings.hpp` — bounded C++20 reference models for joystick recalibration, Magic Eye RNG budget, door state 4, 18B-vs-14B completion timing, class16 damage, signed every-20 gating, low16 average truncation, mixed projectile callback state and DOS graphics/SAVE initial aliases.
- `tools/n3d_v038_recent_models.py` — data-free Python oracle for the same bounded contracts.
- `tests/v038_three_day_findings_test.cpp` and `tests/test_n3d_v038_recent_models.py` — synthetic/data-free regressions.

## 11. Runtime blockers deliberately left open

v0.38 does **not** close complete DEMO seed=1 RNG chronology, nested FAST/MAIN/IRQ/callback chronology, projectile target-cache ownership/tie order, final-tick secret/remote-door passability, active SAVE/LOAD first-post-load parity, 64,000-byte indexed framebuffer zero-diff/live DAC parity, WORX MPU/OPL/SB DMA/IRQ timing, or full DOS/Win16 runtime equivalence.

No project-wide parity percentage is raised solely because these bounded contracts and synthetic regressions exist.
