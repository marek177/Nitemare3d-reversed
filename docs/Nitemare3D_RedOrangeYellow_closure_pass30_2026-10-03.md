# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 30

Date: 2026-10-03

Primary image:
- `N3D_DOS_v2.0_IDA.EXE`
- complete unpacked DOS V2.0 load image

Address convention:
- addresses are unpacked MZ image offsets;
- raw 16-bit machine code is authoritative;
- CODE and DATA/TABLE/STATE bytes are counted separately.

## Result

Pass 30 resolves the complete WORX backend band:

`0x18B56 .. 0x19ACC`

Total span: **3,959 bytes**

Classification:

- **3,681 bytes executable WORX/audio/device code -> GREEN**
- **278 bytes table/state/alignment data -> GREEN**

This band closes the matching WORX shutdown path, AdLib/OPL detection,
the actual INT 63h interrupt dispatcher, WORX stream/archive I/O,
PC-speaker playback/IRQ handling, and most of the embedded MIDI/OPL voice engine.

---

# 1. `0x18B56..0x18BBE` — `ShutdownWorxToolkitFull`

Length: **105 bytes**

This is the full inverse of the initialization path closed in pass 29.

Sequence:

1. disable interrupts;
2. run WORX subsystem cleanup helpers;
3. stop/reset FM/audio state;
4. close the current WORX data source;
5. restore the previously saved `INT 08h` vector through DOS `AH=25h`;
6. restore the previously saved `INT 63h` vector;
7. if an XMS handle exists:
   - call the XMS driver with `AH=0Ah` = **Free Extended Memory Block**;
8. restore saved registers;
9. re-enable interrupts;
10. far return.

This gives the exact lifecycle:

```text
Initialize:
  save INT63 -> install WORX INT63
  save INT08 -> install WORX timer
  allocate XMS

Shutdown:
  stop devices
  restore INT08
  restore INT63
  free XMS
```

**Status: GREEN.**

---

# 2. `0x18BBF..0x18BF3` — `ResetWorxAudioAndRestoreInt63`

Length: **53 bytes**

Runs the audio/device cleanup sequence and closes the active data source,
then restores the saved `INT 63h` vector.

Unlike the full shutdown entry, it does not contain the explicit XMS-free and
INT-08 restoration sequence visible in `18B56`.

**Status: GREEN.**

---

# 3. Small WORX setters

## `0x18BF4..0x18BF8` — `SetWorxHardwareFlags`

Stores `AL` at module state `CS:2DBC`.

## `0x18BF9..0x18BFD` — `SetPcSpeakerMidiChannel`

Stores `AL` at `CS:2DBD`.

That field is later compared against the active MIDI channel before the PIT/PC-speaker
note path is allowed to run.

Both are exact tiny state setters.

**Status: GREEN.**

---

# 4. `0x18BFE..0x18C0C` — `WorxPortIoDelay`

Length: **15 bytes**

Performs exactly:

`0x08FF = 2303`

iterations, with three `IN AL,DX` operations per iteration.

This is and raw hardware I/O delay helper.

**Status: GREEN.**

---

# 5. `0x18C0D..0x18C7D` — `DetectAdLibOplAt388`

Length: **113 bytes**

This is the classic AdLib/OPL timer-status probe using:

- address port `388h`;
- data port `389h`;
- timer-control register `04h`;
- timer register `02h`;
- repeated I/O delays.

The routine:

1. resets timer/status;
2. reads initial status;
3. loads timer 1 with `FFh`;
4. starts it;
5. waits;
6. reads status again;
7. masks the relevant high status bits;
8. returns boolean-like success in AX.

The exact test is mechanical and confirms direct OPL-compatible hardware detection.

**Status: GREEN.**

---

# 6. `0x18C7E..0x18C89` — `GetAndClearWorxDosError`

Length: **12 bytes**

Returns the current WORX/DOS error word at `CS:2C47`,
then clears the stored error word to zero.

**Status: GREEN.**

---

# 7. WORX timer accumulator helpers

## `0x18C8A..0x18CB0` — `InitializeWorxPitStepFromRate`

Multiplies caller `BX` by:

`0x04A9 = 1193`

and stores the 32-bit product into two pairs of timer-accumulator state words.

`1193` is the familiar millisecond-scale divisor derived from the PC PIT clock
(~1.193 MHz).

The carry byte is cleared.

