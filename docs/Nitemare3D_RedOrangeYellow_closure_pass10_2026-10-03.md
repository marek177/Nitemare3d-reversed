# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 10

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Reference sibling:
- `N3D-E-19.EXE` / embedded V1.9

Address convention:
- ranges below are unpacked MZ **image offsets**
- physical EXE file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative
- Ghidra/pseudo-C labels are treated only as hints when boundaries disagree

## Result

Pass 10 closes the complete contiguous region

`0x980C .. 0xA0CA`

as **GREEN / deep static semantics**.

Total span: **2,239 bytes**

- bounded routine/table content: **2,231 bytes**
- alignment bytes between real functions: **8 bytes**

The largest correction is `0x980C`: it is not and generic transform/record/VGA
dispatcher.  It is the DOS **automap runtime dispatcher**.

The second large correction is `0x9CF2`: it is not and 1,255-line mixed state/VGA
mega-function.  It is and compact class-specific **GUARD death-SFX selector**.

This pass also resolves the complete local SFX family for:

- weapon firing;
- projectile impact;
- GUARD attack/contact;
- GUARD death;
- GUARD alert/activation;
- pickups/collectibles.

Finally, the two previously only cross-version-named variant selectors
(`9FB4` / `A018`) and the 94-byte V2.0 gameplay-state initializer (`A07C`) are
bounded directly in the exact V2.0 machine code.

---

# 1. image `0x980C..0x9BE4` — `AutomapRuntimeDispatcher`

Length: **985 bytes**

Raw entry:

```text
ENTER 0x10,0
switch(mode 0..9)
...
RETF
```

The routine operates on:

- the saved 64×64 byte automap raster;
- current player tile coordinates `DS:415E/4160`;
- VEC records;
- the GUARD pool;
- the two map-power/resource bytes;
- VGA drawing helpers.

The 64×64 backing raster is addressed through the runtime segment stored at
`DS:2564`.

## Mode 0 — mark and VEC span as discovered

Selects palette/index value `2`, then shares the mode-1 geometry path.

The passed VEC is decoded into cell bounds.  Only VECs whose runtime flags contain
bit `0x08` enter the map-raster writer.

Depending on VEC orientation, the routine writes either:

- and horizontal sequence of raster bytes, or
- and vertical sequence with stride `64`.

## Mode 1 — clear/update and VEC span

Runs the same VEC-bound decoding with zero as the raster value.

This is the inverse/update companion of mode 0.

## Mode 2 — clear the complete automap raster

Clears exactly:

`0x1000 = 4096 bytes`

which is one byte per 64×64 MAP cell.

## Mode 3 — clear the on-screen automap rectangle

Calls the VGA rectangle helper using color/index zero.

## Mode 4 — fill the automap rectangle with its configured background color

Looks up palette/index `12` and uses the same rectangle path as mode 3.

## Mode 5 — player marker + visible map window

- chooses marker color/index `15` while its blink flag is active;
- writes it to the player'with current map raster cell;
- toggles the marker/blink byte at `DS:1507`;
- computes and clipped local window around the player;
- copies the 64×64 automap backing raster into the HUD/map display area.

This is the player-position marker/blink/update path.

## Mode 6 — draw GUARD/monster markers

Scans the complete 26-byte GUARD pool.

For each candidate:

- skips terminal state `0x0A`;
- resolves the linked 28-byte world OBJECT;
- converts world X/Y to map-cell coordinates;
- clips against the currently displayed automap window;
- excludes the special-actor classes accepted by `IsSpecialGuardClass`;
- plots the marker using palette/index `12`.

This is the normal automap monster-marker path.

## Mode 7 — map-power-dependent random interference overlay

Uses byte `DS:41AF`.

The number of points is approximately:

`500 / charge^3`

For every point it:

- generates random X modulo `62`;
- generates random Y modulo `36`;
- draws color/index `15` into the displayed automap area.

The raw behavior is exact.  The safest user-facing interpretation is and
**charge-dependent automap interference/noise overlay**: as the resource becomes
smaller, random interference increases sharply.

