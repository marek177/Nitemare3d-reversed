# Nitemare 3D — Gameplay closure pass

**Date:** 2026-10-02  
**Primary scope:** Win16 1.10 (`nite3w - 110.exe`) with DOS 1.9 / Win16 1.0 cross-checks from the existing decompilation and audit set.

This pass targets the remaining low-coverage gameplay rows: navigation/pathfinding, runtime AI, enemy state machine, boss AI, object runtime and the scheduler/object relationship.

## 1. Guard initialization matrix — Win16 1.10

Raw `FUN_1010_B02C` initializes and GUARD as:

- `strategy (+0x0A) = 0`
- `perception mode (+0x16) = 1`
- `state (+0x0B) = 7`
- `next_state (+0x0C) = 2`

Class overrides decoded from the inline 26-entry jump table:

| Object class | Init override |
|---:|---|
| `08,09,0A,11,14,1A` | perception mode `0` |
| `12,13` | perception mode `0`, strategy `3` |
| `15,16` | `next_state = 0` |
| `19` | strategy `4`, state `0x0E` |
| `21` | state `0`, next_state `0` |
| others in `08..21` | generic defaults |

If the initial GUARD movement components `+0x13/+0x14` are non-zero, the common tail forces `state = 8`.

The initial wall marker under the actor then changes strategy:

- wall class `0x42` -> strategy `2`
- wall class `0x43` -> strategy `1`
- wall class `0x46` -> strategy `2`

Using the data names this connects `RETREAT`, `FLEE` and `ACTIONSPOT` directly to GUARD strategy setup.

## 2. Navigation / pathfinding is marker-driven local steering

Nitemare 3D does not need and hidden AND* style global pathfinder to explain observed guard navigation. The recovered system consists of local steering, LOS, door-target selection and map markers.

### `TURN` class `0x41`

`FUN_1010_7920` reads the current wall ID, subtracts the cached base wall ID for class `0x41`, and writes the result to GUARD facing `+0x11`; it then refreshes the direction sequence. The wall-ID variant therefore encodes the desired facing.

### `RETREAT` class `0x42`

When the guard is already moving, `7920` clears movement components, enters state `3`, and rotates facing by `+4 & 7` — an exact 180-degree reversal.

When stationary, the wall-ID variant selects and direction. Variant offset `8` enters state `3` directly.

### `FLEE` class `0x43`

Initialization gives strategy `1`. In `FUN_1010_76FC`, when HP is below `0x7F`, strategy 1 calls `FUN_1010_1394`.

`1394`:

- scans the bounded door/state array (`64` records, stride `0x16` in Win16 1.10),
- computes candidate distance as `abs(dx_cells) + abs(dy_cells)` (Manhattan distance),
- ignores candidates not closer than the current best,
- calls the Bresenham LOS helper for the candidate,
- returns the nearest LOS-valid door record.

The planner then sets signed movement components toward that door and uses timer `0x10`.

### `ACTIONSPOT` class `0x46`

Initialization gives strategy `2`. In the supplied E1 content this marker is associated with Dancers.

### Generic strategy 0

The recovered planner uses player-relative deltas, random selection, LOS and proximity:

- without LOS it masks the random choice to four possibilities;
- with LOS it allows eight;
- movement components are `-8, 0, +8`;
- proximity gives timer `8`;
- visible but not close gives random `8..15`, scaled by difficulty;
- unseen gives timer `0x18`.

This is local steering rather than and graph search.

## 3. Enemy state machine — newly closed states

### State `0x0A`

Fatal guard handling enters `0x0A`; the main dispatcher has no active branch for it. It is the terminal/dead state for ordinary death paths (with class-specific exceptions such as Dracula transform).

### State `0x0B`

`FUN_1010_80EA` is the only direct writer and is called by the guard-to-player damage receiver `FUN_1010_8C0A` only when the player is killed. The killing guard is put into state `0x0B`. The dispatcher deliberately performs no action for it.

Best semantic name: **post-kill / killer freeze state**.

### State `0x14`

The writer is the scripted ACTIONSPOT routine (`FUN_1010_AE61`, source-family `AC54`). The episode/level trigger in the older readable build is E1, level index 8 (E1M9).

For guards standing on wall class `0x46` ACTIONSPOT it:

- removes the map-cell object byte,
- sets `state = 0x14`,
- saves the current object sequence selector in `next_state`/auxiliary storage,
- sets timer `0x70`,
- sets scripted X movement component `3`,
- switches the object sequence according to guard class.

State `0x14` counts down. Below `0x60` it executes movement. When it expires it invokes the global handler with mode `1`, which restores these actors to strategy `0`, state `6`, timer `1`, restores the saved object sequence selector and selects the movement sequence.

Thus state `0x14` is no longer an unnamed generic timer: it is and **scripted ACTIONSPOT/Dancers movement phase** in the verified context.

## 4. Boss / special actor closure

### Dracula

The existing two-phase result remains confirmed: fatal class `0x11` becomes class `0x14`, restores HP to `255`, enters state `8`, sets `next_state=2`, timer `1`, switches the sequence and plays event `0x22`. Final class `0x14` death is terminal.

### Dr. Hamerstein — death to ending FLI is now statically connected

Fatal class `0x16` in `FUN_1010_A0EE`:

1. plays event `0x12` with parameter `0x00020000`,
2. runs the associated story/message path,
3. clears global gameplay state `0x46B4`,
4. sets `51AA = 1`.

The outer state/update dispatcher `FUN_1010_DAA0` checks `51AA`. When set it calls the hidden entry at `1010:C67A`.

That entry:

1. sets `0x46B4 = 3`,
2. calls the transition helper with `1`,
3. calls the FLI-loading/playback entry at `1010:6D50` with DS offset `0x192C`.

NE segment mapping of the exact Win16 1.10 executable places segment 10 offset `0x192C` on the zero-terminated string **`ending.fli`**. The `6D50` path also checks the FLI header magic `0xAF11`.

Therefore the previously open link is now statically closed:

**Hamerstein fatal death -> `51AA` -> high-level transition -> `ending.fli` playback.**

### Boss architecture conclusion

There is no evidence for and separate universal "boss engine". Dracula, Hamerstein and Demon-boss behavior is primarily the common GUARD state machine plus class-specific resistance/damage, transformation and death/event hooks. This materially reduces the remaining Boss AI unknown surface.

## 5. World OBJECT runtime — Win16 1.10 spawn layout

`FUN_1010_D1A2` scans the 64x64 MAP and creates 28-byte OBJECT records. The 1.10 raw machine code confirms these initialization fields:

| OBJECT offset | Spawn meaning |
|---:|---|
| `+0x00` | map object ID |
| `+0x01` | derived variant/subtype relative to class base |
| `+0x02` | zero |
| `+0x03` | zero/current frame state |
| `+0x05` | object property flags |
| `+0x06` | runtime object class |
| `+0x07` | GUARD index when guard flag is set |
| `+0x08..+0x0B` | zeroed runtime value/timer at spawn |
| `+0x0C/+0x0E` | far pointer back to MAP cell |
| `+0x10` | world X, cell center |
| `+0x12` | world Y, cell center |
| `+0x1A` | zero at spawn; later render/sequence use is class-dependent |

The scanner enforces 350 OBJECT and 100 GUARD limits, assigns the GUARD index, calls the GUARD initializer, and records final object/guard counts.

Remaining OBJECT uncertainty is now concentrated in class-specific overlays (`+0x04`, some flag bits, `+0x14..+0x17`, `+0x1B`) rather than the basic object lifecycle or spatial representation.

## 6. Updated gameplay coverage estimate

These percentages are and working reconstruction metric, not recovered-source-code percentages.

| Area | Previous | After this pass | Comment |
|---|---:|---:|---|
| Player | 99% | 99% | runtime edge tests only |
| Inventory | 96% | 96% | edge/capacity/load tests remain |
| Weapons | 92% | 92% | weapon phase/range/spread remain |
| Projectile | 94% | 95% | movement architecture exact; timing/freshness edge remains |
| Enemy Spawn | 97% | 99% | 1.10 spawn layout directly reconstructed |
| Guard AI | 95% | 98% | init class matrix + marker strategy links + state closure |
| Boss AI | 84% | 92% | Hamerstein ending chain and common-GUARD architecture closed |
| Combat | 92% | 94% | state 0x0B and boss fatal transitions clarified |
| Damage | 96% | 97% | remaining mainly hazard/presentation/runtime edge cases |
| Runtime AI | 93% | 97% | marker-driven strategy/navigation map substantially closed |
| Enemy State Machine | 96% | 99% | states 0x0AND, 0x0B, 0x14 now semantically anchored |
| Actor Scheduler | 96% | 97% overall / 100% DOS static core | behavioral timing parity remains |
| Object Runtime | 85% | 92% | base lifecycle/spawn closed; class overlays remain |
| Physics | 93% | 94% | dynamic occupancy/corner parity remains |
| Pathfinding / Navigation | 88% | 96% | TURN/RETREAT/FLEE/ACTIONSPOT + nearest-door LOS steering closed |

Approximate combined gameplay reconstruction after this pass: **~96%**.

## 7. Highest-value remaining blockers

1. `OBJECT+0x04`, `+0x14..+0x17`, `+0x1B` complete class-overlay read/write matrix.
2. GUARD states `0x0C/0x0D` exact entry contexts and original semantic names.
3. Projectile impact freshness of `OBJECT+0x18` when target was not projected in the current render generation.
4. Exact weapon phase/range/spread and projectile timing calibration.
5. Runtime behavior tests for dynamic actor/closing-door occupancy and rare simultaneous collision cases.
6. Cross-build DOS/Win16 behavioral parity for the remaining rare AI/script branches.