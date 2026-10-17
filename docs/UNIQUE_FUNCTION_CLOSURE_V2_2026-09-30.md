# Nitemare 3D unique-function closure v2

Date: 2026-09-30

## Result

The initial 261 DOS records flagged as possible version-unique functions were re-processed with a second-stage normalized control/data-flow matcher, semantic overlays, and a boundary-overlap test.

| Closure class | Records | Meaning |
|---|---:|---|
| `semantic-equivalent-known` | 26 | Same manually recovered semantic function exists in multiple DOS versions. |
| `structural-equivalent-high` | 44 | High-confidence normalized structural equivalent found. |
| `structural-equivalent-probable` | 20 | Probable normalized structural equivalent found. |
| `review-near-match` | 29 | Promising match; requires binary/manual closure. |
| `decompiler-boundary-overlap` | 31 | Decompiler body crosses one or more other recognized function starts; uniqueness cannot be trusted until boundary repair. |
| `remaining-unique-candidate` | 111 | Still open after the current automatic and semantic closure passes. |

**Still open as genuine uniqueness candidates: 111 records** (DOS 1.0=21, 1.1=25, 1.5=29, 1.9=36).

## Boundary contamination finding

31 candidates are now separated from semantic uniqueness because their decompiled body provably spans across one or more other recognized function starts in the same DOS segment. This is a strong indication of function-boundary/decompiler contamination, not 31 newly discovered giant source functions.

Examples:

- DOS 1.0 `FUN_1000_4965`: 949 decompiled lines, forward label span 0xA1F3, overlaps 198 recognized function starts.
- DOS 1.5 `FUN_1000_4a49`: 973 decompiled lines, forward label span 0xA0BF, overlaps 193 recognized function starts.
- DOS 1.0 `FUN_1000_810c`: 2708 decompiled lines, forward label span 0x7E44, overlaps 153 recognized function starts.
- DOS 1.0 `FUN_1000_807a`: 409 decompiled lines, forward label span 0x7C12, overlaps 152 recognized function starts.
- DOS 1.0 `FUN_1000_8350`: 1318 decompiled lines, forward label span 0x793C, overlaps 147 recognized function starts.
- DOS 1.9 `FUN_1000_87ce`: 2131 decompiled lines, forward label span 0x7818, overlaps 147 recognized function starts.

## Universal provisional canonical IDs

The v2 canonical map covers **3017 exported bodies** across DOS and Win16 1.0 in **1803 provisional canonical families**.

- cross-platform provisional families: 26
- cross-version same-platform provisional families: 561
- single-build unresolved families: 1216

Cross-platform families are only automatically merged when loose-normalized bodies are exact. DOS cross-version families additionally use strong/refined structural matches and evidence-backed manual semantic names. Win16 1.3/1.6/1.8/1.10 and DOS 1.7/2.0 remain represented at build-manifest/hard-closure level until complete body exports are available.

## Next binary closure target

Work the 111 remaining candidates in priority order. For each candidate: repair/confirm exact function boundaries in the executable, extract a byte-range fingerprint, resolve direct call targets and global writers/readers, then compare the resulting normalized instruction graph against the corresponding versions. Only after that should a record be marked truly version-exclusive.
