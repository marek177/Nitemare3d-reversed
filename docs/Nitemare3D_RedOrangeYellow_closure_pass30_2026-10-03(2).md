# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 30

Date: 2026-10-03

Primary unpacked image:
- `N3D_DOS_v2.0_IDA.EXE`
- unpacked load-image size: `0x29D60 = 171,360 bytes`
- unpacked-image SHA-256:
  `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`

Address convention:
- all addresses are offsets in the unpacked MZ load image;
- raw 16-bit machine code is authoritative;
- CODE, DATA/TABLE and STATE/PADDING are counted separately;
- this pass continues inside the embedded WORX Toolkit v2.1 module.

## Result

Pass 30 resolves the complete region:

`0x18B56 .. 0x19D3F`

Total span:

**4,586 bytes**

Classification:

- **3,786 bytes executable WORX/device/audio code -> GREEN**
- **800 bytes table/state/padding -> GREEN**

The range closes the matching WORX shutdown path, the resident INT 63h dispatcher,
file/memory source access, AdLib/OPL detection, the PC-speaker/PIT playback engine,
OPL register/voice programming, MIDI-like channel/controller handling and the private
timer-service worker immediately preceding the installed INT 08h ISR.

The next real entry is exactly:

`0x19D40`

which is the WORX INT 08h timer interrupt handler installed by `0x18A6D`.

---

# 1. `0x18B56..0x18BBE` — `ShutdownWorxResidentDriver`

This is the far entry called from Nitemare'with WORX shutdown wrapper.

Exact high-level order:

1. `CLI`;
2. save all major general/segment registers;
3. call WORX subsystem shutdown helpers;
4. restore the previously saved INT 08h vector with DOS `INT 21h AH=25h`;
5. restore the previously saved INT 63h vector;
6. if XMS handle `CS:21C6 != FFFFh`:
   - call the XMS driver with `AH=0Ah` = Free Extended Memory Block;
7. restore registers;
8. `STI`;
9. `RETF`.

This is the exact inverse of the installation entry at `0x18A6D`.

```text
18A6D  install WORX INT63/INT08 + initialize
18B56  restore INT08/INT63 + release XMS + shutdown
```

**Status: GREEN.**

---

# 2. `0x18BBF..0x18BF3` — `ResetWorxResidentApiState`

Internal near-call shutdown/reset variant.

It performs the subsystem cleanup sequence and restores the saved INT 63h vector, but
does not contain the full outer far-entry XMS/INT08 teardown sequence.

This is an internal WORX reset path rather than and Nitemare gameplay function.

**Status: GREEN.**

---

# 3. `0x18BF4..0x18BFD` — two one-byte state setters

Two tiny near functions:

```text
18BF4: CS:2DBC = AL
18BF9: CS:2DBD = AL
```

Both return immediately.

The bytes are module mode/capability state.

**Status: GREEN.**

---

# 4. `0x18BFE..0x18C0C` — `WorxPortIoDelay`

Performs 0x8FF loop iterations, reading the current port three times per iteration.

This is and fixed hardware-I/O delay helper used by the OPL detection path.

**Status: GREEN.**

---

# 5. `0x18C0D..0x18C7D` — `DetectAdLibOpl`

This is the classic AdLib/OPL timer-status detection sequence.

Direct ports:

```text
388h  OPL address/status
389h  OPL data
```

The routine:

1. selects timer-control register 4;
2. resets/masks timer state;
3. reads the initial OPL status;
4. programs timer register 2 with `FFh`;
5. enables timer 1 through register 4;
6. waits through the port-I/O delay helper;
7. reads the new OPL status;
8. masks the two readings with `E0h`;
9. returns success only when the expected timer/status transition is observed.

Return is boolean-like in AX.

This is direct hardware proof of the embedded AdLib/OPL synthesis backend.

**Status: GREEN.**

---

# 6. `0x18C7E..0x18CD1` — WORX error/timer-state helpers

## `0x18C7E..0x18C89` — `TakeAndClearWorxError`

