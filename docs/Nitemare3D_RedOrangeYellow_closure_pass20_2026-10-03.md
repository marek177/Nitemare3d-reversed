# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 20

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- all ranges below are unpacked MZ image offsets
- physical EXE file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative
- far-call targets are linearized only when the actual segment:offset call establishes
  that mapping
- static GREEN is separate from runtime/pixel acceptance

## Result

Pass 20 closes the complete contiguous region

`0xF43E .. 0xFD3F`

as **GREEN / deep static semantics**.

Total span: **2,306 bytes**

- bounded executable routine content: **2,292 bytes**
- inter-function alignment NOPs: **14 bytes**

This pass closes the remaining top-level DOS menu/save/load flow and the small
gameplay/runtime utility tail immediately following it.

The largest correction is and reversal in the old tracker:

- `F494` is the **LOAD-game slot dialog**
- `F5D6` is the **SAVE-game slot dialog**

The raw call targets make this unambiguous.

Pass 20 also closes:

- options/configuration menu loop;
- quick-save and quick-load confirmation paths;
- main-menu variant selection;
- map-set / episode availability probing;
- DEMO scene/session bootstrap;
- complete top-level main-menu action dispatcher;
- fatal printf-style error exit;
- timestamped status output;
- conventional-memory probe;
- direct DOS read/write wrappers;
- bit reversal;
- exact custom rounded integer square root;
- rounded 2-D vector length.

---

# 1. image `0xF43E..0xF493` — `RunOptionsMenuLoop`

Length: **86 bytes**

This is the top-level **Configure game...** submenu loop.

Each pass:

1. displays presentation/resource screen `9` through `D690`;
2. runs `EBD6 = RunInteractiveMenu` on menu table `20B9:103E`;
3. dispatches selected actions.

Known result routing:

```text
0x23 -> F150  hardware settings
0x0E -> F33A  cheat settings

0x06 -> exit
0x15 -> exit
0x16 -> exit
```

When and dispatched settings submenu reports success, this function calls the
configuration persistence path at image `0x3474`, then returns.

Thus:

```text
Configure game
    -> Hardware...
    -> Cheats...
    -> persist accepted CONFIG changes
```

is statically closed at the menu-orchestration level.

**Status: YELLOW -> GREEN.**

---

# 2. image `0xF494..0xF5D4` — `RunLoadGameSlotDialog`

Length: **321 bytes**

## Important correction

The old hard-closure table called `F494` the save selector.

Raw DOS V2.0 machine code shows that `F494` is the **LOAD** dialog.

It uses literal:

`user.sav`

and builds ten temporary 18-byte menu rows.

## Ten-slot construction

For each slot `0..9`:

1. probe/read USER.SAV slot metadata;
2. if invalid/empty:
   - copy the fixed empty-slot placeholder:
     `"          ** Empty slot **"`
   - make the row disabled (`type 6`);
3. if valid:
   - copy the saved description/name;
   - make the row selectable (`type 1`);
4. store slot metadata required by the restore path.

The rows are then passed to `RunInteractiveMenu`.

## Accepted selection

On accepted selection, the highlighted row yields the zero-based slot index.

When the caller requests scene synchronization, the saved episode/level metadata is
compared with current:

```text
DS:626A  episode
DS:626C  level
```

If different, the corresponding level scene is initialized first through `DBEA`.

The routine then invokes the USER.SAV **restore/read** path at image `0x38E6` using:

- literal `user.sav`;
- selected slot index.

It restores font bank 2 before returning.

Return:

- selected slot index on accepted load;
- `-1` on cancel/no accepted slot.

**Status: old mislabeled slot routine -> GREEN.**

---

# 3. image `0xF5D6..0xF6B8` — `RunSaveGameSlotDialog`

Length: **227 bytes**

This is the complementary **SAVE** dialog.

The old hard-closure register had the load/save identities reversed.

## Row preparation

The routine:

1. displays the save-game presentation screen;
2. probes the same ten USER.SAV slots;
3. fills their descriptions;
4. uses the same empty-slot placeholder for missing entries;
5. creates editable menu rows.

These rows are menu type `4`, with `EBD6` invokes `E1DE/DE36` to edit the save name.

## Accepted save

