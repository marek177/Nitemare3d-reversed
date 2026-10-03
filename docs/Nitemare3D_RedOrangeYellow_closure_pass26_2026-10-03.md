# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 26

Date: 2026-10-03

Primary runtime image:
- `N3D_DOS_v2.0_IDA.EXE`
- unpacked load-image size: 171,360 bytes
- this pass concerns the compiler/CRT tail, not gameplay logic

## Result

Pass 26 classifies the complete continuous image range:

`0x13B38 .. 0x1591C`

as **GREEN / standard DOS CRT + DOS-service runtime**.

Total span: **7,653 bytes**.

The main purpose of this pass is not to reimplement every Borland/Turbo-C helper in the game core. It removes this entire range from the RED/ORANGE/YELLOW gameplay count and records the application-visible ABI boundaries that Nitemare 3D actually uses.

The next byte, `0x1591D`, begins and different compiler-runtime family: signed/unsigned 32-bit arithmetic helpers. That family is deliberately left for the next pass.

---

## 1. `0x13B38 / 0x13B52` — DOS open/create/share translation

The raw body translates CRT-style open flags into DOS services.

Observed services include:

- `INT 21h AH=3Dh` — open file;
- `INT 21h AH=3Ch` — create/truncate;
- `INT 21h AX=4300h/4301h` — get/set file attributes;
- `INT 21h AX=4400h` — device information;
- `INT 21h AH=3Eh` — close during reopen/error paths;
- `INT 21h AH=42h` — seek;
- zero-length `AH=40h` write for truncate behavior.

The routine also maps DOS handles into the runtime handle-state table near `DS:212A` and records binary/text/device/append-related flags.

**Status: CRT/DOS GREEN.**

---

## 2. `0x13CF4` — DOS read with CRT text-mode translation

Direct underlying read:

```text
AH = 3Fh
BX = handle
CX = count
DS:DX = buffer
INT 21h
```

For text-mode handles the wrapper additionally performs CRT translation behavior:

- CR/LF handling;
- DOS EOF byte `0x1A` handling;
- device/stream-state updates;
- translated byte-count return.

This is the lower-level helper behind game resource, config and save-file reads.

**Status: CRT/DOS GREEN.**

---

## 3. `0x13DDD` family — DOS write with text-mode CR/LF conversion

The complementary output path uses:

```text
AH = 40h
INT 21h
```

For text streams it expands LF to CR/LF and writes through temporary chunks when required. Device and disk-handle paths are kept separate.

This is compiler runtime behavior rather than an N3D-specific resource format.

**Status: CRT/DOS GREEN.**

---

## 4. `0x13F1E` — `stackavail`-style helper

Compares the current SP with the runtime-maintained stack boundary and returns the remaining available stack space, or zero when the boundary has already been crossed.

This matches the previously cross-version-identified V2.0 runtime stack-availability helper.

**Status: CRT GREEN.**

---

## 5. `0x13F32..0x141xx` — runtime heap / allocation bookkeeping

This cluster contains internal runtime allocation-list and block-management helpers.

It operates on compiler-owned heap metadata and callback pointers rather than N3D world records.

The important architectural conclusion is that these routines belong to the C runtime allocator layer. Modern reimplementations to not need to clone this heap internals unless binary-identical DOS output is the goal.

**Status: CRT GREEN.**

---

## 6. `0x14206` — `strcat`

Raw behavior:

1. find destination NUL;
2. find source length;
3. copy source including terminating NUL to destination end;
4. return original destination pointer.

**Status: CRT string GREEN.**

---

## 7. `0x14246` — `strcpy`

The raw implementation determines source length and copies the complete NUL-terminated string to the destination with optimized byte/word moves.

This is the V2.0 address of the already cross-version-classified runtime `strcpy` family.

**Status: CRT string GREEN.**

---

## 8. `0x14278` — `strlen`

Uses `REPNE SCASB` to locate the terminating NUL and returns the length excluding that byte.

**Status: CRT string GREEN.**

---

## 9. `0x14294+` — memory/string comparison and copy support

The following small routines are conventional compiler-library memory/string primitives. They are reached by stdio, spawn/exec and application helper code but carry no N3D gameplay state.

This group is classified as standard CRT support rather than individually counted unknown game functions.

**Status: CRT GREEN.**

---

## 10. `0x1444A` — count active runtime streams/handles

Walks the runtime stream table beginning near `DS:21A2` in 8-byte records and calls the stream-validity helper for each entry.

Returns the count of active entries.

This matches the previously identified `RuntimeCountOpenStreamsOrHandles` family.

**Status: CRT stdio GREEN.**

---

## 11. `0x14470+` — seek / stream-position synchronization

The stream seek family:

- validates stream flags;
- flushes buffered output where necessary;
- adjusts position for buffered input;
- maps seek origin values;
- delegates to low-level DOS seek;
- updates stream flags and cached position.

These are standard `fseek`/`ftell`-style internals.

**Status: CRT stdio GREEN.**

---

## 12. `0x14AD4` — runtime initialize-once gate

