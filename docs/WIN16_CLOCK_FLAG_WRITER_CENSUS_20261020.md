# Nitemare 3-D Win16 1.10 — clock mode and one-shot latch writer census

**RE pass:** 20 October 2026. **Provenance:** pre-existing original
Ghidra ASM/DS binary listing in the user archive `nite3w(1).docx`.
This note is recovered existing original STATIC evidence; no original
Win16 runtime or new 230,400-byte EXE SHA check was performed in this pass.

## Original DGROUP initial values

| DGROUP address | Original byte | Role |
|---|---:|---|
| DS:00A2 | `01` | One-shot global initialization latch |
| DS:46B2 | `00` | Multimedia clock mode flag |

The original Ghidra DGROUP listing identifies
`DAT_1048_00a2 XREF[2]`: `1010:0E9E(R)`, `1010:0ECA(W)`.
There is only ONE directly resolved writer to the latch in this recovered
XREF table.

The original Ghidra DGROUP listing identifies
`DAT_1048_46b2 XREF[5]`: two writes and three reads:

| Offset | Opcode (original Ghidra listing) | Direct role |
|---|---|---|
| NE3:0ED6 | `A2 B2 46` | Clock flag cleared to zero on first global init |
| NE3:D691 | `A2 B2 46` | Clock flag set from timeGetDevCaps success |
| NE3:D6A3 | `80 3E B2 46 00` | Capability-success gate to timeBeginPeriod |
| NE3:D6B4 | `80 3E B2 46 00` | Cleanup gate to timeEndPeriod |
| NE3:D6C6 | `80 3E B2 46 00` | timeGetTime vs GetTickCount reader gate |

This is a census of **direct resolved symbol XREFs**. It does NOT
include pointer-alias/ES writes or all hypothetical dynamically computed
DGROUP addressing. Overlapping dword/word writes also need their own
writer graph; the obvious neighboring writes at `3:93A4`,
`3:93CB`, and `3:93D2` target DS:46B1 with explicit BYTE
opcodes `C6 06 B1 46 ..` and therefore do **not** overlap DS:46B2.

## Exact initial reset 3:0E9E

    3:0E9E  80 3E A2 00 00   CMP BYTE PTR DS:[00A2],0
    3:0EA3  74 37            JE 3:0EDC
    ...
    3:0EC8  32 C0            XOR AL,AL
    3:0ECA  A2 A2 00         MOV DS:[00A2],AL
    3:0ECD  A2 AB 46         MOV DS:[46AB],AL
    3:0ED0  A2 AE 46         MOV DS:[46AE],AL
    3:0ED3  A2 B0 46         MOV DS:[46B0],AL
    3:0ED6  A2 B2 46         MOV DS:[46B2],AL
    3:0ED9  A2 BE 46         MOV DS:[46BE],AL

Normal Win16 startup reaches 3:0E9E from `FUN_1010_1118`
at `3:1129` BEFORE command-line parsing/WinG/video/audio/timer init
(the direct normal timer setup is `3:0F34`).
If DS:00A2 initially equals 1, the routine clears it and resets
the timer flag to zero. On later entries with DS:00A2 still zero, the
branch at 0EA3 skips DS:46B2 reset. Another direct caller of 0E9E
in the original Ghidra XREF table is `FUN_1018_09F2:4:0A16`.

This explains why the directly traced sound-initialization failure
before `3:0F34` can call global shutdown while DS:46B2 remains zero:
`D66C(mode=1)` skips the multimedia end API in this regular first
startup sequence. If an untraced alias writer/reentrant hook modifies
the byte between the reset and shutdown, further proof is required
before generalizing beyond this static path.

The later original timer `D66C(mode=0)` overwrites DS:46B2 based on
`timeGetDevCaps`, independent of `timeBeginPeriod` success. Its
mode=1 branch does not reset that byte after calling `timeEndPeriod`.

## Bounded code/test regression

- `src/re/Win16TimerLifecycleGate.hpp` models only the one-shot
  reset predicate and clock flag outcome (no host memory reads).
- `tests/win16_timer_lifecycle_gate_test.cpp` checks initial
  values, both direct writer addresses, first-entry reset and
  subsequent latch==0 preservation of a selected multimedia flag.
- `tools/n3d_win16_timer_binary_proof.py` pins 0E9E, 0EA3, 0EC8,
  0ECA and 0ED6 original opcode witnesses to the hash-gated verifier.
- `tests/test_n3d_win16_timer_archive_v110.py` asserts the same
  archived-code witnesses through synthetic fixtures.
- C++20 and Python verification workflows run separately. These are
  non-runtime regression tests.

## Proof obligations that remain open

1. Pointer-derived, overlapped and aliased writers to DS:00A2 / 46B2,
   including far ES: based accesses and mixed-width memory stores.
2. Exhaustive Win16 v1.10 NE-fixup/call-target census of timer 3:D66C;
   the original Ghidra direct XREF names two callers, not a global
   exclusion proof for all dynamic FAR pointer paths.
3. Original runtime stack residue SS:[BP-2] and multimedia
   timeEndPeriod response under authentic Windows 3.11 conditions.
4. Full frame/timing/pixel equality across DOS/Windows and remake.

**Behavior/timing/render parity percentages are unchanged.**
