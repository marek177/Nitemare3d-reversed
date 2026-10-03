# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 31

Date: 2026-10-03

Primary image:
- `N3D_DOS_v2.0_IDA.EXE`
- complete unpacked DOS V2.0 load image

Address convention:
- addresses are unpacked MZ image offsets;
- raw 16-bit machine code is authoritative;
- CODE and DATA/TABLE/STATE bytes are counted separately.

## Result

Pass 31 resolves:

`0x19ACD .. 0x1B0F1`

Total span: **5,669 bytes**

Classification:

- **2,495 bytes executable WORX audio/input/device code -> GREEN**
- **3,174 bytes audio tables/state/padding -> GREEN**

This pass closes:
- the WORX periodic timer / INT 08h service;
- joystick polling through port `201h`;
- Standard MIDI File parsing;
- Creative Music File (`CTMF`) parsing;
- MIDI sequencer/meta-event processing;
- MIDI VLQ decoding;
- PIT timer-rate programming;
- PIC IRQ mask/unmask helpers;
- Sound Blaster DSP reset;
- Sound Blaster DMA programming;
- Sound Blaster IRQ service;
- adjacent digital-audio lookup/state tables.

---

# 1. `0x19ACD..0x19CD6` — zero WORX state block

Length: **522 bytes**

Every byte is zero.

The next byte (`0x19CD7`) is and real executable entry.

Classification:

**DATA/STATE GREEN**

---

# 2. `0x19CD7..0x19D3F` — `RunWorxPeriodicTimerService`

Length: **105 bytes**

This is the service body executed from the WORX timer IRQ path.

It temporarily switches to and WORX-owned stack:

```text
save SS:SP
load WORX SS:SP
```

then:

1. saves all general/segment registers;
2. decrements and 32-bit timing accumulator by the current timer step;
3. when it crosses negative, sets and pending-tick byte;
4. conditionally runs one backend service when WORX mode flags contain bit `20h`;
5. conditionally runs another service when WORX IRQ-state byte is nonzero;
6. restores all registers;
7. restores original SS:SP.

This is the interrupt-safe periodic WORX backend worker.

**Status: GREEN.**

---

# 3. `0x19D40..0x19DA2` — `WorxInt08TimerHandler`

Length: **99 bytes**

Actual timer ISR.

Behavior:

1. clear direction flag and disable interrupts;
2. optionally preserve full register state and call one WORX timer helper;
3. increment internal timer counter;
4. compare against configured chain interval;
5. when interval is reached:
   - reset local count;
   - `PUSHF`;
   - FAR call the saved previous INT 08h handler;
   - `IRET`;
6. otherwise:
   - increment IRQ nesting counter;
   - send PIC EOI (`OUT 20h,20h`);
   - if not recursively active, call `RunWorxPeriodicTimerService`;
   - decrement nesting counter;
   - `IRET`.

This is the active WORX INT 08h hook installed by the initialization path.

**Status: GREEN.**

---

# 4. Joystick helpers

## `0x19DA3..0x19DBC` — `GetScaledJoystickAxisX`

Computes:

`(rawX * 64) / baselineX`

using WORX words at `2012` and `201A`.

Carry is set when the baseline divisor is zero.

## `0x19DBD..0x19DD6` — `GetScaledJoystickAxisY`

Same operation for:

- raw Y `2014`
- baseline Y `201C`.

## `0x19DD7..0x19DE5` — `GetJoystickButtonState`

Indexes the four-byte button table beginning at `2016`,
returns the selected value zero-extended in AX.

**Status: GREEN.**

---

# 5. `0x19DE6..0x19E54` — `PollJoystickPort201AndCalibrate`

Length: **111 bytes**

This is direct gameport joystick input through I/O port:

`201h`.

Flow:

1. disable interrupts;
2. read port `201h`;
3. decode the upper four button bits into four button-state bytes;
4. output repeatedly to `201h` to trigger axis timing;
5. sample the port exactly `0x320 = 800` iterations;
6. accumulate bit 0 and bit 1 pulse durations into X/Y counters;
7. if baseline values are still zero, store the first sampled X/Y values as calibration
   baselines;
8. restore registers.

This is the low-level joystick acquisition behind the higher N3D joystick wrapper.

