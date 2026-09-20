# NITE3W AI state-machine audit

## Confirmed runtime fields

The shipped guard diagnostic gives these runtime fields:
- +0x06 word timer
- +0x08 word definition index
- +0x0A byte strategy
- +0x0B byte state
- +0x0C byte nextstate
- +0x10 byte strength
- +0x11 byte octant
- +0x12 byte resoct

These names come from the executable's own debug format, not from OpenNitemare3D naming.

## State-machine model supported by the fields

The simultaneous presence of state, nextstate and a word timer strongly supports a timed finite-state machine. The safe reconstruction at this stage is:

runtime guard -> current state + queued/next state + countdown/delay timer + strategy selector + directional octants.

No numeric state ID has yet been assigned a behavioral name such as chase/attack/pain/death without branch-level evidence.

## Definition indirection

runtime +0x08 is multiplied by 0x1C to reach a definition record. The class printed by the debug routine is read from that secondary record. This separates per-instance AI state from per-class definition data.

## Strength

+0x10 is definitely called strength by the original executable. It remains deliberately unrenamed in reconstructed C until writes/decrements and a death transition prove HP semantics.
