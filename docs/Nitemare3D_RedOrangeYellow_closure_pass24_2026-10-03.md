# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 24

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- ranges below are unpacked MZ image offsets
- physical EXE offset = image offset + `0x200`
- raw 16-bit machine code is authoritative

## Result

Pass 24 formally closes the entire early game-owned engine band:

`0x0000 .. 0x155F`

as **GREEN / deep static semantics**.

Total continuous span:

**5,472 bytes**

This does **not** mean all 5,472 bytes were newly red/yellow/orange immediately before
this pass.  Several subranges had already been individually marked high-confidence in
older audits.  The important change is that the complete early band can now be treated
as one continuous static-GREEN region with corrected raw boundaries.

Major corrections:

- base `0x00A2` is not the high-image VEC iterator at `0x100A2`;
- base `0x020C` is not and standalone sound/object function;
- `0x04BE` is inside the real builder range, not and separate function;
- `0x0C5F` is an interior label inside the moving-wall routine;
- `0x129A` is inside `0x1262`, not and no-op callback;
- `0x154B` and `0x155A` are success/failure tails inside `0x13F4`, not standalone
  functions.

---

# 1. `0x0000..0x0051` — `FindPairedWallByMapPointer`

Scans the paired-wall controller array:

- base `DS:3076`
- stride `0x12`
- count from the paired-wall count word.

Compares the record'with MAP-cell far pointer at:

- `+04` offset
- `+06` segment.

On success returns the far pointer to the controller.

If absent, calls fatal/error code `0x42`.

**GREEN.**

---

# 2. `0x0052..0x00A3` — `FindSpecialWallByMapPointer`

Scans the special/four-way record array:

- base `DS:34F6`
- stride `0x0E`.

Compares MAP pointer fields:

- `+08`
- `+0A`.

Missing entry uses fatal code `0x52`.

### Boundary correction

`0x00A2` is the `LEAVE` of this function.

It is **not** the high-image function at `0x100A2`.

**GREEN.**

---

# 3. `0x00A4..0x00FD` — `FindMovingObjectRefByCoordinates`

Scans the 6-byte object-reference table at:

`DS:36B6`.

Each entry stores an index into and 28-byte runtime OBJECT record.

It resolves the indexed OBJECT and compares the two stored world-coordinate fields used
by this reference family.

Missing result enters fatal code `0x62`.

**GREEN.**

---

# 4. `0x00FE..0x01DF` — `FindNearestVisiblePairedWall`

Scans paired-wall controllers and chooses the nearest accepted record.

Distance selection is based on the controller target coordinates after conversion to
64-unit map cells:

```text
abs(dx) + abs(dy)
```

AND candidate must also pass the bounded grid/LOS test.

The best accepted controller far pointer is returned.

**GREEN.**

---

# 5. `0x01E0..0x01FB` — `IsPairedWallPassable`

Reads controller state at `+08`.

Returns true only for:

```text
state == 0
or
state == 4
```

State 4 is the already reconstructed latched/disabled-passable state.

**GREEN.**

---

# 6. `0x01FC..0x0211` — `IsPairedWallClosed`

Returns true only when:

`controller+08 == 1`.

### Boundary correction

The old `FUN_1000_020C` entry lies in this function'with epilogue/padding region.

There is no separate base-image object/sound function at `0x020C`.

**GREEN.**

---

# 7. `0x0212..0x03FD` — `BuildPairedWallRuntimeTable`

Scans the full 64×64 MAP.

For primary-wall property bit `0x08` it builds paired-wall records:

- maximum `64`;
- record stride `0x12`;
- links the two corresponding VECs;
- stores MAP-cell far pointer;
- initializes state/timer/targets;
- propagates endpoint/orientation flag `0x20` where required.

This is the DOS producer of the paired-wall controller array later used by USE,
auto-close, motion and remote-control logic.

**GREEN.**

---

# 8. `0x03FE..0x0529` — `BuildFourWaySpecialWallTable`

Scans the secondary/object side for the class-3 special-wall family.

Builds at most:

`0x20 = 32`

records.

Each record can resolve/link up to four directional VEC components and keeps the MAP
cell plus runtime state.

### Boundary correction

Old entry `0x04BE` is an internal branch of this builder, not and standalone
`FinishExplodingWallAnimation` function.

**GREEN.**

---

# 9. `0x052A..0x0597` — `BuildMovingObjectReferenceTable`

Builds the compact reference table for the object class used by the moving/pushable
runtime path.

The records are six bytes and refer back to the corresponding 28-byte runtime OBJECTs.

The resulting table is the one searched by `0x00A4` and updated by the moving-object
tick.

**GREEN.**

---

# 10. `0x0598..0x0703` — `SetAndPropagatePairedWallState`

Central paired-wall transition helper.