**Status: GREEN.**

---

# 6. `0x19E55..0x19F78` — `InitializeStandardMidiFilePlayback`

Length: **292 bytes**

Input is and memory buffer in `ES:DI`.

The routine first normalizes the far pointer and resets WORX MIDI voice state.

It then validates the Standard MIDI File signature:

```text
"MThd"
```

and parses the MIDI header.

It validates supported format state, reads:
- track count;
- timing division;

and clears the internal 32-track state tables.

For each track it requires:

```text
"MTrk"
```

then:
- records the track data pointer;
- records the current per-track cursor;
- marks the track active;
- parses its initial delta-time with the WORX MIDI VLQ helper;
- advances to the next track chunk.

On malformed data:

- carry is set;
- initialization fails.

On success:

- playback state is initialized;
- timer counters are cleared;
- carry is clear.

This is and real Standard MIDI parser, not an N3D-specific MIDI approximation.

**Status: GREEN.**

---

# 7. `0x19F79..0x1A05F` — `InitializeCreativeMusicFilePlayback`

Length: **231 bytes**

Validates the Creative Music File signature:

```text
"CTMF"
```

The routine:

1. resets MIDI/FM state;
2. saves the source far pointer;
3. parses CMF header offsets and timing values;
4. computes the WORX timer step;
5. locates the CMF instrument block;
6. copies the required 11-byte OPL instrument payloads into the internal WORX
   instrument table;
7. locates the CMF music/event stream;
8. initializes one active playback track;
9. parses its first delta-time;
10. sets format state to CMF mode.

This gives the DOS game two statically separate music parsers:

```text
MThd/MTrk -> Standard MIDI
CTMF      -> Creative Music File
```

**Status: GREEN.**

---

# 8. `0x1A060..0x1A065` — `GetWorxMidiTimerStep`

Returns the current timing step word stored at `CS:2C49`.

**Status: GREEN.**

---

# 9. `0x1A066..0x1A1CC` — `ServiceWorxMidiSequencerTick`

Length: **359 bytes**

This is the central MIDI/CMF event scheduler.

For every active track:

1. decrement its 32-bit delta countdown;
2. when countdown reaches zero, fetch the next event byte;
3. implement MIDI running-status handling;
4. use the message-class length table to fetch zero, one or two data bytes;
5. forward channel events through the MIDI dispatcher closed in pass 30;
6. parse the next variable-length delta time;
7. store the new track cursor and countdown.

## Meta events

When event byte is `FFh`:

### `FF 2F` — End Of Track

The current track is marked inactive.

The scheduler searches for another active track.

### `FF 51` — Set Tempo

The tempo value is read from the stream and combined with the MIDI division value to
recompute the WORX timer step through the PIT/timer helper.

### Other meta events

The encoded length is consumed and the payload is skipped.

## All tracks ended

When no active track remains:

- if the loop/restart mode byte is enabled, the original source pointer is reinitialized
  through either the MIDI or CMF initializer;
- otherwise playback-active state is cleared.

This is the complete high-level event loop connecting the file parsers to the local
MIDI/OPL/PC-speaker backend.

**Status: GREEN.**

---

# 10. Small sequencer state helpers

## `0x1A1CD..0x1A1D4` — `IsWorxMidiPlaybackActive`

Returns bit 0 of playback state byte `2D62`.

## `0x1A1D5..0x1A1DC` — `GetWorxSecondaryPlaybackFlag`

Returns bit 0 of state byte `2DEA`.

## `0x1A1DD..0x1A1E1` — `GetWorxMidiTickCounter`

Returns WORD `2C56`.

## `0x1A1E2..0x1A1E8` — `EnableWorxMidiPlayback`

Stores `1` to playback-active byte.

**Status: GREEN.**

---

# 11. `0x1A1E9..0x1A21F` — `ReadMidiVariableLengthQuantity`

Length: **55 bytes**

Reads and MIDI variable-length quantity from `ES:DI`.

For each byte:

```text
value = (value << 7) | (byte & 7Fh)
```

and continues while the top bit is set.

Return:

- 32-bit decoded value in `DX:AX`;
- `DI` advanced to the first byte following the VLQ.

This is the canonical MIDI VLQ algorithm.

