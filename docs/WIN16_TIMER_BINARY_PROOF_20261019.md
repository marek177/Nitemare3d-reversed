# Win16 timer byte proof: original EXE, NE fixups and precise stack arguments

Date: 2026-10-19. Scope: Nitemare 3-D Windows 1.0 / 1.3 / 1.6 / 1.8 / 1.10.
Static-first audit. This note does **not** claim new original-runtime coverage
or alter the game's main simulation or renderer.

## What is proved from existing static records

Win16 releases have two clock backends:
- MMSYSTEM ordinal 607 -> timeGetTime;
- USER ordinal 13 -> GetTickCount.

The guard byte is set by the local timeGetDevCaps success comparison, not by
the success of timeBeginPeriod; an unsuccessful timeBeginPeriod does not itself
flip the selection flag. Windows 1.10 uses DS:46B2. Refer to:
- NITE3W 1.10 Ghidra export, D66C/D6C6;
- other/n3d/builds_12/static_byte_evidence/
  N3D_Win16_reloc_anchored_import_CALLs.csv;
- docs/WIN16_CLOCK_PRESENTATION_STATIC_AUDIT_20261019.md.

| Win build | Timer init entry | timeGetDevCaps | timeBeginPeriod | timeEndPeriod | timeGetTime | GetTickCount |
|---|---|---|---|---|---|---|
| 1.0 | 3:D43E | 3:D457 | 3:D47D | 3:D490 | 3:D49F | 3:D4A6 |
| 1.3 | 3:D44A | 3:D463 | 3:D489 | 3:D49C | 3:D4AB | 3:D4B2 |
| 1.6 | 3:D5BE | 3:D5D7 | 3:D5FD | 3:D610 | 3:D61F | 3:D626 |
| 1.8 | 3:D5BE | 3:D5D7 | 3:D5FD | 3:D610 | 3:D61F | 3:D626 |
| 1.10 | 3:D66C | 3:D685 | 3:D6AB | 3:D6BE | 3:D6CD | 3:D6D4 |

Ordinals 604/605/606/607 in MMSYSTEM and 13 in USER are tied to imported
calls by NE relocation evidence. This does **not** by itself reconstruct
the instruction(s) preparing the 16-bit stack argument for timeEndPeriod.

## New original-only static verifier

File: tools/n3d_win16_timer_binary_proof.py

The script:
1. Reads a local original .EXE or .ZIP (including up to two nested ZIP levels).
2. Selects only one of five pinned Win16 SHA-256 identities from the existing
   N3D_12build_identities.csv, and checks the byte length.
3. Parses the original NE segment table with tools/ne_renderer_audit.py.
4. Verifies expected raw file offset/size of NE logical segment 3.
5. Checks all five critical FAR call opcodes and import-ordinal fixups.
6. Decodes 16-bit instructions around timer init and clock selection.
7. Emits the preceding **instructions** around timeEndPeriod so its exact pushed
   argument can be evaluated without trusting incomplete Ghidra call signatures.
8. Emits fixup-backed references and raw near-call E8 candidates, explicitly
   marking raw E8 candidates as unverified until boundaries/CFG are established.
9. Produces a local structured JSON report without embedding the original EXE.

No original Windows, Nitemare 3-D, or WinG executable is committed.

### Run on an original ZIP

With Python 3.12+ and Capstone 5 installed:

    python -m pip install capstone==5.0.9
    python tools/n3d_win16_timer_binary_proof.py \
        "/path/to/nite3w_original_v_ZIP.zip" \
        --version 1.10 \
        --output win16_timer_original_v110.json

Or with an exact original Win16 1.10 binary:

    python tools/n3d_win16_timer_binary_proof.py \
        "/path/to/nite3w.exe" --version 1.10 \
        --output win16_timer_original_v110.json

The verifier **rejects** installers, repacks, a mismatched patch and unpinned
EXEs. It requires SHA-256
12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481
for Windows 1.10 and validates segment 3 (90048 / 61372 bytes).

### How to close the precise timeEndPeriod argument

Inspect the JSON field cleanup_call_context. Confirm, using disassembled
instructions before call 3:D6BE (Windows 1.10):
- the push operands and ordering;
- the 16-bit Pascal ABI argument count;
- the value used to call timeBeginPeriod at 3:D6AB;
- the value that actually reaches timeEndPeriod at 3:D6BE;
- the branch predicate and the callee cleanup conditions.

Never fill the missing argument with "10" or the saved timer resolution by
guessing from the C decompiler. The code has not yet been run on the original
EXE in the current environment, so this proof obligation remains OPEN.

For negative reachability claims, distinguish:
- a direct E8 site confirmed on an instruction boundary;
- a raw E8 candidate (may be immediate data);
- a fixup-backed internal FAR pointer (could be a call or data pointer);
- an unresolved indirect FAR call through a writable table.

The existing missing named Ghidra call to D66C(0) is insufficient to conclude
the multimedia clock never initializes. V058-10 remains OPEN.

