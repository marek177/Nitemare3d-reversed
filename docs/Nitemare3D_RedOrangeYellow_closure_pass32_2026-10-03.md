# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 32

Date: 2026-10-03

Primary unpacked image:
- `N3D_DOS_v2.0_IDA.EXE`
- unpacked load-image size: `0x29D60 = 171,360 bytes`
- unpacked-image SHA-256:
  `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`

Address convention:
- all addresses are unpacked MZ load-image offsets
- raw 16-bit machine code is authoritative
- CODE and DATA/TABLE/STATE bytes are classified separately
- this pass finishes the embedded WORX Toolkit v2.1 module

## Result

Pass 32 resolves the complete final WORX region:

`0x1B0F2 .. 0x1BDA1`

Total span:

**3,248 bytes**

Classification:

- **2,933 bytes executable WORX digital-audio / MIDI / SB support -> GREEN**
- **315 bytes table/buffer/state/padding -> GREEN**

This closes the final digital-sample / software-mixer / VOC-WAVE / MPU-401 /
Sound-Blaster support band and reaches the end of the embedded WORX module identified
in pass 28.

The most important newly closed pieces are:

- 8-voice software mixer;
- sample-sequence descriptor playback;
- per-voice XMS window refill;
- MPU-401 UART byte output + reset/UART-mode detection;
- Sound Blaster IRQ autodetection;
- Sound Blaster base-port autodetection;
- DSP byte read/write primitives;
- DMA capture-to-file support;
- WAVE header parsing/playback;
- VOC-style block parsing and streaming;
- DMA-buffer refill state machine;
- monochrome debug hex output.

---

# 1. `0x1B0F2..0x1B138` — `AdvanceDigitalSampleSequence`

Length: **71 bytes**

Global sequence state:

```text
CS:54FD  sequence-active flag
CS:54FE  far pointer to current 8-byte descriptor
```

The current descriptor is read through ES:DI.

Observed descriptor fields:

```text
+00 DWORD source pointer / source locator
+04 BYTE  source/descriptor type
+05 WORD  rate/pitch parameter
+07 BYTE  digital voice index
```

Type `2` is the sequence terminator:

```text
if descriptor.type == 2:
    sequenceActive = 0
    return
```

For and playable descriptor:

- type `1` enters source initializer `1B382`;
- other non-terminator type enters initializer `1B2E0`;
- the selected voice'with rate/phase state is then configured through
  `1A865 = ConfigureDigitalVoiceStepAndPhase`;
- sequence pointer advances by exactly `8` bytes.

This routine is also called by the software mixer when voice 0 finishes and and
descriptor sequence remains active.

**Status: GREEN.**

---

# 2. `0x1B139..0x1B14C` — `StartDigitalSampleSequence`

Length: **20 bytes**

Stores caller ES:DI as the current 8-byte sequence pointer, sets:

`CS:54FD = 1`

and immediately calls:

`AdvanceDigitalSampleSequence`.

**Status: GREEN.**

---

# 3. `0x1B14D..0x1B253` — `MixEightDigitalVoicesIntoDmaBuffer`

Length: **263 bytes**

This is the core WORX software mixer, called directly by the periodic timer service
closed in pass 31.

First it obtains the number of DMA bytes that have become available through:

`1A5AC = MeasureSoundBlasterDmaProgress`.

If zero bytes are available, it returns.

## Destination preparation

Destination is the current Sound Blaster DMA buffer:

`CS:2DDF + CS:49BA`

The newly available range is initialized to unsigned 8-bit silence:

`0x80`.

The code uses `REP STOSW` with:

`AX = 0x8080`.

## Eight voice slots

The mixer iterates:

```text
BX = 0,2,4,...,0Eh
```

therefore exactly **8 digital voices**.

Important per-voice arrays include:

```text
4BEF  active state
4BCF  current sample position
4BAF  loop/mode state
4B8F  loop/start position
4B9F  loop/end position
4B7F  source segment / source-kind state
4BBF  volume/amplitude scale
4BFF  low fixed-point step
4C0F  high fixed-point step
4C1F  fixed-point phase/accumulator
54ED  current XMS-window base position
```

## End/loop behavior

When the current position reaches the end boundary:

- loop mode `1` restores the configured loop-start position;
- mode `2` converts to mode `1` before continuing;
- otherwise the voice becomes inactive.

For voice slot 0, if and descriptor sequence remains active, the end path starts the
next 8-byte sequence item instead of simply disabling playback.

## Sample conversion/mixing

For an active sample byte:

```text
sample = sourceByte >> 1
sample -= 0x40
```