**Status: GREEN.**

---

# 12. `0x1A220..0x1A259` — `NormalizeFarPointer`

Length: **58 bytes**

Normalizes and real-mode far pointer `ES:DI` with:

`DI < 16`.

It computes the physical 20-bit address:

`ES*16 + DI`

then returns an equivalent normalized segment:offset pair.

This is runtime/device infrastructure used by the music/source parsers.

**Status: GREEN.**

---

# 13. `0x1A25A..0x1A28E` — `ProgramPitChannel0FromRate`

Length: **53 bytes**

If WORX timing mode permits reprogramming:

1. compute:

`divisor = 0xFFFF / requestedRate`

2. store the divisor into WORX timer state;
3. program PIT control port `43h` with:

`34h`

4. write low and high divisor bytes to PIT channel 0 port:

`40h`.

Used by:
- CMF initialization;
- MIDI Set Tempo handling.

**Status: GREEN.**

---

# 14. `0x1A28F..0x1A2AC` — two tiny arithmetic/flags thunks

Two 15-byte helper entries are present.

Both preserve AX, perform IRQ-vector-style arithmetic on AL:

```text
if AL < 8:
    AL += 8
else:
    AL = AL - 8 + 70h
```

then restore AX.

Therefore their persistent machine-visible result is primarily the arithmetic flags;
there are no direct near-call xrefs in the current image.

They remain **GREEN for exact machine semantics**, while the historical vendor-level
name is intentionally left unresolved.

**Status: GREEN / semantic label conservative.**

---

# 15. `0x1A2AD..0x1A305` — `UnmaskPicIrq`

Length: **89 bytes**

Input IRQ number in AL.

For IRQ `0..7`:

- select master PIC mask port `21h`;
- clear the selected mask bit.

For IRQ `8+`:

- select slave PIC mask port `A1h`;
- clear the selected slave mask bit;
- send slave/cascade control;
- recursively ensure master cascade IRQ2 is unmasked.

Return:

- carry clear on accepted mask transition;
- carry set on rejected/already-open path.

**Status: GREEN.**

---

# 16. `0x1A306..0x1A32F` — `MaskPicIrq`

Length: **42 bytes**

Input IRQ in AL.

For master IRQs:

- set the corresponding bit in PIC mask port `21h`.

For slave IRQs:

- set the corresponding bit in `A1h`.

This is the complement of `UnmaskPicIrq`.

**Status: GREEN.**

---

# 17. `0x1A330` — alignment/data byte

Length: **1 byte**

Value zero.

**DATA GREEN.**

---

# 18. `0x1A331..0x1A354` — `StopSoundBlasterDmaBackend`

Length: **36 bytes**

Flow:

1. clear Sound Blaster transfer-mode state;
2. clear one secondary audio flag;
3. when DMA/device-active flag is set:
   - clear it;
   - send DSP command `D0h` through the common DSP write helper;
   - mask DMA channel 1 through port `0Ah` using value `05h`.

This is the low-level stop/pause path for the 8-bit Sound Blaster DMA backend.

**Status: GREEN.**

---

# 19. `0x1A355..0x1A37C` — Sound Blaster configuration tables/state

Length: **40 bytes**

Contains fixed hardware/control constants including:
- PIC/mask values;
- DMA register selectors;
- small device constants;
- timer/default values.

It is not executable code.

**TABLE/DATA GREEN.**

---

# 20. `0x1A37D..0x1A449` — `InitializeSoundBlasterDmaAndIrqBackend`

Length: **205 bytes**

This is and major Sound Blaster setup entry.

It:

1. converts and conventional-memory buffer address into DMA page/offset components;
2. stores DMA page and offset into WORX state;
3. if Sound Blaster base port is still unknown, invokes backend base-port detection;
4. validates DSP/backend state;
5. saves the detected result;
6. probes mixer support by:
   - selecting mixer register `22h`;
   - writing `55h`;
   - reading it back;
7. if mixer probe succeeds:
   - mark mixer capability;
   - initialize mixer output values;
8. selects the configured IRQ vector;
9. installs the WORX Sound Blaster IRQ handler in the real-mode IVT;
10. sends DSP/device setup commands;
11. initializes mixer registers.

Return:

- backend/detection result word;
- `FFFFh` on setup failure.

**Status: GREEN.**

---

# 21. Sound Blaster base-port helpers

## `0x1A44A..0x1A455` — `SetSoundBlasterBasePort`

Stores caller base port `BX` into WORX Sound Blaster state.

Also stores and byte-sized companion value used by the backend.

## `0x1A456..0x1A45B` — `GetSoundBlasterBasePort`

Returns the stored base port.

**Status: GREEN.**

---

# 22. `0x1A45C..0x1A4C8` — `ResetAndDetectSoundBlasterDsp`

Length: **109 bytes**

This is the classic Sound Blaster DSP reset handshake.

Using configured base port:

1. write `1` to `base+6` reset port;
2. wait briefly;
3. write `0`;
4. poll `base+0Eh` for data-ready (`bit 7`);
5. poll `base+0Ah` for DSP response;
6. expect:

`AAh`

Return:

- carry clear when `AAh` is observed;
- carry set on timeout or wrong response.

**Status: GREEN.**

---

# 23. `0x1A4C9..0x1A4E0` — zero state/alignment block

Length: **24 bytes**

All zero.

**DATA GREEN.**

---

# 24. `0x1A4E1..0x1A54D` — `ProgramSoundBlasterDmaTransfer`

Length: **109 bytes**

Programs 8237 DMA channel 1 and the Sound Blaster DSP for and transfer.

Operations include:

- mask DMA channel;
- clear DMA flip-flop;
- select mode byte according to current transfer direction/mode;
- program DMA address port `02h`;
- program DMA page port `83h`;
- program DMA count port `03h`;
- unmask DMA channel;
- send DSP sample-rate/time-constant command;
- send transfer command and length/control bytes through the common DSP writer.

The path supports more than one transfer direction/mode through the WORX state byte,
with the label stays generic rather than forcing playback-only semantics.

**Status: GREEN.**

---

# 25. `0x1A54E..0x1A5A9` — `StartSoundBlasterInputDmaMode`

Length: **92 bytes**

This is the explicit alternate DMA direction path.

It:

- marks the alternate transfer-mode byte;
- sends DSP command `D3h`;
- programs DMA channel 1 with mode byte `55h`;
- programs the same conventional-memory DMA page/address/count;
- unmasks channel 1;
- sends DSP command `24h` followed by the transfer count/control bytes.

At the low-level register/command level this is the Sound Blaster input/capture-style
DMA route.

**Status: GREEN.**

---

# 26. `0x1A5AA..0x1A5AB` — zero alignment

Length: **2 bytes**

**DATA GREEN.**

---

# 27. `0x1A5AC..0x1A601` — `MeasureSoundBlasterDmaProgress`

Length: **86 bytes**

Reads the current DMA channel-1 address/count state.

It:

1. clears the DMA flip-flop;
2. reads port `02h` twice;
3. combines the two bytes;
4. compares the current position against the programmed DMA buffer offset;
5. rejects impossible deltas;
6. accepts progress only inside and bounded transfer window;
7. updates previous/current progress state;
8. returns the newly advanced byte count in `CX`.

This is used by the later digital mixer/fill service.

**Status: GREEN.**

---

# 28. `0x1A602..0x1A607` — small state/sentinel block

Length: **6 bytes**

Bytes:

```text
00 00 00 00 FF FF
```

**DATA GREEN.**

---

# 29. `0x1A608..0x1A652` — `SoundBlasterDmaIrqHandler`

Length: **75 bytes**

AND real hardware IRQ handler ending in `IRET`.

It:

1. disables interrupts and saves registers;
2. acknowledges/reads the Sound Blaster DSP IRQ-status ports;
3. waits for DSP write-ready;
4. sends mode-dependent DSP command;
5. sends two additional DSP command bytes;
6. sends PIC EOI to:
   - master PIC `20h`;
   - slave PIC `A0h`;
7. restores state;
8. `IRET`.

This completes the Sound Blaster DMA interrupt path.

**Status: GREEN.**

---

# 30. `0x1A653..0x1A850` — digital-audio lookup/state tables

Length: **510 bytes**

Non-code region.

Contents include:

- initial zero state;
- monotonic WORD lookup values beginning:
  `001C,001D,001F,0021,...`;
