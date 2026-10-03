# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 32

Date: 2026-10-03

Primary image:
- `N3D_DOS_v2.0_IDA.EXE`
- complete unpacked DOS V2.0 load image

Address convention:
- addresses are unpacked MZ image offsets;
- WORX module CS-relative base in this band is `0x15BF0`;
- raw 16-bit machine code is authoritative;
- CODE and embedded DATA/TABLE/STATE are counted separately.

## Result

Pass 32 resolves the complete digital sample/mixer tail:

`0x1B0F2 .. 0x1BD92`

Total span: **3,233 bytes**

Classification:

- **2,933 bytes executable WORX digital-audio code -> GREEN**
- **300 bytes embedded data/scratch/table -> GREEN**
- **34 real function entries**

This pass closes:
- the eight-voice unsigned-PCM software mixer;
- per-voice fixed-point stepping;
- XMS sample-cache refill;
- generic digital sample descriptors;
- VOC-style sample descriptors;
- MPU-401 UART output/detection;
- 128-entry OPL instrument-bank import;
- Sound Blaster IRQ auto-detection;
- Sound Blaster base-port auto-detection;
- raw PCM playback;
- WAV file/memory playback;
- VOC file/memory playback;
- PCM capture/write service;
- VOC block-stream refill;
- and final VGA text-mode hexadecimal diagnostic helper.

It also establishes that raw PCM, VOC-style and RIFF/WAVE sample paths are separate in
the WORX backend.

---

# 1. `0x1B0F2..0x1B138` — `AdvanceDigitalSequenceEntry`

Length: **71 bytes**

Uses the current far pointer stored at:

```text
CS:54FE  offset
CS:5500  segment
```

The pointed record has an **8-byte stride**.

Observed fields:

```text
+00 DWORD  far sample/source pointer
+04 BYTE   source/descriptor type
+05 WORD   rate/pitch parameter
+07 BYTE   digital voice index
```

Behavior:

1. if `record+4 == 2`:
   - clear sequence-active byte `54FD`;
   - return;
2. otherwise load the far source pointer;
3. route source type:
   - type `1` -> `LoadVocStyleDigitalVoiceDescriptor`;
   - other supported type -> `LoadDigitalVoiceDescriptor`;
4. load:
   - voice index from `+7`;
   - rate/pitch argument from `+5`;
5. call `ConfigureDigitalVoiceStepAndPhase`;
6. advance the sequence cursor by exactly `8` bytes.

This is the stepper for WORX digital-sample sequence command `4Eh`.

**Status: GREEN.**

---

# 2. `0x1B139..0x1B14C` — `StartDigitalSequence`

Length: **20 bytes**

WORX INT63 command:

`4Eh`

Stores the caller far sequence pointer into `54FE:5500`,
sets sequence-active byte `54FD = 1`,
and immediately executes the first 8-byte sequence record.

**Status: GREEN.**

---

# 3. `0x1B14D..0x1B253` — `MixEightDigitalVoicesIntoDmaWindow`

Length: **263 bytes**

This is the core software PCM mixer.

## DMA window size

First calls:

`MeasureSoundBlasterDmaProgress`

which returns the number of newly consumed/output bytes in `CX`.

When zero bytes need service, return immediately.

## Silence baseline

The selected part of the Sound Blaster DMA ring buffer is initialized with:

`0x80`

using repeated WORD:

`0x8080`.

This is the unsigned 8-bit PCM silence midpoint.

## Eight voice slots

The routine iterates:

```text
BX = 0,2,4,...,14
```

therefore exactly:

**8 digital voices**.

Per-voice state includes:

```text
4BEF  active flags
4B7F  direct sample source segment
4B6F  direct sample source offset/index
4BAF  playback/loop mode
4B8F  loop/start position
4B9F  loop/end position
4BBF  volume
4BCF  current integer sample position
4BDF  sample end
4BFF  fixed-point step low word
4C0F  fixed-point step high word
4C1F  fractional phase
4CED  8 × 256-byte XMS sample caches
54ED  cached XMS block base for each voice
```

## End/loop handling

When the sample cursor reaches its boundary:

- one mode restarts from the stored loop/start point;
- and second mode transitions into looping;
- non-looping voices are deactivated;
- when the first voice belongs to an active 8-byte digital sequence,
  `AdvanceDigitalSequenceEntry` is invoked.

