# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 19

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- all ranges below are unpacked MZ image offsets
- physical EXE file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative
- static GREEN remains separate from runtime/pixel acceptance

## Result

Pass 19 closes the complete contiguous menu/configuration region:

`0xE9DC .. 0xF43D`

as **GREEN / deep static semantics**.

Total span: **2,658 bytes**

- bounded executable routine content: **2,650 bytes**
- inter-function alignment NOPs: **8 bytes**

This pass closes:

- the exact 18-byte menu-record renderer;
- menu selection movement;
- the complete generic interactive-menu engine;
- elevator/floor and stair/variant choice dialogs;
- key-requirement prompt logic;
- remote-control-card dispatch;
- hardware settings staging/apply logic;
- the DOS cheat settings menu and registered/shareware gate.

The largest semantic correction is `F33A`: it is not "control bindings".
Its four staged values are the four cheat flags at `DS:4150..4153`.

---

# 1. image `0xE9DC..0xEB42` — `DrawMenuItem`

Length: **359 bytes**

Input:

- far pointer to one 18-byte menu record.

Confirmed record layout:

```text
+00 byte   action/result ID
+01 byte   subtype/context value
+02 word   value
+04 byte   current-selection marker
+05 byte   menu item type
+06 dword  optional far callback
+0A word   X
+0C word   Y
+0E dword  far text pointer
```

Known item types used by the raw menu engine:

```text
1 = command/action
2 = toggle
3 = signed enable+magnitude control
4 = editable text
6 = disabled/unavailable
```

## Label color/style

Type `6` obtains and disabled style.

Other rows obtain the normal style.

When selection byte `+4` is nonzero, the selected-row style overrides that value.

The label at `+0E` is drawn at `+0A/+0C`.

## Type-3 slider/value bar

For item type `3`, the function also draws and horizontal control track.

Magnitude:

```text
abs(record.value)
```

is scaled to:

```text
abs(value) * 80 / 100
```

giving an 80-unit maximum bar width.

Thus type-3 records encode both:

- sign = enabled/disabled state;
- absolute value = 0..100 magnitude.

## State marker

The function draws the small row-state marker around:

```text
X - 12
Y + 2
```

and derives its visible state from selection/value information.

This is the renderer counterpart of the sign/toggle logic in `EBD6`.

**Status: YELLOW -> GREEN.**

---

# 2. image `0xEB44..0xEBD4` — `MoveMenuSelection`

Length: **145 bytes**

Inputs include:

- first menu record;
- last menu record;
- current menu record;
- direction:
  - `-1`
  - `+1`.

Exact behavior:

1. clear current record `+4`;
2. redraw current row through `DrawMenuItem`;
3. step through the array by:
   `0x12 = 18 bytes`;
4. stop at first non-disabled record;
5. wrap at the supplied first/last boundaries;
6. limit search to at most `100` checks;
7. set new record `+4 = 1`;
8. redraw it;
9. return far pointer to the selected record.

Rows with:

`type == 6`

are skipped.

**Status: YELLOW -> GREEN.**

---

# 3. image `0xEBD6..0xEDA1` — `RunInteractiveMenu`

Length: **460 bytes**

This is the central DOS menu engine.

Input:

- far pointer to the first 18-byte row.

## Initial drawing

1. select font bank 2;
2. walk rows until action byte `+00 == 0`;
3. draw row text;
4. call `DrawMenuItem` for each row;
5. find the row whose selection byte `+04 != 0`.

If no selected row exists, the engine enters the fatal menu-definition path.

## Input source

Input is read through:

`6EBE = ReadAndTranslateUserInput`.

Direct event handling:

```text
0x0D  Enter
0x20  Space
0x1B  Escape
0x48  Up
0x50  Down
0x4B  Left
0x4D  Right
```

## Up / Down

Call `MoveMenuSelection` with:

```text
-1  for Up
+1  for Down
```

## Escape

Returns menu code:

`6`.

## Enter / Space activation by row type

### Type 1 — command

Set exit flag.

The routine later returns:

`row.action`.

### Type 2 — toggle

```text
row.value ^= 1
```

and redraw.

### Type 3 — signed control

Activation negates the value:

```text
row.value = -row.value
```

