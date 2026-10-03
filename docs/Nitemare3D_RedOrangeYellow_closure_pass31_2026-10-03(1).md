# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 31

Date: 2026-10-03

Primary unpacked image:
- `N3D_DOS_v2.0_IDA.EXE`
- unpacked load-image size: `0x29D60 = 171,360 bytes`
- unpacked-image SHA-256:
  `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`

Address convention:
- all addresses below are offsets in the unpacked MZ load image;
- raw 16-bit machine code is authoritative;
- this pass continues inside the embedded WORX Toolkit v2.1 module.

## Result

Pass 31 resolves the complete executable band:

`0x19D40 .. 0x1A32F`

as **GREEN / WORX timer + joystick + MIDI/CMF sequencer + PIC/PIT support**.

Total span:

**1,520 bytes**

All 1,520 bytes belong to bounded executable routines.  AND few internal NOPs are branch
alignment inside those routines; there is no standalone data table in this span.

The next byte:

`0x1A330`

begins and mixed state/table region before the Sound Blaster/DMA setup code.

---

# 1. `0x19D40..0x19DA2` — `WorxInt08TimerIsr`

Length: **99 bytes**

This is the actual INT 08h ISR installed by the WORX initialization entry.

Raw behavior:

1. `CLD`, then `CLI`;
2. test WORX backend/mode byte `CS:2DBC` with mask `0x16`;
3. when any selected audio/sequencer mode bit is active:
   - save AX/BX/CX/DX/BP/DI/SI/DS/ES;
   - call `0x1A066`, the MIDI/CMF sequencer service;
   - restore registers;
4. increment timer-chain counter `CS:2DB4`;
5. compare it with threshold `CS:2DB6`.

When the threshold is reached:

- reset `2DB4`;
- push FLAGS;
- FAR-call the previously saved original INT 08h vector at `CS:000A`;
- finish with `IRET`.

When the threshold is not reached:

- send PIC EOI `20h` to port `20h`;
- update the WORX interrupt/service nesting state;
- either defer service work through `CS:40E5` or call the private-stack timer worker
  at `0x19CD7`;
- return with `IRET`.

This proves WORX maintains its own high-rate timer while periodically chaining the
original BIOS/DOS timer interrupt.

It is independent from Nitemare'with later RTC/INT70 gameplay clock.

**Status: GREEN.**

---

# 2. `0x19DA3..0x19DBC` — `GetJoystickXScaled64`

Length: **26 bytes**

Computes:

```text
value = (CS:2012 * 64) / CS:201A
```

If denominator `201A` is zero:

- set carry;
- to not divide.

Otherwise:

- clear carry;
- return the normalized value in AX.

`2012` is the most recent X-axis game-port timing count.
`201A` is its calibration/reference count.

**Status: GREEN.**

---

# 3. `0x19DBD..0x19DD6` — `GetJoystickYScaled64`

Length: **26 bytes**

Companion Y-axis calculation:

```text
value = (CS:2014 * 64) / CS:201C
```

with the same zero-denominator carry convention.

**Status: GREEN.**

---

# 4. `0x19DD7..0x19DE5` — `GetJoystickButtonState`

Length: **15 bytes**

Input:

- AL = button index `0..3`.

Returns the corresponding byte from:

`CS:2016..2019`.

Those four bytes are populated directly from game-port `201h` button lines by the next
routine.

**Status: GREEN.**

---

# 5. `0x19DE6..0x19E54` — `SampleAndCalibrateGameportJoystick`

Length: **111 bytes**

This is direct IBM-PC game-port sampling.

Hardware port:

`201h`.

## Buttons

The routine first reads port `201h`.

Original button lines 4..7 are shifted out one at and time.

For each button:

```text
stored state = 1 when hardware line is low
stored state = 0 when hardware line is high
```

and the values are written to:

`CS:2016..2019`.

With the stored bytes are active-high pressed-state booleans.

