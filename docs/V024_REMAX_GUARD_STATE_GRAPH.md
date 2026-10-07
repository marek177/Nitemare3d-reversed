# v0.24 RE MAX — GUARD state transition evidence graph

v0.24 promotes the currently audited Win16 v1.10 GUARD dispatcher into a machine-readable 22-state evidence table.

## Win16 v1.10 dispatcher

Dispatcher:

`3:7B55`

Accepted numeric states:

`0x00..0x15`

All 22 handler offsets from the current executable audit are represented.

## Strong control-flow transitions now encoded

Examples:

- state 00 -> `nextstate`
- state 01 -> 02
- state 06 -> 03
- state 0E conditionally -> 0F
- state 0F -> 10 or 0E
- state 10 -> 0F
- state 11 -> 07 and resets strategy to 0
- state 12 -> `nextstate`
- state 15 -> `nextstate`

State 15 is the only state in this registry currently given CONFIRMED semantic confidence as the normal pain/hit-reaction return state.

## Important semantic boundary

States 02 through 14 are not given invented CHASE/ATTACK/SEARCH labels merely because their control flow is partly known.

The table separately records:

- control-flow confidence;
- semantic confidence;
- transition form.

This allows exact state-machine reconstruction to progress without over-naming partially understood states.

## DOS v2.0

The DOS v2.0 dispatcher at `1000:59F0` is represented at dispatcher level with STRONG confidence and the same observed numeric state range `00..15`.

Per-state DOS handler addresses are deliberately not fabricated in v0.24. They should be added only after direct disassembly pairing or runtime traces close each state.

## Next closure targets

1. pair each DOS handler with its Win16 behavior ID;
2. enumerate every writer of GUARD state and nextstate;
3. bind RNG calls to state transitions;
4. bind movement/LOS/attack/SFX consumers;
5. then promote semantic labels for states 02..14 individually.