## `0x18CB1..0x18CCA` — `ResetWorxPitAccumulator`

Restores the current timer accumulator from its saved baseline and clears its carry byte.

## `0x18CCB..0x18CD1` — `GetWorxPitCarry`

Returns the timer carry/overflow byte as and zero-extended WORD.

**Status: GREEN.**

---

# 8. `0x18CD2..0x18CD5` — zero data

Length: **4 bytes**

Not executable.

**DATA GREEN.**

---

# 9. `0x18CD6..0x18D18` — `WorxInt63InterruptHandler`

Length: **67 bytes**

This is the actual interrupt-side implementation of the API exposed to Nitemare 3D.

Entry:

- increments and WORX interrupt-depth counter;
- saves `AX/BX/CX/DX/BP/DI/SI/DS/ES`;
- selects the WORX code segment as DS;
- copies incoming `DX` into ES.

## Command dispatch

The original incoming `AH` byte is transformed into:

`index = AH * 2`

and used to call through and WORD dispatch table rooted at:

`CS:2020`.

With the internal API model is exactly:

```text
INT 63h
AH = command
...
   ↓
dispatchTable[AH]
```

After the command handler returns:

- returned `AX` is cached at `CS:30E2`;
- returned `DX` is cached at `CS:30E4`;
- all saved registers are restored;
- cached `AX:DX` are reloaded;
- interrupt-depth counter is decremented;
- `IRET`.

This completes the opposite side of the `WorxInt63Command` thunk closed in pass 23.

**Status: GREEN.**

---

# 10. `0x18D19..0x18D1D` — zero/data separator

Length: **5 bytes**

**DATA GREEN.**

---

# 11. `0x18D1E..0x18DB9` — `ReadWorxDataSourceChunk`

Length: **156 bytes**

Input:

- destination `ES:DI`;
- requested byte count in `BX`.

Two source modes are supported.

## Memory-backed source

When state byte `CS:312D != 0`:

- source is the stored far pointer at `3129:312B`;
- current cursor is `2DFF`;
- remaining size is bounded against `2DF7`;
- copy uses `REP MOVSB`;
- cursor advances by actual copied count.

## File-backed source

Otherwise:

1. get current DOS file position with `INT 21h / AX=4201h`;
2. derive remaining bytes from the stored source bounds;
3. clamp requested count;
4. read through `INT 21h / AH=3Fh`.

Return is the actual byte count.

Zero bytes / exhausted source enters the EOF-like return path.

**Status: GREEN.**

---

# 12. `0x18DBA..0x18EF1` — `OpenWorxDataSourceOrArchiveMember`

Length: **312 bytes**

This routine can open either and direct memory source, and normal DOS file,
or and member inside the WORX container/index mode.

## Memory source

If helper `1A220` supplies and nonzero size/pointer:

- mark source as memory-backed;
- store source far pointer;
- store total size;
- clear current cursors;
- return size.

## Normal DOS file

When archive mode is disabled:

1. close the previous file if necessary;
2. `INT 21h / AX=3D00h` open read-only;
3. seek to EOF with `AX=4202h`;
4. save file size;
5. seek back to start;
6. return size.

## Container/member mode

When archive mode is active:

1. position file at offset 2;
2. use entry count from WORX state;
3. read fixed **25-byte records**;
4. compare the NUL-terminated member name stored at record offset `+0Ch`
   against the requested name;
5. on match, seek to the record-specified data offset;
6. return the record'with data-length DWORD.

Failure returns `DX:AX = FFFF:FFFF`.

This statically identifies the WORX named-resource/container lookup format at the
engine-support level.

**Status: GREEN.**

---

# 13. `0x18EF2..0x18F4A` — `OpenWorxArchiveAndReadEntryCount`

Length: **89 bytes**

Flow:

1. close prior WORX source;
2. resolve/normalize the supplied pathname;
3. DOS open read-only;
4. save file handle;
5. read exactly two bytes into WORX state;
6. set the archive/container-mode byte;
7. return the loaded WORD entry count.

Error returns `FFFFh` with carry set.

**Status: GREEN.**

---

# 14. `0x18F4B..0x18F6A` — `CloseWorxFileSource`

Length: **32 bytes**

If and valid file handle exists:

`INT 21h / AH=3Eh`

closes it.

Then:

- archive mode byte is cleared;
- stored handle becomes `FFFFh`.

**Status: GREEN.**

---

