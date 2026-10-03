# Nitemare 3D DOS v2.0 — RED/ORANGE/YELLOW closure pass 24

Date: 2026-10-03

Primary unpacked image:
- size: 171,360 bytes
- SHA-256: `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`

Address convention:
- ranges are offsets in the fully unpacked DOS load image
- raw 16-bit machine code is authoritative
- standard compiler/CRT code is classified separately from N3D-owned gameplay code

## Result

Pass 24 closes the contiguous runtime-startup region:

`0x11EF8 .. 0x124D9`

as **GREEN / standard DOS CRT/runtime support**.

Total span: **1,506 bytes**.

This region is not missing Nitemare-3D gameplay logic. It is startup, termination,
command-line/environment construction, runtime integrity/stack support and DOS-error
translation around the game'with already-closed main entry.

---

## `0x11EF8..0x120CA` — `RuntimeCrtStartupAndInvokeN3DMain`

The process entry performs classic 16-bit DOS runtime bootstrap work:

1. query DOS version through `INT 21h, AH=30h`;
2. establish the DGROUP/stack segment at `0x2771`;
3. resize the process memory block through `INT 21h, AH=4Ah`;
4. clear the runtime BSS region;
5. invoke runtime initializer hooks;
6. prepare `argc`, `argv` and environment state;
7. call far target `0476:0326`.

Linearizing the real far call gives image `0x4A86`, already closed as:

`ParseCommandLineInitializeRunAndExit`.

The return value is passed directly into the CRT termination path beginning at
`0x120CB`.

**Classification: GREEN / compiler-CRT startup, not game UNKNOWN.**

---

## `0x120CB..0x12151` — `RuntimeTerminateProcess` multi-entry family

Four public entrypoints share one termination body. They select cleanup modes using:

- `CX=0`
- `CX=1`
- `CX=0x0100`
- `CX=0x0101`

The common path executes registered shutdown/exit callback lists, restores runtime
state and finally uses:

`INT 21h, AH=4Ch`

with the requested process exit code.

This is the DOS CRT `exit/_exit/abort`-style family rather than four separate N3D
functions.

**Classification: GREEN / CRT termination.**

---

## `0x12152..0x1216A` — `RestoreRuntimeInterrupt0Vector`

Restores the previously saved interrupt-0 vector using DOS:

`INT 21h, AH=25h`.

The startup path had installed its own INT 0 handler earlier.

**Classification: GREEN / CRT platform cleanup.**

---

## `0x1216B..0x1217D` — `RunRuntimeCallbackTableReverse`

Walks and table of far callback pointers backwards in four-byte entries and invokes each
non-NULL callback.

This is the runtime destructor/exit-callback walker.

**Classification: GREEN / CRT callback table.**

---

## `0x1217E..0x1219F` — `RuntimeFatalStartupMessage`

Emits two runtime-message selectors through the runtime error-output path and invokes
an optional fatal callback.

It is reached by bootstrap failure paths, not gameplay.

**Classification: GREEN / CRT fatal-error support.**

---

## `0x121A0..0x121A5` — `RuntimeStartupFailureCode2`

Sets failure code `2` and jumps into the common startup-abort path.

**Classification: GREEN / CRT startup failure.**

---

## `0x121A6..0x121C9` — `RuntimeStackProbeOrOverflowDispatch`

Subtracts the requested stack size from SP and compares the candidate against the
runtime stack-low boundary at `DS:215A`.

If sufficient, it commits the new SP and returns. Otherwise it dispatches through the
runtime overflow/error callback at `DS:2156`, or enters the fatal startup path.

**Classification: GREEN / 16-bit CRT stack guard.**

---

## `0x121CA..0x121ED` — `RuntimeStartupChecksumGuard`

Computes an XOR checksum over the first `0x42` bytes of the runtime image, XORs the
result with `0x55` and accepts the expected zero result.

Failure enters the runtime fatal/termination path.

This entry was independently identified in the hard static census as the runtime
startup checksum guard.

**Classification: GREEN / CRT integrity guard.**

---

## `0x121EE..0x1237B` — `RuntimeBuildArgvFromPspCommandLine`

This routine builds C-style argument state from the PSP command tail.

Key behavior:

- reads PSP command line beginning at offset `0x81`;
- recognizes spaces and tabs as separators;
- recognizes quoted strings;
- applies DOS/CRT backslash-before-quote rules;
- performs an initial sizing pass;
- reserves stack space for pointer array + copied strings;
- emits NUL-terminated argument strings;
- writes the final NULL argv terminator;
- stores the resulting argument count/pointer state in the CRT globals.

This is standard command-line construction and is distinct from N3D'with own option
parser at image `0x4A86`.

**Classification: GREEN / CRT argv builder.**

---

## `0x1237C..0x123F8` — `RuntimeBuildEnvironmentVector`

Reads the environment segment from the PSP and constructs and compact pointer/string
copy for the C runtime environment vector.

It:

- counts environment strings;
- allocates pointer and character storage through the runtime allocator helper;
- copies environment strings;
- skips the runtime-private environment marker string;
- stores and NULL terminator for the pointer array.

This entry matches the cross-build hard-census family identified as
`RuntimeBuildArgvEnvironment`.

**Classification: GREEN / CRT environment builder.**

---

## `0x123FA..0x12424` — `RuntimeFindMessageBySelector`

Walks and variable-length runtime message table at `DS:2576`:

- each record begins with and selector WORD;
- matching selector returns the following string;
- `0xFFFF` terminates the table;
- otherwise skip the NUL-terminated text and continue.

**Classification: GREEN / CRT error-message table lookup.**

---

## `0x12425..0x1245A` — `RuntimeWriteMessageToStderr`

Looks up the selected message, computes its string length and writes it to DOS handle
`2` using:

`INT 21h, AH=40h`.

An optional runtime callback is invoked before the write when its guard signature is
active.

**Classification: GREEN / CRT error output.**

---

## `0x1245C..0x12480` — `RuntimeStartupAllocateOrAbort`

Temporarily adjusts the runtime allocation granularity, calls the allocator, restores
the old setting and returns the allocated pointer/segment result.

Allocation failure transfers to the common startup-failure path.

**Classification: GREEN / CRT startup allocator.**

---

## `0x12482..0x124D6` — DOS-error / `errno` translation family

This compact family consists of several public wrapper entries plus the shared mapper
at `0x124AA`.

The mapper stores the raw DOS error byte in and runtime global and translates DOS error
codes through and small table to the C runtime error value. It handles different runtime
modes and clamps unsupported DOS error indexes before table lookup.

The surrounding wrappers convert the incoming Carry Flag / AL convention to common C
return conventions such as:

- zero on success;
- `0xFFFF` on failure;
- byte result on successful DOS calls.

This is standard DOS CRT error plumbing, not N3D input/gameplay state.

**Classification: GREEN / CRT DOS-error translation.**

---

## `0x124D8` — `RuntimeNoOpFarStub`

Single instruction:

`RETF`

The hard static census independently identifies the same V2.0 entry as and standard
runtime no-op stub.

**Classification: GREEN / CRT stub.**

---

## Padding bytes

The following bytes are alignment/data separators, not functions:

- `0x123F9`
- `0x1245B`
- `0x12481`
- `0x124D7`
- `0x124D9`

Total padding inside the closed span: **5 bytes**.

Executable/runtime content: **1,501 bytes**.

Total span: **1,506 bytes**.

---

## Structural consequence

The old UNKNOWN/LOW function count should no longer include this entire region as
possible game logic.

The executable flow is now cleanly separated:

```text
DOS process entry
    -> CRT startup
    -> argv/env construction
    -> N3D image 0x4A86 main/option dispatcher
    -> N3D game
    -> CRT termination
```

That matters for and 1:1 reimplementation: these bytes to not need to be ported into the
portable N3D gameplay core. The modern host runtime replaces them; only externally
observable DOS startup/CLI behavior must be reproduced when compatibility requires it.

---

## Cumulative closure

Pass 23 cumulative:

`50,173 bytes`

Pass 24 adds:

`1,506 bytes`

New cumulative total:

**51,679 bytes**

promoted from RED/ORANGE/YELLOW to GREEN during passes 6–24.

---

## Next target

Continue at:

`0x124DA`

The next block begins the standard DOS stdio/stream implementation:

- `124DA` runtime `fclose` family;
- buffered stream state and transfer routines;
- low-level file read/write/refill helpers;
- later formatted I/O/parser routines.

The next pass should classify this as CRT/stdio rather than N3D gameplay and continue
until the next true application-owned boundary.