## Direct versus XMS source

If the per-voice source segment is nonzero:

- sample data is read directly through that segment.

If the source segment is zero:

- use the 256-byte cache at:

`CS:4CED + voice*0x100`;

- when the current cursor has left the cached 256-byte window,
  call `RefillDigitalVoiceCacheFromXms`.

## Sample conversion and mixing

For each source byte:

```text
sample = (sourceByte >> 1) - 0x40
scale  = volume * 4
mixed contribution = high byte(sample * scale)
destination += contribution
```

The output byte began at unsigned silence `0x80`.

No separate general-purpose Z/audio object is involved; this is and direct integer
software mixer.

## Fixed-point stepping

After every output sample:

```text
fraction += stepLow
position += stepHigh + carry
```

This is exact fixed-point resampling.

**Status: GREEN.**

---

# 4. Small digital-mixer API entries

## `0x1B254..0x1B25F` — `IsDigitalVoiceActive`

WORX command:

`36h`.

Input voice index in `AL`.

Returns the corresponding active WORD from the 8-voice table.

## `0x1B260..0x1B264` — `GetDigitalMixerStateWord`

Returns WORX state WORD `CS:4C5F`.

The exact vendor symbolic meaning of the word is left conservative.

## `0x1B265..0x1B268` — `DigitalCommand32UnsupportedStub`

WORX command:

`32h`.

Always returns:

`FFFFh`.

## `0x1B269..0x1B27B` — `StopDigitalMixerBackend`

WORX command:

`34h`.

Sequence:

1. stop Sound Blaster DMA backend;
2. wait four BIOS ticks;
3. clear WORX hardware-mode bit `20h`;
4. return zero.

**Status: GREEN.**

---

# 5. `0x1B27C..0x1B2DF` — digital descriptor/XMS scratch

Length: **100 bytes**

Initially zero.

The sample-descriptor loaders configure XMS move destination:

```text
segment = 15BFh
offset  = 568Ch
```

which linearizes exactly to image:

`0x1B27C`.

Thus this is and conventional-memory scratch area used to materialize descriptor headers
from XMS.

**DATA/STATE GREEN.**

---

# 6. `0x1B2E0..0x1B381` — `LoadDigitalVoiceDescriptor`

Length: **162 bytes**

WORX command:

`33h`.

Input:
- source far pointer in `ES:DI`;
- digital slot/type index in `BL`.

The far pointer is normalized.

## Direct source

The normalized far pointer is stored into per-slot source fields.

## XMS-backed source

When the incoming source is represented as an XMS object:

1. select the appropriate XMS source offset from table `20C6/20C8`;
2. configure XMS source handle from `21C6`;
3. request exactly:

`0x40 = 64 bytes`

4. destination is the scratch block at image `1B27C`;
5. execute XMS function:

`AH = 0Bh` — Move Extended Memory Block.

Descriptor fields are then copied into the digital-voice runtime arrays, including:

- source/end bound;
- base rate value;
- playback/loop mode;
- loop start/end fields.

**Status: GREEN.**

---

# 7. `0x1B382..0x1B452` — `LoadVocStyleDigitalVoiceDescriptor`

Length: **209 bytes**

WORX command:

`41h`.

Like `LoadDigitalVoiceDescriptor`, the header may be read directly or copied from XMS
into the 64-byte scratch buffer.

The decisive format clue is the exact sample-rate formula:

```text
rate = 1,000,000 / (256 - timeConstant)
```

using descriptor byte:

`+1Eh`.

That is the classic **Creative VOC time-constant conversion**.

Other parsed fields include:
- sample/end bound;
- playback mode;
- optional loop bounds.

The initial playback cursor is set to:

`0x40`

which matches the WORX 64-byte descriptor/header arrangement used by this path.

This is therefore safely identified as and VOC-style digital sample descriptor loader.

**Status: GREEN.**

---

# 8. `0x1B453..0x1B4C7` — `RefillDigitalVoiceCacheFromXms`

Length: **117 bytes**

Internal helper.

For the selected voice:

1. choose its dedicated cache buffer:

`4CED + voice*0x100`;

2. set XMS transfer length:

`0x100 = 256 bytes`;

