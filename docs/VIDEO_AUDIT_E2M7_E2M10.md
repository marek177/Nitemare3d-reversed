# Nitemare 3D — E2M7–E2M10 video/MAP audit

Source walkthrough MP4s are not distributed. This document records reconstruction-relevant observations and MAP correlations.

## E2M7

- Video confirms a four-floor elevator selector with Floor 1–4 choices and no visible Cancel entry.
- MAP.2 contains exactly four `WARP_E1` endpoints for this level.
- Level also contains colored key locks, both ID cards, Transportation Chamber Door 1, LEVEL_UP, explodable walls and a separate stair warp pair.
- Completion observed: Level 7, 7 enemies remaining, 0 panels not found, 5000 bonus, score 27600.

## E2M8

- Video confirms the three-choice stair selector (`Climb up`, `Climb down`, `Cancel`).
- Video confirms a five-option remote-control menu for opening/closing remote doors and enabling/disabling remote cannons plus Cancel.
- MAP.2 contains CONTROL tiles, remote doors, one cannon, six PUSH objects, five ONE_SHOT walls and fifteen destructible walls/hedges.
- Completion observed: Level 8, 14 enemies remaining, 1 panel not found, score 29400.

## E2M9

- Same remote-control menu confirmed.
- MAP.2 contains an eight-cannon bank, CONTROL tiles, remote doors, multiple warp networks, six pushable boxes, all four colored keys, both ID cards and 59 destructible walls/hedges.
- Completion observed: Level 9, 11 enemies remaining, 2 panels not found, score 30700.

## E2M10

- Remote-control menu appears again.
- Video confirms a scripted Plasma Core destruction objective and success state.
- MAP.2 has a 12-tile generic exploding-wall core cluster and no `LEVEL_UP` cell, supporting a scripted finale path rather than a normal level gateway.
- Completion observed: Level 10, 0 enemies remaining, 0 panels not found, 10000 bonus, score 42200.

## Reconstruction consequences

Implement elevator selectors separately from stair selectors; preserve remote-door and remote-cannon state as distinct systems; route CONTROL tiles through group/ID logic; and implement the Episode 2 finale as a scripted Plasma Core objective rather than a normal LEVEL_UP transition.
