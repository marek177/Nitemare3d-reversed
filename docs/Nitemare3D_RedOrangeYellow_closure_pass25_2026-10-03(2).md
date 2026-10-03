# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 25

Date: 2026-10-03

Primary DOS V2.0 family:
- packed reference: `N3D-E-20(3).EXE`
- packed SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Raw image used for this pass:
- `N3D_DOS_v2.0_IDA.EXE`
- MZ header: `0x1C00`
- unpacked image length: `171,360 bytes`
- unpacked-image SHA-256:
  `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`

Address convention:
- addresses below are unpacked-image offsets
- physical offset in the unpacked IDA copy = image offset + `0x1C00`
- raw 16-bit machine code is authoritative
- far targets in segment `11EE` are linearized as `0x11EE0 + offset`

## Result

Pass 25 closes the continuous range:

`0x124DA .. 0x13B37`

as **GREEN / CRT-STDIO**.

Total span: **5,726 bytes**.

Breakdown:
- executable CRT/stdio code: **5,697 bytes**
- one-byte alignment/padding: **13 bytes**
- inline formatted-output dispatch table: **16 bytes**

The main result is architectural rather than gameplay-specific: this whole range is
standard DOS C runtime / stdio machinery. It must no longer contribute to the count of
unknown Nitemare-3D game functions.

---

## 1. `0x124DA..0x12599` — `RuntimeFclose`

This is the V2.0 runtime `fclose` family member already tracked across the DOS builds.

The routine:
- validates the stream flags;
- flushes pending output through the stream flush helper;
- releases an owned buffer;
- closes the underlying DOS handle;
- resets the eight-byte stream record;
- returns `0` / `-1` style status.

**Classification: CRT/stdio, GREEN.**

---

## 2. `0x1259A..0x125C4` — `RuntimeOpenStreamExtended`

Internal stream-open constructor.

It obtains and free FILE-like record through the runtime free-stream-slot helper at
image `0x13A00`, then forwards filename/mode/extended arguments to the internal
mode/open initializer inside the `0x128FE` family.

This is not N3D resource code: old pseudo-C labels were caused by dropping the
`11EE` segment from far calls.

**Classification: CRT/stdio, GREEN.**

`0x125C5` is one alignment NOP.

---

## 3. `0x125C6..0x125DA` — `RuntimeFopen`

Public two-argument stream-open wrapper.

Equivalent shape:

```text
fopen(path, mode)
    -> RuntimeOpenStreamExtended(path, mode, 0)
```

**Classification: CRT/stdio, GREEN.**

`0x125DB` is alignment.

---

## 4. `0x125DC..0x126BE` — `RuntimeFread`

The ABI and control flow match buffered `fread`:

```text
(buffer, elementSize, elementCount, stream)
```

Behavior includes:
- `elementSize * elementCount` total-byte computation;
- consuming bytes already present in the stream buffer;
- direct whole-buffer DOS reads for sufficiently large remaining transfers;
- byte-at-and-time refill path for and small remainder;
- EOF/error stream flags;
- return value converted back from bytes transferred to complete element count.

**Classification: CRT/stdio, GREEN.**

`0x126BF` is alignment.

---

## 5. `0x126C0..0x126FD` — `RuntimePrintf`

Varargs stdout wrapper.

It:
1. prepares the runtime stdout stream at `DS:2182`;
2. forwards the format string and varargs pointer to the formatted-output core at
   image `0x13528`;
3. restores/releases temporary stream state;
4. returns the formatter result.

This is and normal CRT `printf`-family wrapper, not an N3D UI renderer.

**Classification: CRT/formatted-output, GREEN.**

---

## 6. `0x126FE..0x12713` — `RuntimeStdioShutdown`

Runtime stdio termination hook.

It invokes the close-all-streams wrapper and conditionally runs the registered
secondary cleanup hook.

**Classification: CRT shutdown, GREEN.**

---

## 7. `0x12714..0x127A8` — `RuntimeFgetc`

