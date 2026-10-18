# Nitemare 3D RE MAX v0.45 — weapon switch / frame-order closure

**Date:** 18 October 2026  
**Method:** static composition of already SHA-bound DOS weapon-switch, HUD-animation, scheduler and FIRE evidence. No new original gameplay runtime is claimed in this pass.

## 1. Weapon selection request is not an immediate swap when a weapon is active

For the checked DOS switch routine:

- if current weapon is `0xFF`, the requested weapon is installed immediately, its fireMode is recomputed (weapon 2 -> hitscan mode 1, others -> projectile mode 2), and HUD phase becomes Raise;
- if a weapon is already active and a different weapon is requested, only `pending` is replaced;
- if HUD phase was Idle, that request starts Lower;
- requests during an already active Raise/Lower phase do not locally force a different phase.

Therefore repeated selection requests can overwrite `pending` while the old weapon remains current.

A request equal to the current weapon does not locally clear an already stored different pending request.

## 2. Same input call: selection request precedes FIRE

The active-input function contains the weapon-selection request before the later FIRE block.

This creates two distinct cases.

### current == FF

The switch routine directly installs the requested weapon. The later FIRE block in the same input call can therefore see the new weapon/fireMode, subject to cadence, held/edge input, jam, ammo and pool rules.

### current already valid

The request only changes `pending` and possibly HUD phase. No HUD commit runs inside that same request. The later FIRE block in the same input call therefore still sees the **old current weapon and old fireMode**.

This closes a common clean-room ambiguity: requesting weapon 3 while weapon 2 is active does not make the subsequent FIRE block in that same input invocation automatically act as Multi Plasma.

## 3. Direct parent frame order

For the checked DOS direct parent main-frame path, the relevant ordering is:

```text
weapon/HUD render update
-> projectile pool update
-> present/synchronization
-> active gameplay input
```

The weapon overlay transition belongs to the pre-input render/HUD side of that frame.

Consequences:

1. A weapon request made by gameplay input happens **after** that frame's HUD transition opportunity.
2. In the direct non-reentrant parent path, a pending switch created by input cannot be committed by the already-finished HUD updater in that same frame.
3. When a later frame's HUD Lower step reaches zero and commits pending -> current, the subsequent gameplay input of that same frame can already observe the new current weapon and fireMode.
4. The projectile pool pass for that frame happened before input. Therefore a projectile newly allocated by FIRE at the end of the frame cannot be processed by that already-completed direct parent projectile pass.

This is a static direct-path statement. Nested/reentrant outer-scheduler calls remain a separate blocker.

## 4. Multi Plasma first accepted FIRE after commit

Weapon 3 threshold is 1 and does not require a fresh FIRE edge.

The switch/HUD routines do not explicitly reset the cadence counter. Thus, on a direct frame where HUD Lower commits pending weapon 3 before input:

- if FIRE is still held;
- and cadenceCounter is already >= 1;
- and later FIRE acceptance checks pass;

the Multi Plasma cadence gate may accept a shot **in the same frame as the HUD commit**.

This does not prove wall-clock timing or that shipped input always permits holding FIRE through the switch. It closes the static ordering needed to design the runtime acceptance test.

## 5. Cooldown transfer

Weapon switching does not locally reset the cadence counter. The counter therefore carries across selector changes unless changed by:

- the slow-update cadence increment;
- an accepted cadence attempt, which resets it;
- another writer not part of this bounded switch/HUD contract.

Because thresholds differ per weapon, carried cooldown can change first-shot timing after commit.

## 6. New projectile first movement

In the direct parent scheduler path:

```text
projectile update -> ... -> input/FIRE -> allocate new slot
```

So a newly spawned projectile is not revisited by the already-completed direct parent projectile updater of that same frame.

The remaining question is whether nested/reentrant scheduling after or inside input can create an additional projectile-pool visit before the parent frame returns. That is intentionally still OPEN.

## 7. Remaining P0/P1 work

- natural held-FIRE switch trace, especially 2 -> 3;
- exact HUD position/limit timing across real scheduler buckets;
- repeated requests during Raise and Lower with shipped input;
- nested scheduler after input and first movement of the newly allocated projectile;
- projectile deadline and impact timing under Multi Plasma saturation;
- DEMO seed=1 RNG chronology;
- framebuffer/HUD zero-diff around the commit frame.

## 8. Added files

- `src/re/N3DV045WeaponSwitchFrameOrder.hpp`
- `tests/v045_weapon_switch_frame_order_test.cpp`
- this report

The model intentionally preserves only statically supported local/direct-parent semantics and does not claim runtime 1:1 acceptance.