3. save current sample position as the cache-window base;
4. compute XMS source offset from:
   - per-source XMS base table;
   - current digital sample position;
5. destination is conventional memory;
6. invoke XMS move function `0Bh`.

This is the exact producer of the 256-byte per-voice caches consumed by the mixer.

**Status: GREEN.**

---

# 9. `0x1B4C8..0x1B4E7` — `ActivateDigitalVoiceFromStart`

Length: **32 bytes**

Marks selected voice active:

`active = 1`.

Sets integer sample cursor to:

`0x40`.

If the voice has no direct conventional-memory source segment,
immediately primes its 256-byte XMS cache.

**Status: GREEN.**

---

# 10. MPU-401 MIDI UART support

## `0x1B4E8..0x1B515` — `WriteMpu401DataByte`

Length: **46 bytes**

Waits until MPU status port:

`331h`

reports output-ready (`bit 6 clear`).

Writes the MIDI byte to:

`330h`.

If and WORX output callback is installed at `3896:3898`, invokes it afterward.

## `0x1B516..0x1B562` — `ResetAndEnterMpu401UartMode`

Length: **77 bytes**

WORX command:

`38h`.

Up to three attempts:

1. wait for command-ready at `331h`;
2. output:

`FFh` — reset;
3. wait for input-ready;
4. read `330h`;
5. require acknowledgement:

`FEh`;
6. wait for command-ready again;
7. output:

`3Fh` — MPU-401 UART mode.

Return:
- `0` on success;
- `FFFFh` on failure.

**Status: GREEN.**

---

# 11. `0x1B563..0x1B587` — `Load128OplInstrumentParameterRecords`

Length: **37 bytes**

WORX command:

`39h`.

Processes exactly:

`128`

source records.

For every source record:
- skip four bytes;
- copy exactly 11 bytes into the internal OPL instrument parameter table;
- skip five trailing bytes.

Thus each source record consumes exactly:

`20 bytes`.

The 11 retained bytes match the instrument parameter payload consumed by the OPL voice
programmer closed in pass 30.

The exact historical bank-file symbol is left conservative.

**Status: GREEN.**

---

# 12. `0x1B588..0x1B5B7` — RIFF/WAVE header scratch

Length: **48 bytes**

Initialized with literal chunk identifiers:

```text
RIFF
WAVE
fmt 
data
```

and zeroed numeric fields.

The WAV playback entries read the first **44 bytes** of an incoming WAV file directly
into this buffer.

Important standard fields consumed later include:
- sample rate at WAVE header offset `24`;
- data size at offsets `40..43`.

This is data/scratch, not code.

**DATA GREEN.**

---

# 13. Sound Blaster IRQ/DSP detection helpers

## `0x1B5B8..0x1B5F1` — `ShutdownSoundBlasterIrqRoute`

Length: **58 bytes**

WORX command:

`04h`.

Stops active digital DMA, restores PIC mask state and restores the previously saved
Sound Blaster IRQ vector when the hardware route is installed.

## `0x1B5F2..0x1B60D` — `SoundBlasterIrqProbeHandler`

Length: **28 bytes**

Temporary IRQ handler used during IRQ detection.

It:
- acknowledges DSP IRQ status at base+0Eh;
- sets probe-success WORD `4787 = 1`;
- sends EOI to both master and slave PIC;
- ends with `IRET`.

## `0x1B60E..0x1B62E` — `ReadSoundBlasterDspByte`

WORX command:

`50h`.

Polls DSP read status at `base+0Eh` until data is available, then reads and byte from
`base+0Ah`.

## `0x1B62F..0x1B65B` — `WriteSoundBlasterDspByte`

WORX command:

`4Fh`.

Polls `base+0Ch` until DSP write-ready, then outputs the caller byte.

**Status: GREEN.**

---

# 14. `0x1B65C..0x1B767` — `AutoDetectSoundBlasterIrq`

Length: **268 bytes**

Scans the WORX IRQ candidate tables.

For each candidate:

1. inspect the corresponding PIC mask port and save its prior value;
2. save the old IVT vector;
3. replace the vector with `SoundBlasterIrqProbeHandler`;
4. unmask the selected IRQ;
5. clear probe-success state;
6. send and fixed DSP command sequence;
7. wait three BIOS ticks;
8. test whether the IRQ probe handler executed.

