# NITE3W guard reaction and timed-movement audit — 2026-09-23

## Scope and evidence

This pass follows the Win16 1.10 guard-state dispatcher and its damage writer, then checks the same state branches in Win16 1.8. It uses the supplied Ghidra C exports, so function labels are analysis labels rather than original symbols. No live-game trace was performed.

## State 13: strategy-3 timed movement

In Win16 1.10, `FUN_1010_7B56` dispatches guard state `+0x0B`. In state 7 it updates facing, checks the shared perception predicate, and returns if the global guard-processing gate is set or perception fails. If perception succeeds and strategy `+0x0A` is 3, it calls `FUN_1010_7A06`; otherwise it returns the guard to state 2.

`FUN_1010_7A06` writes:

- timer `+0x06 = random() % 0x50 + 8`, so 8–87 simulation updates;
- state `+0x0B = 0x13`;
- movement components `+0x13/+0x14` from two lookup tables indexed by facing `+0x11`.

The tables are recoverable from the supplied 1.10 NE executable (SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`). NE segment 10 begins at file offset `0x2C040`; bytes corresponding to data offsets `0x00E8..0x00F7` are `00 08 08 00 00 F8 F8 00 F8 00 00 08 08 00 00 F8`. The dispatcher reads the first eight as X and the second eight as Y; signed values are:

| Facing index | X step | Y step |
|---:|---:|---:|
| 0 | 0 | -8 |
| 1 | +8 | 0 |
| 2 | +8 | 0 |
| 3 | 0 | +8 |
| 4 | 0 | +8 |
| 5 | -8 | 0 |
| 6 | -8 | 0 |
| 7 | 0 | -8 |

Thus eight facings map to four cardinal movement vectors, with neighboring facing indices sharing a vector. If all seven movement updates succeed, the displacement is 56 internal units, or seven-eighths of a 64-unit map cell. A cell boundary can still be crossed when the guard begins close to that edge.

State 13 calls `FUN_1010_7A44`. That routine decrements the timer. At the point where the remaining timer is 8, it requests a facing-dependent sound through the sound helper. During the following seven updates it computes a candidate position from the current coordinates plus the stored movement components. It checks the candidate map cell and occupancy before updating the object coordinates and the map's occupant bookkeeping. When the timer expires, it clears strategy `+0x0A` and sets state 2.

The code therefore proves a delayed, short cardinal movement sequence tied to strategy 3 and the guard's facing. Each proposed update can be blocked by map-cell occupancy. Calling the behavior a flank, retreat, or named patrol would go beyond the evidence.

## State 15: damage reaction and return state

Win16 1.10 `FUN_1010_80F8` handles a guard hit. If HP is no greater than the computed damage, it takes the lethal branch. A zero damage result returns without reducing HP. For a positive nonlethal result, it subtracts HP and writes 8 to guard byte `+0x12`.

For ordinary current states, the hit path selects a sequence through the guard-class table at offset `+0x3A`, writes that sequence's starting frame to the associated VEC, copies the current state into `+0x0C` (unless the current state is 0), then sets state `0x15`. States 3, 4 and `0x0B` take a special shared path; strategy 4 also returns early. The class-specific reaction selector returned by `FUN_1010_B9B2` is not yet decoded.

State 15 advances the associated VEC frame until it reaches the last frame in the selected sequence, then sets the current state to the saved `+0x0C` value. This makes `+0x0C` a deferred/return state on this path, rather than merely an unused “next state” byte. The separate lethal branch invokes death handling and a class-table sequence; its complete morph/drop/removal chain remains open.

## Cross-version check

Win16 1.8 has the same transitions in `FUN_1010_7AB2`, starts state 13 in `FUN_1010_7962`, and performs its timer/movement work in `FUN_1010_79A0`. The state-13 timer range, sound point, movement window, strategy clear, state-2 return, and state-15 frame/return logic match 1.10. This confirms the behavior is not a 1.10-only change; it does not establish DOS parity.

## Remaining proof

1. Resolve the class-specific damage reaction sequence selector and readers of byte `+0x12`.
2. Trace all writers into states 7, 13 and 15, then classify affected guard/object classes from the map data.
3. Compare the same transitions with DOS v2.0 raw code and a runtime capture, including occupied/blocked candidate cells and the sound event.
