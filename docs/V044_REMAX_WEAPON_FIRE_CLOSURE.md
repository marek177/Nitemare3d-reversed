# Nitemare 3D RE MAX v0.44 — weapon FIRE/cadence rejection closure

**Date:** 18 October 2026  
**Method:** RE-first consolidation of SHA-bound DOS v1.2, DOS v2.0 and Win16 v1.10 weapon/cadence evidence. No new original gameplay run is claimed by this repository pass.

## 1. Exact cadence table

The four initialized thresholds are now closed for the audited data images:

```
weapon 0 -> 2
weapon 1 -> 1
weapon 2 -> 3
weapon 3 -> 1
```

The cadence counter is 8-bit and saturates at 255 in slow-update mode. FIRE input calls the cadence gate before the downstream FIRE dispatcher.

Weapons 0, 1 and 2 additionally require a fresh FIRE edge. Weapon 3 (Multi Plasma) bypasses that edge requirement once its threshold is met, creating held-fire auto-repeat.

On accepted cadence, the counter resets to zero **before** the FIRE dispatcher determines whether the shot will later be rejected.

## 2. Failed shots can consume cooldown

Because cadence acceptance/reset precedes the FIRE dispatcher, the following later failures still leave the cadence counter reset:

- no selected weapon after cadence has accepted;
- jam/lock branch;
- unsupported fireMode/action state;
- zero ammo;
- full projectile pool.

This is important for exact timing: a clean-room rewrite must not move the cooldown reset after ammo/pool checks unless intentionally choosing non-compatible behavior.

## 3. Projectile pool-full ordering

For projectile fireMode 2, the first-free scan of the 8 x 42-byte projectile pool occurs **before** the ammo helper.

Therefore:

- all eight slots occupied -> shot rejected;
- ammo helper is not called;
- ammo is not decremented;
- cooldown may already have been consumed by the accepted cadence gate.

If a free slot exists, the ammo helper runs before the new slot is committed to flying state 1.

## 4. Ammo mapping

The audited helper maps weapons as follows:

- weapon 0 and weapon 3 use the same plasma-cell counter;
- weapon 1 uses its own counter;
- weapon 2 (hitscan) uses its own counter.

With ammoBypass set, the helper succeeds without decrementing ammo. The broader in-game meaning/name of that bypass flag should remain evidence-scoped rather than guessed.

## 5. Hitscan and projectile ordering

Weapon 2 uses fireMode 1 and consumes one ammo helper event before scanning GUARD candidates.

Weapons 0/1/3 use fireMode 2 and request one projectile allocation per accepted FIRE call. Multi Plasma is therefore not a multi-slot burst inside one call; its repeated projectiles come from repeated cadence acceptance while FIRE remains held.

The static hitscan loop can continue to later GUARD candidates after a successful damage call. Natural multi-target reachability remains a separate runtime/source-path question.

## 6. selectedWeapon == FF edge

The cadence helper indexes threshold memory with zero-extended selectedWeapon **before** the FIRE routine checks selectedWeapon==FF. There is no local 0..3 bounds check in the cadence helper.

Audited initialized bytes at thresholdBase+FF differ:

- DOS v1.2: 0x33
- DOS v2.0: 0x65
- Win16 v1.10: 0x03

Thus a hypothetical FIRE sample with selectedWeapon==FF can diverge across builds even before the common FIRE routine rejects the unselected weapon.

Example at cadenceCounter=3 and fresh edge:

- DOS v2.0: threshold 0x65 -> cadence denied, counter remains 3.
- Win16 v1.10: threshold 3 -> cadence accepts/resets to 0, then FIRE rejects selectedWeapon==FF.

Natural gameplay reachability of FIRE while currentWeapon==FF remains open. This is a bounded static/data difference, not a claimed user-visible bug.

## 7. Current P0 boundary

This closes more of Weapon FSM 0..3, but not the entire subsystem. Still open:

1. Natural runtime timing of Multi Plasma held-fire over multiple slow ticks.
2. Weapon switch while FIRE is held, especially 2->3 and repeated requests during HUD animation.
3. Natural multi-target hitscan scene and exact GUARD damage order.
4. Jam helper side effects and per-weapon ammo event helper semantics.
5. Win16 parity beyond the audited v1.10 slice and historical build differences.
6. Coupling to projectile impact, slot reuse, RNG and DEMO seed=1 chronology.
7. Exact HUD/framebuffer animation timing.

## 8. Added code

- `src/re/N3DV044WeaponFireClosure.hpp`
- `tests/v044_weapon_fire_closure_test.cpp`
- this report

The model is intentionally bounded and does not pretend to reproduce unknown runtime-only side effects.
