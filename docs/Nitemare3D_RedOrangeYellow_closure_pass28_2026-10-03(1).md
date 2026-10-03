# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 28

Date: 2026-10-03

Primary unpacked reference:
- `N3D_DOS_v2.0_IDA.EXE`
- physical MZ header: `0x1C00`
- unpacked load image: `0x29D60 = 171,360 bytes`
- unpacked-image SHA-256:
  `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`

Address convention:
- all ranges below are offsets in the fully unpacked load image
- physical file offset = image offset + `0x1C00`
- raw 16-bit machine code is authoritative
- third-party library/platform code is classified separately from N3D-owned gameplay

## Result

Pass 28 corrects the previous assumption that executable code ended at `0x15BF6`.

Raw relocation/call analysis proves that Nitemare-3D contains an **embedded WORX
Toolkit v2.1 runtime/driver module** after the Microsoft CRT tail.

The complete embedded module region:

`0x15BF7 .. 0x1BDA1`

can be classified as:

**GREEN / identified third-party DOS audio-device module + its code/data workspace**

Total span:

**25,003 bytes**

The executable portion is interleaved with module tables and state; the main code run
is approximately:

`0x18A05 .. 0x1BD92`

while earlier bytes contain large initialized lookup/buffer areas and toolkit metadata.

This is not hidden Nitemare gameplay logic.

---

# 0. Correction to pass 27

Pass 27 stated that the executable-code run stopped after `0x15BF6`.

That is true only for the **Microsoft CRT/compiler-helper family**.

It is not true for the whole DOS load image.

Two direct N3D far calls prove executable code later in the image:

```text
image 0x11A6A:
    CALL FAR 15BF:2E7D
    -> linear image 0x18A6D

image 0x10C6C:
    CALL FAR 15BF:2F66
    -> linear image 0x18B56
```

These are the toolkit initialization and shutdown entries.

Therefore:

`0x15BF7+`

must not be treated as one monolithic data region.

---

# 1. Toolkit identity — direct binary string

At image offset approximately:

`0x187FD`

the executable contains the null-terminated vendor string:

```text
WORX TOOLKIT VERSION 2.1 COPYRIGHT 1993 BY MYSTIC SOFTWARE
```

This is direct binary ownership evidence.

The previously closed N3D wrapper layer at `0x10BFC..0x11EE6` talks to this module
through `INT 63h`.

The architecture is now:

```text
Nitemare game/audio manager
    ↓
0x10BFC..0x11EE6 WORX command wrappers
    ↓
INT 63h
    ↓
embedded WORX Toolkit implementation
    0x15BF7..0x1BDA1
```

---

# 2. `0x15BF7..0x17BFF` — initialized 0x80-filled audio area

After seven zero bytes, the image contains:

`0x15BFE..0x17BFF`

= **8,194 consecutive bytes of `0x80`**.

`0x80` is the neutral midpoint normally used by unsigned 8-bit PCM audio.

Because this range sits inside the WORX module and later WORX code manages DMA/SFX
buffers, the safest map label is:

`WORX initialized audio buffer/table area`.

For the byte map the important classification is:

- DATA, not executable code;
- third-party audio-module ownership;
- no N3D gameplay semantics hidden here.

**Status: former UNKNOWN/DATA ambiguity -> GREEN + DATA overlay.**

---

# 3. `0x17C00..0x18A04` — WORX lookup/configuration tables

This band contains non-code toolkit data and lookup tables.

Evidence includes:

- dense signed/unsigned numeric tables;
- long zero-filled table sections;
- hardware/audio lookup values;
- the WORX Toolkit v2.1 vendor string at `0x187FD`;
- state/configuration values immediately preceding the first internal helper code.

It should be classified as:

`GREEN / WORX static DATA/TABLES`

rather than disassembled as N3D functions.

---

# 4. `0x18A05..0x18A6C` — internal utility helpers

The first obvious executable helpers include:

- byte/string movement utility;
- BIOS `INT 1Ah` timing delay;
- short internal buffer-copy/state helpers;
- one-byte toolkit flag setter.

They use near `RET`, showing that they are internal routines within the embedded WORX
code segment rather than N3D far-callable API functions.

**Status: WORX internal code -> GREEN platform dependency.**

---

# 5. `0x18A6D` — `InitializeWorxResidentDriver`

This is the far entry called directly by Nitemare at image `0x11A6A`.

Major raw operations:

1. save all major registers and segment registers;
2. disable interrupts;
3. clear toolkit runtime state;
4. obtain old `INT 63h` vector:
   - `INT 21h AH=35h AL=63h`;
5. save that vector inside WORX state;
6. install WORX `INT 63h` handler:
   - `INT 21h AH=25h AL=63h`
   - handler offset `0x30E6` in the current code segment;
7. initialize hardware/device state;
8. obtain old `INT 08h` vector;
9. install WORX timer handler at offset `0x4150`;
10. perform hardware/audio initialization;
11. restore registers and return far.

Linear handler addresses under the module segment:

```text
INT 63h handler:
15BF:30E6 -> image 0x18CD6

INT 08h handler:
15BF:4150 -> image 0x19D40
```

This establishes the embedded module as and resident interrupt-driven DOS sound/device
runtime.

**Status: GREEN / exact platform lifecycle role.**

---

# 6. `0x18B56` — `ShutdownWorxResidentDriver`

This is the far entry called directly from the N3D WORX shutdown wrapper.

It:

1. disables interrupts;
2. calls internal device shutdown helpers;
3. restores the saved `INT 08h` vector;
4. restores the saved `INT 63h` vector;
5. invokes an optional toolkit callback when installed;
6. restores all registers;
7. re-enables interrupts;
8. returns far.

This closes the installation/restoration pair:

```text
18A6D  install/init WORX
18B56  stop/restore WORX
```

**Status: GREEN.**

---

# 7. `0x18CD6` — resident `INT 63h` command handler

`InitializeWorxResidentDriver` installs:

`CS:30E6`

as interrupt vector 63h.

With module CS `0x15BF`, this maps to:

`0x18CD6`.

This is the resident side of the command ABI previously closed at `0x10BFC`.

The handler dispatches WORX command registers to the module'with music/SFX/input/device
subsystems.

For N3D reconstruction this confirms that `INT 63h` is not and BIOS/DOS service guessed
by the game: it is installed dynamically by the embedded WORX library itself.

**Status: GREEN / resident command dispatcher.**

---

# 8. OPL/AdLib hardware path

Internal code beginning around `0x18C0D` directly accesses:

```text
port 388h
port 389h
```

and performs the classic status/register delay/read/write pattern.

This is the AdLib/OPL hardware branch of the WORX module.

The exact user-facing music synthesis path can be replaced by and modern MIDI/OPL
backend in and portable reconstruction, but the historical DOS binary clearly contains
the original direct-port implementation.

**Status: GREEN / hardware backend.**

---

# 9. PC-speaker / PIT path

The embedded module directly accesses:

```text
port 43h  PIT control
port 42h  PIT channel 2
port 61h  speaker gate/control
```

in routines around the `0x191xx..0x197xx` area.

This statically identifies the fallback speaker path that the N3D-side wrapper layer
already exposes through separate start/stop/status WORX commands.

**Status: GREEN / PC-speaker backend.**

---

# 10. IRQ/PIC/DMA hardware support

The module contains direct accesses to:

```text
port 20h / 21h
port A0h
DMA/PIC control ports through DX-selected I/O
```

and installs/restores interrupt vectors through DOS `INT 21h AH=25h/35h`.

The code around `0x1A2xx..0x1A5xx` contains timer/PIC/DMA setup and transfer-support
logic used by digitized SFX.

This is third-party platform code, not unexplained gameplay.

**Status: GREEN / DOS hardware-support layer.**

---

# 11. `0x19D40` — WORX timer IRQ handler

The install routine programs `INT 08h` to:

`CS:4150 -> image 0x19D40`.

The handler services WORX timing/audio state and acknowledges the interrupt controller.

This is separate from Nitemare'with own later RTC/INT70 timing subsystem.

Therefore the byte map should not merge:

- WORX INT08 device timing;
- N3D RTC INT70 game clock.

They are two independent interrupt-driven systems.

**Status: GREEN / WORX ISR.**

---

# 12. `0x1B590` — WAVE format support

The module contains literal:

```text
WAVEfmt 
```

near image `0x1B590`.

The surrounding executable code parses/handles waveform resource descriptors and feeds
the toolkit'with SFX playback state.

This independently confirms that the late `1Bxxx` region still belongs to the embedded
audio toolkit rather than arbitrary application data.

---

# 13. `0x1B0F2..0x1BD92` — mixer/resource/playback engine

The late toolkit code contains:

- channel state arrays;
- per-channel cursor/rate/volume state;
- audio-buffer fill loops;
- resource/buffer descriptors;
- WAVE parsing support;
- volume/rate conversion;
- hardware-transfer preparation;
- command completion/state changes;
- diagnostic/internal display support.

The code remains within the same `15BF` module segment and calls the same internal
hardware/timer helpers.

For portable behavioral reconstruction this can be represented as one historical
audio-backend module behind the already closed WORX compatibility interface.

**Status: GREEN / third-party audio engine.**

---

# 14. `0x1BD3A..0x1BD49` — hexadecimal digit table

Literal:

```text
0123456789ABCDEF
```

Immediately afterward, `0x1BD4A..0x1BD92` contains an internal routine that converts and
WORD into four hexadecimal digits and writes them to text-mode video memory:

`segment B000h`.

This is toolkit diagnostic/debug support.

The final executable `RET` is at:

`0x1BD92`.

Bytes `0x1BD93..0x1BDA1` are trailing module data/pointers.

---

# 15. Revised code/data map

The correct map of this region is:

```text
15BF7–17BFF  WORX initialized buffer/table data
17C00–18A04  WORX lookup/config/static data
18A05–1BD92  WORX executable code with small inline tables/state
1BD93–1BDA1  WORX trailing data
```

Whole owned span:

`15BF7–1BDA1 = 25,003 bytes`

All should be GREEN for ownership/static subsystem knowledge, with DATA/TABLE overlays
where applicable.

The important distinction is:

- **not N3D gameplay**
- **not Microsoft CRT**
- **not arbitrary UNKNOWN bytes**
- **embedded WORX Toolkit v2.1**

---

# 16. Byte-map consequence

Pass 27 cumulative promoted bytes:

`65,788`

Pass 28 newly reclassifies:

`25,003 bytes`

as known WORX module bytes.

Working cumulative promoted/reclassified total:

**90,791 bytes**

This cumulative number is now based on the unpacked load-image map and includes:

- N3D game code;
- Microsoft CRT/runtime;
- WORX wrapper API;
- embedded WORX implementation/data.

It should no longer be compared directly with the earlier packed-EXE `116,094-byte`
census without and fresh unified recensus.

---

# 17. Next target

The next bytes begin at:

`0x1BDA2`

AND large zero/workspace area follows, but it is interrupted by several nonzero static
data islands and known far-data segments (`1D0F`, `20B9`, `21FD`) before DGROUP at
`0x27710`.

The next useful pass should classify that memory-layout region as:

- initialized data;
- zero/BSS-style reserved buffers;
- N3D/WORX fixed arenas;
- font/resource/gameplay memory segments;

and should not try to disassemble zero/data buffers as code.