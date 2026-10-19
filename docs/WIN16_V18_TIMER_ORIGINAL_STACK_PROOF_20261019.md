# Nitemare 3-D Windows 1.8: SHA-256-pinned timer bytecode proof

Date: 19 October 2026. Status: **ORIGINAL STATIC VERIFIED, Win16 1.8 only**.

## Origin and identity

Public historical distribution:
`https://www.classicdosgames.com/files/games/gray/nite3w18.zip`
(MD5 `2caa732f42e5b8a9ac2930008bec724e`, 1,465,344 bytes).

The distribution nests the original game executable as:

`nite3w18.zip -> N3WUNR.EXE (Win16 ZIP-SFX) -> NITE3W.EXE`

Only archive bytes were read; neither installer nor game was executed.

Inner `NITE3W.EXE`, **230,224 bytes**:
SHA-256 `144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22`.

This **exactly matches** existing Win16 1.8 build identity in
`other/n3d/builds_12/static_byte_evidence/N3D_12build_identities.csv`.
Its NE segment 3 begins at file offset 90016 and is 61301 bytes.
Five original critical time-related FAR calls independently passed
MMSYSTEM/USER imported-ordinal NE-fixup validation.

Reproducible original-byte evidence, including full timer-body disassembly:
[GitHub Actions run 39315099929](https://github.com/marek177/Nitemare3d-reversed/actions/runs/39315099929).

## Main new closure: both direct FAR caller sites

The NE internal segment-word fixups to `3:D5BE` are:

| Verified caller | Original bytes near call | Action | Caller stack cleanup |
|---|---|---|---|
| `3:0EE8` | `0EE6: 6A 00`, `0EE8: 9A BE D5 ...` | `push 0; call far 3:D5BE` | `0EED: ADD SP,2` |
| `3:0F24` | `0F22: 6A 01`, `0F24: 9A BE D5 ...` | `push 1; call far 3:D5BE` | `0F29: ADD SP,2` |

Fixup selector-word positions: `3:0EEB` and `3:0F27`.
The original function **is not a detached unused timer** simply because the
Ghidra C function export failed to name the initializer call.
These are two direct original static edges, one for initialization and
one for cleanup. Reachability of their *enclosing* lifecycle functions
is a separate question.

The raw unaligned `E8` scan found zero candidate same-segment NEAR calls
to `3:D5BE`; this does not close possible writable indirect pointers
or every dynamically computed entry.

## Exact timer routine and cleanup argument

SHA-pinned original instruction excerpt:

```asm
3:D5BE  C8 06 00 00    ENTER 6,0             ; 6 local bytes
3:D5C3  8B 46 06       MOV AX,[BP+6]         ; init(0) / close(1)
3:D5D0  8D 46 FA       LEA AX,[BP-6]         ; TIMECAPS output base
3:D5D5  6A 04          PUSH 4                 ; output size: 4 bytes
3:D5D7  9A ...         CALL FAR MMSYSTEM.604  ; timeGetDevCaps
3:D5E3  A2 B2 46       MOV [46B2],AL         ; capability-success flag
3:D5E6  8B 76 FA       MOV SI,[BP-6]         ; minimum period
3:D5F2  83 C6 0A       ADD SI,10             ; after 10ms clamp math
3:D5FC  56             PUSH SI
3:D5FD  9A ...         CALL FAR MMSYSTEM.605  ; timeBeginPeriod
3:D606  80 3E B2 46 00 CMP BYTE PTR [46B2],0
3:D60B  74 08          JE D615
3:D60D  FF 76 FE       PUSH WORD PTR [BP-2]  ; different operand from SI
3:D610  9A ...         CALL FAR MMSYSTEM.606  ; timeEndPeriod
```

**Important evidence boundary:** Each invocation allocates a *fresh* 6-byte
local frame with `ENTER 6,0`. The 4-byte `TIMECAPS` buffer begins at
`[BP-6]`, occupying `BP-6..BP-3`. The routine does not write `[BP-2]`.
The end branch reads `[BP-2]` anyway, on a *different* invocation
from the initializer. Consequently the argument to `timeEndPeriod`
is **uninitialized stack residue**, not the SI period passed to
`timeBeginPeriod`. Its actual runtime WORD value cannot be assigned
a fixed constant by static reasoning.

This is a source-logic defect / possible cleanup bug visible in the original
instructions. It does **not** prove a runtime crash, audible divergence or
timer failure. The multimedia runtime's response to the residual WORD
has not been measured.

The capability-success flag is set from the `timeGetDevCaps` result,
not from `timeBeginPeriod` return success.

## Compatibility implications

A safe modern C++ port must NOT emulate this using an uninitialized host
local: that would create undefined behavior. Preserve the original fact in a
version-scoped evidence contract and explicitly choose between:
- safe host cleanup with a saved matching `timeBeginPeriod` resolution
  (intentional compatibility deviation), or
- a bounded original-runtime stack-shadow model **only if actual historic
  behavior demands this edge case** and runtime evidence pins its semantics.

The existing `src/re/Win16ClockPresentationContract.hpp` exposes an evidence
enum only for Win16 1.8; other versions remain marked as *raw byte unverified*.

## Automated guardrails

- `tools/n3d_win16_timer_binary_proof.py` verifies the exact 1.8 original
  program SHA and all the opcode/fixup anchors before returning
  `win18_timer_stack_proof`.
- `tests/test_n3d_win16_timer_binary_proof.py` tests NE/SFX parser behavior
  on synthetic fixtures.
- `tests/win16_clock_presentation_contract_test.cpp` tests the C++ scoped
  evidence enum; no original game file is committed.
- Public reference original-byte run:
  [39315099929](https://github.com/marek177/Nitemare3d-reversed/actions/runs/39315099929).

## Still OPEN

1. Verify **Win16 1.10 `3:D66C..D6C6` from its own SHA-256-pinned original
   raw bytes**, including actual `timeEndPeriod` operand and direct/indirect
   callsites. Matching decompiled shape is not proof of raw byte equality.
2. Win16 1.3/1.6 have historic public distributions with valid checksums
   but their `N3WUNR.EXE` / `INSTALL.EXE` SFX wrappers were not parsed
   as ZIP nor by 7-Zip in the diagnostic run; no original inner EXE hash
   match was achieved in those two tests. C exports exist, but do not claim
   their timer cleanup stack operand is byte-verified.
3. Actual Windows 3.11 runtime `timeEndPeriod` argument value
   and MMSystem return path, if required for authentic timing compatibility.
4. Full aliased/indirect Win16 FAR callgraph and renderer/pixel parity.

No new global percentage of 1:1 parity is claimed.
