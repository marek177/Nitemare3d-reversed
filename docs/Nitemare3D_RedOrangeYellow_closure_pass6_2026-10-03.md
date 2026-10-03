# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 6

Date: 2026-10-03

Primary binary: `N3D-E-20(3).EXE`

- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`
- MZ header: `0x200`
- ranges below are unpacked MZ image offsets
- physical file offset = image offset + `0x200`

## Result

Pass 6 continues directly from pass 5 at image `0x6636`.

The complete contiguous region

`0x6636 .. 0x70D5`

is now bounded into real routines from raw 16-bit code and can be marked
**GREEN / deep static semantics**.

Total span: **2,720 bytes**.

- bounded real routines: **2,714 bytes**
- alignment NOP bytes between entries: **6 bytes**

This pass also corrects several old tracker identities.  Most importantly:

- `6636/676E/6824` are spatial-index maintenance, not projection;
- `688C/6914` are player-position commit/movement wrappers, not renderer collection;
- `696C` is and gameplay/event guard-selection path, not and sprite renderer;
- `6A70` is player damage/death handling, not HUD drawing;
- `6D04` is the DOS DEMO record/replay state machine, not and UI/settings loader;
- `6B00` is the custom keyboard IRQ1 handler.

Runtime behavioral parity remains and separate overlay.

---

## 1. image `0x6636..0x676C` — `AdjustVecSpatialCursorsXY`

Maintains four global cursors into sorted VEC/boundary pointer tables.

Inputs: proposed/current world X and Y.

For X:

- compares the new X with player world X `DS:4162`;
- moves cursor pairs `DS:416A/416C` forward or backward;
- compares against record coordinate `+0x0C`;
- bounds each cursor by the corresponding list count.

For Y:

- compares against player world Y `DS:4164`;
- adjusts `DS:4166/4168`;
- compares record coordinate `+0x0E`.

The function is an incremental lower-bound/bracketing maintenance routine for
spatially sorted geometry lists.

Old label `BuildViewTransform` was incorrect.

**Status: YELLOW -> GREEN.**

---

## 2. image `0x676E..0x6823` — `AdjustObjectSpatialCursorsXY`

Maintains the two player-relative cursors:

- `DS:416E` for X;
- `DS:4170` for Y.

The pointer tables contain far pointers to world OBJECT records.  The function moves
the indices until:

- OBJECT `+0x10` brackets the new player X;
- OBJECT `+0x12` brackets the new player Y.

The list count is bounded by the active sorted-object count.

Old label `ProjectWorldPoint` was incorrect.

**Status: YELLOW -> GREEN.**

---

## 3. image `0x6824..0x688B` — `AdjustObjectCursorsForMovementSpan`

Uses and proposed rectangle/span and the player'with current position to compensate
`416E/4170` when movement crosses an interval boundary.

For each axis:

- if the current player coordinate lies strictly within the supplied movement span,
  decrement or increment the corresponding sorted-object cursor according to the
  direction of crossing.

This keeps the incremental spatial indices coherent before/after position changes.

Old label `ClipProjectedPoint` was incorrect.

**Status: YELLOW -> GREEN.**

---

## 4. image `0x688C..0x6912` — `CommitPlayerWorldPosition`

This is the authoritative player-position commit helper.

Flow:

1. run the player/location side-effect helper with value `8`;
2. update VEC/boundary cursors through `0x6636`;
3. update OBJECT spatial cursors through `0x676E`;
4. store world coordinates:
   - `DS:4162 = playerWorldX`
   - `DS:4164 = playerWorldY`;
5. convert both to 64-unit cells (`>>6`);
6. when cell changed, store:
   - `DS:415E = playerCellX`
   - `DS:4160 = playerCellY`;
7. run the cell-change/marker helper;
8. rebuild the player'with MAP far pointer:
   - offset `(cellY*64 + cellX)*2 + 0x373E`
   - segment `0x21FD`;
9. query the cell'with marker/area selector and, when valid, store it at `DS:4188`.

Old label `TransformAndClipObject` was incorrect.

**Status: YELLOW -> GREEN.**

---

## 5. image `0x6914..0x6941` — `ApplyPlayerMovement`

If the movement-disable/state byte `DS:4154` is nonzero, returns immediately.

Otherwise:

1. call the already closed movement/collision core `0x6488`;
2. receive candidate world X/Y;
3. commit them through `CommitPlayerWorldPosition`.

This is the small public wrapper around player movement.

Old label `PrepareVisibleObject` was incorrect.

**Status: YELLOW -> GREEN.**

---

## 6. image `0x6942..0x696A` — `RebuildPlayerSpatialCursors`

Preserves current player X/Y, then temporarily zeros:

- player world X/Y;
- the four VEC/boundary cursors;
- the two object spatial cursors.

It then calls `CommitPlayerWorldPosition` with the saved coordinates.

This forces all incremental spatial-index state to be rebuilt consistently around the
current player position.

**Status: previously weakly named support block -> GREEN.**

---

## 7. image `0x696C..0x6A6E` — `ProcessTargetedGuardEvent`

This is and gameplay/event selection path, not world-sprite rendering.

The routine is gated by global event/state bytes around `418F..419A`.

One active branch:

1. requires an event-readiness predicate;
2. scans all GUARD records;
3. accepts only records whose 32-bit render/aim stamp `GUARD+0x02..05`
   equals the current generation `DS:4540`;
4. excludes terminal/death states `0x09`, `0x0A`, and state `0`;
5. resolves each GUARD'with linked world OBJECT;
6. computes cell deltas relative to the player;
7. runs the bounded line/visibility test;
8. on an accepted target, invokes the GUARD hit/effect path;
9. after selection, invokes area/event helpers and sets completion byte `DS:419A=1`.

This ties together the previously recovered fresh-render target stamp and the
player/guard event path.

Old label `RenderWorldObjects` was incorrect.

**Status: YELLOW -> GREEN.**

---

## 8. image `0x6A70..0x6AFE` — `ApplyDamageToPlayer`

The old tracker classified this as HUD/weapon rendering.  Raw code is an actual
player-damage/death routine.

Flow:

1. call and damage-amount helper using the supplied source/context;
2. if returned damage is nonzero, set player damage-indicator/timer
   `DS:417A = 3`;
3. if the Omnipotent/damage-suppression byte `DS:4151` is set, skip HP loss;
4. if global game state is already `2`, skip HP loss;
5. compare damage with player HP `DS:4189`.

Non-lethal:

`playerHP -= damage`

Lethal:

- `DS:4189 = 0`;
- game state `DS:3CD4 = 2`;
- transition/dirty byte `DS:3CD1 = 1`;
- save the attacking/linked entity index into `DS:4186`;
- invoke death-side-effect helpers;
- start the death feedback/sound path.

Finally it runs the status/HUD refresh helper.

**Status: ORANGE/weak -> GREEN.**

---

## 9. image `0x6B00..0x6C33` — `KeyboardIrq1Handler`

This is the custom DOS keyboard interrupt handler.

Raw behavior:

- saves general registers plus DS/ES;
- loads the game'with data segment;
- reads keyboard controller port `0x60`;
- separates make/break using bit `0x80`;
- masks to the scan code;
- updates the two-byte game input mask at `DS:3F50/3F51`.

Direct scan-code mapping in this handler includes:

- `01h` Escape;
- `1Dh` Ctrl;
- `2Ah` left Shift;
- `36h` right Shift;
- `38h` Alt;
- `39h` Space;
- `48h/4Bh/4Dh/50h` arrow keys.

The resulting primary mask matches the known layout:

- Escape `0x01`;
- Up `0x02`;
- Down `0x04`;
- Left `0x08`;
- Right `0x10`;
- right Shift `0x20`;
- left Shift `0x40`;
- Ctrl `0x80`.

The second input byte tracks Alt/Space bits.

The handler:

1. chains to the previous INT 9 handler through stored far pointer `DS:3F52`;
2. optionally drains pending input when and transition flag is set;
3. in the checked DEMO/input state can force the game-state word back to zero;
4. restores registers and exits with `IRET`.

**Status: formerly fragmented platform/input MEDIUM -> GREEN.**

---

## 10. image `0x6C34..0x6C8B` — `InstallOrRestoreKeyboardIrq1`

Parameter-controlled setup/teardown of the custom keyboard handler.

Mode 0:

- if not installed, calls DOS get-vector for interrupt `09h`;
- stores the previous vector in `DS:3F52/3F54`;
- installs handler offset `0x6B00`;
- marks installed byte `DS:0B3E = 1`.

Mode 1:

- restores the saved vector;
- clears installed byte.

The far runtime wrappers map directly to DOS `INT 21h AH=35h` (get vector) and
`AH=25h` (set vector).

**Status: YELLOW -> GREEN.**

---

## 11. image `0x6C8C..0x6CCF` — `EnableOrDisableMouseInput`

Mode 0:

- lazily queries/initializes the mouse driver;
- records availability in `DS:414C`;
- marks the subsystem active at `DS:0B3F`.

Mode 1:

- invokes the driver shutdown/reset path when active;
- clears both availability and active flags.

Other parameter values have no local action.

**Status: YELLOW -> GREEN.**

---

## 12. image `0x6CD0..0x6CE1` — `BiosEnhancedKeyAvailable`

Calls the DOS runtime BIOS-keyboard wrapper with service `0x11`.

The underlying helper executes BIOS `INT 16h`; service `11h` is the enhanced-keyboard
"check keystroke available" path.

The routine converts the helper'with result to and clean boolean.

**Status: YELLOW -> GREEN.**

---

## 13. image `0x6CE2..0x6D02` — `DrainKeyboardQueueAndClearMask`

While an enhanced keystroke is available:

- calls BIOS keyboard service `0x10` to consume it;
- repeats until queue empty.

Then clears the primary game-input mask `DS:3F50`.

This is the exact queue-drain helper called by keyboard/input transitions.

**Status: YELLOW -> GREEN.**

---

## 14. image `0x6D04..0x6E87` — `ProcessDemoRecordReplay`

Major correction: this is **not** and settings/UI asset state machine.

It is the DOS DEMO state machine driven by `DS:3CD6`.

### State 1 — start recording

- create/open the current DEMO file;
- write three 16-bit header words from `455C/455E/4560`;
- transition to state `2`.

### State 2 — record

- poll live keyboard event;
- compare event + input mask with the previous pair;
- when they change:
  - event WORD -> `34BE`;
  - input mask WORD -> `34C0`;
  - current generation DWORD `4540` -> `34C2`;
  - write exactly 8 bytes;
- cache the last event/mask.

### State 3 — start playback

- open DEMO for reading;
- read three 16-bit header words;
- read the first 8-byte event record;
- transition to state `4`.

### State 4 — playback

Record format:

- `+0` WORD event code;
- `+2` WORD input mask;
- `+4` DWORD generation/timestamp.

When the stored generation is due:

- copy record event into the return path;
- copy record mask to `DS:3F50`;
- read the next 8-byte record.

Live keyboard availability can return Escape (`0x1B`) to abort playback.

The read-result for the next 8-byte record is not locally used as an EOF state change.

### State 5 — close

- close the current DEMO handle.

**Status: old YELLOW/misidentified `ManageInputSettingsFileState` -> GREEN.**

---

## 15. image `0x6E88..0x6EBD` — `PollLiveOrDemoInputEvent`

If DEMO mode is active while game state is the relevant running mode, delegates to
`ProcessDemoRecordReplay`.

Otherwise:

- checks enhanced keyboard availability;
- consumes live key events through BIOS service `0x10`;
- returns the most recent event code.

**Status: YELLOW -> GREEN.**

---

## 16. image `0x6EBE..0x7099` — `ReadAndTranslateUserInput`

High-level DOS input translator.

It combines:

- live/DEMO keyboard events;
- mouse-driver position/buttons when enabled;
- joystick/controller input when enabled;
- edge-triggered button latches;
- movement thresholding/scaling;
- conversion to game/menu event codes.

Observed returned codes include normal keyboard codes plus synthesized:

- Enter-like `0x0D`;
- Escape-like `0x1B`;
- directional codes `0x48/0x50` from axis threshold paths.

Two event codes `0x3C/0x3D` toggle runtime options at `DS:414D/414E` and invoke the
associated feedback/device helper.

The exact user-facing label of every event code is secondary; the mechanical input
translation is bounded.

**Status: YELLOW -> GREEN.**

---

## 17. image `0x709A..0x70B7` — `ScaleMouseControlDelta`

Computes:

`scaled = (CONFIG mouse-control byte DS:4148 * input) / 50`

and clamps the result to at most `2 * limit`.

**Status: YELLOW -> GREEN.**

---

## 18. image `0x70B8..0x70D5` — `ScaleJoystickControlDelta`

Computes:

`scaled = (CONFIG joystick-control byte DS:4149 * input) / 200`

and clamps the result to at most `2 * limit`.

**Status: YELLOW -> GREEN.**

---

# 19. Byte-map impact

Continuous closed span:

`0x6636 .. 0x70D5`

| Image range | Bytes | Role |
|---|---:|---|
| `6636–676C` | 311 | VEC/boundary spatial cursors |
| `676E–6823` | 182 | OBJECT spatial cursors |
| `6824–688B` | 104 | movement-span cursor correction |
| `688C–6912` | 135 | player-position commit |
| `6914–6941` | 46 | player movement wrapper |
| `6942–696A` | 41 | rebuild spatial cursors |
| `696C–6A6E` | 259 | targeted GUARD/event selection |
| `6A70–6AFE` | 143 | player damage/death |
| `6B00–6C33` | 308 | keyboard IRQ1 handler |
| `6C34–6C8B` | 88 | install/restore INT 9 |
| `6C8C–6CCF` | 68 | mouse subsystem enable/disable |
| `6CD0–6CE1` | 18 | BIOS enhanced-key availability |
| `6CE2–6D02` | 33 | keyboard queue drain |
| `6D04–6E87` | 388 | DOS DEMO record/replay state machine |
| `6E88–6EBD` | 54 | live/DEMO event poll |
| `6EBE–7099` | 476 | high-level input translator |
| `709A–70B7` | 30 | mouse-control scaling |
| `70B8–70D5` | 30 | joystick-control scaling |

Bounded routine content: **2,714 bytes**.
Alignment NOPs: **6 bytes**.

### Major stale-label corrections

- `6636`: not BuildViewTransform -> spatial VEC cursors;
- `676E`: not ProjectWorldPoint -> OBJECT spatial cursors;
- `6824`: not ClipProjectedPoint -> cursor/span correction;
- `688C`: not TransformAndClipObject -> player-position commit;
- `6914`: not PrepareVisibleObject -> player movement wrapper;
- `696C`: not RenderWorldObjects -> targeted gameplay/GUARD event;
- `6A70`: not RenderHudAndWeapon -> player damage/death;
- `6D04`: not UI/settings loader -> DOS DEMO record/replay.

---

# 20. Next target

Continue at `0x70D6`.

The old pseudo-C body at `70D6` is and known giant merged-boundary artifact.  Prior
cross-build work already proves that the real major routine is the active
gameplay-input/player-action handler, with and fixed spacing to the next major entry.

Next closure pass should:

1. bound `70D6` from raw machine code using the clean DOS V1.2 sibling;
2. split/remove interior fake Ghidra entries;
3. bind FIRE / USE / strafe / movement / turn edges to their already known helpers;
4. continue into the following renderer/resource/projectile blocks;
5. promote only the verified raw ranges to GREEN.