The save action is accepted when the relevant menu command completes.

The routine finds the selected row and calls the USER.SAV **write/save** path at
image `0x358C` with:

- selected row'with edited description;
- literal `user.sav`;
- zero-based slot index.

Return:

- selected slot index on accepted save;
- `-1` otherwise.

This exactly explains why save slots use editable 41-byte descriptions while load
slots are ordinary selectable rows.

`0xF5D5` is alignment NOP.

**Status: old mislabeled slot routine -> GREEN.**

---

# 4. image `0xF6BA..0xF724` — `QuickSaveWithConfirmation`

Length: **107 bytes**

Uses remembered/last slot:

`DS:3CC4`.

## No remembered slot

When `3CC4 < 0`:

1. open `RunSaveGameSlotDialog`;
2. store returned slot in `3CC4`;
3. return through the gameplay-display restore helper at `E916`.

## Remembered slot

When and valid remembered slot exists:

1. probe its saved description from `user.sav`;
2. format:

```text
About to SAVE game:
"<slot description>"
Press ESC to abort...
```

3. display/read the prompt through `D9B0`;
4. Escape cancels;
5. otherwise call the USER.SAV save/write path at `0x358C`.

This is the exact DOS quick-save confirmation behavior.

`0xF6B9` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 5. image `0xF726..0xF7BD` — `QuickLoadWithConfirmation`

Length: **152 bytes**

Symmetric to quick save.

Uses:

`DS:3CC4`

as remembered slot.

## No remembered slot

When no slot is remembered:

1. call `RunLoadGameSlotDialog` with scene-sync enabled;
2. store selected slot in `3CC4`;
3. restore gameplay presentation through `E916`.

## Remembered slot

Formats:

```text
About to LOAD game:
"<slot description>"
Press ESC to abort...
```

Escape cancels.

Otherwise it calls the USER.SAV read/restore path at:

`0x38E6`

for the remembered slot, then runs the gameplay/display re-entry sequence.

`0xF725` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 6. image `0xF7BE..0xF899` — `SelectMainMenuVariantForSceneState`

Length: **220 bytes**

This chooses which top-level menu table should be shown.

It normalizes the initial selection markers in the candidate tables with that the
expected default action is highlighted.

The returned menu depends on:

- caller mode;
- `DS:3CD4` gameplay/session state;
- remembered slot state.

## Restart-at-last-save check

When scene state is `3` and and remembered slot index is nonnegative:

1. probe USER.SAV metadata for that slot;
2. compare saved level with:
   `DS:626C`;
3. compare saved episode with:
   `DS:626A`.

When both match the current scene, the function selects the special menu variant whose
action text is equivalent to:

`Restart at last save`

instead of ordinary:

`Return to game`.

Return is and far pointer to the selected 18-byte menu table.

This closes the DOS counterpart of the three known top-level menu variants:

- front-end;
- in-game;
- restart-at-last-save.

**Status: YELLOW -> GREEN.**

---

# 7. image `0xF89A..0xF925` — `ChooseAvailableMapSet`

Length: **140 bytes**

This is not and save-slot routine.

It builds labels/files using:

```text
"map."
"%s%d"
```

and tests map-set numbers starting at `1`.

AND candidate row is selectable when:

- the corresponding `map.N` file exists; and
- either:
  - BSF selector 1 reports registered/full, or
  - `N == 1`.

It then runs and small menu and maps the returned action code back to the selected map
set.

Cancel returns zero.

This is the DOS episode/map-set availability chooser used by New Game.

**Status: old generic record-slot name -> GREEN.**

---

# 8. image `0xF926..0xF970` — `FindFirstAvailableMapSet`

Length: **75 bytes**

Scans:

`N = 1 .. 6`

and formats:

`map.N`.

For each candidate:

1. test whether the file exists;
2. require either:
   - registered/full BSF capability, or
   - `N == 1`.

Returns the first accepted map set.

If none of `1..6` succeeds:

`return 7`.

This helper is used by the DEMO bootstrap.

**Status: old generic record-slot helper -> GREEN.**

---

# 9. image `0xF972..0xF98A` — `InitializeDemoSceneForAvailableMapSet`

Length: **25 bytes**

Hidden real function entry.