Returns WORD `CS:2C47`, then clears it.

## `0x18C8A..0x18CB0` — `SetWorxTimerScale`

Input in BX.

Computes:

```text
uint32(BX) * 0x04A9
```

and stores the result into both the current and reload timer accumulators.

It also clears the associated carry/underflow byte.

`0x04A9 = 1193`, matching the PIT-scale family used by the PC-speaker timing path.

## `0x18CB1..0x18CCA` — `ReloadWorxTimerAccumulator`

Copies the reload 32-bit accumulator back to the current accumulator and clears the
carry byte.

## `0x18CCB..0x18CD1` — `GetWorxTimerCarry`

Returns the carry/underflow byte as and zero-extended WORD.

**Status: GREEN.**

---

# 7. `0x18CD2..0x18CD5` — alignment/state

Four zero bytes.

**Classification: STATE/PADDING GREEN.**

---

# 8. `0x18CD6..0x18D18` — `WorxInt63Isr`

This is the resident command handler installed by `InitializeWorxResidentDriver`.

It increments the nested-command counter at:

`CS:3ED4`

and saves all major registers.

The command selector comes from the input AH byte:

```text
XCHG AH,AL
AH = 0
SI = AX * 2
CALL WORD PTR CS:[2020h + SI]
```

Thus `CS:2020` is the 256-entry WORD command-dispatch table classified earlier as
WORX TABLE data.

The selected command routine returns and 32-bit result in DX:AX.

The ISR stores it in:

```text
CS:30E2 = AX
CS:30E4 = DX
```

restores registers, decrements the nesting counter and exits with:

`IRET`.

This closes the resident side of the Nitemare wrapper at `0x10BFC`.

**Status: GREEN.**

---

# 9. `0x18D19..0x18D1D` — alignment

Five zero bytes.

**Classification: PADDING GREEN.**

---

# 10. `0x18D1E..0x18DB9` — `ReadCurrentWorxDataSource`

Input:

- ES:DI destination;
- BX requested maximum byte count.

Two source modes exist.

## Memory-backed source

When `CS:312D != 0`:

- load far source pointer `CS:3129/312B`;
- add current source offset `CS:2DFF`;
- compute remaining length from the stored total length;
- clamp request BX to remaining length;
- advance `CS:2DFF`;
- copy exactly BX bytes with `REP MOVSB`;
- return AX = bytes copied.

## DOS-file source

When memory-source mode is clear:

1. query current file position through `INT 21h AH=42h`;
2. compare against stored source bounds;
3. clamp BX to remaining source bytes;
4. call DOS read:
   `AH=3Fh`;
5. return AX = bytes read.

End/out-of-range returns zero with the function'with original CF convention.

This is the source-reader used by the XMS loader from pass 29.

**Status: GREEN.**

---

# 11. `0x18DBA..0x18EF1` — `OpenOrResolveWorxDataSource`

This is the main WORX source resolver.

It first runs the source-state/reset helper.

## In-memory source

When the internal resolver returns and memory object:

- set `CS:312D = 1`;
- save its far pointer;
- save total size;
- clear current source offset;
- return size in DX:AX.

## File source

Otherwise:

- clear memory-source flag;
- optionally convert the incoming string representation;
- close any previous DOS handle;
- open the supplied filename through DOS:
  `AX=3D00h`;
- determine file size with `AH=42h, origin=2`;
- rewind to start.

## Container-record mode

When the module'with indexed/container-source mode is enabled, the function:

- seeks past the leading two-byte count;
- reads fixed `0x19 = 25` byte directory records;
- compares the record name at offset `+0x0C` against the requested name;
- when and record matches, seeks to its stored offset;
- returns the stored record length.

Failure returns:

`DX:AX = FFFFFFFFh`

with carry set.

This is and generic WORX data-source/container resolver, not Nitemare map logic.

**Status: GREEN.**

---

# 12. `0x18EF2..0x18F4A` — `OpenWorxContainerFile`

