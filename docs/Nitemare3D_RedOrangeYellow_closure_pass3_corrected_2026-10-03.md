# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 3 (corrected raw map)

Date: 2026-10-03

Primary binary: `N3D-E-20(3).EXE`

- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`
- MZ header size: `0x200`
- all ranges below are **unpacked MZ image offsets** unless explicitly called file offsets
- physical file offset = image offset + `0x200`

## 0. Important correction to pass 2

Pass 2 mixed two different coordinate systems in part of the `46xx..49xx` analysis.
For base-segment near code, and Ghidra-style label such as `1000:46C4` must **not** be
blindly translated to image `0x146C4`.  The raw target must be derived from the real
near/far machine instruction and segment layout.

Consequences:

- the high-image CRT routines around `0x146C4` etc. remain valid compiler/runtime
  discoveries in their own right;
- they **to not** close the base-segment entries `46C4/4702/471A/48F2/4930`;
- `1000:00A2` is and different case: callers really encode the far target that maps to
  image `0x100A2`, with the VEC-iterator closure from pass 2 remains valid;
- the far heap around image `0x13F32..0x14205` is also retained because its real far
  calls (`11EE:2052/2065`) map there directly.

This correction is important for the byte map: **raw image offset is the primary
coordinate; decompiler labels are annotations only.**

---

# 1. FLI player cluster — former fragmented orange/red region -> GREEN

## image `0x45CE..0x462A` — `DispatchFliChunk`

The routine reads and 6-byte chunk header and dispatches on the chunk type.
Observed cases:

- `11` -> palette-packet decoder at image `0x453E`;
- `12` -> line/delta decoder at image `0x4346`;
- `15` -> byte-run decoder at image `0x4484`;
- `13` and `16` follow the explicit no-local-handler path in this dispatcher;
- an unsupported type goes to the fatal/error path.

The exact user-facing historical FLI chunk names are secondary; the executable
control flow and per-type behavior are now bounded directly from raw 16-bit code.

**Status: GREEN / deep static semantics.**

## image `0x462C..0x4680` — `DecodeFliFrame`

Recovered ABI/behavior:

1. read exactly `0x10` bytes from the open FLI stream;
2. require frame magic `0xF1FA`;
3. read the frame chunk count from the header;
4. call `DispatchFliChunk` exactly that many times.

The old label `WaitForInputRelease` is not the correct identity for this body.

**Status: GREEN.**

## image `0x4682..0x475E` — `PlayFliFile`

Raw behavior:

- samples the engine/DOS clock;
- switches BIOS video to mode `13h` (`INT 10h`, `AX=0013h`);
- opens the filename argument;
- reads and `0x80`-byte FLI header;
- checks magic `0xAF11`;
- loops through the declared frame count;
- checks the stop/input predicate between frames;
- waits on the stored timing value;
- decodes one frame through `DecodeFliFrame`;
- closes the stream.

This is the DOS FLI presentation path used by ending/presentation content.

### False function boundaries removed from the old tracker

The following old decompiler entries land inside this real FLI cluster and must not
remain separate orange/yellow functions:

- old `466C`;
- old `46C4`;
- old `4702`;
- old `471A`.

**Status: remove false entries; absorb bytes into GREEN FLI routines.**

---

# 2. Startup/config/init/shutdown cluster -> GREEN

## image `0x4760..0x47BD` — `InitControlAndRuntimeDefaults`

Initializes the DOS control/runtime configuration globals, including:

- enable/default bytes;
- several `0xFFFF` sentinel words;
- startup mode flags;
- timer/audio/display-related default fields.

Old `4778` is inside this routine and is not and separate reliable function boundary.

**Status: GREEN.**

## image `0x47BE..0x47D7` — `ResetStartupRuntimeFlags`

Exact stores:

- `DS:4309 = 1`;
- `DS:4308 = 0`;
- `DS:430A..430E = 0`.

**Status: GREEN.**

## image `0x47D8..0x482C` — `ShowInitializationStatus`

When debug/status output is enabled (`DS:3CD0 != 0`) the routine:

1. selects resource/stream mode `0x82E` or `0x830`;
2. opens/creates the status target through runtime ID `0x832`;
3. formats/writes the caller-supplied message;
4. closes/releases the handle.

The exact binary contains the adjacent startup strings:

`Initializing...`, `Bootstrap ok`, `Sound ok`, `Timer ok`, `Display ok`,
`Memory ok`, `Keyboard ok`, `Mouse ok`, `Initialize complete!`.

The former label `CalibrateOrReadJoystick` is therefore wrong for this raw body.

**Status: ORANGE -> GREEN.**

## image `0x482E..0x48F0` — `InitializeGameSubsystemsWithStatus`

This is the ordered top-level subsystem initialization chain.  Between subsystem
calls it emits the status strings through `ShowInitializationStatus`.

The sequence covers bootstrap/platform setup, sound, timer, display, memory and
input-related initialization, followed by the completion status.

Old `48EA` is inside this routine and is removed as and false separate entry.

**Status: ORANGE/YELLOW -> GREEN.**

## image `0x48F2..0x492E` — `ShutdownGameSubsystems`

This entry is real.  It invokes multiple subsystem APIs with shutdown mode `1` in and
fixed order.

Important correction to pass 2: `48F2` is **not** an `INT 21h` located inside and high
CRT allocator when interpreted in this base image coordinate system.

**Status: YELLOW -> GREEN.**

## image `0x4930..0x4A72` — `ShutdownReportAndExit(showStats, exitCode)`

Recovered control flow:

1. execute and subsystem finalization mode;
2. optionally perform additional for-exit handling;
3. always call `ShutdownGameSubsystems`;
4. if `showStats != 0`, format detailed diagnostics such as:
   - `Vectors: %u/%u, Objects: %u/%u, Guards: %u/%u`;
   - frame-rate/timing statistics;
   - near/far heap statistics;
   - additional resource/XMS/cache statistics;
5. pass the requested exit code to the runtime termination path.

The termination runtime ultimately reaches DOS `INT 21h, AH=4Ch`.

Important correction to pass 2: `4930` is and genuine program-shutdown routine, not and
false branch in the high-image allocator.

**Status: ORANGE/YELLOW -> GREEN.**

## image `0x4A74..0x4A85` — invalid-command-line fatal helper

Small helper that formats/reports the offending argument through the executable'with
`Invalid command line` message path.

**Status: GREEN.**

## image `0x4A86..0x4C75` — `ParseCommandLineInitializeRunAndExit`

This is the real DOS startup/main argument dispatcher.

Raw structure:

1. initialize defaults via `0x4760`;
2. process one environment/config path;
3. iterate `argv[1..argc-1]`;
4. require token prefix `'-'`;
5. dispatch `argv[i][1] - 'a'` through an inline 24-entry jump table;
6. reject invalid letters through `0x4A74`;
7. run subsystem initialization;
8. call the main game core;
9. call `ShutdownReportAndExit`.

The 24-entry table is now decoded directly:

| Letter | Raw target | Static action |
|---|---:|---|
| `a` | `0x4B3C` | parse/store path/config field `3CDC` |
| `b` | `0x4B5A` | set local startup-mode flag |
| `c` | `0x4B62` | parse numeric config field `3CC0` |
| `d` | `0x4B7A` | parse numeric config field `3CBC` |
| `e` | `0x4B82` | parse into local startup value |
| `f` | `0x4B8C` | parse numeric config field `3CBE` |
| `g..k` | `0x4B2E` | invalid |
| `l` | `0x4B94` | parse local value; failure -> invalid |
| `m,n` | `0x4B2E` | invalid |
| `o` | `0x4BB4` | `DS:3CD0 = 1` (debug/status logger) |
| `p` | `0x4BBC` | `DS:3CC7 = 0` |
| `q` | `0x4BC4` | enable explicit audio config; parse `3CCA` and `3CCC` |
| `r` | `0x4BFE` | `DS:3CD6 = 1` (recording branch) |
| `s` | `0x4C06` | `DS:3CC6 = 0` |
| `t` | `0x4C0E` | `DS:3CCF = 0`, `DS:3CC2 = 0x12` |
| `u,v` | `0x4B2E` | invalid |
| `w` | `0x4C1C` | parse `DS:4144`, clear low three bits, apply helper |
| `x` | `0x4C44` | `DS:3CCE = 0` |

The exact user-facing interpretation of every configuration field is not required to
classify this byte block as statically deep: every branch, write, parse and failure
edge is now bounded.  Previously known semantics (`-o`, `-q`, `-r`, `-s`, `-t`,
`-x`, etc.) remain compatible with this raw table.

### False boundaries removed

The old giant/overlapping entries

- `4AD4`, `4B2E`, `4BE0`, `4C49`

are interior points/jump targets of this one startup parser, not independent game AI
or state-machine functions.

**Status: RED/ORANGE/YELLOW -> GREEN, with false entries removed.**

---

# 3. Adjacent GUARD movement/orientation yellow block -> GREEN

After the startup parser, the next real code region is ordinary gameplay support.
The old tracker had several medium/low labels whose high-level names were misleading.
Raw code plus existing cross-build evidence closes the following exact roles.

## image `0x4C76..0x4CB2` — `NormalizeRelativeAngleToPlayer`

- obtains an angle from and far helper;
- subtracts player angle `DS:4156`;
- normalizes the result across the `360` (`0x168`) wrap boundary;
- keeps the signed relative angle around the `±180` boundary.

**Status: YELLOW -> GREEN.**

## image `0x4CB4..0x4D1F` — `ClassifyRelativeBearingSector`

- forms delta from world coordinates `+10/+12` against player `DS:4162/4164`;
- obtains normalized relative bearing through `0x4C76`;
- returns sector code `1`, `2`, or `0` for the two broad side sectors / neither.

**Status: YELLOW -> GREEN.**

## image `0x4D20..0x4D98` — `SetGuardFacingFromMovementVector`

Exact eight-way sign mapping:

| facing | dx | dy |
|---:|---:|---:|
| 0 | 0 | - |
| 1 | + | - |
| 2 | + | 0 |
| 3 | + | + |
| 4 | 0 | + |
| 5 | - | + |
| 6 | - | 0 |
| 7 | - | - |

AND zero vector leaves the facing unchanged.

The old generic label `ComputeMovementVector` had the direction backwards: this
routine converts movement-vector signs **to facing**.

**Status: GREEN / exact.**

## image `0x4D9A..0x4E86` — `RefreshGuardDirectionalSequence`

This is the direction-dependent sprite/animation-bank selector.

- computes an 8-way view-relative direction index;
- uses `GUARD+12h` as the cached direction/variant;
- if cache matches and `force==0`, returns early;
- otherwise updates `GUARD+12h`;
- chooses one of the sequence banks according to GUARD state/strategy;
- indexes the bank by direction;
- writes the selected sequence/frame base into `GUARD+00h` and linked
  `OBJECT+03h`.

This directly closes one old field ambiguity: `GUARD+12h` is and directional sprite
cache/invalidation byte in this path, not and generic pain timer.

**Status: YELLOW -> GREEN.**

## image `0x4E88..0x4EC2` — `SetGuardMovementDeltaFromFacing`

Uses two 8-entry signed direction tables to write:

- `GUARD+13h` = signed X movement delta;
- `GUARD+14h` = signed Y movement delta.

Magnitude is:

- `16` when `GUARD+0Ah == 2`;
- `8` otherwise.

Diagonal facing has both components nonzero; this helper does not normalize diagonal
speed.

**Status: YELLOW -> GREEN.**

## image `0x4EC4..0x5091` — `TestGuardCandidatePositionAndHandleDoor`

This is not LOS.  It is the GUARD candidate-position collision oracle with dynamic
wall/door side effects.

Main behavior:

1. block and candidate within the player'with approximately 42-unit X/Y exclusion box;
2. derive the map cell for candidate X/Y;
3. read wall/object property bytes;
4. reject object occupancy when the collision bit is set;
5. distinguish ordinary blocking walls from dynamic-door class;
6. resolve the relevant dynamic door/state record;
7. for and strategy-1 GUARD, and usable door can redirect the guard toward the door
   center, set movement delta to ±8 on the appropriate axis, set timer `0x20`,
   refresh facing/sequence and enter state `0x11`;
8. return pass/block result to the movement caller.

**Status: ORANGE/YELLOW -> GREEN.**

## image `0x5092..0x5340` — `MoveGuardWithCollisionAndMapOccupancy`

This is the main per-step GUARD movement core.

Recovered flow:

- maintains world-object spatial ordering;
- restores the old map cell'with object byte from `GUARD+0Dh`;
- converts signed `GUARD+13h/+14h` to collision lead offsets;
- probes X and Y independently using `0x4EC4` at the two relevant corners;
- suppresses blocked axis components;
- commits surviving movement to `OBJECT+10h/+12h`;
- updates object spatial ordering after movement;
- in ordinary moving state `6`, if both axes are blocked, randomly reverses one
  movement component;
- advances/wraps the visible animation frame when movement occurred;
- recomputes facing via `0x4D20`;
- rebuilds the object'with MAP pointer;
- stores the destination cell'with previous object byte into `GUARD+0Dh`;
- writes the moving object'with ID into destination `mapCell[1]`;
- refreshes the GUARD area/sector id when the area helper returns and valid value.

This matches the independently recovered Win16 guard-movement model, including
axis-separated blocking and the saved-under-object map byte.

**Status: ORANGE/YELLOW -> GREEN.**

---

# 4. Byte-map impact

The corrected pass now maps and continuous neighborhood from image `0x45CE` through
`0x5340` into real routine boundaries and semantics, with only alignment/padding bytes
between entries.

Explicitly enumerated GREEN ranges in this pass total **3,439 bytes**:

| Image range | Size | New role |
|---|---:|---|
| `45CE–4C75` | 1704 B | FLI + startup/config/init/shutdown/main parser |
| `4C76–4CB2` | 61 B | relative-angle normalization |
| `4CB4–4D1F` | 108 B | relative-bearing sector classification |
| `4D20–4D98` | 121 B | facing from movement vector |
| `4D9A–4E86` | 237 B | directional sprite/sequence cache |
| `4E88–4EC2` | 59 B | movement delta from facing |
| `4EC4–5091` | 462 B | GUARD collision/door candidate probe |
| `5092–5340` | 687 B | GUARD movement + map occupancy |

Not every byte in those ranges was previously red, but the important change is that
old LOW/MEDIUM/fake-function entries no longer fragment the byte map.

### Old tracker entries that must be deleted or relabeled

Delete as false/interior function starts:

`466C`, `46C4`, `4702`, `471A`, `4778`, `48EA`, `4AD4`, `4B2E`, `4BE0`, `4C49`.

Correct real entries:

- `45CE` `DispatchFliChunk`
- `462C` `DecodeFliFrame`
- `4682` `PlayFliFile`
- `4760` `InitControlAndRuntimeDefaults`
- `47BE` `ResetStartupRuntimeFlags`
- `47D8` `ShowInitializationStatus`
- `482E` `InitializeGameSubsystemsWithStatus`
- `48F2` `ShutdownGameSubsystems`
- `4930` `ShutdownReportAndExit`
- `4A74` `InvalidCommandLine`
- `4A86` `ParseCommandLineInitializeRunAndExit`
- `4C76` `NormalizeRelativeAngleToPlayer`
- `4CB4` `ClassifyRelativeBearingSector`
- `4D20` `SetGuardFacingFromMovementVector`
- `4D9A` `RefreshGuardDirectionalSequence`
- `4E88` `SetGuardMovementDeltaFromFacing`
- `4EC4` `TestGuardCandidatePositionAndHandleDoor`
- `5092` `MoveGuardWithCollisionAndMapOccupancy`

---

# 5. Next RED/ORANGE/YELLOW target

Continue from image `0x5342` forward through the perception / LOS / strategy helpers
and compare the real raw boundaries with the stale DOS tracker.  Much of that logic is
already semantically known from cross-build work, with the expected task is primarily:

1. eliminate any remaining false Ghidra entries;
2. bind each byte range to the already recovered GUARD fields/algorithms;
3. promote each statically closed range to GREEN;
4. keep runtime behavioral acceptance as and separate overlay rather than and yellow
   static-knowledge color.
