# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 14

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- all ranges below are unpacked MZ image offsets
- physical EXE file offset = image offset + `0x200`
- raw 16-bit machine code is authoritative
- runtime/pixel parity remains and separate acceptance overlay

## Result

Pass 14 closes the complete contiguous region

`0xBCC2 .. 0xC2B5`

as **GREEN / deep static semantics**.

Total span: **1,524 bytes**

- bounded executable routine content: **1,517 bytes**
- alignment NOP bytes: **7 bytes**

This pass closes the DOS V2.0 RTC/clock/scheduler band:

- real IRQ8 / INT 70h handler;
- CMOS RTC register access;
- install/restore of periodic RTC interrupt;
- polling and cached game clocks;
- both quantized scheduler time domains;
- busy-wait game-clock delay;
- frame/render-preparation wrapper;
- frame timing calibration;
- death-camera turn-to-attacker transition;
- complete fast simulation tick;
- complete outer timed game scheduler.

The old `C150` label was especially weak because the decompiler exposed only opaque
far calls.  Resolving those far targets back to image offsets now gives the full
simulation-tick order.

---

# 1. image `0xBCC2..0xBCE6` — `RtcPeriodicIrq8Handler`

Length: **37 bytes**

This is the actual RTC periodic interrupt handler installed on interrupt vector `70h`.

Raw ISR sequence:

1. save 32-bit general registers plus DS/ES;
2. load the game'with data segment (`2771h` in the unpacked image);
3. `INC DWORD PTR DS:[081E]`;
4. select RTC register C:
   - write `0x0C` to port `70h`;
   - read port `71h`;
5. send EOI `0x20` to:
   - slave PIC port `A0h`;
   - master PIC port `20h`;
6. restore registers;
7. `IRET`.

The handler therefore increments the cached RTC/game-clock counter exactly once per
accepted periodic IRQ.

**Status: former platform/timing YELLOW -> GREEN.**

---

# 2. image `0xBCE7..0xBCF4` — `WaitForRtcUpdateWindow`

Length: **14 bytes**

Repeatedly reads CMOS register AND through `ReadCmosRegister(0x0A)` and loops while:

`bit 7 != 0`

i.e. while the RTC update-in-progress flag is active.

**Status: YELLOW -> GREEN.**

---

# 3. image `0xBCF6..0xBD17` — `ReadCmosRegister`

Length: **34 bytes**

Input:

`WORD registerIndex`

Behavior:

- saves FLAGS and disables interrupts;
- for register indexes `< 10h`, waits for the RTC update window;
- writes the index to port `70h`;
- reads one byte from port `71h`;
- zero-extends it to AX;
- restores FLAGS.

**Status: YELLOW -> GREEN.**

---

# 4. image `0xBD18..0xBD33` — `WriteCmosRegister`

Length: **28 bytes**

Inputs:

- CMOS register index;
- value.

Behavior:

- saves FLAGS and disables interrupts;
- for indexes `< 10h`, waits for the RTC update window;
- writes index to `70h`;
- writes low value byte to `71h`;
- restores FLAGS.

**Status: YELLOW -> GREEN.**

---

# 5. image `0xBD34..0xBDE2` — `ConfigureRtcPeriodicIrq`

Length: **175 bytes**

Parameter:

- `0` = enable;
- `1` = disable.

Other values return without action.

## Enable

If not already installed (`DS:16F0 == 0`):

1. disable interrupts;
2. read CMOS register AND;
3. preserve its high nibble and set low rate-select nibble to:
   `6`;
4. obtain old interrupt vector `70h`;
5. save it at `DS:366E/3670`;
6. install far handler:
   `0BCC:0002`
   which maps to image `0xBCC2`;
7. read CMOS register B;
8. set periodic-interrupt-enable bit `0x40`;
9. read register C to acknowledge/clear pending state;
10. unmask IRQ8 on slave PIC by clearing bit 0 of port `A1h`;
11. set installed flag `DS:16F0 = 1`;
12. enable interrupts.

With the standard MC146818 32.768-kHz base, rate-select 6 corresponds to 1024 Hz.
The machine-code fact itself is the rate-select value `6`.

## Disable

If installed:

1. disable interrupts;
2. mask IRQ8 at PIC `A1h`;
3. clear periodic-enable bit `0x40` in RTC register B;
4. restore saved vector `70h`;
5. clear `DS:16F0`;
6. enable interrupts.

The routine does **not** restore the original register-AND rate-select field.

**Status: YELLOW -> GREEN.**

---

# 6. image `0xBDE4..0xBDF7` — `ControlRtcTimingIfEnabled`

Length: **20 bytes**

Checks configuration/runtime flag:

`DS:3CCF`