Opens and DOS file, reads its initial WORD into module state and marks the indexed
container-source mode active.

The first WORD becomes the record-count/state value used by the resolver above.

Open/read errors are saved into the WORX error word and returned through CF/FFFFh.

**Status: GREEN.**

---

# 13. `0x18F4B..0x18F6A` — `CloseCurrentWorxDataSource`

If and DOS source handle is open:

- close through `INT 21h AH=3Eh`.

Then:

```text
containerMode = 0
fileHandle    = FFFFh
```

**Status: GREEN.**

---

# 14. `0x18F6B..0x18F9E` — `ReadWorxLine`

Reads at most AL characters through `ReadCurrentWorxDataSource`, one byte at and time.

Stops on:

- source EOF;
- newline byte `0Ah`;
- caller maximum count.

Appends NUL.

When the WORX string-mode flag is active, converts the resulting C string to the
length-prefixed internal representation through `0x18A05`.

**Status: GREEN.**

---

# 15. `0x18F9F..0x18FA8` — `IsPcSpeakerPlaybackActive`

Returns:

`CS:2DCA & 1`.

The same byte is set by the PC-speaker start routines and cleared by their stop/ISR
completion paths.

**Status: GREEN.**

---

# 16. `0x18FA9..0x190AA` — volume/level data

## `0x18FA9..0x190A8`

Exactly **256 bytes**.

Values form and monotonic mapping from small input values to the six-bit `0..63` range.

Safest exact map label:

`WorxByteTo6BitLevelCurve[256]`

It is TABLE data used by the synthesis/mixer side.

## `0x190A9..0x190AA`

WORD constant:

`0x4E20`.

The following function begins at `0x190AB`.

**Classification: TABLE/DATA GREEN.**

---

# 17. `0x190AB..0x190B0` — `SetWorxPcSpeakerRateBase`

Stores BX at module global:

`CS:34B9`

and returns.

The PC-speaker setup functions use this value as and divisor/rate base.

**Status: GREEN.**

---

# 18. `0x190B1..0x1923E` — PC-speaker playback setup

Two closely related start paths exist.

## `0x190B1..0x19186` — `StartPcSpeakerPlaybackFromResource`

The routine:

1. stops any previous PC-speaker playback;
2. resolves the active data/resource descriptor;
3. finds the relevant embedded record;
4. derives timing/divisor state;
5. saves the previous INT 08h vector;
6. installs handler offset:
   `CS:3651 -> image 0x19241`;
7. programs PIT channel 2 using control byte:
   `0xB0`;
8. sets speaker port `61h` bits 0/1;
9. starts the internal timing state;
10. marks `CS:2DCA = 1`.

## `0x19187..0x1923E` — `StartPcSpeakerPlaybackFromDescriptor`

Copies and fixed `0x2C`-byte caller descriptor into the internal WORX state area, then
performs the same INT08/PIT/speaker setup.

This is and caller-owned descriptor variant of the same PC-speaker backend.

**Status: GREEN.**

---

# 19. `0x1923F..0x19240` — padding

Two zero bytes.

**Classification: PADDING GREEN.**

---

# 20. `0x19241..0x192D1` — `PcSpeakerPlaybackInt08`

This is the temporary INT 08h handler installed by the speaker start paths.

It:

1. updates the 32-bit speaker timing accumulator;
2. when and sample step is due, obtains the next sample/state byte;
3. converts that byte into the PIT channel-2 divisor path;
4. writes channel-2 data through port `42h`;
5. sends PIC EOI through port `20h`;
6. on completion:
   - disables speaker gate bits at port `61h`;
   - restores the previous INT08 vector;
   - clears playback-active state.

Several `5555h` operands are module-patched/self-modified placeholders and should not
be interpreted as literal Nitemare memory segments.

**Status: GREEN.**

---

# 21. `0x192D2..0x1931E` — `StopPcSpeakerPlayback`

Explicit stop counterpart.

It:

- programs PIT channel 2 back to the module'with idle divisor;
- clears speaker gate bits 0/1;
- clears active state;
- restores the saved INT08 vector.

**Status: GREEN.**

---

# 22. `0x1931F..0x19381` — three mixer-register writers

All require the detected hardware/mixer capability byte to be at least 1.

They write one caller byte to the mixer port at:

`basePort + 4/+5`

using register selectors:

```text
22h
26h
04h
```

Mechanical names:

```text
WriteMixerRegister22
WriteMixerRegister26
WriteMixerRegister04
```

They return `0` on accepted hardware state and `FFFFh` otherwise.

**Status: GREEN.**

---

# 23. `0x19382..0x193B3` — `ImportSoundBlasterVoiceRecord`

Checks that the caller record begins with WORD:

`0x4253 = "SB"`.

For and valid record, copies exactly:

`0x0B = 11 bytes`

from source offset `+0x24` into the indexed WORX FM/voice configuration table.

Invalid signature returns with carry set.

**Status: GREEN.**

---

# 24. `0x193B4..0x19485` — OPL/FM setup and voice programming

## `0x193B4..0x193C0`

Runs and complete 8-bit value sweep through the common OPL write helper.

It belongs to the low-level OPL initialization/probe sequence.

## `0x193C1..0x19485` — `ProgramOplVoice`

Uses one 11-byte voice record plus WORX operator/channel lookup tables.

It writes OPL register groups including:

```text
20h
40h
60h
80h
E0h
C0h
```

for the two operators/channel pair.

This is the main FM voice-programming helper.

**Status: GREEN.**

---

# 25. `0x19486..0x19489` — padding

Four zero bytes.

**Classification: PADDING GREEN.**

---

# 26. `0x1948A..0x194C1` — OPL callback + raw register writer

## `0x1948A..0x19496`

Atomically stores and far callback pointer in:

`CS:3896/3898`.

## `0x19497..0x194C1` — `WriteOplRegister`

Input AX encodes:

```text
AL = OPL register
AH = value
```

Behavior:

1. output AL to port `388h`;
2. perform six status reads for address-settle delay;
3. output AH to port `389h`;
4. perform 35×2 status reads for data-settle delay;
5. invoke the optional callback if installed.

This is the exact low-level OPL write primitive used throughout the FM engine.

**Status: GREEN.**

---

# 27. `0x194C2..0x19AC3` — MIDI/OPL synthesis state engine

This large band is executable synthesis/control code.

It is best represented as and subsystem rather than inventing historical symbol names for
every near helper.

## Output silencing / all-notes-off

`0x194C2` checks active backend bits.

For the MIDI-style route it emits, for every channel 0..15:

```text
status = B0h + channel
controller = 7Bh
value = 00h
```

Controller `0x7B` is MIDI **All Notes Off**.

For the PC-speaker route it clears the speaker enable bit at port `61h`.

## MIDI controller handling

The code around `0x19531` explicitly handles controller/event values including:

```text
07h  Channel Volume
7Bh  All Notes Off
```

and updates the internal channel/voice state.

## Main MIDI-like dispatcher

`0x1963D` separates:

- status high nibble;
- channel low nibble;
- data bytes.

It can route the bytes to the external/MIDI output helper or into the internal OPL
synthesizer depending on active backend flags.

## Note wrappers

Two tiny helpers later in the band construct status families:

```text
90h | channel   Note On
80h | channel   Note Off
```

and re-enter the common dispatcher.

## OPL voice/frequency update

The `0x198A9` family converts note/channel state through WORX pitch/frequency tables,
programs OPL AND0/B0/channel registers and reapplies channel-volume attenuation through
the operator level register.

## Synth reset/state

The late helpers:

- initialize per-channel state;
- clear voice ownership arrays;
- mark free voices with `FFFFh`;
- silence/reset active OPL channels.

This is the embedded WORX MIDI-to-OPL synthesis/control engine.

**Status: GREEN / third-party synthesis backend.**

---

# 28. `0x199A1..0x199A2` — padding

