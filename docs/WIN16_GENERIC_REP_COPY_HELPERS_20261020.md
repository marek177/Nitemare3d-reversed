# Win16 1.10 — generic REP copy helper reachability

Audit date: 20 October 2026. Original source: archived Ghidra Win16
disassembly nite3w(1).docx. This is statically recovered evidence,
not a fresh v1.10 original EXE hash/run or runtime parity proof.

## Six REP sites across three generic helpers

| Helper | REP sites | Behavior | Proof status |
|---|---|---|---|
| NE2:602C | NE2:605F MOVSW; 6063 MOVSB | NUL-terminated strcat-like append | Only named direct call is guarded false; if forced, source is 2-byte literal |
| NE2:606C | NE2:6092 MOVSW; 6096 MOVSB | NUL-terminated strcpy-like copy | Two named caller envelopes; one static two-byte source, one heap strlen+1 source; capacity/overflow still OPEN |
| NE2:6C80 | NE2:6CA0 MOVSW; 6CA4 MOVSB | Parameter-count memcpy-like copy | Eight named caller edges; byte count exact but destination alias/capacity still OPEN |

Machine-code behavior labels do not imply standard-library ABI equivalence
or a full global indirect-call provenance closure.

## 1. The sole named strcat call is gated unreachable on normal input

The original Win16 v1.10 DGROUP image contains:
- DS:08CC: bytes 5C 00 (backslash followed by NUL)
- DS:08CE: bytes 5C 00 (another backslash followed by NUL).

Original FUN_1008_3D80 (NE2) shows:

    2:3D85 SUB SP,12h             ; caller's stack local space
    2:3E0E MOV AX,08CCh
    2:3E11 PUSH AX
    2:3E12 LEA AX,[BP-0Eh]
    2:3E15 PUSH AX
    2:3E16 CALL FAR 2:606C       ; copy backslash and NUL, exactly 2 bytes
    2:3E1B ADD SP,4
    2:3E24 CMP BYTE [BP-0Eh],5Ch
    2:3E28 JE 2:3E3C            ; true after successful fixed string copy
    2:3E2A MOV AX,08CEh
    2:3E32 CALL FAR 2:602C       ; append second backslash, bypassed

The code between the initial strcpy call and the compare does not
write the compared byte. The compare must therefore be true if the
copy completed normally and no unexpected memory alias clobbers it.
Thus the only named direct call to strcat-like 2:602C is not
executed along this normal local instruction path.

If a fault, memory corruption or indirect call forces 2:602C
to execute with these original operands, DS:08CE contributes
exactly two bytes (backslash + NUL). Within this caller frame
the maximum composed string is 3 bytes (two slashes + NUL).
This conditional two-byte bound is recorded separately from
global dynamic helper reachability.

The static REP ledger marks 1008:605F and 1008:6063 as
DIRECT_CALL_BRANCH_FALSE_SLASH_APPEND. This is not a reason
to remove the original helper from the 1:1 clean-room port.

## 2. Two named direct callers of near strcpy-like NE2:606C

- At 2:3E16 source is DS:08CC (backslash NUL, 2 bytes)
  and destination is SS:BP-0E inside the allocated 12h-byte caller frame.
- At 2:69C0, FUN_1008_699C first invokes strlen(src)
  at 2:69AB, increments AX at 2:69B0, requests LocalAlloc(strlen+1)
  via 2:69B2, and only on a nonzero return copies the original source.

For ordinary valid NUL-terminated strings whose strlen+1 fits
uint16, the heap caller attempts to allocate precisely enough
space for the copy. Its edge is not a globally fixed-size copy.

Boundary still OPEN: when the 16-bit length is FFFFh, INC AX
wraps to zero; the LocalAlloc wrapper substitutes a one-byte
request for zero. The source's reachability at that extreme,
overflow consequences, indirect callers and computed pointer
aliases have not been closed. Thus 1008:6092/6096 remain
STRCPY_DIRECT_CALLER_ENVELOPES_PARTIAL among OPEN REP sites.

## 3. MEMCPY-like NE2:6C80: caller WORD count is exact

Original relevant bytes and operands:

    2:6C8B MOV SI,[BP+8]       ; near source
    2:6C8E MOV DI,[BP+6]       ; near destination
    2:6C93 MOV CX,[BP+0Ah]     ; uint16 byte count
    2:6C96 JCXZ 2:6CA6
    2:6C98 TEST AL,1
    2:6C9C MOVSB              ; if destination is odd
    2:6C9D DEC CX
    2:6C9E SHR CX,1
    2:6CA0 REP MOVSW
    2:6CA2 ADC CX,CX
    2:6CA4 REP MOVSB

For any uint16 n and destination parity:
- lead = 1 iff destination odd and n>0; otherwise 0.
- words = (n-lead)//2.
- tail = (n-lead)%2.
- lead + 2*words + tail = n.

This byte-count formula is verified for all 65536 n values
and both parity cases in synthetic regression. It does not
prove source/destination capacity, address-wrap exclusion or
that the target cannot overlap DGROUP timer flag DS:46B2.

Eight named direct Ghidra caller sites:

    0:0DD0  0:0E16  0:0E51  0:0ED9
    0:0EEA  0:0F74  0:4C72  2:3F20

For the 2:3F20 site, original caller FUN_1008_3EBE
compares current available bytes with remaining buffer count
and chooses their unsigned minimum at 2:3F12..3F18 before
copying. It uses the unusual PUSH CS + CALL NEAR 6C80
combination so that the far-returning callee's RETF still
has a valid saved CS/IP. This is a *single-site count guard*,
not complete pointer capacity proof for all eight sites.

The ledger marks 1008:6CA0/6CA4 as
MEMCPY_16BIT_PARAMETER_TARGET_OPEN, with the original eight
direct callers preserved for future interprocedural analysis.

## Current REP evidence counts, bounded to archived Ghidra listing

| Evidence scope | Count |
|---|---:|
| Earlier fixed/source-bounded REP sites | 46 |
| New direct-branch-excluded slash-copy sites (2-byte bound if reached) | 2 |
| LocalAlloc symbolic-length STOSW | 1 |
| Unresolved destination/length, including strcpy and memcpy helpers | 34 |
| **Total** | **83** |

The 48 fixed/conditional-class sites are NOT 48 proven gameplay
executions. Reachability and bounds have different evidence grades.
No Win16 1.10 original runtime was performed; no 1:1 behavior,
timing or pixel-parity percentage changed.

Source and regression:
- other/n3d/builds_12/static_byte_evidence/N3D_Win110_Ghidra_REP_destination_register_20261020.csv
- tools/n3d_win16_rep_destination_audit.py
- tests/test_n3d_win16_rep_destination_audit.py
- .github/workflows/win16-timer-ne-proof.yml

Next statics: dataflow for remaining eight memcpy caller pointers
and remaining 34 original Ghidra REP sites; then indexed ES:DI
aliases, non-REP byte writers and hidden callback targets.