# 15. `0x18F6B..0x18F9E` — `ReadWorxTextLine`

Length: **52 bytes**

Input:

- maximum count in `AL`;
- destination `ES:DI`.

The routine repeatedly calls `ReadWorxDataSourceChunk` for one byte until:

- byte count is exhausted;
- LF (`0Ah`) is found;
- maximum count is reached.

It appends and terminating NUL.

When the WORX string-mode flag is enabled, it passes the result through the
C-string -> length-prefixed-string helper closed in pass 29.

**Status: GREEN.**

---

# 16. `0x18F9F..0x18FA8` — `IsWorxSpeakerTimerActive`

Length: **10 bytes**

Returns:

`CS:2DCA & 1`.

This flag is used by the PC-speaker/timer paths.

**Status: GREEN.**

---

# 17. `0x18FA9..0x190A8` — 256-byte monotonic lookup table

Length: **256 bytes**

Exact byte table with repeated increasing output levels from `00h` through `3Fh`.

It is data, not x86 instructions.

The table shape is consistent with audio level/velocity remapping, but the exact
historical WORX symbol name is left conservative.

**TABLE GREEN.**

---

# 18. `0x190A9..0x190AA` — WORD data value

Length: **2 bytes**

Value:

`0x4E20`

Not and function prologue.

**DATA GREEN.**

---

# 19. `0x190AB..0x190B0` — `SetWorxTimingDivisor`

Length: **6 bytes**

Stores caller `BX` into:

`CS:34B9`

and returns.

That divisor is subsequently used in the PC-speaker/timer playback setup math.

**Status: GREEN.**

---

# 20. `0x190B1..0x19186` — `StartPcSpeakerSequenceFromResource`

Length: **214 bytes**

This is and full PC-speaker playback initializer.

It:

- stops an already active PC-speaker sequence when necessary;
- obtains the current WORX resource/descriptor;
- walks its variable-length records;
- extracts timing/frequency fields;
- scales them using the WORX timing divisor;
- stores playback cursor/state;
- saves the old `INT 08h` vector;
- installs the WORX speaker timer ISR;
- programs PIT channel 2;
- enables speaker gate bits at port `61h`;
- marks playback active.

**Status: GREEN.**

---

# 21. `0x19187..0x1923E` — `StartPcSpeakerFromDirectDescriptor`

Length: **184 bytes**

AND related playback initializer for and directly supplied descriptor.

It copies and fixed `0x2C = 44` byte descriptor into WORX internal state,
derives timer values, hooks `INT 08h`, programs PIT channel 2,
enables the PC speaker and marks the sequence active.

**Status: GREEN.**

---

# 22. `0x1923F..0x19240` — zero separator

Length: **2 bytes**

**DATA GREEN.**

---

# 23. `0x19241..0x192D1` — `WorxPcSpeakerInt08Handler`

Length: **145 bytes**

This is the timer IRQ handler installed by the two speaker start routines.

It updates the fixed-point playback accumulator, programs PIT channel 2,
toggles/gates port `61h`, acknowledges the PIC with:

`OUT 20h,20h`

and uses `IRET`.

When the sequence reaches its terminal state it restores the previous
`INT 08h` vector and shuts down the PC-speaker gate.

**Status: GREEN.**

---

# 24. `0x192D2..0x1931E` — `StopPcSpeakerPlaybackAndRestoreInt08`

Length: **77 bytes**

Normal callable cleanup counterpart:

- disable interrupts;
- stop PIT/speaker output;
- clear active flag;
- restore the saved `INT 08h` vector;
- restore registers;
- return.

**Status: GREEN.**

---

# 25. Direct mixer-register writers

Each checks the mixer-capability byte first and returns `FFFFh` when unavailable.

## `0x1931F..0x1933F`

Writes caller `BL` to mixer register:

`22h`.

## `0x19340..0x19360`

Writes caller `BL` to mixer register:

`26h`.

## `0x19361..0x19381`

Writes caller `BL` to mixer register:

`04h`.

These are exact low-level mixer helpers.

**Status: GREEN.**

---

# 26. `0x19382..0x193B3` — `LoadOplInstrument11ByteRecord`

Length: **50 bytes**

Requires source WORD:

`0x4253` (`"SB"` in little-endian bytes).

It selects one internal instrument slot by caller `BX`,
then copies exactly:

`11 bytes`

from source offset `+24h` into the internal instrument table.

