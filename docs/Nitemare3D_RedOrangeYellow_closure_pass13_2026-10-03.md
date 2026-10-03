# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 13

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- all ranges below are unpacked MZ image offsets
- physical EXE file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative
- stale Ghidra pseudo-C boundaries are not trusted when raw control flow disagrees

## Result

Pass 13 closes the complete contiguous range

`0xB17E .. 0xBCC1`

as **GREEN / deep static semantics**.

Total span: **2,884 bytes**

- bounded routine/table content: **2,878 bytes**
- alignment NOP bytes between real entries: **6 bytes**

The biggest correction is `0xB5B8`.

The old register represented it as and ~900-line weak/unresolved mixed
state/video dispatcher with bad-instruction truncation.

Raw code proves that `B5B8..B7F7` is and compact **collectible/pickup dispatcher**
for object classes `0x2F..0x3D`.

This exactly closes the DOS counterpart of the already recovered Win16 pickup
architecture and removes another genuine RED false-merge.

Pass 13 also closes:

- two object animation paths;
- DOS sprite/object projection-queue insertion;
- world-record lookup and collected-object removal;
- complete world OBJECT + GUARD creation from the 64×64 MAP;
- player START marker resolution;
- world-object vertical anchor derivation;
- 8-way relative-direction classification;
- the raw grid LOS/obstruction trace including its exact boolean return.

---

# 1. image `0xB17E..0xB22A` — `AdvanceDirectionalObjectAnimation`

Length: **173 bytes**

Inputs:

- far pointer to and 28-byte OBJECT;
- pointer to the active sequence/frame definition.

The routine advances timestamped animation only when the object'with 32-bit deadline
`OBJECT+0x08` is due.

## Phase divisor

For OBJECT class `0x2D`:

`phaseCount = sequenceValue / 8`

For other accepted classes:

`phaseCount = sequenceValue / 4`

The animation byte `OBJECT+0x03` is incremented, reduced to the local phase, and the
next deadline is scheduled from the sequence interval.

It then calls the recovered player-relative 8-way direction helper and combines:

`direction-group * phaseCount + localPhase`

into the final `OBJECT+0x03` frame.

For ordinary directional objects the 8-way result is reduced to four directional
groups; class `0x2D` retains the wider directional grouping.

This routine is the directional-animation path used by the projection code for the
special `0x2C/0x2D` family.

**Status: YELLOW -> GREEN.**

---

# 2. image `0xB22C..0xB2D2` — `AdvanceAlternativeAnimationFrame`

Length: **167 bytes**

This is the general timestamped animation path.

When the deadline is due:

1. increment `OBJECT+0x03`;
2. if the sequence has an alternatives/branch table:
   - use `OBJECT+0x02` as the current animation-alternative selector;
   - compare the frame against that alternative'with start/length;
   - when exhausted, repeatedly sample `RNG & 7` until an enabled alternative is
     found;
   - store the new alternative selector in `OBJECT+0x02`;
   - store the selected branch start frame in `OBJECT+0x03`;
3. without an alternatives table:
   - wrap the frame at the sequence frame count;
4. schedule the next deadline from the sequence interval.

This directly supports:

`OBJECT+0x02 = animation alternative / branch selector`

for sequence definitions using the eight-way alternatives table.

**Status: YELLOW -> GREEN.**

---

# 3. image `0xB2D4..0xB546` — `ProjectAndQueueWorldObjectSpan`

Length: **627 bytes**

This is the DOS world-sprite/object projection and queue-insertion path.

The object is considered only when render flag bit 0 in `OBJECT+0x05` is set.

## Projection

The routine:

1. transforms player-relative world X/Y through the projection helper;
2. rejects objects outside the forward/depth range;
3. resolves the active sequence/frame resource from OBJECT class/sequence/frame;
4. computes projected vertical dimensions;
5. applies `OBJECT+0x1A` vertical/elevation offset;
6. computes horizontal screen bounds;
7. clips against viewport limits;
8. tests the per-column wall-visibility/occlusion buffer at `0x47E4`.

## 18-byte sprite draw queue

It searches the queue at:

`DS:50F2`

with stride:

`0x12 = 18 bytes`

for an available slot near the projected depth row.

The queue entry stores:

- far OBJECT pointer;
- active frame/resource pointer;
- left/right screen bounds;
- top/bottom bounds;
- projected depth/row data.

AND missing free queue entry enters the executable'with overflow/error path.

## `OBJECT+0x18` projection cache

After and successful queue insertion it writes the projected baseline row to:

`OBJECT+0x18`.