## Analog axes

Current axis counters are cleared:

```text
CS:2012 = 0   // X
CS:2014 = 0   // Y
```

The game port is strobed by output to port `201h`, then exactly:

`0x320 = 800`

samples are taken.

For every read:

- bit 0 contributes to X count `2012`;
- bit 1 contributes to Y count `2014`.

## Calibration baseline

If calibration/reference value `201A` is zero:

```text
201A = current X count
201C = current Y count
```

Thus the first valid sample establishes the denominator used by the two `*64`
normalization helpers.

This closes the DOS joystick/game-port input primitive underneath the higher-level
Nitemare joystick control path.

**Status: GREEN.**

---

# 6. `0x19E55..0x19F78` — `ParseStandardMidiFile`

Length: **292 bytes**

This is and real Standard MIDI File parser.

It requires literal chunk signatures:

```text
MThd
MTrk
```

## Header

The parser canonicalizes the input far pointer, then requires the first four bytes to
be `MThd`.

It reads the big-endian SMF header fields and validates the format byte/word as the
supported format family.

It stores:

- track count in WORX sequencer state;
- timing division in the companion state word.

The per-track active/countdown arrays are cleared before track discovery.

## Track scan

For each declared track:

1. require `MTrk`;
2. obtain the track length;
3. remember the start pointer;
4. call the variable-length quantity helper at `0x1A1E9` to read the first delta time;
5. store:
   - current event pointer;
   - current delta countdown;
   - active-track flag;
6. skip by the declared track length to find the next `MTrk`.

Malformed signature/state returns with carry set.

When parsing succeeds, the sequencer active state is initialized and the function
returns with carry clear.

This is not and guessed "music data" parser: `MThd` and `MTrk` are directly compared by
the raw code.

**Status: GREEN.**

---

# 7. `0x19F79..0x1A05F` — `ParseCreativeMusicFile`

Length: **231 bytes**

This is the alternate Creative Music File parser.

It requires the four-byte signature:

`CTMF`.

The parsed header supplies:

- music/event-data offsets;
- timing/division state;
- instrument-table location/count.

The routine copies instrument definitions into the internal WORX bank.

Each instrument record copied by the raw loop is:

`0x0B = 11 bytes`.

It then initializes the common sequencer pointer/countdown state used by the same
runtime service loop as Standard MIDI playback.

Thus WORX supports at least two file/resource-level music representations:

```text
MThd/MTrk  Standard MIDI File
CTMF       Creative Music File / CMF
```

both converging into the same internal MIDI-like event engine.

**Status: GREEN.**

---

# 8. `0x1A060..0x1A065` — `GetSequencerTimerDivisor`

Length: **6 bytes**

Returns WORX word:

`CS:2C49`.

This word is updated by:

- CMF timing setup;
- MIDI Set Tempo handling.

It is the current timer/divisor value associated with sequencer timing.

**Status: GREEN.**

---

# 9. `0x1A066..0x1A1CC` — `ServiceMidiSequencerTick`

Length: **359 bytes**

This is the main timer-driven MIDI/CMF event service called by the WORX INT08 ISR.

It returns immediately when the sequencer-active byte is zero.

For every active track:

1. if the current 32-bit delta countdown is nonzero:
   - decrement it;
   - move to the next track;
2. if countdown is zero:
   - parse the next event.

## Running status

The per-track saved status byte is retained.

When the next byte has bit 7 set:

- it becomes and new MIDI status;
- event pointer advances.

When the next byte is data:

- reuse the saved running status.

The high nibble indexes the internal table that determines how many MIDI data bytes are
required.

One- and two-data-byte messages are forwarded to the common MIDI/OPL dispatcher at:

`0x1963D`.

## Next delta time

After handling the event, the routine calls:

`ReadMidiVariableLengthQuantity`

and stores the new 32-bit countdown for that track.

## Meta events

