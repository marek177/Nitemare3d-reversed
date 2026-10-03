# Nitemare 3D – Episode 3 partial video/MAP audit

This audit covers the most recently supplied Episode 3 walkthrough material. Source MP4 files are **not included**. Video observations are kept separate from MAP/OBJECTS/WALLS evidence so behavior that is not actually shown is not silently invented.

## Coverage and duplicate check

- **E3M1:** only **part 2/2** is available in this batch. The files `E3 L1 (2 2).mp4` and `E3 L1 (2 2)(1).mp4` are byte-for-byte duplicates (same SHA-256 `c0f5bcb352ec1bb9705cdaf3b38b9d0a1314f94d508e55de15c3d2cbf9f53d4c`). Duration: **271.209 s**.
- **E3M2:** complete. Part 1 duration **564.756 s**, SHA-256 `8048ff703bd9bbf99cace769c8ed8b9cf28034d0dccaddcbdb401e39c044daf2`. Part 2 duration **129.660 s**, SHA-256 `92d32775b32eb49ab487b4ee9a9cf74d50d606a89b65bdfec1b087ff9e820846`. The two uploaded copies of part 2 are byte-for-byte duplicates.
- **E3M10 + Ending:** complete supplied video. Duration **178.678 s**, SHA-256 `20ee13b445f0961ea4777ff593ac46dfa9c68c85548988e239f3d640bd658304`.
- **E3M3–E3M9:** not supplied in this batch.

Data correlation uses `MAP.3`, `OBJECTS.3`, `WALLS.3`, plus the original `ENDING.FLI` already supplied with the game data.

## E3M1 – part 2 only

### Final yellow-key lock and chamber route

At approximately **04:17.5** the game explicitly displays:

```text
You use the Yellow key
```

This matches the Episode 3 map definition `WARP_L4` (yellow-key locked wall). The final path in MAP.3 is especially useful for reconstruction:

- yellow-key `WARP_L4` at **(44,59)**,
- `GUARD22` Demon W at **(47,59)**,
- Transportation Chamber Door 1 (`DOORVI`) at **(48,59)**,
- `LEVEL_UP` gateway at **(49,59)**.

The video shows the demon in the red chamber approach, the chamber/gateway sequence, a bright green transition, and then the completion screen.

### Completion

The final screen shows:

```text
Level Completed:     1
Enemies Remaining:  3
Panels Not Found:    3
Bonus for Level:     0
Score so far:        1775
```

### MAP-only mechanics not fully video-confirmed in this half

MAP.3 contains **5 pushable tombstones** at `(22,25)`, `(22,26)`, `(24,26)`, `(21,27)`, `(23,27)`. It also contains four remote-controlled door tiles around `x=44, y=36..40` and five nearby `TRIGGER1` cells surrounding the player start region. Because E3M1 part 1 is missing, this audit does **not** claim the exact remote-door trigger behavior from video and does not treat a push sequence as newly confirmed here.

The level also contains red, green, blue and yellow keys/locks, a red ID card, a `WARP_3` stairs network, five explodable brick walls, seven secret panels and four trunks.

## E3M2 – complete

### Sequential colored key locks

The walkthrough directly confirms three different locked-wall interactions:

- approximately **03:07** — `You use the Red key`
- approximately **03:15** — `You use the Green key`
- approximately **01:57 in part 2** — `You use the Blue key`

The blue-key interaction occurs close to the level exit. MAP.3 places `WARP_L3` (blue-key brick door) at **(15,61)**, Transportation Chamber Door 2 at **(15,57)**, and three `LEVEL_UP` gateway cells at `x=13, y=56..58`.

The second video then shows the chamber approach, green transition, and completion screen.

### Completion

```text
Level Completed:     2
Enemies Remaining:  14
Panels Not Found:    5
Bonus for Level:     0
Score so far:        5125
```

### Data-side mechanics

