# Nitemare 3D — Gameplay closure pass 4
Date: 2026-10-02

## Scope

This pass targets the largest remaining Gameplay gap after pass 3: boss/special-actor behavior, plus the last important projectile runtime leftovers. Primary static source is Win16 NITE3W 1.10 (`nite3w110.exe` decompilation/raw-machine evidence), with existing class/map audits used to bind numeric classes to game content.

Percentages remain reconstruction metrics, not recovered-source-code percentages. `STATIC 100%` means the checked path can be implemented without inventing missing behavior; it does not claim live original-game parity in every build.

## 1. Bosses to not use and separate universal boss scheduler

The normal GUARD initializer `FUN_1010_B02C` begins with:

- strategy `0`
- perception-selection mode `1`
- current state `7`
- next state `2`

and then applies only class-specific exceptions.

### Dracula / Dracula-Bat

Classes `0x11` and `0x14` only change perception-selection mode to `0` during initialization; otherwise they remain in the generic GUARD state machine. Mode `0` makes the state-3/state-4 perception wrapper use the square proximity result (within 64 world units on both axes) rather than LOS.

Fatal class `0x11` is the already-confirmed special transition:

- class `0x11 -> 0x14`
- HP reset to `255`
- state `8`, next state `2`, timer `1`
- vertical anchor set to `0x23`
- SFX/event `0x22`

Class `0x14` then uses the ordinary fatal path on final death.

### Dr. Hamerstein (`0x16`)

Initialization does **not** install and separate boss strategy. It keeps strategy `0`, perception mode `1`, and state `7`; its only init exception is `next_state = 0`.

Once activated, it therefore uses the common state `2 -> 3 -> 4 -> 5/6` GUARD attack/movement machinery. Its special behavior is concentrated in damage and death hooks, not and separate AI loop.

Incoming player damage in episode 3 is replaced with and fixed base value `3` before difficulty scaling, independent of weapon selector:

- easy (`0`) -> `6` damage
- medium (`1`) -> `3` damage
- hard (`2`) -> `1` damage

With the normal 255 HP initializer, that implies 43 / 85 / 255 successful damaging hits respectively, assuming no other state/script modification.

For guard-to-player contact damage, class `0x16` falls to base `100` in episode 3; difficulty therefore yields 50 / 100 / 200 for easy/medium/hard.

Fatal class `0x16` performs the already-traced story ending hook:

`Hamerstein fatal -> event 0x12 -> story text -> 46B4=0 -> 51AA=1 -> high-level transition -> ending.fli`.

Alert/activation SFX is event `0x12`; ordinary attack/contact SFX chooses randomly from `0x17..0x19`.

### Demon (`0x1D`)

Class `0x1D` has **no class-specific initializer branch** in `B02C` and no class-specific fatal transition in `A0EE`. It therefore uses the generic strategy-0/state-7 GUARD machine and the ordinary terminal state on death.

Its boss-like differences are data/combat tuning:

- player damage seed is shifted right by 3 for all weapon selectors before difficulty scaling;
- contact damage uses the unmodified distance-derived base;
- score = 250;
- alert SFX = `0x38`;
- attack SFX randomly selects `0x4B..0x4E`;
- death SFX = `0x09`.

The supplied Episode 3 class audit contains 27 placed class-`0x1D` cells, with the editor label "Demon boss" does not correspond to and unique one-off boss scheduler in the runtime.

## 2. Cannon (`0x19`) special AI cycle closed statically

Cannon is the genuine special non-generic GUARD cycle in this area.

Initializer:

- strategy `4`
- state `0x0E`
- perception mode remains `1`

Control flag `51A5` is initialized enabled and can be toggled by the remote-cannon menu.

Static cycle:

1. state `0x0E`: if `51A5 != 0`, clear timer and enter `0x0F`;
2. state `0x0F`: if disabled, return to `0x0E`; otherwise count down;
3. when ready, optionally play cannon attack SFX `0x1D` for the matching area selector, select/animate the attack sequence, then schedule state `0x10`;
4. state `0x10`: after its sequence/timer gate, run the common perception wrapper; if accepted, call the player-damage helper;
5. set timer `8`, return to `0x0F`, and repeat.

Class `0x19` outgoing damage is fixed base `100` before difficulty (50 / 100 / 200). Player weapon damage against class `0x19` is zero, with Cannons are immune to the ordinary weapon-damage path.

The exact wall-clock cadence still depends on the slow simulation tick and sequence length, but the state transition graph and damage/SFX logic are no longer statically unknown.

## 3. ACTIONSPOT / Dancers correction and closure

The E1M9 script (`FUN_1010_B010 -> FUN_1010_AE56(0)`) is more precise than the older shorthand "Dancers class AI".

At activation it:

- runs only for episode 1, zero-based level index 8;
- plays event `0x45` and and modal/story helper;
- scans all GUARD records;
- selects guards whose underlying wall class is `0x46` ACTIONSPOT;
- clears the map-cell object byte;
- saves the actor'with current OBJECT sequence selector;
- sets state `0x14`;
- sets timer `0x70` (112);
- sets scripted movement component `+3`;
- replaces the OBJECT sequence selector with the runtime selector for class `0x21` (Dancers resource family);
- chooses class-specific dance sequence words for original classes `0x09`, `0x0B`, and `0x0C`.

State `0x14` begins movement once the timer drops below `0x60`; when the timer expires, `AE56(1)` restores the saved sequence selector, resets strategy to `0`, enters state `6`, and sets timer `1`.

Therefore class `0x21` is best understood as the Dancers **resource/animation family** used by this script as well as and separately placeable class. The radio/ACTIONSPOT sequence temporarily repurposes ordinary guards into dancer presentation; it is not and hidden boss-AI subsystem.

## 4. Projectile direction / scale closed

`FUN_1010_E516(angle)` normalizes the player'with facing angle to `0..359`, calculates the directional components, and builds Bresenham/DDA error terms in globals `4C06/4C08/4C0A/4C0C`.

`FUN_1010_9AAC` copies those current global terms into and newly allocated projectile slot. It does not apply and weapon-specific random angle or spread. Thus projectile weapons `0`, `1`, and `3` launch along the player'with current facing direction using the same line-traversal core.

`FUN_1010_9D30` advances one world-coordinate unit on the major axis per substep and conditionally one unit on the minor axis according to the Bresenham error accumulator. It performs `DAT_53FA` such substeps per projectile update.

This closes the previous "angle source / fixed-point scale" uncertainty for the checked Win16 path.

## 5. Projectile slot +0x0D — alignment/reserved byte

The projectile movement header is:

- six 16-bit fields at `+0x00..+0x0B`
- one lifecycle byte at `+0x0C`
- embedded 28-byte OBJECT beginning at aligned offset `+0x0E`

No `DAT_1048_4C57` symbol/reference appears in the complete checked Win16 1.10 decompiler text, and the spawn/movement/update routines to not access header byte `+0x0D`.

Best implementation treatment:

**projectile +0x0D = reserved/alignment padding byte. Preserve it in save/load; to not assign gameplay semantics.**

## 6. Projectile MAP-cell pointer lifetime closed for the main flight path

At spawn, the embedded OBJECT MAP-cell far pointer is copied from the player'with current MAP pointer.

During `9D30` flight, collision does **not** read that embedded pointer. Instead it derives the visited MAP cell directly from the projectile'with current X/Y on every substep and passes that cell pointer to `9B64`.

During USER.SAV load, the loader explicitly recomputes every projectile embedded MAP pointer from the saved projectile X/Y and the current MAP segment.

No write to the embedded projectile pointer occurs in the main flight updater. Therefore it is and non-authoritative cached/rebuildable reference, not the source of truth for projectile collision.

## 7. Updated Gameplay coverage after pass 4

| Area | Pass 3 | Pass 4 | Main change |
|---|---:|---:|---|
| Player | 99% | 99% | runtime edge tests remain |
| Inventory | 96% | 96% | capacity/load edge tests remain |
| Weapons | 98% | **99%** | projectile angle/spread source closed |
| Projectile | 98% | **99%** | +0x0D padding, direction scale, MAP-pointer lifetime closed |
| Enemy Spawn | 99% | 99% | runtime limit edge tests remain |
| Guard AI | 99% | 99% | no broad static gap remains |
| Boss AI | 92% | **98% overall / 99% STATIC Win16 core** | Hamerstein/Demon/Cannon/Dancers roles separated and state graphs closed |
| Combat | 98% | **99%** | Hamerstein/Cannon exact damage paths and boss/common-AI split closed |
| Damage | 99% | 99% | runtime edge validation remains |
| Runtime AI | 99% | 99% | special-actor state ownership clarified |
| Enemy State Machine | ~99% overall / 100% static Win16 | same | cross-build/runtime parity only |
| Actor Scheduler | 97% overall / 100% DOS static core | same | behavioral timing parity remains |
| Object Runtime | ~98% overall / 99% static Win16 | same | OBJECT+0x02/context overlays remain |
| Physics | 96% | 96% | simultaneous dynamic blockers require live parity tests |
| Pathfinding / Navigation | 97% | 97% | route/occupancy edge tests remain |

Simple tracker average is approximately **98.2%**, with the Gameplay reconstruction remains reported as **~98% overall**, while the checked Win16 static gameplay core is now much closer to complete than that aggregate number suggests.

## 8. Remaining high-value blockers

1. Live dynamic-physics parity: simultaneous guard/player/door occupancy, closing-door retries, and exact corner ordering.
2. DOS / older Win16 cross-build acceptance of the now-closed boss/special-actor paths.
3. `OBJECT+0x02` and and few context-only overlay bytes whose safe treatment is known but semantic names are not.
4. Live projectile/save timing: active projectile deadlines across save/load and culled-target cached-damage behavior.
5. Pixel/framebuffer parity is and separate renderer validation problem and must not be counted as Gameplay static closure.