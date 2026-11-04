# Nitemare 3D — PASS 020: direct incoming target candidate audit

Date: 2026-11-05

## Direct source and method
Read the already reconstructed DOS 2.0 expanded load image at synthetic load base 0x1000 (171360 bytes), SHA-256 `ad4f4c3104475118c8c318bcb6df8748d3b8736476d90bd36c9b4a2225341d38`. Re-read 19 deduplicated overlap records from the existing PASS019 data, 17 using the previously proposed Ghidra-to-image mapping and two still unresolved.

A newly executed scanner examined **every byte offset** for x86/i8086 direct relative transfer patterns (short Jcc, LOOP, JCXZ, near CALL/JMP, short JMP). It calculated signed rel8/rel16 targets with 16-bit IP wrap and retained only candidates to mapped overlap endpoints. These are *candidate opcode patterns*, not recursively decoded/validated instruction starts. Segment boundaries and far target aliases need additional verification.

**7 raw candidates** were found:

| Source image offset | Opcode bytes | Candidate target |
|---|---|---|
| 0xFFE4 | EB 20 | 0x0006 (IP wrap; requires segment context) |
| 0x0022 | 7F 04 | 0x0028 |
| 0x1336 | 7E 41 | 0x1379 |
| 0x5B48 | 76 06 | 0x5B50 |
| 0x8DF0 | 77 12 | 0x8E04 |
| 0x8DF5 | EB 0D | 0x8E04 |
| 0xE3F6 | 76 06 | 0xE3FE |

Target-specific raw-pattern counts: `0x8E01=0`, `0x8E04=2`, `0x8E06=0`, `0x26F8=0`, `0x26F9=0`. Zero candidates is *not* proof of unreachability.

## Locally anchored disassembly
A second GNU objdump-i8086 pass was performed over `0x8DE5..0x8E15` and `0x26F4..0x2704`, both anchored to previously independently checked instruction starts. This reconfirms the two direct relative branches to `0x8E04` and the exact byte-boundary distinction at `0x26F8/0x26F9`. The second fixed-length window ends with a truncated opcode at `0x2702`; do not treat that last partial output as a completed instruction.

## Scope and limits
- This is an *unaligned byte-pattern search*, not global CFG or callgraph reconstruction.
- It omits indirect/FAR memory transfer resolution and prefixes, and cannot close all alternate entry points.
- Some raw candidates may lie in operands/data/unreachable regions.
- All 19 conflicts remain globally unresolved; no runtime tests were performed.
- Cumulative conversation artifact: `N3D_FUNCTION_RESEARCH_PASS020.zip`, including `PASS020_RAW_DIRECT_TARGET_CANDIDATES.csv`, `PASS020_ANCHORED_ASM.csv`, `PASS020_SUMMARY.json`, `PASS020_REPORT.md`, and `pass020_build.py`.

**Next P0:** recursive, segment-aware decoding from confirmed entrypoints and incoming edge provenance, including indirect jump tables, then per-function boundary reviews.
