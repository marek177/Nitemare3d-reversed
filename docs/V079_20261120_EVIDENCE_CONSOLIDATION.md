# v0.79 — 2026-11-20 evidence consolidation (addendum)

This is an **addendum to the historical renderer v0.79**, not a rollback of later v0.80+ research. Snapshot of available source reports and prior-session statements; no original executable, emulator, or private CPU CSV was re-executed in this commit.

## Evidence classes and bounded conclusions

| ID | Subsystem | Previously reported result | Limits / remaining proof |
| --- | --- | --- | --- |
| V079_CEDC | DOS 2.0 renderer | 1,808/1,808 CEDC signed-division outcomes, four branches: 1030 / 474 / 187 / 117; caller U pre-22CA 1,808/1,808, five complete 304-column frames linked (1,520 rows); 23 observed 22CA boundary corrections | Captured **original CPU operands** are the inputs. This is not an original-vs-remake full-frame claim. |
| NONCODE_20261119 | DOS 2.0 NON-CODE | Follow-up reported 57,206/57,295 B classified, with 15 UNKNOWN spans totaling 89 B (99.84% classified) | Deep-verified increase reported as **0 B**. Exact spans and current canonical file hashes are required to promote any byte. This is not 99.84% deep semantics. |
| SPRITE_20261119 | Renderer | Prior session reported 11 bounded sprite renders across three episodes, each matching 64,000 indexed pixels against its comparator | Confirm comparator source, frame data and independent replay; do not infer whole-engine or all-build parity. |
| MENU_20261119 | Hardware menu | Prior session reports Music ID 13 / -60, Sound FX ID 12 / +70, Mouse +50, Joystick -50 | Requires original opcode/trace mapping for all menu flows and persistence boundaries. |
| SAVE_20261119 | SAVE/LOAD | Prior session accounts for five changed bytes in one SAVE overwrite comparison; 32-bit time values 8601 and 8403 observed | Timer epoch unknown. First post-LOAD frame, short I/O, rollback, and full save-field provenance remain open. |
| GUARD_RENDER_20261104 | Renderer/guard state | Original machine-code report links 130E:0650 and 130E:0655 to indexed GUARD[25] fields +02/+04, record stride 0x1A; prior trace records 1→2→3 for +02 | Demonstrates targeted writer; does not establish complete guard lifecycle or prove a general out-of-bounds bug. |

## Exact original DOS2 renderer v0.79 anchors

- Original unpacked DOS2 EXE historical SHA-256: `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.
- Canonical v0.79 report: [CEDC perspective-U evidence](V079_DOS20_CEDC_PERSPECTIVE_RUNTIME_SK.md).
- Native algorithm model: [CEDC projection header](../src/re/N3DDos20CedcProjection.hpp).
- Verification tool: [n3d_v079_cedc_verify.py](../tools/n3d_v079_cedc_verify.py).
- Independent early-November writer evidence was located in user Library as `N3D_DOS20_P0_RendererWritesGuard_Reconciliation_2026-11-04.md`, not revalidated against raw archive in this update.
- The November NON-CODE, sprite, menu, and SAVE items are **reported observations pending imported evidence bundles**; until matching traces/bytes are committed, no automatic promotion to DEEP_VERIFIED is justified.

## Explicit unresolved acceptance gates

1. For each NON-CODE gap: original canonical image SHA-256, exact half-open byte interval, raw bytes, ownership (code/data/padding), XREF and dataflow proof, non-overlapping interval check.
2. For renderer: original and remake start in identical state, input/tick synchronization, 64,000 indexed framebuffer bytes and 768 DAC component comparisons for every accepted frame, plus divergence localization.
3. For SAVE/LOAD: original save-byte witness, exact writer and read-back offsets, rollback on short read/write and first scheduler/render frame after LOAD.
4. For GUARD: track all aliases, object/renderer writers, independent state transitions and post-load reconstruction.
5. For Win16: maintain build-specific offsets and asset hashes. DOS2 conclusions are not promoted across versions without proof.

## Repository integration

The companion [machine-readable v0.79 addendum](../research/v079_20261120_evidence.json) deliberately stores the evidence class and open blocker for each claim. The [validator](../tools/n3d_v079_addendum_audit.py) checks schema, duplicate identifiers, bounds, counts and file links **without claiming to validate original CPU behavior**.

Existing v0.79 renderer code and tests are preserved unchanged. Game assets and private trace CSV files are not copied into this public repository.
