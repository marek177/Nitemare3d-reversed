# Nitemare 3D unique-function closure v3

Date: 2026-09-30

## Scope

This pass starts from the 111 DOS records that survived v2 as possible build-exclusive/unique functions. The v3 audit adds real-mode MZ byte mapping, normalized 16-bit x86 instruction matching, positional anchors, dense unique 16-byte anchors, and exact-byte presence checks in DOS 1.7/1.8/2.0 binaries that do not yet have full C exports.

## Final v3 classification of the 111 candidates

| Class | Count | Confidence / meaning |
|---|---:|---|
| `cross-version-equivalent` | 33 | Same normalized machine routine found in another exported DOS build. |
| `present-in-other-build` | 33 | Exact byte range exists in DOS 1.7/1.8/2.0 without needing a C export. |
| `boundary-split-merge-correspondence` | 23 | Same mapped machine region exists, but decompiler function boundaries differ between builds. |
| `decompiler/internal-block-artifact` | 11 | Switch/basic-block/interior entry exported as a function-like record; not a trustworthy standalone source-function boundary. |
| `cross-version-counterpart` | 8 | Counterpart located by exact binary anchors and positional/order evidence. |
| `version-modified-counterpart` | 1 | Same anchored region/function slot, but machine code was materially modified. |
| `probable-cross-version-counterpart` | 1 | Near instruction match plus dense binary anchor evidence. |
| `decompiler-alias` | 1 | Duplicate thunk/alias of the same address. |
| unresolved | **0** | No candidate remains without a cross-build explanation. |

Confidence distribution: **82 High**, **27 Medium-High**, **2 Medium**. **29** records remain marked for manual follow-up because their exact semantic/function-boundary identity is not yet closed to High confidence.

Important: “unresolved = 0” means every one of the 111 candidates now has a concrete cross-build explanation. It does **not** prove that the entire Nitemare 3D codebase contains no version-exclusive source functions. Builds without complete decompiler exports and semantics still need full coverage.

## Key findings

- DOS MZ addresses can be bound directly to executable load-module locations for the current builds, which allows instruction-level validation instead of relying only on C decompiler text.
- DOS 1.5 `FUN_1000_82f4` ↔ DOS 1.9 `FUN_1000_84f4` has a normalized instruction match of **1.0000**.
- DOS 1.5 `FUN_1000_8386` ↔ DOS 1.9 `FUN_1000_8586` has a normalized instruction match of **1.0000**.
- DOS 1.1 `FUN_2000_6c9f` ↔ DOS 1.5 `FUN_2000_6d53` has a normalized instruction match of **1.0000**.
- DOS 1.0 `FUN_1000_0c04` maps into the corresponding DOS 1.1 machine region with instruction similarity **0.9318** and byte-sequence similarity **0.9467**, but Ghidra assigns different function boundaries.
- DOS 1.0 `FUN_1000_3dd2` maps to a DOS 1.1 region that is byte-for-byte identical over the audited interval even though it is contained inside a differently delimited function.
- DOS 1.9 `FUN_1000_fb5f` is an internal/decompiler block artifact and its exact byte block is also present in DOS 1.7, DOS 1.8 and DOS 2.0.

## Canonical map v3

V2 was too permissive for tiny identical normalized bodies. V3 uses a conservative evidence graph and only unions functions when supported by semantic hard closure, direct binary equivalence/counterpart evidence, or a true alias.

- exported bodies: **3017**
- conservative canonical families: **2957**
- multi-member families: **51**
- largest family: **4**
- explicit evidence relations: **104**

Boundary split/merge relations remain explicit relations and are not blindly forced into the same canonical ID.

## Next target

The old 111-candidate list is no longer the priority. The next phase is to obtain complete body exports for DOS 1.7/2.0 and Win16 1.3/1.6/1.8/1.10, run the same conservative relation graph over them, repair boundary artifacts, and then search for genuinely DOS-only / Win16-only functions at the machine level.
