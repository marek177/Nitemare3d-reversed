# Nitemare 3-D Win16 — direct clock flag overlapping-write audit

**Date:** 20 October 2026. **Scope:** Windows v1.8 original executable and
archived Windows v1.10 Ghidra disassembly. This note does NOT claim that
computed indirect/alias writers have all been ruled out.

## Why direct XREF is not enough

A direct write to `DS:46B0` might overwrite `DS:46B2` if its width were
32 bits. A direct WORD/DWORD write to `DS:46B1` could also overlap
`46B2`, as could a DWORD write starting at `DS:46AF`.
Ghidra names references by the base operand address, so counting
`DAT_1048_46B2` XREFs alone would silently miss wider neighboring
stores. Directly computed, register-indexed or ES: pointer writes also
need a separate proof.

## A. Windows v1.10 — opcode-backed direct fixed-address ledger

Source: user's archived original Ghidra disassembly
`nite3w(1).docx`; read the machine bytes and data-symbol XREFs,
NOT inferred from Win16 v1.8 displacement.

| Direct store | Exact archived opcode | Address written | Width |
|---|---|---|---|
| `3:0ECA` | `A2 A2 00` | `DS:00A2` | 1 B |
| `3:300D` | `A2 AF 46` | `DS:46AF` | 1 B |
| `3:0ED3` | `A2 B0 46` | `DS:46B0` | 1 B |
| `3:2D95` | `C6 06 B0 46 00` | `DS:46B0` | 1 B |
| `3:2EC8` | `C6 06 B0 46 01` | `DS:46B0` | 1 B |
| `3:93A4` | `C6 06 B1 46 01` | `DS:46B1` | 1 B |
| `3:93CB` | `C6 06 B1 46 01` | `DS:46B1` | 1 B |
| `3:93D2` | `C6 06 B1 46 00` | `DS:46B1` | 1 B |
| `3:0ED6` | `A2 B2 46` | `DS:46B2` | 1 B |
| `3:D691` | `A2 B2 46` | `DS:46B2` | 1 B |

**Consequence:** all seven identified neighboring direct writers are
BYTE stores and do NOT overlap `DS:46B2`. The two known direct
`DS:46B2` writers are the one-shot global initialization reset and
`timeGetDevCaps` mode selection. The lone named direct
`DS:00A2` writer is the one-shot latch reset.

This is precisely an **original Ghidra resolved direct-reference /
opcode-width census**. No standalone fixed-address references are named
at `DS:009F/00A0/00A1` in the archived Ghidra listing; however a
missing symbol XREF must not be treated as proof against overlapping
computed writes, data copying, segment aliasing or undetected code.

Machine-readable, reproducible ledger:
`other/n3d/builds_12/static_byte_evidence/N3D_Win110_timer_direct_write_witnesses_20261020.csv`.

## B. Windows v1.8 — new current-turn original executable verification

Full original Win16 v1.8 executable SHA-256:
`144e96bb649c5463d440c343ad982ed8e5f143e788c9af08bbb890fcd1b3db22`.

The current SHA-gated GitHub Actions run extracted the original executable
from public `nite3w18.zip -> N3WUNR.EXE -> NITE3W.EXE`. Then it scanned
**all four file-backed NE code segments 1,2,3,4**, searching for
selected direct-moffs, absolute-ModRM and immediate
arithmetic/logic raw-byte store patterns whose operand width could
overlap `DS:46B2` or `DS:00A2`.

Results against the exact hash-matched v1.8 bytes:

| Target | Raw store-pattern candidates | Instruction pattern |
|---|---|---|
| `DS:46B2` | `3:0E8A`, `3:D5E3` | `A2 B2 46` (MOV [46B2],AL) |
| `DS:00A2` | `3:0E7E` | `A2 A2 00` (MOV [00A2],AL) |

**No other candidates** were emitted by the implemented selected
absolute-write patterns, including the checked WORD/DWORD cases
starting before the flags. The scanner never calls raw matches
instruction-boundary validated. The three matches also have matching
archived local lifecycle context; they are not being used as proof of
all possible indirect stores.

Evidence:
[GitHub Actions original v1.8 raw-byte scan](https://github.com/marek177/Nitemare3d-reversed/actions/runs/39449309638).
A second original run asserts that these exact candidate sets remain
unchanged rather than merely printing them.

## C. Cross-version corroboration

| Direct behavior | Win16 v1.8, SHA-verified | Win16 v1.10, archived ASM | Difference |
|---|---|---|---|
| Reset one-shot latch | `3:0E7E` | `3:0ECA` | `+0x4C` |
| Reset multimedia clock flag | `3:0E8A` | `3:0ED6` | `+0x4C` |
| Write capability-success flag | `3:D5E3` | `3:D691` | `+0xAE` |

All six witnesses have original opcode `A2` (one-byte DS absolute
write). Code relocation between builds is thus consistent without
claiming whole-function machine-byte equality.

## D. Code and tests

- `tools/n3d_win16_clock_alias_writes.py`: validates source opcode
  widths and write-range intersections for all 10 original-Ghidra
  v1.10 direct store witnesses; can optionally require exact original
  1.10 SHA-256 and verify these 10 machine-code spans.
- `tests/test_n3d_win16_clock_alias_writes.py`: 12 tests, including
  intentionally overlapping synthetic WORD at `46B1` and DWORD at
  `46AF/46B0` which must trigger evidence divergence.
- `tools/n3d_win16_raw_fixed_store_candidates.py`: conservative
  original-image raw byte pattern scanner over all code NE segments.
- `tests/test_n3d_win16_raw_fixed_store_candidates.py`: 5 tests
  checking that the scanner detects overlapping BYTE/WORD/DWORD
  patterns but excludes CMP and non-overlapping neighbor BYTE writes.
- CI: `.github/workflows/win16-timer-ne-proof.yml` and
  `.github/workflows/win16-original-shareware-byte-check.yml`.

The raw pattern scan includes a bounded selection of common x86-16
absolute DS stores and arithmetic/logical read-modify-write forms.
It is **not** full 16-bit x86 instruction disassembly or validated CFG
traversal; false positive bytes remain possible in embedded data.
In particular it excludes computed SI/DI/BX/BP, ES: and string
instructions and does not prove every possible overlapping memory store
absent. Never use it to claim all original indirect accesses are closed.

## Next static proof tasks

1. Run the fresh SHA-pinned original v1.10 executable through the
   same all-NE-code-segment scanner. Verify the expected current
   `0ECA/0ED6/D691` byte witnesses and review every other hit.
2. Audit far-pointer/ES: alias roots, bulk `REP MOVS/STOS`, copied
   structures and callgraph paths that could write to `00A2` or
   `46B2` without a literal direct operand.
3. Check data-segment pointer table identities, index arithmetic,
   memory allocation/initialization aliases and Win16 MFC callbacks.
4. Only after static exhaustion: actual original Windows 3.11
   `SS:[BP-2]` at shutdown and observed MMSYSTEM.606 return/result.

**Current conclusion:** the bounded direct fixed-address write-width
closure is strong in v1.10 archived ASM and independently supported
by a SHA-pinned original v1.8 all-code raw-pattern check. Full alias
writer/indirect execution closure remains OPEN. No global 1:1
behavior/timing/pixel percentage change.
