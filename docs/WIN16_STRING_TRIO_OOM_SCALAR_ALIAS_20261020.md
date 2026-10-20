# Nitemare 3-D Win16 v1.10 — buffer trio and two conditional global-writer paths

> **20 October 2026 OOM callback CFG follow-up:** archived original
> code at **1000:076A** is a hidden, indirect-callable OOM handler,
> registered by a neighbouring 1000:0772 thunk. On entry it calls
> 1000:4564 -> 1000:4492, whose full instruction CFG has **no
> normal RETF**: it either loops among exception handlers or calls
> nonlocal Win16 KERNEL.THROW. Thus the installed default callback
> would NOT normally return AX=0 from its fallback XOR/RETF.
> The original 1008:5AB0 LocalAlloc wrapper can still return zero
> if no callback is installed or callback is temporarily disabled.
> This refines, but **does not exclude**, the conditional
> terminator write DS:[n] on 1000:0D65. Read
> [hidden callback original-byte and no-return CFG evidence](WIN16_OOM_CALLBACK_HIDDEN_CODE_ISLAND_20261020.md).
> Its ordinary registration/indirect startup reachability is OPEN.


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

## 4. First interprocedural filter: three named callers of 1000:0E26

The archived original Ghidra target XREF table for FUN_1000_0E26
lists **exactly three named direct CALL sites**:

| Original callsite | Caller | Count passed as param3 | Is count>=8000h locally excluded? |
|---|---|---|---|
| 1000:0E7B | FUN_1000_0E6A | source string-trio [source+2] used WORD; source offset [source+0] | NO; source trio writer graph needed |
| 1000:0EAB | FUN_1000_0E88 | strlen(param2) from FUN_1008_609E, or zero if input ptr is null | NO; all origin strings and maximum lengths needed |
| 1000:3275 | FUN_1000_3250 | return SI from USER.LOADSTRING of a string resource into its local buffer | **YES** under original LoadString size semantics |

At 1000:3250, the function starts with ENTER 0100h, allocating
a 256-byte local byte buffer. It calls helper FUN_1000_3282 at
1000:325D with that buffer. The helper passes an explicit
maximum output size **00FFh = 255 bytes** to USER.LOADSTRING
at 1000:3293. The returned count in AX is transferred to SI
at 1000:3262. Nonzero SI becomes the count argument of
the original 1000:3275 call to FUN_1000_0E26.

A documented LoadString buffer size restricts copied text to
fit that size (usual terminating-NUL policy); independently of
the precise off-by-one return convention, 255 is a conservative
upper bound far below 32768. Therefore the resource-loading
direct caller cannot enter the signed-negative 8000h..FFFFh
assignment case under its normal Win16 API contract.
Historic/related Microsoft LoadString API documentation:
https://techshelps.github.io/MSDN/WINBASE/devdoc/live/pdwbase/strings_6j53.htm

This is **one of three direct caller branches bounded**, not a
global exclusion of the dangerous assignment:
- 1000:0E7B copies the source object's used field and its near pointer.
  This is a circular ownership/invariant question until ALL original
  writers of that field and source aliases are enumerated.
- 1000:0EAB uses near-string strlen. The original strlen helper
  can count up to 65535 by REPNE SCASB, so its *local* behavior
  does not guarantee a count under 8000h.
- Any computed/indirect call to 1000:0E26 is still unproven absent.

Exact direct call records and source expressions:
other/n3d/builds_12/static_byte_evidence/
N3D_Win110_E26_assignment_direct_callers_20261020.csv

## 5. Evidence boundary and regression

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

## 6. Next proof obligations

The named 1000:3275 resource/LoadString input is already
bounded to 255, excluding 8000h in that direct path.
Now resolve the remaining two named direct callers of
FUN_1000_0E26: 1000:0E7B (source trio used field) and
1000:0EAB (strlen of dynamic near input string).
Determine their maximum original reachable n values.

Then enumerate all six named callers of FUN_1000_0D3E:
1000:0DBF, 1000:0E0B, 1000:0E3F, 1000:0ECE,
1000:0F69, 1000:107C. Check whether 00A2h or 46B2h
can coincide with an exhausted LocalAlloc/retry branch.

The original OOM callback setter/writers DS:094A/094C,
other non-REP scalar alias writes, and the existing 34
unclosed REP site destinations remain outstanding.

Nothing here changes the measured percentage of full
Nitemare 3-D 1:1 behavior, timing, or rendering parity.