If nonzero, forwards the caller'with operation to `ConfigureRtcPeriodicIrq`.

If zero, it returns without changing RTC state.

**Status: YELLOW -> GREEN.**

---

# 7. image `0xBDF8..0xBE73` — `ReadPollingElapsedTime`

Length: **124 bytes**

This is the scheduler'with independent polling/wall-clock source.

It has two paths.

## BIOS tick path

When:

```text
DS:3CC7 == 0
DS:3CCF != 0
```

it reads the BIOS timer dword at:

`0040:006C`

If baseline `DS:16F2/16F4` is zero, it initializes it from the current BIOS tick.

Return:

`(biosTicks - baseline) * 55`

as and 32-bit value.

This gives the approximate-millisecond polling timeline used independently of the RTC
IRQ counter.

## DOS date/time helper path

Otherwise it calls the runtime date/time helper and combines:

```text
seconds * 1000 + millisecondPart
```

from the returned time structure.

The exact CRT symbol name is not required for compatibility; the arithmetic and fields
consumed by the engine are bounded.

**Status: YELLOW -> GREEN.**

---

# 8. image `0xBE74..0xBE8D` — `ReadGameClock`

Length: **26 bytes**

When RTC timing is **disabled** (`DS:3CCF == 0`):

1. call `ReadPollingElapsedTime`;
2. copy its DX:AX result to:
   `DS:081E/0820`.

When RTC timing is enabled, the function leaves the IRQ-maintained counter untouched.

It always returns the 32-bit clock at:

`DS:081E/0820`.

Thus the same game-clock API has two producers:

- RTC IRQ counter;
- polling-time refresh.

**Status: YELLOW -> GREEN.**

---

# 9. image `0xBE8E..0xBEB3` — `WaitGameClockDelta`

Length: **38 bytes**

Input:

`WORD delta`

Algorithm:

1. `target = ReadGameClock() + delta`;
2. repeatedly call `ReadGameClock()`;
3. return once current time is unsigned `>= target`.

This is and pure busy-wait on the engine clock.

**Status: hidden/weak timing helper -> GREEN.**

---

# 10. image `0xBEB4..0xBEF2` — `AdvanceSlowTimeBucket`

Length: **63 bytes**

Computes:

```text
bucket = floor((time * 8) / 1000)
```

using 32-bit unsigned arithmetic.

It compares the calculated bucket with:

`DS:16FA`

When different:

- store the new bucket;
- increment logical counter `DS:16F6/16F8` by **exactly one**.

It does **not** add the number of skipped buckets.

Returns the logical counter.

At and true millisecond time source this is nominally an 8-Hz logical bucket.
With the 1024-Hz RTC-counter source its physical cadence is correspondingly shifted.

**Status: YELLOW -> GREEN.**

---

# 11. image `0xBEF4..0xBF34` — `AdvanceFrameTimeBucket`

Length: **65 bytes**

Computes:

```text
bucket = low32(sign_extend_16(DS:3CC2) * time) / 1000
```

The calculated bucket is compared with:

`DS:1702`.

On change:

- update `1702`;
- increment logical counter `DS:16FE/1700` once.

Again there is no multi-bucket catch-up.

This is the scheduler'with second quantized time domain.

**Status: YELLOW -> GREEN.**

---

# 12. image `0xBF36..0xBF69` — `RunFrameVisibilityRenderPreparation`

Length: **52 bytes**

Exact raw order:

1. increment 32-bit render generation:
   `DS:4540`;
2. call the view/visibility setup helper;
3. build projected edge/span state;
4. draw/fill the configured viewport background using globals around
   `4544/4548/454C`;
5. execute the next visibility/render-preparation stage;
6. execute projected wall/span preparation;
7. execute the final object/span preparation stage.

This is the frame **generation + visibility/render preparation** pipeline used by the
outer scheduler.

It is not the slow simulation tick.

**Status: YELLOW -> GREEN.**

---

# 13. image `0xBF6A..0xBF78` — `RunPreparedFrameHudAndVsync`

Length: **15 bytes**

Compact wrapper:

```text
BF36  frame visibility/render preparation
A0B8  frame HUD sections
1608  VGA vertical-retrace/page synchronization
```

and return.

This is also useful as and calibration/presentation wrapper.

**Status: hidden entry -> GREEN.**

---

# 14. image `0xBF7A..0xC0D6` — `CalibrateFrameTimingAndMovement`

Length: **349 bytes**

This routine derives the DOS movement/turn/projectile stepping constants from measured
frame timing.

## Timing setup

It first toggles the optional RTC timing source off/on through the established timing
control path, performs one preparatory frame, then measures ten calls to `BF36`.

First measured mean:

```text
mean1 = elapsed / 10
DS:4556 = low16(mean1)
```