Flow:

1. call `FindFirstAvailableMapSet`;
2. if selected set is `1`:
   - choose level index `10`;
3. otherwise:
   - choose level index `0`;
4. call `DBEA = InitializeLevelScene`.

This is DEMO scene setup.

The existing uncertainty about the exact content identity of DEMO.2/DEMO.3 is not
resolved merely by this helper; the machine behavior of this bootstrap is nevertheless
closed.

`0xF971` is alignment NOP.

**Status: hidden entry -> GREEN.**

---

# 10. image `0xF98C..0xF9CE` — `RunDemoPlaybackSession`

Length: **67 bytes**

Hidden real entry.

If current DEMO mode is not already `1`, set:

`DS:3CD6 = 3`

which is the start-playback state consumed by the closed DEMO state machine.

Then:

1. run input/platform preparation;
2. call `InitializeDemoSceneForAvailableMapSet`;
3. clear render generation:
   `DS:4540 = 0`;
4. run `E964 = RunGameplaySessionAndPostSequence`;
5. on return set:
   `DS:3CD6 = 5`;
6. run cleanup.

This is the outer DOS DEMO-session runner.

`0xF98B` is alignment NOP.

**Status: hidden DEMO entry -> GREEN.**

---

# 11. image `0xF9D0..0xF9DB` — `ShowWeaponJammedMessage`

Length: **12 bytes**

Thin prompt wrapper around literal:

`Your weapon appears to be jammed!`

using the normal modal prompt function.

This is the already known weapon-jam feedback path.

`0xF9CF` is alignment NOP.

**Status: GREEN / confirmed.**

---

# 12. image `0xF9DC..0xFBAA` — `RunMainMenuLoop`

Length: **463 bytes**

This is the complete DOS top-level menu loop.

## Opening presentation

When the caller'with startup/display flag requests it:

- call `DA56 = ShowOpeningPresentationSequence`.

The menu then enters its regular loop.

## Menu selection

1. choose the appropriate front-end/in-game/restart menu through `F7BE`;
2. display PCX/resource screen `6`;
3. run `EBD6 = RunInteractiveMenu`.

The menu result is dispatched by an inline eight-entry WORD jump table.

### Action 1 — New Game

- call `ChooseAvailableMapSet`;
- if accepted, display difficulty-selection screen/resource `8`;
- difficulty actions map to:

```text
0x12 -> DS:4180 = 0
0x13 -> DS:4180 = 1
0x14 -> DS:4180 = 2
```

- initialize requested level/episode through `DBEA`;
- enter gameplay session through `E964`.

### Action 2 — Configure game

Call:

`F43E = RunOptionsMenuLoop`.

### Action 3 — Load game

Call:

`F494 = RunLoadGameSlotDialog`

and remember the resulting slot in:

`DS:3CC4`.

### Action 4 — Save game

Call:

`F5D6 = RunSaveGameSlotDialog`

and remember the resulting slot.

### Action 5 — Instructions

Open the BSF document viewer with:

- background resource `16`;
- BSF selector `3` = HELP/manual block.

### Action 6 — Quit

Prompt:

`Really quit?`

Only uppercase:

`'Y'`

accepts the quit.

Any other response returns to the menu.

### Action 7 — Demo

The routine snapshots the 16-byte runtime configuration block.

For DEMO playback it temporarily changes input/cheat settings, including forcing the
resource-grant cheat state used by the demo environment.

It runs the DEMO session until the game state returns to the menu, then restores the
saved configuration block.

### Action 8 — Return/resume game

Enter the gameplay session through `E964`.

## Inline data

`0xFA36..0xFA45`

is an **8-WORD action jump table**.

Mark it:

`GREEN knowledge + TABLE/DATA overlay`.

**Status: YELLOW -> GREEN.**

---

# 13. image `0xFBAC..0xFBD4` — `FatalErrorPrintfAndExit`

Length: **41 bytes**

This is and variadic fatal-error reporter.

Flow:

1. shut down game subsystems through the already closed shutdown path;
2. pass caller format string and varargs pointer to:
   `11EE:285A`;
3. that far target maps to image `0x1473A`, the already closed printf/stdout-style
   formatted-output wrapper;
