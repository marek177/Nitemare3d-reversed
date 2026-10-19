# Nitemare 3D RE MAX v0.70 — 12-build static LUT/CFG/Object+18 closure

**Date:** 19 October 2026  
**Evidence:** SHA-gated original static analysis only; no gameplay execution in this pass.

## DOS formatter state machine

Across all seven audited DOS builds, the formatter lookup table is the same 89-byte logical LUT after version-specific relocation.

The two-level lookup is locally closed:

```
index = inputByte - 0x20
kind = index <= 0x58 ? (lut[index] & 0x0F) : 0
secondIndex = (kind << 3) + state
nextState = lut[secondIndex] >> 4
```

Exhaustive evaluation of all 256 input bytes × 8 prior states in all seven DOS builds gives 14,336 transitions and zero out-of-range next states. All eight states 0..7 are reachable in the local model.

This closes the old question whether the second XLAT could index nonexistent dispatcher states 8..15.

## DOS1.9 packed/unpacked provenance correction

The packed and true unpacked DOS1.9 load images first diverge at image offset 0x15BC3. Linear CALL/JMP addresses beyond this boundary from the packed representation must not be treated as executable addresses in the real unpacked image.

The corrected unpacked DOS1.9 linear scan contains 75 indirect-call/jump candidates rather than 77. The previously catalogued 23 near jump tables / 408 table words are all before the divergence and remain byte-identical in the real unpacked image.

## OBJECT+0x18 cross-build anchors

Twelve SHA-pinned builds (7 DOS + 5 Win16) all contain the exact local writer/reader opcode family for the OBJECT +0x18 projection/depth field.

This provides stable cross-build anchors for the local projection-depth→damage path, but it is **not** a proof that these are the only global writers. Alias pointers, bulk LOAD/copy, heap aliases, cull races and full last-writer reachability remain open.

## Remaining static frontier

- recursive code/data-aware CFG on the true unpacked images;
- complete indirect FF/2,/3,/4,/5 and callback census;
- transitive OBJECT+18 alias/writer graph;
- legal accepted-hit reachability;
- E1M9 timing and DEMO/RNG orchestration.

No runtime or whole-project parity percentage is raised by this static closure.