Status `FFh` takes the meta-event path.

### `FF 2F` — End of Track

The current track active flag is cleared.

The routine scans all track flags.

When no tracks remain active:

- if loop/restart state is enabled:
  - reparses the original source using the appropriate MIDI/CMF parser;
- otherwise:
  - clears sequencer-active state.

### `FF 51` — Set Tempo

Reads the tempo payload and recomputes timer/divisor state using the SMF division word.

The resulting timing value is passed to:

`ProgramWorxTimerDivisor`

and saved as the current sequencer timing word.

Other meta-event types are skipped through their encoded payload length.

This closes the actual timer-to-MIDI event execution path.

**Status: GREEN.**

---

# 10. Small sequencer state accessors

## `0x1A1CD..0x1A1D4` — `IsSequencerActive`

Returns:

`CS:2D62 & 1`.

## `0x1A1D5..0x1A1DC` — `GetWorxFlag2DEA`

Returns:

`CS:2DEA & 1`.

The mechanical state is exact; and stronger historical UI name is not assigned without and
specific caller.

## `0x1A1DD..0x1A1E1` — `GetSequencerTickCounter`

Returns:

`CS:2C56`.

## `0x1A1E2..0x1A1E8` — `ForceSequencerActive`

Writes:

`CS:2D62 = 1`.

**Status: GREEN.**

---

# 11. `0x1A1E9..0x1A21F` — `ReadMidiVariableLengthQuantity`

Length: **55 bytes**

Reads bytes from `ES:DI`.

For every byte:

```text
value |= byte & 0x7F
```

When bit 7 is set:

```text
value <<= 7
continue
```

When bit 7 is clear:

- stop.

The 32-bit result is returned in:

`DX:AX`.

`DI` is advanced past all consumed bytes.

This is the standard MIDI variable-length quantity decoder used for track delta times.

**Status: GREEN.**

---

# 12. `0x1A220..0x1A259` — `CanonicalizeFarPointerESDI`

Length: **58 bytes**

Input:

`ES:DI`.

It converts the segmented pointer to and canonical equivalent with:

```text
linear = ES * 16 + DI
DI     = linear & 0x000F
ES     = linear >> 4
```

The raw code performs the operation using 32-bit value construction from 16-bit
registers.

NULL segment is left unchanged.

This is and generic WORX real-mode far-pointer normalization helper.

**Status: GREEN.**

---

# 13. `0x1A25A..0x1A28E` — `ProgramWorxTimerDivisor`

Length: **53 bytes**

If WORX timer mode word `CS:201E == 1`, the routine returns without reprogramming PIT.

Otherwise input AX is treated as the PIT divisor.

It computes:

```text
chainThreshold = 0xFFFF / divisor
```

and writes that value to both:

```text
CS:2DB6
CS:2DB4
```

Then programs PIT channel 0:

```text
OUT 43h, 34h
OUT 40h, divisor low byte
OUT 40h, divisor high byte
```

Control byte `34h` selects channel 0, low/high-byte access and periodic rate-generator
mode.

This directly links MIDI tempo changes to the high-rate WORX INT08 clock while
maintaining the old timer-chain threshold.

**Status: GREEN.**

---

# 14. `0x1A28F..0x1A2AC` — two legacy IRQ transform stubs

There are two instruction-identical 15-byte helpers.

They transform AL as though mapping IRQ number to vector number:

```text
IRQ < 8  -> IRQ + 8
IRQ >= 8 -> IRQ - 8 + 70h
```

but AX is pushed on entry and restored before return.

Therefore the transformed AL value itself is not returned.

No global state is written.

The only externally observable machine effect is the resulting FLAGS state.

There are no direct near-call references in the checked image.

Safest label:

```text
LegacyIrqVectorTransformFlagsStubA
LegacyIrqVectorTransformFlagsStubB
```

They are known executable bytes, not UNKNOWN data, but should not be given stronger
semantics without an address-taken caller.

