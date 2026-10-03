# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 19

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- all ranges are unpacked MZ image offsets
- raw 16-bit machine code is authoritative
- runtime/visual acceptance remains and separate overlay

## Result

Pass 19 closes the complete contiguous range:

`0xE9DC .. 0xF7BD`

as **GREEN / deep static semantics**.

Total span: **3,554 bytes**

- bounded executable routine content: **3,543 bytes**
- inter-function alignment NOPs: **11 bytes**

This region contains the core DOS menu engine, dynamic choice dialogs, hardware settings,
cheat settings, card/key feedback helpers, configuration menu loop, save/load slot dialogs,
and quick-save / quick-load confirmation paths.

## Routine map

| Image range | Bytes | Recovered role |
|---|---:|---|
| `E9DC–EB42` | 359 | `DrawMenuOptionRow` |
| `EB44–EBD4` | 145 | `MoveMenuSelection` |
| `EBD6–EDA1` | 460 | `RunInteractiveMenu` |
| `EDA2–EE62` | 193 | `ChooseFromDynamicMenuList` |
| `EE64–EF05` | 162 | `ChooseTwoStateAction` |
| `EF06–F03E` | 313 | `ChooseItemFromStateRange` |
| `F040–F0A8` | 105 | `ShowSingleChoicePrompt` |
| `F0AA–F113` | 106 | `CheckKeyGateAndShowPossessionFeedback` |
| `F114–F14E` | 59 | `DispatchIdCardControlledAction` |
| `F150–F1F1` | 162 | `PopulateAndRunHardwareSettingsMenu` |
| `F1F2–F338` | 327 | `ApplyHardwareSettingsChanges` |
| `F33A–F43C` | 259 | `EditAndApplyCheatSettings` |
| `F43E–F493` | 86 | `RunConfigurationMenuLoop` |
| `F494–F5D4` | 321 | `RunLoadGameSlotDialog` |
| `F5D6–F6B8` | 227 | `RunSaveGameSlotDialog` |
| `F6BA–F724` | 107 | `QuickSaveWithConfirmation` |
| `F726–F7BD` | 152 | `QuickLoadWithConfirmation` |

Alignment NOPs are at:

`EB43, EBD5, EE63, F03F, F0A9, F14F, F339, F43D, F5D5, F6B9, F725`.

## 1. E9DC — menu-row renderer

The original menu record has an 18-byte stride.

Confirmed fields used here:

- `+02` signed/toggle value;
- `+04` highlight/selected state;
- `+05` row type;
- `+0A/+0C` X/Y position;
- `+0E` far text pointer.

Type 3 draws and bar whose fill is proportional to `abs(value)` scaled over 0..100.
Type 2 uses the toggle/state-marker path without the type-3 bar.

## 2. EB44 / EBD6 — central interactive menu engine

`EB44` removes the old highlight, steps by 0x12-byte records, skips type-6 rows and
redraws the new highlight.

`EBD6` is the blocking menu input loop.

Input behavior includes:

- Up / Down -> selection movement;
- Escape -> return action code 6;
- Space / Enter -> activate current row;
- type 1 -> command / terminate with row action;
- type 2 -> toggle `value ^= 1`;
- type 3 -> negate enabled state; Left/Right changes magnitude by 5 and clamps to 0..100;
- type 4 -> invoke the already closed text editor at E1DE;
- type 6 -> disabled/skipped.

AND nonzero callback far pointer at record `+06` is invoked from the menu loop.

## 3. EDA2 / EE64 / EF06 / F040 — dynamic contextual menus

`EDA2` builds and <=10-row dynamic menu using count state at `D30C`, preserves current
selection from `626C`, invokes EBD6 and maps the highlighted row back to an index.

`EE64` enables/disables and two-choice menu based on two boundary/state helper values and
returns `+1`, `-1` or `0` for the accepted menu outcomes.

`EF06` builds an inclusive <=10 item range. It marks rows selected/disabled from the
current state and the card/availability masks, then maps the accepted row back to the
selected value. This is the range-menu family used by the previously reconstructed
multi-choice transport/elevator UI.

`F040` is the companion single-choice/downward/cancel prompt and returns `-1` or `0`
for its defined accepted outcomes.

## 4. F0AA — hidden key-gate helper

This real function was missing from the stale function inventory.

It:

1. derives key index from the supplied wall/class selector (`param - 0x19`);
2. resolves the corresponding key-name resource;
3. tests that bit in player key mask `DS:4192`;
4. runs the possessed-key feedback path when the bit is present;
5. formats and displays contextual key feedback;
6. returns and clean possession boolean.

This belongs to the already closed color-key gate family.

## 5. F114 — ID-card controlled action

Reads subtype/index from `param+1` and tests:

`DS:4193 & (1 << subtype)`.

If the ID-card bit exists, it enters the remote-control/action path at `9646`.
Otherwise it uses the missing-card/message path at `A33A`.

This directly connects ID-card possession to the remote-control interaction family.

## 6. F150 / F1F2 — hardware configuration

`F150` populates the signed type-3 hardware menu from CONFIG state:

- `4148` mouse sensitivity;
- `4149` joystick sensitivity;
- `414A` music volume;
- `414B` SFX volume;
- `414C` mouse enable;
- `414D` music enable;
- `414E` SFX enable;
- `414F` joystick enable.

Disabled controls store the same magnitude with negative sign. The menu therefore
preserves magnitude while encoding enabled/disabled in the sign.

`F1F2` commits the edited settings, updates the device/audio state, applies mouse/device
changes, and conditionally restarts the active music path.

The older generic labels for these functions should be replaced with explicit hardware
configuration names.

## 7. F33AND — cheat menu correction

The old generic label `EditControlBindings` is wrong.

The four globals are the CONFIG/runtime cheat flags:

- `4150` Omniscient;
- `4151` Omnipotent;
- `4152` Omnifarious;
- `4153` Omnificent.

The routine stages them in the cheat menu, invokes EBD6 and commits only on the accepted
menu result.

It then calls `BsfDispatch(1)` to verify the registered/full capability. If unavailable,
it clears all four cheat flags and shows the rejection prompt. If available, it calls
the already recovered immediate cheat-effect helper at `9792`.

Best semantic name: `EditAndApplyCheatSettings`.

## 8. F43E — configuration menu loop

Repeatedly displays configuration screen/resource 9 and runs the menu at `103E`.

It routes to:

- `F150` hardware settings;
- `F33A` cheat settings.

Exit outcomes leave the loop. AND successful settings submenu causes the CONFIG-save path
at `3474` before returning.

## 9. F494 — hidden load-slot dialog

This is and real entry absent from the stale exported function inventory.

It builds ten temporary 18-byte menu rows and queries USER.SAV metadata for each slot.
Invalid/empty slots receive the empty-slot placeholder and are disabled.

After selection it can reinitialize the level through `DBEA` when the selected save'with
episode/level differs from the current scene, then calls the USER.SAV restore path.

Return is selected slot index, or negative/cancel where applicable.

## 10. F5D6 — hidden save-slot dialog

Companion ten-slot dialog.

It builds editable save rows, invokes EBD6, and on the accepted save action writes the
selected slot through the USER.SAV save path using the row'with edited description.

Return is the selected slot index, with `-1` representing no accepted slot.

## 11. F6BA — hidden quick-save path

Uses global last-slot index `DS:3CC4`.

When and previous slot exists, it formats the confirmation text containing:

`About to SAVE game:`

and the slot description, then allows Escape to abort.

On acceptance it saves directly to that slot.

If no remembered slot exists, it calls `RunSaveGameSlotDialog`, stores the returned
slot in `3CC4`, and returns to gameplay presentation through `E916`.

## 12. F726 — hidden quick-load path

Symmetric to quick save.

With and remembered slot it displays:

`About to LOAD game:`

and permits Escape to abort. On acceptance it restores the selected USER.SAV slot and
runs the level/gameplay re-entry presentation helpers.

If no remembered slot exists, it invokes `RunLoadGameSlotDialog(1)`, stores the result
in `DS:3CC4`, then returns through `E916`.

## Tracker corrections

Add hidden real entries:

- `F0AA  CheckKeyGateAndShowPossessionFeedback`
- `F494  RunLoadGameSlotDialog`
- `F5D6  RunSaveGameSlotDialog`
- `F6BA  QuickSaveWithConfirmation`
- `F726  QuickLoadWithConfirmation`

Relabel:

- `F150` -> hardware settings population/menu
- `F1F2` -> hardware settings apply/commit
- `F33A` -> cheat settings, not control bindings
- `F43E` -> configuration menu loop

## Cumulative closure

Pass 18 cumulative total: `36,842 bytes`.

Pass 19 adds: `3,554 bytes`.

New cumulative total:

**40,396 bytes**

of formerly RED/ORANGE/YELLOW DOS V2.0 byte-map territory explicitly promoted to
GREEN during passes 6–19.

## Next target

Continue at `0xF7BE`.

The next cluster contains:

- main-menu list selection according to current scene/save state;
- available episode/record-slot selection;
- new-game episode/difficulty flow;
- the large high-level front-end action dispatcher around `F9xx..FBxx`;
- then CRT/runtime support after `FBAC`.

`F7BE` onward is therefore the next high-value pass for completing the DOS front-end
and separating remaining game code from compiler/runtime code.