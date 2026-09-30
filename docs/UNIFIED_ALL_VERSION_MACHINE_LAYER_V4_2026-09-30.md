# Nitemare 3D unified all-version machine layer v4

Date: 2026-09-30

## Purpose

v4 extends the full decompiler-dossier layer with machine-level function coverage for builds that do not yet have their own complete C export. It preserves provenance instead of treating inherited contracts as native decompilation.

## New machine dossier layer

- DOS 1.7: 600 instruction-boundary dossiers; 375 functions with inferred stack parameters; 829 inferred parameter slots; 2,008 direct call edges; 2,835 memory-write sites.
- DOS 2.0: 600 instruction-boundary dossiers; 376 functions with inferred stack parameters; 835 inferred parameter slots; 1,996 direct call edges; 2,819 memory-write sites.
- Win16 1.3: 957 valid machine dossiers from 959 Win16 1.0 source starts; 2 alias/interval collisions remain explicit.
- Win16 1.6: 952 valid machine dossiers; 7 source records remain open.
- Win16 1.8: 952 valid machine dossiers; 7 source records remain open.
- Win16 1.10: 948 valid machine dossiers; 11 source records remain open.

Total new machine dossier files: **5,009**.

DOS 1.8 is still represented as the exact-byte alias of the supplied DOS 1.9 binary rather than double-counting the same code.

## DOS 1.7 versus DOS 2.0

589 relations are directly compared:

- 561 normalized-identical machine bodies
- 7 very-near
- 8 modified-near
- 8 materially modified
- 5 boundary/entry mismatches

These classes are triage evidence, not semantic verdicts.

## Win16 body comparison against 1.0

| Target | Byte-identical | Normalized-identical | Very-near | Modified-near | Materially modified |
|---|---:|---:|---:|---:|---:|
| 1.3 | 560 | 353 | 16 | 15 | 13 |
| 1.6 | 311 | 579 | 19 | 21 | 22 |
| 1.8 | 311 | 577 | 19 | 21 | 24 |
| 1.10 | 149 | 711 | 25 | 33 | 30 |

The comparison intentionally does not force weak short-anchor cross-segment mappings. The Win16 source-1.0 tail region around selector 1010 offsets EBxx-EFxx remains an explicit review target in later builds.

## Parameter / local-variable evidence

DOS 1.7 and 2.0 parameters are inferred directly from BP-relative machine accesses. Width, observed signedness and comparison constraints are kept separate from guessed semantics.

Win16 1.3/1.6/1.8/1.10 parameter and local names/types are transferred from Win16 1.0 only when binary mapping establishes the counterpart. Those rows are marked as transferred evidence, not build-native decompiler truth.

## Canonical identity discipline

v4 adds relation edges for every new machine dossier but does not automatically union all of them into canonical IDs. A relation may mean “same mapped binary counterpart” without proving identical source semantics. This continues the conservative v3 rule.

## Remaining hard work

1. Parse Win16 NE relocation/fixup records so raw far-call sites become resolved cross-segment call edges.
2. Independently close the small Win16 tail-region set instead of relying on weak duplicate anchors.
3. Produce native C/decompiler exports for DOS 1.7/2.0 and Win16 1.3/1.6/1.8/1.10.
4. Review materially-modified body lists to separate gameplay changes from compiler/runtime/linker/boundary changes.
5. Promote relation edges to canonical identities only after those checks.