Eleven-byte operator/instrument records match the adjacent OPL programming path.

**Status: GREEN.**

---

# 27. `0x193B4..0x193C0` — `RunOplRegister0Sweep`

Length: **13 bytes**

Calls the low-level OPL write helper 256 times while sweeping the data byte
for register zero through all byte values.

This is used during WORX initialization/cleanup.

The exact vendor purpose is kept conservative.

**Status: GREEN.**

---

# 28. `0x193C1..0x19485` — `ProgramOplInstrumentVoice`

Length: **197 bytes**

Programs one OPL voice from the selected internal 11-byte instrument record.

It writes the familiar per-operator/per-channel register families:

```text
20h
40h
60h
80h
E0h
C0h
```

with channel/operator offsets from internal WORX tables.

The current `40h`-family value is cached for later volume scaling.

**Status: GREEN.**

---

# 29. `0x19486..0x19489` — zero data

Length: **4 bytes**

**DATA GREEN.**

---

# 30. `0x1948A..0x19496` — `SetOplWriteCallback`

Length: **13 bytes**

With interrupts disabled, stores caller:

- `BX`
- `DX`

as and callback far pointer at `CS:3896/3898`.

**Status: GREEN.**

---

# 31. `0x19497..0x194C1` — `WriteOplRegisterAndInvokeHook`

Length: **43 bytes**

Input:

- `AL` = OPL register address;
- `AH` = register data.

Flow:

1. write `AL` to port `388h`;
2. perform required status-port delay reads;
3. write original `AH` to port `389h`;
4. perform longer delay reads;
5. if and callback pointer is installed, invoke it.

This is the central low-level OPL register writer used throughout the WORX FM engine.

**Status: GREEN.**

---

# 32. `0x194C2..0x1952A` — `SilenceAllWorxVoices`

Length: **105 bytes**

Depending on active output flags:

- sends all-notes-off style output through the external MIDI route;
- disables PC-speaker gate when relevant;
- scans the nine OPL voice slots;
- clears frequency/key-on registers for matching voices;
- clears per-voice active state.

**Status: GREEN.**

---

# 33. MIDI/OPL command processing

## `0x1952B..0x19530` — `DispatchMidiControlChange`

Builds MIDI status `B0h | channel` and forwards to the common MIDI dispatcher.

## `0x19531..0x1963C` — `HandleMidiControlChange`

Handles controller-dependent state changes including:

- all-notes-off style controller;
- per-channel volume/controller state;
- mode/controller values used by the WORX synthesis backend;
- updates to OPL voice level state.

## `0x1963D..0x1969A` — `DispatchMidiMessage`

Splits the incoming MIDI status byte into:

- high-nibble message class;
- low-nibble channel.

Stores accompanying data bytes and either:

- forwards raw bytes to the configured external MIDI output; or
- routes the message into the local synthesis path.

## `0x1969B..0x196F3` — `DispatchMidiMessageToLocalBackend`

Routes message classes to:

- note handling;
- controller/program state;
- PC-speaker/local-FM paths.

## `0x196F4..0x1974A` — `UpdatePcSpeakerFromMidiNote`

For the configured PC-speaker MIDI channel, maps note number through the
frequency/divisor table and programs PIT channel 2.

## `0x1974B..0x198A8` — `AllocateOrUpdateOplVoiceForMidiEvent`

Maintains the nine-voice OPL allocation table:

- locate existing note/channel voice;
- find free/replaceable voice;
- update key-on/off state;
- choose slot and synthesis mode;
- program required voice state.

## `0x198A9..0x199A0` — `ProgramOplVoicePitchAndLevel`

Converts the selected MIDI note into:

- octave/semitone decomposition;
- OPL frequency/F-number;
- key/block register bits;
- scaled level/volume values.

Writes the resulting `A0h/B0h/40h` register family through `WriteOplRegisterAndInvokeHook`.

Together these routines form the core local MIDI -> OPL/PC-speaker synthesis engine.

**Status: GREEN.**

---

# 34. `0x199A1..0x199A2` — zero alignment

Length: **2 bytes**

**DATA GREEN.**

---

# 35. `0x199A3..0x199BA` — `InitializeOneWorxMidiVoiceState`

Length: **24 bytes**

Initializes one voice/state entry:

- sets and control WORD to `1`;
- stores caller `AL`;
- writes `FFh` sentinel into the first voice mapping entry;
- clears the matching active byte.