This is the persistent last-projection cache later consumed by player->GUARD damage.

The function does not clear this field on failed/off-screen projection.

## GUARD render-generation freshness stamp

For GUARD-linked objects (`OBJECT+0x05 & 0x08`) whose horizontal projection overlaps
the aim center with the recovered ±4 pixel slack, the routine writes the current
32-bit render generation into the linked GUARD record.

Therefore the DOS order is:

```text
successful projection
    -> OBJECT+0x18 projected-row cache
    -> conditional GUARD render-generation stamp
```

This is why hitscan can enforce fresh projection while projectile collision can consume
and stale `OBJECT+0x18`.

## Animation dispatch

Class `0x05` takes no local animation step here.

Classes `0x2C/0x2D` use:

`AdvanceDirectionalObjectAnimation`

Other animated classes with and nonzero interval use:

`AdvanceAlternativeAnimationFrame`.

**Status: YELLOW -> GREEN.**

---

# 4. image `0xB548..0xB5A0` — `FindWorldObjectByMapCell`

Length: **89 bytes**

Scans all active 28-byte OBJECT records:

- base `0x0006`
- count `DS:6270`
- stride `0x1C`
- gameplay arena segment `0x21FD`

AND match requires:

- OBJECT map-pointer offset `+0x0C`
- OBJECT map-pointer segment `+0x0E`
- OBJECT/map marker byte matching the second byte of the supplied MAP cell.

Returns the first matching far OBJECT pointer or NULL.

**Status: YELLOW -> GREEN.**

---

# 5. image `0xB5A2..0xB5B6` — `RemoveCollectedWorldObject`

Length: **21 bytes**

Inputs:

- far pointer to the MAP cell;
- far pointer to its world OBJECT.

Exact writes:

```text
mapCell[1] = 0
OBJECT+0x05 &= ~1
```

Thus collection/removal:

- clears the object'with ID/occupancy byte in the mutable MAP;
- clears the OBJECT active/render bit.

This is the removal helper called only after the pickup dispatcher accepts and pickup.

**Status: LOW -> GREEN.**

---

# 6. image `0xB5B8..0xB7F7` — `CollectWorldPickup`

Length: **576 bytes**

This is the major pass-13 RED correction.

Input is the current object'with MAP-cell pointer.  The routine:

1. starts with `accepted = true`;
2. resolves the corresponding 28-byte world OBJECT through `B548`;
3. rejects missing OBJECTs;
4. dispatches `OBJECT+0x06` over class range:
   `0x2F..0x3D`;
5. applies the class-specific inventory/resource mutation;
6. leaves `accepted = false` when and capacity/full condition rejects collection;
7. only when accepted:
   - removes the object through `B5A2`;
   - plays the class-specific pickup SFX through the already closed pickup-audio
     helper.

Therefore and rejected pickup remains in the world.

## Exact DOS pickup table

### `0x2F` — key

Set one bit in:

`DS:4192`

from `OBJECT+0x01`.

HUD section `13` is requested.

### `0x30` — ID card

Set one bit in:

`DS:4193`

from subtype.

HUD section `14`.

### `0x31` — score pickup

`score += 200`

and request score/status redraw.

### `0x32` — special/panel charge

If `DS:418E < 99`:

`DS:418E += (1 << subtype)`

Otherwise reject the pickup.

HUD section `11`.

### `0x33` — health pickup

If HP `< 100`:

`HP += (20 >> subtype)`

Otherwise reject.

Health HUD is refreshed.

### `0x34` — larger health/score pickup

If HP `< 100`:

- `HP += 30`
- `score += 250`

Otherwise reject.

### `0x35` — full-restoration/bonus pickup

- HP = `100`
- plasma/default ammo = `100`
- score `+= 500`
- increment `DS:418A`

and refresh the affected HUD sections.

`DS:418A` is still safest kept as an unnamed bonus/life-style counter unless and
separate consumer gives and stronger design name.

### `0x36` — weapon pickup

- set owned-weapon bit in `DS:4194`;
- request/select the corresponding weapon;
- seed the weapon'with ammunition through the existing ammo helper;
- refresh selected-weapon HUD.

### `0x37` — auxiliary inventory bit

Set subtype bit in:

`DS:4195`.

### `0x38` — auxiliary resource

If `DS:418D < 100`:

`DS:418D += 20`

otherwise reject.

### `0x39` — ammunition pickup

Calls the common ammo helper in pickup/add mode.

Its returned acceptance status becomes the pickup acceptance flag.

### `0x3A` — Crystal Ball