## Validation / acceptance

- tests/test_n3d_win16_timer_binary_proof.py constructs a synthetic NE file
  with three segments, one imported-ordinal relocation to MMSYSTEM.606 and
  one near E8 candidate. It also checks nested ZIP discovery and SHA rejection.
- .github/workflows/win16-timer-ne-proof.yml runs Python syntax checks,
  Capstone 5.0.9 disassembly, and unittest synthetic fixtures.
- GitHub Actions run 39311898231 succeeded on the initial standalone script.
- This is **synthetic parser correctness**, not proof that the original
  timeEndPeriod stack argument, NE indirect graph or gameplay timing
  is already resolved.

## Next static pass

1. Run the pinned verifier on actual Windows 1.10 EXE bytes, record the
   timeEndPeriod push and annotate 3:D6AB..D6C6.
2. Reconstruct all cross-segment and same-segment callers of 3:D66C, starting
   with NE internal-fixup-backed FAR references, then independently validated
   near E8 call boundaries and any dynamic function pointers.
3. Repeat identical byte-level check across Win16 1.0/1.3/1.6/1.8.
4. Only if static inspection leaves a genuinely environment-dependent gate,
   capture the Windows 3.11 original runtime flag DS:46B2 and both clock calls.

Relevant public technical reference: Microsoft KB Q65122, segmented NE
executable format and segment relocation records
https://jeffpar.github.io/kbarchive/kb/065/Q65122/


## Five-release clock flags and calibration gates

The intermediate 1.3 and 1.6 Ghidra exports were also inspected, rather
than extrapolating addresses from 1.0/1.8/1.10:

| Build | Clock selector byte | Timer init/cleanup | Read clock | Render calibration |
|---|---|---|---|---|
| 1.0 | DS:45F2 | 3:D43E | 3:D498 | 3:D5A2 |
| 1.3 | DS:45F2 | 3:D44A | 3:D4A4 | 3:D5AE |
| 1.6 | DS:46A2 | 3:D5BE | 3:D618 | 3:D722 |
| 1.8 | DS:46B2 | 3:D5BE | 3:D618 | 3:D722 |
| 1.10 | DS:46B2 | 3:D66C | 3:D6C6 | 3:D7D0 |

Evidence: NITE3W13.EXE(7).c, FUN_1010_D44A/D5AE; NITE3W16.EXE(5).c,
FUN_1010_D5BE/D722; earlier 1.0, 1.8, 1.10 exports plus NE relocation CSV.
In 1.3 and 1.6 the keyboard handler invokes calibration after Alt+Enter,
while the calibration callee checks screen=1, state=1, and scheduler mode
belonging to {0,1,3}. Windows 1.0 has the equivalent narrower input
condition at the keyboard *caller* with scheduler mode 0.

WinG direct blit selector in 1.3/1.6 also checks native dimensions
320x200 for WinGBitBlt and otherwise uses WinGStretchBlt; the
presentation mode IDs retain older 0/1 window sizes, 2 fullscreen,
3 restore behavior. Only Windows 1.10 introduces window selector 2
for 960x600 and shifts fullscreen/restore to selectors 3/4.

src/re/Win16ClockPresentationContract.hpp and the synthetic C++ regression
now carry the five-build flag/entry/mode matrix. All five rows have direct
decompiler evidence, but precise multimedia-timer cleanup argument and
overall original-runtime parity remain separate OPEN obligations.

## Win16 v1.8 original-byte correction (19 October, later pass)

**This explicitly supersedes older generic statements above that
`timeEndPeriod` had an unknown argument in every release.**

For the **SHA-256-matched original Windows v1.8 only**, the argument is now
instruction-exactly recovered: `3:D60D PUSH WORD PTR [BP-2]`, immediately
before `3:D610 CALL FAR MMSYSTEM.606`. In the same fresh `ENTER 6,0`
frame, the function never initializes `[BP-2]`; `timeGetDevCaps`
receives its four-byte output buffer at `[BP-6]`, outside the
cleanup operand. The argument comes from residual local stack memory.

Original NECALL callers `3:0EE8` with `PUSH 0` and `3:0F24`
with `PUSH 1` are proven by raw `9A` opcodes, exact target offsets
and internal NE fixups. The Ghidra-export absence of the init call
was an incomplete recovered-C callgraph, not a real missing caller.

Proof: [Original Win16 v1.8 CI byte check](https://github.com/marek177/Nitemare3d-reversed/actions/runs/39316588090);
[full evidence and limitations](WIN16_V18_TIMER_ORIGINAL_STACK_PROOF_20261019.md).

The **Win16 v1.10 `3:D6BE` operand** is still not byte-verified and
continues to be OPEN. The same applies to version-specific original
byte claims for the 1.0/1.3/1.6 release timer cleanup paths and full
indirect FAR callgraph. No binary or gameplay parity percentage is raised.