**Status: GREEN mechanically.**

---

# 15. `0x1A2AD..0x1A305` — `UnmaskPicIrqLine`

Length: **89 bytes**

Input:

- AL = IRQ number.

For master IRQs `<8`:

- derive `1 << irq`;
- read mask port `21h`;
- when the line is masked, clear that mask bit.

IRQ 2 is handled as the cascade special case.

For slave IRQs `>=8`:

- subtract 8;
- operate on slave mask port `A1h`;
- perform the corresponding slave-PIC EOI/cascade handling;
- ensure the cascade route through IRQ2 is available.

Return carry distinguishes the helper'with already-enabled/failure-style path from the
successful-unmask path.

This is direct 8259 PIC control.

**Status: GREEN.**

---

# 16. `0x1A306..0x1A32F` — `MaskPicIrqLine`

Length: **42 bytes**

Input:

- AL = IRQ number.

For IRQ `<8`:

```text
mask = IN 21h
mask |= 1 << irq
OUT 21h, mask
```

For IRQ `>=8`:

```text
mask = IN A1h
mask |= 1 << (irq-8)
OUT A1h, mask
```

This is the complement of the IRQ-unmask helper.

**Status: GREEN.**

---

# 17. Byte-map impact

New continuous GREEN span:

`0x19D40 .. 0x1A32F`

Total:

**1,520 bytes executable code**

| Range | Bytes | Role |
|---|---:|---|
| `19D40–19DA2` | 99 | WORX INT08 timer ISR |
| `19DA3–19DBC` | 26 | joystick X normalized to 64 |
| `19DBD–19DD6` | 26 | joystick Y normalized to 64 |
| `19DD7–19DE5` | 15 | joystick button-state accessor |
| `19DE6–19E54` | 111 | game-port sample/calibration |
| `19E55–19F78` | 292 | Standard MIDI parser |
| `19F79–1A05F` | 231 | Creative Music File parser |
| `1A060–1A065` | 6 | sequencer timer/divisor getter |
| `1A066–1A1CC` | 359 | timer-driven MIDI/CMF sequencer |
| `1A1CD–1A1D4` | 8 | sequencer-active getter |
| `1A1D5–1A1DC` | 8 | WORX flag getter |
| `1A1DD–1A1E1` | 5 | sequencer tick-counter getter |
| `1A1E2–1A1E8` | 7 | force sequencer active |
| `1A1E9–1A21F` | 55 | MIDI VLQ decoder |
| `1A220–1A259` | 58 | canonicalize ES:DI |
| `1A25A–1A28E` | 53 | program PIT0/WORX timer divisor |
| `1A28F–1A29D` | 15 | legacy IRQ-vector flags stub AND |
| `1A29E–1A2AC` | 15 | legacy IRQ-vector flags stub B |
| `1A2AD–1A305` | 89 | unmask PIC IRQ |
| `1A306–1A32F` | 42 | mask PIC IRQ |

---

# 18. Closure metrics

Pass 30 executable GREEN cumulative:

`70,194 bytes`

Pass 31 adds:

`1,520 bytes`

New executable GREEN cumulative:

**71,714 bytes**

Tracked DATA/TABLE/STATE GREEN remains:

**12,307 bytes**

These totals remain intentionally separate.

---

# 19. Next target

Continue at:

`0x1A330`

The next region begins with and mixed WORX hardware state/table block and then the
Sound Blaster DSP/DMA path.

Already visible immediately afterward:

- DSP base-port setup;
- classic Sound Blaster DSP reset handshake (`base+6`, poll `base+0E`, read `AAh`
  from `base+0A`);
- 8237 DMA channel programming through ports `0Ah/0Bh/0Ch/02h/03h/83h`;
- Sound Blaster IRQ handler;
- DMA cursor/remaining-byte sampling;
- mixer-register capability tests.

That is the next useful pass.