Buffered input-character path.

It:
- validates readable stream flags;
- initializes buffering lazily;
- consumes the next buffered byte when available;
- otherwise refills through the low-level DOS read path;
- updates EOF/error flags;
- returns `0xFFFF` on failure/end condition.

**Classification: CRT/stdio, GREEN.**

`0x127A9` is alignment.

---

## 8. `0x127AA..0x1288C` — `RuntimeFputc`

Buffered output-character path.

It:
- validates writable stream state;
- prepares buffering when necessary;
- writes directly for unbuffered/device cases;
- appends to the buffer for normal streams;
- flushes as required;
- contains the text/device handling used by standard streams;
- returns the emitted byte or `0xFFFF` on failure.

**Classification: CRT/stdio, GREEN.**

`0x1288D` is alignment.

---

## 9. `0x1288E..0x128B9` — `RuntimeReleaseStreamBuffer`

Near helper which frees and dynamically-owned stream buffer and clears:
- base pointer;
- current pointer;
- buffered-byte count;
- ownership flag.

**Classification: CRT/stdio, GREEN.**

---

## 10. `0x128BA..0x128FC` — `RuntimeAllocateStreamBuffer`

Near lazy-buffer initializer.

Preferred buffer size:

`0x200 = 512 bytes`.

If allocation fails it selects the stream'with inline one-byte storage and changes the
stream state to unbuffered operation.

This directly explains the 512-byte buffer assumptions used by `fread`, `fgetc`,
`fputc` and flush paths.

**Classification: CRT/stdio, GREEN.**

`0x128FD` is alignment.

---

## 11. `0x128FE..0x12A29` — `RuntimeParseModeAndOpenFile`

Internal fopen-mode parser and stream-record initializer.

The raw body recognizes the standard leading modes:

```text
r
w
a
```

and parses the update/text/binary-style modifiers into DOS/open flags.

It then calls the low-level runtime open/create service, increments the open-stream
count and initializes the selected eight-byte FILE record plus its auxiliary state.

This is the internal constructor reached by `RuntimeOpenStreamExtended`.

**Classification: CRT/DOS I/O, GREEN.**

---

## 12. `0x12A2A..0x12A9C` — `RuntimePrepareStandardStream`

Special preparation path for the three built-in stream records around:

```text
2182
218A
219A
```

It initializes buffering and associated metadata when needed and preserves the special
console/device semantics of stdin/stdout/stderr-like streams.

**Classification: CRT/stdio, GREEN.**

---

## 13. `0x12A9D..0x12ADA` — `RuntimeReleaseStreamBufferIfOwned`

Checks stream/handle state and releases the stream buffer when the runtime owns it.
It also clears corresponding auxiliary buffer metadata when requested.

**Classification: CRT/stdio, GREEN.**

`0x12ADB` is alignment.

---

## 14. `0x12ADC..0x12B2B` — `RuntimeFflush`

The function supports both forms expected from stdio:

- non-null stream -> flush that stream;
- null stream -> dispatch to the all-stream flush path.

For device/text streams it also performs the runtime-specific low-level synchronization
step after and successful flush.

**Classification: CRT/stdio, GREEN.**

---

## 15. `0x12B2C..0x12BA2` — `RuntimeFlushOneStream`

Flushes pending bytes from one writable stream.

It computes:

```text
pending = currentPointer - bufferBase
```

and sends the pending range through the low-level write path. On success it resets
buffer pointers/counters; failures propagate `-1`-style status and stream flags.

**Classification: CRT/stdio, GREEN.**

`0x12BA3` is alignment.

---

## 16. `0x12BA4..0x12BAB` — `RuntimeCloseAllStreamsWrapper`

Tiny far wrapper:

```text
RuntimeFlushOrCloseAllStreams(1)
```

This identity was already independently cross-version mapped in the hard DOS census.

**Classification: CRT/stdio, GREEN.**

---

