# GUARD strategy matrix + active states 0x02–0x08 closure — Win16 1.10 — 2026-09-29

## Result

The Win16 1.10 GUARD strategy byte at `GUARD+0x0A` has a closed normal-runtime value set:

```text
0 = default movement / player-biased roam-chase planner
1 = wounded door-seeking behavior
2 = route-marker movement
3 = gargoyle / ONE_SHOT timed movement
4 = Cannon behavior
```

No normal gameplay writer of strategy `5` was recovered. Older notes referring to "strategy 5" were conflating another state/value and should not be used.

This closes the **strategy ID / writer / primary control-flow matrix to 100% for Win16 1.10**. It does not mean every original designer-facing name is known.

The active state cycle `0x02..0x08` is also now functionally named from direct side effects. Its control flow is closed; remaining uncertainty is primarily exact loaded sequence/IMG/SND presentation rather than what the states do.

## Strategy writers

Normal initialization starts with strategy 0.

Class-specific overrides in `3:B02C`:

| Source | Strategy |
|---|---:|
| object class `0x12` Cemetery Gargoyle | 3 |
| object class `0x13` Garden Gargoyle | 3 |
| object class `0x19` Cannon | 4 |

Map-marker overrides in the same initializer:

| wall class under actor | retail family / evidence | Strategy |
|---:|---|---:|
| `0x42` | RETREAT | 2 |
| `0x43` | third TURN/RETREAT/FLEE-family class in older audit; supplied maps use zero cells | 1 |
| `0x46` | ACTIONSPOT | 2 |
| anything else | no strategy override | 0 |

Reset writers:

- strategy-3 state `0x13` completion clears strategy to 0 before entering state 2;
- strategy-1 door-maneuver state `0x11` completion clears strategy to 0 before returning state 7;
- Radio/Dancers restore path clears strategy to 0 before state 6.

No writer above value 4 appears in the recovered GUARD gameplay graph.

A raw USER.SAV could of course contain an arbitrary byte, but that is save/debug compatibility rather than a normal producer.

## Strategy 0 — DefaultMovement

Planner `3:76FC` uses the player's relative cell direction and the stored perception/proximity flags to select signed movement components in `{-8,0,+8}`.

Timer selection:

- neither close nor visible -> `0x18`;
- visible -> `RNG % 8 + 8`;
- close-proximity -> `8`;
- difficulty 2 halves the visible timer;
- difficulty 0 doubles it.

The planner then writes state 6 and updates direction/animation/movement.

This is the ordinary player-biased movement planner used by most guards.

## Strategy 1 — WoundedDoorSeek

This strategy has a special planner only while strength is below `0x7F`.

`3:1394` scans the active **22-byte DoorRuntime controller array**, computes tile-distance to each door anchor, requires the candidate to pass the LOS/path helper, and returns the closest valid controller.

The planner then points the guard toward that door anchor with movement components `-8/0/+8`, sets timer `0x10`, and enters state 6.

If strength is not below `0x7F`, strategy 1 falls through to the generic strategy-0 planner.

The associated special collision route can enter state `0x11`, the already-recovered dynamic-door maneuver; when that state finishes it clears strategy to 0 and returns to state 7.

Thus the code-level semantic is **wounded door-seeking / flee-to-door**.

The initializer selects strategy 1 from wall class `0x43`. The supplied map inventory reports zero used cells for that class, so this strategy appears implemented but dormant in the supplied retail maps unless reached via save/debug/other data.

## Strategy 2 — RouteMarkerMovement

The initializer selects strategy 2 on wall class:

- `0x42` RETREAT;
- `0x46` ACTIONSPOT.

Its planner uses a fixed random movement interval `RNG % 8 + 8` and enters state 6.

The directional movement helper distinguishes it from all other strategies:

- ordinary movement scale = 8 world units;
- strategy 2 scale = **16 world units**;
- state-6 animation uses the alternate class sequence bank at `row+0x04+2*facing` rather than the normal `row+0x24+2*facing`.

Moving state 8 also consumes TURN/RETREAT markers through `3:7920`, changing facing or ending/reversing a route.

The safest name is therefore **route-marker movement**. This covers RETREAT pathing and ACTIONSPOT-driven special placements without inventing a narrower original symbol.

## Strategy 3 — GargoyleOneShot

