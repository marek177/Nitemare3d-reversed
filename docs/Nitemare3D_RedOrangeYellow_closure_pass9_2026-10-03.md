# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 9

Date: 2026-10-03

Primary binaries used:
- `N3D-E-20(3).EXE` — exact V2.0 distribution image used by the byte map
- `N3D_DOS_v2.0_IDA.EXE` — unpacked MZ image used to resolve far-data strings/tables

Reference executable SHA-256:
`552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- ranges below are DOS V2.0 image offsets / `1000:xxxx` family offsets
- the old Ghidra pseudo-C function boundaries are not trusted when contradicted by
  raw 16-bit control flow
- static GREEN does not claim runtime parity

## Result

Pass 9 closes the complete region:

`0x90EA .. 0x980B`

as **GREEN / deep static semantics**.

Total span: **1,826 bytes**
- real bounded routine/table content: **1,815 bytes**
- alignment NOPs: **11 bytes**

This removes the next major false-merge at `0x954A` and resolves several routines that
were previously missing from the decompiler altogether.

The major discoveries are:

1. `90EA` is and developer/debug GUARD inspector, not collision traversal.
2. `917E` is the missing SAFE/TRUNK reward dispatcher.
3. `9282` is the DOS SAFE/TRUNK interaction handler including the six-character
   combination path.
4. `9376` is the ACTIONSPOT / E1M9 Dancers script activation/restoration engine.
5. `954A` is the class/marker-driven GUARD initializer, not and 2500-line mixed
   subsystem.
6. `9646` is the remote door/cannon control handler.
7. `9792` applies the Omniscient / Omnipotent / Omnifarious cheat effects immediately.

---

# 1. image `0x90EA..0x917C` — `ShowFrontGuardDebugInfo`

The old hard-closure register only knew this as and generic map/collision traversal.
Raw code plus the actual far-data format string makes the purpose much more precise.

The function:

1. reads current player facing/octant state;
2. obtains the MAP cell immediately in front of the player;
3. checks the cell'with secondary/object property table for bit `0x08`;
4. resolves the linked GUARD/runtime record;
5. resolves its linked 28-byte OBJECT;
6. formats and diagnostic string containing:

```text
class %d, strength %d, strategy %d
state %d, nextstate %d, timer %d
octant %d, resoct %d
```

7. sends that formatted diagnostic to the game'with text/message display path.

Fields passed to the formatter include:

- linked OBJECT class;
- GUARD HP/strength;
- strategy;
- current state;
- next state;
- timer;
- facing/octant;
- the cached/result octant byte.

The active-input handler reaches this function from and special extended key/event code,
with it is best treated as and **developer/debug gameplay inspector**, not ordinary
collision logic.

**Status: ORANGE/MEDIUM generic label -> GREEN.**

---

# 2. image `0x917E..0x9238` — `ApplySafeTrunkRewardCode`

This routine was effectively missing from the stale decompiler, yet its raw body is and
clean switch over reward codes `2..11`.

The common tail refreshes HUD state and emits and reward feedback event.

## Reward code effects

### Code 2

- player HP `DS:4189 = 100`;
- score `DS:4182:4184 += 150`;
- reward feedback code `0x30`.

### Code 3

- plasma ammo `DS:418C = 100`;
- if the corresponding owned-weapon bit is set, pistol ammo `DS:418B = 100`;
- if the corresponding owned-weapon bit is set, wand ammo `DS:41B0 = 100`;
- score `+= 100`;
- reward feedback `0x30`.

### Code 4

- one magic/map charge byte `DS:41AF = 100`;
- score `+= 250`;
- reward feedback `0x30`.

### Code 5

- the companion magic/map charge byte `DS:41AE = 100`;
- score `+= 250`;
- reward feedback `0x30`.

The two charge bytes are the DOS counterparts of the Magic Eye / Crystal Ball
resource pair.

### Codes 6..9

Set one bit in:

`DS:4192`

using:

`1 << (code - 6)`

and use reward feedback `0x31`.

### Codes 10..11

Set one bit in:

`DS:4193`

using:

`1 << (code - 10)`

and use feedback `0x31`.

These bitfields are inventory/progress fields consumed by the central USE path.

### Embedded data

`0x919A..0x91AD` is and **10-WORD jump table** for codes 2..11.

**Status: previously missing RED body -> GREEN.**

---

# 3. image `0x923A..0x924A` — `TriggerEffect32`

Thin fixed event/effect wrapper:

- context/severity flag `0x00020000`;
- event/effect code `0x32`.

This is the success/open feedback used by the SAFE/TRUNK interaction path.

**Status: YELLOW -> GREEN.**

---

# 4. image `0x924C..0x925C` — `TriggerEffect44`

Thin fixed event/effect wrapper for code:

`0x44`

**Status: YELLOW -> GREEN.**

---

# 5. image `0x925E..0x926E` — `TriggerEffect43`

Thin fixed event/effect wrapper for code:

`0x43`

This also explains the previously opaque downstream call from object activation code.

**Status: YELLOW -> GREEN.**

---

# 6. image `0x9270..0x9280` — `TriggerEffect42`

Thin fixed event/effect wrapper for code:

`0x42`

**Status: YELLOW -> GREEN.**

---

# 7. image `0x9282..0x9374` — `HandleSafeOrTrunkInteraction`

This is the common DOS runtime handler for:

- object class `0x26` SAFE;
- object class `0x27` TRUNK.

It first resolves the object'with small state record and dispatches according to state byte
`record+3`.

## SAFE combination path

For class `0x26` while unopened:

1. reads exactly six input characters;
2. derives the SAFE combination selector from the current object/map ID;
3. compares the entered text with the corresponding stored combination;
4. failure takes the wrong-combination text path;
5. success continues into the common open-state transition.

The raw data near the function contains the known combinations and messages, including:

```text
333
01532
080993
372535
I'm sorry, that is not
the correct combination.
```

The object/wall data independently labels the related wall class `0x45` as SAFESPOT.

## TRUNK path

Class `0x27` skips the combination test and enters the common content/opening path.

## Opening state

On accepted activation:

`record+3 = record+1 + 2`

then event/effect `0x32` is emitted.

## Already-open/content state

For state values above the initial prompt/opening state:

- SAFE adjusts its reward code by `+4`;
- TRUNK uses the stored state directly;
- calls `ApplySafeTrunkRewardCode`;
- returns the state record to the post-open state.

This establishes the direct bridge:

`SAFE/TRUNK -> state code -> player reward/inventory mutation`.

**Status: YELLOW/MEDIUM -> GREEN.**

---

# 8. image `0x9376..0x952C` — `SetActionSpotDancerScriptMode`

Parameter selects activation/restoration.

This is the DOS counterpart of the already recovered ACTIONSPOT / Dancers script.

## Mode 0 — activate scripted dance sequence

The routine:

1. emits event/message `0x45`;
2. invokes the associated story/script helper;
3. scans every GUARD record;
4. resolves each linked OBJECT and MAP cell;
5. selects guards whose underlying wall class is:
   `0x46 = ACTIONSPOT`;
6. clears that cell'with object byte;
7. sets GUARD state:
   `GUARD+0x0B = 0x14`;
8. saves the old OBJECT sequence selector in `GUARD+0x0C`;
9. sets timer:
   `GUARD+0x06 = 0x70`;
10. sets scripted movement component:
    `GUARD+0x13 = 3`;
11. switches OBJECT sequence/resource state into the Dancers presentation family;
12. selects class-specific dance sequence words for the supported original guard
    classes.

## Mode 1 — restore

The routine:

1. emits event/message `0x45`;
2. invokes the reset/transition helper;
3. scans GUARDs in state `0x14`;
4. clears strategy;
5. sets state `6`;
6. sets timer `1`;
7. restores the saved sequence selector;
8. rebuilds the normal class sequence pointer.

This is not and hidden boss AI path.  It is and temporary scripted actor presentation.

**Status: YELLOW -> GREEN.**

---

# 9. image `0x952E..0x9548` — `MaybeStartE1M9ActionSpotScript`

Reads:

- episode selector `DS:626A`;
- zero-based/current level selector `DS:626C`.

If:

- episode == `1`;
- `level + 1 == 9`;

it calls:

`SetActionSpotDancerScriptMode(0)`.

This is the direct DOS hook tying ACTIONSPOT to the Episode-1 level-9 event.

The routine itself does not contain and generic level loader.

**Status: YELLOW -> GREEN.**

---

# 10. image `0x954A..0x9644` — `InitializeGuardBehaviorFromClassAndMarker`

This is the second major false-merge removed by pass 9.

The old Ghidra export treated `954A` as and 2,500-line multi-subsystem dispatcher.
The raw function is only **251 bytes** and is the class/marker-specific GUARD behavior
initializer called from the already closed `6302` GUARD-slot constructor.

## Default GUARD state

Writes:

- `GUARD+0x0A strategy = 0`;
- `GUARD+0x16 perception mode = 1`;
- `GUARD+0x0B state = 7`;
- `GUARD+0x0C next_state = 2`.

## Class overrides

The inline class table covers object classes `0x08..0x21`.

The recovered class matrix matches the independently closed Win16 initializer:

- `08,09,0A,11,14,1A` -> perception mode `0`;
- `12,13` -> perception mode `0`, strategy `3`;
- `15,16` -> next state `0`;
- `19` Cannon -> strategy `4`, state `0x0E`;
- `21` Dancers -> state `0`, next state `0`;
- other classes -> default.

If the initial movement components `GUARD+0x13/+0x14` are nonzero, the common tail
forces:

`state = 8`.

## Underlying navigation marker

The routine then reads the wall class beneath the linked OBJECT.

Marker overrides:

- wall class `0x42` RETREAT -> strategy `2`;
- wall class `0x43` FLEE -> strategy `1`;
- wall class `0x46` ACTIONSPOT -> strategy `2`.

This directly binds the DOS initializer to the recovered local-navigation model.

### Embedded data

The bytes beginning around `0x9588` are the class jump table for object classes
`0x08..0x21`, not executable instructions.

**Status: huge RED false-merge -> GREEN.**

---

# 11. image `0x9646..0x9790` — `HandleRemoteDoorAndCannonControl`

This is the remote-control menu/runtime handler.

Input parameter selects and remote-control group/channel.

The routine:

1. derives the corresponding bit in global remote-door state `DS:4308`;
2. prepares and four-command menu/control table;
3. disables/enables command rows according to the current door and cannon state;
4. invokes the menu/action selector;
5. handles returned command IDs `0x1B..0x1E`.

## Commands `0x1B / 0x1C` — remote doors

Scans the remote door/state record array beginning at far arena `0x3076`.

It filters:

- object classes `0x3B..0x3C`;
- matching control-group subtype.

Depending on open/close command it accepts the corresponding wall-controller states,
marks the record for transition and calls the central paired-wall state helper.

It then updates the selected bit in `DS:4308`.

## Commands `0x1D / 0x1E` — remote cannon state

These commands toggle:

`DS:4309`

which is the remote cannon enable/disable control consumed by the Cannon GUARD cycle.

This matches the already reconstructed user-facing command family:

- open remote doors;
- close remote doors;
- enable remote cannons;
- disable remote cannons.

**Status: YELLOW/MEDIUM -> GREEN.**

---

# 12. image `0x9792..0x980B` — `ApplyEnabledCheatEffects`

This routine gives direct DOS V2.0 semantics for three of the four CONFIG cheat flags.

The fourth cheat, Omnificent, is read dynamically by GUARD AI rather than being and
resource-grant path here.

## `DS:4150` — Omniscient

When enabled:

- Magic Eye charge -> `100`;
- Crystal Ball charge -> `100`.

This matches the documented "all seeing" behavior: infinite mapping/monster-map power.

## `DS:4151` — Omnipotent

When enabled:

- pistol ammo -> `100`;
- plasma ammo -> `100`;
- wand ammo -> `100`;
- player HP -> `100`;
- owned-weapon mask -> `0x0F`;
- if no weapon is selected, requests weapon selector `0`.

The independent damage path already uses this same flag to suppress player damage.

Thus the DOS code directly matches the documented "all powerful" cheat.

## `DS:4152` — Omnifarious

When enabled it fills the broad collectible/inventory state:

- key/card/progress bitfields;
- owned weapons;
- all three ammo pools;
- player HP;
- both magic charges;
- an additional inventory/status counter set to `99`.

If no weapon is active it requests selector `0`.

This matches the documented "all things" cheat that grants collectible access items,
weapons, keys/cards and pentagram/progress items.

## Omnificent

The fourth CONFIG cheat is not granted here; its effect is consumed by GUARD
perception/AI.

**Status: former MEDIUM cheat uncertainty -> GREEN for immediate resource effects.**

---

# 13. Byte-map impact

New continuous GREEN span:

`0x90EA .. 0x980B`

Total: **1,826 bytes**

| Image range | Bytes | Role |
|---|---:|---|
| `90EA–917C` | 147 | front-cell GUARD developer/debug inspector |
| `917E–9238` | 187 | SAFE/TRUNK reward dispatcher |
| `923A–924A` | 17 | fixed effect 0x32 |
| `924C–925C` | 17 | fixed effect 0x44 |
| `925E–926E` | 17 | fixed effect 0x43 |
| `9270–9280` | 17 | fixed effect 0x42 |
| `9282–9374` | 243 | SAFE/TRUNK combination/open/content handler |
| `9376–952C` | 439 | ACTIONSPOT/Dancers activation + restore |
| `952E–9548` | 27 | E1M9 ACTIONSPOT hook |
| `954A–9644` | 251 | class/marker GUARD initializer |
| `9646–9790` | 331 | remote door/cannon controller |
| `9792–980B` | 122 | immediate cheat-effect application |

Real routine/table content: **1,815 bytes**.
Alignment NOPs: **11 bytes**.

### DATA/TABLE overlays

- `919A–91AD` — 10-WORD SAFE/TRUNK reward jump table;
- `9588...` — GUARD class initialization jump table.

---

# 14. Major stale-label corrections

| Address | Old/general label | Correct role |
|---:|---|---|
| `90EA` | ResolveMapCollisionOrTraversal | front GUARD debug/status inspector |
| `917E` | not decompiled / unknown | SAFE/TRUNK reward dispatcher |
| `9282` | queued device/world event | SAFE/TRUNK runtime interaction |
| `9376` | generic marker actor conversion | ACTIONSPOT/Dancers script |
| `952E` | generic level advance | E1M9 ACTIONSPOT hook |
| `954A` | 2500-line mixed dispatcher | GUARD behavior initializer |
| `9646` | generic key/world action | remote door/cannon controller |
| `9792` | generic player reset/refill | apply Omniscient/Omnipotent/Omnifarious effects |

---

# 15. Next target

Continue at:

`0x980C`

This begins another decompiler-polluted dispatcher region.

Existing evidence suggests the next useful targets are:

- `980C` spatial/transform/record collection operations;
- `9CF2` another false merged state/VGA region;
- `9DB4` actor vertical/elevation oscillator;
- later `9E..A?` gameplay/render support.

The next pass should repeat the same process:
raw boundary -> real ABI -> constants/data tables -> cross-build semantic match ->
GREEN only when implementation semantics are bounded.