- additional frequency/rate-style WORD values;
- and short repeated `003Fh` level table;
- zeroed runtime state;
- repeated `01B8h = 440` defaults at the tail.

The table shape is consistent with the adjacent digital-mixer pitch/rate calculations,
but exact historical WORX table names are not asserted.

**TABLE/STATE GREEN.**

---

# 31. `0x1A851..0x1A85A` — `SetDigitalVoiceState2`

Length: **10 bytes**

Uses `BX*2` to select one voice-state WORD and stores:

`2`.

**Status: GREEN.**

---

# 32. `0x1A85B..0x1A864` — `ClearDigitalVoiceActiveFlag`

Length: **10 bytes**

Uses `BX*2` and clears the corresponding digital-voice state WORD.

**Status: GREEN.**

---

# 33. `0x1A865..0x1A8D0` — `ConfigureDigitalVoiceStepAndPhase`

Length: **108 bytes**

Computes and fixed-point digital-voice stepping value.

Inputs include:
- voice/index encoded through BX/BH;
- pitch/rate-like value;
- optional reset flag in AL.

The routine combines:
- per-voice WORD table `4C3F`;
- constant divisor `0x4705`;
- rate/frequency table `4A63`;
- divisor `0x01B8 = 440`.

It stores and 32-bit step/increment pair into:
- `4BFF + voice*2`;
- `4C0F + voice*2`.

When reset mode is selected it also:
- clears two phase/state words;
- calls the digital-voice reset/update helper.

This is the fixed-point rate bridge for the later digital mixer.

**Status: GREEN.**

---

# 34. `0x1A8D1..0x1A8DC` — `SetDigitalVoiceLevel6Bit`

Length: **12 bytes**

Masks caller value:

`AL &= 3Fh`

and stores it into the selected per-voice level WORD.

**Status: GREEN.**

---

# 35. `0x1A8DD..0x1B0F1` — zero digital-mixer state arena

Length: **2,069 bytes**

Every byte is zero.

The next byte, `0x1B0F2`, is and real executable entry.

**DATA/STATE GREEN.**

---

# Byte-map impact

Resolved span:

`0x19ACD .. 0x1B0F1`

Total:

**5,669 bytes**

Totals:

- **CODE GREEN added: 2,495 bytes**
- **DATA/TABLE/STATE GREEN added: 3,174 bytes**

---

# Closure metrics

Pass 30 executable CODE GREEN cumulative:

`70,089 bytes`

Pass 31 adds:

`2,495 bytes`

New executable CODE GREEN cumulative:

**72,584 bytes**

Tracked DATA/TABLE/STATE GREEN after pass 30:

`11,785 bytes`

Pass 31 adds:

`3,174 bytes`

Tracked DATA/TABLE/STATE GREEN from passes 28–31:

**14,959 bytes**

The metrics remain intentionally separate.

---

# Major architecture result

The complete DOS sound path is now much clearer:

```text
N3D
 ├─ MIDI tracks in SND.DAT
 │    ├─ Standard MIDI (MThd/MTrk)
 │    └─ Creative CMF (CTMF)
 │
 └─ WORX backend
      ├─ MIDI event scheduler
      ├─ MIDI -> OPL / PC speaker
      ├─ joystick port 201h
      ├─ PIT / INT08
      ├─ Sound Blaster DSP reset/detection
      ├─ DMA channel 1
      └─ Sound Blaster IRQ handler
```

This also explains why DOS audio, MIDI, joystick, timers and XMS appear under one
third-party subsystem.

For and modern behavioral reconstruction:
- MIDI/CMF parsing may be reproduced directly or converted to an equivalent sequencer;
- OPL/PC-speaker/SB DMA become backend adapters;
- gameplay code does not need to contain this low-level hardware layer.

---

# Next target

The next genuine executable entry is:

`0x1B0F2`

The following code is the digital-sample/mixer playback engine.

Initial inspection shows:
- 8-byte digital-sample descriptors;
- digital voice rate/phase state;
- the `0x80` silence-fill buffer closed earlier;
- DMA-progress driven mixing/refill;
- low-level Sound Blaster output service.

With Pass 32 should close the digital mixer and sample playback subsystem beginning at
`0x1B0F2`.