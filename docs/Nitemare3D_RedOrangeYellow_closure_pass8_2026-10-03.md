# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 8

Date: 2026-10-03

Primary binary: `N3D-E-20(3).EXE`

- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`
- MZ header: `0x200`
- ranges below are unpacked MZ image offsets
- physical file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative; stale Ghidra body boundaries are not

## Result

Pass 8 continues at `0x7F96` and closes the large region through `0x90E9`.

New continuous GREEN span:

`0x7F96 .. 0x90E9`

Total span: **4,436 bytes**

- bounded real routine/table content: **4,422 bytes**
- one-byte alignment NOPs between real entries: **14 bytes**

This pass is especially valuable because it dismantles the large false Ghidra
clusters beginning at `84FE`, `8590`, `86DC`, `87D8`, and `89A2`.
They are not giant multi-subsystem functions.  Raw assembly plus the clean DOS 1.9
siblings resolves them into ordinary combat, death, weapon, HUD, projectile and
device routines.

Together, passes 6–8 have moved another **10,932 bytes** into GREEN after pass 5.

---

# 1. image `0x7F96..0x8141` — `ResolveProjectileCellCollision`

This is the player-projectile map-cell collision and impact resolver.

Inputs include:

- target MAP-cell far pointer;
- candidate projectile world X/Y.

The function obtains property bytes for both MAP bytes and then applies the following
logic.

## Object/touch interaction

If the secondary/object property byte has bit `0x40`, the object interaction helper is
called first.  AND handled interaction immediately counts as and projectile hit.

## Ordinary wall block

Primary-wall property bit `0x04` is and projectile-blocking path.

## Explodable wall path

When the blocking wall also has bit `0x10`:

1. play event/SFX `0x29`;
2. resolve the matching wall world OBJECT from the current map coordinates;
3. accept the relevant exploding-wall source classes (`0x2E` / `0x2F`);
4. convert the runtime OBJECT to class `0x2D`;
5. select the proper initial explosion frame/sequence;
6. create an animation deadline from the active sequence definition.

Thus the projectile-wall explosion path is and real map/object state transition, not
only and visual effect.

## Dynamic wall/door path

The remaining blocking/dynamic wall branch uses the existing wall-state predicate and
returns collision when the wall is not projectile-passable.

## GUARD impact

When the object-property path indicates and linked actor:

1. resolve the GUARD from the cell;
2. resolve its linked 28-byte world OBJECT;
3. compare projectile candidate X against OBJECT X;
4. compare projectile candidate Y against OBJECT Y;
5. require both absolute differences to be `< 10` — exact tolerance `±9`;
6. call the common player-to-GUARD damage route.

There is **no render-generation freshness test** on this projectile route.

Therefore projectile damage can consume the current cached `OBJECT+0x18` value even
when it is stale.  Hitscan and projectile damage deliberately have different cache
freshness rules.

Return value:

- `1` = collision/handled impact;
- `0` = projectile may continue.

**Status: YELLOW -> GREEN.**

---

# 2. image `0x8142..0x822E` — `AdvanceProjectileTrajectoryAndCollide`

This is the per-update DDA/Bresenham projectile trajectory stepper.

Projectile slot layout used directly:

- `+00` major-axis selector;
- `+02` error accumulator;
- `+04` first error increment;
- `+06` second/error-correction increment;
- `+08` signed X step;
- `+0A` signed Y step;
- `+0C` lifecycle;
- `+0E` embedded 28-byte OBJECT.

The routine starts from embedded OBJECT X/Y and performs up to:

`DS:4560`

substeps.

At each substep it:

1. advances the selected major axis;
2. updates the error accumulator;
3. conditionally advances the secondary axis;
4. derives the visited MAP-cell pointer;
5. calls `ResolveProjectileCellCollision`.

## Collision transition

On and hit:

- projectile lifecycle `+0x0C = 2` — impact animation;
- embedded OBJECT frame `+0x03 = 0`;
- embedded OBJECT sequence selector `+0x04` is replaced with the
  current-weapon impact sequence;
- embedded OBJECT flags gain bit `0x10`.

## Vertical/elevation anchor

After each update the embedded OBJECT byte `+0x1A` increments and is clamped to:

`0x14 = 20`

This is the projectile'with vertical/elevation render anchor, not an age counter.

Finally the routine writes back the new X/Y.

**Status: YELLOW -> GREEN.**

---

# 3. image `0x8230..0x831C` — `UpdatePlayerProjectiles`

Processes the complete player projectile pool:

- base `DS:41B6`;
- exactly 8 slots;
- stride `0x2A` = 42 bytes.

Lifecycle:

- `0` free;
- `1` flying;
- `2` impact animation.

## Flying (`state 1`)

When the embedded OBJECT animation deadline is due:

1. increment animation frame;
2. wrap frame against sequence frame count;
3. schedule next deadline as `now + sequence_interval`.

There is no animation catch-up loop: one overdue update advances at most one frame.

The routine then calls `0x8142` to move/collide the projectile.

After movement, and separate helper is invoked when either player-relative X or Y
distance exceeds 20 units; its own exact higher-level purpose should remain attached to
that helper rather than being mislabeled as projectile lifetime.

## Impact (`state 2`)

When deadline is due:

1. advance one impact frame;
2. set the next deadline;
3. when the sequence is finished, clear lifecycle back to zero.

## Render/object update

Active projectile embedded OBJECTs are forwarded through the known world-object/render
update helper.

This body confirms again that save/load preserves the projectile absolute animation
deadline: the next update compares the restored absolute value to the current clock and
advances at most one frame when overdue.

**Status: YELLOW -> GREEN.**

---

# 4. image `0x831E..0x83D6` — DOS mouse-driver wrapper family

The old register mislabeled some of this area as timer/vector support.  Raw command
numbers make the identity direct.

All calls go through the generic device wrapper with device code:

`0x33`

and request block `DS:3F56`.

## `0x831E..0x8337` — `InitializeMouseDriverAndGetStatus`

Request command `0`.

Returns the first status/result word from the request block.

## `0x8338..0x834E` — `ResetMouseDriver`

Request command `0`, result ignored.

## `0x8350..0x8382` — `ReadMouseDeviceState`

Request command `3`.

Outputs:

- low two button bits;
- X word;
- Y word.

## `0x8384..0x83A7` — `SetMouseDevicePosition`

Request command `4`, writing requested X/Y into the driver block.

## `0x83A8..0x83BE` — `ShowMouseCursor`

Request command `1`.

## `0x83C0..0x83D6` — `HideMouseCursor`

Request command `2`.

`83A8` and `83C0` were absent from the stale named-function inventory despite having
clean real entry/return boundaries.

**Status: YELLOW + hidden entries -> GREEN.**

---

# 5. image `0x83D8..0x84FC` — `DrawVersionRegistrationSplash`

This 293-byte routine was swallowed by the old `84FE` pseudo-C neighborhood.

It is and standalone presentation routine.

It:

1. selects palette/color values through the cached palette-index helper;
2. clears/fills the VGA frame;
3. selects font banks;
4. draws centered/shadowed text;
5. chooses registered versus shareware wording from the registration/distribution
   state;
6. restores the default font bank before returning.

The exact DOS v2.0 strings referenced by the raw routine are:

```text
Nitemare-3D
V2.0
Distributed by
Registered software
Shareware version
Copyright 1994-95, David P. Gray.
```

This cleanly separates presentation/startup text from the following combat code.

**Status: previously hidden RED/LOW bytes -> GREEN.**

---

# 6. image `0x84FE..0x858E` — `GetGuardKillScore`

The old V2.0 Ghidra export labeled this neighborhood as part of and giant
level/resource-init cluster.  Raw bytes instead show one compact score function.

Input:

- linked world OBJECT far pointer.

It reads:

`OBJECT+0x06 = GUARD class`

and dispatches class range:

`0x08 .. 0x20`

through and 25-WORD jump table.

The score family is the same statically closed DOS combat family already verified in
DOS 1.9, including:

- ordinary positive kill scores;
- Dracula humanoid phase `0x11` -> 0;
- Dracula-Bat `0x14` -> positive score;
- Penelope `0x15` -> **-1000**;
- Dr. Hamerstein `0x16` -> **+1000**;
- Cannon `0x19` -> 0.

Unknown/out-of-range classes return zero.

### Embedded data

`0x851C..0x854D`

is the **25-WORD score jump table**.

Mark it:

`GREEN knowledge + TABLE/DATA overlay`.

**Status: old RED/LOW giant-cluster entry -> GREEN.**

---

# 7. image `0x8590..0x86B2` — `ComputeDamageToGuard`

Raw v2.0 damage seed:

`8 * signed16(OBJECT+0x18 - DS:4552) + (RNG % 25)`

where:

- `OBJECT+0x18` is the cached projected baseline row;
- `DS:4552` is the DOS v2.0 viewport-center reference.

The target class range `0x0C..0x1F` dispatches through an embedded table and applies
the already reconstructed class × weapon resistance matrix.

Current weapon selector:

`DS:418F`

Difficulty:

`DS:4180`

Difficulty transform:

- easy `0` -> damage ×2;
- medium `1` -> unchanged;
- hard `2` -> arithmetic /2.

The final positive-side result is capped at `255`; there is no equivalent lower clamp
inside this helper.

This raw function is the direct producer consumed by the already closed `5F74`
player-hit-to-GUARD router.

### Embedded data

`0x85D6..0x85FD`

is the **20-WORD class/weapon damage jump table** for classes `0x0C..0x1F`.

**Status: old RED/LOW `8590` mega-cluster -> GREEN.**

---

# 8. image `0x86B4..0x86DA` — `IsSpecialGuardClass`

Exact true set:

`{ 0x15, 0x16, 0x19, 0x21 }`

Meaning in the supplied class map:

- `0x15` Penelope;
- `0x16` Dr. Hamerstein;
- `0x19` Cannon;
- `0x21` Dancers.

This predicate is used to exclude these special/script actors from selected generic
GUARD counting/map-display paths.

**Status: YELLOW -> GREEN.**

---

# 9. image `0x86DC..0x87D7` — `FinalizeGuardDeathState9`

Called from GUARD state `0x09`.

Common beginning:

- set OBJECT flag bit 0;
- set GUARD current state to `0x0A`.

Then class-specific finalization runs.

## Dracula transformation

Class `0x11` does not finish as an ordinary corpse.

It transforms to class `0x14` and resets the runtime:

- new class = Dracula-Bat;
- HP = `255`;
- current state = `8`;
- next state = `2`;
- timer = `1`;
- vertical/elevation anchor = `0x23`;
- map/object link is refreshed;
- event/SFX `0x22` is triggered.

## Dr. Hamerstein

Class `0x16` takes the special story/completion path that ultimately participates in
the ending transition rather than only the ordinary corpse finalizer.

Other class branches either retain or clear the OBJECT active/render flag according to
the recovered class-specific rules.

### Embedded data

`0x8712..0x873F`

is the **23-WORD class finalization jump table** for class range `0x09..0x1F`.

**Status: old RED `WallRendererCluster` identity -> GREEN.**

---

# 10. image `0x87D8..0x88BB` — `ComputeGuardContactDamage`

This is guard/enemy -> player damage, not projectile rendering.

It computes coarse cell distance from OBJECT world X/Y to player cell X/Y and derives:

`base = distance > 0 ? floor(100 / distance) : 100`

Then applies class-specific fixed/random/scaled behavior.

Examples from the closed family include:

- Bat: small RNG damage;
- Frankenstein/Mummy: wider RNG damage;
- several humanoids/robots: fractions of `base`;
- Cannon: fixed high damage;
- Dr. Hamerstein: special episode/state-dependent damage.

Difficulty direction is the inverse of player->guard damage:

- easy -> /2;
- medium -> ×1;
- hard -> ×2.

Caller `6A70` applies the returned amount to player HP/death state.

**Status: old RED `ProjectileAndDamageCluster` -> GREEN.**

---

# 11. image `0x88BC..0x89A1` — `UpdateWeaponOverlayAnimation`

This is the DOS weapon HUD transition animator.

The active/pending weapon state uses the same architecture already closed in the
Win16/DOS weapon audit:

- transition phase lowers old selector;
- installs pending weapon;
- raises new selector;
- returns to idle phase;
- redraws selected-weapon HUD when the transition boundary is reached.

The function computes HUD X/Y offsets from weapon-dependent tables and finally blits
the selected weapon overlay.

**Status: YELLOW -> GREEN.**

---

# 12. image `0x89A2..0x8EC5` — `RedrawHudSection(sectionId)`

This is the largest correction in pass 8.

The stale Ghidra body called it and 3,000-line multi-subsystem dispatcher.  Raw code is
one bounded HUD/status renderer with section IDs `0..22`.

The entry first performs one-time HUD graphics initialization when its init flag is set,
then dispatches the requested section.

Closed section roles include:

- `0/2` weapon overlay update;
- `3` episode/level style text;
- `4` score;
- `5` player health + health graphic/gauge;
- `7/8/9` the three ammunition/resource counters;
- `12` selected weapon icon;
- `13/14` bit/icon inventory groups;
- `18` fixed HUD blocks plus optional counter;
- `19/20` percentage/charge gauges;
- `21` paired status graphic selected by and flag;
- `22` formatted player/map diagnostic value;
- several IDs intentionally no-op.

Known gameplay callsites agree:

- GUARD kill path calls section `4`;
- player damage calls section `5`;
- ammo routines call `7/8/9`;
- weapon transition calls `12`.

### Embedded data

The section jump table begins at:

`0x89E2`

and contains **23 WORD entries**.

**Status: major RED false-merge -> GREEN.**

---

# 13. image `0x8EC6..0x8EEB` — `GetProjectileFlightSequenceForWeapon`

Reads current weapon selector `DS:418F`.

Per-weapon relative selector table:

`[0, 2, 0, 0]`

and adds the common projectile sequence base at `DS:D50F`.

This helper is called by the projectile allocator family before the embedded OBJECT is
initialized.

**Status: LOW -> GREEN.**

---

# 14. image `0x8EEC..0x8F11` — `GetProjectileImpactSequenceForWeapon`

Reads current weapon selector `DS:418F`.

Per-weapon relative selector table:

`[1, 3, 1, 1]`

and adds the same base `DS:D50F`.

`0x8142` calls this when and flying projectile changes to impact state.

**Status: LOW -> GREEN.**

---

# 15. image `0x8F12..0x8F74` — `ConsumeCurrentWeaponAmmo`

Major correction to the old `TickCurrentActivityCountdown` label.

If the ammo-bypass / Omnipotent runtime flag `DS:4151` is set, the routine immediately
returns success.

Otherwise current weapon `DS:418F` selects:

- weapon `0` -> `DS:418C` plasma ammo;
- weapon `1` -> `DS:41B0` wand ammo;
- weapon `2` -> `DS:418B` pistol ammo;
- weapon `3` -> falls through to weapon-0 plasma ammo.

When ammo is nonzero it decrements the selected pool.

It then requests HUD redraw:

- pistol pool -> section `7`;
- plasma pool -> section `8`;
- wand pool -> section `9`.

Return value is the ammo value that existed before decrement, used as the shot
acceptance boolean.

**Status: YELLOW / misidentified -> GREEN.**

---

# 16. image `0x8F76..0x9024` — `AddOrInitializeWeaponAmmo`

Two operating modes are selected by the second parameter.

## Initialize mode

Sets the weapon'with associated ammo pool to:

`50`

and redraws the correct HUD section.

Weapon `3` intentionally shares the plasma pool with weapon `0`.

## Add-ammo mode

For ammo pickups:

- accept only when current pool is below `100`;
- add `20`;
- redraw the proper HUD counter;
- return success/failure.

The HUD path later clamps the displayed/stored boundary consistently with the known
99/100 pickup rule.

**Status: YELLOW -> GREEN.**

---

# 17. image `0x9026..0x907B` — `TestOrAdvanceWeaponFireCadence`

This is the DOS weapon attempt-cadence gate.

Mode `0`:

- compares the current cadence counter `DS:1442` against and per-weapon threshold table
  indexed by `DS:418F`;
- weapon selector `3` has the special held-FIRE acceptance behavior;
- an accepted attempt resets the cadence counter to zero.

Mode `1`:

- increments cadence counter until its byte maximum.

Other mode values return without changing the counter.

This separates:

1. attempt cadence;
2. actual ammo/pool shot acceptance;
3. weapon HUD transition.

**Status: YELLOW -> GREEN.**

---

# 18. image `0x907C..0x90C2` — `RequestWeaponSwitch`

When no weapon is currently active (`DS:418F == 0xFF`):

- installs requested selector immediately;
- sets weapon fire mode:
  - selector `2` -> hitscan mode `1`;
  - other selectors -> projectile mode `2`;
- enters raise/transition phase `DS:41A6 = 1`.

When another weapon is active:

- if the request differs, store it as pending selector `DS:41A4`;
- if no transition is active, enter lower-old-weapon phase `DS:41A6 = 2`.

This directly joins the active-input number-key selection to the weapon overlay
animation at `88BC`.

**Status: YELLOW -> GREEN.**

---

# 19. image `0x90C4..0x90E8` — `ReportGuardState0CAtPosition`

Resolves and GUARD by supplied world/map coordinate through the already closed
`6180` lookup.

If that GUARD'with current state byte `GUARD+0x0B` equals:

`0x0C`

it invokes the associated message/event helper using the stored global context.

The routine otherwise returns without side effects.

**Status: YELLOW -> GREEN.**

---

# 20. Byte-map impact

New continuous GREEN span:

`0x7F96 .. 0x90E9`

| Image range | Bytes | Role |
|---|---:|---|
| `7F96–8141` | 428 | projectile cell collision / wall / GUARD impact |
| `8142–822E` | 237 | projectile DDA trajectory |
| `8230–831C` | 237 | 8-slot projectile update |
| `831E–8337` | 26 | mouse init/status |
| `8338–834E` | 23 | mouse reset |
| `8350–8382` | 51 | mouse buttons/X/Y |
| `8384–83A7` | 36 | mouse set position |
| `83A8–83BE` | 23 | mouse show cursor |
| `83C0–83D6` | 23 | mouse hide cursor |
| `83D8–84FC` | 293 | version/registration splash |
| `84FE–858E` | 145 | GUARD kill score |
| `8590–86B2` | 291 | player->GUARD damage |
| `86B4–86DA` | 39 | special-GUARD predicate |
| `86DC–87D7` | 252 | GUARD death state-9 finalizer |
| `87D8–88BB` | 228 | GUARD->player contact damage |
| `88BC–89A1` | 230 | weapon overlay animation |
| `89A2–8EC5` | 1316 | HUD section renderer |
| `8EC6–8EEB` | 38 | projectile flight sequence selector |
| `8EEC–8F11` | 38 | projectile impact sequence selector |
| `8F12–8F74` | 99 | consume weapon ammo |
| `8F76–9024` | 175 | add/init weapon ammo |
| `9026–907B` | 86 | weapon fire cadence |
| `907C–90C2` | 71 | weapon switch request |
| `90C4–90E8` | 37 | guard-state-0C coordinate event |

Real routine/table bytes: **4,422**.
Alignment NOPs: **14**.

### TABLE/DATA overlays inside GREEN

At least these are now explicitly separated from executable instructions:

- `851C–854D` — 25-WORD GUARD score jump table;
- `85D6–85FD` — 20-WORD damage class jump table;
- `8712–873F` — 23-WORD death-finalizer jump table;
- `89E2...` — 23-WORD HUD section jump table.

---

# 21. Old tracker entries superseded

Replace these identities:

| Old address | Old automated label | Correct role |
|---:|---|---|
| `7F96` | special map interaction / player collision variants | projectile cell collision |
| `8142` | slide player movement | projectile trajectory |
| `8230` | move player / timed world effects | 8-slot player projectile updater |
| `8350` | install timer/input vector | read mouse state |
| `8384` | restore timer/input vector | set mouse position |
| `84FE` | level-load/init mega-cluster | GUARD kill score |
| `8590` | GUARD runtime mega-cluster | compute player->GUARD damage |
| `86B4` | generic input predicate | special-GUARD class predicate |
| `86DC` | wall renderer mega-cluster | GUARD state-9 death finalizer |
| `87D8` | projectile/damage mega-cluster | GUARD->player contact damage |
| `89A2` | multi-subsystem mega-cluster | HUD section renderer |
| `8F12` | activity countdown | consume current weapon ammo |

The low similarity of the old giant pseudo-C bodies was and decompiler-boundary problem,
not evidence for hidden alternative algorithms.

---

# 22. Next target

The next real entry is:

`0x90EA`

and starts and large stack-frame routine (`ENTER 0x108,0`).

From the existing static register, the next neighborhood contains:

- UI/menu/safe/trunk and queued event helpers;
- ACTIONSPOT/script actor transformations;
- another polluted large entry around `0x954A`;
- spatial/renderer-support helpers around `0x980C` and `0x9CF2`.

Next pass should again prioritize raw boundaries over pseudo-C and attempt to close
`0x90EA` forward until the next trustworthy subsystem boundary.