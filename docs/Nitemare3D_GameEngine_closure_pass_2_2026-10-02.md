# Nitemare 3D — Game Engine closure pass 2
Date: 2026-10-02

## Scope

This pass continues the Game Engine closure work after the first 2026-10-02 pass.
Primary references:

- DOS V1.2 `N3D-D-12.exe` / `N3D-D-12.exe.c`
- DOS V2.0 `N3D-E-20.EXE.c`
- project class/register and prior Win16/DOS event audits

The goal is to separate **static closure** from **runtime/pixel parity**. "100% STATIC"
below means that the relevant control-flow/state-machine needed for an implementation
is no longer an unknown for the named DOS scope. It does not claim pixel-perfect or
all-build runtime identity.

## 1. Game Loop — true scheduler located

The earlier large `70D6` block is not the whole outer scheduler. The actual timed
scheduler family is now anchored directly in two DOS builds.

### DOS V1.2

- `FUN_1000_BE8E` — fast simulation tick bundle
- `FUN_1000_BEE6` — outer timed scheduler
- `FUN_1000_BC74` — frame visibility/render-preparation pipeline
- `FUN_1000_6E7E` — active gameplay input/player-action handler

`FUN_1000_BE8E` calls, in order:

1. platform/driver tick helper
2. `1000:0A36` — paired-door/boundary delayed-state update
3. `1000:5CD8` — GUARD update loop
4. status/power-up timer update
5. player/view-state update
6. `1000:0E46` — moving map-object update
7. floor/contact hazard update
8. visual/status event update
9. HUD/status dirty update
10. state timer/update helper
11. an additional HUD refresh every eighth tick

`FUN_1000_BEE6` maintains two time domains and conditionally runs the fast tick.
Its main frame branch then calls, in order:

1. state/camera transition helper
2. `FUN_1000_BC74` — visibility/render preparation
3. HUD/status update
4. status/power-up application
5. `1000:0AE0` — moving door/boundary state machine
6. `1000:7FD8` — eight-slot projectile update
7. VGA present/page-flip synchronization (`15FA` or `15E0`)
8. `1000:6E7E` — active gameplay input/player-action handling

The scheduler also contains the slow-clock recovery/resync path after and 500-unit gap.

### DOS V2.0 cross-build confirmation

The same architecture survives with shifted addresses:

- `FUN_1000_C150` — fast simulation tick bundle
- `FUN_1000_C1A8` — outer timed scheduler
- `FUN_1000_BF36` — frame visibility/render-preparation pipeline
- `1000:70D6` — active gameplay input/player-action handler

The V2.0 fast tick contains the same recognizable subsystem sequence:
`0A40` door/boundary delayed update → `5F26` GUARD loop → `0E50` moving objects
plus status/hazard/UI helpers.

The V2.0 main frame branch contains:
`C0D8` → `BF36` → status helpers → `0AEA` moving door/boundary state machine
→ `8230` projectile update → VGA sync → `70D6` gameplay input/player-action handler.

### Closure decision

**Game Loop: STATIC CLOSED for the checked DOS scheduler core.**

The former blocker "true outer scheduler/order unknown" is removed. Remaining work is
runtime parity (pause/resume timing, slow-frame behavior, exact observable ordering in
edge cases), not an unknown scheduler architecture.

## 2. Switch / special-object logic

### SAFE and TRUNK

DOS V1.2 `FUN_1000_9026` is the common runtime handler.

- class `0x26` SAFE performs the six-character combination-input/validation path
- class `0x27` TRUNK uses the same state/opening path but skips the combination gate
- inactive state `0` transitions to `record[+1] + 2`
- successful activation plays event `0x32`
- already-open/intermediate states route through the existing display/state helpers

The class table confirms `0x26` = SAFE and `0x27` = TRUNK for supplied Episode 1
content.

### PUSH

The V1.2 push-object path at `1000:0DEE`:

- refuses to start when the object'with movement state is already active
- checks the destination/object blocking flag
- copies the player'with directional components into the push record
- sets movement countdown/state to `8`
- starts the associated effect/sound path

Per-tick moving-object behavior is already part of the fast simulation tick.

### Remote panel

Existing Win16 evidence plus the DOS menu/string set establish separate remote
commands:

- remote door open / close (`0x1E` / `0x1F`)
- remote cannon enable / disable (`0x20` / `0x21`)
- cancel

The cannon enable state is the saved event byte corresponding to the cannon attack
loop; this is separate from safe-combination progress.

### Closure decision

**Switch Logic: STATIC CLOSED for the supplied core interaction classes.**

Map-specific story triggers remain and scripting/content layer, not an unknown generic
switch dispatcher.

## 3. Warp, stairs, elevators and key gates

### Central transport dispatcher

DOS V1.2 `FUN_1000_13E6` dispatches wall classes `0x0D..0x2C` into explicit
families:

- `0x0D..0x14` → generic stair/dumb-waiter selector
- `0x15..0x18` → special mirror/pentagram transport family
- `0x19..0x1C` → color-key gate family
- `0x1D..0x24` → elevator floor selector
- `0x25..0x2C` → auxiliary selector family

After and successful selector it resolves the destination wall/cell, calls the adjacent
free-cell/facing helper, and converts cell coordinates to centered world coordinates:
`cell * 0x40 + 0x20`.

### Stairs / dumb waiter

`FUN_1000_EBAA` derives the class-local min/max wall IDs, enables/disables the
up/down choices, and returns:

- next selector: `+1`
- previous selector: `-1`
- cancel: `0`

### Elevator

`FUN_1000_EC4C`:

- computes the number of floors from the class-local min/max IDs
- supports at most ten floors
- marks the current floor
- applies and floor-availability mask
- returns the selected floor as an ID delta
- returns `0` on cancel

### Color-key gates

The raw DOS path at `0xEDF0` indexes the player key bitfield by
`wall_class - 0x19`, checks the corresponding possession bit and chooses the
success/failure feedback. The possession test itself does not decrement the bit.

### Mirror / pentagram transport

The raw DOS path around `0xA49C` checks the four pentagram bits and only takes the
special success transition when the required four-bit set is complete; missing pieces
select the failure/message path.

### Closure decision

**Teleports / stairs / elevators / key-gates: STATIC CLOSED for variants used by the
supplied DOS data.**

Unused class IDs remain data-driven rather than being assigned invented semantics.

## Updated Game Engine static matrix

| Module | Static status after pass 2 |
|---|---:|
| Architecture | 100% |
| Game Loop | **100% core DOS scheduler** |
| Player Movement | 100% core DOS |
| Collision | 100% core static mechanics |
| Door Engine | 100% DOS state machine |
| Secret Walls | 100% known core |
| Teleports | **100% supplied DOS variants** |
| USE Dispatcher | 100% DOS core |
| Switch Logic | **100% supplied core interaction classes** |
| Renderer | still requires exact render-output closure |
| Raycaster / visibility | still requires edge/tie and output closure |
| Clipping | still requires exact edge/tie closure |
| Projection | still requires fixed-point/edge/output closure |
| Resource Manager | still requires ownership/lifetime closure |

## Next highest-value closure target

The remaining blocker cluster is now the renderer family:

1. `Renderer`
2. `Raycaster / visibility`
3. `Clipping`
4. `Projection`

The next pass should statically lock the complete V2.0 `BF36` pipeline and its
callees, then pair it with Win16 vector/span/column-owner paths before doing
pixel-parity tests.