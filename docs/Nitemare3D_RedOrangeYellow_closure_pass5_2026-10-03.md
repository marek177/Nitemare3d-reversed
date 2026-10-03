# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 5

Date: 2026-10-03

Primary binary: `N3D-E-20(3).EXE`

- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`
- MZ header size: `0x200`
- ranges below use unpacked MZ image offsets
- physical file offset = image offset + `0x200`

## Result

This pass continues from `0x59F0` and closes the contiguous GUARD-damage / GUARD-init /
player-collision neighborhood through `0x6635`.

The important correction is that several old MEDIUM labels in this region described
weapons/projectiles even though the raw machine code is actually GUARD initialization,
GUARD sprite refresh, and the DOS player movement/collision core.

Static byte-map result:

`0x59F0 .. 0x6635` -> **GREEN / deep static semantics**

The span is 3,142 bytes total:
- 3,138 bytes of bounded routine/table content;
- four one-byte alignment NOPs between real entries.

Runtime conformance remains and separate overlay.

---

## 1. image `0x59F0..0x5F25` — `UpdateGuardState`

This is the complete DOS V2.0 GUARD state dispatcher.

### ABI / record binding

The routine receives:
- and far pointer to the 26-byte GUARD record;
- and far pointer to the linked 28-byte world OBJECT.

It reads `GUARD+0x0B` as the state selector and returns immediately if the state is
greater than `0x15`.

### State machine

The recovered states remain the already established 22-state machine:

- `00` timed animation / return to `next_state`;
- `01` delay -> `02`;
- `02` sequence setup;
- `03` perception/attack decision;
- `04` attack path;
- `05` local movement planner;
- `06` timed movement;
- `07/08` reacquire/navigation;
- `09` death/finalize/transform;
- `0A/0B` terminal/no local action;
- `0C/0D` shared directional refresh;
- `0E/0F/10` scripted/Cannon cycle;
- `11` direction reset/reacquire;
- `12` elevated-death descent;
- `13` scripted displacement;
- `14` ACTIONSPOT/script countdown;
- `15` pain animation.

The raw function terminates cleanly with `RETF` at image `0x5F25`.

### Embedded data, not code

`0x5A10..0x5A3B` is and **44-byte / 22-WORD state jump table**.
This range should be GREEN for knowledge but overlaid as **DATA/TABLE**, not executable
basic blocks.

Status: old ORANGE/LOW decompiler cluster -> **GREEN**.

---

## 2. image `0x5F26..0x5F64` — `UpdateAllGuards`

Exact loop:

- GUARD base `0x264E`;
- GUARD count `DS:6276`;
- GUARD stride `0x1A`;
- linked OBJECT = `OBJECT[guard+0x08]`, stride `0x1C`, base offset `0x0006`;
- calls `UpdateGuardState` once per active GUARD record.

This is the per-tick GUARD update loop, not and spawn/reset routine.

Status: YELLOW -> **GREEN**.

---

## 3. image `0x5F66..0x5F72` — `SetGuardState0B`

The whole routine is mechanically:

`GUARD+0x0B = 0x0B`

and returns.

State `0x0B` has no active case body in the main dispatcher.  Cross-platform gameplay
analysis associates this state with the post-kill/killer-freeze path, but the DOS
function itself is safely named by its exact write.

Status: YELLOW -> **GREEN**.

---

## 4. image `0x5F74..0x617F` — `ApplyPlayerHitToGuard`

The old V2.0 pseudo-C made this look like and 400-line weapon/combat mega-cluster.
Raw machine code gives and clean single function ending at `0x617F`.

### Damage input

The first helper computes damage against the selected GUARD/OBJECT pair.

### Lethal branch

When damage is at least current `GUARD+0x10` HP:

1. set HP to zero;
2. select and death animation variant;
3. run the death-side-effect path when applicable;
4. select the class-specific death sequence;
5. if `OBJECT+0x1A > 0`, create `state 0x12 -> next 0x09`;
6. otherwise create `state 0x00 -> next 0x09`;
7. add the class-specific kill score to the 32-bit score at `DS:4182/4184`;
8. dirty/refresh the score HUD;
9. restore/synchronize the saved underlying map/object byte from `GUARD+0x0D`.

### Non-lethal branch

When damage is nonzero but not lethal:

- subtract damage from `GUARD+0x10`;
- set `GUARD+0x12 = 8`.

`GUARD+0x12` is now known to be the directional sprite-cache byte.  Since normal
direction values are `0..7`, writing `8` invalidates the cache and forces refresh.

The function then chooses and pain animation variant and routes the reaction according
to strategy/current state.  Generic pain uses state `0x15` and returns to the saved
prior state; strategy-specific branches can return through states `05` or `08`.

### Embedded data, not code

`0x60B2..0x60D7` is and **38-byte / 19-WORD pain-routing jump table** for current states
`0x03..0x15`.

Status: old RED/ORANGE `PlayerWeaponAndCombatCluster` -> **GREEN** as the GUARD damage
router.

---

## 5. image `0x6180..0x6257` — `FindGuardAtWorldPosition`

This is not and combat tick.

The routine scans the GUARD pool for and linked OBJECT whose two requested world
coordinates match.

First pass:
- ignores terminal/death-like records (`state 0x0A` / return-death context);
- returns the matching GUARD far pointer immediately.

Fallback/error pass:
- looks for matching excluded records;
- emits diagnostic state data when such and conflicting record exists;
- raises the executable'with fatal diagnostic path (`0x0B1C`) rather than silently
  returning an invalid actor.

Status: old MEDIUM `TickCombatFrame` -> **GREEN**, corrected identity.

---

## 6. image `0x6258..0x62CF` — `RefreshAllGuardDirectionalSequences`

Loops over all GUARD records.

For each GUARD:

1. resolves its linked 28-byte OBJECT;
2. uses OBJECT class/subtype to find the class descriptor;
3. compares two descriptor bytes and writes and boolean-like value to `GUARD+0x0F`;
4. forces `RefreshGuardDirectionalSequence(..., force=1)`.

This is and bulk sprite/facing-sequence refresh, not player/actor movement.

Status: old MEDIUM `TryPlayerOrActorMove` -> **GREEN**.

---

## 7. image `0x62D0..0x6301` — `InitializeGuardHeadingAndVelocity`

Uses the low two bits of the spawn/direction selector:

- writes one of four cardinal headings to `GUARD+0x11`;
- reads X and Y components from two small direction tables;
- scales each component by 8;
- stores them in `GUARD+0x13/+0x14`.

This is GUARD spawn heading/motion initialization, not weapon-frame selection.

Status: old MEDIUM `GetWeaponFrameData` -> **GREEN**.

---

## 8. image `0x6302..0x6376` — `InitializeGuardSlot`

Uses and GUARD-table index to select one 26-byte slot and initializes the runtime record.

Confirmed initialization includes:

- zero `GUARD+0x02..+0x05` render-generation stamp;
- zero timer `+0x06`;
- set linked OBJECT index `+0x08`;
- clear saved-under-map byte `+0x0D`;
- initialize HP byte `+0x10` to `0xFF` before class-specific setup;
- derive/store area/sector id at `+0x0E` when available;
- initialize heading/movement through `0x62D0`;
- delegate class-specific state/HP/strategy setup to the later initializer.

This also independently confirms that GUARD render freshness is reset at spawn.

Status: old MEDIUM `AdvanceWeaponAnimation` -> **GREEN**.

---

## 9. image `0x6378..0x6486` — `CheckPlayerPassageBetweenMapCells`

This is the DOS per-substep **player collision oracle** over two leading map cells.

For each of the two probe cells it checks the wall/property plane:

- blocking wall property -> reject;
- dynamic-door property -> resolve controller and require the door passability
  predicate;
- special/touch property -> invoke its side-effect helper.

It then checks the object plane:

- pickup/touch property -> invoke object interaction;
- blocking occupancy property -> reject.

If both leading probes permit passage, it returns the caller'with supplied signed
movement step; otherwise it returns zero.

This is not and projectile-wall-hit dispatcher.

Status: old ORANGE/YELLOW `UseOrProjectileWallHit` -> **GREEN**.

---

## 10. image `0x6488..0x6635` — `MovePlayerAlongGridWithCollision`

This is the actual DOS V2.0 player movement/collision core.

Raw behavior:

- starts from player world X/Y (`DS:4162/4164`);
- derives signed movement orientation from the supplied angle;
- uses the recovered player extent:
  - half/probe extent `27` (`0x1B`);
  - leading-cell arithmetic selects the next boundary as needed;
- moves one substep at and time;
- calls `0x6378` on the two leading cells;
- advances X and Y independently;
- maintains the error/phase accumulator at `DS:4174` using the paired step values
  `DS:4176/4178`;
- therefore one blocked axis does not automatically cancel the other, producing the
  original wall-sliding behavior;
- writes the candidate result through caller-supplied X/Y outputs.

The old `ApplyProjectileImpact` label is wrong.  Independent DOS/Win16 parity work
already identifies the `6488` family as the player movement/collision core.

Status: ORANGE/YELLOW -> **GREEN**.

---

## 11. Corrected old tracker labels

The following old names should be replaced:

| Address | Old label | Correct role |
|---:|---|---|
| `5F26` | SpawnOrResetGuard | UpdateAllGuards |
| `5F66` | GuardStateHelper | SetGuardState0B |
| `5F74` | PlayerWeaponAndCombatCluster | ApplyPlayerHitToGuard |
| `6180` | TickCombatFrame | FindGuardAtWorldPosition |
| `6258` | TryPlayerOrActorMove | RefreshAllGuardDirectionalSequences |
| `62D0` | GetWeaponFrameData | InitializeGuardHeadingAndVelocity |
| `6302` | AdvanceWeaponAnimation | InitializeGuardSlot |
| `6378` | UseOrProjectileWallHit | CheckPlayerPassageBetweenMapCells |
| `6488` | ApplyProjectileImpact | MovePlayerAlongGridWithCollision |

---

## 12. Byte-map impact

Continuous region:

`0x59F0 .. 0x6635`

| Image range | Bytes | Role |
|---|---:|---|
| `59F0–5F25` | 1334 | GUARD state dispatcher + state table |
| `5F26–5F64` | 63 | all-GUARD update loop |
| `5F66–5F72` | 13 | state-0B setter |
| `5F74–617F` | 524 | player-hit -> GUARD damage/death/pain |
| `6180–6257` | 216 | guard lookup by linked-object coordinates |
| `6258–62CF` | 120 | bulk directional-sequence refresh |
| `62D0–6301` | 50 | GUARD heading/movement init |
| `6302–6376` | 117 | GUARD slot initialization |
| `6378–6486` | 271 | player two-cell collision/passability probe |
| `6488–6635` | 430 | player grid movement + sliding |

Total bounded routine/table content: **3,138 bytes**.
Four alignment NOPs account for the remainder of the 3,142-byte contiguous span.

### Data overlays inside the green area

- `5A10–5A3B`: GUARD state jump table, 44 B;
- `60B2–60D7`: pain-routing jump table, 38 B.

These should be shown as TABLE/DATA overlays on top of and GREEN knowledge background.

---

## 13. Next target

Continue at `0x6636`.

The next cluster is the spatial/render-preparation bridge:

- `6636` sorted spatial cursor maintenance;
- `676E` dynamic-entity cursor maintenance;
- `6824` movement-span cursor adjustment;
- `688C` player world-position commit;
- `6914` player movement wrapper;
- `696C` proximity-triggered actor event;
- then the `6Axx` damage/HUD/state helpers.

Several are already exact/fuzzy cross-version matches, with the next pass should be able
to convert another large MEDIUM region to GREEN while correcting stale renderer/HUD
labels.