# Nitemare 3D — Episode 3 extended video audit

This audit covers newly supplied E3M1 part 1/2 plus complete E3M7, E3M8 and E3M9 walkthroughs. Source MP4s and frame-evidence images are intentionally not distributed.

## Source integrity

- E3M1 part 1/2: 496.900 s, SHA-256 `345fa66d8b807121a423a0d7fe4842548a16ba359a795f6c245e4fc0285d334a`
- E3M7: 1119.641 s, SHA-256 `90c34ff3f442a8175a71d3008402bcd1e6f0f43c292a42dfa703b824d89f4cbf`
- E3M8: 508.090 s, SHA-256 `deebc56393682fd3e59d7c75e407d6c9f1e9363dcc8a225e8c40a0ff80fb2dd5`
- E3M9: 831.529 s, SHA-256 `43178cb7ef110acfc3d762f5f6e6e28903e633cef6d4f8cb4f9ad8223dbe22f1`

Combined with the previously audited second half, E3M1 is now video-complete.

## E3M1

- Opening is a scripted post-Plasma-Core state with scattered/zeroed inventory and blocked doors.
- About 00:18: stair selector confirms the normal `Climb up / Climb down / Cancel` flow.
- About 03:18.5: attempting a blue-key lock without the key confirms the missing-key branch (`You need a Blue key`).
- Previously audited second half covers the final yellow-key lock, Demon, Transportation Chamber, green transition and completion.

## E3M7

- About 17:47: green-key success message.
- About 18:22.8: yellow-key success message.
- Final chapel/Transportation Booth route leads to the bright-green transition.
- Completion observed: Level 7; 2 enemies remaining; 2 panels not found; score 33575.

## E3M8

- The same green key is successfully used at multiple different green-key doors, directly confirming that colored keys persist and are not consumed.
- About 08:06.2: blue-key success message near the exit.
- Completion observed: Level 8; 27 enemies remaining; 18 panels not found; score 38025.

## E3M9

- About 12:51–12:55: elevator selector shows Floor 1 and Floor 2 only; no visible Cancel entry.
- About 13:39.8: approaching the cracked Mirror of Destiny immediately triggers the bright-green transition, strongly supporting a dedicated scripted mirror warp/exit path.
- Completion observed: Level 9; 2 enemies remaining; 4 panels not found; score 44700.

## Reconstruction consequences

1. Colored keys are persistent inventory permissions, not one-shot consumables.
2. Locked-door logic needs separate missing-key and owned-key success branches.
3. Stairs and elevators are separate interaction/UI classes.
4. E3M9 needs a dedicated MirrorWarp/scripted mirror exit.
5. Preserve the bright-green transition used by Transportation Booth and special level exits.
6. E3M1 can be marked video-complete when both halves are combined.