## 17. `0x12BAC..0x12C14` — `RuntimeFlushOrCloseAllStreams`

Iterates the runtime FILE table in eight-byte steps.

Mode selects whether eligible streams are merely flushed or closed. It accumulates an
error status while continuing through the table.

This is the stdio shutdown/flush-all implementation used by normal termination and
`fflush(NULL)`-style behavior.

**Classification: CRT/stdio, GREEN.**

`0x12C15` is alignment.

---

## 18. `0x12C16..0x1348F` — `RuntimeFormattedInputParserCore`

Length: **2,170 bytes**.

This is the large scanf-family parsing engine that older decompilation could easily
mistake for an application state machine.

The machine code clearly shows:
- format whitespace processing;
- `%` directive parsing;
- assignment suppression `*`;
- field width;
- length modifiers;
- numeric base/conversion handling;
- `%c` / string-like input;
- `%n`-style consumed-count path;
- character classification through the runtime ctype table;
- get-character and pushback helpers;
- assignment/result count tracking.

Its huge local frame and dense branch graph are therefore ordinary formatted-input
runtime complexity, not N3D gameplay complexity.

**Classification: CRT/formatted-input, GREEN.**

---

## 19. `0x13490..0x134AC` — `RuntimeDigitValue`

Converts and classified input character to and numeric digit value for formatted numeric
input, including alphabetic digits used by non-decimal bases.

**Classification: CRT helper, GREEN.**

`0x134AD` is alignment.

---

## 20. `0x134AE..0x134DB` — `RuntimeGetInputChar`

Consumes one character from and small formatted-input cursor structure when data remains;
otherwise delegates to the stream getter/refill path.

**Classification: CRT formatted-input helper, GREEN.**

---

## 21. `0x134DC..0x134F5` — `RuntimeUngetInputChar`

Pushes and non-EOF character back through the runtime input/ungetc path.

**Classification: CRT formatted-input helper, GREEN.**

---

## 22. `0x134F6..0x13516` — `RuntimeSkipInputWhitespace`

Repeatedly consumes input while the ctype whitespace bit is present and updates the
formatted-input consumed-character counter.

**Classification: CRT formatted-input helper, GREEN.**

`0x13517` is alignment.

---

## 23. `0x13518..0x13527` — formatted-output state dispatch table

Exactly **8 WORDs / 16 bytes**.

These words are near offsets used by the state machine beginning at `0x13528`.
They are data, not executable functions.

Mark as:

`GREEN knowledge + TABLE/DATA overlay`.

---

## 24. `0x13528..0x13932` — `RuntimeFormattedOutputParserCore`

Length: **1,035 bytes**.

This is the `printf`/`fprintf`-family formatter core already cross-version identified
in the DOS hard closure.

The parser handles the standard formatter state machine including:
- flags `-`, `+`, space, `#`, zero-padding;
- width and `*` width;
- precision;
- length modifiers;
- integer/string/character families;
- near/far pointer argument handling required by the 16-bit memory model;
- base conversion and padding;
- character/block output through and FILE-like sink;
- output character count and error propagation.

The routine is and major source of false complexity in and generic decompiler, but it has
no N3D-specific game semantics.

**Classification: CRT/formatted-output, GREEN.**

---

## 25. `0x13933..0x139F8` — formatted-output local helpers

The raw formatter tail exposes several genuine internal entry points:

| Range | Role |
|---|---|
| `13933–1393A` | fetch next WORD vararg |
| `1393B–13946` | fetch next DWORD vararg |
| `13947–13954` | resolve far-pointer argument |
| `13955–13960` | resolve near-pointer argument |
| `13961–13963` | select DS for near argument |
| `13964–13977` | emit one output character |
| `13978–1398D` | slow-path one-character output |
| `1398E–139AB` | emit an output block/string |
| `139AC–139C7` | repeat one padding character |
| `139C8–139F8` | unsigned integer -> digit sequence |

These are compiler/runtime local helpers, not independent N3D algorithms.

