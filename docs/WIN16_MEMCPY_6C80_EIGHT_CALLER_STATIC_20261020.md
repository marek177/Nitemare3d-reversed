# Nitemare 3-D Win16 v1.10 — eight direct memcpy callers

**Audit:** 20 October 2026. **Method:** original-static reverse engineering.
Primary source: archived original Ghidra listing nite3w(1).docx, logical
Win16 code NE segment 1 (Ghidra 1000) and segment 2 (Ghidra 1008).
No fresh original Win16 1.10 executable SHA-256 check or runtime execution.

## Address labels and callee

This document uses original **Ghidra selectors** 1000 and 1008.
Earlier shorthand 0:hhhh and 2:hhhh in older audit prose denotes
these same locations. The exact callee is FUN_1008_6C80.

    1008:6C8B  MOV SI,[BP+8]     ; source near offset
    1008:6C8E  MOV DI,[BP+6]     ; destination near offset
    1008:6C93  MOV CX,[BP+0A]   ; uint16 copy bytes
    1008:6C96  JCXZ 6CA6
    1008:6C98  TEST AL,1        ; destination parity
    1008:6C9C  MOVSB            ; optional leading byte
    1008:6C9D  DEC CX
    1008:6C9E  SHR CX,1
    1008:6CA0  REP MOVSW
    1008:6CA2  ADC CX,CX
    1008:6CA4  REP MOVSB

The helper sets ES from the active DS; caller arguments supply NEAR
offsets, not arbitrary FAR destination segment selectors.
The copy counts are instruction-exact for a non-faulting execution,
but no callee-side destination capacity check exists.

## All eight named original direct callsites

| Original callsite | Target offset | Source offset | Bytes copied | Local guard / allocation |
|---|---|---|---|---|
| 1000:0DD0 | [param5 struct+0] | [param1 struct+0] + param3 | param4 | 0DBF requests reallocation sized uint16(param2+param4) |
| 1000:0E16 | [param1 struct+0] | param2 string | strlen(param2) | 0E0B requests allocation strlen+1 |
| 1000:0E51 | [param1 struct+0] | param2 string | param3 | 0E30 CMP capacity,requested; signed JGE or reallocation |
| 1000:0ED9 | [param1 struct+0] | param4 buffer | param5 | 0EC7 computes combined uint16(param5+param3) |
| 1000:0EEA | [param1 struct+0] + param5 | param2 buffer | param3 | same combined length, destination offset computed at 0EE7 |
| 1000:0F74 | new [struct+0] | saved old pointer [BP-2] | old used length [struct+2] | 0F58 compares capacity,requested with signed JGE |
| 1000:4C72 | [struct+0] + used | param2 | param3 | 4C43 ADD used+count wraps; 4C49 signed JLE selects fast append |
| 1008:3F20 | caller output BX | stream cursor [SI+0] | unsigned min(available,remaining) | 3F12..3F18 chooses minimum, nonzero available required |

Seven sites use an immediate FAR CALL opcode. At 1008:3F20 the
original code uses PUSH CS followed by a near CALL so that the
RETF-returning callee receives the expected far-return stack frame.
These eight edges are from the archived original Ghidra direct XREF
table; computed or indirect FAR callers are not ruled out.

The exact per-site source, destination, byte-count expression, local
guard and unclosed pointer/size obligation are pinned in the CSV:
other/n3d/builds_12/static_byte_evidence/
N3D_Win110_memcpy_6C80_direct_callers_20261020.csv.

## Important local 16-bit boundary behavior

At 1000:0E51 and 1000:0F74, the original checks capacity with
a SIGNED JGE rather than an unsigned compare. For hypothetical
capacity = 0x7FFF (32767) and requested = 0x8000 (32768),
the original signed comparison reads 32767 >= -32768,
and incorrectly treats the capacity as sufficient for the
unsigned requested length. This is an arithmetic counterexample;
no claim of real-world execution with those parameters is made.

At 1000:4C72 the original fast append path performs:

    1000:4C40 MOV AX,[SI+2]       ; used count
    1000:4C43 ADD AX,[BP+0A]     ; new total modulo 2^16
    1000:4C46 CMP AX,[SI+4]      ; stored capacity
    1000:4C49 JLE 4C66          ; SIGNED JLE

With hypothetical used = 65530, added = 10 and
capacity = 20, unsigned true total is 65540 but the
wrapped 16-bit AX is 4. Thus signed 4 <= 20 allows the
fast-path copy, even though the unsigned requested length
does not fit. This result is a local arithmetic witness,
not an observed buffer overflow or a proven reachable state.

A stronger mathematical counterexample has a **valid pre-call**
used<=capacity relationship: used=0, capacity=32767, added=32768.
The 16-bit AX becomes 0x8000, interpreted as -32768 by JLE,
and the original therefore chooses the fast append branch even
though the requested 32768 bytes exceed 32767 data-byte capacity.
The subsequent terminating NUL would be written after those
bytes. This is a conditional original-ASM hazard, not proof that
a real Windows 3.11 gameplay or user-input path reaches 32768
characters.

The append and two-part concatenation helper also compute
combined lengths using 16-bit ADD with no observed carry
check before requesting allocation. Local allocator helper
FUN_1000_0D3E requests uint16(count+1) bytes and writes
a trailing zero on its normal route. At count=65535 this
size calculation wraps to zero and requires separate heap
and reachability analysis.

The stream copy at 1008:3F20 is different: its local
unsigned count is min(stream.available, requested.remaining)
and it decrements both after copying. This is an exact
per-iteration byte-count restriction, but it does not prove
that the caller output buffer is large enough or that
the stream object's pointers are valid.

## Reproducible synthetic tests

- Static auditor: tools/n3d_win16_memcpy_6c80_caller_audit.py
- Eight caller ledger: other/n3d/builds_12/static_byte_evidence/
  N3D_Win110_memcpy_6C80_direct_callers_20261020.csv
- Tests: tests/test_n3d_win16_memcpy_6c80_caller_audit.py
- CI: .github/workflows/win16-timer-ne-proof.yml

The synthetic tests check all eight direct site labels, all
three signed capacity branch sites, four uint16 addition sites,
the unsigned stream minimum, local strdup length+1 wrap, and
intentional corrupted ledger entries. Signed differences and
boundary examples are deterministic arithmetic tests, not
original Win16 gameplay traces.

**Correct global REP status remains unchanged:**
48 direct/fixed/conditional bounded + 1 symbolic LocalAlloc +
34 unresolved = 83 archived Ghidra-listed REP instructions.
Both generic memcpy REP instructions 1008:6CA0 and 1008:6CA4
remain OPEN for complete all-callers pointer/capacity/alias safety.

## Next static proof requirements

1. Recover constructors and invariants of three-word dynamic
   string objects: pointer [object+0], used [object+2],
   capacity [object+4]. Prove each legitimate caller's
   maximum 16-bit length before signed operations.
2. Trace all buffer writers and free/realloc ownership transitions;
   distinguish valid initial states from corrupted/uninitialized ones.
3. Exclude computed FAR caller edges and indirect writes to
   DS:46B2 only after a complete static provenance review.
4. Continue the other 32 unresolved REP instructions and all
   non-REP indexed writers. Runtime only for genuinely
   statically unresolvable reachability.

No overall Nitemare 3-D 1:1 behavior/timing/pixel parity
percentage increase is asserted.
