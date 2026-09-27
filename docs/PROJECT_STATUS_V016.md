# Nitemare3D-Reversed v0.16 — cross-version function coverage

Date: 2026-09-27

## Purpose

v0.16 makes the existing function-audit counts machine-readable and testable.

This release does **not** claim that 82.7% of DOS or 96.1% of Win16 behavior is understood. Those numbers describe support for **function identity across versions**, not semantic reconstruction completeness.

## Audited definition counts

| Platform | Primary audited version | Function definitions | Exact/strong cross-version matches | Weak/manual review |
|---|---|---:|---:|---:|
| DOS | 2.0 | 519 | 429 | 90 |
| Win16 | 1.10 | 967 | 929 | 38 |
| **Total** | — | **1486** | **1358** | **128** |

Derived identity-match ratios:

- DOS: 429 / 519 = about 82.7%
- Win16: 929 / 967 = about 96.1%

Again, these are **matching/identity ratios only**.

## Why this matters

Before v0.16, these counts existed only in prose reports. The new
`src/re/N3DV016Coverage.hpp` makes them available to code and tests so future analysis can update them without silently changing project-wide status claims.

## Current high-priority manual-review families

The existing audits still flag several areas for split/merge or weak-match review:

- DOS main/update region around `1000:70D6`;
- DOS level-load region around `1000:84FE`;
- DOS GUARD runtime around `1000:8590` and related overlapping state-machine groups;
- DOS wall-render region around `1000:86DC`;
- DOS combat clusters with split/merge warnings;
- large 2000-segment blocks that may mix code/data or multiple logical routines;
- Win16 weak/changed functions, short thunks and MFC/runtime wrappers.

## Rules for future updates

1. Keep **function identity** separate from **semantic understanding**.
2. Do not convert match ratios into project-completion percentages.
3. When a weak match is resolved, record the evidence used:
   body shape, callers/callees, constants, data stride, XREFs or behavior.
4. Track split/merge corrections explicitly.
5. Update both the audit document and the compile-time coverage constants together.

## v0.16 code

- `src/re/N3DV016Coverage.hpp`
- `tests/v016_coverage_test.cpp`
- CMake target: `n3d_v016_coverage_test`
