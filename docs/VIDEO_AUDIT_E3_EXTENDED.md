# Nitemare 3D — Episode 3 extended video audit

This audit adds the newly supplied **E3M1 part 1/2**, **E3M7**, **E3M8**, and **E3M9** walkthrough videos to the earlier Episode 3 audit. The MP4 source files are intentionally not bundled. All timestamps are approximate and refer to the newly supplied files.

## Source integrity

| Level | Duration | SHA-256 |
|---|---:|---|
| E3M1 part 1/2 | 496.900 s | `345fa66d8b807121a423a0d7fe4842548a16ba359a795f6c245e4fc0285d334a` |
| E3M7 | 1119.641 s | `90c34ff3f442a8175a71d3008402bcd1e6f0f43c292a42dfa703b824d89f4cbf` |
| E3M8 | 508.090 s | `deebc56393682fd3e59d7c75e407d6c9f1e9363dcc8a225e8c40a0ff80fb2dd5` |
| E3M9 | 831.529 s | `43178cb7ef110acfc3d762f5f6e6e28903e633cef6d4f8cb4f9ad8223dbe22f1` |

Combined with the already audited E3M1 part 2/2, **E3M1 is now fully covered by video**. E3M7–E3M9 are complete single-file walkthroughs.

## E3M1 — part 1/2 added

### Opening story state
At about **00:05** the game shows the Episode 3 opening story popup:

> You recover to witness the defunct plasma core's residual radiation slowly decaying.
>
> When the plasma core imploded into another dimension the blast jammed the automatic doors shut and scattered your possessions.
>
> There does not appear to be any way out!

This is important for reconstruction because the player begins Episode 3 with **zeroed/scattered inventory** and a scripted blocked-door situation rather than a normal level start.

### Stair selector
At about **00:18** the familiar stairs UI is visible:

- `Climb up`
- `Climb down`
- `Cancel`

This is the same three-choice stair/warp selector family seen in other levels and remains distinct from elevator-floor selection.

### Locked-door denial text
At about **03:18.5**, attempting a blue-key lock without the key produces:

`You need a Blue key`

This complements the success messages already captured elsewhere (`You use the Blue key`) and gives us both branches of the locked-door state machine.

### E3M1 coverage consequence
The first half visibly covers the post-Plasma-Core opening, ghost-heavy stone/chapel areas, trunks, keys and graveyard traversal. The previously audited second half contains the final yellow-key lock, Demon, Transportation Chamber, green transition and level result. Together the two videos now provide full E3M1 walkthrough coverage.

## E3M7 — complete video

### Reusable colored locks
Near the final route the video explicitly shows:

- about **17:47** — `You use the Green key`
- about **18:22.8** — `You use the Yellow key`

The yellow lock leads into the final chapel/Transportation Booth route.

### Exit and result
At roughly **18:31–18:32** the booth/exit produces the bright green transition. The completion screen then shows:

- Level Completed: **7**
- Enemies Remaining: **2**
- Panels Not Found: **2**
- Bonus for Level: **0**
- Score so far: **33575**

The video also directly shows the extensive fire-field traversal used by this level. The exact large/medium/small fire damage classes remain best documented by original game documentation, while the video confirms that fire tiles are active hazards affecting the player's route and health.

## E3M8 — complete video

### Strong evidence that keys are persistent, not consumed
The walkthrough shows `You use the Green key` at several separate green-key doors on the route (approximately **07:11**, **07:17**, and **07:27**). The same green key remains usable afterward. This is direct video evidence that a colored key is an inventory permission flag rather than a one-shot consumable.

Near the exit, at about **08:06.2**, the game shows:

`You use the Blue key`

### Exit and result
The player then reaches the Transportation Booth and the usual bright-green transition. The completion screen shows:

- Level Completed: **8**
- Enemies Remaining: **27**
- Panels Not Found: **18**
- Bonus for Level: **0**
- Score so far: **38025**

For reconstruction, the repeated green-key interactions are one of the strongest direct observations in the current audit because they establish key persistence independently of EXE disassembly.

## E3M9 — complete video

### Two-floor elevator selector
At approximately **12:51–12:55** the elevator UI shows only:

- `Floor 1`
- `Floor 2`

No `Cancel` entry is visible. This matches the two-floor elevator selector pattern and should not be implemented using the stair selector UI.

### Cracked Mirror of Destiny exit
At about **13:39.8** the player approaches the large cracked circular mirror in the white control area. Immediately afterward the game enters the characteristic bright-green transition. This is strong evidence that the cracked Mirror of Destiny acts as a **special scripted warp/exit trigger**, rather than a conventional door.

### Completion
The result screen shows:

- Level Completed: **9**
- Enemies Remaining: **2**
- Panels Not Found: **4**
- Bonus for Level: **0**
- Score so far: **44700**

## Reconstruction consequences

1. **Colored keys are persistent.** Do not remove a key after a successful locked-door interaction.
2. Implement separate locked-door messages for missing vs. owned key: `You need a <color> key` and `You use the <color> key`.
3. **Stairs and elevators are separate interaction classes/UI flows.** Stairs can expose `Climb up / Climb down / Cancel`; E3M9 elevator exposes `Floor 1 / Floor 2`.
4. Add a dedicated **MirrorWarp / scripted mirror exit** path for E3M9. It directly triggers the level transition.
5. Preserve the **bright green transition** used by Transportation Booth / special level exits before the completion screen.
6. E3M1 can now be marked **video-complete** when this part 1/2 audit is combined with the existing part 2/2 audit.

## Evidence

The `evidence/` directory contains stills for the E3M1 story/stair/blue-key-denial events, E3M7 green/yellow key and completion, E3M8 green/blue key and completion, and E3M9 elevator/mirror/completion events.