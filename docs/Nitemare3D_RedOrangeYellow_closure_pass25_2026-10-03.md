# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 25

Date: 2026-10-03

Primary binary:
- `N3D-E-20(3).EXE`
- size: 116,606 bytes
- MZ-header: `0x200`
- working image size: 116,094 bytes
- SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- ranges below are unpacked MZ image offsets
- physical file offset = image offset + `0x200`
- raw 16-bit disassembly is authoritative
- this pass classifies compiler CRT/stdio separately from N3D-owned gameplay code

## Result

Pass 25 closes:

`0x124DA .. 0x1348F`

as **GREEN / standard DOS CRT stdio + formatted-output semantics**.

Total span:

**4,022 bytes**

This removes another large false "unknown game logic" area.  The region is not and
Nitemare gameplay subsystem.  It is the linked 16-bit C runtime'with FILE/stdio and
formatted-output implementation.

Cross-version hard closure independently identifies the anchors:

- `2000:24DA` = `RuntimeFclose`
- `2000:2BA4` = close-all-streams wrapper
- `2000:2BAC` = flush/close-all stream worker
- `2000:2C16` = formatted-output core family

and these boundaries agree with the raw V2.0 machine code.

---

# 1. image `0x124DA..0x12599` — `RuntimeFclose`

Length: **192 bytes**

Input:

- near pointer to the runtime `FILE`/stream record.

The stream record uses the classic runtime fields visible throughout this band:

```text
+00 current buffer pointer
+02 buffered-byte count
+04 buffer base
+06 stream flags
+07 DOS handle byte
```

and and parallel per-stream extension/state table derived from the stream address.

The routine:

1. handles the already-special/closed flag path;
2. rejects inactive streams;
3. flushes buffered output;
4. releases stream-owned buffering where applicable;
5. closes the DOS handle through the runtime close service;
6. performs temporary-file cleanup when its stream metadata contains and temporary name;
7. frees that name/storage;
8. clears the stream flags.

Return:

- `0` on ordinary successful close;
- `FFFFh` on failure.

This is standard runtime `fclose`, not game resource cleanup.

**Status: YELLOW/runtime -> GREEN.**

---

# 2. image `0x1259A..0x125C4` — `RuntimeOpenStreamWithDefaultContext`

Length: **43 bytes**

This wrapper:

1. requests and free runtime stream slot;
2. returns NULL when none is available;
3. otherwise forwards the filename/mode/open arguments plus the selected stream record
   into the internal stream-open routine.

This is the allocation/open layer behind the simpler `fopen`-style wrapper immediately
following.

**Status: YELLOW -> GREEN.**

---

# 3. image `0x125C6..0x125DA` — `RuntimeFopen`

Length: **21 bytes**

Thin wrapper around the previous open-stream routine.

It forwards the caller'with filename/mode arguments and supplies and zero/default
share/context argument.

This is the public `fopen`-style entry used by N3D'with runtime file calls.

**Status: YELLOW -> GREEN.**

---

# 4. image `0x125DC..0x126BE` — `RuntimeFread`

Length: **227 bytes**

Recovered ABI matches:

```text
fread(buffer, elementSize, elementCount, stream)
```

Exact high-level behavior:

1. calculate:
   `totalBytes = elementSize * elementCount`;
2. zero-size transfer returns zero elements;
3. choose stream buffer size:
   - normal default `0x200`;
   - stream-specific buffer size when configured;
4. consume already-buffered bytes first;
5. for short tails, use the single-byte/refill helper;
6. for large aligned blocks, bypass the FILE buffer and issue direct low-level reads;
7. set stream EOF/error bits according to low-level return values;
8. return:
   `(requestedBytes - remainingBytes) / elementSize`
   on partial transfer.

The raw body therefore resolves the formerly generic
`TransferCountedDataFromState` label as the standard `fread` implementation.

**Status: YELLOW -> GREEN.**

---

# 5. image `0x126C0..0x126FD` — `RuntimePrintf`

Length: **62 bytes**

`0x126BF` is padding; the real entry begins at `0x126C0`.