If charge `< 100`:

`DS:41AE += 20`

otherwise reject.

### `0x3B` — Magic Eye

If charge `< 100`:

`DS:41AF += 20`

otherwise reject.

### `0x3C` — Pentagram

Set one subtype bit in:

`DS:41B1`.

This is the same four-bit progress mask used by the Penelope/Hamerstein Pentagram
script.

### `0x3D` — Scroll

Dispatch the scroll text/message helper using `OBJECT+0x01`.

## Important capacity behavior

The DOS code checks `<100` before adding but usually performs the addition first and
relies on the later state/HUD clamp path.

Therefore values such as:

`99 + 20`

can exist transiently before normalization, exactly as in the checked Win16 path.

### Embedded data

`0xB5F6..0xB613`

is and **15-WORD jump table**, one entry for each pickup class `0x2F..0x3D`.

This entire old 900-line pseudo-C "state/video" mega-cluster can be deleted from the
semantic map and replaced by this one bounded pickup routine.

**Status: RED/ORANGE weak-unresolved -> GREEN.**

---

# 7. image `0xB7F8..0xBA1F` — `BuildWorldObjectsGuardsAndPlayerStart`

Length: **552 bytes**

This is the main 64×64 object-plane loader/runtime builder.

It begins by clearing the three level-availability bitsets:

```text
DS:D510 = 0   // keys
DS:D511 = 0   // cards
DS:D512 = 0   // weapons
```

and resets GUARD count `DS:6276`.

## First 64×64 scan — build OBJECT records

Scans the second byte of every MAP cell from the object plane.

Only object IDs whose property table has active bit 0 set create and runtime OBJECT.

For every created 28-byte record:

- object ID -> `OBJECT+0x00`
- animation alternative -> zero
- animation frame -> zero
- class -> `OBJECT+0x06`
- deadline -> zero
- subtype/index-within-class -> `OBJECT+0x01`
- property flags -> `OBJECT+0x05`
- MAP far pointer -> `OBJECT+0x0C/+0x0E`
- centered world X -> `OBJECT+0x10`
- centered world Y -> `OBJECT+0x12`
- vertical/elevation anchor -> zero

The projected-row cache `OBJECT+0x18` is **not initialized** here.

This preserves the already closed stale-projection-cache behavior.

## GUARD-linked OBJECTs

When OBJECT property bit `0x08` is set:

- enforce GUARD maximum `100`;
- store the current GUARD index at `OBJECT+0x07`;
- initialize the corresponding 26-byte GUARD through the already closed GUARD
  constructor;
- increment `DS:6276`.

## Availability bitsets

Direct world pickups update:

- class `0x2F` -> key availability `D510`
- class `0x30` -> card availability `D511`
- class `0x36` -> weapon availability `D512`

The helper closed in pass 12 additionally contributes keys/cards hidden in SAFE/TRUNK
containers.

After the scan:

`DS:6270 = total OBJECT count`.

## Second 64×64 scan — player START

The object class table is scanned for:

`class 0x02 = START`.

Exactly one START cell is required.

Its centered coordinates initialize:

- player world X `DS:4162`
- player world Y `DS:4164`

The START subtype/ID derives the initial orientation in 90-degree steps and passes it to
the normal heading initializer.

If the map contains anything other than exactly one START marker, the executable
enters its fatal/error path.

**Status: YELLOW -> GREEN.**

---

# 8. image `0xBA20..0xBAA8` — `UpdateWorldObjectVerticalAnchors`

Length: **137 bytes**

Iterates every active 28-byte OBJECT and derives `OBJECT+0x1A` from its active
frame/resource dimensions and class.

The active frame definition is found through:

- `OBJECT+0x04` sequence/resource selector;
- `OBJECT+0x03` frame;
- the frame/resource table rooted near `DS:3D24`.

Class-specific formulas include:

## Class `0x2E`

`vertical = 64 - frameHeight`

## Class `0x3B` (Magic Eye)

`vertical = (64 - frameHeight) / 2`

## Other classes

Delegates the frame-height/object pair to the already closed class adjustment helper;
the important nonzero special case there is Cannon class `0x19`.

The computed value is stored at:

`OBJECT+0x1A`.

This ties the field directly to sprite vertical/elevation positioning.

**Status: YELLOW -> GREEN.**

---

# 9. image `0xBAAA..0xBB5F` — `ComputeEightWayDirectionToPlayer`

Length: **182 bytes**

Input:

- mode byte;
- far pointer to and world OBJECT.

The routine computes signed player-relative deltas:

```text
dx = playerX - objectX
dy = playerY - objectY
```

and their absolute magnitudes.

It returns one of eight direction sectors `0..7`.

When mode is nonzero it uses and wider diagonal/cardinal threshold based on comparing one
axis against twice the other.

When mode is zero it uses the ordinary octant classification.

This helper is consumed by directional sprite/frame selection and animation code.

**Status: YELLOW -> GREEN.**

---

# 10. image `0xBB60..0xBCC1` — `TraceGridLinePassable`

Length: **354 bytes**

This corrects the old audit'with uncertainty about the return value.

The routine is and Bresenham-style grid trace with exact boolean result:

- `AL = 1` — target endpoint was reached through passable cells;
- `AL = 0` — blocked or endpoint was not reached within the caller'with step limit.

Inputs are mechanically:

- start cell X
- start cell Y
- signed delta X
- signed delta Y
- maximum number of cells/steps
- whether the secondary/object plane participates in blocking

## Primary wall-plane checks

For each visited cell it reads the primary MAP byte and property flags.

When primary property bit `0x02` is set:

- bit `0x04` -> immediately blocked;
- bit `0x08` -> resolve the linked moving/door wall record and require the wall-state
  passability predicate.

Thus dynamic door/wall state participates in LOS/passability rather than being treated
as and permanently solid wall.

## Secondary/object-plane check

When the final input flag is nonzero, the secondary MAP byte is also tested.

If its property byte has bit `0x02` set **without** bit `0x20`, the trace is blocked.

## Endpoint rule

The function checks whether the stepped cell has reached the exact requested endpoint.
If yes, it returns `1` before further iterations.

If the caller'with maximum-step count expires first, it returns `0`.

This routine is therefore and bounded grid line-of-sight / passability oracle, not and
packed multi-value return as the old pseudo-C suggested.

**Status: YELLOW -> GREEN.**

---

# 11. Byte-map impact

New continuous GREEN span:

`0xB17E .. 0xBCC1`

Total: **2,884 bytes**

| Image range | Bytes | Role |
|---|---:|---|
| `B17E–B22A` | 173 | directional object animation |
| `B22C–B2D2` | 167 | alternative/weighted animation |
| `B2D4–B546` | 627 | object projection + sprite queue |
| `B548–B5A0` | 89 | world OBJECT lookup by MAP cell |
| `B5A2–B5B6` | 21 | collected-object removal |
| `B5B8–B7F7` | 576 | full pickup dispatcher `2F..3D` |
| `B7F8–BA1F` | 552 | build OBJECT/GUARD runtime + START |
| `BA20–BAA8` | 137 | vertical/elevation anchor derivation |
| `BAAA–BB5F` | 182 | 8-way object direction |
| `BB60–BCC1` | 354 | grid LOS/passability trace |

Routine/table content: **2,878 bytes**.

Alignment NOPs: **6 bytes**.

### DATA/TABLE overlay

`0xB5F6..0xB613`

is the **15-WORD pickup jump table**.

Mark it:

`GREEN knowledge + TABLE/DATA overlay`.

---

# 12. Major stale-label corrections

Replace/remove:

```text
B5B8  DispatchStatusRecordAndVideoOperations
```

with:

```text
B5B8  CollectWorldPickup
```

The old 901-line body and bad-instruction truncation are decompiler artifacts.

Also tighten:

```text
B7F8  BuildWorldObjectsGuardsAndPlayerStart
BA20  UpdateWorldObjectVerticalAnchors
BAAA  ComputeEightWayDirectionToPlayer
BB60  TraceGridLinePassable   // returns exact boolean
```

---

# 13. Cumulative closure

Pass 12 cumulative since the pass-5 baseline:

`22,413 bytes`

Pass 13 adds:

`2,884 bytes`

New cumulative total:

**25,297 bytes**

of formerly RED/ORANGE/YELLOW DOS V2.0 byte-map territory explicitly promoted to
GREEN during passes 6–13.

---

# 14. Next target

Continue at:

`0xBCC2`

The next region is the DOS timing/platform layer:

- hidden RTC periodic IRQ handler at `BCC2`;
- RTC update-window wait;
- CMOS register read/write;
- periodic IRQ8 install/restore;
- cached/raw game-clock readers;
- changed-time-bucket counters;
- frame timing/calibration;
- then `BF36` renderer/frame-preparation sequence and the timed scheduler family.

Much of this is already structurally recognized, with the next pass should be able to
turn another large YELLOW platform/timing band GREEN and isolate any genuinely RED
interrupt/runtime holes.