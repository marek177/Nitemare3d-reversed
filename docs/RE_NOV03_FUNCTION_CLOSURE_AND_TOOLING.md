# 3 November 2026 — function-inventory closure and unknown-code audit

## Scope
This is a **tooling + research status** milestone, not a claim of newly recovered original code or a parity breakthrough. The purpose is to make future DOS/Win16 Ghidra/IDA exports auditable and to prevent candidate entries from being counted as verified functions.

## New tool
`tools/n3d_function_inventory_audit.py` reads a UTF-8 CSV with columns:

```csv
version,entry,status,evidence
DOS2.0,1234:0000,confirmed,EXE-SHA256-and-callsite-reference
DOS2.0,1234:0010,candidate,
WIN1.10,2:3994,unresolved,
```

Run:

```sh
python3 tools/n3d_function_inventory_audit.py inventory.csv --json-out function_audit.json
python3 -m unittest discover -s tests -p 'test_n3d_function_inventory_audit.py' -v
```

Exit codes: 0 clean, 1 invalid or duplicate records, 2 file/format error. The audit retains per-version candidate/unresolved/confirmed counts; duplicates are errors; a confirmed entry must have an evidence pointer. Counts describe **supplied rows**, not a provable total of functions in the program.

## Analytical frontier after 1–2 November

- Multiple DOS/Win16 versions have raw disassembly exports whose function boundaries may be missing or inferred incorrectly.
- The key outstanding task is recursive instruction reachability, segmented near/far CFG closure, alias and indirect CALL/JMP resolution and detection of data misclassified as code.
- Verify any claimed total against executable identity (hash), a specific Ghidra/IDA export, relocation base/segments and a reviewer-audited function boundary ledger.
- Keep separate counts for candidate entries, valid function starts, resolved returns, thunk/wrapper cases and unknown indirect targets. Do **not** turn the historical approximate 99% RE estimates into a measured coverage figure.

## Priorities and acceptance

1. DOS 1.1 and 1.2 exact function counts: determine and validate actual entries instead of repeating tentative 490–510 claims.
2. DOS 2.0 unknown-byte/CFG closure: resolve FAR context, data/code conflicts and indirect targets.
3. Win16 1.0/1.3/1.6/1.8/1.10: reconstruct FAR pointers with segment-aware call graphs.
4. Use bounded original runtime traces to confirm ambiguous execution paths, never substitute synthetic tests.
5. Continue full-game original-vs-remake deterministic and indexed-frame + DAC regression gates.

## Evidence classification

- `static`: authenticated executable/disassembly/offset and control-flow argument.
- `original_runtime`: captured original hardware/emulator state with reproduction details.
- `synthetic`: self-contained unit tests or generated fixtures.
- `parity`: captured, synchronized original-vs-port inputs/state/output, including first divergence.

The new audit and tests are **synthetic tooling verification only**. No original binaries are committed and no new runtime parity is claimed.

See [24 October status](RE_STATUS_AREAS_20261024_SK.md) and [research consolidation](RE_CONSOLIDATION_20261022_24_SK.md).
