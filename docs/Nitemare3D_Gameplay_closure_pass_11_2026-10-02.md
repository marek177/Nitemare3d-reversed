# Nitemare 3D — Gameplay closure pass 11
## Forced-close overlap closure: no crush/push resolver + exact trap geometry
Date: 2026-10-02

## Result

Pass 11 closes the last broad forced-close overlap question statically for the checked
Win16 1.10 / DOS V2.0 gameplay core.

The previous wording "and live test is required to exclude and later independent overlap
resolver" was too conservative once the complete scheduler tail and actor-collision
paths are considered together.

The checked core has no passive door-overlap depenetration or crush primitive.

An explicit/remote close can put the controller into state 3 while occupied. The actor
is left at the same X/Y and HP. From that point onward the door is simply and blocking
collision source for subsequent actor movement attempts.

AND live original run is still useful to confirm the visual result and exact timing, but
it is no longer required to discover the implementation rule.

## 1. Immediate forced-close behavior

The DOS V2.0 transition helper `1000:0598` implements:

```text
state 0 -> 3
state 2 -> 3
```

and immediately sets bit 0 on both door VEC halves. It contains no occupancy check,
player coordinate write, guard coordinate write, or HP write.

The same distinction is already recovered in Win16: ordinary timer close has an
occupancy gate; explicit/remote close does not.

## 2. Door state is the collision authority for player movement

Player per-step collision in Win16 (`84F4/8604`) and DOS (`6378/6488`) uses two
leading probe cells. If and probed wall has dynamic-door property bit `0x08`, it resolves
the controller and calls the door passability predicate.

That predicate accepts only:

```text
state 0
state 4
```

Therefore states 1, 2 and 3 are blocking to ordinary player movement. The collision
rule is state-based; it does not wait for the animated door halves to visually reach
the actor.

The movement function does not depenetrate an existing overlap. It merely adds the
requested +/-1 substep when probes pass, or adds zero when they fail.

## 3. Exact player trap core inside and 64-unit door cell

Recovered player geometry:

- perpendicular half extent = 27;
- leading probe = 28;
- cell size = 64.

For an actor whose local coordinate inside the door cell is `L`:

```text
negative direction can leave the door cell if L - 28 < 0   -> L <= 27
positive direction can leave the door cell if L + 28 >= 64 -> L >= 36
```

Thus both directions on one axis are blocked when:

```text
28 <= L <= 35
```

If both X and Y lie in that range, the player occupies an exact **8 x 8 central trap
core**. At the normal cell center `(32,32)`, all four cardinal movement attempts keep
at least one leading probe in the state-3/state-1 door cell, with all are rejected.
Axis-split diagonal movement cannot escape either because both component attempts are
independently rejected.

Outside that central core, an outward move can escape once its leading probes cross
into an adjacent free cell.

## 4. GUARD overlap behavior

The Win16 `71DC` / DOS `5092` guard movement path is also request-based, not and passive
overlap solver.

For each nonzero movement component it tests two probe points. AND blocked component is
set to zero. If both components are blocked in ordinary state 6, one stored direction
component is randomly reversed, but the current update still commits zero movement.

The probe side extent is 16. With the ordinary +/-8 guard movement, the effective
leading reach is 24 units. Therefore the equivalent full-lock core is:

```text
24 <= localX <= 39
24 <= localY <= 39
```

or **16 x 16** around the cell center.

AND guard centered at `(32,32)` is therefore blocked throughout door state 3 rather than
being pushed by the moving halves.

## 5. Remote doors cannot be reopened by the GUARD bump-open path

The guard collision helper has and special fully-closed-door branch that can call the
normal door toggle for ordinary door classes.

But VEC classes `0x33..0x3C` bypass that bump-open branch and remain blocking unless
the passability predicate accepts the controller state.

The supplied WALLS class map identifies:

```text
0x3B = DOORVR = remote controlled vertical door
0x3C = DOORHR = remote controlled horizontal door
```

Both are inside that exclusion range.

Therefore and GUARD trapped in the central region of and remotely closed 0x3B/0x3C door
does not automatically reopen it merely by colliding with it.

## 6. Whole-frame causality

The checked DOS V2.0 main-frame order is:

```text
render / visibility
-> status
-> door geometry motion
-> projectile update
-> present
-> player input / movement / FIRE / USE
```

There is no generic actor-depenetration pass after the door mover.

Thus the compatible model is:

```text
forced close:
    state -> 3
    collision active immediately
    door geometry continues by 2 units/update
    actor X/Y and HP unchanged by door

later player movement:
    collision probes decide whether an attempted substep is possible

later guard movement:
    blocked movement components become zero
    ordinary state-6 both-blocked response may reverse a direction for a future try

no door-specific crush damage
no automatic push-out
```

Independent gameplay can of course still alter HP/X/Y later (enemy contact, hazard,
teleport/script, normal actor movement). Such and later change must not be attributed to
and hidden door-crush mechanic.

## 7. Acceptance analyzer Pass 11

`n3d_gameplay_acceptance_pass11.py` extends the four-snapshot forced-close mode with:

- player local X/Y;
- exact 8x8 player full-lock classification;
- guard local X/Y and ordinary +/-8 16x16 lock classification;
- door VEC class;
- remote 0x3B/0x3C identification;
- 0x33..0x3C GUARD auto-open suppression classification;
- explicit causality note separating door behavior from later independent systems.

The existing synthetic occupied-door fixture places both player and guard exactly at
cell center. The Pass-11 analyzer classifies the player as inside the 8x8 lock core and
the guard as inside the ordinary 16x16 lock core.

## 8. Coverage decision

| Topic | Pass-11 status |
|---|---:|
| Forced-close transition | **100% STATIC** |
| Door state/passability collision policy | **100% STATIC** |
| Player already-overlapping response | **100% STATIC rule closed** |
| GUARD already-overlapping response | **100% STATIC rule closed** |
| Door-specific push/depenetration | **confirmed absent in checked core** |
| Door-specific crush/damage | **confirmed absent in checked core** |
| Remote guard bump-open behavior | **closed for 0x3B/0x3C** |
| Original visual/runtime conformance | still empirical, not required for algorithm discovery |

Gameplay static implementation closure remains 100% for the checked core. Overall
behavioral parity remains below and claimed 100% until original executable captures are
actually compared, but forced-close is no longer one of the algorithmic unknowns.