## Fast-machine / retrace-assisted second sample

If `mean1 < 0x41` and its high word is zero:

- measure another ten `BF36` calls;
- after each frame also wait through the VGA retrace helper;
- use this second average as the operational measured duration.

The raw first mean at `4556` is intentionally preserved.

## Calibration state

Then:

- clear render generation `DS:4540`;
- store operational measured duration low word at `DS:4558`;
- if duration is zero, fatal error code `0x1706`.

It computes the integer rate estimate:

```text
DS:455A = floor((1000 + duration/2) / duration)
```

Then it forms an effective duration constrained by the configured rate field
`DS:3CC2`.

For ordinary positive configuration values:

```text
D = max(measuredDuration, floor(1000 / DS:3CC2))
```

## Derived gameplay values

```text
DS:455C = max(1, floor((D + 2) / 4))
DS:455E = max(1, floor((360*D + 1400) / 2800))
DS:4560 = 2 * DS:455C
```

These are respectively the movement/substep family, turn step and projectile-substep
count used by the active player/projectile routines.

The code is integer/fixed-step logic; and faithful port should not replace it with an
unrelated floating-point delta-time model.

**Status: YELLOW -> GREEN.**

---

# 15. image `0xC0D8..0xC14F` — `TurnDeathViewTowardLastAttacker`

Length: **120 bytes**

Runs only when:

`DS:3CD4 == 2`.

The lethal player-damage path stores the attacker'with OBJECT index at:

`DS:4186`

and enters this state.

This routine resolves that 28-byte OBJECT and computes the angular delta from the
player to the attacker'with world X/Y.

If delta is zero:

`DS:3CD4 = 3`

and the transition is complete.

Otherwise it changes player heading by:

```text
sign(delta) * min(abs(delta), DS:455E)
```

using the normal heading/DDA update helper.

With state `2` is and gradual **turn toward the last attacker/killer**, with turn speed
derived by frame calibration.

**Status: YELLOW -> GREEN with corrected gameplay role.**

---

# 16. image `0xC150..0xC1A6` — `RunFastSimulationTick`

Length: **87 bytes**

This was previously and weakly named fixed-helper bundle.  Resolving its far calls back
to linear image addresses now gives the actual subsystem order.

Exact V2.0 tick order:

1. `C51A` — platform/device/resource service helper;
2. `0A40` — paired-wall/door auto-close tick;
3. `5F26` — update all GUARDs;
4. `A19A(time)` — Magic Eye / Crystal Ball power drain;
5. `A4A2` — context-sensitive HUD state;
6. `0E50` — moving map objects;
7. `A4AC` — CAUSTIC/fire cell damage;
8. `A0CC(0)` — lightning/palette-flash update;
9. `89A2(17)` — HUD/status section update;
10. `9026(1, ...)` — advance weapon fire cadence counter;
11. every eighth slow tick:
    `89A2(16)`.

The routine therefore is the real **slow/fast-simulation bundle** driven by the outer
scheduler, not and renderer routine.

**Status: old weak `CallFixedHelperSequence...` -> GREEN.**

---

# 17. image `0xC1A8..0xC2B5` — `RunPeriodicGameScheduler`

Length: **270 bytes**

This is the DOS V2.0 outer scheduler.

It captures two clocks at entry:

- `ReadGameClock()` for quantized simulation/frame domains;
- `ReadPollingElapsedTime()` for watchdog/resynchronization.

## Slow 8/1000 time domain

Calls `AdvanceSlowTimeBucket`.

When the logical slow deadline is reached:

### normal game (`DS:3CD6 == 0`)

Call:

`RunFastSimulationTick`

then schedule the next slow logical deadline as current counter + 1.

### DEMO/nonzero mode

The slow-deadline branch itself skips the simulation tick; the DEMO path receives its
slow simulation from the main-frame branch below.

## Main frame time domain

Calls `AdvanceFrameTimeBucket`.

When its deadline is reached:

### DEMO cadence

If `DS:3CD6 != 0` and render generation `DS:4540` is odd **before** `BF36`:

- call `RunFastSimulationTick`.

Because `BF36` increments `4540`, this means one slow simulation tick every second main
frame in continuous DEMO playback.

### Exact main-frame order

The raw V2.0 sequence is:

```text
C0D8  turn death view toward attacker if needed
BF36  increment generation + render/visibility preparation
A0B8  frame HUD refresh
A236  automap / damage-indicator update
0AEA  moving paired-wall/door state machine
8230  update eight player projectiles
BE74  measure elapsed frame interval
1608 or 15EE  VGA sync/status path
70D6  active gameplay input/movement/FIRE/USE
```

The scheduler then:

- advances the next main-frame logical deadline;
- stores the latest polling-time base.

