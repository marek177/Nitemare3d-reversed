# Nitemare 3D — PASS 029: signed parser/index conditional tests

Date: 2026-11-05

## Source and scope
Reused the statically reconstructed DOS2 expanded synthetic base-0x1000 image, SHA-256 `ad4f4c3104475118c8c318bcb6df8748d3b8736476d90bd36c9b4a2225341d38`. Verified 16 instruction byte anchors at parser sign handling, conditional 16-bit storage, signed upper-bound guards and subsequent byte-sized color lookup. The image is **not yet independently checked by executing the original loader**.

## Machine-backed logic
- `0x12FA9` compares current input to minus sign; `0x12FAE` increments a negative flag.
- `0x1318A`, `0x1318E`, `0x13193` perform paired WORD negation with carry; `0x131E0` can store low WORD via ES:[BX] subject to scanner control flow.
- Callers `0xE3EE/0xE3F2` and `0xE42A/0xE42E` apply signed `JLE 15`, without a local nonnegative guard; `0xE405` and `0xE43F` load low BYTE into AL for FAR function `1277:0188`.

## Conditional arithmetic tests (not original CPU runtime)
A 16-entry logical mapping is indexed by the low byte of the result. Assuming successful numeric parse of a given signed word, `-1` passes signed `<=15` but indexes `255`, `-16` indexes `240`, while `-256` indexes `0`. Among 16 modeled input values, 4 pass the signed guard yet have low-byte indices outside `[0,15]`. The result is a **conditional index-domain mismatch**, not proof of out-of-bounds physical memory access or runtime input reachability. Full scanner success, error/abort behavior, DS/ES runtime context and original emulator execution remain unverified.

## Produced evidence
`N3D_FUNCTION_RESEARCH_PASS029.zip` (685 files, verified ZIP) includes `PASS029_MACHINE_ANCHORS.csv`, `PASS029_CONDITIONAL_TEST_VECTORS.csv`, three local i8086 disassemblies, `PASS029_SUMMARY.json`, `PASS029_REPORT.md`, and `build_pass029.py` plus cumulative earlier reports. Original copyrighted executables are not published to GitHub.

New original runtime tests: **0**. Globally closed historical overlap conflicts: **0/19**. New fully verified function reports: **0**.