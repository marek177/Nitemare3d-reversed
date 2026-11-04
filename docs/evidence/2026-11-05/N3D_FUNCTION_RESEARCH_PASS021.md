# Nitemare 3D — PASS 021: anchored recursive CFG and correction of raw pattern matches

Date: 2026-11-05

## Evidence source
Reused the unpacked DOS 2.0 relocated synthetic load-base-0x1000 image, SHA256 `ad4f4c3104475118c8c318bcb6df8748d3b8736476d90bd36c9b4a2225341d38`, contained in the previous PASS020 artifact. This is a previous static-loader reconstruction, **not a fresh independently CPU-emulated image**.

Seven raw opcode-pattern candidates from PASS020 were inspected via GNU objdump i8086 at locally established instruction boundaries.

## Reclassification
- **Five interior byte patterns**, not independent branch instructions *on their locally decoded paths*:
  - `0x0022` inside `0x0020: 26 39 7F 04` (`CMP ES:[BX+4],DI`).
  - `0x1336` inside `0x1334: 3B 16 7E 41` (`CMP DX,DS:[417E]`).
  - `0x5B48` inside `0x5B46: 66 FF 76 06` (`PUSH DWORD PTR [BP+6]`).
  - `0x8DF0` inside `0x8DED: 9A 88 01 77 12` (`CALL FAR 1277:0188`).
  - `0xE3F6` inside `0xE3F4: 66 FF 76 06` (`PUSH DWORD PTR [BP+6]`).
- **One confirmed local branch**: `0x8DF5: EB 0D` (`JMP 0x8E04`).
- **One encoded branch with unresolved segment mapping**: `0xFFE4: EB 20`. A 16-bit IP-wrapping branch requires CS identity before assigning a global flat-image destination.

### Critical correction
PASS019 and PASS020 erroneously presented `0x8DF0: 77 12` as a `JA 0x8E04` instruction. Those bytes are the **segment part of the operand of the `CALL FAR` at `0x8DED`**. There is only one byte-decoded branch to `0x8E04` on the locally anchored path: `0x8DF5 JMP`. Any independent overlapping entry at `0x8DF0` would need a separate incoming-edge proof.

## Local recursive CFG traversal
Starting at `0x8DE5` and confined to the window `0x8DE5..0x8E20`, decoding successors using branch and fallthrough:
- 23 visited instruction start offsets
- 24 local taken/fallthrough edges
- Three FAR CALL instructions with unresolved callee effects at `0x8DED`, `0x8DFA` and `0x8E09`
- One fallthrough beyond the audit window
- **0/19** global overlap regions reachability-closed.

The executable expanded image is not committed. Cumulative archive `N3D_FUNCTION_RESEARCH_PASS021.zip` includes `PASS021_CANDIDATE_RECLASSIFICATION.csv`, `PASS021_LOCAL_CFG_EDGES.csv`, `PASS021_LOCAL_CFG.json`, `PASS021_ANCHORED_WINDOWS.asm`, `PASS021_SUMMARY.json`, `pass021_build.py`, and historical PASS001–020 records.

No new DOSBox-X gameplay runtime test was performed. Do not upgrade complete-function metrics from this bounded CFG.