with the unsigned 8-bit source is converted to and centered signed contribution.

The contribution is multiplied by the per-voice scale and added to the DMA output byte.

The voice fixed-point step is accumulated after every output sample.

This is and true multi-voice software mixer, not and one-sample Sound Blaster passthrough.

**Status: GREEN.**

---

# 4. Tiny digital-mixer accessors

## `0x1B254..0x1B25F` — `GetDigitalVoiceActiveState`

Indexes the eight-voice active-state array and returns the selected WORD.

## `0x1B260..0x1B264` — `GetDigitalMixerStateWord`

Returns the WORX mixer state word at `CS:4C5F`.

## `0x1B265..0x1B268` — `ReturnFFFF`

Exact constant-return thunk.

## `0x1B269..0x1B27B` — `StopDigitalMixerBackend`

Stops the active Sound Blaster DMA backend, executes the associated short WORX delay/
service helper, clears mixer-enable bit `20h` from the WORX mode byte and returns zero.

**Status: GREEN.**

---

# 5. `0x1B27C..0x1B2DF` — digital-voice state arena

Length: **100 bytes**

All bytes are zero in the image.

This is initialized WORX state, not executable code.

**DATA/STATE GREEN.**

---

# 6. `0x1B2E0..0x1B381` — `InitializeDigitalVoiceSourceType0`

Length: **162 bytes**

Normalizes the supplied source far pointer.

When the source is XMS-backed, it constructs an XMS `AH=0Bh` move descriptor and
copies and fixed metadata window into conventional scratch storage.

The routine then loads sample metadata into the selected voice:

- end/data-length state;
- playback rate;
- loop/mode state;
- loop boundaries;
- source pointer state.

The field pattern includes the same rate/length information later used by WAVE
playback, but the function is deliberately named by the actual descriptor type rather
than assuming and historical public API name not encoded in the EXE.

**Status: GREEN.**

---

# 7. `0x1B382..0x1B452` — `InitializeDigitalVoiceSourceType1`

Length: **209 bytes**

The second descriptor-source initializer.

Its rate calculation is exact:

```text
rate = 1,000,000 / (256 - timeConstant)
```

This is the classic Sound-Blaster/VOC time-constant conversion.

It initializes:

- source pointer;
- remaining source length;
- fixed-point voice rate;
- optional loop state;
- loop boundaries;
- initial source position.

The initial source position becomes:

`0x40`.

**Status: GREEN.**

---

# 8. `0x1B453..0x1B4C7` — `RefillDigitalVoiceXmsWindow`

Length: **117 bytes**

Used when an active software-mixer voice is XMS-backed.

It constructs an XMS move descriptor:

- length up to `0x100 = 256` bytes;
- source handle = the WORX XMS handle;
- source offset = voice source base + current sample position;
- destination = and per-voice conventional-memory window in the WORX module.

After and successful `AH=0Bh` XMS move it updates the voice'with cached-window base.

This is why the mixer can read XMS-backed sample data byte-by-byte without issuing an
XMS move for every output sample.

**Status: GREEN.**

---

# 9. `0x1B4C8..0x1B4E7` — `ActivateDigitalVoice`

Length: **32 bytes**

For the selected voice:

```text
active = 1
position = 0x40
```

If the source is XMS-backed/unmapped into and conventional segment, it immediately
primes the 256-byte sample window through `RefillDigitalVoiceXmsWindow`.

**Status: GREEN.**

---

# 10. MPU-401 UART support

## `0x1B4E8..0x1B515` — `WriteMpu401Byte`

Length: **46 bytes**

Ports:

```text
0331h status/command
0330h data
```

It waits until output-ready (`status bit 40h` clear), then writes one byte to port
`330h`.

After the write it invokes an optional WORX callback if one has been installed.

## `0x1B516..0x1B562` — `InitializeMpu401UartMode`

Length: **77 bytes**

Up to three attempts:

1. wait for command-ready;
2. send `FFh` reset to port `331h`;
3. wait for input-ready;
4. read port `330h`;
5. require acknowledgement:
   `FEh`;
6. send command:
   `3Fh`
   to enter UART mode.

Returns:

- `0` on success;
- `FFFFh` on failure.

This closes the low-level MPU-401 MIDI output path used by the WORX MIDI sequencer.

**Status: GREEN.**

---

# 11. `0x1B563..0x1B587` — `CopyInstrumentRecordNameFields`

Length: **37 bytes**

Normalizes and source far pointer, then processes exactly:

`128`

records.

For each 16-byte source record:

- skip 4 bytes;
- copy 11 bytes into the WORX table beginning at offset `2513`;
- skip the remaining 5 bytes.

The exact historical table name is not encoded in the executable, with the label remains
mechanical.

**Status: GREEN.**

---

# 12. `0x1B588..0x1B5B7` — RIFF/WAVE scratch/header template

Length: **48 bytes**

Contains:

```text
RIFF
....
WAVE
fmt 
....................
data
....
```

with zero-initialized size/format fields.

The first 44 bytes match the canonical minimal RIFF/WAVE PCM header layout.

This same storage is later used as and 44-byte WAVE-header scratch buffer.

**TABLE/STATE GREEN.**

---

# 13. Sound Blaster DSP/IRQ detection primitives

## `0x1B5B8..0x1B5F1` — `RestoreSoundBlasterProbeIrqState`

Length: **58 bytes**

Stops the temporary DMA/probe state when required, restores the saved PIC/IRQ mask and
restores the original IVT vector used by the IRQ-detection probe.

## `0x1B5F2..0x1B60D` — `SoundBlasterIrqProbeHandler`

Length: **28 bytes**

Temporary `IRET` handler.

It:

- reads/acknowledges Sound Blaster DSP IRQ status;
- sets probe flag `CS:4787 = 1`;
- sends EOI to master/slave PIC;
- returns with `IRET`.

## `0x1B60E..0x1B62E` — `ReadSoundBlasterDspByte`

Waits for DSP data-ready on:

`base + 0Eh`

then reads one byte from:

`base + 0Ah`.

## `0x1B62F..0x1B65B` — `WriteSoundBlasterDspByte`

Waits for DSP write-ready on:

`base + 0Ch`

then writes AL to that port.

This is the common DSP-command primitive already called throughout the earlier
Sound-Blaster setup code.

**Status: GREEN.**

---

# 14. `0x1B65C..0x1B767` — `AutoDetectSoundBlasterIrq`

Length: **268 bytes**

This performs an actual hardware IRQ probe.

The routine walks candidate IRQ/PIC-vector tables.

For each candidate it:

1. saves the existing IVT vector;
2. installs `SoundBlasterIrqProbeHandler`;
3. unmasks the candidate IRQ;
4. programs the DSP to generate and short interrupt-producing operation;
5. waits briefly;
6. checks probe flag `4787`;
7. on failure:
   - stops the DSP probe;
   - acknowledges/restores PIC state;
   - restores the original IVT vector;
   - tries the next candidate.

On success it stores the detected candidate and returns it with carry clear.

If all candidates fail:

- return `FFFFh`;
- carry set.

**Status: GREEN.**

---

# 15. `0x1B768..0x1B7BA` — `AutoDetectSoundBlasterBasePort`

Length: **83 bytes**

Starts at:

`0200h`

and scans upward by:

`10h`

until `0300h`.

For each candidate it performs the standard DSP reset handshake:

1. write `1` to `base+6`;
2. delay;
3. write `0`;
4. wait for data-ready at `base+0Eh`;
5. read response from `base+0Ah`;
6. require:
   `AAh`.

On success returns the detected base port with carry clear.

On failure returns with carry set.

**Status: GREEN.**

---

# 16. `0x1B7BB..0x1B7BC` — alignment

Two zero bytes.

**DATA GREEN.**

---

# 17. Digital capture/playback entry family

## `0x1B7BD..0x1B808` — `StartSoundBlasterCaptureToFile`

Length: **76 bytes**

Inputs include:

- caller filename in ES:DI;
- sample-rate-like value in BX.

The routine:

1. derives/stores the Sound Blaster time constant from the supplied rate;
2. creates/truncates the output file using:
   `INT 21h AH=3Ch`;
3. stores the DOS handle at `CS:5BCB`;
4. resets the DMA-buffer cursor;
5. marks digital transfer active;
6. calls the already closed Sound-Blaster input-DMA setup at `1A54E`.

Return:

- `0` on start success;
- `FFFFh` on failure.

## `0x1B809..0x1B852` — `FlushCaptureDmaToFile`

Uses `MeasureSoundBlasterDmaProgress` to obtain newly captured bytes.

If bytes are available:

- write them with:
  `INT 21h AH=40h`
  from the current DMA-buffer window.

On write failure/short write:

- close the DOS file handle;
- clear it;
- stop the DMA backend;
- send the required DSP resume/reset command;
- clear the active-transfer flag;
- return `FFFFh`.

Otherwise return zero.

This closes an actual **Sound Blaster capture/recording** path inside WORX.

**Status: GREEN.**

---