4. print final:
   `".\n"`;
5. terminate with error status `1`.

This explains why many engine fatal helpers can supply an error code/text and not
return.

`0xFBAB` is alignment NOP.

**Status: old weak generic helper -> GREEN.**

---

# 14. image `0xFBD6..0xFBF6` — `PrintTimestampedStatusMessage`

Length: **33 bytes**

Calls far runtime helper:

`11EE:2EB4`

which maps to image `0x14D94`.

That runtime helper obtains DOS time through:

`INT 21h, AH=2Ch`

and formats an ASCII timestamp:

`HH:MM:SS`.

This function then prints:

```text
%s: %s\n
```

using:

- local timestamp;
- caller-supplied text.

This is and timestamped stream/status-output helper.

It should **not** automatically be conflated with the separate `debug.txt` logger
unless and concrete caller establishes that connection.

`0xFBD5` is alignment NOP.

**Status: old failure-message label -> GREEN with corrected role.**

---

# 15. image `0xFBF8..0xFC3C` — `ProbeLargestAllocatableKiB`

Length: **69 bytes**

Starts with candidate:

`0x400`

and decrements before each test, with maximum tried amount is:

`1023 KiB`.

For every candidate:

1. request:
   `candidate << 10`
   bytes through the already closed far zero-initializing allocator;
2. if allocation succeeds:
   - immediately free it;
   - return candidate;
3. otherwise continue downward.

If every candidate fails:

`return 0`.

This is and conventional-memory availability probe expressed in KiB.

`0xFBF7` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 16. image `0xFC3E..0xFC56` — `DosRead`

Length: **25 bytes**

Direct DOS file read wrapper:

```text
BX = handle
DS:DX = buffer
CX = byteCount
AH = 3Fh
INT 21h
```

On success:

- AX = bytes read.

On carry/error:

- AX = `0xFFFF`.

The old generic "call DOS service" label can be replaced with the exact service.

`0xFC3D` is alignment NOP.

**Status: LOW -> GREEN.**

---

# 17. image `0xFC58..0xFC70` — `DosWrite`

Length: **25 bytes**

Direct DOS file write wrapper:

```text
BX = handle
DS:DX = buffer
CX = byteCount
AH = 40h
INT 21h
```

On success:

- AX = bytes written.

On carry/error:

- AX = `0xFFFF`.

`0xFC57` is alignment NOP.

**Status: LOW -> GREEN.**

---

# 18. image `0xFC72..0xFCAA` — `ReverseBitsInByte`

Length: **57 bytes**

In-place exact bit reversal.

Starting masks:

```text
sourceMask = 0x80
destMask   = 0x01
```

For exactly eight iterations:

- if source bit is set, set the corresponding destination bit;
- source mask shifts right;
- destination mask shifts left.

Final reversed byte is written back to the caller'with location.

This is used by the DOS font bitmap loading path.

`0xFC71` is alignment NOP.

**Status: YELLOW -> GREEN.**

---

# 19. image `0xFCAC..0xFCB7` — `SquareSigned16To32`

Length: **12 bytes**

Raw `IMUL`-based helper.

Input:

`signed 16-bit value`

Output:

`DX:AX = value * value`

The old decompiled C signature exposed only AX and therefore hid the high word.

For compatibility this is and 32-bit product helper.

`0xFCAB` is alignment NOP.

**Status: LOW -> GREEN with corrected return width.**

---

# 20. image `0xFCB8..0xFD17` — `RoundedIntegerSqrt16`

Length: **96 bytes**

This is Nitemare-3D'with custom integer square-root routine.

For:

`n < 2`

it returns `n`.

Otherwise it processes eight two-bit groups using and restoring square-root algorithm.

After the base root is produced, the function applies and nonstandard upward correction.

For the gameplay/map-distance domain already exhaustively checked:

```text
q = floor(sqrt(n))

result =
    n                              if n <= 1
    q + (n - q*q >= q - 1)        otherwise
```

Examples:

```text
sqrtN3D(2) = 2
sqrtN3D(5) = 3
```

which intentionally differ from plain `floor(sqrt())`.

This is the exact helper used by actor/player distance calculations.

**Status: YELLOW -> GREEN.**

---

