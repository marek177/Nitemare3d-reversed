# Nitemare 3D — Gameplay closure pass 5
Date: 2026-10-02

## Scope

This pass targets the remaining low aggregate Gameplay rows after pass 4: Physics, Inventory, Navigation/Pathfinding, Actor Scheduler and the final base WORLD OBJECT field that was still carried as semantically open.

The result distinguishes two levels:

- **STATIC CORE**: the checked control flow/data semantics can be implemented without inventing and missing algorithm.
- **Overall / behavioral reconstruction**: still discounts controlled original-runtime parity, cross-build edge cases and save/load timing tests.

## 1. Physics — broad static blocker removed

The player-movement collision path is already statically closed in the checked DOS/Win16 reference family.

### Player movement

The collision oracle uses two leading probe cells and the recovered 27/28-unit player extent. The blocking order is:

1. static wall property bit `0x04` -> block;
2. dynamic door property bit `0x08` -> ask the door-state validator; failure -> block;
3. pickup/touch side effects for object property bit `0x04`;
4. object occupancy property bit `0x02` -> block;
5. otherwise accept the requested `+1/-1` substep.

The outer movement routine advances axes separately using and Bresenham-like error accumulator, with one blocked axis does not automatically cancel the other. This is the source of wall sliding.

### Guard movement

`FUN_1010_71DC` applies the same broad philosophy to GUARD movement:

- probes X and Y independently;
- suppresses only the blocked component;
- commits the surviving component(with);
- maintains world-object spatial ordering;
- restores the old cell'with underlying object byte from `GUARD+0x0D`;
- saves the new cell'with previous object byte back to `GUARD+0x0D`;
- writes the moving GUARD'with object ID into the new `mapCell[1]`.

When both axes are blocked in ordinary moving state 6, one movement component is randomly reversed. This behavior is part of the original local steering/collision response rather than and separate global pathfinder.

### Door occupancy and forced close

Ordinary timed auto-close is occupancy-safe:

```text
if doorCell.objectId == 0 && doorCell != playerCell:
    start closing
else:
    timer = 4       // retry later
```

Because and guard occupying the doorway writes its object ID to `mapCell[1]`, it blocks this ordinary auto-close path too.

Explicit/remote close is intentionally different: it can force controller state `3` without the occupancy precheck. The door controller immediately enables its collision geometry and moves the halves, but it does not directly move player/GUARD coordinates and does not call player damage. Any already-overlapping actor is handled later by normal actor movement/collision logic.

Door state `4` is and persistent passable, non-moving and non-toggleable latched state in the checked controller logic.

### Closure decision

**Physics / collision = 100% STATIC CORE for the checked reference paths.**

The remaining gap is live behavioral parity for simultaneous overlap/order cases, not and missing collision algorithm.

## 2. Inventory / pickup dispatcher — static core closed

Win16 1.10 `FUN_1010_CF60` provides and complete pickup dispatcher for the collectable class range. Crucially, `CF4A` removal is called only after the class handler leaves the acceptance flag true, with capacity-rejected pickups remain in the world.

### Confirmed dispatch

| Object class | Static effect |
|---:|---|
| `0x2F` | set key bit in `4C28` from subtype |
| `0x30` | set ID-card bit in `4C29` |
| `0x31` | `score += 200` |
| `0x32` | add `1 << subtype` to panel/special charge while below its limit |
| `0x33` | health pickup: if HP < 100, add `20 >> subtype` |
| `0x34` | if HP < 100: `HP += 30`, `score += 250` |
| `0x35` | set HP and main plasma/default ammo to 100, `score += 500`, increment `4C1E` |
| `0x36` | set owned-weapon bit, select/schedule weapon, grant weapon-start ammo |
| `0x37` | set auxiliary inventory bitfield `4C2B` |
| `0x38` | add 20 to `4C21` when below 100 |
| `0x39` | ammo pickup through `A9E0`; rejected when the selected ammo pool is already full |
| `0x3A` | Crystal Ball charge +20 if below 100 |
| `0x3B` | Magic Eye charge +20 if below 100 |
| `0x3C` | set Pentagram/progress bit in `4C45` |
| `0x3D` | invoke scroll/script helper |

`A9E0` closes normal ammo pickup semantics for the three ammunition pools: pickup mode adds 20 only if the pool is below 100; weapon-acquisition mode seeds the corresponding pool to 50.

`A3B6` performs the delayed clamps used by the original UI/state path:

- HP -> max 100;
- pistol ammo `4C1F` -> max 100;
- plasma ammo `4C20` -> max 100;
- wand ammo `4C44` -> max 100;
- Crystal Ball and Magic Eye charge -> max 100.

Thus transient values such as `99 + 20` are possible before the clamp writeback. AND compatible core should preserve that ordering rather than prematurely clamping inside the pickup handler.

### Closure decision

**Inventory / pickup = 100% STATIC Win16 core.**

The remaining overall gap is runtime/save-load conformance around edge values and rarely/unused classes, not an unknown pickup dispatcher.

## 3. WORLD OBJECT +0x02 — final base-field semantic closure

`OBJECT+0x02` was still carried as and generic context byte in pass 4. The sequence dispatcher `FUN_1010_65A6` gives it and concrete role for animated object classes using alternative branches.