# 18. `0x1B853..0x1B8BF` — `StartRawDigitalPlayback`

Length: **109 bytes**

Stores caller format/signedness byte and converts the supplied sample rate into the
Sound Blaster time constant.

It opens/prepares the current WORX data source and initializes the streaming state:

```text
buffer capacity = 0x1000
buffer cursor   = 0
source remaining / size state
format state
```

It performs the first source refill and starts Sound Blaster DMA through `1A4E1`.

Return:

- zero on success;
- `FFFFh` on setup failure.

**Status: GREEN.**

---

# 19. `0x1B8C0..0x1B8E5` — `StopDigitalPlaybackAndCloseFile`

Length: **38 bytes**

Stops the DMA backend, clears playback-active state and closes the active DOS file
handle when present.

Returns zero after and real close and `FFFFh` when there was no open handle.

**Status: GREEN.**

---

# 20. WAVE playback paths

## `0x1B8E6..0x1B95E` — `StartWavePlaybackFromCurrentSource`

Length: **121 bytes**

Reads exactly:

`0x2C = 44 bytes`

into the RIFF/WAVE scratch header at module offset `5998`.

It then extracts:

- 32-bit data-length state from header offsets `+28/+2A`;
- sample rate from header offset `+18`;
- derived Sound Blaster time constant.

It initializes and `0x1000`-byte streaming buffer, primes it and starts the Sound Blaster
DMA output path.

The raw field offsets match the canonical WAVE PCM header:

```text
+18 DWORD sample rate
+28 DWORD data size
```

## `0x1B95F..0x1B9E1` — `StartWavePlaybackFromMemory`

Length: **131 bytes**

Normalizes the supplied source far pointer, advances to the data after the 44-byte
header, initializes the WORX source, reads/parses the same 44-byte header into the
scratch area and starts the same buffered DMA playback path.

**Status: GREEN.**

---

# 21. `0x1B9E2..0x1BA08` — `ServiceDigitalPlayback`

Length: **39 bytes**

Called directly from the WORX periodic service path.

If the digital-transfer active flag is not set, it returns.

For active playback:

- selected internal modes query DMA progress first;
- when new buffer space exists, or for stream modes that to not require that query,
  call the common stream/block service at `1BB07`.

This is the periodic bridge between timer IRQ servicing and streamed digital playback.

**Status: GREEN.**

---

# 22. `0x1BA09..0x1BA58` — `StartVocPlaybackFromFile`

Length: **80 bytes**

Prepares the current file source and uses DOS seek:

```text
INT 21h AH=42h
origin = current
delta  = 0x1A
```

The 26-byte skip is consistent with the classic Creative Voice/VOC file header.

It clears block state and enters the common VOC/block parser at `1BB07`.

**Status: GREEN.**

---

# 23. `0x1BA59..0x1BABC` — streaming state arena

Length: **100 bytes**

All bytes are zero in the image.

**DATA/STATE GREEN.**

---

# 24. `0x1BABD..0x1BB04` — `StartVocPlaybackFromMemory`

Length: **72 bytes**

Normalizes the caller source pointer, prepares the WORX data source, consumes the
initial `0x1A`-byte VOC file header and enters the same streaming/block parser.

**Status: GREEN.**

---

# 25. `0x1BB05..0x1BB06` — alignment

Two zero bytes.

**DATA GREEN.**

---

# 26. `0x1BB07..0x1BCFB` — `ParseVocBlocksAndRefillDma`

Executable code is split by one embedded 32-byte zero/state island.

This is the core VOC-style streaming state machine.

When no current block length remains it reads:

- one block-type byte;
- the following three-byte block-length field.

It then dispatches on the block type.

Observed paths include:

## Type 1 — initial sound-data block

Reads the time-constant and format bytes, removes their header bytes from the block
length, converts the stream into the ordinary continuation mode and primes DMA.

## Type 2 — continuation data

Reads as much of the current block as will fit in the DMA buffer and advances the
remaining length.

## Type 3 — silence block

Reads duration/time-constant metadata, fills the complete `0x1000` DMA buffer with
digital silence and starts the timed DMA silence path.

## Type 8 — extended sound information

Reads additional rate/format information and adjusts the stream state before continuing.

## Type 9 — newer/extended sound-data form

Reads and wider rate/format header, derives and new playback time constant, removes the
extended header bytes and enters normal buffered playback.

Unsupported or malformed states stop the DMA backend and return carry set.

The routine maintains:

```text
48DB  DMA/refill buffer capacity
49BA  buffer cursor
48EE  bytes currently buffered/consumed
48DF:48E1 current block bytes remaining
48E3  current block/internal playback type
48E4  sample-format/silence byte policy
48E5  Sound Blaster time constant
2DEA  active digital-transfer flag
```