Only retail classes `0x12/0x13` initialize this strategy.

When state 7 acquires the player it does not enter state 2 directly. It enters state `0x13` through `3:7A06`:

```text
timer = RNG % 0x50 + 8      // 8..87
state = 0x13
moveX/moveY = direction table
```

State `0x13`:

- decrements its timer every update;
- at new timer value 8 finds wall class 7 and activates its ONE_SHOT frame;
- for new values 7..0 attempts movement;
- blocked movement still consumes timer;
- on the following entry with timer 0 clears strategy to 0 and enters state 2.

This is the disappearing-gargoyle / ONE_SHOT emergence movement path.

## Strategy 4 — Cannon

Object class `0x19` initializes:

```text
strategy = 4
state = 0x0E
```

The Cannon-specific state cycle is `0x0E <-> 0x0F <-> 0x10`, controlled by global cannon-enable flag `51A5`.

The ordinary non-lethal hit receiver suppresses the normal hit-state transition when strategy == 4. The class-specific player->guard damage producer already yields zero for class `0x19`, matching the retail Cannon's effective invulnerability.

This is a class-specific stationary/turret strategy rather than a generic movement planner.

## Functional closure of states 0x02..0x08

### State 0x02 — AlertSequence

Direct effects:

1. call class-dependent sound selector `B862`;
2. load sequence token from class row `+0x34`;
3. schedule wrapper state 0 with next state 3.

This is the alert/activation sequence that begins the ordinary active cycle.

### State 0x03 — AttackOpportunityCheck

Calls `7594`, the perception/proximity decision helper.

- false -> state 5, no attack wind-up;
- true -> sequence token `row+0x36`, wrapper state 0, next state 4.

This is the attack-opportunity / pre-attack decision.

### State 0x04 — AttackExecution

Re-checks `7594`.

When true:

- calls class-dependent attack SFX selector `B5E4`;
- calls `8C0A`, the guard->player damage path.

Unless that attack changed the game into player-death state 2, it then schedules `row+0x38` through wrapper state 0 with next state 5.

This is a confirmed attack-execution state.

### State 0x05 — MovementReplan

Calls the strategy planner `76FC`, which enters state 6 (except strategy-3 acquisition is routed separately from state 7).

### State 0x06 — TimedMovement

Each update:

- refresh directional animation;
- execute movement through `71DC`;
- decrement timer;
- when timer reaches zero -> state 3.

Thus the normal cycle is:

```text
3 check -> 4 attack -> 5 replan -> 6 move -> 3 check
```

with state 2 as the activation/alert entry.

### State 0x07 — StationaryAcquire

- refresh directional sequence;
- Omnificent can return before acquisition;
- otherwise run LOS helper `7494`;
- no LOS -> remain state 7;
- LOS + strategy 3 -> state 0x13;
- LOS + other strategy -> state 2.

This is the stationary/passive acquisition state.

### State 0x08 — MovingAcquire

- process TURN/RETREAT marker rule through `7920`;
- execute movement;
- refresh directional sequence;
- only when saved/next state == 2 does it perform acquisition;
- Omnificent suppresses that acquisition;
- successful LOS -> state 2.

This is the moving/patrol acquisition state.

## Perception helper boundary

The attack checks in states 3/4 use `7594`, not merely raw LOS.

`7594`:

- stores raw visibility result in `GUARD+0x17`;
- computes a square close-proximity flag from player/guard world deltas (< 65 units on both axes) into `GUARD+0x18`;
- selects the decision source using `GUARD+0x16`.

The exact original human-readable name of each `+0x16` mode is still separate work, but the inputs and consumers are statically mapped.

State 7/8 acquisition instead uses raw `7494` LOS directly.

## Coverage

| Subarea | 2026-09-29 status |
|---|---:|
| strategy numeric set / normal writers | **100% Win16 1.10** |
| strategy 0–4 primary control flow | **100% Win16 1.10** |
| states 0x02–0x08 control flow | **100% Win16 1.10 static control flow** |
| states 0x02–0x08 semantic behavior | **98–99%** |
| exact IMG/SEQDEF/SND presentation for every class/state | lower; tracked separately |
| complete DOS dispatcher/strategy parity | not included in this 100% claim |

The residual 1–2% semantic gap is presentation/author-intent naming, not uncertainty about the executable transitions described above.
