# Nitemare 3-D Win16 v1.10 timer: recovered archived ASM proof

**Audit synced:** 20 October 2026. **Original source audit:** RE MAX v0.61, 16–17 October 2026.

## Important correction to previous GitHub reports

Previous Win16 timing reports (19 October) marked the Win16 v1.10
timeEndPeriod stack argument at NE3:D6BE as OPEN solely because the
original EXE could not be reread by the local container.

The user's *pre-existing* archival research already contained the
Ghidra instruction listing with the answer:
- archived file: nite3w(1).docx, Ghidra disassembly section headed FUN_1010_d66c;
- independent extracted evidence: machine_anchors_v20.csv, records 0–29;
- archival SHA-gated report: N3D_REMAX_V061_ANALYZA_SK_20261017.md,
  original Win16 1.10 SHA-256
  12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481.

This is a **recovered existing original-static result**, not a new
fresh SHA verification or gameplay runtime measurement in October 20's session.
The independent current-turn check compared the exact quoted
Ghidra instruction bytes with the archived machine-anchors CSV and v0.61
report. All sources agree.

## Instruction-exact Win16 v1.10 lifecycle

### Startup: 3:0F14 -> 3:0F34 -> 3:D66C(0)

    3:0F32  6A 00        PUSH 0
    3:0F34  9A 6C D6 .. CALL FAR 3:D66C
    3:0F39  83 C4 02     ADD SP,2

The original Ghidra XREF table for 3:D66C names
FUN_1010_0F14:3:0F34 and FUN_1010_0F64:3:0F70.
The original 0F14 startup routine is itself called by 3:128D
inside FUN_1010_1118.

### Cleanup: 3:0F64 -> 3:0F70 -> 3:D66C(1)

    3:0F6E  6A 01        PUSH 1
    3:0F70  9A 6C D6 .. CALL FAR 3:D66C
    3:0F75  83 C4 02     ADD SP,2

The cleanup routine 0F64 is called by the destructor path
3:06B0 and by 4:316F from the error-handling path.
These are original-code XREF observations, not exhaustive dynamic reachability.

### Timer implementation (Ghidra original instruction bytes)

    3:D66C  C8 06 00 00 ENTER 6,0
    3:D670  56           PUSH SI
    3:D671  8B 46 06     MOV AX,[BP+6]
    3:D674  0B C0        OR AX,AX
    3:D676  74 06        JE D67E
    3:D678  48           DEC AX
    3:D679  74 39        JE D6B4
    3:D67E  8D 46 FA     LEA AX,[BP-6]
    3:D681  16           PUSH SS
    3:D682  50           PUSH AX
    3:D683  6A 04        PUSH 4
    3:D685  9A ..        CALL FAR MMSYSTEM.604 timeGetDevCaps
    3:D68A  3D 01 00     CMP AX,1
    3:D68D  1A C0        SBB AL,AL
    3:D68F  F6 D8        NEG AL
    3:D691  A2 B2 46     MOV DS:[46B2],AL
    3:D694  8B 76 FA     MOV SI,[BP-6]
    3:D697  83 EE 0A     SUB SI,10
    3:D69A  1B C0        SBB AX,AX
    3:D69C  F7 D0        NOT AX
    3:D69E  23 F0        AND SI,AX
    3:D6A0  83 C6 0A     ADD SI,10
    3:D6A3  80 3E B2 46 00  CMP BYTE PTR DS:[46B2],0
    3:D6A8  74 19        JE D6C3
    3:D6AA  56           PUSH SI
    3:D6AB  9A ..        CALL FAR MMSYSTEM.605 timeBeginPeriod
    3:D6B0  5E           POP SI
    3:D6B1  C9           LEAVE
    3:D6B2  CB           RETF
    3:D6B4  80 3E B2 46 00  CMP BYTE PTR DS:[46B2],0
    3:D6B9  74 08        JE D6C3
    3:D6BB  FF 76 FE     PUSH WORD PTR SS:[BP-2]
    3:D6BE  9A ..        CALL FAR MMSYSTEM.606 timeEndPeriod
    3:D6C3  5E           POP SI
    3:D6C4  C9           LEAVE
    3:D6C5  CB           RETF

The timeGetDevCaps size is 4 bytes and output buffer begins at BP-6;
its output spans BP-6 through BP-3. The end branch can be entered
directly from 3:D679 without visiting any initializer. No instruction
in this lifecycle routine initializes BP-2 before its read at D6BB.
ENTER 6,0 reserves locals, but does not zero them.

Therefore **the exact local operand for timeEndPeriod in pinned Win16
1.10 is SS:[BP-2] and is read-before-write in the local body**.
This mirrors pinned Windows v1.8 at 3:D60D. Neither case proves any
particular residual stack WORD during a real execution.
Original 16-bit MMSYSTEM.606 takes exactly one UINT16 period argument;
matching begin and end resolutions is the intended Windows multimedia API
contract. Host C++ should not imitate undefined stack-variable reads.

## Evidence level and what remains open

- CLOSE (archived original ASM): Win16 1.10 local byte opcode
  3:D6BB FF 76 FE and conditional timeEndPeriod entry at 3:D6BE.
- CLOSE (archived original ASM): two named direct lifecycle calls with
  immediate arguments 0 and 1, at 3:0F34 and 3:0F70.
- CLOSE (archived local dataflow): BP-2 is not written in 3:D66C..D6C5
  prior to the cleanup push, and the 4-byte TIMECAPS buffer cannot overlap it.
- PARTIAL: archived v0.61 claims SHA-gated original 12-build verification,
  but the original 230,400-byte EXE was not rehashed in this session.
  The new verifier now encodes expected v1.10 opcodes for a reproducible
  later exact-EXE check; do not confuse synthetic CI with a new original run.
- OPEN: global exhaustive indirect FAR and aliased-pointer caller census
  (V058-10); current Ghidra direct XREF list is not exhaustive.
- OPEN: actual original Windows 3.11 stack residue, MMSYSTEM.606 return
  code, effect on system timer resolution and exact timing parity.
- OPEN: all other global 1:1 rendering/AI/combat parity obligations.

Original proprietary EXE bytes have not been committed; only short
instruction anchors, independent original-derived reports and code tests.

## Existing original provenance

RE MAX v0.61 supplied matching whole-original Win16 v1.10 SHA-256
12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481
and the corresponding opcode/codepath table. No new percentage increase.
