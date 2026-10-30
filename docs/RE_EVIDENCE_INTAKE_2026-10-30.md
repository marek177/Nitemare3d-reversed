# Nitemare 3D — evidence intake (2026-10-30)

This note preserves findings reported in the ongoing DOS/Win16 reverse-engineering work. **It is not a fresh binary reanalysis or a claim of 1:1 parity.** Original traces, disassembly and executable hashes must be checked before promoting any item to verified implementation behavior.

## Reported instruction-semantics audit

- Reported audit scope: 3,922 instruction references at 3,787 unique addresses across 1,786 CFG files and 13 binary images.
- Potential decoding error: 16-bit `0x98` / `0x99` must be interpreted according to operand size (`CBW`/`CWD` in 16-bit mode; `CWDE`/`CDQ` in 32-bit mode). Do not infer mode from opcode alone.
- Reported example: `04C7:0C3F` opcode `0x99` was incorrectly labeled `CDQ` rather than `CWD`.
- Required check: inspect instruction bytes, processor context and operand-size prefixes in the original binary, then regenerate data dependencies and CFG-derived semantics.

## Reported DOS 2.0 RNG / DEMO evidence

- RNG wrapper candidate `0FBA:01A0`, with 22 reported direct call sites; indirect call sites remain to be audited.
- DEMO.1 trace reportedly observed 734 events, including 229 completed RNG calls and 275 applied DEMO inputs; the first 72 RNG observations reportedly agreed with a second, truncated run.
- First reported DEMO EOF at render counter 1074. In a follow-up empty-BIOS-queue experiment, the last key value `0x74E0` and flags `0x0090` reportedly persisted; the final loaded DEMO record reportedly remained unchanged.
- These counts are **trace-specific**, not universal game constants. Verify input archive, executable checksum, seed, event definition and trace provenance.

## Remaining reverse-engineering gates

1. Confirm function entry/exit boundaries, far calls, far returns, segment bases, relocation and overlay behavior across each DOS/Win16 version.
2. Reconcile disassembler/decompiler outputs with raw bytes; preserve unknown bytes as unknown, not executable code by assumption.
3. Recover exact projectile damage/RNG sequencing and tick-exact OBJECT scheduling.
4. Recover vector/span renderer path, indexed framebuffer, DAC timing and first-frame-after-load state.
5. Verify DEMO deterministic replay with original-vs-reconstruction traces, first-divergence reports and reproducible hashes.

## Evidence classification

`reported`: supplied by prior project notes/conversation, not independently reproduced in this commit. `verified-static`: original bytes plus control/data flow cross-checked. `verified-runtime`: controlled original executable trace. `parity`: original/reconstruction outputs match under specified test conditions. **All numerical observations above remain `reported` in this document.**

No gameplay algorithm or parity percentage is changed by this documentation-only update.
