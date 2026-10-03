# Nitemare 3D — unified per-function reverse-engineering project

Date: 2026-09-30
Baseline repository: `marek177/Nitemare3d-reversed` at `d2be7fb09d6b1b6e0404517b603b306c8f1096db` (v0.17).

## Goal

Create one evidence-preserving catalog for every known DOS and Win16 Nitemare 3D build. A function dossier is intended to answer, without collapsing uncertainty:

- exact decompiler signature/calling convention;
- parameter names/types and physical storage range;
- observed comparisons/masks that constrain a parameter on individual branches;
- local variables;
- direct callees and callers within the same export;
- global/pointer reads and writes;
- additions, subtractions, increments/decrements, shifts, masks, multiply/divide/modulo;
- return expressions and control/data-flow outline;
- complete decompiled body when an export exists;
- manually verified semantic name/evidence where available;
- structural equivalents across versions and conservative unique-function candidates.

## Current body-level coverage

| Platform | Version | Indexed records | Bodies | Explicit decompiler failures | Parameters present | Functions with internal callers | Functions with pointer/memory writes |
|---|---:|---:|---:|---:|---:|---:|---:|
| DOS | 1.0 | 507 | 503 | 4 | 308 | 227 | 263 |
| DOS | 1.1 | 513 | 508 | 5 | 308 | 225 | 263 |
| DOS | 1.5 | 517 | 513 | 4 | 307 | 238 | 267 |
| DOS | 1.9 | 537 | 533 | 4 | 314 | 258 | 278 |
| Win16 | 1.0 | 960 | 960 | 0 | 756 | 737 | 420 |

Total: **3,034 function records**, **3,017 exported bodies**, **17 explicit decompiler failures**.

This is body/structure coverage, not 3,017 semantically solved routines. Current semantic overlays contain **37 Confirmed**, **28 Inferred**, **1 Unknown**, and **2,968 automatic-structural-only** records.

## Parameter-range discipline

For every parameter the catalog records two separate concepts:

1. `storage_range`: the representable range implied by the decompiler type/width. Examples: `int` in these 16-bit builds is recorded as `-32768..32767`; `uint` as `0..65535`; `undefined2` as raw `0x0000..0xFFFF` with unknown signedness; pointers are recorded as addresses rather than invented numeric gameplay ranges.
2. `observed_conditions`: comparisons/masks actually seen in the function (`==`, `!=`, `<`, `>=`, switch cases, bit tests). These are branch-local evidence and are **not automatically promoted to the valid range of the whole parameter**.

That distinction avoids inventing contracts from one conditional branch.

## Cross-version matching

For the four DOS C exports currently available:

- 1,636 per-build function records have either a loose-normalized exact match or a strong SimHash structural match in another DOS version;
- 160 are weaker SimHash candidates;
- 261 are conservative `unique_candidate_same_platform` records: DOS 1.0 = 59, 1.1 = 66, 1.5 = 64, 1.9 = 72.

The 261 number is **not** a count of proven unique source functions. It is a triage list: no strong structural match was found among the currently exported DOS bodies. Compiler layout, decompiler boundaries, switch artifacts, inlining and genuine version changes must be separated manually/binary-wise.

Win16 version uniqueness is deliberately left unresolved because only Win16 1.0 currently has a C decompiler export in this dataset.

## Exact binary identities already established

The current binary manifest proves byte identity for these supplied files:

- `N3D-10-2.exe` = `N3D-10.exe` = `N3D-E-10(4).EXE` (SHA-256 `7035d185d27a4629664e9a300b77870577195205bbabcd17bbaf74a9ecf4cd04`).
- `N3D-17.exe` = `N3D-E-17(3).EXE` (SHA-256 `6abf5745d1b2862267be16395d6fd37b46c41fc3ad4248973883f5e1db8efcc2`).
- The supplied `N3D-E-18(4).EXE` = supplied `N3D-19.exe` byte-for-byte (SHA-256 `1cbb55c193b75424ee6b287f3a902a0a3c243a392d034086d040b07c99994be8`). Therefore these two exact supplied binaries cannot contain different functions; the version/distribution labels must not be mistaken for a binary-code difference.

## Binary-only builds in the current dataset

The following builds are indexed in the manifest but do not yet have their own full C body export in the unified analyzer:

- DOS 1.7;
- DOS 2.0;
- Win16 1.3;
- Win16 1.6;
- Win16 1.8;
- Win16 1.10.

The supplied DOS 1.8-labeled binary is byte-identical to the supplied DOS 1.9 binary and can reuse the exact binary/body facts for that supplied pair, subject to keeping the distribution labels distinct in provenance.

## Hard-closure evidence retained

The project imports **95 DOS cross-version closure families** from the 2026-09-29 hard-closure ledger: 85 hidden/missing families plus 10 decompiler-failure families. These records preserve mappings for DOS builds such as 1.7/1.8/2.0 even where no complete C export is available.

## Output schema

- `functions_master.csv`: one row per function record; signature, counts, semantic overlay, fingerprints, match status.
- `parameters.csv`: one row per parameter; type, bit width, signedness/storage range, observed conditions and use count.
- `call_edges.csv`: direct caller -> callee edges and counts.
- `memory_writes.csv`: extracted pointer/array write sites with expression and offset terms.
- `unique_candidates.csv`: conservative DOS uniqueness triage list.
- `function_dossiers.jsonl`: machine-readable full records including decompiled bodies.
- `dossiers/<platform_version>/<function>.md`: human-readable deep dossier for every record.
- `build_manifest.csv`: binary hashes, format, version label, exact-byte alias groups and current body coverage.
- `dos_hard_closure_families.json`: retained closure evidence.

## Evidence levels

- **Confirmed**: manual semantic overlay tied to binary/assembler or cross-build evidence.
- **Inferred**: strong but not fully closed semantic interpretation.
- **automatic-structural-only**: parser/fingerprint/call/memory facts only; no semantic name is claimed.
- **decompiler_failed**: body not trusted/available; assembler/function-boundary work is required.

## Immediate next closure order

1. Generate equivalent decompiler exports for Win16 1.3, 1.6, 1.8 and 1.10 and feed them into the same schema.
2. Generate/repair exports for DOS 1.7 and 2.0; preserve the exact-byte DOS 1.8/1.9 relationship in provenance.
3. Re-run cross-version matching across all builds, then manually inspect the 261 current uniqueness candidates before calling any function genuinely version-exclusive.
4. For high-value gameplay clusters (renderer, object, guard/AI, combat, projectile, input/use, save/load), replace generic `FUN_*` identifiers with evidence-backed canonical names and field/parameter roles.
5. Add binary-address + byte-range fingerprints so decompiler boundary drift can be distinguished from actual source-level changes.

The project deliberately does not equate “decompiled” with “understood”; the goal is a single database in which every claim can be traced back to an executable/export and its evidence level.
