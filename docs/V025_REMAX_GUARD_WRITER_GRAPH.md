# v0.25 RE MAX — GUARD state/nextstate writer graph

v0.25 records the currently proven GUARD state-transition writes as a separate evidence graph.

## Why this is separate from the state table

A state handler table answers: "what code executes for state X?"

A writer graph answers: "what code or external event changes GUARD state/nextstate/strategy/timer?"

These are not the same thing, and mixing them hides important transition sources.

## Handler-level writers with known Win16 v1.10 addresses

The registry includes:

- `3:7BA2`: state 00 -> state=nextstate
- `3:7BE0`: state 01 -> state 02
- `3:7CEC`: state 06 -> state 03
- `3:7E6C`: state 0E conditionally -> 0F
- `3:7E9E`: state 0F -> 10 or 0E
- `3:7F26`: state 10 -> 0F
- `3:7F8E`: state 11 writes strategy=0 and state=07
- `3:7FEE`: state 12 -> state=nextstate
- `3:807E`: state 15 -> state=nextstate

## Confirmed external transitions with writer address still unresolved

The registry deliberately supports `addressKnown=false`.

### Normal non-lethal hit

Confirmed invariant:

1. preserve old state into `nextstate`;
2. write `resoct=8`;
3. write `state=0x15`;
4. state 15 later returns through `nextstate`.

The exact writer instruction address is not fabricated in v0.25.

### Dracula phase transition

Confirmed writes:

- `OBJECT+06 = 0x14`
- `GUARD+0B state = 0x08`
- `GUARD+0C nextstate = 0x02`
- `GUARD+06 timer = 1`

Again, exact writer instruction addresses are left unresolved until the direct XREF/callsite is pinned.

## What remains open

This is not yet the complete GUARD+0B/+0C write-XREF census.

Still needed:

- all initialization writers;
- all class/strategy-specific state writes;
- death-state writers;
- boss-specific writers beyond the confirmed Dracula reset;
- map/script writers;
- DOS v2.0 per-state/write-site pairing;
- RNG call association for every conditional transition.

The next closure pass should target the direct write-XREF export for GUARD+0B and GUARD+0C.