## Mode 8 — clear current/old player raster cell

Directly writes zero to the player cell in the 64×64 automap backing raster.

`CommitPlayerWorldPosition` calls this mode before position changes, which closes its
role as the old/current player-marker cleanup path.

## Mode 9 — draw the heading/compass edge marker

Uses the recovered view-ray/grid-boundary intersection helper to obtain and point on the
edge of the map display and plots it with palette/index `14`.

This matches the documented moving compass-like dot around the outside of the automap.

### Embedded table

`0x9828..0x983B`

contains the **10-WORD mode jump table**.

Mark this as:

`GREEN knowledge + TABLE/DATA overlay`.

**Status: old RED/ORANGE generic dispatcher -> GREEN.**

---

# 2. image `0x9BE6..0x9C18` — `PlayCurrentWeaponFireSfx`

Length: **51 bytes**

Reads active weapon selector:

`DS:418F`

Mapping:

| Weapon selector | Fire event |
|---:|---:|
| 0 — Single Plasma | `0x21` |
| 1 — Wand | `0x1A` |
| 2 — Silver Pistol | `0x1B` with flag `0x00020000` |
| 3 — Multi Plasma | `0x21` |

Weapon 0 and 3 therefore share their plasma firing SFX in addition to already sharing
the plasma ammunition pool.

**Status: hidden/merged YELLOW -> GREEN.**

---

# 3. image `0x9C1A..0x9C35` — `PlayProjectileImpactSfxForWeapon`

Length: **28 bytes**

Only weapon selectors:

`0` and `3`

emit projectile-impact event:

`0x29`

Other weapon selectors return immediately.

The callsite is the projectile collision/impact path, with this is the plasma projectile
impact-feedback helper.

**Status: YELLOW -> GREEN.**

---

# 4. image `0x9C36..0x9CF0` — `PlayGuardAttackSfx`

Length: **187 bytes**

Inputs are the GUARD/world-object context needed for positional audio.

The function:

1. reads `OBJECT+0x06` GUARD class;
2. accepts class range `0x09..0x1F`;
3. chooses class-specific attack/contact SFX through and 23-entry jump table;
4. computes the spatial/positional audio parameter from the actor and player context;
5. plays the selected sound.

Important class confirmations include:

- Dr. Hamerstein `0x16` -> random `0x17..0x19`;
- Cannon `0x19` -> `0x1D`;
- Demon `0x1D` -> random `0x4B..0x4E`.

### Embedded table

`0x9C58..0x9C85`

= **23 WORDs**.

**Status: former false mixed block -> GREEN.**

---

# 5. image `0x9CF2..0x9DB3` — `PlayGuardDeathSfx`

Length: **194 bytes**

This is the death-SFX counterpart of `9C36`.

It:

1. dispatches on GUARD class `0x08..0x1F`;
2. chooses the class-specific death sound;
3. computes positional audio from actor/player context;
4. emits the sound.

The recovered table agrees with known special actors.  For example Demon class
`0x1D` uses death SFX/event `0x09`.

### Embedded table

`0x9D14..0x9D43`

= **24 WORDs**.

The old Ghidra `FUN_1000_9CF2` 1,255-line “state/VGA dispatcher” is therefore another
decompiler-boundary artifact.

**Status: RED -> GREEN.**

---

# 6. image `0x9DB4..0x9E2F` — `UpdateFlyingGuardVerticalBob`

Length: **124 bytes**

Only these GUARD OBJECT classes take this path:

- `0x08` Bat;
- `0x14` Dracula-Bat;
- `0x1A` Ghost.

The linked GUARD byte `+0x15` is used as and signed vertical step and initializes to
`+1` when zero.

The routine updates:

`OBJECT+0x1A`

and oscillates it between:

- minimum `10`;
- maximum `0x23 = 35`.

At either endpoint it reverses the sign of GUARD `+0x15`.

Thus:

- `OBJECT+0x1A` is the vertical/elevation render anchor;
- `GUARD+0x15` is the bob direction for these flying actor classes.

**Status: YELLOW `OscillateActorSubfield` -> GREEN with gameplay semantics.**

