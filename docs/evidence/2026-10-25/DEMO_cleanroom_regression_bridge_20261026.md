# DEMO regression bridge to OpenNitemare3D (2026-10-26)

Original evidence: [RNG/DEMO to first EOF](RNG_DEMO_EOF_report.md), [original summary](RNG_DEMO_rng_run_f_summary.json), [EOF caller context](RNG_EOF_context_summary.json) and [read-only original verifier](../../../tools/verify_rng_demo_ledger.py).

## First proven implementation divergence and bounded fix

[OpenNitemare3D draft PR #1](https://github.com/marek177/OpenNitemare3D/pull/1) corrects the first publicly demonstrable implementation discrepancy: the clean-room DEMO parser interpreted each 8-byte record as 1-byte event / 2-byte input mask / padding / 4-byte counter. The hash-pinned original record and independent verifier require LE `<HHI`: 16-bit key, 16-bit flags, 32-bit counter. First original record: key `0x48E0`, flags `0x0002`, counter `8`. No asset bytes were copied.

The PR adds synthetic deterministic tests for format layout, 275 applications, 274 successful 8-byte next-prefetch reads followed by the zero-length first EOF, retained `0x74E0` key, retained `0x0090` flags and unchanged last pending record. These are regressions of an evidence-bounded local reader model, **not** proof that the clean-room engine ran an event-for-event paired original trace.

## Original-only verified checkpoints (not yet matched against remake)

- 734 original events; 229 RNG returns; 275 applied records; 0 seed setter calls, seed 1; final state `0xD0643564`; first EOF at render counter 1074.
- First 72 RNG caller/counter/result observations identical across two independent starts. The interrupted execution and completed one are not stitched.
- Original RNG recurrence: `state = low32(state * 214013 + 2531011)`, output `AX=(state >> 16) & 0x7FFF`. These computations are already checked in `verify_rng_demo_ledger.py`.
- Separate original 32-event EOF continuation reaches `06B0:039C` with restored stack, final key `0x74E0`, flags `0x0090`, unchanged pending record and unchanged game mode.
- The C++ model returns to its C++ caller only: it does not emulate the original FAR return, SP +12, BIOS queue/IRQ timing or outer game-mode decisions.

## Evidence gate still open

The private ordered original ledger, hash-matched DEMO.1 and original executable are required to compare all 275 original values/timing checkpoints and all 229 RNG calls to a live remake. The published verifier can independently recheck those private inputs but public summary totals cannot imply those pairwise matches. Do not declare 1:1 parity or invent post-EOF calls/termination.

Reproduction of C++ test: `cmake -S . -B build -DBUILD_TESTING=ON && cmake --build build && ctest --test-dir build --output-on-failure` in the OpenNitemare3D PR branch. Status: committed test, local compilation not verified here because the working container cannot resolve GitHub to clone the repository; do not treat CI as passed.
