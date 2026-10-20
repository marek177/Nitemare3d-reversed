# Nitemare 3-D Win16 v1.10 — buffer trio and two conditional global-writer paths

**Audit:** 20 October 2026. **Method:** original-static RE, from the user's
archived original Win16 v1.10 Ghidra listing nite3w(1).docx, not a fresh
EXE SHA-256 recheck or authentic Windows 3.11 runtime trace.
All Python/C++ contract code plans address effects without accessing host memory.
Overall 1:1 gameplay, timing and pixel parity remains unmeasured.

## 1. Original six-byte string buffer

The original FUN_1000_0CDC contains:

    1000:0CDF MOV BX,[BP+6]
    1000:0CE2 XOR AX,AX
    1000:0CE4 MOV [BX+4],AX         ; capacity=0
    1000:0CE7 MOV [BX+2],AX         ; used=0
    1000:0CEA MOV WORD [BX],0584h  ; shared empty pointer

The original DGROUP image has a zero byte at DS:0584.
The normal canonical empty state is therefore:

| Field | Offset | Original empty value |
|---|---:|---|
| ptr | +0 | 0584h (NOT nullptr) |
| used | +2 | 0 |
| capacity | +4 | 0 |

The free helper FUN_1000_0CF2 compares a pointer against 0584h at
1000:0CF8 and skips the free if equal. FUN_1000_0D74 frees (unless
sentinel), then resets the triple through 0CDC.

When FUN_1000_0D3E receives a nonzero requested length n:

    1000:0D43 MOV DI,[BP+8]          ; n
    1000:0D46 OR DI,DI
    1000:0D48 JNZ 0D54
    1000:0D4D CALL FAR 1000:0CDC    ; n=0: reset (NO free)
    1000:0D57 LEA AX,[DI+1]         ; uint16(n+1)
    1000:0D5B CALL FAR 1008:5FE0    ; Win16 LocalAlloc wrapper
    1000:0D61 MOV BX,AX             ; returned heap pointer
    1000:0D63 MOV [SI],AX           ; ptr=AX
    1000:0D65 MOV BYTE [BX+DI],0    ; terminator, NO null guard
    1000:0D68 MOV [SI+2],DI         ; used=n
    1000:0D6B MOV [SI+4],DI         ; capacity=n

Under valid returned LocalAlloc ownership, this requests n+1 bytes
and sets (heap_ptr,n,n). The 16-bit n+1 request can wrap to zero;
the underlying FUN_1008_5AB0 wrapper replaces a zero request by
one byte (1008:5AB8..5ABE). The n=0 branch overwrites the state
with the sentinel without first releasing a previous owning pointer;
a leak requires further interprocedural reachability evidence.

The LocalAlloc wrapper calls KERNEL.LOCALALLOC at 1008:5AD3.
On a zero return it may invoke an OOM callback through the
far pointer DS:094A/094C at 1008:5AF6 and retry if the
callback asks. If no callback exists, or retry is declined,
AX=0 can reach its return at 1008:5B01.

## 2. Conditional global write when LocalAlloc fails

The terminator instruction at 1000:0D65 has no null check.
On returned AX=0, BX=0 and the store is to DS:[DI]=0.

| Requested n | LocalAlloc requested | Failed BX | Byte written |
|---|---:|---:|---|
| 00A2h (162 decimal) | 163 | 0 | DS:00A2=00h (initialization latch) |
| 46B2h (18098 decimal) | 18099 | 0 | DS:46B2=00h (timer backend flag) |

Both n values are below signed 8000h, so a normal canonical
empty object in FUN_1000_0E26 first takes its reallocation
branch, if the appropriate parameter is supplied.

**This is a conditional computed-address scalar writer, not
an observed OOM or normal gameplay memory corruption.**
Failure of LocalAlloc and the exact caller n still require
proof; neither is established as a real run. A direct Ghidra
reference census sees constant-address MOV instructions but
can miss this register-indexed store.

## 3. More important: signed JGE can skip allocation from valid empty state