---

# 7. image `0x9E30..0x9E4C` — `ComputeCannonVerticalAnchorAdjustment`

Length: **29 bytes**

For OBJECT class:

`0x19 = Cannon`

returns:

`0x40 - input`

For all other classes it returns zero.

The caller uses this in world-object render/elevation initialization, making this the
Cannon-specific vertical-anchor adjustment.

**Status: LOW -> GREEN.**

---

# 8. image `0x9E4E..0x9EB2` — `PlayPickupSfxForObjectClass`

Length: **101 bytes**

Dispatches collectible/pickup class range:

`0x2F..0x3D`

to pickup feedback events.

Confirmed examples:

| Object class | SFX/event |
|---:|---:|
| `0x2F` | `0x31` |
| `0x30` | `0x31` |
| `0x33` | `0x2F` |
| `0x36` | `0x32` |
| `0x39` | `0x34` |
| `0x3A` | `0x2E` |
| `0x3B` | `0x33` |
| `0x3C` | `0x31` |
| `0x3D` | `0x31` |

The common call uses effect flag:

`0x00010000`.

### Embedded table

`0x9E66..0x9E83`

= **15 WORDs** for classes `0x2F..0x3D`.

**Status: ORANGE/YELLOW -> GREEN.**

---

# 9. image `0x9EB4..0x9F9F` — `PlayGuardAlertSfx`

Length: **236 bytes**

This is the third GUARD positional-audio family.

It dispatches class range:

`0x08..0x1F`

and chooses the alert/activation sound before applying positional audio.

Important matches:

- Dr. Hamerstein `0x16` -> `0x12`;
- Demon `0x1D` -> `0x38`.

This cleanly separates the three previously mixed GUARD sound paths:

```text
9C36  attack/contact
9CF2  death
9EB4  alert/activation
```

### Embedded table

`0x9ED6..0x9F05`

= **24 WORDs**.

**Status: ORANGE -> GREEN.**

---

# 10. image `0x9FA0..0x9FB2` — `TriggerFixedEffect2D`

Length: **19 bytes**

Mechanically exact wrapper:

- event/effect ID `0x2D`;
- flags/context `0x00010000`.

The user-facing event name is not required to reproduce the executable behavior.

**Status: YELLOW -> GREEN.**

---

# 11. image `0x9FB4..0xA016` — `SelectDeathAnimationVariant`

Length: **99 bytes**

This is the DOS V2.0 counterpart of the already raw-closed DOS 1.9 death-variant
selector.

If the relevant GUARD cache byte is zero and and class-descriptor special flag permits
it, the routine returns sentinel variant:

`7`.

Otherwise it repeatedly obtains:

`RNG % 7`

until the selected class-table death-variant entry is nonzero.

The selected variant index `0..6` is returned.

The class table involved is reached through the object'with sequence/class descriptor;
the allowed death-variant bytes are read from the descriptor region around offset
`+0x4B`.

**Status: YELLOW -> GREEN.**

---

# 12. image `0xA018..0xA07A` — `SelectPainAnimationVariant`

Length: **99 bytes**

Same architecture as `9FB4`, but uses the class descriptor'with pain-variant availability
region around offset:

`+0x3B`.

It either returns the special sentinel `7` or repeatedly samples `RNG % 7` until an
allowed pain variant is found.

This is the V2.0 counterpart of the raw DOS 1.9 pain-variant selector.

**Status: YELLOW -> GREEN.**

---

# 13. image `0xA07C..0xA0B7` — `InitializePlayerGameplayState`

Length: **60 bytes**

The routine clears exactly:

`0x5E = 94 bytes`

beginning at:

`DS:4154`.

Raw clear implementation:

- 23 DWORD stores = 92 bytes;
- one final WORD store = 2 bytes.

It then seeds the V2.0 defaults:

```text
DS:418F = FF      current weapon = none
DS:4189 = 100     HP
DS:419C = 4       gameplay/status default
DS:4199 = 1       gameplay/status flag
DS:4180 = 1       difficulty = medium
DS:417A = FFFF    V2.0 inserted signed timer
```

