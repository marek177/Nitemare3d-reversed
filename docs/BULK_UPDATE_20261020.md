# v0.78 bulk integration — 20 October 2026

This release combines bounded MAP→VEC construction, the existing pool/geometry bridge, a local GUARD special-state implementation and newly supplied DOS/Win16/render reports. It does not change the active game loop to an unverified native renderer or certify complete gameplay parity.

## Before and after

| Area | Before this release | Added here | Still open |
|---|---|---|---|
| MAP→VEC | Existing pool importer/lookup needed supplied records | Four orientation passes, wall merging, centered doors, runtime property imports and primary-key grouping | Resource-bit08 remap, original full-pool bytes, external sort ties |
| Geometry | Terminal SPAN→VEC lookup→LevelState already merged in PR67 | Producer output shares the same 28-byte record contract and synthetic lookup integration | Native SPAN producer, shared cursor reentry, scheduler integration |
| GUARD state21 | Broad state graph and report evidence | Executable local conditional save/restore of +0B/+0C | Eligibility, clocks, helper5342 causality and full actor traversal |
| Static audit | Producer patch remained external | SHA-gated 59-window/10-edge auditor, portable tests and invalid/truncated CALL rejection | Direct original rerun; indirect/aliased count writers |
| DOS/Win RNG | Existing seed/LCG/countdown arithmetic | Archived Win16 EVENT before/after/timer report and arithmetic regression | Same-tick cross-build ordering and continuous RNG ledger |
| Rendering | Runnable native wall snapshot replay | Consolidated authentic IMG/shade/U/V/writer evidence | Entire synchronized wall frame, sprites/HUD, 64000 indices + 768 DAC |

## Code and bounded behavior

`Dos20VecProducer.hpp` scans 64×64 MAP cells in orientation order 0→1→2→3. It consumes explicitly supplied DOS wall-property/class, object-class and first-resource tables. DS imports read D00C/D30E/D40E; F7:0004 mappings remain caller supplied. It supports ordinary edge creation/merge and the original odd/even door orientation gate (classes31..40), then emits `vecpool::RawVec` records. Capacity is bounded at 1000 records and 333 pointers per orientation. Equal primary sort keys remain tied; external quicksort permutation is not guessed. The unsupported 106BC..106EB remap fails explicitly and does not publish a partial pool.

`Dos20GuardSpecialState.hpp` implements the local IMG6103/610C/6113 rule: when entering state21 from a nonzero state, save the old state at +0C; from zero, retain +0C. A validated return event restores +0B from +0C. Thus the source-reported actors `{state=5,saved=4}` and `{state=0,saved=4}` restore 5 and 4 respectively. The API does not infer when a hit, timer or scheduler should invoke either event. The host return guard prevents an unrelated state from being changed.

The producer static test's import path is adapted to the repository `tools/` layout. CALL helpers use explicit errors instead of Python assertions so malformed/truncated calls remain rejected under `python -O`. Private original data remains opt-in; a skipped original test is not a synthetic PASS for original evidence.

## Newly integrated source evidence

These reports were read and archived. Original EXE/DS/IMG/trace artifacts were not rerun or independently authenticated during this bulk integration; reported primary observations retain that attribution.

| Supplied evidence | Reported result | Exact limitation |
|---|---|---|
| [D02-N VEC producer](D02N_VEC_PRODUCER_STATIC_AND_CODE_20261020.md) | 59 original opcode windows,10 edges,16 door dispatch entries | Synthetic producer; 592-record original pool acceptance still open |
| [D02-N GUARD memory](evidence/2026-10-20/D02N_GUARD_MEMORY_RUNTIME_REPORT.md) | Selected CPU/R/W window1024..1110; GUARD5 saved-state mechanism; actual DEMO reset at1085 in one7000-cycles run | Earliest observed branch is window-local; helper5342/root cause and cycles-only causality not closed |
| [Win16 EVENT RNG v26](evidence/2026-10-20/V026_WIN16_EVENT_RNG_REPORT.md) | Seed1→0029E2C0,AX41,timer201 in one unchanged NITE3W process | Timer evidence uses live disassembly annotation; data-view command was mistyped; not simultaneous DOS/Win tick parity |
| [Authentic IMG wall v080](evidence/2026-10-20/V080_AUTHENTIC_IMG_WALL_REPORT.md) | Source-reported 592/592 cache selectors; U106,XLAT256/256 and42/42 pixels for one original x8 writer | Captured DS was mid-render; corrected phase334 versus331; no valid post-wall whole-frame reference |

The x8 report distinguishes original DOS2 IMG SHA `faf0cec3502d8b86ebb30a432b46b467e349864987f91a1c26358a9a5ca58cb1` from another IMG family `2d955091…60311`. Do not substitute build assets. Its 2MiB zero-diff VRAM result and 64000-byte next snapshot apply to one writer's change over supplied original background, not a complete port-rendered scene. The phase restoration is one SHA-pinned checkpoint alignment, not a constant texture-U correction.

## Validation for this integration

- Strict GCC C++20 warnings and UBSan: producer fixtures and GUARD local semantics.
- CMake Debug/CTest combined checks: producer, GUARD special state, VEC lookup, LevelState geometry, existing collision, native wall CLI, CEDC and material binding.
- Python static-auditor tests, also under optimized Python. Private original EXE test is skipped when unavailable.
- Added combined Linux/Windows CI; runtime captures are not fabricated for public CI.

Synthetic producer scenarios cover isolated walls, horizontal/vertical merge, all16 door class orientation gates, boundary neighbours, DS imports, missing resource bindings, unsupported bit08 remap,1000-record/333-pointer limits and equal-key sort behavior. GUARD scenarios cover the reported pair, unrelated-state rejection and all256 byte-valued entry states. Existing wall CLI tests retain16 patterned/mask/invalid-input scenarios.

## Next acceptance gates

Recover matching pre/post producer DS, original MAP and resource mappings; compare each original28-byte VEC in order. Close remap and sort ties before enabling general native production. Capture the helper5342 inputs at the first differing branch, preserving frame/slow clocks. Produce a true post-wall original framebuffer on the same tick before evaluating304 native wall columns, then sprites,HUD and live DAC. No global completeness percentage is assigned.

Confidence: medium for transferring supplied original-evidence claims; synthetic code behavior is directly checked in this integration. The release adds implementation and reproducible checks while leaving unmeasured reachability and timing explicitly open.