E3M2 contains four red-key locks, one green-key lock and one blue-key lock, two explodable brick walls, a Yellow ID card, seven secret panels and no `PUSH` objects. Therefore E3M2 is useful for validating locked-wall behavior without pushable-object interactions complicating the test.

A **Yellow ID card** exists in MAP.3 at `(7,4)`, but the supplied videos do not show an unambiguous `You use ... ID card` message at the final chamber door. The reconstruction should therefore keep **colored key locks** and **Transportation Chamber/card logic** separate until EXE or stronger video evidence confirms the precise card-consumption rule.

## E3M10 – final Episode 3 level and ending

### Stair/warp selector

At approximately **00:46** the game displays the familiar three-option selector:

```text
Climb up
Climb down
Cancel
```

MAP.3 contains a multi-cell `WARP_5` stair network, so this level reuses the stair selector rather than the multi-floor elevator UI seen elsewhere.

### Scripted final confrontation

At approximately **01:06** the game displays:

```text
Look! It's Penelope! Where's Dr. Hamerstein?
```

MAP.3 independently contains exactly one `GUARD14` Penelope at **(42,14)**, one `GUARD15` Dr. Hamerstein at **(42,17)** and one `TRIGGER1` at **(52,16)**. The video then shows the fight with Dr. Hamerstein and, after victory, the game displays:

```text
You've won! You've won!
```

This is therefore a scripted boss/finale path rather than a normal exit-door sequence. **E3M10 has no `LEVEL_UP` tile in MAP.3.**

### ENDING.FLI verification

After the victory popup the game plays the supplied `ENDING.FLI`. The original file is FLIC, **320×200**, **488 frames in the FLI header**; FFmpeg decodes 489 frames (the extra decoded frame is consistent with a FLIC ring/repeat frame). Nominal frame rate is `70/9` (~7.78 fps), giving approximately **62.7 seconds** from the header timing.

The original FLI confirms the house scene and the dialogue between Hugo and Penelope. In summary: Penelope thanks Hugo for rescuing her; Hugo says he could not let Dr. Hamerstein prevail and suggests they go home; Penelope says she learned disturbing information about the genetic experiments and must leave for a while; Hugo offers help if needed; they say goodbye.

The walkthrough video adds large yellow editorial captions such as `REMATCH TIME!!!`, `Wait... WHAT!?` and `What a Bitch!`. Those captions **do not exist in the original ENDING.FLI** and must not be reproduced by the reconstructed game.

### Final completion screen

```text
Level Completed:     10
Enemies Remaining:  0
Panels Not Found:    0
Bonus for Level:     10000
Score so far:        55700
```

## Important reconstruction consequences

1. **E3M1 remote-door logic remains pending E3M1 part 1.** The map structure is known, but the trigger/action sequence is not sufficiently video-confirmed.
2. **Pushables remain a general engine mechanic.** E3M1 has five pushable tombstones, while E3M2 has none.
3. **Locked-wall classes are independently confirmed.** Episode 3 video directly shows yellow, red, green and blue key-use messages across E3M1/E3M2.
4. **Do not merge key locks and ID-card chamber logic.** In these videos, the visible exit-route messages are for yellow/blue keys on preceding locked walls; no explicit card-use popup is captured at the chamber door itself.
5. **E3M10 requires a dedicated finale state machine:** stair navigation → trigger → Penelope/Dr. Hamerstein encounter → boss victory popup → `ENDING.FLI` playback → final score screen → main menu.
6. **Walkthrough editorial overlays must be ignored.** The original `ENDING.FLI` provides a clean reference for what belongs to the game.

## Evidence files

The `evidence/` folder contains overview sheets and focused filmstrips for the E3M1 final chamber, E3M2 key locks/exit, E3M10 stair selector, boss sequence, ending, and a reference sheet decoded directly from `ENDING.FLI`. The MP4 walkthrough files are not bundled.