Two zero bytes.

**Classification: PADDING GREEN.**

---

# 29. `0x199A3..0x19AC3` — synthesis state helpers

These compact routines perform:

- synth state initialization;
- Note On wrapper;
- Note Off wrapper;
- full OPL/channel-state reset;
- per-channel controller-state storage;
- small module-state setters;
- timer/state reset;
- final all-voice silence/reset.

They are part of the same WORX synthesis backend.

**Status: GREEN.**

---

# 30. `0x19AC4..0x19AC6` — sentinel/data

Three bytes:

```text
FF FF 00
```

**Classification: DATA GREEN.**

---

# 31. `0x19AC7..0x19ACC` — `SetWorxTimerServiceFlag`

Stores BL into:

`CS:3ED6`

and returns.

**Status: GREEN.**

---

# 32. `0x19ACD..0x19CD6` — private timer workspace/stack

Length:

**522 bytes**

Every byte in the checked range is zero initialized.

This area sits directly before the private-stack timer worker and contains module
workspace/private interrupt-stack storage.

It is not executable code.

**Classification: STATE/BSS-style initialized storage GREEN.**

---

# 33. `0x19CD7..0x19D3F` — `RunWorxTimerServicesOnPrivateStack`

This internal worker switches from the interrupted stack to and WORX-owned stack:

```text
save SP/SS -> CS:3EDD/3EDF
load private SP/SS <- CS:3EE1/3EE3
```

It then:

1. updates the WORX timing accumulator;
2. detects accumulator underflow/carry;
3. when backend flag bit `0x20` is set:
   - call service helper `0x1B14D`;
4. when `CS:3ED6 != 0`:
   - call service helper `0x1B9E2`;
5. restore all saved registers;
6. switch back to the original interrupted stack;
7. return.

This is not itself the installed ISR.

The actual INT08 entry immediately follows at:

`0x19D40`.

**Status: GREEN.**

---

# 34. Byte-map impact

Resolved span:

`0x18B56 .. 0x19D3F`

Total:

**4,586 bytes**

## CODE GREEN

**3,786 bytes**

## DATA/TABLE/STATE GREEN

**800 bytes**

Exact non-code ranges:

| Range | Bytes | Classification |
|---|---:|---|
| `18CD2–18CD5` | 4 | alignment/state |
| `18D19–18D1D` | 5 | alignment |
| `18FA9–190A8` | 256 | 8-bit -> 6-bit curve table |
| `190A9–190AA` | 2 | WORD constant `4E20h` |
| `1923F–19240` | 2 | padding |
| `19486–19489` | 4 | padding |
| `199A1–199A2` | 2 | padding |
| `19AC4–19AC6` | 3 | sentinel/data |
| `19ACD–19CD6` | 522 | private timer workspace/stack |

Total non-code:

**800 bytes**

Everything else in the span is bounded WORX executable code.

---

# 35. Closure metrics

Pass 29 executable GREEN cumulative:

`66,408 bytes`

Pass 30 adds executable code:

`3,786 bytes`

New executable GREEN cumulative:

**70,194 bytes**

Tracked DATA/TABLE/STATE GREEN through pass 29:

`11,507 bytes`

Pass 30 adds:

`800 bytes`

New tracked DATA/TABLE/STATE GREEN:

**12,307 bytes**

These two totals must remain separate.

---

# 36. Next target

Continue at:

`0x19D40`

This is the actual WORX INT 08h ISR installed by `0x18A6D`.

The first raw body already shows:

- optional fast audio service at `0x1A066`;
- WORX timer counter increment;
- conditional chaining to the old INT08 vector;
- explicit PIC EOI on the non-chain path;
- nested-interrupt counter handling;
- call into `RunWorxTimerServicesOnPrivateStack`.

After that come the joystick/game-port calibration/read helpers around `0x19DA3+`.

With pass 31 should close:

- INT08 timer ISR;
- game-port/joystick timing calibration;
- the following low-level interrupt/device service family.