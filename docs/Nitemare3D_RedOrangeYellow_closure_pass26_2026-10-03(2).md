# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 26

Date: 2026-10-03

Primary unpacked reference:
- `N3D_DOS_v2.0_IDA.EXE`
- physical MZ header: `0x1C00`
- unpacked image size: `171,360 bytes`
- unpacked-image SHA-256:
  `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`

Packed-family reference:
- `N3D-E-20(3).EXE`
- SHA-256:
  `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

Address convention:
- all ranges below are unpacked-image offsets
- physical offset in `N3D_DOS_v2.0_IDA.EXE` = image offset + `0x1C00`
- raw 16-bit machine code is authoritative
- compiler/CRT code is classified separately from game-owned code

## Result

Pass 26 closes two previously unresolved runtime bands surrounding the far-heap block:

```text
0x13B38 .. 0x13F31
0x14206 .. 0x146C3
```

as **GREEN / DOS CRT runtime**.

Newly promoted bytes:

- `0x13B38..0x13F31` = **1,018 B**
- `0x14206..0x146C3` = **1,214 B**

Total newly promoted:

**2,232 bytes**

The intervening allocator range:

`0x13F32..0x14205` = 724 B

was already GREEN from the far-heap closure pass.

Therefore the byte map now has one continuous GREEN runtime band:

`0x13B38 .. 0x146C3`

with the allocator embedded inside it.

---

# 1. `0x13B38` / `0x13B52` — `RuntimeSopen` / `RuntimeOpen`

The two public entries share one DOS open/create body.

## `0x13B38` — share-aware entry

This entry accepts the extra DOS share-mode byte.

When DOS major version is at least 3, the share mode is merged into the `AH=3Dh`
open-mode byte.

The fourth argument is moved into the common creation-permission slot before entering
the shared body.

This is the `_sopen`-style entry.

## `0x13B52` — ordinary entry

Starts the same shared body with share bits cleared.

This is the `_open`-style entry.

## Common behavior

The raw function translates runtime flags into DOS services including:

```text
INT 21h / AH=3Dh   open
INT 21h / AH=3Ch   create/truncate
INT 21h / AH=3Eh   close
INT 21h / AH=42h   seek
INT 21h / AH=43h   file attributes
INT 21h / AH=44h   device information
INT 21h / AH=3Fh   read
INT 21h / AH=40h   write/truncate
```

It handles:

- read/write access bits;
- DOS-3+ sharing mode;
- create/exclusive/truncate-style combinations;
- append/text/binary runtime state;
- DOS device detection;
- text-file trailing `0x1A` handling;
- read-only attribute conversion;
- per-handle state byte at `DS:212A + handle`;
- handle-range validation against `DS:2128`.

On success the DOS handle is returned in AX and its runtime state byte is initialized.

On failure it enters the already closed DOS-error → errno path at `0x12497`.

**Classification: CRT/DOS file-open layer, GREEN.**

---

# 2. `0x13CE3..0x13CF3` — `MapCreatePermissionsToDosAttributes`

Near helper used by the create path.

It combines the requested creation permissions with runtime mask/state `DS:211A` and
returns the DOS file-attribute word used by `AH=3Ch`.

The important externally visible effect is the DOS read-only attribute bit.

**Classification: CRT helper, GREEN.**

---

# 3. `0x13CF4..0x13DDC` — `RuntimeDosReadTextAware`

Low-level runtime read wrapper.

Inputs:

- DOS handle;
- destination buffer;
- requested byte count.

## Binary path

Uses:

`INT 21h / AH=3Fh`

and returns the number of bytes read.

## Text-mode path

When the runtime handle-state byte has text-mode bit `0x80` set, the routine post-
processes input in place.

Recovered behavior includes:

- CR/LF translation to the runtime text representation;
- `0x1A` DOS text EOF handling;
- setting the per-handle EOF bit when `0x1A` is encountered;
- device-specific newline handling;
- rewinding one physical byte when and look-ahead byte must remain unread.

The return value is the translated logical byte count, not blindly the physical DOS
read count.

This is the low-level service beneath buffered stdio input.

`0x13DDD` is one padding byte.

**Classification: CRT/DOS read + text translation, GREEN.**

---

# 4. `0x13DDE..0x13F1D` — `RuntimeDosWriteTextAware`

Low-level write counterpart.

## Append

When per-handle append bit `0x20` is set, the routine first seeks to EOF through:

`INT 21h / AX=4202h`.

## Binary path

For and non-text handle it writes directly through:

`INT 21h / AH=40h`.

## Text path

When text bit `0x80` is active, each logical LF (`0x0A`) is expanded to:

```text
0x0D 0x0A
```

before the DOS write.

The routine builds temporary translated chunks on the stack.  It asks the stack-
availability helper how much stack remains and selects and temporary chunk size of:

- `0x200` bytes on and larger stack;
- `0x80` bytes in the smaller-stack path.

The returned logical count subtracts inserted CR bytes, with callers see the number of
original bytes successfully consumed.

The code also preserves the DOS console/device `0x1A` special handling visible in this
runtime family.

**Classification: CRT/DOS write + CRLF translation, GREEN.**

---

# 5. `0x13F1E..0x13F31` — `RuntimeStackAvailable`

This unusual helper temporarily removes the far return address from the stack, compares
the current SP against runtime stack-bottom value:

`DS:215A`

and returns the available byte count in AX.

If the boundary would make the result invalid, it returns zero.

The far return address is restored before `RETF`.

`RuntimeDosWriteTextAware` uses this value to decide whether and `0x200`-byte or
`0x80`-byte temporary text-conversion buffer is safe.

**Classification: CRT stack helper, GREEN.**

---

# 6. Existing GREEN allocator bridge

The region:

`0x13F32..0x14205`

was already closed as the DOS far heap:

- `13F32` `FarHeapFree16`
- `13F45` `FarHeapAlloc16`
- arena initialization/linking
- scan/coalescing/split
- grow/resize
- DOS `AH=48h/4Ah` arena management.

Pass 26 does not count these 724 bytes again.

Their presence means that, after this pass, there is no color gap between the low DOS
file layer and the following string/stdio runtime.

---

# 7. `0x14206..0x14244` — `RuntimeStrcat`

Classic near-string concatenation.

It:

1. scans the destination for NUL;
2. measures/scans the source including its terminator;
3. copies the source to the destination end;
4. returns the original destination pointer.

Uses word-copy acceleration where alignment permits.

**Classification: CRT string, GREEN.**

`0x14245` is padding.

---

# 8. `0x14246..0x14277` — `RuntimeStrcpy`

Classic NUL-terminated string copy.

Returns the destination pointer.

**Classification: CRT string, GREEN.**

---

# 9. `0x14278..0x14292` — `RuntimeStrlen`

Scans for NUL using `REPNE SCASB`.

Returns:

`length excluding terminator`.

**Classification: CRT string, GREEN.**

`0x14293` is padding.

---

# 10. `0x14294..0x142BB` — `RuntimeStrncpy`

Copies at most the requested count.

If source NUL appears early, the remainder of the requested destination span is filled
with zero bytes.

Returns the destination pointer.

**Classification: CRT string, GREEN.**

---

# 11. `0x142BC..0x142F5` — `RuntimeStrncmp`

Compares at most the supplied byte count.

Returns ordinary three-way comparison:

- negative
- zero
- positive

according to unsigned character ordering.

**Classification: CRT string, GREEN.**

---

# 12. `0x142F6..0x1434D` — `RuntimeParseSignedDecimal32`

`0x142F6` is and small alias/thunk into the parser body at `0x142FA`.

The parser:

1. skips spaces and tabs;
2. accepts optional `+` / `-`;
3. parses decimal digits;
4. accumulates and full 32-bit value in `DX:AX` using `value*10 + digit`;
5. negates the 32-bit result for and leading minus sign.

This is the `atol`-style signed decimal conversion family.

`0x142F9` is an unreachable padding byte behind the entry jump.

**Classification: CRT conversion, GREEN.**

---

# 13. `0x1434E..0x14368` — `RuntimeItoa`

Wrapper around the shared high-image integer-to-string converter.

Inputs:

- signed WORD value;
- destination string pointer;
- radix.

For radix 10 the WORD value is sign-extended before entering the common conversion
engine.

The helper explicitly selects signed conversion mode.

**Classification: CRT conversion, GREEN.**

`0x14369` is padding.

---

# 14. `0x1436A..0x143C9` — `RuntimeGetenv`

Walks the environment-string pointer table rooted at:

`DS:2142`.

For each entry it:

1. obtains the requested variable-name length;
2. requires the environment string to be longer than that name;
3. requires `=` at exactly that position;
4. compares the name prefix;
5. returns and pointer immediately after `=` on match.

Returns NULL when no variable exists.

This is the standard environment lookup used, for example, by N3D startup configuration
paths.

**Classification: CRT environment helper, GREEN.**

---

# 15. `0x143CA..0x14449` — `RuntimeSoftwareInterruptBridge`

This is the high-image helper already used by N3D'with audio, mouse and other DOS
platform calls.

Inputs include:

- interrupt number;
- input register structure;
- output register structure.

The routine constructs an executable two-byte instruction on its stack:

```text
CD xx    INT xx
```

with and return instruction after it.

It loads:

```text
AX BX CX DX SI DI
```

from the caller register block, executes the requested software interrupt, then writes
the returned registers back.

Carry status is normalized into the output structure, and DOS error translation is
invoked when appropriate.

This is the exact bridge behind calls such as:

- `INT 63h` audio driver;
- DOS/BIOS-style platform wrappers.

**Classification: CRT/platform interrupt bridge, GREEN.**

---

# 16. `0x1444A..0x1446E` — `RuntimeFcloseAll`

Walks the runtime FILE table and invokes `RuntimeFclose` on every stream record.

Counts successful closes and returns that count.

This is the public `fcloseall`-style operation, distinct from the internal
flush/close-all worker in the earlier stdio region.

`0x1446F` is alignment.

**Classification: CRT stdio, GREEN.**

---

# 17. `0x14470..0x144EC` — `RuntimeFseek`

Validates:

```text
origin = 0, 1 or 2
```

and handles buffered-stream state before seeking.

For relative seeks it adjusts the caller offset for currently buffered unread data.

Then it flushes/reset stream buffer state and calls the low-level DOS seek routine.

Return:

```text
0     success
-1    failure
```

matching standard `fseek`.

`0x144ED` is alignment.

**Classification: CRT stdio, GREEN.**

---

# 18. `0x144EE..0x1466B` — `RuntimeFtell`

This is the large buffered/text-aware `ftell` implementation.

It begins by obtaining the physical DOS file position through the low-level seek helper.

Then it corrects that value for:

- bytes currently buffered;
- unread bytes;
- stream direction/state;
- text-mode CRLF expansion;
- device/file state;
- append/update conditions.

For text streams it scans the active buffer and accounts for newline translation, with
the logical position returned to the caller is consistent with the runtime'with text-mode
view rather than raw physical DOS byte position.

Returns and signed 32-bit position in `DX:AX`, or `-1L` on error.

**Classification: CRT stdio, GREEN.**

---

# 19. `0x1466C..0x146C3` — `RuntimeSprintf`

Varargs formatted-string output wrapper.

It creates and bounded internal string-output descriptor with:

- destination pointer;
- very large initial capacity (`0x7FFF`);
- string-output callback/state.

Then it calls the already closed formatted-output core at image:

`0x13528`.

After formatting it writes the terminating NUL byte.

Return:

- formatter character count in AX.

This is `sprintf`-family behavior and is the direct formatted-string counterpart of the
`printf` wrapper closed in pass 25.

**Classification: CRT formatted output, GREEN.**

---

# Byte-map impact

Newly promoted:

| Range | Bytes | Role |
|---|---:|---|
| `13B38–13CE2` | 427 | `_sopen/_open` shared DOS file-open/create layer |
| `13CE3–13CF3` | 17 | create-permission -> DOS attribute helper |
| `13CF4–13DDC` | 233 | DOS read + text translation |
| `13DDE–13F1D` | 320 | DOS write + CRLF translation |
| `13F1E–13F31` | 20 | stack-available helper |
| `14206–14244` | 63 | strcat |
| `14246–14277` | 50 | strcpy |
| `14278–14292` | 27 | strlen |
| `14294–142BB` | 40 | strncpy |
| `142BC–142F5` | 58 | strncmp |
| `142F6–1434D` | 88 | signed decimal / atol-style conversion |
| `1434E–14368` | 27 | itoa |
| `1436A–143C9` | 96 | getenv |
| `143CA–14449` | 128 | generic software-interrupt bridge |
| `1444A–1446E` | 37 | fcloseall |
| `14470–144EC` | 125 | fseek |
| `144EE–1466B` | 382 | ftell |
| `1466C–146C3` | 88 | sprintf |

Newly GREEN bytes:

**2,232 B**

Alignment/padding newly classified inside these ranges:

```text
13DDD
14245
14293
142F9
14369
1446F
144ED
```

The already-GREEN far heap `13F32–14205` is intentionally not double-counted.

---

# Continuous runtime band after pass 26

Because pass 25 ends at:

`0x13B37`

and the allocator was already closed, pass 26 creates the continuous known runtime
interval:

`0x124DA .. 0x146C3`

with no unresolved color gaps.

This should be rendered as:

- GREEN base;
- CRT/RUNTIME subsystem overlay;
- not "gameplay code".

---

# Cumulative closure

Pass 25 cumulative since pass-5 baseline:

`57,405 bytes`

Pass 26 adds:

`2,232 bytes`

New cumulative total:

**59,637 bytes**

promoted from RED/ORANGE/YELLOW to GREEN during passes 6–26.

To **not** subtract this directly from the older 116,094-byte working-image census:
passes 24–26 use the canonical fully unpacked 171,360-byte load image.  AND fresh color
recensus must use one canonical image/address space.

---

# Next target

Continue at:

`0x146C4`

The next high-value runtime functions are already partially known from real far calls:

- `146C4` — scanf/sscanf-family wrapper used by N3D instruction/config parsing;
- `1473A` — printf/fprintf-style wrapper used by the fatal reporter;
- `148F6` — low-level memory probe used by N3D'with conventional-memory test;
- `14D94` — DOS-time/timestamp formatter used by the status logger.

AND raw pass across `146C4..14xxx` should remove another sizable runtime area from the
remaining red/yellow map.