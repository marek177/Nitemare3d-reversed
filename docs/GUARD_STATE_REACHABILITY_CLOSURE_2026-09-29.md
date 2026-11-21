# GUARD state producer/reachability closure — Win16 1.10 — 2026-09-29

## Result

The numeric GUARD state space `0x00..0x15` is now closed at the **producer / reachability** level for Win16 1.10.

- total numeric states accepted by the dispatcher: **22**
- states with a recovered retail producer: **20**
- terminal states with no dispatcher body: **2** (`0x0A`, `0x0B`)
- retained handlers with no recovered normal retail producer: **2** (`0x0C`, `0x0D`)

This is **100% state-ID/reachability coverage**, not 100% semantic AI reconstruction. Several reachable states still need more precise gameplay-facing names, exact animation/SFX binding or attack timing.

## Complete producer graph

| State | Reachability | Recovered producer / entry |
|---:|---|---|
| `00` | normal | common sequence wrapper; also class `0x21` initialization |
| `01` | conditional | accepted-fire wake cache: eligible strategy-0 guards in state 7/8 get timer `RNG%8`, state 1 |
| `02` | normal | state 1 timeout; state 7/8 successful acquisition; state 13 completion; several special returns |
| `03` | normal | state 2 schedules class sequence through the common state setter as `state=0,next=3`; state 6 also returns directly to 3 |
| `04` | normal | state 3 successful perception schedules `state=0,next=4` |
| `05` | normal | state 4 post-attack sequence schedules `state=0,next=5`; state 3 perception failure also enters 5 |
| `06` | normal | movement planner; E1M9 Radio/Dancers restore path also writes 6 |
| `07` | normal | default GUARD initialization; state 11 completion returns to 7 |
| `08` | normal | moving-spawn initialization when movement deltas are nonzero; Dracula `0x11 -> 0x14` phase transform writes 8 |
| `09` | conditional | lethal-damage chain uses it as death/special finalization next state |
| `0A` | terminal | ordinary death finalizer writes decimal 10 / `0x0A`; dispatcher intentionally has no local case |
| `0B` | terminal | guard that causes lethal player contact is written to `0x0B`; dispatcher intentionally has no local case |
| `0C` | dormant | retained shared handler and USE text, but no recovered normal retail writer |
| `0D` | dormant | retained shared handler, but no recovered normal retail writer |
| `0E` | class-specific | class `0x19` Cannon initialization |
| `0F` | class-specific | Cannon state `0E` enters when cannon-enable flag is active; state `10` returns here |
| `10` | class-specific | Cannon state `0F` timeout/selector branch enters the attack cycle |
| `11` | conditional | strategy-1 guard encountering a usable dynamic door; door maneuver helper writes `0x11` |
| `12` | conditional | lethal damage when associated OBJECT `+0x1A > 0`; waits/animates, then restores next state `09` |
| `13` | conditional | strategy-3 branch from state 7; timer `RNG%0x50 + 8` |
| `14` | scripted | E1M9 Radio/Dancers script writes `0x14` with timer `0x70`; restore path returns those actors to 6 |
| `15` | conditional | ordinary non-lethal pain/reaction for states not handled by the special recovery branches |

## Death-path packing detail

The common state/sequence setter writes:

```text
GUARD+00 = packed sequence token
OBJECT+03 = low byte(sequence token)
GUARD+06 = high byte(sequence token) - 1
GUARD+0C = nextState
GUARD+0B = currentState
```

The lethal-damage raw call pushes one of two packed dwords for the final two byte parameters:

```text
0x00090000 -> currentState 0x00, nextState 0x09
0x00090012 -> currentState 0x12, nextState 0x09
```

The second form is selected when `OBJECT+0x1A > 0`. State `0x12` waits until both its timer and the OBJECT vertical/animation field drain to zero, then restores `nextState=0x09`. State `0x09` runs the class-specific death/special finalizer. Normal finalization writes state `0x0A`; Dracula class `0x11` instead transforms in place to class `0x14`, restores strength 255, and enters state `0x08`.

This closes the previously ambiguous relationship among states 0, 9, 0x0A and 0x12.

## Door-maneuver state 0x11

The movement/collision helper enters state `0x11` only on the strategy-1 dynamic-door branch. It also:

- sets a 0x20 countdown;
- clears/recomputes movement components to approach the door;
- updates the directional sequence;
- activates the linked door helper.

State `0x11` performs movement/sequence updates while counting down, then clears strategy/movement and returns to state `0x07`.

## Radio/Dancers state 0x14

The E1M9 Radio script iterates eligible actors, writes state `0x14`, timer `0x70`, and swaps their presentation/resource state for the dance sequence. The matching restore path identifies state-`0x14` actors and returns them to state `0x06`.

Thus state `0x14` is not a generic AI mode; it is a confirmed scripted Episode-1 Radio/Dancers state.

## Dormant 0x0C / 0x0D

Both values remain valid dispatcher inputs and share the normal directional/sequence-refresh handler. State `0x0C` additionally retains the USE message `"I've nothing left!"`.

However, writer audits over the audited Win16 builds do not recover a normal producer for either value. DOS 1.0/1.7/1.8(=supplied 1.9)/2.0 retain the analogous `state==0x0C` interaction fossil without a recovered normal writer as documented separately.

They remain implemented for save/debug compatibility but are not inserted into the clean-room normal transition graph.

## Coverage boundary

### Closed at 100%

- numeric state range `0x00..0x15`;
- handler/no-handler identity;
- recovered producer existence for every state;
- normal vs conditional vs class-specific vs scripted vs terminal vs dormant reachability category;
- death transition relationship `00/12 -> 09 -> 0A`;
- lethal-player-contact terminal state `0x0B`;
- dormant classification of `0x0C/0x0D`.

### Still separate from this 100% claim

- final semantic names for all normal states 02..08;
- exact sequence/IMG/SND binding for every state/class;
- all attack cadence/projectile decisions;
- complete DOS dispatcher parity at the same confidence;
- runtime frame-perfect parity.

Therefore **GUARD state-ID/reachability = 100% Win16 1.10**, while overall GUARD AI remains below 100%.