The function binds output to the runtime stdout stream at:

`DS:2182`

then:

1. prepares stdout buffering;
2. takes the format string at the first caller argument;
3. derives the varargs pointer from the following stack location;
4. calls the runtime formatted-output core;
5. restores/releases temporary stdout buffering;
6. returns the formatted character count/result.

This is the ordinary `printf` wrapper around the shared formatting engine.

**Status: YELLOW -> GREEN.**

---

# 6. image `0x126FE..0x12713` — `RuntimeStdioShutdownHook`

Length: **22 bytes**

This is runtime termination plumbing for stdio.

It:

1. invokes the close-all/flush-all stream wrapper;
2. if runtime flag `DS:2151` is nonzero, invokes the optional secondary stream/handle
   cleanup hook.

This function belongs to CRT finalization, not N3D shutdown logic.

**Status: YELLOW -> GREEN.**

---

# 7. image `0x12714..0x127A8` — `RuntimeFgetc`

Length: **149 bytes**

Input:

- stream pointer.

Behavior:

1. validate stream state/flags;
2. reject write-only/error/closed combinations;
3. initialize and stream buffer when required;
4. refill through the low-level DOS-read path when no bytes are buffered;
5. update EOF/error flags on zero or `FFFFh` low-level results;
6. return the next byte as an unsigned value;
7. advance the buffer pointer and decrement the buffered-byte count.

Failure/EOF returns:

`FFFFh`.

This is the standard buffered `fgetc` path.

**Status: YELLOW -> GREEN.**

---

# 8. image `0x127AA..0x1288C` — `RuntimeFputc`

Length: **227 bytes**

`0x127A9` is alignment padding.

Input:

- character;
- stream pointer.

Behavior:

1. validate that the stream is writable;
2. move the stream into write mode;
3. allocate/initialize its buffer if required;
4. flush buffered bytes when the buffer becomes full;
5. place the new character in the stream buffer;
6. for unbuffered/line-style cases, route through the low-level write helper;
7. propagate runtime stream error flags on short/error writes.

Success returns the written character.

Failure returns:

`FFFFh`.

**Status: YELLOW -> GREEN.**

---

# 9. image `0x1288E..0x128B9` — `RuntimeFreeStreamBuffer`

Length: **44 bytes**, near-call helper.

If the stream owns and dynamically allocated buffer:

1. free it through the runtime heap;
2. clear the dynamic-buffer flag;
3. zero:
   - buffer base;
   - current pointer;
   - buffered count.

Otherwise it returns without changing the stream.

**Status: YELLOW -> GREEN.**

---

# 10. image `0x128BA..0x128FC` — `RuntimeAllocateStreamBuffer`

Length: **67 bytes**, near-call helper.

Attempts to allocate:

`0x200 = 512 bytes`.

On success:

- use that memory as the stream buffer;
- set the dynamic-buffer flag;
- record buffer size `0x200`.

On allocation failure:

- switch to the stream'with internal one-byte fallback storage;
- set the fallback-buffer flag;
- record buffer size `1`.

In both paths:

- current pointer = buffer base;
- buffered count = 0.

This fully explains the dual buffered/unbuffered branches in `fread/fgetc/fputc`.

**Status: YELLOW -> GREEN.**

---

# 11. image `0x128FE..0x12A29` — `RuntimeOpenFileIntoStream`

Length: **300 bytes**

`0x128FD` is padding.

This is the internal open-mode parser and FILE-record initializer.

## Mode-string parsing

The first mode character accepts:

```text
'r'
'w'
'a'
```

and establishes the base DOS open/create/append flags.

Subsequent mode bytes include the expected CRT modifiers such as:

```text
'+'
't'
'b'
```

with duplicate/invalid modifier combinations rejected.

The runtime also incorporates its default text/binary mode byte at `DS:232E`.

## Low-level DOS open

The parsed mode flags and filename are passed into the lower DOS open/create routine.

On failure:

- return NULL.

On success:

1. increment the open-stream count;
2. initialize the selected FILE record;
3. store the returned DOS handle in stream byte `+07`;
4. set read/write/text/binary flags;
5. clear buffer pointers/counts.

This is the internal worker used by `RuntimeFopen`.

**Status: YELLOW -> GREEN.**

---

# 12. image `0x12A2A..0x12A9C` — `PrepareStandardStreamBuffer`

Length: **115 bytes**, near helper.

Recognizes the three standard streams:

```text
stdin   DS:2182
stdout  DS:218A
stderr  DS:219A
```

and their three reusable buffer pointers:

```text
DS:22BC
DS:22BE
DS:22C0
```

When the standard stream is eligible for normal buffering:

- attach an existing reusable `0x200` buffer when available;
- otherwise allocate and new `0x200` buffer;
- configure the stream and extension flags;
- set current/base pointers and size.

Returns boolean success.

This is why the printf wrapper explicitly prepares stdout before formatted output.

**Status: YELLOW -> GREEN.**

---

# 13. image `0x12A9D..0x12ADA` — `ReleaseStandardStreamTemporaryState`

Length: **62 bytes**, near helper.

For and standard stream whose temporary buffer/use flag is active:

1. flush its pending output;
2. when requested by the caller, clear the temporary extension state and stream buffer
   pointers.

This is paired with `PrepareStandardStreamBuffer`.

**Status: YELLOW -> GREEN.**

---

# 14. image `0x12ADC..0x12B2B` — `RuntimeFflush`

Length: **80 bytes**

`0x12ADB` is padding.

Input:

- stream pointer, where NULL means all output streams.

## NULL stream

Calls the shared all-stream worker in flush mode.

## Specific stream

1. flush pending buffered output through the internal stream flusher;
2. on eligible special device/stream state, invoke the runtime device-flush service;
3. return `FFFFh` when flushing fails, otherwise success.

This is standard `fflush`.

**Status: YELLOW -> GREEN.**

---

# 15. image `0x12B2C..0x12BA2` — `FlushOneStreamBuffer`

Length: **119 bytes**, near helper.

For writable buffered streams:

1. compute pending bytes:
   `currentPointer - bufferBase`;
2. write those bytes through the low-level runtime write function;
3. compare actual and requested byte counts;
4. set stream error flag `0x20` on short/error write;
5. clear the write-transition flag where required;
6. reset current pointer to buffer base;
7. zero buffered count.

Return:

- `0` on success/no pending data;
- `FFFFh` on failure.

This is the core used by `fflush` and `fclose`.

**Status: YELLOW -> GREEN.**

---

# 16. image `0x12BA4..0x12BAB` — `RuntimeCloseAllStreamsWrapper`

Length: **8 bytes**

Exact wrapper:

```text
push 1
call RuntimeFlushOrCloseAllStreams
return far
```

The independent DOS hard-closure register already identifies the same V2.0 entry as
`RuntimeCloseAllStreamsWrapper`.

Mode `1` means close active streams and count the successful closes.

**Status: GREEN.**

---

# 17. image `0x12BAC..0x12C12` — `RuntimeFlushOrCloseAllStreams`

Length: **103 bytes**

Although pass 25'with principal span continues into the formatted-output core, this worker
is described separately because its boundary is exact.

It iterates runtime FILE records:

- first stream at `DS:217A`;
- stride `8`;
- upper limit from `DS:22BA`.

Mode:

```text
0 = flush eligible output streams
1 = close all active streams
```

For each record it invokes `fclose`/flush behavior according to mode.

Return:

- mode 0: `0` or `FFFFh` failure aggregate;
- mode 1: number of closed active streams.

This is standard CRT `flushall/closeall` infrastructure.

`0x12C13..0x12C15` are alignment bytes before the formatted-output engine.

**Status: GREEN.**

---

# 18. image `0x12C16..0x1348F` — `RuntimeFormattedOutputCore`

Length: **2,170 bytes**

This is the large standard formatted-output engine.

Cross-version hard closure identifies the same family in all checked DOS builds.