On failure:
- pause the DSP;
- acknowledge PIC;
- restore the old mask and vector;
- move to the next candidate.

On success:
- preserve selected IRQ index;
- restore the permanent state required by later initialization;
- return the selected IRQ number/state with carry clear.

On complete failure:
- return `FFFFh` with carry set.

This is the low-level IRQ autodetection used by the command-01 Sound Blaster detection
path.

**Status: GREEN.**

---

# 15. `0x1B768..0x1B7BA` — `AutoDetectSoundBlasterBasePort`

Length: **83 bytes**

Scans candidate base ports:

```text
200h
210h
220h
...
2F0h
```

For each base:

1. pulse DSP reset at `base+6`;
2. poll data-ready at `base+0Eh`;
3. read response at `base+0Ah`;
4. require:

`AAh`.

On success:
- wait four BIOS ticks;
- return carry clear.

If every base below `300h` fails:
- carry set.

This is the internal base-I/O scan behind Sound Blaster autodetection.

**Status: GREEN.**

---

# 16. `0x1B7BB..0x1B7BC` — alignment/data

Length: **2 bytes**

Both zero.

**DATA GREEN.**

---

# 17. PCM capture / recording

## `0x1B7BD..0x1B808` — `BeginPcmCaptureToFile`

Length: **76 bytes**

WORX command:

`3Ch`.

Inputs include:
- output filename far pointer;
- sample rate in `BX`.

The Sound Blaster time constant is computed from:

```text
1,000,000 / sampleRate
```

and converted to:

`256 - quotient`.

The routine:

1. DOS-creates/truncates the output file (`INT 21h/AH=3Ch`);
2. stores the file handle;
3. resets DMA ring position state;
4. marks digital I/O active;
5. starts the Sound Blaster input-DMA path.

This is and raw PCM capture/file-output path at the hardware level.

## `0x1B809..0x1B852` — `ServicePcmCaptureToFile`

Length: **74 bytes**

WORX command:

`45h`.

Uses `MeasureSoundBlasterDmaProgress`.

For newly captured bytes:
- writes exactly that many bytes from the DMA buffer into the DOS file via
  `INT 21h/AH=40h`.

On write failure or short write:
- close file;
- stop DMA;
- send DSP command `D1h`;
- clear digital-I/O active state;
- return `FFFFh`.

Otherwise return zero.

**Status: GREEN.**

---

# 18. Raw PCM and WAV playback

## `0x1B853..0x1B8BF` — `StartRawPcmPlaybackFromSource`

Length: **109 bytes**

WORX command:

`3Fh`.

Inputs include:
- source path/member through the WORX source abstraction;
- sample rate in `BX`;
- one PCM mode byte in `AL`.

It:
- derives Sound Blaster time constant;
- opens the file/archive source;
- initializes and 4096-byte output/refill window;
- primes the stream through `FillDigitalStreamBuffer`;
- marks digital playback active;
- starts Sound Blaster output DMA.

## `0x1B8C0..0x1B8E5` — `StopDigitalFilePlayback`

Length: **38 bytes**

WORX command:

`3Dh`.

Stops DMA, clears playback state and closes the active DOS source handle.

Returns zero on and closed handle, `FFFFh` when no file handle was active.

## `0x1B8E6..0x1B95E` — `StartWavePlaybackFromFileOrArchive`

Length: **121 bytes**

WORX command:

`3Bh`.

1. stop prior DMA playback;
2. open WORX file/archive source;
3. read exactly **44 bytes** into the RIFF/WAVE header scratch;
4. obtain:
   - data length from offsets `40..43`;
   - sample rate from WAVE offset `24`;
5. derive Sound Blaster time constant;
6. initialize 4096-byte stream state;
7. fill initial DMA data;
8. mark active;
9. start output DMA.

## `0x1B95F..0x1B9E1` — `StartWavePlaybackFromMemory`

Length: **131 bytes**

WORX command:

`3Ah`.

The caller far memory pointer is normalized.

Its WAVE data-size field is used to derive total memory-source length:

`dataSize + 44`.

The source is then opened through the memory-backed WORX source mode,
the same 44-byte WAVE header is parsed,
and playback initialization follows the same output-DMA path.

