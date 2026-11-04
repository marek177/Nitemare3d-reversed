# Nitemare 3D — PASS 024: DOS 2.0 FAR 1277:0188 callsite inventory and score bounds

Date: 2026-11-05

## Inputs and provenance
Examined synthetic relocated DOS 2.0 expanded image, 171360 bytes, SHA-256 `ad4f4c3104475118c8c318bcb6df8748d3b8736476d90bd36c9b4a2225341d38`. This image was reconstructed statically in PASS018 from original packed DOS v2.0 EXE. This pass did **not** independently run the original packer's CPU instructions or DOSBox-X gameplay.

## Byte-match audit
Exact sequence `9A 88 01 77 12` (`CALL FAR 1277:0188` at synthetic 0x1000 base) occurs **70 times** in the expanded image. All **70** occurrences are immediately followed by `83 C4 02` (`ADD SP,2`).

A local byte-precursor classification (not whole caller stack analysis):
- **36** sites preceded by `6A xx` (PUSH imm8, sign extended to a word);
- **32** sites preceded by `66 68 xx xx xx xx` (PUSH imm32, pushes a dword);
- **2** sites preceded by `50` (PUSH AX).

Important: the PUSH imm32 sites can have a multiword argument context; the post-call cleanup of 2 bytes must not be misread as a complete function-call stack convention. Also, raw opcode matches require recursive CFG validation before counting confirmed call edges.

## 16-bit score and best-index invariant
Previous PASS023 decoded the candidate color-distance function with 16 reference colors, 256 palette-like source triples, a signed 16-bit minimum and three word-sized squared differences. If (and only if) all three source components lie in **[0,63]**, their differences against the reference components in [0,63] have magnitudes <=63. Thus the three-square sum is at most 3*63^2 = **11907**, below signed 16-bit maximum 32767. Under this assumption:
- no signed-cost overflow occurs;
- first scan candidate strictly beats initial best_score 32767;
- best_index is assigned before use.
This is a conditional mathematical bound, **not** proof that the original palette values obey the assumed range.

A model-only example outside the assumed domain: triple (255,255,255) vs (0,0,0) gives modular cost 64003 = signed -1533. A wide-integer rewrite would yield 195075 and change ranking.

## Verification status
- Exact raw byte matches: 70.
- Calls confirmed globally CFG-reachable: **0 newly**.
- Whole-program callgraph: incomplete; origins of palette triplets not yet proven.
- DOS1.0–1.9 cross-version function disassembly: not performed in this pass.
- New original runtime tests: 0.
- Historical Ghidra overlap pairs globally closed: 0/19.
- No new function marked fully complete.

The downloadable conversation artifact `N3D_FUNCTION_RESEARCH_PASS024.zip` includes `PASS024_CALLSITE_CANDIDATES.csv`, `PASS024_CALLSITE_ANCHORS.asm`, `PASS024_SUMMARY.json`, `PASS024_REPORT.md`, and reproducer `pass024_build.py`. Do not publish original proprietary binaries to GitHub.