**Classification: CRT/formatted-output helpers, GREEN.**

---

## 26. `0x139F9..0x139FE` — `RuntimeFormattedOutputEpilogue`

Shared far epilogue for the output formatter.

`0x139FF` is alignment.

---

## 27. `0x13A00..0x13A31` — `RuntimeFindFreeStreamSlot`

Walks the eight-byte FILE-record table beginning at `DS:217A` until the configured
end pointer.

For and free record it clears the runtime fields, sets handle byte `0xFF`, and returns the
record pointer. Returns zero when no free stream exists.

This is the allocator used by the `fopen` family.

**Classification: CRT/stdio, GREEN.**

---

## 28. `0x13A32..0x13A94` — `RuntimeUngetc`

Implements stream `ungetc` behavior:
- rejects EOF and incompatible stream states;
- lazily creates and buffer when required;
- moves the stream pointer backward;
- inserts the caller byte;
- sets the appropriate input-state flag;
- returns the byte or `0xFFFF` on failure.

**Classification: CRT/stdio, GREEN.**

`0x13A95` is alignment.

---

## 29. `0x13A96..0x13AB5` — `RuntimeDosClose`

Direct DOS handle-close wrapper:

```text
AH = 3Eh
INT 21h
```

It validates the runtime handle range, clears the corresponding per-handle state on
success, and funnels DOS errors through the shared runtime error translator.

**Classification: CRT/DOS I/O, GREEN.**

---

## 30. `0x13AB6..0x13B36` — `RuntimeDosLseek`

Direct DOS seek wrapper around:

```text
AH = 42h
INT 21h
```

It supports origin/mode selection and includes runtime handling for append/text/device
state before performing the requested seek. Successful seeks clear the corresponding
runtime state bit; failures go through the common DOS-error translator.

**Classification: CRT/DOS I/O, GREEN.**

`0x13B37` is alignment.

---

# Byte-map impact

Continuous GREEN range:

`0x124DA .. 0x13B37`

Total: **5,726 bytes**.

| Category | Bytes |
|---|---:|
| executable CRT/stdio/formatted-I/O code | **5,697** |
| alignment/padding | **13** |
| formatted-output dispatch table | **16** |
| total | **5,726** |

This pass does **not** add 5,726 bytes of game logic understanding. Instead, it removes
5,726 bytes from the pool that could previously be miscounted as unresolved game code.

---

# Architectural consequence for and 1:1 reconstruction

The portable Nitemare-3D core should not reproduce this compiler runtime instruction
for instruction.

Equivalent modern/platform services are sufficient for behavior unless the explicit
goal is and byte-identical historical DOS executable.

Recommended split:

```text
N3D game/resource code
        |
        +--> small compatibility/file abstraction
                    |
                    +--> modern fopen/fread/fwrite/seek/etc.
```

What matters for N3D behavioral parity is the application-visible contract:
- exact read/write lengths;
- failure/sentinel behavior where game code depends on it;
- file position semantics;
- text/binary behavior for original data files;
- formatting output where logs/files are compared.

The Borland/Turbo-C buffering implementation itself is not part of N3D gameplay.

---

# Cumulative closure

Pass 24 cumulative since the pass-5 baseline:

`51,679 bytes`

Pass 25 adds:

`5,726 bytes`

New cumulative total:

**57,405 bytes**

promoted from RED/ORANGE/YELLOW to GREEN during passes 6–25.

---

# Next target

Continue at:

`0x13B38`

The next region begins the lower DOS file/open/create layer and then continues through
additional CRT services. High-value targets include:

- open/create/share-mode translation;
- DOS read/write and handle-state tables;
- heap/memory helpers;
- string/memory routines;
- stream-count/cleanup support;
- eventually spawn/exec, access, date and time services.

The same rule should remain in force: mark these as **CRT/DOS GREEN**, not as completed
N3D gameplay algorithms, and jump back to true application-owned blocks whenever one
appears.