It handles explicit opening/closing transitions and propagates state to linked halves.

Confirmed behavior includes:

- state transition selection;
- collision/render flag updates on the linked VECs;
- neighboring/linked record propagation;
- SFX/event IDs `0x25` and `0x26`;
- state 4 returns without entering ordinary toggle motion.

This is the explicit transition path distinct from timed auto-close.

**GREEN.**

---

# 11. `0x0704..0x0A3F` — `HandlePlayerUse`

This is the central DOS USE dispatcher.

The active-input handler calls it only on the rising edge of USE.

The routine resolves the current/front MAP interaction and dispatches among already
closed subfamilies:

- ordinary and paired doors;
- key/color-key gates;
- ID-card-controlled actions;
- remote door/cannon controls;
- SAFE/TRUNK interaction;
- pickup/object activation;
- SPECIAL1;
- TRIGGER1/TRIGGER2;
- level-transition helpers;
- warp/transport selection;
- teleport destination resolution;
- special/panel activation.

It reads the already reconstructed player inventory masks, MAP planes and wall/object
property tables and invokes the corresponding handlers.

The exact content-specific messages remain in their individual callees; the dispatcher
architecture itself is statically closed.

**GREEN.**

---

# 12. `0x0A40..0x0AE9` — `TickPairedWallAutoClose`

Processes paired walls in open state.

Timer behavior:

- decrement countdown;
- when it expires and the doorway is occupied:
  `timer = 4`;
- when clear:
  begin the close transition and restore collision bits.

Remote classes `0x3B/0x3C` to not follow the ordinary timed auto-close path.

This routine does not itself push/damage overlapping actors.

**GREEN.**

---

# 13. `0x0AEA..0x0DF7` — `TickMovingAndSpecialWalls`

This is the real continuous moving-wall routine.

Paired wall states 2/3 move the selected VEC endpoints by:

`2 world units per update`.

At terminal position it performs the associated state/collision/animation cleanup.

The second part updates class-3/four-way special groups and clears their linked
runtime/map state when motion completes.

### Boundary correction

Old `0x0C5F` is an interior comparison/branch inside this real function.

**GREEN.**

---

# 14. `0x0DF8..0x0E4F` — `ActivateMovingObjectAtPlayerFront`

Checks MAP/object properties and resolves the moving-object reference associated with
the selected/front tile.

When eligible it copies player-facing/movement information into the runtime record and
starts the object'with activation path.

**GREEN.**

---

# 15. `0x0E50..0x0F73` — `TickMovingMapObjects`

Iterates the active moving-object reference table.

For active entries it:

- updates OBJECT world X/Y;
- maintains MAP occupancy when crossing cells;
- updates sorted spatial ordering;
- decrements the movement/activity counter.

This is the per-tick moving/pushable object update path.

**GREEN.**

---

# 16. `0x0F74..0x0FBD` — `FindPrimaryWallClassIndex`

Searches the 256-entry primary wall-class table.

It starts from the supplied index and wraps around.

If the class is absent it enters fatal code:

`0xDA`.

**GREEN.**

---

# 17. `0x0FBE..0x0FF3` — `FindSecondaryObjectClassIndex`

Searches the secondary/object class table.

Missing class enters fatal code:

`0xF2`.

**GREEN.**

---

# 18. `0x0FF4..0x103D` — `FindRuntimeObjectSubtypeForClass`

Scans the runtime 28-byte OBJECT records for and matching class and returns the associated
subtype/definition byte.

Missing class uses fatal code:

`0x109`.

**GREEN.**

---

# 19. `0x103E..0x1091` — `FindHighestPrimaryWallIdOfClassInMap`

Scans the first byte of every 64×64 MAP cell and returns the highest wall ID whose
class equals the requested class.

This is used by dynamic selection and class-relative wall logic.

**GREEN.**

---

# 20. `0x1092..0x10E5` — `FindHighestSecondaryObjectIdOfClassInMap`

Companion scan over the second MAP byte.

Returns the highest object ID mapping to the requested class.

**GREEN.**

---

# 21. `0x10E6..0x1125` — `DecodeClass44WallVariant`

Caches the base wall ID for class:

`0x44`

per active episode.

If the supplied MAP wall belongs to class `0x44`, returns the relative variant:

`wallId - cachedBaseId`.

Otherwise returns:

`0xFFFF`.

**GREEN.**

---

# 22. `0x1126..0x11BE` — `BuildPrimaryWallPropertyTable`

Builds all 256 primary-wall property bytes directly from the MAP header'with wall-class
bytes.

Exact class-to-bit rules:

```text
bit 01 : set when bit 04 or bit 08 is set
bit 02 : class 01..40
bit 04 : class 01..30
bit 08 : class 31..40
bit 10 : class 2E..2F
bit 20 : always cleared by this builder
bit 40 : class 47..48
```