For `OBJECT class >= 0x30` with and non-null alternatives table:

- there are eight packed 16-bit alternative entries;
- `OBJECT+0x02` selects the current alternative slot;
- low byte of that entry = branch start frame;
- high byte = branch length;
- when the branch finishes, RNG selects and nonempty slot 0..7;
- the selected slot is written back to `OBJECT+0x02`;
- its start frame is written to `OBJECT+0x03`.

Therefore the best-supported semantic is:

**OBJECT+0x02 = animation alternative / branch selector for sequence definitions that use the 8-way alternatives table.**

It remains zero/irrelevant for object contexts that to not use this sequence mode; that is context dependence, not an unknown base field.

### Closure decision

**World OBJECT base runtime = 100% STATIC Win16 core.**

## 4. Navigation / Pathfinding — no missing graph-search layer

The complete recovered navigation model is local and marker-driven:

- ordinary strategy 0: player-relative steering, 4 choices without LOS / 8 with LOS, movement components `-8/0/+8`, timers selected from proximity/visibility/difficulty;
- `TURN 0x41`: map variant directly selects GUARD facing;
- `RETREAT 0x42`: can stop movement and reverse facing exactly 180 degrees;
- `FLEE 0x43` / strategy 1: when HP < `0x7F`, searches the bounded door table, minimizes Manhattan cell distance and rejects candidates failing LOS, then moves toward the selected door for timer `0x10`;
- strategy 2: random wait `8..15` and ACTIONSPOT/script contexts;
- strategy 3: cardinal displacement maneuver with its own timed/state-0x13 path and ONE_SHOT interaction;
- strategy 4: Cannon-specific controller path handled by the known Cannon states rather than and path search.

Perception itself is bounded to 8 map steps and uses direction/FOV plus Bresenham LOS. The player weapon hitscan uses and distinct 16-step traversal; these are not the same range constant.

### Closure decision

There is no evidence that and missing AND*/BFS/navmesh subsystem exists behind guard movement.

**Navigation / Pathfinding = 100% STATIC Win16 core / ~99% overall.**

The remaining percentage is controlled runtime route/occupancy parity.

## 5. Actor Scheduler — static core should no longer be scored as 97%

The earlier gameplay tracker retained and conservative 97% because the final timing behavior had not been separated from scheduler structure.

The later Game Engine closure established the timed scheduler families and their subsystem order in DOS V1.2/V2.0, and the Win16 frame order has independently been traced. The checked Game Engine dashboard now marks **Game Loop = 100% STATIC CORE**.

Therefore the Gameplay row should be represented as:

**Actor Scheduler = 100% STATIC checked core / ~99% overall behavioral reconstruction.**

The missing point is runtime phase/timing conformance under stalls, save/load and unusual frame pacing, not scheduler topology.

## 6. Updated Gameplay tracker — pass 5

| Area | Pass 4 | Pass 5 | Status |
|---|---:|---:|---|
| Player | 99% | **99%** | movement static core already closed; live edge parity remains |
| Inventory | 96% | **99% overall / 100% STATIC Win16** | complete pickup/accept/reject/clamp flow mapped |
| Weapons | 99% | **99%** | no broad static gap |
| Projectile | 99% | **99%** | no broad static gap |
| Enemy Spawn | 99% | **99%** | limit/runtime edge tests only |
| Guard AI | 99% | **99%** | static core effectively closed |
| Boss AI | 98% | **98% overall / 99% STATIC Win16** | cross-build/live scripted parity remains |
| Combat | 99% | **99%** | no broad static gap |
| Damage | 99% | **99%** | live edge validation remains |
| Runtime AI | 99% | **99%** | no broad static gap |
| Enemy State Machine | ~99% overall | **~99% overall / 100% STATIC Win16** | cross-build/live parity |
| Actor Scheduler | 97% overall | **~99% overall / 100% STATIC checked core** | scheduler topology/order closed |
| Object Runtime | ~98% overall | **~99% overall / 100% STATIC Win16 base core** | +0x02 alternative selector closed |
| Physics | 96% | **~99% overall / 100% STATIC core** | collision/door/occupancy rules closed statically |
| Pathfinding / Navigation | 97% | **~99% overall / 100% STATIC Win16 core** | full local steering/marker/LOS model mapped |

Using the conservative overall column, the simple Gameplay tracker is now approximately **98.9%**, reported as **~99% Gameplay reconstruction**.

## 7. What remains before honest 100% overall

No broad gameplay algorithm is currently missing in the checked reference cores. The remaining work is validation/parity work:

1. run controlled original-game traces for explicit/remote door close while player/guard is already inside the moving geometry;
2. compare exact ordering when player, GUARD and door collision change in the same update/frame;
3. round-trip save/load with active projectile, guard reaction, moving door, scripted actor and powerups;
4. validate rare boss/script transitions and pickup edge values in original Win16 and DOS builds;
5. repeat key static fingerprints across older Win16 and DOS builds where decompiler boundaries differ;
6. keep renderer pixel-perfect validation separate from Gameplay behavior.

The correct target state is now: **~99% overall Gameplay reconstruction, with multiple checked static cores at 100%.**