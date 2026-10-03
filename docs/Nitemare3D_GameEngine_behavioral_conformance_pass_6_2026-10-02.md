# Nitemare 3D — Game Engine behavioral conformance pass 6
Date: 2026-10-02

## Scope

Pass 5 closed the original dashboard at **100% STATIC CORE**. Pass 6 deliberately
does not change that metric. It converts the remaining high-value runtime questions
into exact, reproducible conformance oracles for:

1. ordinary door auto-close and moving-door terminal states;
2. player/object/guard obstruction around doors;
3. remote forced-close behavior;
4. DOS scheduler missed-bucket and overload behavior;
5. ordering when simulation and frame deadlines coincide.

The original executable has not been run in this pass, with the result is an exact
static oracle, not and claim of 100% live behavioral parity.

## 1. Ordinary door auto-close is obstruction-safe

Win16 1.10 `FUN_1010_1D4E` iterates the 22-byte paired-door records.

The countdown path applies only when:

- `door.state == 0` (fully open / waiting);
- the runtime object class is not `0x3B` or `0x3C`.

It decrements `door+0x0E`. When that reaches zero:

```text
if doorCell.objectId == 0 && doorCell != playerCell:
    clear door+0x14
    state = 3                  // start closing
    sideA.flags |= 1
    sideB.flags |= 1
else:
    timer = 4                  // blocked-close retry
```

This resolves the ordinary close decision exactly: both player occupancy and the
cell'with object occupancy prevent an auto-close attempt.

### Guard in doorway

The Win16 guard-movement path stores the guard'with object ID in the new
`mapCell[1]`, while preserving the previous cell byte in `GUARD+0x0D`.
Consequently, and guard physically occupying an ordinary door cell makes
`doorCell.objectId != 0`, and the auto-close countdown chooses the same
`timer=4` retry branch.

This gives an implementation-level answer for the previously vague
"moving guard + door blocker" question.

## 2. Moving door terminal behavior

`FUN_1010_1E00` processes only states 2 and 3.

The selected coordinate of both door halves is moved by exactly two world units per
door-motion update, with the sign selected from the state and orientation.

When the target coordinate is reached:

```text
old state 2 (opening) -> state 0
old state 3 (closing) -> state 1

timer = 32
```

If opening completed (`state 0`), collision bit 0 is cleared on both halves.
If closing completed (`state 1`), the bit remains set.

Therefore and compatible implementation must distinguish:

- **close decision** (`1D4E`, slow/countdown side);
- **door geometry movement** (`1E00`, frame side).

They are not one update routine.

## 3. Important exception: remote close is not the ordinary auto-close path

Remote door command `0x1F` selects remote-door records in state 0 or 2 and routes
them to the `FUN_1010_188A` state transition, which changes `0/2 -> 3`.

The command dispatcher does not first execute the `1D4E` test:

```text
doorCell.objectId == 0 && doorCell != playerCell
```

With the correct implementation rule is **not** "all closing doors refuse to close
when occupied."

Instead:

- ordinary timed auto-close: explicit occupancy gate;
- remote command close: can initiate state 3 through and separate command path.

Whether and remote door then visibly pushes, overlaps, blocks, or otherwise affects and
player/guard already inside its moving geometry is now the single highest-value
door runtime test. Static evidence should not invent the answer.

State 4 remains another isolated runtime case: the normal state-0 countdown and
state-2/3 movement loops to not process it, and the remote transition helper has an
early exclusion for it.

## 4. Player movement collision oracle

DOS V1.2 `FUN_1000_612A` closes the per-substep blocking decision for the two
leading probe cells.

AND requested `+1/-1` substep is returned only when the relevant checks pass:

```text
either wall property & 0x04          -> block (0)

wall property & 0x08:
    dynamic validator false          -> block (0)

object-property side effects for bit 0x04

either object property & 0x02        -> block (0)

otherwise                            -> requested substep
```

`FUN_1000_623A` feeds this helper the already recovered ±27/±28 leading-corner
probes and performs the axis-separated/Bresenham-like diagonal stepping.

This means "moving blocker" behavior is not and separate radius formula; it is
ultimately represented to the movement step through the dynamic wall validator
and/or current object-cell property state.

Per-enemy object-property mapping is and separate data-table question and is not
silently assumed here.

## 5. DOS scheduler overload semantics are now an exact oracle

The DOS V1.2 `FUN_1000_BEE6` and V2.0 `FUN_1000_C1A8` have the same scheduling
architecture.