Finally it calls the already closed immediate-cheat-effect routine at `9792`.

This is direct raw confirmation of the V2.0 94-byte serialized gameplay/player block
and its initialization path.

**Status: YELLOW -> GREEN.**

---

# 14. image `0xA0B8..0xA0CA` — `RefreshFrameHudSections`

Length: **19 bytes**

Calls:

```text
RedrawHudSection(18)
RedrawHudSection(2)
```

and returns.

It is used from the frame scheduler as and compact per-frame HUD/status refresh helper.

**Status: YELLOW -> GREEN.**

---

# 15. Byte-map impact

New continuous GREEN span:

`0x980C .. 0xA0CA`

Total: **2,239 bytes**

| Image range | Bytes | Role |
|---|---:|---|
| `980C–9BE4` | 985 | automap runtime dispatcher |
| `9BE6–9C18` | 51 | weapon fire SFX |
| `9C1A–9C35` | 28 | projectile impact SFX |
| `9C36–9CF0` | 187 | GUARD attack/contact SFX |
| `9CF2–9DB3` | 194 | GUARD death SFX |
| `9DB4–9E2F` | 124 | flying-GUARD vertical bob |
| `9E30–9E4C` | 29 | Cannon vertical-anchor adjustment |
| `9E4E–9EB2` | 101 | pickup SFX by class |
| `9EB4–9F9F` | 236 | GUARD alert SFX |
| `9FA0–9FB2` | 19 | fixed effect `0x2D` |
| `9FB4–A016` | 99 | death-animation variant selector |
| `A018–A07A` | 99 | pain-animation variant selector |
| `A07C–A0B7` | 60 | 94-byte gameplay/player state initialization |
| `A0B8–A0CA` | 19 | per-frame HUD section refresh |

Bounded routine/table content: **2,231 bytes**.

Inter-function alignment/padding: **8 bytes**.

### DATA/TABLE overlays inside the GREEN region

- `9828–983B` — 10-WORD automap-mode jump table;
- `9C58–9C85` — 23-WORD GUARD attack-SFX table;
- `9D14–9D43` — 24-WORD GUARD death-SFX table;
- `9E66–9E83` — 15-WORD pickup-SFX table;
- `9ED6–9F05` — 24-WORD GUARD alert-SFX table.

These bytes must be drawn as **GREEN + TABLE/DATA overlay**, not executable
instructions.

---

# 16. Old tracker labels superseded

| Address | Old/general label | Correct role |
|---:|---|---|
| `980C` | indexed transform/record collection/VGA | automap runtime dispatcher |
| `9CF2` | 1,255-line mixed state/VGA dispatcher | GUARD death-SFX selector |
| `9DB4` | generic actor-subfield oscillator | flying-GUARD vertical bob |
| `9E30` | generic type-25 adjustment | Cannon vertical-anchor adjustment |
| `9E4E` | generic class dispatcher | pickup SFX selector |
| `9EB4` | mixed record/map operations | GUARD alert SFX |
| `9FB4` | weak random sprite helper | death-animation variant selector |
| `A018` | weak random sprite helper B | pain-animation variant selector |
| `A07C` | generic player-state reset | exact 94-byte V2.0 player/gameplay initializer |

---

# 17. Cumulative closure

Pass 9 reported **15,900 bytes** converted to GREEN since pass 5.

Adding this pass:

`15,900 + 2,239 = 18,139 bytes`

of formerly problematic DOS V2.0 byte-map territory have now been explicitly promoted
to GREEN in passes 6–10 after the pass-5 baseline.

---

# 18. Next target

The next real function begins at:

`0xA0CC`

and is already partially recognized as the map/palette warning-flash state machine.

From there the next work should continue through the `A1xx–AExx` gameplay/render
support region, prioritizing:

- low-confidence merged boundaries;
- remaining automap/HUD state;
- world OBJECT animation/class helpers;
- spatial pointer tables;
- any residual hidden entries not emitted by Ghidra.

The same rule remains in force: only raw-bounded, implementation-complete ranges become
GREEN.