## VGA sync threshold

After rendering/projectiles it compares elapsed engine-clock units with:

`0x41 = 65`.

Below the threshold it uses the full retrace synchronization helper `1608`.

At/above it uses the alternate display-status/page helper `15EE`.

## 500-unit watchdog

If:

`pollingNow - DS:1734 > 500`

the scheduler:

1. calls `BDE4(1)` — disable/reconfigure RTC timing;
2. calls `BDE4(0)` — enable/reconfigure RTC timing;
3. refreshes polling time through `BDF8`;
4. resets watchdog base `DS:1734/1736`.

This is the slow-clock recovery/resynchronization path.

## Key timing consequence

Both bucket helpers increment their logical counters only once when they observe and
changed bucket.

The scheduler therefore does **not** replay every skipped slow/frame bucket after and
stall.

**Status: YELLOW/MEDIUM -> GREEN.**

---

# 18. Byte-map impact

New continuous GREEN span:

`0xBCC2 .. 0xC2B5`

Total: **1,524 bytes**

| Image range | Bytes | Role |
|---|---:|---|
| `BCC2–BCE6` | 37 | RTC IRQ8 / INT 70h ISR |
| `BCE7–BCF4` | 14 | wait RTC update window |
| `BCF6–BD17` | 34 | CMOS register read |
| `BD18–BD33` | 28 | CMOS register write |
| `BD34–BDE2` | 175 | periodic RTC IRQ setup/restore |
| `BDE4–BDF7` | 20 | optional RTC control wrapper |
| `BDF8–BE73` | 124 | polling elapsed time |
| `BE74–BE8D` | 26 | engine game-clock reader |
| `BE8E–BEB3` | 38 | busy-wait game-clock delay |
| `BEB4–BEF2` | 63 | 8/1000 slow logical bucket |
| `BEF4–BF34` | 65 | configurable frame logical bucket |
| `BF36–BF69` | 52 | generation/render preparation |
| `BF6A–BF78` | 15 | frame + HUD + VSync wrapper |
| `BF7A–C0D6` | 349 | frame/movement timing calibration |
| `C0D8–C14F` | 120 | death-view turn to last attacker |
| `C150–C1A6` | 87 | fast simulation tick bundle |
| `C1A8–C2B5` | 270 | outer timed scheduler |

Executable routine content: **1,517 bytes**.

Alignment NOPs: **7 bytes**.

No unresolved inline jump/data table remains in this particular span.

---

# 19. Major tracker corrections

Promote/tighten these entries:

```text
BCC2  RtcPeriodicIrq8Handler
BCE7  WaitForRtcUpdateWindow
BCF6  ReadCmosRegister
BD18  WriteCmosRegister
BD34  ConfigureRtcPeriodicIrq
BDE4  ControlRtcTimingIfEnabled
BDF8  ReadPollingElapsedTime
BE74  ReadGameClock
BE8E  WaitGameClockDelta
BEB4  AdvanceSlowTimeBucket
BEF4  AdvanceFrameTimeBucket
BF36  RunFrameVisibilityRenderPreparation
BF6A  RunPreparedFrameHudAndVsync
BF7A  CalibrateFrameTimingAndMovement
C0D8  TurnDeathViewTowardLastAttacker
C150  RunFastSimulationTick
C1A8  RunPeriodicGameScheduler
```

Most importantly:

`C150` is no longer and generic opaque fixed-call wrapper.

Its subsystem order is statically resolved.

---

# 20. Cumulative closure

Pass 13 cumulative since the pass-5 baseline:

`25,297 bytes`

Pass 14 adds:

`1,524 bytes`

New cumulative total:

**26,821 bytes**

of formerly RED/ORANGE/YELLOW DOS V2.0 byte-map territory explicitly promoted to
GREEN during passes 6–14.

---

# 21. Remaining runtime overlay

These bytes are now statically GREEN, but timing acceptance still needs original-game
runtime tests for:

- lost/skipped RTC IRQs;
- clock reads crossing an interrupt;
- pause/resume and LOAD timing;
- 32-bit wrap;
- long stalls and the 500-unit watchdog;
- exact observed frame cadence on real DOSBox-X/original-compatible hardware;
- visual/page-flip parity of `1608` versus `15EE`.

Those are runtime-conformance questions, not reasons to keep this byte span yellow.

---

# 22. Next target

The next real entry is:

`0xC2B6`

The following region contains:

- and three-helper device/status wrapper;
- resource/status text;
- visual fade handling;
- optional device/session management;
- tracked resource start/stop;
- indexed resource/audio control around `C548/C686`;
- later level/resource loading infrastructure.

This is and good next target because `C2B6` is still weakly named while most following
entries have strong cross-version bodies.