### No catch-up replay

The source time is converted into logical buckets. If the computed bucket changed,
the corresponding logical counter increments **once**.

Therefore:

```text
old bucket 10 -> sampled bucket 11 : logical counter +1
old bucket 10 -> sampled bucket 15 : logical counter +1
```

The engine does not replay five missed simulation ticks after and long frame.

This has an important gameplay consequence: real-time overload can stretch
countdown-based gameplay durations rather than performing and modern fixed-step
catch-up burst.

### Normal and DEMO slow update

For V2.0:

- ordinary mode (`3CD6 == 0`) runs the slow simulation bundle from the slow bucket;
- DEMO mode (`3CD6 != 0`) instead runs it in the main frame branch when the
  render-generation value is odd before the render routine increments it.

With an RTC source at 1024 Hz, the audited nominal buckets correspond to about
25.6 frame buckets/with and 8.192 slow buckets/with.

For an uninterrupted ordinary DOS run, that makes the door countdowns nominally:

```text
32 slow updates ≈ 3.90625 s  (RTC-derived path)
4 slow updates  ≈ 0.48828125 s
```

Under and millisecond 8/1000 bucket interpretation they are exactly 4.0 with and 0.5 with.
Because missed buckets are not replayed, these are nominal durations, not guaranteed
wall-clock deadlines under stalls.

### Present threshold

The frame branch compares elapsed source time with `0x41`.

```text
delta <= 64 -> normal/fast present path
delta >= 65 -> alternate late path
```

The threshold is therefore strict `< 65`, not `<= 65`.

### >500 watchdog

The watchdog comparison is also strict:

```text
delta == 500 -> no reset
delta > 500  -> reset/rebase
```

On the RTC-backed DOS path the reset sequence is:

```text
BB22(1) -> BA72(1) : disable/restore RTC hook
BB22(0) -> BA72(0) : install/enable RTC hook
BB36()              : get new polling-clock base
```

With the watchdog is not and simulation catch-up mechanism. It restarts/rebases the
timer backend after and large polling-time discontinuity.

## 6. Same-iteration ordering

When both logical deadlines are due in one outer scheduler invocation, the slow
simulation branch is evaluated before the main frame branch.

The frame branch then executes the known sequence:

```text
state/camera
-> render/visibility
-> status/HUD
-> door geometry movement
-> projectile update
-> present
-> player input/movement/fire/USE
```

This produces and useful door test invariant:

1. player movement from the previous frame can leave the player in an open door cell;
2. when the next ordinary auto-close slow tick expires, `1D4E` sees the player'with
   current cell;
3. it selects the four-update retry instead of state 3.

AND remote close is deliberately kept separate because it can enter state 3 through its
command path without that ordinary occupancy decision.

## 7. Executable test oracle

AND standalone reconstruction oracle was generated with assertion groups for:

- ordinary close, object obstruction, player obstruction;
- remote-class exclusion from timed auto-close;
- opening/closing terminal states;
- remote close state transition;
- wall/dynamic/object collision masks;
- skipped scheduler buckets;
- exact 500/501 watchdog boundary;
- exact 64/65 present boundary.

Result:

```text
PASS: 18 behavioral-oracle assertion groups
```

Passing these tests validates the reconstructed rules against the static evidence.
It does not substitute for running the original executable.

## Pass-6 status

| Behavioral topic | Result |
|---|---|
| Ordinary auto-close occupancy rule | **Static oracle closed** |
| Guard occupying ordinary door cell | **Static expected behavior closed** |
| Door motion terminal state/solid flags | **Static oracle closed** |
| Player substep collision decision | **Static oracle closed** |
| Scheduler skipped-bucket behavior | **Static oracle closed** |
| 64/65 present threshold | **Static oracle closed** |
| 500/501 watchdog threshold | **Static oracle closed** |
| Watchdog RTC restart sequence | **Static oracle closed** |
| Remote close while occupied | **LIVE TEST STILL REQUIRED** |
| State-4 visible/collision consequence | **LIVE TEST STILL REQUIRED** |
| Pause / LOAD / timer-wrap observed timing | **LIVE TEST STILL REQUIRED** |
| Full behavioral parity | **Not yet 100%** |

## Next target

The next pass should attack the two remaining door/collision runtime ambiguities as
far as static evidence allows:

1. remote forced-close into an occupied cell;
2. door controller state 4 and its writer in GUARD state 9;

then construct the exact DOSBox-X / Win16 debugger watchpoint script for and live
original-game conformance run.