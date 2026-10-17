# Nitemare 3D RE MAX v0.40 — projectile one-level reentry / ABA narrowing

**Date:** 17 October 2026  
**Method:** RE-first combination of already SHA-gated original-byte findings. The relevant projectile pool/state control flow is verified across nine DOS/Win16 builds in the scheduler v0.45–v0.48 line; the E2M10 property-`0x40` normal-return semantics are independently verified across twelve builds in v0.72. This package adds a bounded logical closure and regression models. **No original game process is executed.**

## 1. Starting point

During an outer projectile movement, the collision callback can reach the E2M10 script and, on the 20th special hit, enter a nested outer scheduler **before** the suspended parent movement writes `slot.state=2`.

Therefore a nested projectile-pool pass may revisit the same physical slot while it still contains `state=1`. This reentry is real at the control-flow/data-flow level; natural frame-due reachability and external callback timing remain separate questions.

## 2. New local negative closure: one state-1 pool visit cannot free the slot

The pool dispatches on the state read at the beginning of that slot visit.

For a visit that **enters with state 1**:

- the state-1 arm runs movement even when its animation deadline is still in the future;
- with no collision, the standard local path leaves the slot in state 1;
- with an accepted collision, movement writes state 2 only **after** the collision callback returns;
- the pool then continues toward the end of the current slot and the next slot;
- there is **no local fall-through** from this state-1 visit into the state-2 expiry arm.

The state-2 arm that can write state 0 is therefore available only on a **later pool visit that begins with state 2**.

This removes the old simplified sequence:

```
one nested visit:
state1 -> collision -> state2 -> state2 expiry -> state0
```

from the standard pool control flow.

## 3. Allocator consequence inside that same nested scheduler invocation

In the audited outer scheduler ordering, the projectile pool executes before player input/FIRE. The player projectile allocator selects a free slot; the reconstructed lifecycle treats state 0 as free.

After the nested pool's revisit of the suspended slot:

- no collision => slot remains state 1;
- collision => slot is state 2;
- neither outcome is state 0.

Therefore the **later input/FIRE allocator in that same nested outer-scheduler invocation cannot reuse this same slot through the standard lifecycle**.

This is a stronger negative closure than simply saying the slot is revisited.

## 4. Same E2M10 hit path does not immediately create a second nesting level

The outer triggering hit advances the E2M10 counter `19 -> 20`, which satisfies the signed `IDIV 20` remainder-zero gate and can enter the nested wait/scheduler path.

If the nested revisit of the same projectile again reaches the same property-`0x40` E2M10 script, the counter advances `20 -> 21`. That is **not** another multiple of 20, so the same direct script path does not immediately launch a second nested wait/scheduler.

Combined with the state-1 dispatch result, the direct one-level self-reentry path cannot produce:

```
state1 -> nested pool -> state2 -> state0 -> allocator reuses same slot
```

before control returns to the suspended parent, using only the standard pool + same E2M10 property-`0x40` recursion + later input allocator.

## 5. What remains open

This is **not** a global proof that projectile ABA is impossible.

A same-slot ABA still requires investigation if any of the following can occur before the suspended parent commits its post-callback fields:

1. another subsystem/callback independently enters the scheduler a second time;
2. an indirect or aliased writer sets the slot state to 0;
3. SAVE/LOAD, reset or bulk-copy code mutates the pool;
4. an IRQ or external callback reaches game-state mutation code;
5. a different collision/event route creates another nested pool visit;
6. a second pool entry begins with the slot already in state 2 and its frame/descriptor test frees it;
7. a later allocator runs only after such a genuine free.

The exact descriptor `N`, impact frame state/deadline and all transitive writers remain part of the next static frontier.

## 6. Implementation impact

A clean-room port must not:

- write `state=2` before the original collision callback if exact reentry behavior is desired;
- process the state-2 expiry arm immediately after a state-1 collision in the same slot visit;
- treat a nested revisit as automatically implying slot reuse.

The v0.40 reference code models only these bounded invariants.

## 7. Added files

- `src/re/N3DV040ProjectileReentryClosure.hpp`
- `tests/v040_projectile_reentry_closure_test.cpp`
- `tools/n3d_v040_projectile_reentry.py`
- `tests/test_n3d_v040_projectile_reentry.py`
- this report

## 8. Next RE-first target

Continue with the remaining condition for a genuine ABA:

**Can any statically reachable second nested scheduler/pool entry occur while the suspended parent has not resumed, and can that second entry start the same slot in state 2 and free it?**

That requires the transitive nested-callback census plus the impact descriptor/frame/deadline value set. Runtime should remain fallback-only for IRQ/external interleaving that cannot be statically decided.
