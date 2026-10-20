# Nitemare 3-D — Win16 timer target-census and cleanup-stack provenance

**Date:** 20 October 2026. **Method:** original-static RE first. No increase in
overall 1:1 behavioral, timing or pixel parity has been claimed.

## Core discovery: two different proof scopes

A *NE-relocation-backed reference* is not automatically a call instruction.
The current target-specific scanner classifies an internal FAR reference only
as `DIRECT_FAR_CALL` when an expanded target relocation (segment-word source
type 2) has matching function offset operand and is preceded by 16-bit
opcode `9A`. Other possible classes are `DIRECT_FAR_JUMP` (opcode `EA`),
`DATA_FAR_POINTER`, `ADDRESS_TAKEN_OR_UNKNOWN`,
`OTHER_FIXUP_REFERENCE`, and a suspicious offset/relocation mismatch.

Unaligned candidate `E8` near calls are reported separately and explicitly
remain **unverified** until an original instruction boundary/CFG proves they
are actual CALL instructions. The scanner never labels a writable/dynamic
callback path impossible merely because no relocation references its target.

### Win16 1.8: actual SHA-matched original binary, *verified now*

Original file SHA-256:
`144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22`.

The public historical nite3w18.zip -> N3WUNR.EXE ZIP-SFX ->
NITE3W.EXE was statically unpacked and original SHA-256 rechecked in
[GitHub Actions run 39440663937](https://github.com/marek177/Nitemare3d-reversed/actions/runs/39440663937).

Target: `NE3:D5BE`. Results:

| Measurement | Observed |
|---|---|
| Expanded internal NE fixups to timer | 2 |
| Typed direct FAR CALL | 2 |
| Exact FAR CALL addresses | `3:0EE8`, `3:0F24` |
| Other data/address-taken fixups | 0 |
| Byte-pattern near E8 candidates | 0 |

Thus we have **all relocation-backed static references to this exact Win16
1.8 timer target**, not proof that an arbitrary computed, writable or aliased
pointer could never reach it.

### Win16 1.10: pre-existing Ghidra original ASM, target-specific proof partial

Target: `NE3:D66C`. Original archived v0.61 Ghidra listing has:

- `3:0F34`, preceded by `PUSH 0`, direct FAR initializer.
- `3:0F70`, preceded by `PUSH 1`, direct FAR cleanup.
- Function header `FUN_1010_D66C` lists exactly those **two named direct XREFs**.

The archived original ASM also establishes `3:D6BB FF 76 FE`,
`PUSH WORD PTR SS:[BP-2]` before `MMSYSTEM.606`, from a fresh
`ENTER 6,0` frame. The local read-before-write is closed.

But we have **not yet re-run a complete target-specific expanded NE fixup
census against the exact 230,400-byte SHA-pinned 1.10 executable in this
session**. Two Ghidra XREF entries are not proof of a zero address-taken
reference census or exhaustive indirect FAR closure. This is intentionally
recorded separately from the original 1.8 stronger byte-tested result.

Relevant old global Win16 v18 graph audit:
`docs/WIN16_INDIRECT_PROVENANCE_V18.md` inventoried 212 indirect sites,
78 with resolved targets and 81 dynamic virtual receiver sites. The
81 is a global *whole-executable* number, **not 81 timer candidates**.
It is not evidence of an indirect edge to timer D66C.

## New static stack provenance: prior sound cleanup shares the same BP slot

The original Win16 1.10 cleanup wrapper is:

    3:0F64  PUSH 1
    3:0F66  CALL FAR 3:E0C4       ; audio/MIDI teardown
    3:0F6B  ADD SP,2
    3:0F6E  PUSH 1
    3:0F70  CALL FAR 3:D66C       ; timer teardown
    3:0F75  ADD SP,2

The preceding `E0C4(1)` enters `ENTER 4,0`; `D66C(1)` enters
`ENTER 6,0`. Because the caller restores SP after the first call,
**both callee BP registers have the same numerical value**:

    starting caller SP = S
    caller PUSH argument -> S-2
    CALL FAR pushes CS:IP -> callee entry SP = S-6
    ENTER pushes old BP -> BP = S-8
    local [BP-2] address = S-10

The different 4-byte and 6-byte frame allocations occur *below BP*
and do not alter this correspondence.

In the observed `E0C4(mode=1)` teardown block (3:E1DC..E257), there
is **no direct store to the same local `[BP-2]`**. Therefore the
immediately preceding audio teardown does not establish a known
`timeEndPeriod` argument for D66C. This conclusion is about local
instructions; no claim is made that all nested callees or prior
unrelated stack uses are globally proven unable to mutate the slot.

Consequently, the Win16 1.10 timer cleanup argument is residual
16-bit stack content, not necessarily the period passed into
`timeBeginPeriod`, and not provably a fixed 10 ms. A portable C++ port
must not model that as an uninitialized C++ local. Keep a documented
intentional safe cleanup or a bounded emulator stack-shadow model until
runtime evidence pins an observable dependency.

The bounded integer frame/slot alias is modeled with no memory reads in
`src/re/Win16ClockPresentationContract.hpp`, with synthetic assertions in
`tests/win16_clock_presentation_contract_test.cpp`.

## New source and regression scope

- `tools/n3d_win16_timer_target_census.py` — types internal NE
  relocation references and keeps non-direct candidates visible.
- `tests/test_n3d_win16_timer_target_census.py` — synthetic fixtures
  with two FAR CALLs, FAR JMP, code address-taken pointer, data FAR
  pointer and an unaligned E8 byte candidate.
- `tools/n3d_win16_timer_binary_proof.py` — automatically adds a
  target-specific census to original SHA-gated Win16 verifications,
  requiring original 1.10 direct callers when a 1.10 image is present.
- `.github/workflows/win16-timer-ne-proof.yml` — synthetic decoder
  regression only.
- `.github/workflows/win16-original-shareware-byte-check.yml` —
  full Win16 1.8 original SHA + real target-specific fixup census.

Synthetic [CI result](https://github.com/marek177/Nitemare3d-reversed/actions/runs/39440471554);
original binary [CI result](https://github.com/marek177/Nitemare3d-reversed/actions/runs/39440663937).

## Remaining static obligations

1. Run the already written verifier against the exact original Win16 1.10
   SHA-256 `12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`.
   Preserve and inspect all expanded NE internal fixups to 3:D66C.
2. Classify any remaining address-taken FAR pointer and its writers, alias
   paths and possible indirect dispatchers, including callback tables and
   loader/Win16 MFC lifecycle entries. Only an exhaustive provenance audit
   can justify exclusion of an indirect edge.
3. Where no relocated reference exists, consider code computed offset/
   segment pointers and non-relocated same-segment dynamic invocations;
   searching two direct opcodes alone cannot disprove them.
4. Optional runtime after static exhaustion: at shutdown inspect
   SS:BP-2 immediately before `D6BB`, repeatable call context and
   `MMSYSTEM.606` result under the original Windows 3.11 environment.

**Bottom line:** two direct original timer calls and its local
read-before-write in Windows 1.10 are known. Windows 1.8's full
NE-fixup static reference census is now newly original-byte verified.
No blanket 100% Win16 indirect-call graph or timer behavior parity claim.