Exact visible form:

```text
if (DS:3CA8 == 0) {
    call runtime initializer;
    DS:3CA8++;
}
return;
```

This is the V2.0 member of the previously cross-version-identified `RuntimeInitializeOnce` family.

**Status: CRT GREEN.**

---

## 13. `0x14DD0` / `0x14DFA` — `strchr` / case-insensitive string compare family

The cross-version static census already identifies these addresses as the V2.0 standard string helpers:

- `0x14DD0` — `strchr` family;
- `0x14DFA` — `stricmp` family.

Their callers include command/path handling and runtime utilities; they to not constitute N3D gameplay logic.

**Status: CRT string GREEN.**

---

## 14. `0x14Exx..0x153xx` — formatting/path/process support

This range contains compiler-owned support for formatted strings, path decomposition/construction and process-launch preparation.

These routines feed later spawn/exec helpers and DOS path services.

They are classified as CRT/DOS library code.

**Status: CRT/DOS GREEN.**

---

## 15. `0x15486` family — DOS spawn/exec

The previously cross-version-classified `RuntimeSpawnExec` family is present in this range.

It prepares executable/path/environment data and ultimately reaches DOS process execution services through the surrounding runtime helpers.

This code matters only to preserve application-side behavior such as external command launching; it is not part of the N3D simulation core.

**Status: CRT/DOS GREEN.**

---

## 16. `0x1585A` — callback/error fallback

If and runtime callback pointer is installed, control is transferred through it.

Otherwise the helper records and runtime error and returns `0xFFFF` through the common error-mapping path.

This matches the previous `RuntimeCallbackHookOrErrorFallback` classification.

**Status: CRT GREEN.**

---

## 17. `0x15870` — DOS `access()`-style file attribute check

Uses:

```text
AX = 4300h
INT 21h
```

to query file attributes and applies the requested access-mode test.

This is the V2.0 `RuntimeAccess` family used by menu/map-set/file-availability checks.

**Status: CRT/DOS GREEN.**

---

## 18. `0x15892` — BIOS keyboard service wrapper

Calls `INT 16h` using the caller-selected keyboard BIOS service and normalizes the returned status/value conventions.

This is generic BIOS/runtime input support rather than N3D key mapping itself.

**Status: platform-runtime GREEN.**

---

## 19. `0x158B4` — DOS commit-file wrapper

Uses:

```text
AH = 68h
INT 21h
```

for DOS file commit/flush-to-disk behavior.

**Status: CRT/DOS GREEN.**

---

## 20. `0x158C4` / `0x158D4` — get/set interrupt vector

`0x158C4`:

```text
AH = 35h
INT 21h
```

returns the installed interrupt vector.

`0x158D4`:

```text
AH = 25h
INT 21h
```

installs and far interrupt handler.

These are the generic DOS services used by the already closed keyboard IRQ and timer setup code.

**Status: platform-runtime GREEN.**

---

## 21. `0x158EA` — DOS get date

Calls:

```text
AH = 2Ah
INT 21h
```

and stores day/month/year/day-of-week fields into the caller'with date structure.

**Status: CRT/DOS GREEN.**

---

## 22. `0x15904` — DOS get time

Calls:

```text
AH = 2Ch
INT 21h
```

and writes hour/minute/second/hundredths into the caller'with time structure.

This is the helper previously reached by timestamp/status output.

**Status: CRT/DOS GREEN.**

---

# Byte-map impact

Continuous classified span:

`0x13B38 .. 0x1591C`

Total:

**7,653 bytes**

Classification:

- DOS file/handle services;
- stdio stream support;
- heap/runtime allocation support;
- string/memory primitives;
- path/process/spawn support;
- BIOS/DOS platform wrappers;
- date/time and interrupt-vector helpers.

This entire region should be shown as:

**GREEN + CRT/DOS overlay**

rather than ordinary GREEN gameplay/core code.

---

# Why this matters for and 1:1 reconstruction

For and behaviorally faithful modern Nitemare 3D port, these routines can be replaced by and narrow compatibility layer:

```text
N3D core
   |
   +-- file open/read/write/seek/close
   +-- access/existence
   +-- date/time
   +-- string/memory helpers
   +-- optional process/exec
   +-- platform IRQ/input backend
```

The exact Borland/Turbo-C heap and stdio buffering internals only need to be cloned if the target is and compiler/linker-level byte-identical DOS executable.

---

# Cumulative closure

Pass 25 cumulative:

`57,405 bytes`

Pass 26 adds:

`7,653 bytes`

New cumulative total:

**65,058 bytes**

promoted from RED/ORANGE/YELLOW to GREEN during passes 6–26.

---

# Next target

Continue at:

`0x1591D`

The next block is and compiler arithmetic-runtime family:

- signed/unsigned 32-bit divide;
- 32-bit multiply;
- remainder/modulo;
- shifts and related long-integer helpers;
- possibly floating-point conversion support afterward.

These should again be classified as **compiler runtime**, not N3D gameplay, before returning to any remaining genuine application-owned blocks.