This toggles enabled/disabled while preserving magnitude.

### Type 4 — editable text

Call:

`E1DE = EditMenuTextRow`

The editor'with result becomes the menu-exit/accepted state.

## Left / Right on type 3

Only type 3 accepts left/right magnitude adjustment.

First:

```text
row.value = abs(row.value)
```

Then:

```text
Left  -> value -= 5
Right -> value += 5
```

Clamp:

```text
0 .. 100
```

and redraw.

## Per-row callback

At the end of every menu loop iteration:

```text
if row.callback != NULL:
    call far row.callback
```

This is why hardware settings can apply/preview changes while the menu remains open.

## Return

When activation completes:

```text
return row.action
```

Cancel/Escape returns `6`.

**Status: YELLOW -> GREEN.**

---

# 4. image `0xEDA2..0xEE62` — `ChooseElevatorFloor`

Length: **193 bytes**

This is the dynamic floor/level chooser.

The routine saves current level:

`DS:626C`

as the default result.

It reads the active episode/map count from:

`DS:D30C`.

If the count is `>= 11`, it enters the fatal range-check path.

Thus at most ten floor entries are presented.

## Dynamic rows

It enables one 18-byte row for each available floor in the table around:

`DS:1301`.

AND terminating zero row is written immediately after the active entries.

The dialog height is derived from the number of entries.

It then runs:

`RunInteractiveMenu`

over the dynamic floor list.

## Result

When menu result is:

`0x17`

the routine scans the rows for the selected marker and returns that zero-based floor
index.

For any other result it returns the previously saved:

`DS:626C`.

This matches the runtime "Floor 1 ... Floor 10" elevator chooser.

**Status: YELLOW -> GREEN.**

---

# 5. image `0xEE64..0xEF05` — `ChooseStairDirection`

Length: **162 bytes**

The routine evaluates two map/wall-state candidates and marks the corresponding menu
rows usable/disabled before showing and small contextual movement dialog.

Two rows are converted to:

```text
type 1  = usable
type 6  = unavailable
```

according to whether their computed current wall/state values equal the caller'with
current value.

It then draws the contextual panel and runs the menu table near:

`DS:13C2`.

Return mapping is exact:

```text
menu 6 or 0x16 ->  0
menu 0x18      -> +1
menu 0x19      -> -1
```

The ±1 result is the stair/directional choice consumed by the caller.

Other unrecognized menu IDs preserve the routine'with original local-value behavior.

**Status: YELLOW -> GREEN.**

---

# 6. image `0xEF06..0xF03E` — `ChooseAvailableWallVariantFromRange`

Length: **313 bytes**

This builds and contextual selection list from one primary-wall class.

Inputs include:

- currently selected value;
- wall class code.

## Range discovery

It calls:

- `0F74 = FindPrimaryWallClassIndex`
- `103E = FindHighestPrimaryWallIndexInMap`

to derive the inclusive runtime index range.

Count:

```text
high - low + 1
```

must be below 11.

Therefore the dynamic list is again limited to ten entries.

## Per-row availability

Rows are created at the same dynamic menu-table area.

When Omnifarious cheat is disabled, availability can be restricted using:

- player'with card mask `DS:4193`;
- level card-availability mask `DS:D511`.

Unavailable rows are changed to:

`type 6`.

The caller-selected value gets the selection marker.

## Result

On accepted menu result:

`0x17`

the selected row is converted back to the wall/index value.

Cancel results:

```text
6
0x16
```

return zero.

This is the generic contextual wall/transport selection helper used by higher-level
USE/transition logic.

**Status: YELLOW -> GREEN.**

---

# 7. image `0xF040..0xF0A8` — `ShowSingleContextChoice`

Length: **105 bytes**

The routine first obtains and current wall/index state.

If it already equals the caller'with requested value:

```text
return 0
```

Otherwise it displays and small contextual menu rooted near:

`DS:140A`.

Return mapping:

```text
menu 0x1A -> -1
menu 6    -> 0
menu 0x16 -> 0
```

Other paths preserve the routine'with original local return behavior.

This is the compact one-direction/context choice dialog used by special navigation
logic.

**Status: YELLOW -> GREEN.**

---

# 8. image `0xF0AA..0xF113` — `CheckKeyRequirementAndPrompt`

