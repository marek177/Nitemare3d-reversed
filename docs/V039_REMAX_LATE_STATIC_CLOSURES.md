# Nitemare 3D RE MAX v0.39 — late-day static closures (17 October 2026)

**Evidence mode:** RE-first. This release packages bounded findings from SHA-gated original DOS/Win16 machine-code audits and synthetic reference models. **No original gameplay execution, CPU chronology trace, renderer zero-diff or audio zero-diff is added.**

## 1. E2M10 property-0x40 collision: one P0 hypothesis removed

Across 7 DOS and 5 Win16 builds, the audited E2M10 special-property path returns `AL=1` on normal script return. The collision helper therefore reports a hit, and the DDA branches directly to IMPACT. It does **not** enter the `AL=0` continuation that rereads the DDA step budget.

This closes only that specific candidate mechanism. Other collision callbacks that can return zero, slot reentry/ABA, DEMO/load writers and pointer-derived aliases remain open.

The same audit identified five supported **direct** budget references per normal build family: calibration writer, DEMO record parameter, DEMO playback parameter, DDA input compare and the post-`AL=0` reread. This is not a whole-program alias proof.

## 2. E1M9 radio/state-0x14 timing

The radio transition is global rather than per-guard. Activation puts affected GUARD records in state `0x14` with timer `0x70` (112). In the local state handler:

- updates 1–16 decrement to 96 without the movement helper;
- updates 17–112 run the movement helper;
- update 113 enters with timer 0 and invokes the global stop path.

The global stop scans all GUARDs and restores only those still in state `0x14` to strategy 0, state 6 and timer 1. Because the GUARD scheduler walks upward by index, a stop triggered by an earlier guard can make later guards execute state 6 in the **same** scheduler pass, creating a deterministic intra-pass asymmetry under the stated no-external-mutation assumptions.

A nonlethal hit on strategy 2 during the transformed radio state can leave the target in state 0 and overwrite the saved byte used by the radio restoration path. That guard is then skipped by the local state14-only restore. Long-term visible behavior and natural reachability still require the remaining writer/read graph.

## 3. FIRE cadence gate before the weapon dispatcher

The 86-byte cadence core is statically matched for five Win16 builds and DOS v2.0 after address normalization.

Threshold bytes are:

```
weapon 0: 2
weapon 1: 1
weapon 2: 3
weapon 3: 1
```

Mode 1 (FAST) increments the 8-bit timer with saturation at `0xFF`. Mode 0 checks the selected weapon threshold. Weapons 0–2 also require a fresh FIRE edge; weapon 3 has the held-FIRE exception. An accepted cadence attempt resets the timer **before** the downstream weapon/jam/ammo/guard dispatcher.

Therefore clearing E1M9 TRIGGER2/jam state is not sufficient to prove a shot: cooldown and the correct FIRE edge must also be satisfied.

The original function does not bounds-check the selected-weapon byte before table indexing. Reset code can write `0xFF`, but actual reachability of the out-of-range read at FIRE time remains open and build-dependent.

## 4. Cannon class 0x19: damage zero, RNG still consumed

In all 12 audited original programs, the normal player-to-GUARD damage producer consumes one RNG draw before class dispatch, then class `0x19` overwrites the computed damage with zero. Difficulty transforms preserve zero.

For a live Cannon with positive HP, the ordinary receiver returns on the zero-damage path before pain/death selection. The HP=0 edge is a separate reachability question.

The placed-guard asset scan found 11 Cannon placements in the audited archive, and their low-seven pain/death alternatives are zero. This does not create the Dancers/radio rejection-loop case through normal Cannon hits because the zero-damage receiver exits earlier.

### Pain selector refinement

The ordinary nonlethal receiver writes `GUARD+0x12 = 8` before both direct pain-selector calls. The selector's fast variant-7 shortcut requires `GUARD+0x12 == 0`, so that shortcut is unreachable in the uninterrupted standard nonlethal receiver path. The normal low-seven RNG/rejection path remains relevant.

## 5. DOS scheduler has two local clock-source layers

The DOS scheduler's cache getter and its backend are not interchangeable.

- When `DS:3CCF != 0`, the cache getter reads the IRQ-updated RTC cache.
- When `DS:3CCF == 0`, it calls the backend and refreshes the cache.
- The backend uses BIOS BDA `0040:006C/006E` only for `DS:3CC7==0 && DS:3CCF!=0`; otherwise it uses the system date/time runtime path.

The BIOS branch initializes an origin when zero and returns low32((tick-origin)*55). Precise interrupt interleaving and split-read tearing remain runtime/IF-closure questions.

## 6. Renderer angle normalizer: one-turn correction, not modulo 360

Across 12 audited builds the SIN/COS function bodies and adjacent LUT data are strongly cross-version stable. For retail angles 0..359 the local projection divisors can be proven safe in the audited branches.

The angle normalizer, however, performs only:

```text
if a < 0:   a += 360
if a >=360: a -= 360
```

Thus signed input interval `[-360, 719]` maps into `0..359`; `720` maps to `360`, not zero. Two of ten direct angle-init caller families per build are already statically bounded to safe cardinal values. Eight caller families plus indirect alias writers remain open.

## 7. What v0.39 adds to the repository

- `src/re/N3DV039LateStaticClosures.hpp`
- `tests/v039_late_static_closures_test.cpp`
- `tools/n3d_v039_static_models.py`
- `tests/test_n3d_v039_static_models.py`
- this report
- README/DISCOVERIES/CMake/CI integration

The code deliberately models only bounded local contracts and does not pretend to be the original source.

## 8. Remaining highest-priority blockers

1. Complete path-sensitive DEMO seed=1 RNG ordering, including render/automap/AI consumers.
2. Nested scheduler/IRQ/IF chronology and all clock/deadline aliases.
3. Projectile slot identity/reentry/ABA plus remaining `AL=0` collision paths.
4. Full OBJECT/GUARD writer→reader graph, especially `OBJECT+18`, GUARD stamps and HP.
5. E1M9 accepted-hit reachability through key/door/secret/jam/cadence/projection conditions.
6. Remote/secret wall and SAVE/LOAD alias writers.
7. Pixel-perfect renderer clipping/rounding/sprite/palette output.
8. WORX hardware/IRQ/live-audio timing.

No project-wide 1:1 parity percentage is increased by this static packaging alone.