FUN_1000_0E26 has the following original local path:

    1000:0E2A MOV SI,[BP+0Ah]       ; uint16 requested copy n
    1000:0E2D MOV BX,[BP+6]         ; object
    1000:0E30 CMP WORD [BX+4],SI   ; capacity vs requested n
    1000:0E33 JGE 0E44            ; SIGNED comparison!
    1000:0E36 CALL FAR 1000:0D74  ; free/reset if capacity small
    1000:0E3F CALL FAR 1000:0D3E  ; then allocate n
    1000:0E44 OR SI,SI
    1000:0E46 JZ 0E59
    1000:0E51 CALL FAR 1008:6C80  ; memcpy n to [object+0]
    1000:0E5C MOV [BX+2],SI       ; used=n
    1000:0E61 MOV BYTE [BX+SI],0  ; terminal NUL

From the original canonical empty state capacity=0, ptr=0584h.
For request n=8000h (32768), the signed value is -32768,
and signed 0 >= -32768 is true. Therefore JGE SKIPS the
needed allocation. The next copy uses original ptr DS:0584
and writes exactly 32768 bytes there on a nonfaulting path:

    first written byte         DS:0584
    copied byte count          8000h
    last written byte          DS:8583
    copied flag within range   DS:46B2 (offset 412Eh)
    next terminator offset     DS:8584

The original Win16 v1.10 file-backed DGROUP NE segment 10 is
0x8EAE bytes long, so both DS:8583 and DS:8584 fit inside
its file-backed region. This particular conditional example
does NOT require a 16-bit address wrap or allocator failure.

A caller able to supply 32768 readable source bytes, and the
absence of fault or interfering pointer/segment corruption,
remain **UNPROVEN**. No authentic 1:1 runtime reproduction
of this scenario has been performed.

The branch effect holds for all unsigned n>=8000h when
interpreted as a signed request, although larger values
may introduce separate 16-bit address wrap/segment faults.
The least boundary case n=8000h is therefore the cleanest
local conditional witness.

## 4. Evidence boundary and regression

Original-static and safe address models:
- tools/n3d_win16_string_trio_lifecycle_audit.py
- src/re/Win16StringTrioContract.hpp

Tests:
- tests/test_n3d_win16_string_trio_lifecycle_audit.py
- tests/win16_string_trio_contract_test.cpp

GitHub Actions:
- .github/workflows/win16-timer-ne-proof.yml
- .github/workflows/win16-clock-presentation-static.yml

The synthetic regression covers all 65536 unsigned 16-bit
lengths, original empty sentinel and normal success state,
the special allocator size-0->1 substitution, both failed
allocation global targets, signed JGE growth rejection and
the nonwrapping 8000h copy interval that includes DS:46B2.

Proof grades:

| Claim | Status |
|---|---|
| Shared empty pointer and initial fields | CLOSED, original archived ASM and DGROUP |
| Null result not checked before original terminator write | CLOSED locally |
| Failure n=00A2h or 46B2h targets corresponding DS global | CLOSED conditionally |
| Signed 0E33 skips growth at n=8000h from canonical empty state | CLOSED locally |
| 8000h-byte copy from 0584h would include flag 46B2h | CLOSED address arithmetic |
| Input 8000h actually reaches original game path | OPEN |
| Historical OOM returns zero for target n in a real run | OPEN |
| Global computed/aliased writer and dynamic FAR graph | OPEN |
| Fresh original Win16 1.10 whole-file SHA check | NOT PERFORMED |
| Runtime / pixel / timing parity | NOT ESTABLISHED |

## 5. Next proof obligations

First statically audit all named direct callers of FUN_1000_0E26:
1000:0E7B, 1000:0EAB and 1000:3275.
Identify precise n bounds from their source objects, strlen
or input and whether 8000h is reachable.

Then enumerate all six named callers of FUN_1000_0D3E:
1000:0DBF, 1000:0E0B, 1000:0E3F, 1000:0ECE,
1000:0F69, 1000:107C. Check whether 00A2h or 46B2h
can coincide with an exhausted LocalAlloc/retry branch.

The original OOM callback setter/writers DS:094A/094C,
other non-REP scalar alias writes, and the existing 34
unclosed REP site destinations remain outstanding.

Nothing here changes the measured percentage of full
Nitemare 3-D 1:1 behavior, timing, or rendering parity.