# 21. image `0xFD18..0xFD3E` — `ComputeRoundedVectorLength`

Length: **39 bytes**

Inputs:

- signed 16-bit X delta;
- signed 16-bit Y delta.

Computes:

```text
n = x*x + y*y
return RoundedIntegerSqrt16(n)
```

The old C export incorrectly presented the function as `void`; raw machine-code ABI
returns the square-root result in AX.

For normal 64×64 map-cell coordinate deltas, the previously audited input domain does
not overflow the sum.

This helper feeds the GUARD/contact-damage distance path.

`0xFD3F` is alignment NOP.

**Status: YELLOW -> GREEN with corrected return ABI.**

---

# 22. Byte-map impact

New continuous GREEN span:

`0xF43E .. 0xFD3F`

Total: **2,306 bytes**

| Image range | Bytes | Role |
|---|---:|---|
| `F43E–F493` | 86 | options/config menu loop |
| `F494–F5D4` | 321 | LOAD-game 10-slot dialog |
| `F5D6–F6B8` | 227 | SAVE-game 10-slot dialog |
| `F6BA–F724` | 107 | quick-save confirmation |
| `F726–F7BD` | 152 | quick-load confirmation |
| `F7BE–F899` | 220 | top-level menu variant selector |
| `F89A–F925` | 140 | available map-set chooser |
| `F926–F970` | 75 | first available map set |
| `F972–F98A` | 25 | DEMO scene bootstrap |
| `F98C–F9CE` | 67 | DEMO session runner |
| `F9D0–F9DB` | 12 | weapon-jammed prompt |
| `F9DC–FBAA` | 463 | main menu dispatcher |
| `FBAC–FBD4` | 41 | fatal printf + exit |
| `FBD6–FBF6` | 33 | timestamped status output |
| `FBF8–FC3C` | 69 | conventional-memory KiB probe |
| `FC3E–FC56` | 25 | DOS read, AH=3Fh |
| `FC58–FC70` | 25 | DOS write, AH=40h |
| `FC72–FCAA` | 57 | reverse bits in byte |
| `FCAC–FCB7` | 12 | signed16 square -> DX:AX |
| `FCB8–FD17` | 96 | custom rounded integer sqrt |
| `FD18–FD3E` | 39 | rounded 2-D vector length |

Executable routine content: **2,292 bytes**.

Alignment NOPs:

```text
F5D5
F6B9
F725
F971
F98B
F9CF
FBAB
FBD5
FBF7
FC3D
FC57
FC71
FCAB
FD3F
```

Total: **14 bytes**.

### TABLE/DATA overlay

```text
FA36–FA45  8-WORD main-menu action jump table
```

Mark it:

`GREEN knowledge + TABLE/DATA overlay`.

---

# 23. Major tracker corrections

Replace the old reversed slot labels:

```text
F494  SelectSaveGameSlot
F5D6  SelectLoadGameSlot
```

with:

```text
F494  RunLoadGameSlotDialog
F5D6  RunSaveGameSlotDialog
```

Add hidden real entries:

```text
F972  InitializeDemoSceneForAvailableMapSet
F98C  RunDemoPlaybackSession
```

Tighten:

```text
F89A  ChooseAvailableMapSet
F926  FindFirstAvailableMapSet
F9DC  RunMainMenuLoop
FBAC  FatalErrorPrintfAndExit
FBD6  PrintTimestampedStatusMessage
FBF8  ProbeLargestAllocatableKiB
FC3E  DosRead
FC58  DosWrite
FCAC  SquareSigned16To32
FD18  ComputeRoundedVectorLength
```

---

# 24. USER.SAV consequence

The menu code independently confirms the fixed multi-slot architecture already known
from the save format:

- exactly ten visible menu slots are constructed;
- slots contain an editable/saved description;
- LOAD and SAVE are separate dialogs;
- and remembered slot is retained for quick save/load;
- saved episode/level metadata is inspected before load scene reinitialization.

The detailed serialization inside the lower USER.SAV writer/reader remains and separate
static area; closing this menu band does not automatically mark those subordinate
serialization routines GREEN.

---

# 25. Cumulative closure

Pass 19 cumulative since the pass-5 baseline:

`39,500 bytes`

Pass 20 adds: