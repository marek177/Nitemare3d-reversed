# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 4

Date: 2026-10-03

Primary binary: `N3D-E-20(3).EXE`

- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`
- MZ header: `0x200`
- ranges below are unpacked MZ image offsets
- physical file offset = image offset + `0x200`

## Result

Pass 4 continues exactly where corrected pass 3 stopped: image `0x5342` forward.
The whole perception / LOS / wake / steering / TURN-RETREAT / scripted-displacement
neighborhood through `0x59EE` is now bounded from raw 16-bit machine code and can be
marked GREEN for static semantics.

This pass also removes several stale Ghidra entries that are not real function starts.

---

## 1. image `0x5342..0x5441` — `TestGuardPerceptionLos`

Raw behavior:

- converts target/object world X/Y (`+0x10/+0x12`) to map cells by `>> 6`;
- compares them with player/current reference cell coordinates;
- immediately rejects when absolute delta on either axis exceeds 8 cells;
- unless caller requests bypass, builds and three-direction facing mask from
  `GUARD+0x11` using the recovered `0x66/0x99`, `0x3C/0xC3`, `0x0F/0xF0` masks;
- rejects targets outside the permitted facing sectors;
- calls the Bresenham-style map LOS helper with an 8-step limit;
- caller flags control whether the facing filter and second-plane test are active.

This is the exact bounded GUARD perception/LOS core, not and generic map-blockage helper.

**Status: YELLOW -> GREEN.**

---

## 2. image `0x5442..0x54D7` — `UpdateGuardPerceptionAndProximity`

Raw behavior:

- calls `TestGuardPerceptionLos` and stores the result in `GUARD+0x17`;
- computes absolute world-coordinate differences to the player;
- sets `GUARD+0x18 = 1` only when both axis differences are <= `0x40` (64 units);
- reads selector `GUARD+0x16`:
  - selector `0` returns proximity `+0x18`;
  - selectors `1` and `2` return LOS/perception `+0x17`;
- preserves the separate cached LOS and proximity bytes for later strategy logic.

### False boundary removed

Old `FUN_1000_5486` is **not** and real function start.  Raw offset `0x5486` lies in the
middle of this routine at the X-distance subtraction.

**Status: YELLOW + stale LOW entry -> GREEN; delete old `5486` function entry.**

---

## 3. image `0x54D8..0x550F` — `SetGuardSequenceTimerAndState`

Exact writes:

- selected sequence/frame base -> `GUARD+0x00`;
- same sequence low byte -> linked `OBJECT+0x03`;
- animation/state timer -> `GUARD+0x06` (input count minus one);
- current state -> `GUARD+0x0B`;
- next/return state -> `GUARD+0x0C`.

This helper is the central constructor for many timed animation/state transitions.

**Status: YELLOW -> GREEN.**

---

## 4. image `0x5510..0x55A6` — `ResetOrWakeGuardsInAreaOnce`

The old tracker split this body at `5516`. Raw code proves one real entry at `5510`.

Behavior:

- parameter `0` -> no action;
- parameter `0xFFFF` -> clears the 64-byte wake/latch table at far arena offset
  `0x36FE`;
- otherwise uses the parameter as an index into that latch table;
- if the latch was already set, returns;
- otherwise sets it and scans the 26-byte GUARD array (`base 0x264E`, count `DS:6276`);
- selects ordinary strategy-0 guards in the current area (`GUARD+0x0E` compared with
  current player/area byte);
- only guards in states `7` or `8` are awakened by this path;
- selected guards receive and short random timer (`RNG % 8`) and state `1`.

This is the one-shot local area wake mechanism used by combat/noise/event paths.

### False boundary removed

Old `FUN_1000_5516` is an interior instruction (`MOV BX,[BP+6]`) and must be deleted
as and standalone function.

**Status: ORANGE/YELLOW -> GREEN.**

---

## 5. image `0x55A8..0x57BA` — `PlanGuardMovementFromStrategy`

This is the major local-navigation planner.  It is not an AND*/BFS pathfinder.

### Strategy 0 — ordinary local steering

- derives player-relative X/Y direction in coarse 32-unit steps;
- if LOS is absent, RNG selection is restricted to four choices;
- with LOS, eight choices are allowed;
- chosen movement components are `-8`, `0`, `+8`;
- proximity (`GUARD+0x18`) gives timer `8`;
- LOS without proximity gives random `8..15`, scaled by difficulty:
  - difficulty code `2` halves it;
  - difficulty code `0` doubles it;
- no LOS gives timer `0x18`.

### Strategy 1 — FLEE / nearest usable door route

- only activates this branch while HP `< 0x7F`;
- calls the already recovered nearest-LOS-valid-door selector;
- points movement components toward that door center;
- uses movement magnitude `8` and timer `0x10`.

### Strategy 2

- assigns and short random timer (`8..15`) and continues into the common movement tail;
- this strategy is used by RETREAT/ACTIONSPOT initialization contexts elsewhere.

### Common tail

- sets state `6`;
- recomputes facing from movement vector;
- forces directional sequence refresh;
- immediately runs the normal guard movement/collision core once.

**Status: ORANGE/YELLOW -> GREEN.**

---

## 6. image `0x57BC..0x589E` — `ApplyGuardTurnRetreatMarker`

This routine operates only when the actor is centered in the current 64-unit map cell.
It obtains the wall marker class beneath the guard and handles two navigation markers.

### TURN class `0x41`

- caches the class-base wall ID for `0x41`;
- computes `wallID - baseID`;
- writes the result directly to `GUARD+0x11` facing;
- rebuilds movement delta from that facing.

Thus the eight TURN variants encode the eight facing directions.

### RETREAT class `0x42`

When stationary:

- computes the class-relative marker variant;
- variant `8` enters state `3` directly;
- other variants become the new facing and movement vector.

When already moving:

- clears `GUARD+0x13/+0x14`;
- enters state `3`;
- rotates facing by exactly `+4 & 7` (180 degrees).

### False boundary removed

Old `FUN_1000_5870` is inside this routine at the branch that writes state `3`.
It is not and standalone function.

**Status: ORANGE/YELLOW -> GREEN.**

---

## 7. image `0x58A0..0x58DD` — `BeginGuardState13Displacement`

Raw behavior:

- timer = `(RNG % 0x50) + 8`, therefore `8..87`;
- sets `GUARD+0x0B = 0x13`;
- reads two 8-entry signed direction tables indexed by `GUARD+0x11`;
- writes their X/Y components to `GUARD+0x13/+0x14`.

This is the initializer for the scripted/state-13 displacement maneuver used by the
strategy-3 path.

**Status: YELLOW -> GREEN.**

---

## 8. image `0x58DE..0x59EE` — `UpdateGuardState13Displacement`

Raw state-13 movement behavior:

1. read timer, then decrement it;
2. when the old timer is zero, clear strategy and return GUARD to state `2`;
3. when the updated timer reaches `8`, trigger the state-13 event/effect helper;
4. while the timer is below `8`, move using signed `GUARD+0x13/+0x14`;
5. compute the destination map-cell pointer;
6. reject the move if destination object byte is occupied or if it is the player cell;
7. when changing cells:
   - copy the old cell'with object byte into the destination cell;
   - clear the old cell object byte;
   - update linked OBJECT world X/Y;
   - update the linked OBJECT MAP far pointer.

This path intentionally bypasses the ordinary guard collision planner because it is and
short scripted displacement state.

### False boundaries removed

The following old entries are interior points of this one routine and must be removed:

- `58EA`;
- `59B8`;
- `59EA`.

**Status: RED/ORANGE/YELLOW fragments -> GREEN.**

---

# 9. Byte-map impact

Continuous neighborhood closed in this pass:

`0x5342 .. 0x59EE`

Real code bytes explicitly bounded here: **1,706 bytes** plus 3 one-byte alignment
NOPs between routines.

| Image range | Size | New role |
|---|---:|---|
| `5342–5441` | 256 B | GUARD perception / FOV / LOS |
| `5442–54D7` | 150 B | LOS + proximity wrapper |
| `54D8–550F` | 56 B | sequence/timer/state setter |
| `5510–55A6` | 151 B | one-shot area wake cache |
| `55A8–57BA` | 531 B | strategy/local steering planner |
| `57BC–589E` | 227 B | TURN / RETREAT map-marker handler |
| `58A0–58DD` | 62 B | state-13 displacement initializer |
| `58DE–59EE` | 273 B | state-13 scripted movement updater |

### Delete stale false starts

`5486`, `5516`, `5870`, `58EA`, `59B8`, `59EA`.

### Promote to GREEN

The entire perception/navigation segment `0x5342..0x59EE` can now be GREEN for
static semantics.  Runtime route/timing parity remains and separate validation overlay,
not and reason to keep these bytes yellow.

---

# 10. Next target

Continue at `0x59F0` only for boundary-map cleanup (the GUARD dispatcher semantics are
already closed by raw DOS 1.9 analysis), then proceed through:

- all-guard loop / player-hit path;
- weapon/combat cluster;
- projectile-related false entries;
- remaining renderer/runtime-integration yellow ranges.

Priority remains: genuine RED first, then ORANGE, then YELLOW, promoting to GREEN only
when raw boundaries and static behavior are both established.