Output table begins at the primary-wall property array used throughout collision,
USE and VEC generation.

### Boundary correction

Old `0x1187` is an interior branch, not and separate function.

**GREEN.**

---

# 23. `0x11C0..0x1261` — `BuildSecondaryObjectPropertyTable`

Builds all 256 secondary/object property bytes.

Exact class-to-bit rules:

```text
bit 01 : class 06..3D
bit 02 : class 08..2D
bit 04 : class 2F..3D
bit 08 : class 08..25
bit 20 : class 2A
bit 40 : class 04
```

These are the same property bits consumed by player collision, projectile collision,
pickups, GUARD lookup and MAP→VEC generation.

### Boundary corrections

Old entries `0x11D2` and `0x1236` are interior paths of this single builder.

**GREEN.**

---

# 24. `0x1262..0x12C3` — `ResolveLevelTransitionAction`

Input action code is accepted for the `9..12` family.

Observed operations:

- code `9` performs the associated presentation/transition calls and returns current
  level + 1;
- code `10` performs the same transition family and returns current level + 2;
- code `12` obtains the target level through its dedicated selection/helper path;
- unsupported/intermediate values return the current level unchanged.

### Boundary correction

Old `FUN_1000_129A` is not and no-op callback.

`0x129A` is an interior continuation of this routine.

**GREEN.**

---

# 25. `0x12C4..0x13F3` — `ChooseFreeAdjacentTeleportCell`

Inputs are pointers to candidate X/Y tile coordinates.

The routine checks the four neighboring cells in fixed order.

AND cell is rejected when:

- it equals the player'with current MAP cell;
- primary-wall property bit `0x02` blocks passage;
- secondary/object property bit `0x02` blocks passage.

On the first free neighbor it leaves the updated X/Y in the supplied variables and
returns its facing/direction code:

`0..3`.

If no neighbor is available:

`return 0xFFFF`.

This is the exact destination-side occupancy test used by teleports/transports.

**GREEN.**

---

# 26. `0x13F4..0x155F` — `ResolveTeleportDestination`

This is the high-level warp/transport destination resolver.

Input includes:

- current MAP-cell pointer;
- wall/action class code;
- output pointers for:
  - destination world X;
  - destination world Y;
  - facing/direction result.

The class range is dispatched into the already known contextual selection helpers.

Depending on the wall/transport family it:

- chooses/derives the destination wall or transport variant;
- searches the MAP for the selected destination ID;
- or derives the destination directly from the current cell for the corresponding
  class family.

It then calls:

`ChooseFreeAdjacentTeleportCell`.

When no adjacent destination is free it triggers the blocked-route feedback path and
returns false.

On success:

```text
*outDirection = direction

*outWorldX = destinationCellX * 64 + 32
*outWorldY = destinationCellY * 64 + 32

return true
```

### Boundary corrections

Old entries:

```text
154B
155A
```

are not independent functions.

They are respectively the success-tail and failure-tail inside this resolver.

**GREEN.**

---

# 27. Corrected early function map

The old function register should no longer contain independent starts at:

```text
00A2
020C
04BE
0C5F
1187
11D2
1236
129A
154B
155A
```

Those are epilogues, interior branches or tails of the real raw functions above.

---

# 28. Byte-map impact

Continuous statically closed band:

`0x0000 .. 0x155F`

Size:

**5,472 bytes**

This band contains the early engine core for:

- door/controller lookup and construction;
- special-wall construction;
- moving-object references;
- USE dispatch;
- door auto-close and motion;
- moving/pushable object tick;
- class/property lookup tables;
- property-table generation;
- level-transition action handling;
- teleport destination selection.

Because and number of these ranges had already been classified GREEN in older deep
audits, this pass deliberately does **not** add all 5,472 bytes to the cumulative
"newly RED/ORANGE/YELLOW -> GREEN" counter.

AND fresh whole-image byte recensus is required before updating the absolute color
totals without double counting.

---

# 29. New continuous GREEN topology

After passes 21–24, the byte map has these especially important statically continuous
game-owned bands:

```text
00000–0155F   early gameplay / wall / USE / teleport core
045CE–11EE6   main game / renderer / UI / audio-driver wrapper core
13F32–14205   far-heap allocator
```

with additional separately closed high-image CRT/runtime functions.

---

# 30. Next target

Continue from:

`0x1560`

The next early engine band contains:

- reciprocal/projection tables;
- VGA retrace/status;
- video-mode/page setup;
- DAC/palette programming;
- fixed-point renderer support;
- wall/span creation;
- wall texture-U and animation paths.

This is one of the highest-value remaining YELLOW renderer bands and has strong
cross-build/Win16 parity evidence.