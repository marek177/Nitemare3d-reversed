# Nitemare 3-D Windows 1.10 — `-p`, input scanner and launch-route safety proof

**Date:** 20 October 2026. **Method:** original Win16 static-analysis evidence
first. **Status:** source/destination argument and original scanner local
width semantics established; **Windows 3.1 Program Manager** entry-field
route bounded from Microsoft KB Q71364. Other Win16/Win3.11 launch
routes and full alias/writer completeness remain OPEN.

## Significant correction: FUN_1008_6442 is an input scanner, not sprintf

The earlier
[WIN16_FILENAME_PREFIX_P0_STATIC_20261020.md](WIN16_FILENAME_PREFIX_P0_STATIC_20261020.md)
called `FUN_1008_6442` an output `sprintf-like` formatter.
That interpretation was incorrect. Direct original ASM and decompiled C
show the `-p` call is equivalent to a **scanf-family input conversion**:

    sscanf(parsed_argument_token, "%s", DS:46BE);

This is **not** a complete standard-library identity assertion:
`FUN_1008_6442` is the recovered application's Win16 stream-scanner
wrapper; its behavior matters more than the source-level name.

### Machine-code argument order (original Ghidra Win16 1.10)

    3:120C  PUSH 46BE             ; target buffer
    3:120F  PUSH 0D8C             ; DS:0D8C = "%s\0"
    3:1212  LEA AX,[BP-4]
    3:1215  PUSH AX
    3:1216  PUSH 0
    3:1218  CALL FAR 2:6B06       ; token reader; AX becomes token
    3:121D  ADD SP,4
    3:1220  PUSH AX              ; input TOKEN pointer
    3:1221  CALL FAR 2:6442      ; input scanner
    3:1226  ADD SP,6
    3:1229  CALL FAR 3:52AE      ; config.sav use

Original `FUN_1008_6442` accesses the first argument at
`2:644C` as its **source** string pointer; `2:645E` calls
`FUN_1008_609E` to measure its input length; `2:6474`
calls `FUN_1008_4504` with a source-stream state, a format pointer,
and the destination pointer taken from the remaining variadic arguments.
The original format bytes at `DS:0D8C` are `25 73 00` (`%s\0`).

`FUN_1008_4504`, **case `%s` at 2:46AC**, is scanner logic:

| Original code | Recovered behavior |
|---|---|
| `2:46AC` | sets input character class for `%s` conversion |
| `2:47F5` | tests if a numeric format-width field exists |
| `2:47FA` | if no width was specified, jumps over width-decrement exit |
| `2:480F` | reads the next input byte from the input stream |
| `2:4838` | stops if input character fails acceptance class |
| `2:4843` | loads output far pointer from conversion's argument |
| **`2:484B`** | **`MOV BYTE PTR ES:[BX],AL`**, writes accepted byte |
| `2:4892` | writes NUL to output upon completed `%s` conversion |

Original format is precisely `%s`, with **no numeric field width**.
The caller passes a destination pointer, but no destination capacity
value. On this path the local scanner limits the write by accepted
input length, not by the allocated size of `DS:46BE`.

An unusual failure/EOF/conversion path may change the exact number
of writes, but none supplies an intrinsic 4-KiB output bound. The
buffer overflow analysis must therefore follow the **maximum source
token length**, not invent a hidden `sprintf` output bound.

## Independent historical OS source: Windows 3.1 Program Manager

Microsoft Knowledge Base **Q71364**:
https://jeffpar.github.io/kbarchive/kb/071/Q71364/

The original Microsoft KB article's historical note states that the
Windows **3.1 Program Manager Program Item Properties Command Line**
field accepts at most **128 characters**. The article primarily
addresses Windows 3.0 and includes this explicit 3.1 comparison.

Scope of that bound:

- A command-line token obtained entirely from that editable
  Program Item field cannot exceed the whole field's length.
- Therefore, in **that one launch route**, the parsed `-p` prefix
  has length at most 128, and in realistic invocation it is smaller
  because the executable name and option occupy field characters.
- For `config.sav` (10 chars) and `user.sav` (8 chars), even the
  overconservative bound `prefix<=128` results in final offsets
  `128+10=138` and `128+8=136`, far smaller than the timer flag
  offset `DS:46B2 - DS:36BE = 0xFF4 = 4084`.
- Thus **the defined Program Manager Windows 3.1 launch field
  cannot supply enough input for the -p -> DS:46BE -> 5260
  scenario to touch DS:46B2**, assuming no other independent writer
  subsequently changes the prefix.

This does **NOT** prove a **universal Win16 lpCmdLine maximum**, a
limit for a separate `WinExec` caller or custom launcher, or an
independently verified Windows/Windows for Workgroups **3.11**
Program Manager input limit. Do not conflate these routes with
MS-DOS PSP command tails or modern CreateProcess/Win32 limits.

## Precise threshold still relevant for other routes

The original output staging start is `DS:36BE`;
the multimedia timer byte is `DS:46B2`.
The first overlapping output offset is `0xFF4=4084`:

| Suffix from all 12 named direct calls | Suffix length | Minimum prefix length |
|---|---:|---:|
| config.sav | 10 | 4074 |
| user.sav | 8 | 4076 |

The `%s` scanner itself has no explicit field width.
Whether some other Win16 3.11 launch mechanism can provide tokens
approaching 4,074 characters, and whether they pass all original
near-pointer parsing conditions, is **not yet proven**. No runtime
overflow was induced or observed.

## Reproducible evidence and tests

- `tools/n3d_win16_filename_alias_calls.py`: reports scanner
  source/destination, original opcode witnesses, both suffix
  thresholds and the scoped 128-character Program Manager route.
- `tests/test_n3d_win16_filename_alias_calls.py`: synthetic
  assertions for the lack of explicit `%s` field width, original
  destination write addresses, and scoped Program Manager safety.
- `.github/workflows/win16-timer-ne-proof.yml` runs the tests on
  GitHub Actions without original Windows executables.

## Remaining static P0 obligations

1. Resolve all pointer/alias writers to `DS:46BE`, not merely the
   `-p` path.
2. Examine alternate Windows 3.11 launcher command-line contracts
   and the actual `lpCmdLine` / Win16 MFC startup path from original
   Windows 3.11 sources, without substituting Win32 limits.
3. Finish computed/indexed scalar writers and non-REP copy helpers
   for watched bytes `DS:00A2` / `DS:46B2`.
4. Prove original program's indirect FAR target reachability
   separately; a 128-character launch field does not close arbitrary
   callback input or memory corruption.
5. Only when static evidence is exhausted, measure original
   Windows 3.11 environment for unresolved launcher conditions.

**No change to overall 1:1 behavior, timing or rendering parity percentages.**