**Status: GREEN.**

---

# 19. `0x1B9E2..0x1BA08` — `ServiceStreamedDigitalPlayback`

Length: **39 bytes**

WORX command:

`42h`.

If digital playback is active:

- selected stream modes first query current DMA progress;
- when refill is required, call `FillDigitalStreamBuffer`.

This is the periodic streaming service for raw/WAV/VOC output.

**Status: GREEN.**

---

# 20. VOC playback

## `0x1BA09..0x1BA58` — `StartVocPlaybackFromFileOrArchive`

Length: **80 bytes**

WORX command:

`05h`.

1. stop prior DMA playback;
2. open WORX file/archive source;
3. seek forward exactly:

`0x1A = 26 bytes`;

4. initialize 4096-byte stream state;
5. enter the VOC block-stream refill/parser.

The 26-byte skip matches the classic Creative VOC file header size.

## `0x1BA59..0x1BABC` — `VocExtendedBlockScratch`

Length: **100 bytes**

Initially zero.

VOC block type `8` reads its payload into this scratch area.

**DATA/STATE GREEN.**

## `0x1BABD..0x1BB04` — `StartVocPlaybackFromMemory`

Length: **72 bytes**

WORX command:

`06h`.

Uses and normalized memory-backed WORX source,
reads the 26-byte VOC prefix,
then enters the same block-stream refill parser.

## `0x1BB05..0x1BB06` — zero alignment

Length: **2 bytes**.

**DATA GREEN.**

---

# 21. `0x1BB07..0x1BC61` — `RefillVocStreamBuffer`

Length: **347 bytes**

This is the main Creative VOC block interpreter/refill routine.

The current DMA/refill region is initialized to either:
- `0x80` unsigned PCM silence; or
- zero for the alternate PCM mode.

When no block payload remains, it reads:

```text
1 byte  block type
3 bytes block length
```

from the WORX source.

Recognized block routes include:

## Type `1` — sound data

Reads:
- VOC time constant byte;
- packing/format byte.

The block payload length is reduced by the two header bytes.

The stream switches into continuation-data mode and starts/refills DMA.

## Type `2` — continuation data

Reads sample payload directly into the output buffer.

## Type `3` — silence

Reads:
- silence duration;
- VOC time constant.

The output region is filled with the configured silence byte and the stream transitions
into the timed-silence mode.

## Type `8` — extended block

Reads the block'with auxiliary payload into the 100-byte scratch at image `1BA59`.

## Type `9`

Routes to and dedicated header parser at `1BC82`.

Unsupported/unrecognized block state stops the Sound Blaster stream and returns carry
set.

This is the exact block-level connection between Creative VOC resources and the
Sound Blaster DMA output path.

**Status: GREEN.**

---

# 22. `0x1BC62..0x1BC81` — VOC type-9/header scratch

Length: **32 bytes**

Initially zero.

The type-9 block helper begins by reading its small header into this storage.

**DATA/STATE GREEN.**

---

# 23. `0x1BC82..0x1BCD7` — `HandleVocBlockType9`

Length: **86 bytes**

Called specifically for VOC block type `9`.

It reads:
- an initial rate-related WORD;
- one additional mode byte;
- and further 13-byte header payload.

The rate is converted into the Sound Blaster time-constant form used by the rest of
the digital engine.

The consumed header length is subtracted from the remaining VOC block length,
then output buffer refill and DMA playback continue.

The exact subfield names in this extended VOC header are left conservative, but the
block routing and byte counts are exact.

**Status: GREEN.**

---

# 24. `0x1BCD8..0x1BCFB` — `HandleVocContinuationPayload`

Length: **36 bytes**

Requests additional stream bytes,
then subtracts the current output-buffer size from the remaining block count.

When subtraction underflows:
- remaining block count is clamped to zero.

**Status: GREEN.**

---

# 25. `0x1BCFC..0x1BD39` — `FillDigitalStreamBuffer`

Length: **62 bytes**

Common streamed digital-audio payload reader.

The request length begins with configured output-window size (`48DB`)
and is clamped to the remaining 32-bit block payload length.

If nonzero:
- destination is current Sound Blaster DMA buffer + ring offset;
- data comes from `ReadWorxDataSourceChunk`.

After reading:
