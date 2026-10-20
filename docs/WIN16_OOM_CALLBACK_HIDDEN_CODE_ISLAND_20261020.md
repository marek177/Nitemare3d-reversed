# Nitemare 3-D Win16 1.10 — hidden OOM callback static proof

**Audit:** 20 October 2026. **Evidence:** archived original Win16 v1.10 Ghidra ASM
from nite3w(1).docx. Strictly static; no fresh original binary SHA-256
recheck and no Windows 3.11 runtime execution.

## Discovered hidden executable code island

Ghidra treats eight original bytes at 1000:076A..0771 as undecoded data.
Those exact bytes nevertheless encode an unambiguous x86-16 routine:

    1000:076A  9A 64 45 00 10   CALL FAR 1000:4564
    1000:076F  33 C0            XOR AX,AX
    1000:0771  CB               RETF

This routine **returns AX=0 if the error handler at 1000:4564 returns**.
That is an instruction-exact conditional statement, not proof that the
original handler routinely returns; 1000:4564 invokes 1000:4492, which
can issue KERNEL.THROW at 1000:451E.

The adjacent original byte island at 1000:0772..0788 contains:

    1000:0772  CALL FAR 1000:53CA (_AFX_VERSION)
    1000:0777  PUSH 1000h
    1000:077A  PUSH 076Ah
    1000:077D  CALL FAR 1008:601A (OOM pointer setter)
    1000:0782  ADD SP,4
    1000:0785  MOV AX,1
    1000:0788  RETF

The argument words register a FAR code pointer 1000:076A as OOM handler.
**One source-byte limitation is explicitly preserved:** archived Ghidra
shows the first four bytes (9A 1A 60 08) of the five-byte FAR call at
1000:077D, but not the fifth relocated segment word byte at 1000:0781.
Our optional byte verifier masks only 0781 and verifies all other
recorded original instruction bytes. It does not invent the unrecorded byte.
Startup reachability of this unnamed registrar is also NOT yet closed.

## Global callback pointer and five direct writers

The original DGROUP image initializes:

    DS:094A = 0000h   OOM callback offset
    DS:094C = 0000h   OOM callback segment

1008:5FF0 saves and replaces the 32-bit far pointer using direct
writes at 1008:6009 (offset word) and 1008:600C (segment word).
The forwarding wrapper 1008:601A has five Ghidra-named direct callers:

| Setter call site | Value installed | Local reason |
|---|---|---|
| 1000:077D | 1000:076A | Default error handler, conditional on registrar running |
| 1000:28DE | 0000:0000 | Temporarily disable OOM callback |
| 1000:2913 | previous pointer | Restore after temporary disable |
| 1000:29BB | 1008:12D2 | Temporarily install recovery callback |
| 1000:29EB | previous pointer | Restore after recovery |

This is the direct caller and direct DGROUP writer inventory only.
Computed, aliased pointer writes and complete initialization reachability
are still OPEN.

## LocalAlloc failure/retry semantics

Original allocator wrapper 1008:5AB0:

    1008:5AD3 CALL FAR KERNEL.LOCALALLOC
    1008:5AD8 MOV [BP-4],AX
    1008:5AE4 CMP [BP-4],0
    1008:5AE8 JNZ 5B01                ; successful allocation
    1008:5AEA MOV AX,DS:[094C]
    1008:5AED OR AX,DS:[094A]
    1008:5AF1 JE 5B01                 ; no installed handler
    1008:5AF3 PUSH allocation_bytes
    1008:5AF6 CALL FAR [DS:094A]      ; callback through stored pointer
    1008:5AFD OR AX,AX
    1008:5AFF JNZ 5AC3                ; nonzero callback AX => retry
    1008:5B01 MOV AX,[BP-4]           ; return last LocalAlloc result

Thus a failed LocalAlloc can propagate AX=0 when there is no callback,
or when an installed callback returns AX=0. The default hidden code
returns AX=0 only if its error helper returns. If KERNEL.THROW
transfers control, the wrapper may not return to its caller.

## Recovery handler 1008:12D2

A distinct handler reads the app object DS:081C and backing pointer
object+7A. If either is absent, it calls 1000:4564 and sets AX=0 if that
helper returns. Otherwise it checks the backing LocalSize and frees or
shrinks that allocation, then executes MOV AX,1 at 1008:1329.
The caller at 1008:5AFF retries LocalAlloc when this result is nonzero.
The recovery code does not locally prove the next allocation succeeds;
in particular not every realloc result is checked before AX=1.

## Interaction with original string-trio global writes

Earlier original ASM statically proved that 1000:0D3E calls the LocalAlloc
wrapper with (n+1) modulo 65536 and at 1000:0D65 writes NUL into DS:[BX+n]
without checking returned BX. Thus if BX=0 reaches that instruction:

| Requested used n | Possible destination of NUL byte |
|---|---|
| 00A2h (162) | DS:00A2 one-shot initialization latch |
| 46B2h (18098) | DS:46B2 multimedia clock mode flag |

This is a conditional computed-address write, not observed OOM or
a demonstrated gameplay bug. The newly decoded callback may throw
before 0D65, so callback returns cannot be presumed. Independently,
the signed JGE branch at 1000:0E33 can bypass allocation for n>=8000h
when capacity=0, then copy from sentinel DS:0584 across DS:46B2.
Actual source-length reachability remains OPEN.

## Artifacts and evidence grades

- Static executable-code-island checker:
  tools/n3d_win16_oom_callback_indirect_proof.py
- Synthetic regression tests:
  tests/test_n3d_win16_oom_callback_indirect_proof.py
- Existing trio/OOM state model:
  tools/n3d_win16_string_trio_lifecycle_audit.py
- Prior original ASM note:
  docs/WIN16_STRING_TRIO_OOM_SCALAR_ALIAS_20261020.md
- GitHub Actions:
  .github/workflows/win16-timer-ne-proof.yml

The checker may optionally accept --original with the exact SHA-pinned
v1.10 game EXE or supported source ZIP and verify original known byte
anchors. CI does not distribute or run original game executables.
The only masked original byte is 1000:0781.

**New static closure:** code at 1000:076A, its pointer-registration
mechanism, five named setters and callback retry conditions.

**Still OPEN:** whether registrar 1000:0772 is normally executed,
historical KERNEL.THROW return behavior, indirect setter targets,
actual OOM and large-length input reachability, complete source-pointer
invariants and Win16 timing/pixel parity.

No overall 1:1 behavior/timing/rendering parity percentage increase
is asserted.