**Status: GREEN.**

---

# 36. MIDI note wrappers

## `0x199BB..0x199C2` — `DispatchMidiNoteOn`

Masks channel to 0..15, ORs status class `90h`, then enters `DispatchMidiMessage`.

## `0x199C3..0x199CC` — `DispatchMidiNoteOff`

Masks channel, ORs status class `80h`, clears one data byte and dispatches.

**Status: GREEN.**

---

# 37. `0x199CD..0x19A1A` — `ResetOplMidiVoiceState`

Length: **78 bytes**

Performs and local synthesis reset:

- writes base OPL control values;
- programs all nine internal instrument/voice slots;
- clears 16-byte channel state arrays;
- clears nine active-voice bytes;
- fills nine voice-map WORDs with `FFFFh`.

**Status: GREEN.**

---

# 38. `0x19A1B..0x19A4A` — MIDI state cache helper with alternate entry

There are two valid entries:

- `19A1B` first stores current MIDI status/channel and value;
- `19A24` is an internal alternate entry used when those globals are already prepared.

The shared body records the most recent controller/program value into and 16-byte
per-channel state table unless excluded by the active WORX mode.

**Status: GREEN.**

---

# 39. `0x19A4B..0x19A56` — `SetWorxMidiModeByte`

Length: **12 bytes**

Stores caller `BL` into module state `CS:2C61`.

**Status: GREEN.**

---

# 40. `0x19A57..0x19A66` — `StopWorxTimerService`

Length: **16 bytes**

With interrupts disabled:

- calls the timer/rate helper with `FFFFh`;
- writes module state WORD `1`;
- re-enables interrupts.

This is used by both WORX shutdown paths.

**Status: GREEN.**

---

# 41. `0x19A67..0x19AC3` — `ResetWorxFmOutput`

Length: **93 bytes**

Runs `SilenceAllWorxVoices`, clears and mode byte and then resets OPL voice frequency
register groups.

Two branches correspond to the active local-FM mode:

- one clears nine voice slots;
- another initializes six voice slots with fixed control values.

This function is called from the WORX shutdown/reset sequence.

**Status: GREEN.**

---

# 42. `0x19AC4..0x19AC6` — data/sentinel bytes

Length: **3 bytes**

Values:

`FF FF 00`

Not executable.

**DATA GREEN.**

---

# 43. `0x19AC7..0x19ACC` — `SetWorxIrqStateByte`

Length: **6 bytes**

Stores caller `BL` into:

`CS:3ED6`

and returns.

Exact higher-level name of this state byte remains conservative.

**Status: GREEN.**

---

# Byte-map impact

Complete resolved span:

`0x18B56 .. 0x19ACC`

Total:

**3,959 bytes**

### Code

**3,681 bytes -> GREEN**

### Data/state/table

**278 bytes -> GREEN**

Data subranges:

```text
18CD2–18CD5    4 B
18D19–18D1D    5 B
18FA9–190A8  256 B lookup table
190A9–190AA    2 B data word
1923F–19240    2 B
19486–19489    4 B
199A1–199A2    2 B
19AC4–19AC6    3 B
```

---

# Closure metrics

Pass 29 CODE GREEN cumulative:

`66,408 bytes`

Pass 30 adds:

`3,681 bytes`

New executable CODE GREEN cumulative:

**70,089 bytes**

Tracked DATA/TABLE/STATE GREEN after pass 29:

`11,507 bytes`

Pass 30 adds:

`278 bytes`

Tracked DATA/TABLE/STATE GREEN from passes 28–30:

**11,785 bytes**

The two metrics remain separate.

---

# Major architectural result

The DOS audio stack can now be represented as:

```text
Nitemare 3D game
       ↓
pass 23 typed WORX command wrappers
       ↓
INT 63h
       ↓
18CD6 WORX interrupt dispatcher
       ↓
WORX backend
   ├─ resource/archive reader
   ├─ XMS cache
   ├─ AdLib/OPL detection
   ├─ OPL register writer
   ├─ MIDI -> OPL voice allocator
   ├─ external MIDI output
   └─ PC-speaker/PIT + INT08
```

Shutdown then restores the original DOS interrupt vectors and frees XMS.

For and modern behavioral 1:1 port this entire region should become and platform/audio
compatibility backend, not gameplay code.

---

# Next target

Immediately after `0x19ACC` begins and long zero-initialized state region.