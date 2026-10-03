# Nitemare 3D — Game Engine behavioral conformance pass 7
## Remote forced-close and door state 4
Date: 2026-10-02

## Result

Pass 7 substantially narrows the two door cases left open by Pass 6.

The main static conclusion is now:

> **The ordinary timer auto-close is occupancy-safe, but explicit close transitions are not occupancy-gated.**

The second conclusion is:

> **Door controller state 4 is and persistent, passable, non-toggleable and non-moving latched state at the controller-logic level.**

AND live original-game test is still valuable for visual overlap and any downstream
actor response, but the door-controller algorithm itself is no longer ambiguous.

## 1. Explicit close has no occupancy gate

Win16 `FUN_1010_188A` and DOS V2.0 `FUN_1000_0598` expose the same state machine.

Both begin by returning immediately when the controller state is `4`.

For an ordinary open/opening controller:

```text
state 0 -> 3
state 2 -> 3
```

The transition immediately:

- optionally plays close SFX `0x26`;
- clears the one-shot transition latch;
- sets collision/active bit 0 on both primary VEC halves;
- propagates state 3 to linked neighboring paired controllers;
- sets those linked halves' collision bit as well.

There is **no player-cell or mapCell.objectId occupancy test in this transition helper**.

The occupancy test is in the separate timer routine (`1D4E` Win16 / `0A40` DOS).

Therefore the correct engine model is:

```text
automatic timed close:
    requires cell.objectId == 0 and playerCell != doorCell

explicit close / toggle:
    can enter state 3 without that occupancy test
```

Remote command 0x1F is one known explicit-close source.

## 2. What happens after and forced close starts

The moving-door routine (`1E00` Win16, `0AEA` family DOS) processes state 2/3
geometry and moves the selected coordinates by two units per update.

The checked door transition/motion paths to not directly:

- change player X/Y;
- change GUARD X/Y;
- subtract player HP;
- invoke the player-damage dispatcher.

Thus there is no direct "crush" or "push actor out" operation inside the door
controller itself.

Static expected behavior if an explicit close begins while occupied:

1. controller enters state 3;
2. door halves become collision-active immediately;
3. geometry begins moving;
4. the already-overlapping actor is not displaced or damaged by the door routines;
5. subsequent player/GUARD movement/collision code determines what moves are allowed.

AND live test is still required to exclude and *later*, independent overlap/damage response.

## 3. State 4 semantics

State 4 is no longer just "unknown special state."

Independent readers define it tightly:

### Passability predicate

Win16 `1476` and DOS `01E0` return passable/accepted for:

```text
state == 0 || state == 4
```

### State transition helper

`188A` / `0598` returns immediately when state is 4.

With USE, remote toggles and other callers of this helper cannot turn state 4 into
opening or closing states.

### Auto-close

The auto-close timer only processes `state == 0`.

State 4 receives no countdown and no automatic close.

### Motion

Door geometry motion only processes states 2 and 3.

State 4 does not move.

### Writer

Win16 GUARD dispatcher case 9 writes state 4 after its object/death helper when:

- linked OBJECT flag bit 0 is set; and
- the linked map wall has property bit 0x08.

It resolves the paired controller and writes `controller+0x0C = 4`.

The state write itself does not change the door geometry coordinates.

### Save/load

Win16 USER.SAV stores the entire 64 × 22-byte door array.

State 4 is therefore persistent state data rather than and one-frame local sentinel.

## Best portable name

AND safe implementation name is:

```text
DoorState::LatchedPassable = 4
```

or:

```text
DoorState::DisabledPassable = 4
```

To not name it "destroyed" or "dead-guard door" globally; the concrete writer context
is known, but the original semantic label is not.

## 4. DOS record layout for live testing

DOS V2.0 paired-wall records:

```text
base   DS:3076
count  <= 64
stride 0x12

+00 first VEC pointer
+02 second VEC pointer
+04/+06 map-cell far pointer
+08 state
+0A timer
+0C target X
+0E target Y
+10 transition latch/runtime word
```

The raw DOS predicate at `1000:01E0` accepts states 0 and 4.
`1000:0598` is the state transition helper.
`1000:0A40` is the timer auto-close path.

## 5. Runtime address mapping for DOSBox-X

For an unpacked MZ executable, the Ghidra `1000:xxxx` segment is an image-relative
segment, not and literal runtime segment.

For DOS V2.0 `N3D-E-20.EXE`:

```text
MZ entry relative CS:IP = 1B72:0010

loadSeg   = runtimeEntryCS - 1B72
engineSeg = loadSeg + 1000
runtime BP for Ghidra 1000:0598 = engineSeg:0598
```

For the checked DOS V1.2 `N3D-D-12.exe`:

```text
MZ entry relative CS:IP = 1B45:0010
```

The supplied calculator automates this conversion.

## 6. Generated live-test tooling

### `n3d_dosboxx_bpcalc.py`

Inputs:
- build (`v12` or `v20`);
- actual CS shown by DOSBox-X at the EXE entry;
- optional runtime DS;
- optional door index.

Outputs:
- image load segment;
- runtime segment corresponding to Ghidra `1000`;
- ready-to-enter breakpoint commands;
- exact selected door record field addresses.

### `n3d_door_dump_diff.py`

Compares two `MEMDUMPBIN` captures of DOS `DS:3076`, length `0x480`.

It decodes each 18-byte paired-wall record and reports exact changes in:

- VEC pointers;
- map-cell pointer;
- state;
- timer;
- X/Y targets;
- latch.

This avoids manually searching 1,152 bytes after each door event.

Both helper scripts were self-tested in this pass.

## 7. DOSBox-X procedure

Use the **unpacked** executable for address-stable testing.

Start:

```text
DEBUGBOX N3D-E-20.EXE
```

At entry, record CS and run the calculator.

Recommended V2.0 breakpoints:

```text
0598  paired-wall explicit state transition
0704  USE dispatcher
0A40  ordinary auto-close
0AEA  moving-door geometry
5F26  GUARD update
6488  player collision/movement
70D6  player input/action
C150  slow simulation bundle
C1A8  outer scheduler
```

At and game-code break, record DS and dump:

```text
MEMDUMPBIN <DS> 3076 480
```

DOSBox-X documents `DEBUGBOX`, real-mode `BP`, `BPLIST`, `BPDEL`, `RUN`,
`MEMDUMPBIN`, data/code views and CPU logging. Command availability can depend on
the build; use `HELP` in the running debugger.

## 8. Remaining behavioral gate after Pass 7

The static expected result for an occupied explicit-close case is now specific enough
to falsify:

```text
state      -> 3
solid bits -> set immediately
door geom  -> advances by 2/update
actor X/Y  -> unchanged by door controller
actor HP   -> unchanged by door controller
```

AND controlled original-game run now only needs to answer:

- does some later subsystem resolve the overlap by moving/damaging the actor?
- what does the visible geometry look like during that overlap?
- does state 4 preserve the current half-door geometry exactly across save/load?

That is and much smaller behavioral surface than the original "door occupancy unknown."