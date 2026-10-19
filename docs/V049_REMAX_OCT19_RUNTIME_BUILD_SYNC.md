# Nitemare 3D RE MAX v0.49 — 19 October runtime, cross-build and buildability sync

**Date:** 19 October 2026

## Evidence boundary

This update synchronizes the strongest new evidence acquired after v0.48 and fixes three host-portability/build defects discovered by compiling the clean-room project on Linux.

Evidence classes remain separate:

- **original runtime:** instructions, memory/register writes or device events executed by an original Nitemare 3-D binary;
- **original static:** SHA-pinned binary/data analysis without claiming reachability;
- **controlled runtime:** original executable logic after explicitly documented RAM setup;
- **model/build test:** validation of the clean-room reconstruction or compiler portability; not proof that the original game behaves identically.

This release does not claim full original-vs-port, pixel, audio or timing parity.

## 1. DOS 1.2 DEMO.1 RNG #11–#17 frontier

The unchanged original DOS 1.2 executable was captured in the Advanced History v3 environment.

New bounded runtime facts:

- RNG #11 is reached from the GUARD planner for GUARD index 41. The observed transition is `DF90722B -> 1649B442`, result `5705`; the planner changes the Y vector `00 -> F8`.
- RNG #12 executes `1649B442 -> 6DF109FD`, result `28145`; the observed local consequences include timer `0 -> 9` and state `05 -> 06`.
- stack evidence ties RNG #13 and #14 to planning of GUARD 43 and GUARD 40 respectively, but the multi-million-instruction gaps are not presented as one continuous trace.
- RNG #15 executes `C1BBB05F -> A6E9C9A6`, result `9961`; the original damage path writes GUARD41 HP `111 -> 0` with returned damage `165`.
- RNG #16 executes `A6E9C9A6 -> 81EB59D1`, result `491`; its animation candidate is rejected and the original branches back to the RNG callsite.
- RNG #17 entry is observed with pre-state `81EB59D1`. The mathematically expected next state `0BB31550`, result `2995`, remains a prediction because the capture stops before executing RNG #17.

Therefore the DEMO RNG ledger has advanced beyond the v0.48 bootstrap and RNG #1–#10 evidence, but it is still not one unbroken #1→#17 CPU trace and the death/drop/score aftermath is not closed.

## 2. DOS v2.0 Advanced History E1M1 trace

A separate original DOS v2.0 E1M1 trace records:

- 3,775,835 executed instructions by runtime summary;
- 289,190 VRAM events;
- 7,315 VGA-register snapshots;
- three frame-hash events;
- 12 complete entries into the measured main update function;
- a 33-record, 26-byte-stride scheduler list dispatched 396 times.

In that measured window, state 7 dispatch occurred 372 times and state 8 occurred 24 times. The conditional tail call was taken 2 of 12 times.

Six executed VGA writer families account for all 289,190 recorded VRAM changes in the checked capture. The local validation found zero address mismatches and zero written-color mismatches against the pre-state CPU value. This is strong low-level writer evidence, **not** a 64,000-byte final-framebuffer zero-diff result.

## 3. DOS v2.0 controlled projectile lifecycle

A controlled-reachability original-runtime test leaves the executable, projectile pool and RNG untouched while setting only documented player weapon/mode/ammo RAM fields.

The original FIRE path allocates slot 0, consumes one ammunition unit `64 -> 63`, and the sampled slot then executes the complete basic lifecycle:

`0 free -> 1 flying -> 2 impact -> 0 free`.

The trajectory starts at world `(1440,3596)`, performs regular movement steps and reaches impact at `(1440,3263)`; the following state-2 snapshots hold position until expiry. The nearby E1M1 wall data supports a wall collision at the crossed grid boundary, but the exact collision helper was not captured instruction-by-instruction at transition time.

This closes one FC-selector wall-impact lifecycle, not FB/FD/FE, GUARD-hit damage, pool-full behavior or all weapons.

## 4. E2M10 nested scheduler static narrowing

SHA-pinned opcode analysis closes the local E2M10 loop that repeatedly calls the outer scheduler while an unsigned target generation remains ahead of the current generation.

The calculation intentionally keeps only the low 16 bits of the product before division. This detail is preserved in the v0.49 bounded model.

Repeated scheduler calls make stale projectile-state resurrection and a true ABA overwrite structurally possible under additional conditions. **Neither stale resurrection nor ABA reuse has yet been observed in a natural original E2M10 runtime capture.**

## 5. Cross-build differences that now require version adapters

### DOS 1.9 -> 2.0

The examined loaded code segment grows by 48 bytes. Several concrete v2.0 branches differ from v1.9, including a new dispatcher/action path and a temporary state at `DS:417A`. These differences are not represented as a single behavior-percentage score.

### Win16 1.8 -> 1.10 palette manager

The checked Win16 v1.10 code conditionally reserves 10 palette entries at each end for the system palette. When the relevant capability flag is set it copies 236 middle RGB entries; otherwise it copies all 256. Earlier v1.8 behavior uses the full 256-entry path.

This is a real platform/version-specific rendering difference and must not be flattened into one universal DOS/Win palette routine.

### Win16 runtime laboratory

Windows 3.11 itself is functional in the current lab (Notepad opens), but none of the five tested Nitemare Windows builds 1.0/1.3/1.6/1.8/1.10 displayed a game window in the bounded headless attempts. Static imports are internally consistent, while the installed WinG runtime is incomplete. The exact failing Win16 call remains open.

## 6. Clean-room project Linux portability fixes

A full source build exposed three host-side defects:

1. `HandleMap16` acquired trailing host padding; the recovered Win16 layout requires two-byte aggregate packing and explicit offset checks.
2. `kFreshGuardStrength` was independently defined in both combat and guard headers and caused a same-namespace redefinition when both headers entered one translation unit. It now lives in shared `GuardConstants.hpp`.
3. `unknown_systems_audit_test.cpp` depended on registry insertion order. It now searches by area/evidence instead of fixed tail indexes.

The source-level validation that motivated these fixes reported GCC and Clang builds, sanitizer CTest, Python tests and WORX tests passing. Those are clean-room build/regression results, not original-game parity evidence.

A separate SDL3 3.4.18 headless build also produced the `nitemare3d` executable and rendered 12 synthetic-data frames with exit code 0. Because the input data were synthetic and the SDL build was headless, this proves executable integration/smoke behavior only.

## 7. Remaining P0 frontier

Highest-value open items remain:

1. execute RNG #17 and continue the original DEMO ledger through accepted death animation/outcome and later records;
2. close natural E2M10 repeated nested projectile-pool visits and rule in/out stale resurrection/ABA;
3. capture projectile collision writer and projectile-to-GUARD damage/SFX paths;
4. complete SAVE/LOAD first-post-load-frame and RNG/cache rebinding;
5. produce canonical original-vs-port 64,000-byte framebuffer plus palette zero-diff;
6. make the Win16 runtime laboratory reach a real Nitemare game window and collect equivalent event traces;
7. build an end-to-end original-vs-port acceptance matrix before assigning strict complete-parity percentages.

No proprietary executable, game data, RAM dump or original trace is added by this release.
