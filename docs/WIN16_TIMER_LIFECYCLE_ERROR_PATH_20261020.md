# Nitemare 3-D Win16 1.10 — timer lifecycle error path and return-code gate

**RE pass:** 20 October 2026. **Proof level:** archived original Ghidra Win16
instruction listing + local contract tests. The original game was not
executed; whole-program indirect FAR call reachability remains OPEN.

## Original call ordering

Original disassembly in the user's archived
`nite3w(1).docx`, logical NE segment 3:

| Caller | Site | Callee | Mode | Role |
|---|---|---|---:|---|
| `FUN_1010_1118` | `3:128D` | `FUN_1010_0F14` | no arg | Startup, after command-line parser dispatch |
| `FUN_1010_0F14` | `3:0F20` | `FUN_1010_2F36` | 0 | WinG bitmap setup |
| `FUN_1010_0F14` | `3:0F2A` | `FUN_1010_E0C4` | 0 | Multimedia startup |
| `FUN_1010_0F14` | `3:0F34` | `FUN_1010_D66C` | 0 | Multimedia clock setup |
| `FUN_1010_0F64` | `3:0F66` | `FUN_1010_E0C4` | 1 | Multimedia cleanup |
| `FUN_1010_0F64` | `3:0F70` | `FUN_1010_D66C` | 1 | Multimedia clock cleanup |
| `FUN_1018_3118` | `4:316F` | `FUN_1010_0F64` | no arg | Error-handler global cleanup |
| `FUN_1010_06A0` | `3:06B0` | `FUN_1010_0F64` | no arg | CMainFrame cleanup chain |

Timer setup is preceded by audio setup in the **same** direct startup
wrapper. The original Ghidra XREF on `FUN_1010_D66C` includes its two
direct callers `3:0F34` and `3:0F70`. An original SHA-verified
NE reference census is independently complete only for Win16 1.8
(`3:D5BE`, two direct original fixups; see
`WIN16_TIMER_TARGET_INDIRECT_CENSUS_20261020.md`). It is not yet
repeated against exact Win16 1.10 original bytes.

## New bounded failure-ordering observation

Within Win16 1.10 `FUN_1010_E0C4(mode=0)`, the original code checks a
`GLOBALALLOC` return at `3:E1A5/E1A7`. On null allocation it takes the
`3:E1A9–E1AC` error path and calls `FUN_1018_3118`, **before**
the ordinary wrapper proceeds to timer setup `3:0F34`.

The error handler `FUN_1018_3118` performs, in order:

1. Possible return from DisplayDib fullscreen (`4:3123`, conditional).
2. `DS:4BE2 = 0` then `E0C4(mode=2)` (`4:3134`).
3. Message formatting, beep and error dialog.
4. Calls global cleanup wrapper `0F64` at `4:316F`.
5. Calls a termination/helper function at `4:3176`.

Therefore the original has a **syntactically connected failure path**
where cleanup is requested before ordinary timer initialization. Whether
a particular machine/memory failure reaches the entire path depends on
actual execution; this is not a claim of observed runtime failure.

Crucially `D66C(mode=1)` gates `MMSYSTEM.606` on
`DS:[46B2] != 0`. If that byte remains zero before timer setup,
the premature cleanup skips the multimedia-timer API call. No
whole-program proof of *every possible writer* to the flag is asserted.

## Cleanup call semantics

Instruction-exact archived NE3:D66C:

    D66C ENTER 6,0
    D66C+... branches on mode=0 / mode=1
    D6B4 CMP BYTE PTR DS:[46B2],0
    D6B9 JE D6C3
    D6BB PUSH WORD PTR SS:[BP-2]
    D6BE CALL FAR MMSYSTEM.606 timeEndPeriod
    D6C3 POP SI
    D6C4 LEAVE
    D6C5 RETF

The original cleanup operation **does not** set DS:46B2 to zero.
The API return in AX is not checked locally, and no register/state
change resulting from the return is used to update the flag.

Its argument `[BP-2]` is read-before-write in the same local
`ENTER 6,0` frame. It does not equal the successful
`timeBeginPeriod(SI)` value by construction. See the separate
archived-ASM proof for Win16 1.10, and original binary Win16 1.8
verification.

If `D66C(1)` is called a second time with DS:46B2 still nonzero,
it issues a second `timeEndPeriod` request, independently of the
first result. **This is a local conditional behavior**, not evidence
that any natural user session really performs the cleanup twice.

The normal timer initialization path sets DS:46B2 from the
`timeGetDevCaps` result. If capabilities succeed, it calls
`timeBeginPeriod(max(wPeriodMin,10))` but does not check the return
from that API; therefore a begin-period failure does not automatically
switch the reader to GetTickCount. The mode byte selects
`timeGetTime` or `GetTickCount` at NE3:D6C6.

## Synthetic test contract

- `src/re/Win16TimerLifecycleGate.hpp` models the two branches of
  original `D66C`, the retained flag and the unknown stack-residue
  argument without reading any uninitialized host-language data.
- `tests/win16_timer_lifecycle_gate_test.cpp` validates the period
  clamp across all 65,536 UINT16 inputs, success/failure, preserved
  flag and conditional repeat behavior.
- `.github/workflows/win16-clock-presentation-static.yml` compiles
  and runs the test with C++20 and GCC -Werror.
- The test is also registered in `CMakeLists.txt` for CTest.

These are synthetic/local correctness checks. The repository
does not distribute Windows 3.x, multimedia DLLs or original game
executables; no claim of actual runtime 1:1 timing is made.

## Remaining proof obligations

1. Complete NE fixup, code/data alias and indirect FAR census for
   the pinned original Win16 1.10 executable target `NE3:D66C`.
2. Complete DS:46B2 writer and initialization audit, including
   user MFC/error paths and any writable callback pointers.
3. Characterize original-stack `SS:[BP-2]` on the *real* failure and
   ordinary-close trajectories, only after static possibilities are
   exhausted. Treat the exact local operand as proven, but its runtime
   numeric value as UNKNOWN.
4. Distinguish low-level source behavior from intentional safe
   modernization when adapting `timeEndPeriod` to Windows 11.

**Global behavior, timing and renderer 1:1 parity percentages: unchanged.**
