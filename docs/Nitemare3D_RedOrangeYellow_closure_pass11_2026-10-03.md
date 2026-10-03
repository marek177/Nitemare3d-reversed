# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 11

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Reference sibling:
- `N3D-E-19.EXE` / embedded V1.9

Address convention:
- all ranges are unpacked MZ image offsets
- physical file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative
- pseudo-C names are ignored when they contradict raw boundaries

## Result

Pass 11 closes the complete contiguous range

`0xA0CC .. 0xA981`

as **GREEN / deep static semantics**.

Total span: **2,230 bytes**

- bounded routine/table content: **2,226 bytes**
- inter-function alignment bytes: **4 bytes**

This region is mostly automap/HUD power state, environmental hazards, explicit
level-script triggers, SPECIAL1 behavior, Pentagram/Penelope/Hamerstein scripting and
the beginning of the Episode-2 end-of-stage timed sequence.

The important improvement is that several routines absent from the Ghidra function
inventory are now real bounded entries rather than unexplained bytes.

---

# 1. image `0xA0CC..0xA198` — `TickLightningPaletteFlash`

This is the DOS palette-flash / thunder-style state machine.

It is disabled for episode 2.  In episode 3 it runs only on level 10; episode 1 uses
the normal path.

State:

- countdown `DS:3634`
- phase `DS:3636`

## Initialization / reset (`param != 0`)

- countdown = `0x50`
- phase = `0`
- writes black RGB values to VGA DAC index `0xEB`
- writes black RGB values to the second palette index stored in `DS:D2F7`

## Update (`param == 0`)

The countdown is decremented and transition happens when the old value reaches zero.

### Dark -> bright

- phase = `1`
- countdown = `3`
- both selected VGA DAC entries are written as white (`FF,FF,FF`)

### Bright -> dark

- phase = `0`
- countdown = `(RNG % 240) + 160`
- both DAC entries return to black
- fixed effect/event `0x42` is emitted

This is the previously recovered random palette-flash consumer.  The exact artistic
asset illuminated by the two palette entries is presentation-level, but the executable
state machine is fully bounded.

**Status: YELLOW -> GREEN.**

---

# 2. image `0xA19A..0xA235` — `TickAutomapPowerDrain`

This routine drains the two map-power resources while their runtime modes are active.

If the Omniscient cheat `DS:4150` is enabled, no power is consumed.

The paired resources are:

- `DS:41AF` — Magic Eye charge
- `DS:41AE` — Crystal Ball charge

Active-state bytes:

- `DS:4196` — Magic Eye/map mode active
- `DS:4197` — Crystal Ball/monster-map mode active

## Magic Eye drain

When active and:

`param & 0x0F == 0`

decrement `41AF`.

If it reaches zero:

- clear `4196`
- clear charge
- call automap mode `3`

If value changed, redraw HUD section `20`.

## Crystal Ball drain

When active and:

`param & 0x07 == 0`

decrement `41AE`.

If it reaches zero:

- clear `4197`
- clear charge
- call automap mode `3`

If value changed, redraw HUD section `19`.

The relative cadence is therefore encoded directly in the mask tests.

**Status: YELLOW -> GREEN.**

---

# 3. image `0xA236..0xA2C1` — `UpdateAutomapDisplayAndDamageIndicator`

This is and real function entry missing from the stale Ghidra register.

It coordinates the V2.0 damage-indicator timer and active automap layers.

## Damage-indicator timer

`DS:417A` is the V2.0-only signed damage indicator timer.

When it is nonnegative:

1. decrement it;
2. when the new value becomes negative, call automap/display mode `3`;
3. otherwise call automap/display mode `4`.

The exact screen appearance of modes `3/4` is presentation state; the timer ownership
and dispatch are exact.

## Active map layers

If Magic Eye mode `4196` is active:

- call automap mode `5` for player/raster display.

If Crystal Ball mode `4197` is active:

- if Magic Eye is inactive, clear/setup through mode `3`;
- when charge/state conditions permit, call automap mode `6` to draw GUARD markers.

Regardless of those active modes, the routine then runs:

- automap mode `9` — heading/compass edge marker.

When Magic Eye is active and its charge is low (`<= 15`), it additionally calls:

- automap mode `7` — random interference/noise overlay.

This closes the previously separated pieces into one per-update automap presentation
controller.

**Status: hidden RED/YELLOW entry -> GREEN.**

---

# 4. image `0xA2C2..0xA2E3` — `ToggleMagicEyeMapMode`

AND hidden 34-byte entry.

If Magic Eye charge `DS:41AF` is nonzero:

- XOR active flag `DS:4196` with `1`;
- when switched off, call automap mode `3`;
- redraw HUD section `20`.

If charge is zero, no toggle occurs.

This is the direct DOS map-toggle state path.

**Status: hidden entry -> GREEN.**

---

# 5. image `0xA2E4..0xA305` — `ToggleCrystalBallMonsterMapMode`

The companion hidden 34-byte entry.

If Crystal Ball charge `DS:41AE` is nonzero:

- XOR active flag `DS:4197` with `1`;
- when switched off, call automap mode `3`;
- redraw HUD section `19`.

This is the second map-mode toggle.

**Status: hidden entry -> GREEN.**

---

# 6. image `0xA306..0xA339` — `GetIndexedFourEntryFarPointer`

Mechanical helper.

It builds/uses and four-entry far-pointer table from globals around:

- `D0A`
- `D18`
- `D26`
- `D36`

and returns the indexed far pointer selected by the input.

No broader design label is required for and faithful implementation.

**Status: hidden LOW helper -> GREEN.**

---

# 7. image `0xA33A..0xA377` — `FormatAndDisplayIndexedMessage`

Mechanical message helper.

It selects one of two far pointers from globals around:

- `D46`
- `D5A`

then:

1. formats data through the game'with far formatting core using format/resource data near
   `1508`;
2. stores the formatted text in and local buffer of roughly `0x48` bytes;
3. sends that result to the message/text display helper.

The exact narrative use depends on the caller; the dataflow/ABI is bounded.

**Status: hidden LOW helper -> GREEN.**

---

# 8. image `0xA378..0xA423` — `UpdateNearbySpecialWallHudState`

This is the former `UpdateNearbyTriggerCellMode`, now tied to the exact runtime record
layout.

It only runs when Magic Eye charge `DS:41AF` is nonzero.

The routine scans the special-wall record array:

- base `0x34F6`
- stride `0x0E`
- count from the corresponding runtime count word

It accepts records whose state/type word `+0x0C == 1`.

For each accepted record it compares the record'with MAP-cell far pointer at `+8/+0A`
against the player MAP pointer and checks four direct neighbors:

- `+2`
- `-2`
- `+0x80`
- `-0x80`

If and matching adjacent record is found, result becomes `1`.

When this boolean differs from `DS:3CD2`:

- store the new value;
- redraw HUD section `0x15` (21).

This is and proximity-driven HUD state associated with the special-wall runtime, not and
generic renderer operation.

**Status: YELLOW -> GREEN.**

---

# 9. image `0xA424..0xA4A1` — `UpdateCellDependentHudParameters`

Initializes display globals `DS:3CD8/3CDA`.

When global mode `DS:3CD6 == 0`, both begin at zero.  Otherwise the routine copies
defaults from `1378/137A`.

It then derives the current/target MAP cell from player direction state and inspects
the second MAP byte.

If the corresponding object class resolves to:

`0x27 = TRUNK`

it looks up the associated runtime state record.

For TRUNK record states `2..5`, it loads and state-dependent 32-bit parameter pair from
table `0x0E16` into `3CD8/3CDA`.

This is the HUD/context display side of TRUNK state, separate from the actual open and
reward handler closed in pass 9.

**Status: YELLOW -> GREEN.**

---

# 10. image `0xA4A2..0xA4AA` — `UpdateContextSensitiveHudState`

Tiny hidden wrapper:

1. call `UpdateNearbySpecialWallHudState`;
2. call `UpdateCellDependentHudParameters`;
3. return.

**Status: hidden entry -> GREEN.**

---

# 11. image `0xA4AC..0xA53C` — `ApplyCausticCellDamage`

This closes and previously generic "marker hazard" label.

The function returns immediately under Omnipotent (`DS:4151`).

It inspects the player'with current MAP cell and maps the cell'with object ID through the
object-class table.  Damage applies only when:

`object class == 0x07`

which the game data identifies as the CAUSTIC fire family.

It caches the base object ID for class `0x07`, computes the class-relative variant and
uses that to index and per-variant damage table near `1516`.

## Non-lethal

`HP -= damage`

## Lethal

- `HP = 0`
- game state `DS:3CD4 = 3`
- transition/dirty flag `DS:3CD1 = 1`
- trigger player-death feedback/event

The routine finishes by redrawing HUD health section `5`.

This is the exact DOS environmental-fire hazard path.

**Status: ORANGE/YELLOW -> GREEN.**

---

# 12. image `0xA53E..0xA567` — `TriggerE1M7LightsOut`

One-shot story trigger.

When latch `DS:430A == 0`:

- emit effect/event `0x42`;
- set `430A = 1`;
- set dark/shade flag `430E = 1`;
- call the display-mode/shade application helper;
- run the supporting transition helper;
- display the Episode-1 level-7 lights-out message.

This is the trigger behind the storm/fused-lights event.

**Status: hidden story entry -> GREEN.**

---

# 13. image `0xA568..0xA5B6` — `TriggerE1M10HamersteinMonologue`

One-shot Episode-1 level-10 story trigger.

When not previously activated:

- play event `0x12`;
- set event latch `430A = 1`;
- set event byte `430C = 1`;
- set player/control state byte at the gameplay block start;
- clear Omnipotent `4151`;
- queue/display the three Hamerstein dialogue messages.

This is the explicit raw DOS equivalent of the previously mapped E1M10 trigger-G
story sequence.

**Status: hidden story entry -> GREEN.**

---

# 14. image `0xA5B8..0xA5D1` — `TriggerE1M10PenelopeReveal`

One-shot path:

- set latch `430B`;
- display the Penelope/Hamerstein reveal text.

This is the corresponding E1M10 trigger-H path.

**Status: hidden story entry -> GREEN.**

---

# 15. image `0xA5D2..0xA5EB` — `TriggerE3M10PenelopeMessage`

One-shot path using `430A`.

Displays the E3M10 message corresponding to:

`Look! It's Penelope! Where's Dr. Hamerstein?`

**Status: hidden story entry -> GREEN.**

---

# 16. image `0xA5EC..0xA605` — `TriggerE2M10PlasmaCoreMessage`

One-shot path using `430A`.

Displays the Episode-2 level-10 plasma-core warning:

`QUICK! Destroy the plasma core!`

**Status: hidden story entry -> GREEN.**

---

# 17. image `0xA606..0xA61F` — `TriggerE3M1PlasmaCoreAftermath`

One-shot Episode-3 level-1 path.

Displays the long aftermath message about the defunct plasma core, jammed automatic
doors and scattered possessions.

**Status: hidden story entry -> GREEN.**

---

# 18. image `0xA620..0xA6E1` — `HandleTrigger1Trigger2Event`

This is the central DOS TRIGGER1/TRIGGER2 story dispatcher.

It reads:

- episode `DS:626A`
- level selector `DS:626C`
- trigger type derived from the current map/wall record

and routes to episode/level-specific handlers.

Recovered cases include:

## Episode 1

- level 7: TRIGGER1 -> `TriggerE1M7LightsOut`
- level 9:
  - TRIGGER1 enables the weapon-jam latch
  - TRIGGER2 clears the weapon-jam latch
  - both use event `0x44`
- level 10:
  - TRIGGER1 -> Hamerstein monologue
  - TRIGGER2 -> Penelope reveal

## Episode 2

- level 10 TRIGGER1 -> plasma-core warning

## Episode 3

- level 1 TRIGGER1 -> plasma-core aftermath
- level 10 TRIGGER1 -> Penelope/Hamerstein message

This proves directly that TRIGGER1/TRIGGER2 are **content-script markers**, not generic
remote-door links.

**Status: ORANGE/YELLOW -> GREEN.**

---

# 19. image `0xA6E2..0xA75D` — `HandleEpisode1Special1Use`

This routine is limited to episode 1 and handles two known SPECIAL1 contexts.

## E1M2 — morphing chalkboard

The routine resolves the selected runtime sequence record, writes:

`0x96`

to its sequence/cache timing field and emits event `0x44`.

This is the previously documented morphing chalkboard behavior.

## E1M7 — fuse box

When the storm/lights-out event latch is in the repairable state:

- emit success event `0x32`;
- advance event latch from `1` to `2`;
- clear dark/shade flag `430E`;
- reapply normal display/shade settings;
- show the successful power-restoration message.

Otherwise it displays the already-fixed message.

**Status: YELLOW -> GREEN.**

---

# 20. image `0xA75E..0xA8E1` — `HandlePentagramSpecialActorInteraction`

This is and large scripted interaction helper involving the four Pentagram progress bits
and the two special actor classes:

- `0x15` Penelope
- `0x16` Dr. Hamerstein

The DOS Pentagram/progress byte is:

`DS:41B1`

with the required complete mask:

`0x0F`.

The function first copies and base text into and local `0x102`-byte buffer.

For every missing bit 0..3 in `41B1`, it appends one corresponding requirement/help
string from and four-entry string set.

## Class `0x16` — Dr. Hamerstein

Takes and dedicated fixed-message path.

## Class `0x15` — Penelope

When all four Pentagram bits are present:

- emit event `0x44`;
- change the relevant UI/device state;
- invoke the special class/script helper.

When the mask is incomplete:

- emit event `0x42`;
- display the constructed message describing the missing Pentagram requirements.

The exact original high-level function name is not encoded, but the script contract is
now sufficient for and faithful implementation.

**Status: ORANGE/LOW scripted block -> GREEN.**

---

# 21. image `0xA8E2..0xA981` — `AdvanceTimedEpisode2EndEvent`

This is the timed world-stage routine already weakly recognized by the old register.

It:

1. invokes and state/display helper;
2. increments `DS:151C`;
3. only performs the main event every 20 calls;
4. updates/commits player position/state through the known helper family;
5. derives and wait deadline from table data plus global clock;
6. waits/polls until the deadline;
7. emits/displays two event/message resources;
8. sets game state `DS:3CD4 = 3`;
9. invokes the high-level transition/statistics path;
10. returns success.

The immediately following entry `A982` gates this function to Episode 2, level index
9 (E2M10), with this routine is the timed end-stage sequence for that context.

`A982` itself is intentionally left for the next pass because pass 11 ends at `A981`.

**Status: YELLOW -> GREEN.**

---

# 22. Byte-map impact

New continuous GREEN span:

`0xA0CC .. 0xA981`

Total: **2,230 bytes**

| Image range | Bytes | Role |
|---|---:|---|
| `A0CC–A198` | 205 | lightning/thunder palette flash |
| `A19A–A235` | 156 | Magic Eye / Crystal Ball charge drain |
| `A236–A2C1` | 140 | automap display + damage indicator |
| `A2C2–A2E3` | 34 | Magic Eye map toggle |
| `A2E4–A305` | 34 | Crystal Ball monster-map toggle |
| `A306–A339` | 52 | four-entry far-pointer accessor |
| `A33A–A377` | 62 | indexed formatted-message helper |
| `A378–A423` | 172 | nearby special-wall HUD state |
| `A424–A4A1` | 126 | cell/TRUNK-dependent HUD parameters |
| `A4A2–A4AA` | 9 | context-HUD wrapper |
| `A4AC–A53C` | 145 | CAUSTIC/fire cell damage |
| `A53E–A567` | 42 | E1M7 lights-out trigger |
| `A568–A5B6` | 79 | E1M10 Hamerstein monologue |
| `A5B8–A5D1` | 26 | E1M10 Penelope reveal |
| `A5D2–A5EB` | 26 | E3M10 Penelope message |
| `A5EC–A605` | 26 | E2M10 plasma-core warning |
| `A606–A61F` | 26 | E3M1 plasma-core aftermath |
| `A620–A6E1` | 194 | TRIGGER1/TRIGGER2 dispatcher |
| `A6E2–A75D` | 124 | Episode-1 SPECIAL1 handler |
| `A75E–A8E1` | 388 | Pentagram / special-actor interaction |
| `A8E2–A981` | 160 | timed E2M10 end-stage event |

Bounded routine/table content: **2,226 bytes**.

Inter-function alignment bytes: **4 bytes**.

---

# 23. Important map-color changes

Former YELLOW/ORANGE/RED areas promoted to GREEN include:

- automap charge/toggle/update family;
- environmental CAUSTIC damage;
- all checked DOS TRIGGER1/TRIGGER2 story branches;
- E1 SPECIAL1 chalkboard/fuse-box behavior;
- Penelope/Hamerstein Pentagram script;
- timed E2M10 stage event.

The hidden entries at `A236`, `A2C2`, `A2E4`, `A306`, `A33A`, `A4A2`,
`A53E`, `A568`, `A5B8`, `A5D2`, `A5EC`, `A606`, and `A620` must be added to any
future corrected function inventory.

---

# 24. Cumulative closure

Pass 10 cumulative since the pass-5 baseline:

`18,139 bytes`

Pass 11 adds:

`2,230 bytes`

New cumulative total:

**20,369 bytes**

of formerly problematic DOS V2.0 byte-map territory explicitly promoted to GREEN
during passes 6–11.

---

# 25. Next target

Continue at:

`0xA982`

The immediate next neighborhood contains:

- the E2M10 gate wrapper;
- additional level/event helpers;
- world-object category bitsets;
- display-mode setup;
- stage-background MIDI/music selection;
- the weak `AD9A` mixed entry;
- `AEAC/AEC2/AF10` low-confidence helpers;
- `AF5E/AFFE` sorted OBJECT spatial pointer construction/maintenance.

This region is attractive because much of it is already structurally stable across
builds, while `AD9A` and `AEAC` still need raw-boundary correction before they can be
safely made GREEN.