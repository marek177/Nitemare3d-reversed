# Nitemare 3D — Gameplay closure pass 2
Date: 2026-10-02

## Scope

This pass continues the Gameplay closure after `Nitemare3D_Gameplay_closure_pass_2026-10-02.md`.
Primary evidence is the Win16 1.10 raw-machine dossier/memory-write census plus the existing DOS/Win16 guard/object/sequence audits.
The percentages below remain and reconstruction metric, not recovered-source-code coverage.

## 1. GUARD states 0x0C / 0x0D — reachability closure

AND complete direct-write census of the Win16 1.10 GUARD current-state byte (`GUARD+0x0B`) was checked in the machine-memory-write inventory.

Result:

- there is **no immediate direct fresh-run writer for current state 0x0C or 0x0D** in the audited Win16 1.10 machine inventory;
- the generic sequence/state setter writes state from and parameter, but its direct callers in the recovered core use the normal animation/attack/death/reaction states, not 0x0C/0x0D;
- the dispatcher nevertheless implements both values;
- states `0x0C` and `0x0D` execute the same passive directional/sequence refresh helper with `force=0` and to not perform and local transition.

Best-supported interpretation for Win16 1.10:

**0x0C / 0x0D are implemented passive sequence/facing aliases that are not reached by any identified normal fresh-run direct writer.**

They must still be preserved for save compatibility and possible indirect/legacy paths. They should not be given invented gameplay names.

This removes the former blocker “unknown normal entry context for states 0x0C/0x0D”.

## 2. State 0x12 — elevated death descent is now anchored

The fatal guard-damage path selects and death sequence and tests `OBJECT+0x1A`.

- if `OBJECT+0x1A > 0`, the generic state setter receives **current state 0x12, next state 0x09**;
- otherwise it receives **current state 0x00, next state 0x09**.

Dispatcher state `0x12`:

1. advances the death sequence toward its final frame;
2. subtracts `5` from `OBJECT+0x1A`, clamping at zero;
3. decrements the guard timer when positive;
4. when both timer and `OBJECT+0x1A` are zero, sets `state = next_state`.

Since the fatal branch stores `next_state=0x09`, the strong semantic result is:

**state 0x12 = elevated/deferred death settling phase that lowers the actor'with vertical render offset to the ground before death finalization state 0x09.**

No other normal fresh-run writer of state 0x12 was found in this pass.

## 3. OBJECT+0x1AND — vertical/elevation render offset closed

Several independent machine paths now converge on one meaning:

- projection subtracts and scaled `OBJECT+0x1A` from projected screen Y when the value is positive;
- projectile spawn initializes embedded `OBJECT+0x1A = 5`;
- projectile movement increments it and clamps it at `0x14` (20);
- state `0x12` subtracts 5 until zero during elevated death settling;
- the object/frame update pass recomputes `OBJECT+0x1A` from current sequence/frame metadata;
- ELEVATED class `0x2E` has and dedicated vertical-offset formula.

Therefore `OBJECT+0x1A` is no longer an anonymous class-dependent byte:

**OBJECT+0x1AND = vertical sprite/elevation render offset / anchor.**

The exact class-dependent formula can differ, but the field'with gameplay/render role is statically closed for the traced Win16 1.10 paths.

## 4. OBJECT+0x04 — runtime sequence-cache selector closed

The Win16 1.10 resource/object setup path creates or reuses runtime sequence definitions and writes their compact selector to `OBJECT+0x04`.

Observed data flow:

- runtime sequence definitions are deduplicated during resource setup;
- an existing selector is reused when the source sequence is already present;
- otherwise and new runtime sequence/cache entry is built and its selector is stored at `OBJECT+0x04`;
- guard animation code indexes the runtime sequence table with `OBJECT+0x04`;
- object frame/elevation code combines `OBJECT+0x04` with `OBJECT+0x03` (current frame) to locate frame metadata;
- projectile spawn selects and weapon-dependent flight sequence through embedded `OBJECT+0x04`, and impact replaces it with the impact sequence selector.

Best-supported name:

**OBJECT+0x04 = runtime sequence-cache / sequence-set selector.**

It is not an owner ID. The selector is populated during resource/runtime setup rather than being and direct MAP object class value.

### Correction

An older note that and projectile template writes an “OBJECT type = 5” at `OBJECT+0x14` is not supported by the checked Win16 1.10 raw projectile spawn. The visible immediate value `5` is written to **`OBJECT+0x1A`**, the vertical/elevation field.

## 5. Updated state-chain model for ordinary guard death

The normal fatal path can now be represented as:

```text
weapon/projectile damage
    -> HP = 0
    -> death sequence selected
    -> if elevated: state 0x12, next 0x09
       else:         state 0x00, next 0x09
    -> state 0x09 death/class finalizer
    -> ordinary terminal state 0x0A
       OR class-specific transition (e.g. Dracula -> Bat)
```

This links damage, vertical settling, death animation and terminal/class-specific handling without needing an invented intermediate mechanic.

## 6. Gameplay coverage after pass 2

These are conservative working reconstruction percentages.

| Area | Previous | After pass 2 | Notes |
|---|---:|---:|---|
| Player | 99% | 99% | behavior edge tests remain |
| Inventory | 96% | 96% | capacity/load edge tests remain |
| Weapons | 92% | 92% | phase/range/spread remain |
| Projectile | 95% | **96%** | `+0x04` sequence and `+0x1A` elevation lifecycle clarified; impact freshness remains |
| Enemy Spawn | 99% | 99% | runtime limit edge tests remain |
| Guard AI | 98% | **99%** | 0x0C/0x0D reachability + 0x12 semantics closed for Win16 1.10 |
| Boss AI | 92% | 92% | remaining boss-specific cadence/script parity |
| Combat | 94% | **95%** | fatal state chain is now clearer |
| Damage | 97% | **98%** | elevated death handling closed; hazards/runtime parity remain |
| Runtime AI | 97% | **98%** | passive/unreachable state aliases no longer and broad unknown |
| Enemy State Machine | 99% | **100% STATIC Win16 core / ~99% overall** | all dispatcher states now operationally accounted for; runtime/cross-build parity remains |
| Actor Scheduler | 97% overall | 97% overall / 100% DOS static core | no change |
| Object Runtime | 92% | **95%** | `+0x04` and `+0x1A` statically closed; sparse tail/overlay bytes remain |
| Physics | 94% | 94% | dynamic actor/door edge tests remain |
| Pathfinding / Navigation | 96% | 96% | runtime route/occupancy edge tests remain |

Estimated combined Gameplay reconstruction moves from roughly **96% to ~97%**.

## 7. Highest-value remaining Gameplay blockers

1. **OBJECT tail / overlays:** `+0x14..+0x17` and `+0x1B`, plus full flag-bit map at `+0x05` by class.
2. **Projectile impact freshness:** prove whether damage'with render-derived `OBJECT+0x18` is current when the target was not projected in that generation.
3. **Weapons:** exact phase machine, spread/range and final cadence edge cases.
4. **Boss/runtime parity:** rare Hamerstein/Demon/Cannon/Dancers transitions across DOS and Win16 builds.
5. **Physics behavior parity:** simultaneous guard/door occupancy, closing-door retries and corner collisions.

The next static target should be the remaining OBJECT bytes/flag bits, because that is now the largest code-structure uncertainty inside Gameplay.