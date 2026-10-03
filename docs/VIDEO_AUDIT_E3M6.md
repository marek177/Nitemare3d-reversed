# Nitemare 3-D — E3M6 video audit

Source: `Nitemare 3D Walkthrough by Hexkwondo! E3 L6.mp4`

## Technical identity
- SHA-256: `fbc572b6a0602e1862d93edf29524a4553c51d5a4ff18c24be0d35eeca7fc26f`
- Duration: 861.135238 s (14:21.135)
- Video: H.264, 1920x912
- Reported frames: 6963

## Confirmed gameplay events

| Time | Event | RE significance |
|---:|---|---|
| ~00:00 | Main menu then E3M6 gameplay begins | Confirms normal level entry path; no special opening story popup seen. |
| ~01:32.9 | `You use the Red key` | Confirms successful red-key door branch. Red key remains represented as inventory state rather than a one-shot scripted item. |
| ~02:33–02:40 | Green key visible in HUD after progression through red-key section | Confirms green-key acquisition in E3M6. Exact pickup frame should be correlated with MAP/object coordinate if needed. |
| ~05:44.3 | Stair selector: `Climb up / Climb down / Cancel` | Confirms the same three-option StairWarpSelector behavior seen in E3M1/E3M10. |
| ~06:08 | Yellow key visible in HUD | Confirms yellow-key acquisition before the later keyed door. |
| ~09:52.5 | `You use the Yellow key` | Confirms successful yellow-key door branch. |
| ~11:12–11:14 | Red chest/trunk in skull-texture area is opened; score increases by 150 | Confirms mutable container/chest state and score reward. Exact contained item is not asserted solely from these frames. |
| ~11:46–11:50 | Combat in skull corridor; player HP visibly changes | Useful for future damage-timing correlation, but this clip alone does not isolate whether the damage source is enemy contact/projectile/fire. |
| ~12:30 onward | Extended skull/fire/hell section with multiple distinct flame visuals | Strong visual evidence for multiple fire/hazard presentations in E3M6; exact per-class damage requires EXE/MAP correlation. |
| ~14:00 | Final chamber/exit sequence | Transition into level completion path. |
| ~14:12–14:13 | Level completion screen | Level 6; Enemies Remaining 18; Panels Not Found 2; Bonus 0; Score 25675. |

## Directly confirmed mechanics
- Colored locked-key door success messaging in Episode 3.
- Persistent key inventory model remains consistent with the E3M7/E3M8 audits.
- Three-option stair selector (`Climb up`, `Climb down`, `Cancel`).
- Mutable chest/container interaction with score change.
- Large multi-section fire/hazard area in E3M6.
- Standard level-completion statistics screen and values.

## Important caution
The official hint material describes E3M6 as the level that distinguishes large/medium/small fire hazards. The video clearly shows multiple fire presentations, but this audit does **not** assign exact damage or passability values from visuals alone. Those numeric rules should be recovered from `NITE3W.EXE` or verified with controlled gameplay.

## Completion screen
- Level Completed: 6
- Enemies Remaining: 18
- Panels Not Found: 2
- Bonus for Level: 0
- Score so far: 25675

## Deletion status
This source MP4 is now sufficiently audited for the reverse-engineering evidence set. The report preserves its SHA-256, principal timestamps, and selected evidence frames; the original MP4 is not included in the audit package.