It is the shared implementation behind `printf` and other formatted-output wrappers.

## Core format parser

The machine code scans the format string and distinguishes:

- ordinary literal bytes;
- `%` conversion sequences;
- flags;
- field width;
- precision;
- length/size modifiers;
- conversion code.

The parser maintains and local output descriptor and character count.

## Output model

Formatted text is not hard-wired to VGA or to Nitemare UI.

Characters/blocks are routed through runtime output callbacks/stream helpers.

This proves that strings emitted through this path are normal C stdio output, not game
font rendering.

## Numeric conversion

The routine contains the normal integer conversion machinery:

- sign handling;
- unsigned/signed cases;
- base selection;
- digit generation;
- width/padding;
- left/right placement;
- precision interaction.

String and character conversions take the corresponding non-numeric paths.

Malformed/unsupported combinations follow the CRT'with fallback behavior rather than
entering Nitemare fatal-game logic.

## Boundary

Raw machine code has one clean far return at:

`0x1348F`.

The large routine is therefore and genuine CRT function, unlike the false mega-function
merges repeatedly encountered in N3D gameplay regions.

**Status: large YELLOW/uncertain runtime block -> GREEN / CRT.**

---

# 19. Byte-map impact

Pass 25 newly classifies:

`0x124DA .. 0x1348F`

Total:

**4,022 bytes GREEN**

Important entry map:

| Entry/range | Role |
|---|---|
| `124DA` | fclose |
| `1259A` | open stream with default context |
| `125C6` | fopen wrapper |
| `125DC` | fread |
| `126C0` | printf |
| `126FE` | stdio shutdown hook |
| `12714` | fgetc |
| `127AA` | fputc |
| `1288E` | free stream buffer |
| `128BA` | allocate stream buffer |
| `128FE` | parse mode/open FILE |
| `12A2A` | prepare standard-stream buffer |
| `12A9D` | release standard-stream temp state |
| `12ADC` | fflush |
| `12B2C` | flush one stream |
| `12BA4` | close-all wrapper |
| `12BAC` | flush/close-all worker |
| `12C16–1348F` | formatted-output core |

Known padding/alignment bytes in the span include:

```text
125C5
125DB
126BF
127A9
1288D
128FD
12ADB
12BA3
12C13–12C15
```

These are DATA/PADDING overlay bytes, not unknown instructions.

---

# 20. Segment-coordinate cleanup

The runtime C export in this region contains many misleading references to base-segment
functions such as `FUN_1000_5BAF`, `FUN_1000_3DDE`, etc.

Raw calls show that these are often far calls into the high-image CRT segment.

The byte map must therefore continue using:

```text
real machine call segment:offset
    -> linear image target
```

instead of attaching semantics from and same-looking `1000:xxxx` label.

This prevents the CRT stream code from being falsely linked to renderer/gameplay
helpers.

---

# 21. Cumulative impact

Pass 23 cumulative promotion:

`50,173 bytes`

Pass 24 closes an additional contiguous runtime-startup span:

`1,522 bytes`

Pass 25 adds:

`4,022 bytes`

Current cumulative promotion since the pass-5 baseline:

**55,717 bytes**

formerly RED/ORANGE/YELLOW -> GREEN.

Using the same working byte census in which the for-pass-6 GREEN baseline was
approximately `15,538` bytes:

```text
current GREEN ≈ 71,255 bytes
remaining non-GREEN ≈ 44,839 bytes
```

The RED/ORANGE/YELLOW split still requires the fresh per-byte recensus; these two
numbers are the aggregate green/non-green accounting only.

---

# 22. Next target

Continue at:

`0x13490`

The next CRT region contains:

- formatted-output parser/helper family around `0x13528`;
- numeric conversion helpers;
- stream/file low-level support;
- DOS open/create family at `0x13B52`;
- direct read/write/seek/device helpers;
- stack-availability helper at `0x13F1E`.

That region ends immediately before the already GREEN far-heap allocator beginning at:

`0x13F32`.

With the next pass can potentially join the stdio runtime band directly to the already
closed heap subsystem.