Length: **106 bytes**

Input contains and key-requirement code in the range mapped by:

```text
index = input - 0x19
```

That index selects one of four far text resources through:

`A306 = GetIndexedFourEntryFarPointer`.

It also maps directly to one bit of the player key mask:

`DS:4192`.

## Owned key

If the bit is set:

- trigger success/open feedback through `923A` (`effect 0x32`).

## Prompt text

The routine selects one of two fixed text fragments according to whether the key is
owned, combines it with the indexed key-name string, and formats the result into and
local 70-byte buffer.

That prompt is displayed/read through:

`D9B0 = ReadPromptedInputSymbol`.

Return:

```text
1 = required key owned
0 = required key missing
```

The user-input return from the prompt is not the function'with return value; ownership is.

**Status: hidden/weak key UI helper -> GREEN.**

---

# 9. image `0xF114..0xF14E` — `DispatchRemoteControlCardAction`

Length: **59 bytes**

Input:

- pointer to and small context/action record.

It reads:

`record+1`

as the remote-control/card channel.

Then tests:

```text
1 << record[1]
```

against player card mask:

`DS:4193`.

## Card owned

Call:

`9646 = HandleRemoteDoorAndCannonControl(record[1])`.

## Card missing

Call:

`A33A = FormatAndDisplayIndexedMessage(record[1])`.

Thus this is the bridge between ID-card possession and the remote-control menu.

**Status: YELLOW -> GREEN.**

---

# 10. image `0xF150..0xF1F1` — `RunHardwareSettingsMenu`

Length: **162 bytes**

This function stages the current runtime hardware settings into the 18-byte menu rows
at:

`DS:1212`.

The row markers are:

```text
0x0A  Mouse
0x0B  Joystick
0x0C  Sound FX
0x0D  Music
```

For each row it stores and signed type-3 value.

## Mouse

Magnitude:

`DS:4148`

Enable:

`DS:414C`

## Joystick

Magnitude:

`DS:4149`

Enable:

`DS:414F`

## Sound FX

Magnitude:

`DS:414B`

Enable:

`DS:414E`

## Music

Magnitude:

`DS:414A`

Enable:

`DS:414D`

When the feature is disabled, the magnitude is stored negated.

That exactly matches the generic type-3 menu encoding:

```text
positive = enabled
negative = disabled
abs(value) = magnitude
```

The routine then:

1. displays configuration PCX/resource `10`;
2. runs `RunInteractiveMenu` on the hardware table;
3. returns `1` only for accepted/save action `0x15`;
4. otherwise returns `0`.

**Status: YELLOW -> GREEN.**

---

# 11. image `0xF1F2..0xF338` — `ApplyHardwareSettingsChanges`

Length: **327 bytes**

This is the active callback/application side of the hardware menu.

It first snapshots the 16-byte configuration block:

`DS:4144..4153`.

Then it scans the same menu rows at `1212`.

For row markers `0x0A..0x0D`, each signed menu value is split into:

```text
enabled = value > 0
magnitude = abs(value)
```

and written into the snapshot fields corresponding to:

- mouse enable/sensitivity;
- joystick enable/sensitivity;
- SFX enable/volume;
- music enable/volume.

## Music state transition

The routine detects one important transition:

```text
music was disabled
and
new menu state enables music
```

and remembers that and music restart is required.

It also stops the old music path when the staged state disables music.

## SFX preview

If SFX volume changes, it plays event:

`0x2E`

through the common SFX dispatcher as and settings preview.

## Commit

The modified 16-byte local block is copied back to:

`DS:4144..4153`.

Then side effects are applied:

1. mouse driver enable/disable through `6C8C`;
2. DOS audio backend reconfiguration through `C38C(mode=2)`;
3. if music was newly enabled:
   - start music track `12` through `C548`.

This gives the exact DOS Apply/Preview behavior of the hardware settings screen.

**Status: YELLOW -> GREEN.**

---

# 12. image `0xF33A..0xF43C` — `RunAndApplyCheatSettingsMenu`

Length: **259 bytes**

Major semantic correction.

The old tracker called this `EditControlBindings`, but the four rows map directly to the
four cheat globals.

Menu table:

`DS:127E`.

Marker bytes:

```text
0x1F -> DS:4150  Omniscient
0x20 -> DS:4151  Omnipotent
0x21 -> DS:4153  Omnificent
0x22 -> DS:4152  Omnifarious
```

The unusual order is real:

- marker `0x21` maps to `4153`;
- marker `0x22` maps to `4152`.

## Stage values

Before showing the menu, the routine copies current cheat bytes into each row'with
`value +2`.

It displays configuration PCX/resource:

`11`

and runs the interactive menu.

Only result:

`0x15`

commits.

## Commit values

The four menu values are copied back into:

```text
DS:4150
DS:4151
DS:4153
DS:4152
```

## Registered/full gate

After commit it calls:

`BsfDispatch(1)`.

This is the already closed registered/full test.

### Registered/full

If the result is non-NULL:

- call `9792 = ApplyEnabledCheatEffects`.

### Shareware/unavailable

If the result is NULL:

1. clear all four cheat bytes;
2. display/read the fixed cheat-unavailable prompt through `D9B0`.

This is the exact DOS implementation of the rule that cheat modes are gated by the
registered/full version.

Return:

```text
1 = menu accepted/committed
0 = cancelled
```

**Status: old mislabeled YELLOW -> GREEN.**

---

# 13. Byte-map impact

New continuous GREEN span:

`0xE9DC .. 0xF43D`

Total: **2,658 bytes**

| Image range | Bytes | Role |
|---|---:|---|
| `E9DC–EB42` | 359 | 18-byte menu-item renderer |
| `EB44–EBD4` | 145 | selection movement |
| `EBD6–EDA1` | 460 | generic interactive-menu engine |
| `EDA2–EE62` | 193 | elevator/floor chooser |
| `EE64–EF05` | 162 | stair-direction chooser |
| `EF06–F03E` | 313 | dynamic wall/variant chooser |
| `F040–F0A8` | 105 | single contextual choice |
| `F0AA–F113` | 106 | key-requirement prompt/check |
| `F114–F14E` | 59 | card-gated remote-control action |
| `F150–F1F1` | 162 | hardware settings menu |
| `F1F2–F338` | 327 | apply/preview hardware settings |
| `F33A–F43C` | 259 | cheat settings + registration gate |

Executable routine content: **2,650 bytes**.

Inter-function alignment NOPs:

```text
EB43
EBD5
EE63
F03F
F0A9
F14F
F339
F43D
```

Total: **8 bytes**.

Internal NOPs inside branch-heavy menu functions remain part of their executable
function ranges.

---

# 14. Important semantic corrections

## `F33A`

Replace:

`EditControlBindings`

with:

`RunAndApplyCheatSettingsMenu`.

The raw globals are unambiguous:

```text
4150 Omniscient
4151 Omnipotent
4152 Omnifarious
4153 Omnificent
```

and the registered/full validation is explicitly `BsfDispatch(1)`.

## `EBD6`

The signed type-3 value format is now exact:

```text
sign      = enabled/disabled
abs(value)= magnitude
Left/Right= ±5
clamp     = 0..100
Enter     = negate value
```

This directly explains the hardware menu staging logic.

## `F114`

This is not and generic flagged control action.
It explicitly tests the player'with ID-card bit and routes either to the remote
door/cannon controller or and missing-card message.

---

# 15. Cumulative closure

Pass 18 cumulative since the pass-5 baseline:

`36,842 bytes`

Pass 19 adds:

`2,658 bytes`

New cumulative total:

**39,500 bytes**

of formerly RED/ORANGE/YELLOW DOS V2.0 byte-map territory explicitly promoted to
GREEN during passes 6–19.

---

# 16. Next target

Continue at:

`0xF43E`

The next band contains the main options/save/load menu flow:

- `F43E` options/config menu loop;
- `F494` 10-slot save selector;
- `F5D6` 10-slot load selector;
- `F6BA` confirm/save;
- `F726` confirm/load;
- `F7BE` choose main-menu variant from gameplay state;
- `F89A/F926` slot availability selection;
- `F9D0` weapon-jammed feedback;
- `F9DC` in-game/main menu command dispatcher.

Most of these already have strong hard-closure cross-version matches, with the next pass
should close the complete save/load + top-level menu region with high confidence.