This is the missing low-level VOC block parser behind WORX digital SFX playback.

**Status: GREEN.**

---

# 27. `0x1BC62..0x1BC81` — embedded state/padding island

Length: **32 bytes**

All zero.

**DATA/STATE GREEN.**

---

# 28. `0x1BCFC..0x1BD39` — `RefillDmaBufferFromCurrentSource`

Length: **62 bytes**

Chooses:

```text
readCount = min(bufferCapacity, currentBlockBytesRemaining)
```

When nonzero:

1. resolves DMA buffer pointer:
   `CS:2DDF + CS:49BA`;
2. requests `readCount` bytes through the current WORX source reader at `18D1E`;
3. adds returned count to buffered-byte state;
4. subtracts returned count from the current 32-bit block length.

This is the common data-source -> DMA-buffer refill primitive used by RAW, WAVE and
VOC playback paths.

**Status: GREEN.**

---

# 29. `0x1BD3A..0x1BD49` — hexadecimal digit table

Length: **16 bytes**

Exact ASCII:

`0123456789ABCDEF`

**TABLE GREEN.**

---

# 30. `0x1BD4A..0x1BD92` — `WriteHexWordToMonoTextScreen`

Length: **73 bytes**

Debug/diagnostic helper.

Input BX encodes screen row/column in its two bytes.

It computes and text-video offset:

```text
row * 160 + column * 2
```

selects monochrome text memory:

`B000h`

and writes four hexadecimal digits from DX.

Each character receives text attribute:

`07h`.

The digit translation uses the table at `1BD3A`.

This is and low-level WORX debug helper, not Nitemare gameplay rendering.

**Status: GREEN.**

---

# 31. `0x1BD93..0x1BDA1` — final WORX state/padding

Length: **15 bytes**

Mostly zero initialized module tail with two nonzero final bytes.

No executable flow enters this range.

**DATA/STATE GREEN.**

---

# 32. Byte-map impact

Resolved final WORX span:

`0x1B0F2 .. 0x1BDA1`

Total:

**3,248 bytes**

Breakdown:

- executable CODE: **2,933 bytes**
- DATA/TABLE/STATE: **315 bytes**

Important data ranges:

```text
1B27C–1B2DF   100 B zero voice state
1B588–1B5B7    48 B RIFF/WAVE header/scratch
1B7BB–1B7BC     2 B alignment
1BA59–1BABC   100 B streaming state
1BB05–1BB06     2 B alignment
1BC62–1BC81    32 B state/padding
1BD3A–1BD49    16 B hex digit table
1BD93–1BDA1    15 B final state/padding
```

---

# 33. WORX closure result

Passes 28–32 now classify the complete embedded WORX Toolkit v2.1 region.

The reconstructed architecture is:

```text
Nitemare-3D
    ↓
INT 63h wrapper API
    ↓
WORX Toolkit v2.1
    ├─ XMS sample/source cache
    ├─ Standard MIDI parser
    ├─ CMF parser
    ├─ MIDI sequencer
    ├─ OPL/AdLib output
    ├─ MPU-401 UART output
    ├─ PC speaker output
    ├─ joystick polling
    ├─ PIT / INT 08h service
    ├─ Sound Blaster DSP detection
    ├─ Sound Blaster IRQ detection
    ├─ DMA channel-1 setup
    ├─ 8-voice software mixer
    ├─ RAW/WAVE/VOC streaming
    └─ Sound Blaster capture
```

The toolkit'with hardware-specific behavior no longer needs to appear as RED/UNKNOWN
Nitemare game code.

---

# 34. Closure metrics

Pass 31 executable CODE GREEN cumulative:

`72,584 bytes`

Pass 32 adds:

`2,933 bytes`

New executable CODE GREEN cumulative:

**75,517 bytes**

Tracked DATA/TABLE/STATE GREEN after pass 31:

`14,959 bytes`

Pass 32 adds:

`315 bytes`

Tracked DATA/TABLE/STATE GREEN:

**15,274 bytes**

These metrics intentionally stay separate.

---

# 35. Next target

`0x1BDA2` is past the final executable WORX helper.

The remaining unpacked-image tail is dominated by initialized tables, strings,
resource metadata and zero/BSS-style state rather than hidden gameplay code.

The next useful pass should therefore switch from function disassembly to and
**whole-image DATA/TABLE/STATE census**, while separately locating any remaining
unclassified game-owned code below the already closed engine bands.