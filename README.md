# Nitemare3D-Reversed — reconstruction v0.56

**v0.56 / 2026-10-19 recent-days frontier consolidation:** freezes the current evidence boundary after integrating the newly available 19-Oct runtime/static/build findings. The recent chain now covers GUARD41 death through score/map cleanup, Win16 WinG startup to E1M1 in 5/5 builds, the DOS2 random-event timer RNG branch, one controlled projectile `0→1→2→0` lifecycle, E2M10 repeated-scheduler narrowing, DOS HUD reindex/class36 weapon pickups, cross-build MAP marker A/B effects, the Win16 managed-palette delta, and DEMO seed/reader/last-record static narrowing. **Full DEMO RNG/EOF, natural E2M10 ABA, SAVE/LOAD first frame, framebuffer+palette zero-diff, Win16 gameplay timing, exact audio, and strict original-vs-port acceptance remain OPEN.** See [v0.56 frontier](docs/V056_REMAX_FRONTIER_CONSOLIDATION.md).

**v0.55 / 2026-10-19 DEMO seed/EOF static narrowing:** separates the DOS seed helper from real RNG consumption, pins the local seed-reset and DEMO reader opcodes, and records the complete DOS DEMO.1 payload endpoints (275 records; first `48E0/0002/8`, last `74E0/0090/1074`). The reader applies the current record before reading the next, while the local caller near `6E07` does not immediately test the read-count return value. This narrows EOF behavior but does not close CRT short-read/error semantics or the final demo transition. Large older captures that missed the seed-reset interval are explicitly rejected as chronology evidence. See [v0.55 report](docs/V055_REMAX_DEMO_SEED_EOF_STATIC.md).

**v0.54 / 2026-10-19 cross-build map/palette delta:** consolidates the 31-level DOS/Win high-byte marker census and controlled E1M1 A/B tests. The audited data contains four selected `0x25..0x28` high-byte positions per level (124 total), concentrated near the player start; clearing each one individually in DOS2 produces a visible E1M1 scene difference while repeated baseline-vs-baseline remains identical. The same update records the DOS1.9→2.0 main-band growth and the Win16 v1.10 palette rule that conditionally reserves 10+10 system entries and copies 236 middle colors instead of all 256. Exact resource identity and full cross-build pixel parity remain OPEN. See [v0.54 report](docs/V054_REMAX_CROSSBUILD_MAP_PALETTE.md).

**v0.53 / 2026-10-19 HUD reindex + weapon class36 static closure:** corrects the DOS1.9→2.0 HUD dispatcher mapping: DOS2 inserts a new damage-related action at ID4 and shifts the old IDs4–8 to IDs5–9. The local `DS:417A=3` damage signal yields the static HUD action sequence `4→4→4→3`; exact final pixels remain OPEN. Separately, Win16 v1.10 MAP high IDs `0x25..0x28` are now tied to weapon pickup class `0x36`, variants 0..3, ownership bits `1/2/4/8`, and 50-unit ammo initialization, with variants 0 and 3 sharing the same plasma/laser ammo store. DOS pickup-algorithm equivalence is not assumed. See [v0.53 report](docs/V053_REMAX_HUD_WEAPON_CLASS36.md).

**v0.52 / 2026-10-19 DOS2 random-event timer closure:** adds a complete local original-runtime RNG consumer from the DOS v2.0 timed/random-effects substep. The measured branch performs phase `1→0`, RNG state `1→0x0029E2C0`, returns `41`, and stores countdown `201 = 160 + (41 % 240)`. An independent longer trace repeats the same transition and records countdown `201→200→199` while the global tick advances `85→88`. In the measured top-level order this RNG consumer belongs to the `0x039E` random-effects substep after the `0x037D` actor traversal. The writer that initialized state 1 in this normal E1M1 path and the global RNG order remain OPEN. See [v0.52 report](docs/V052_REMAX_DOS20_RNG_TIMER.md).

**v0.51 / 2026-10-19 Win16 WinG runtime closure:** the Windows 3.11 laboratory now reaches a rendered E1M1 scene in **all 5/5 Win16 builds** (1.0, 1.3, 1.6, 1.8, 1.10) after completing the WinG 1.0 runtime from the user-provided Microsoft package. V1.10 also required removing a local old `WING.DLL` conflict in the laboratory copy; no Nitemare executable or game data were patched. Win16 runtime is therefore no longer blocked at application startup, but gameplay-input timing, RNG, framebuffer/palette zero-diff, animation and audio parity remain OPEN. See [v0.51 report](docs/V051_REMAX_WIN16_WING_RUNTIME.md).

**v0.50 / 2026-10-19 GUARD41 death closure:** extends the natural DOS1.2 DEMO.1 runtime path from lethal HP through the measured death handler. A bounded original trace now executes RNG #16, #17 and #18 without a gap: #16 and #17 reject animation candidates, #18 accepts one. The same trace writes GUARD41 HP `111→0`, updates its timer/state/next-state, increments score `0→100`, and clears the linked map marker `0xA5→0x00`. This supersedes the v0.49 prediction-only status for RNG #17. Later death-animation completion, drop logic, pool cleanup, DOS2/Win16 equivalence and end-to-end parity remain OPEN. See [v0.50 report](docs/V050_REMAX_GUARD41_DEATH_OUTCOME.md).

**v0.49 / 2026-10-19 runtime + buildability sync:** integrates the newest DOS runtime/static evidence and fixes three clean-room Linux portability defects. DOS1.2 DEMO.1 now has bounded original-runtime evidence through RNG #16 plus the observed entry to #17, including GUARD41 planner writes, a real HP `111→0` death-producing damage branch at RNG #15, and an animation rejection backedge at RNG #16. A separate DOS2 Advanced History E1M1 trace records 3,775,835 instructions, 289,190 VRAM events, 7,315 VGA-register snapshots and 12 complete main-update executions; the checked low-level VRAM writer events have zero local address/color mismatches, but this is **not** final-framebuffer parity. Controlled DOS2 runtime now also closes one projectile `0→1→2→0` wall-impact lifecycle. E2M10 opcode analysis proves a repeated outer-scheduler backedge, while natural projectile resurrection/ABA remains OPEN. Cross-build work adds a concrete Win16 v1.10 236-vs-256 palette-copy rule. The clean-room source now also fixes Win16 `HandleMap16` host packing, the duplicate GUARD-strength constant, and an order-fragile audit test. See [v0.49 report](docs/V049_REMAX_OCT19_RUNTIME_BUILD_SYNC.md), [evidence facts](docs/V049_EVIDENCE_FACTS.csv) and [Linux build validation](docs/LINUX_BUILD_VALIDATION_2026-10-19.md). **Strict original-vs-port zero-diff parity remains OPEN.**

**v0.48 / 2026-10-18 DEMO bootstrap + first-input closure:** consolidates five original-runtime DEMO.1 evidence captures for the tested DOS runtime build. Natural menu selection now closes the transition into demo playback, E1M11/map-index 10 loading, header `15/7/30`, the first record `key=0x48E0,input=2,counter=8`, and the post-map RNG seed reset to `1`. The alternate demo scheduler is observed returning in both mode 3 and mode 4, with its parity decision occurring before the later render-counter increment. The first record is applied only when the live counter reaches 8, before the next record is loaded, and a paired runtime capture proves that this first input moves the player from `(1056,3168)` to `(1071,3168)` at angle 90 with step 15. The DOS RNG recurrence is also encoded exactly, but **the first natural RNG consumer after seed=1, total RNG order, EOF behavior, later records, cross-build determinism and framebuffer parity remain OPEN.** See [v0.48 report](docs/V048_REMAX_DEMO_BOOTSTRAP.md) and [bounded C++ evidence](src/re/N3DV048DemoBootstrap.hpp).

**v0.47 / 2026-10-18 WORX DMA runtime closure:** records a naturally reached DOS runtime Sound Blaster/DMA start and the later automatic stop path. The original reached WORX with the playback-active flag set, completed DMA/DSP setup including DSP port `0x22C`, DMA mode `0x59`, address `0xDB6E`, page `0x01`, count `0x0FFF`, and unmasked the DMA channel. Later the automatic `5F59` path cleared the active flag, emitted DSP command `0xD0`, masked the DMA channel, and only afterward entered the explicit stop helper with playback already inactive. This closes natural DMA start + automatic stop for the tested DOS build, but **does not** yet close active playback at central shutdown, audible waveform parity, or exact hardware timing. See [v0.47 report](docs/V047_REMAX_WORX_DMA_RUNTIME.md).

**v0.46 / 2026-10-18 runtime acceptance sync:** integrates the latest original DOSBox-X evidence. PASS16 now proves a natural same-scheduler boundary sequence `PROJECTILE C24B→C250 → INPUT C26F→C274` and corrects PASS15 DS/WORLD alias attribution. GUARD PASS17–22 adds executed alert/attack/planner/movement coverage, including real state00 underflow, 14/4 HP attack witnesses, state05's own movement call, eight-step state06 timers and the double-block RNG bounce where odd flips `vx` and even flips `vy`; one measured state05 consumes planner RNG plus collision RNG in the same update. Original DOS1.2 and DOS2 now also agree in controlled weapon selection/commit/mode/ammo tests including held Multi Plasma and shared ID0/ID3 plasma ammo. Shutdown evidence adds non-fatal no-XMS cleanup plus configuration-reachable `INT63 AH=0D/07/04` digital stop/IRQ restore; active DSP/DMA stop remains unobserved. See [v0.46 report](docs/V046_REMAX_RUNTIME_ACCEPTANCE_SYNC.md) and [bounded C++ evidence](src/re/N3DV046RuntimeAcceptance.hpp). **Complete DEMO RNG order, active projectile FB–FE/reentry, SAVE/LOAD first frame, framebuffer+palette zero-diff, Win16 runtime and audible audio parity remain OPEN.**

**v0.45 / 2026-10-18 weapon-switch frame ordering:** composes the audited DOS switch/HUD/scheduler/input paths into one bounded direct-frame contract. A request made while a weapon is already active updates `pending` and, if idle, starts Lower; the current weapon/fireMode remain unchanged until the HUD Lower path reaches zero and commits pending→current. Since weapon selection occurs before FIRE inside the same input function, that later FIRE still sees the old current weapon for a normal active-weapon switch; only the `current==0xFF` direct-equip case can expose the newly selected weapon to FIRE in that same input call. In the direct parent frame, HUD transition runs before projectile update and gameplay input, so a commit can be observed by FIRE later in the same frame; weapon 3 may then fire immediately if held FIRE and carried cadence counter≥1. Conversely a projectile spawned by that input cannot be processed by the already-completed direct parent projectile pass. **Nested/reentrant scheduler visits remain OPEN.** See [v0.45 report](docs/V045_REMAX_WEAPON_SWITCH_FRAME_ORDER.md) and [C++ contract](src/re/N3DV045WeaponSwitchFrameOrder.hpp).

**v0.44 / 2026-10-18 weapon FIRE closure:** promotes the strongest existing weapon/cadence evidence into a buildable compatibility contract. The four cadence thresholds are fixed to `[2,1,3,1]`; weapon 3 (Multi Plasma) can auto-repeat while FIRE remains held, while weapons 0–2 require a fresh edge. Accepted cadence resets the cooldown **before** the FIRE dispatcher, so later rejection by no-selected-weapon, jam, action state, no ammo or full projectile pool can still consume cooldown. Projectile allocation checks the 8-slot pool before the ammo helper, therefore a full pool does not consume ammo. Weapons 0 and 3 share the same plasma-cell counter. The selectedWeapon=`0xFF` cadence overread is now modeled with audited initialized bytes (DOS1.2=`0x33`, DOS2.0=`0x65`, Win1.10=`0x03`), exposing a bounded cross-build timing divergence before the common FIRE rejection. See [v0.44 report](docs/V044_REMAX_WEAPON_FIRE_CLOSURE.md) and [C++ contract](src/re/N3DV044WeaponFireClosure.hpp). **Natural Multi Plasma tick timing, weapon-switch-with-held-FIRE, multi-target hitscan, jam/event side effects and DEMO/RNG coupling remain OPEN.**

**v0.43 / 2026-10-18 runtime + GUARD + renderer sync:** integrates the newest live DOSBox-X evidence and the latest static closures. Main now includes a natural DOS 1.2 E1M1 door USE witness (record 8 state 1→2, flag 0→1 with other door records unchanged), a 32,768-instruction world-update trace with 33/33 live queue entries matching the RAM snapshot order, and a deep DOS shutdown/CRT evidence summary covering video mode 3, WORX/music stop, PIT divisor `0xFFFF`, interrupt restoration, mouse/RTC cleanup, XMS cache release, exit-BSF processing, CRT callbacks, restore INT00 and normal `INT 21h/AH=4Ch` exit code 0. The same release packages the v0.80 complete local GUARD contact-damage switch, the v0.81 OLD19/NEW26 GUARD initializer and conditional Dancers area-wake RNG divergence, the corrected E1M9 radio writer/reader lifecycle, and the DOS v2.0 bounded sprite-pixel contract. **These are scoped original-static/runtime closures, not whole-project zero-diff parity.** See [v0.43 report](docs/V043_REMAX_RUNTIME_STATIC_SYNC.md), [runtime/GUARD contracts](src/re/N3DV043RuntimeClosure.hpp), [E1M9 lifecycle](docs/E1M9_STATIC_LIFECYCLE.md), and [sprite pixel contract](docs/RENDERER_STATIC_PIXEL_CONTRACT.md).

**v0.42 / 2026-10-18 static sync:** integrates the newest October 18 RE passes. The incoming-damage path is now explicitly version-scoped: DOS 1.0–1.9 gates protection/game-state before calculation, while DOS 2.0 and Win16 calculate first, can consume class-dependent RNG and arm the feedback timer before a later protection return. The SAVE/LOAD model now records SECRET fixed-32-byte I/O with only N meaningful panel states, byte-to-WORD restore, and 64-door LOAD prefix preservation (DOS 8/18 bytes, Win16 12/22). A corrected pool audit separates DOS/Win dynamic-wall and class-3 geometry families, reclassifies 62 ambiguous writer sites and records 72 direct OBJECT map-pointer update call edges. Win16 E2M10 mode-4 queue ACK behavior and NE timing-import relocation ordinals are also captured. Adds C++20/Python regressions, CSV facts and [v0.42 report](docs/V042_REMAX_OCT18_STATIC_SYNC.md). **No live original trace, pixel zero-diff or audio zero-diff is claimed.**

**v0.41 / 2026-10-18 latest static-evidence consolidation:** synchronizes the repository with the late 17 October RE passes. The largest correction is E1M9 MAP-layer ownership: Win16 1.3–1.10 radio mode-0 clears the **WALL byte**, not the OBJECT byte, so radio activation does not by itself remove the projectile GUARD-property gate. New bounded contracts also encode the split 16+16 projectile deadline rearm clock hazard, E2M10 palette-effect-before-hit ordering, the nested scheduler global-frame-scratch/local-epoch split, the 12-build OBJECT+18/generation/damage correspondence, exact source pool capacities (including E3M8 SECRET 32/32 and E2M10 door-controller 60/64), matched MAP+IMG resource provenance, and a DOS sprite-compositor reference (100×18-byte slots, status-only init, v1.7+ lazy-load branch). Adds C++20/Python regressions, machine-readable static facts and a consolidated report. **No live original trace, pixel zero-diff or audio zero-diff is claimed.** See [v0.41 report](docs/V041_REMAX_LATEST_STATIC_CONSOLIDATION.md), [evidence contracts](src/re/N3DV041LatestStaticEvidence.hpp) and [frame compositor](src/re/N3DV041FrameCompositor.hpp).

**v0.40 / 2026-10-17 projectile one-level reentry closure:** narrows the E2M10 same-slot ABA hypothesis by combining the audited deferred state-2 write, pool state dispatch, allocator ordering and property-`0x40` counter semantics. A nested pool can revisit the suspended parent slot while it is still `state=1`, but a slot visit that **starts in state 1 never falls through to the state-2 expiry arm in that same visit**. It therefore ends that visit as state 1 (no hit) or state 2 (accepted hit), not state 0. Because input/FIRE allocation occurs later in the same nested outer-scheduler invocation, that allocator cannot reuse the same slot through the standard lifecycle. A same-path second E2M10 hit advances the counter `20 -> 21` and does not immediately launch another nested wait. Thus the **direct one-level self-reentry path cannot perform state1→2→0→reuse before the suspended parent resumes**. Independent nested callbacks, aliased state writers, SAVE/LOAD/IRQ effects and a genuine second pool entry beginning in state 2 remain OPEN. Adds bounded C++20/Python models, regressions, CI and [v0.40 report](docs/V040_REMAX_PROJECTILE_REENTRY_ABA_NARROWING.md).

**v0.39 / 2026-10-17 late-day static closure:** packages the newest RE-first findings into buildable evidence models. The E2M10 property-`0x40` special collision now has a 12-build static return chain proving normal script return `AL=1` -> accepted collision -> IMPACT, so that path does **not** execute the DDA budget reread. E1M9 radio/state-`0x14` timing is narrowed to a 112-count lifecycle with global stop on the 113th slow update under unchanged-state assumptions; the upward GUARD scheduler can create same-pass state asymmetry. The FIRE cadence core is modeled with original thresholds `[2,1,3,1]`, fresh-edge requirements for weapons 0–2 and the held-FIRE weapon-3 exception. Cannon/class-`0x19` weapon damage is zero in all 12 audited builds but still consumes the pre-dispatch RNG draw. DOS clock routing now distinguishes RTC cache, BIOS BDA ×55 and system-date/time backends, and the renderer angle initializer is recorded as a one-turn ±360 correction rather than true modulo. Adds C++20/Python reference models, synthetic regressions, CI and a consolidated report. **No new original-runtime trace, framebuffer zero-diff or audio zero-diff is claimed.** See [v0.39 report](docs/V039_REMAX_LATE_STATIC_CLOSURES.md), [C++ contracts](src/re/N3DV039LateStaticClosures.hpp) and [Python models](tools/n3d_v039_static_models.py).

**v0.38 / 2026-10-17 three-day RE consolidation:** adds a buildable evidence layer for several high-value findings from 14–16 October that were still scattered outside the main N3D code path. New bounded models cover the Win16 v1.8→v1.10 joystick recalibration clamp, Magic Eye automap RNG draw budget, rare door state 4 blocking, the 18-byte door versus 14-byte four-VEC one-extra-update cleanup difference, Hamerstein/class `0x16` damage direction plus pre-dispatch RNG consumption, signed E2M10 every-20 semantics, raw low16 timing averages, DOS v1.2/v2.0 initial graphics/SAVE 4 KiB aliasing, and the projectile callback mixed-generation invariant. Adds a C++20 header, C++ regression, data-free Python oracle/tests, CI wiring and a consolidated report. **No fresh original DOSBox-X/OTVDM trace, framebuffer zero-diff or audio zero-diff is claimed, so full runtime parity remains open.** See [v0.38 consolidation](docs/V038_REMAX_THREE_DAY_CONSOLIDATION.md), [C++ models](src/re/N3DV038ThreeDayFindings.hpp) and [Python oracle](tools/n3d_v038_recent_models.py).

**v0.37 / 2026-10-15 RE MAX scheduler catch-up closure:** Original DOS v2.0 unpacked MZ byte audit resolves the local timing rules in `BEB4` slow clock and `BEF4` calibrated frame clock. Each compares a quantized time key and **increments its counter only once when that key changes**, even after a large time jump. Outer `C1A8` uses unsigned due thresholds and resets the next eligibility to the **observed counter + 1** after one slow/frame pass, never replaying all overdue buckets locally. Normal FAST `C1EA` is suppressed in DEMO; DEMO FAST `C22E` is gated on **pre-render** odd `DS:4540`. **Both FAST paths receive slowCounter**, not frameCounter, which drives the separate `C150` second action `&7` gate. A rare unsigned delta of more than 500 legacy clock units activates `BDE4(1)`, `BDE4(0)` and a `BDF8` resample; clock rollback can satisfy this branch due to wrap. Adds a SHA-bound original opcode verifier checking 25 instruction windows, 13 branch targets and 13 direct calls, a version-scoped C++ reference, regression tests and Windows/Linux CI. **These facts close local static catch-up behavior, NOT nested interrupts, full RNG seed=1 timing, exact original display cadence or 1:1 rendering.** See [v0.37 evidence](docs/V037_REMAX_SCHEDULER_CATCHUP_STATIC_CLOSURE.md), [read-only verifier](tools/n3d_v037_scheduler_gate_probe.py) and [C++ model](src/re/N3DV037SchedulerCatchup.hpp).

**v0.36 / 2026-10-15 RE MAX original-damage-order audit:** independently rechecked four fingerprinted DOS unpacked executables (**1.0, 1.7, 1.9, 2.0**). DOS 1.0/1.7/1.9 test protection and terminal state **before** calling incoming-damage producer; DOS v2.0 calls producer **before** those gates, and nonzero damage sets hit-indicator countdown to 3 even if the protection gate then preserves HP. For RNG-damage classes 08/09/0A/11..14 this can consume a draw without changing HP, a cross-version seed/order parity difference. Original DOS v2.0 hit timer update follows three code-4 draw dispatches and one code-3 clear dispatch over four timer-updater invocations, **not necessarily four rendered frames**. A rare branch condition also means HP=0 and damage=0 would be lethal if the unprotected nonterminal state reaches the comparison; its natural runtime reachability remains OPEN. Added strict SHA-gated four-build opcode/branch/FAR-target verifier, DOS v1.7 profile, build-scoped C++ reference model, data-free regression tests and CI. This revisits a lead from the pre-existing September cross-version audit; it does not claim original game execution or increase full 1:1 parity. See [v0.36 evidence](docs/V036_REMAX_PROTECTED_HIT_RNG_ORDER.md), [verifier](tools/n3d_v036_protected_hit_probe.py) and [C++ reference](src/re/N3DV036ProtectedHitOrdering.hpp).

**v0.35 / 2026-10-15 RE MAX RNG census correction:** a fresh SHA-256-gated scan of the original DOS v2.0 unpacked load image proves **22** literal direct far-CALL sites to `0FBA:01A0`, not the 20 previously encoded. The two missing legitimate calls `8860` and `886C` are *incoming-player-damage* branches reached through the original 23-entry class table; masks are `RNG&7` for class 08, `RNG&15` for classes 09/0A and `RNG&31` for classes 11..14 (existing `887C`). The strict FAST/RNG Python verifier, v0.20 C++ caller table, v0.22 evidence record and v0.26 22-entry immediate-consumer registry are corrected. Further recovered static consumers include GUARD activation `5582` (`RNG%8`), projected OBJECT variant rejection `B276` (possibly multiple draws), numeric class SFX/effect selection, and resource modulo-7 loops at `9FE3/A047` whose comparison with 7 is locally unreachable but whose table-value rejection remains functional. Adds a read-only original-image verifier, 23 instruction-window witnesses, exact class dispatch checks, synthetic C++/Python tests and CI. **This is a corrected static caller census, not a complete indirect-call inventory or measured DEMO seed=1 runtime order.** See [v0.35 evidence](docs/V035_REMAX_RNG_22_CALLSITE_CENSUS.md), [RNG verifier](tools/n3d_v035_rng_census.py) and [C++ census](src/re/N3DV035RngCensus.hpp).

**v0.34 / 2026-10-15 RE MAX original-binary call-graph audit:** DOS v2.0 OBJECT animation updates are now grounded in two conditional rendering/projection routes rather than the disproven `0E50` all-OBJECT hypothesis. `C1A8 → BF36 → 2500 → 241E` advances SPAN-associated OBJECT frames after a deadline and nonzero descriptor gate. `BF36 → 21F0 → B2D4 → B22C/B17E` advances projected objects after flags, clipping and class-specific conditions; projectile update `8230` independently calls `B2D4`. Span animation can invoke RNG at `2478`, relevant to DEMO determinism. DEMO FAST at `C22E` tests the existing frame-generation low bit *before* `BF36` increments it. The first FAST child `C51A` is a RETF-only stub, not object logic. Adds canonical DOS build fingerprint-gated verification of 16 direct call edges and 18 opcode windows, C++ evidence predicates, synthetic regression tests and Windows/Linux CI. **An exhaustive generic OBJECT writer census, dynamic visibility effects and original-run runtime chronology remain OPEN.** See [v0.34 report](docs/V034_REMAX_OBJECT_ANIMATION_RENDER_BRANCHES.md), [original-byte probe](tools/n3d_v034_animation_probe.py) and [C++ evidence](src/re/N3DV034ObjectAnimationEvidence.hpp).

**v0.33 / 2026-10-14 RE MAX original-byte scheduler correction:** the former DOS v2.0 `0E50` generic-OBJECT candidate is definitively the six-byte **PUSH** updater. Its complete 292-byte updater body matches Win16 v1.10 NE seg3:`2210` after masking exactly 20 relocation/address-operand bytes; all 272 remaining instruction bytes are identical. The instruction-exact branch tests destination OBJECT property bits `0x06`, conditionally copies and clears MAP object bytes, commits X/Y, calls X/Y sorted-pointer-list repair, then decrements the PUSH counter. StartPush separately tests destination WALL bit `0x02` and sets counter 8. Updated scheduler/evidence registries, strict fingerprint-gated original-byte verifier, C++ reference primitives and synthetic CI regressions. **Generic OBJECT scheduler and full FAST/RNG/runtime timing remain OPEN; a defensive modern empty-target PUSH policy may diverge on nonblocking occupied cells.** See [v0.33 report](docs/V033_REMAX_PUSH_SCHEDULER_BINARY_CLOSURE.md), [verifier](tools/n3d_v033_push_verify.py) and [PUSH C++ reference](src/re/N3DV033PushScheduler.hpp).

**v0.32 / 2026-10-14 RE MAX original-binary audit:** verified five version-specific executable fingerprints (DOS 1.0/1.9/2.0 unpacked images, DOS 1.2 *packed* MZ candidate, Win16 1.10 raw NE) and checked 16 Win16 + 8 DOS v2.0 original instruction windows. Recovered the Win16 PUSH destination wall-property bit 0x02, 94-byte gameplay-block USER.SAV HP offset 0x206A (100 in supplied real save), exact nonlethal GUARD and Dracula writer addresses, DEMO/input 0x20 and 0x40 steps, DOS door retry=4 writer, Win16 projectile full-pool pre-ammo return, and DOS secret-panel endpoint cleanup. Added a build-hash-gated read-only verifier, synthetic tests and C++ proof registry, with no original game bytes redistributed. **These are narrow static/format closures, not 1:1 full runtime; first passable panel tick, total writer XREF census, DEMO scheduling, and full LOAD chronology are open.** See [v0.32 report](docs/V032_REMAX_ORIGINAL_BINARY_CLOSURES.md), [verifier](tools/n3d_v032_static_verify.py), and [C++ evidence registry](src/re/N3DV032StaticClosure.hpp).

**v0.31 / 2026-10-14 RE MAX update:** protects the modern `LevelState` PUSH implementation against overwriting a destination that becomes blocked mid-animation; a new no-original-assets C++ regression exercises blocked/resumed movement, same-ID occupancy and source mutation. Adds a strict, ordered four-scenario edge-trace comparator for PUSH, door auto-close, full projectile pool and secret-panel VEC geometry, with 11 synthetic Python tests and Windows/Linux CI wiring. CSV matching, even with declared capture envelopes, **does not establish original 1:1 runtime parity**. Door retry=4, pool-full ammo, secret-panel passability and scheduling remain evidence-scoped/open. The ordinary 100-HP Win16 cap was already verified in earlier health analysis, not discovered in v0.31. See [v0.31 report](docs/V031_REMAX_EDGE_CASE_CLOSURE.md), [edge comparison tool](tools/n3d_edge_trace_compare.py) and [data-free PUSH test](tests/pushable_blocked_test.cpp).

**v0.30 / 2026-10-14 RE MAX update:** closes a *verification-harness gap*, not an original-game runtime gap: one syntactically valid LCG stream or matching final RNG state cannot prove the original draw order. Adds a strict original-vs-reconstruction FAST/RNG trace comparator (first divergent call/record, no sorting or silent re-alignment), tests for nested FAST callbacks and missing logger rows, a SHA-256 gate for the canonical **unpacked DOS v2.0** image, and per-CSV integrity/boundary envelopes. Integrates a build-scoped C++ closure model and synthetic Windows/Linux CI tests. A matching trace without captured event boundaries is labeled **unsealed**; even an attested match does not by itself prove a real original-game recording. No gameplay/pixel parity is claimed or percentage raised. See [v0.30 report](docs/V030_REMAX_DIFFERENTIAL_TRACE_CLOSURE.md), [Python comparator](tools/n3d_trace_compare.py) and [C++ checks](src/re/N3DV030TraceClosure.hpp).


**v0.29 / 2026-10-14 RE MAX update:** preserves the reported DOS v2.0 `1000:C150` FAST *direct-call* order, including the gated final `89A2`, in a version-scoped C++ evidence registry. Adds synthetic-tested Python/C++ FAST and seed-1 RNG trace diagnostics that detect first divergences while distinguishing nested calls from direct children. Records DOS v1.2/v2.0 state-4 door differences, PUSH blocked-step behavior, door retry=4, the E2M10 special-hit nested-scheduler lead, and post-LOAD first-tick uncertainty with explicit static/strong/open labels. **These are bounded prior static findings and diagnostic tools, not new original-runtime captures or proven 1:1 scheduler parity.** See [`docs/V029_REMAX_SCHEDULER_TRACE_AND_EDGE_CASES.md`](docs/V029_REMAX_SCHEDULER_TRACE_AND_EDGE_CASES.md), [`src/re/N3DV029SchedulerEvidence.hpp`](src/re/N3DV029SchedulerEvidence.hpp), and [`tools/n3d_trace_audit.py`](tools/n3d_trace_audit.py).


**v0.28 / 2026-10-09 RE evidence update:** cross-checks independent DOS v2.0 documentation and the new native Win11 x64 rewrite, with explicit source attribution and no unverified 1:1 claims. Adds the original read-only Python tools [`n3d_bsf_audit.py`](tools/n3d_bsf_audit.py) (BSF header/chunk decode plus DOS/Win16 checksum verification) and [`n3d_demo_layout_probe.py`](tools/n3d_demo_layout_probe.py) (Win16 vs DOS-record interpretation, without guessing bit semantics), plus synthetic fixture tests and Windows/Linux CI. The prior BSF algorithm was already documented in v5; new work here is executable validation and cross-build evidence classification. See [`docs/V028_EXTERNAL_EVIDENCE_BSF_DEMO.md`](docs/V028_EXTERNAL_EVIDENCE_BSF_DEMO.md). **No original game files or borrowed external source code are included; complete runtime/renderer parity remains open.**

**v0.27 / 2026-10-07 RE MAX update:** projectile behavior is now represented as a build-scoped lifecycle evidence graph covering DOS v2.0 and Win16 v1.10. The graph preserves confirmed allocation/init/movement/collision/render anchors, the 8 x 42-byte composite pool, and the `0 -> 1 -> 2 -> 0` slot lifecycle. Strong-but-open edges such as next-tick movement after FIRE, full-pool ammo preservation, and stale projection-cache effects remain explicitly non-implementation-safe. See [`docs/V027_REMAX_PROJECTILE_LIFECYCLE.md`](docs/V027_REMAX_PROJECTILE_LIFECYCLE.md) and [`tests/v027_projectile_lifecycle_test.cpp`](tests/v027_projectile_lifecycle_test.cpp).

**v0.26 / 2026-10-07 RE MAX update:** DOS v2.0 direct RNG callsites are now coupled to known GUARD/animation consumers with explicit confidence. Confirmed bindings include the animation `RNG&7` rejection-loop callsite, GUARD state-06 blocked-axis one-draw decision, and GUARD state-13 `RNG%80+8` timer. Planner callsites and the damage/pain callsite remain STRONG rather than promoted, while all other direct RNG callsites stay OPEN/Unassigned until runtime chronology closes them. See [`docs/V026_REMAX_GUARD_RNG_COUPLING.md`](docs/V026_REMAX_GUARD_RNG_COUPLING.md) and [`tests/v026_guard_rng_coupling_test.cpp`](tests/v026_guard_rng_coupling_test.cpp).

**v0.25 / 2026-10-07 RE MAX update:** GUARD state changes are now tracked as a writer graph, separate from the state-handler table. Known Win16 v1.10 handler-level writes are recorded with exact handler addresses, while external transitions such as ordinary pain entry and the Dracula phase reset preserve their confirmed written values but keep `addressKnown=false` until the exact write instruction/XREF is pinned. See [`docs/V025_REMAX_GUARD_WRITER_GRAPH.md`](docs/V025_REMAX_GUARD_WRITER_GRAPH.md) and [`tests/v025_guard_writer_graph_test.cpp`](tests/v025_guard_writer_graph_test.cpp).

**v0.24 / 2026-10-07 RE MAX update:** the Win16 v1.10 GUARD dispatcher is now represented as a 22-state evidence graph for states `0x00..0x15`. Each state carries its handler address, control-flow description, transition form, and separate control-flow versus semantic confidence. Confirmed transitions such as `01->02`, `06->03`, `10->0F`, `11->07`, plus `00/12/15 -> nextstate`, are regression-tested. DOS v2.0 `1000:59F0` remains dispatcher-level STRONG evidence only; per-state DOS handlers are not guessed. See [`docs/V024_REMAX_GUARD_STATE_GRAPH.md`](docs/V024_REMAX_GUARD_STATE_GRAPH.md) and [`tests/v024_guard_state_graph_test.cpp`](tests/v024_guard_state_graph_test.cpp).

**v0.23 / 2026-10-07 RE MAX update:** cross-version mapping is now behavior-oriented rather than offset-oriented. `N3DV023CrossBuildSymbolMap.hpp` assigns stable behavior IDs to build-specific DOS v2.0 and Win16 v1.10 symbols, preserves per-entry confidence, and deliberately leaves missing equivalents unresolved instead of guessing addresses. A pair is considered confirmed only when both sides are present and CONFIRMED. See [`docs/V023_REMAX_CROSS_BUILD_SYMBOL_MAP.md`](docs/V023_REMAX_CROSS_BUILD_SYMBOL_MAP.md) and [`tests/v023_cross_build_symbol_map_test.cpp`](tests/v023_cross_build_symbol_map_test.cpp).

**v0.22 / 2026-10-07 RE MAX update:** executable identity and RE confidence are now machine-readable. `N3DV022VersionEvidenceRegistry.hpp` introduces build profiles for DOS v1.0/v1.2/v1.9/v2.0 and Win16, but only DOS v2.0 carries a confirmed fingerprint until the other binaries are independently hashed. The same registry scopes facts to builds, records evidence provenance and closure tests, and exposes a promotion guard so only CONFIRMED facts can be treated as implementation-ready. See [`docs/V022_REMAX_VERSION_EVIDENCE_REGISTRY.md`](docs/V022_REMAX_VERSION_EVIDENCE_REGISTRY.md) and [`tests/v022_version_evidence_registry_test.cpp`](tests/v022_version_evidence_registry_test.cpp).

**v0.21 / 2026-10-07 RE MAX update:** DOS v2.0 subsystem anchors and runtime regions are now centralized in an evidence map with confidence labels. The new layer classifies GUARD, player, projectile, action/FIRE, secret-panel and renderer addresses; keeps `0800:0E50` explicitly OPEN as an OBJECT-runtime candidate; and adds a relative-order verifier for captured traces without pretending the complete FAST/MAIN schedule is already known. See [`docs/V021_REMAX_SUBSYSTEM_EVIDENCE.md`](docs/V021_REMAX_SUBSYSTEM_EVIDENCE.md) and [`tests/v021_subsystem_evidence_test.cpp`](tests/v021_subsystem_evidence_test.cpp).

**v0.20 / 2026-10-07 RE MAX update:** the project now has a dedicated deterministic verification harness for the remaining timing/RNG closure work. `N3DV020VerificationHarness` encodes the confirmed DOS v2.0 IRQ/clock/FAST/MAIN/outer-scheduler anchors, validates captured RNG transitions and known direct callsites, classifies scheduler trace events, and reports the first divergent address between traces. The unresolved `0800:0E50` OBJECT runtime site remains explicitly marked OPEN rather than being mislabeled as a proven scheduler. See [`docs/V020_REMAX_VERIFICATION_HARNESS.md`](docs/V020_REMAX_VERIFICATION_HARNESS.md) and [`tests/v020_verification_harness_test.cpp`](tests/v020_verification_harness_test.cpp).

**v0.19 / 2026-10-07 RE MAX update:** another set of executable-backed runtime primitives is now represented directly in code. `N3DV019RuntimePrimitives` preserves the DOS v2.0 player collision footprint `0x1B`, the GUARD state-06 one-draw blocked-axis decision, planner/state-13 RNG timer formulas, the 2-unit secret-panel retraction step, and automap/detector drain intervals. Evidence confidence is encoded alongside the helpers so unresolved sliding order, exact scheduler interleaving and pool-full ammo behavior are not silently promoted to 1:1 facts. See [`docs/V019_REMAX_RUNTIME_PRIMITIVES.md`](docs/V019_REMAX_RUNTIME_PRIMITIVES.md) and [`tests/v019_runtime_primitives_test.cpp`](tests/v019_runtime_primitives_test.cpp).

**v0.18 / 2026-10-07 update:** October RE findings are now promoted into buildable C/C++ evidence modules instead of remaining only in research notes. `src/re/n3d_v018_facts.h` and `.c` encode build-scoped DOS v2.0 player, projectile, GUARD, RNG, secret-panel, renderer and scheduler anchors; `src/re/N3DV018Evidence.cpp` adds C++ compile-time layout checks; and `tests/v018_evidence_test.cpp` regression-tests the promoted facts and RNG sequence. Corrections from the latest audit are preserved explicitly: old Win16/DOS offsets are not treated as universal, `+0x50` is not promoted as an OBJECT stride, and secret panels are modeled as segmented VEC retraction rather than rigid pushwalls. See [`docs/V018_EVIDENCE_INTEGRATION.md`](docs/V018_EVIDENCE_INTEGRATION.md) and the October 1–7 research reports under [`docs/research/2026-10-01_07/`](docs/research/2026-10-01_07/).

**v0.17 / 2026-09-29 update:** recovered executable behavior is now pushed further into the actual runtime source instead of living only in RE notes. `CombatSystem.hpp` implements the verified class × weapon resistance transform and difficulty scaling; `GuardSystem.hpp` exposes the verified positive-hit receiver outcome; `ObjectSystem.hpp` exposes executable-backed runtime/property predicates; and `ProjectileRuntime.hpp` adds explicit collision/impact decisions around the verified 8 × 42-byte projectile pool. Renderer code remains conservative where directional/vertical sprite selection is still behavioral rather than instruction-verified. See [`docs/PROJECT_STATUS_V017.md`](docs/PROJECT_STATUS_V017.md) and [`tests/v017_runtime_integration_test.cpp`](tests/v017_runtime_integration_test.cpp).

**v0.16 / 2026-09-27 update:** cross-version function coverage is now represented explicitly in code instead of living only in audit prose. The current audited export contains 519 DOS function definitions and 967 Win16 definitions. Exact/strong fuzzy cross-version matching supports 429/519 DOS functions and 929/967 Win16 functions, leaving 90 DOS and 38 Win16 definitions requiring weak-match/manual boundary review. This is a function-identity/matching metric, **not** a percentage of semantic understanding. See [`src/re/N3DV016Coverage.hpp`](src/re/N3DV016Coverage.hpp), [`tests/v016_coverage_test.cpp`](tests/v016_coverage_test.cpp), and [`docs/PROJECT_STATUS_V016.md`](docs/PROJECT_STATUS_V016.md).

**v0.15 / 2026-09-27 update:** behavioral sprite/object spatial findings are now preserved explicitly instead of being folded into generic renderer assumptions. The new model distinguishes floor-, mid-height- and ceiling-anchored sprites; fixed versus view-dependent directional variants; collision/blocking behavior; and vertical oscillation. Current behavioral evidence records the Bat as a ceiling-associated animated GUARD with vertical bob/oscillation during attack behavior, while some world objects use player-view-dependent variants (for example front/side bed views). These are intentionally marked as `BEHAVIORAL` until exact executable writers/dispatchers are recovered. See [`src/re/N3DV015SpriteFacts.hpp`](src/re/N3DV015SpriteFacts.hpp), [`tests/v015_sprite_facts_test.cpp`](tests/v015_sprite_facts_test.cpp), and [`analysis/nite3w_sprite_object_spatial_2026-09-27.md`](analysis/nite3w_sprite_object_spatial_2026-09-27.md).

**v0.14 / 2026-09-27 update:** the project now records a deeper whole-program reverse-engineering workflow in code and documentation. The v0.14 analysis model tracks CFG, SSA-style value flow, DFG, Use-Def/Def-Use chains, liveness, alias relationships, cyclomatic complexity, dominators, natural loops, interprocedural call graphs, cross-version matching and evidence provenance. See [`src/re/N3DV014Analysis.hpp`](src/re/N3DV014Analysis.hpp), [`tests/v014_analysis_test.cpp`](tests/v014_analysis_test.cpp), and [`docs/TOOLS_USED_V014.md`](docs/TOOLS_USED_V014.md).

**v0.13 / 2026-09-26 update:** the newest DOS/Win16 static-analysis pass is now encoded in source. Win16 v1.8 pushables use class `0x28`, a 6-byte PUSH record, cardinalized octant tables, and an 8-tick × 8-unit one-tile move. GUARD direction generation now preserves the audited ±8 movement and strategy-2 ±16 movement, and class-specific initialization from `FUN_1010_AF7E` is represented conservatively. New player direction globals and DOS v1.8/v2.0 table/function anchors are in [`src/re/N3DV013Facts_2026_09_26.hpp`](src/re/N3DV013Facts_2026_09_26.hpp), covered by `n3d_v013_recovered_facts_test`.

**2026-09-25 update:** HUD/automap/menu dispatchers, renderer globals, GUARD state/field corrections, IMG/UIF HUD-bank facts, and CDC/MFC wrapper anchors are now encoded in [`src/re/Win16RecoveredFacts_2026_09_25.hpp`](src/re/Win16RecoveredFacts_2026_09_25.hpp) with a regression test. The full evidence boundary is in [`docs/PROJECT_FINDINGS_DELTA_2026-09-25.md`](docs/PROJECT_FINDINGS_DELTA_2026-09-25.md). `LevelState` also now owns its definition tables and reserves moving pushable destinations to avoid dangling references and target overwrite races.

**v0.12 update:** the 2026-09-23 audit maps the Win16 player projectile pool and save fields, and adds the executable-confirmed 100/10/2 HP fire damage values per simulation update. The IMG pass now separates the two 256-entry image directories from the two 90-byte sequence banks, preserves raw sequence records, and flags an unresolved overlap in the low bank. See [the IMG/seqdef audit](analysis/nite3w_img_seqdef_2026-09-23.md) and [the consolidated delta](docs/PROJECT_FINDINGS_DELTA_2026-09-23.md).

**v0.11 update:** the 2026-09-23 raw-assembly pass resolves the Win16 renderer's occupied-column owner rules, texture-U corrections, 16.16 wall-column sampler, 16.16 span interpolation, and wall-animation update control flow; DOS E-20 contains matching texture-U/animation routines and independently confirms the sampler formulas. Findings are in [`analysis/nite3w_renderer_2026-09-23.md`](analysis/nite3w_renderer_2026-09-23.md); the standalone reference code is [`src/renderer/Win16WallRasterCore.hpp`](src/renderer/Win16WallRasterCore.hpp), with a CMake test target. The 2026-09-22 cross-thread consolidation and system audits remain linked below.

Modern C++ reconstruction scaffold for the **Windows 3.1** version of Nitemare 3D.
The design goal is to preserve the original data formats and reconstructed game logic while replacing obsolete Windows 3.x display plumbing (`WING.DLL` and `DISPDIB.DLL`) with **SDL3**.

## AI assistance disclosure

This is an **AI-assisted reverse-engineering and reconstruction project**. A substantial part of the analysis, research, documentation, code generation, refactoring, and interpretation of reverse-engineered material has been produced with the assistance of **ChatGPT by OpenAI**, under the direction and review of **marek177**.

Git commit authorship therefore identifies the account that committed the files and should **not** be interpreted as meaning that every analysis, document, or line of code was written manually and independently by the repository owner. AI-generated or AI-assisted findings may contain errors, especially where original source code or symbols are unavailable, so important reverse-engineering conclusions should be independently verified against the original executable and game data.

## Reverse-engineering status

Start with the consolidation and newest delta:

- [`docs/PROJECT_FINDINGS_DELTA_2026-09-25.md`](docs/PROJECT_FINDINGS_DELTA_2026-09-25.md) — HUD/automap/menu, renderer globals, GUARD corrections, IMG/UIF HUD bank, MFC CDC anchors and runtime safety fixes
- [`docs/ALL_THREADS_CONSOLIDATION_2026-09-22.md`](docs/ALL_THREADS_CONSOLIDATION_2026-09-22.md)
- [`docs/PROJECT_FINDINGS_DELTA_2026-09-23.md`](docs/PROJECT_FINDINGS_DELTA_2026-09-23.md) — consolidated findings from all current audits
- [`analysis/nite3w_core_function_map_2026-09-23.md`](analysis/nite3w_core_function_map_2026-09-23.md) — DOS/Win16 core-function coverage map
- [`analysis/nite3w_projectile_pool_2026-09-23.md`](analysis/nite3w_projectile_pool_2026-09-23.md) — projectile record, collision, save and render details
- [`analysis/nite3w_img_seqdef_2026-09-23.md`](analysis/nite3w_img_seqdef_2026-09-23.md) — original IMG directory and sequence-bank loading, with the low-bank overlap still unresolved
- [`analysis/nite3w_guard_reaction_2026-09-23.md`](analysis/nite3w_guard_reaction_2026-09-23.md) — Win16 guard state 13 movement and state 15 hit-reaction transitions, cross-checked in 1.8
- [`docs/PROJECT_FINDINGS_DELTA_2026-09-22.md`](docs/PROJECT_FINDINGS_DELTA_2026-09-22.md) — previous cross-session corrections
- [`docs/UNKNOWN_SYSTEMS_AUDIT_2026-09-22.md`](docs/UNKNOWN_SYSTEMS_AUDIT_2026-09-22.md) — consolidated unknowns, priorities and evidence boundaries

Then use the subsystem reports for instruction-level evidence:

- [`analysis/nite3w_renderer.md`](analysis/nite3w_renderer.md)
- [`docs/GUARD_AI_RE.md`](docs/GUARD_AI_RE.md)
- [`docs/COMBAT_DAMAGE_RE.md`](docs/COMBAT_DAMAGE_RE.md)
- [`docs/PLAYER_HEALTH_RE.md`](docs/PLAYER_HEALTH_RE.md)
- [`docs/PLAYER_COLLISION_RE.md`](docs/PLAYER_COLLISION_RE.md)
- [`docs/USE_INTERACTION_RE.md`](docs/USE_INTERACTION_RE.md)
- [`docs/SPECIAL_WALL_USE_RE.md`](docs/SPECIAL_WALL_USE_RE.md)
- [`docs/SAVE_LIBRARIES_IDA_REPORT.md`](docs/SAVE_LIBRARIES_IDA_REPORT.md)
- [`docs/RE_AUDIT_CHEATS_AUDIO.md`](docs/RE_AUDIT_CHEATS_AUDIO.md)

Well-understood areas now include:

- Win16/WinG platform path and 320×200 indexed framebuffer;
- normal 304×152 3-D viewport;
- MAP→boundary-vector construction;
- 1000×28-byte VEC pool;
- four orientation-specific 333-entry VECLIST pointer indexes;
- per-column owner table and wall-span coalescing;
- wall and sprite raster stages plus the 100-entry projected-sprite queue;
- MAP/archive geometry and major runtime capacities;
- OBJECT 28-byte and GUARD 26-byte record sizes;
- player collision/USE/pushable mechanics;
- player health and both directions of difficulty scaling;
- player→GUARD weapon/class damage matrix;
- GUARD score switch and 22-state dispatcher skeleton;
- Dracula `0x11 -> 0x14` two-phase transform with HP reset;
- GUARD25/class `0x20` constrained as an unresolved/cut/fallback class rather than a known enemy;
- SND.DAT directory/PCM format, MIDI inventory;
- CONFIG.SAV physical size and USER.SAV block layout, including the 8-slot/42-byte projectile pool and wake cache;
- many doors/warps/pushables and numerous level-specific scripts.

Renderer work is moving from recovered facts into tested primitives: owner-conflict predicates, texture-U correction, span interpolation, and the linear fixed-point wall-column loop are implemented. The full scene path still needs integration and pixel comparison. Other open work includes wall-animation/resource mapping, sprite and palette details, door/panel/control records, GUARD states 02–14 and attack timing, enemy-projectile identity/behavior, enemy-to-player class binding, GUARD25, Dracula's resource/sound/corpse chain, automap byte values, BSF integrity, and remaining save/resource fields.

## Renderer architecture

The renderer audit corrects an important early assumption: NITE3W does **not** use Wolfenstein 3-D's one-grid-ray-per-screen-column DDA.

The recovered path is:

```text
64x64 MAP
  -> exposed boundary extraction + merging
  -> VEC[1000] (28 B each)
  -> four VECLIST[333] far-pointer indexes
  -> project/near-clip candidate vectors
  -> 320-entry wall-owner table
  -> <=50 visible wall spans (20 B each)
  -> textured wall columns + per-column wall occlusion
  -> <=100 projected sprite commands (18 B each)
  -> 320x200 8-bit framebuffer
```

See the [renderer audit](analysis/nite3w_renderer.md) and its [2026-09-23 raw-assembly update](analysis/nite3w_renderer_2026-09-23.md). The runtime `Raycaster.cpp` remains a provisional grid-DDA viewer; it has not yet been replaced with the recovered vector/span scene renderer.

## Current runtime architecture

```text
original MAP / IMG / GAME.PAL / definitions
                 |
                 v
      reconstructed C++ loaders
                 |
                 v
      8-bit indexed framebuffer
                 |
                 v
        palette -> ARGB8888
                 |
                 v
               SDL3
```

The original `WING.DLL` and `DISPDIB.DLL` are not loaded by the reconstruction.

## Build

### Inspector only (no SDL dependency)

```bash
cmake -S . -B build -DN3D_ENABLE_SDL3=OFF
cmake --build build
./build/n3d_inspect data/original
./build/n3d_pushable_test
./build/n3d_menu_cheat_test
./build/n3d_hazard_test
./build/n3d_projectile_runtime_test
./build/n3d_win16_wall_raster_core_test
./build/n3d_demo_file_test
./build/n3d_guard_facts_test
./build/n3d_v013_recovered_facts_test
./build/n3d_v014_analysis_test
./build/n3d_v015_sprite_facts_test
./build/n3d_v016_coverage_test
./build/n3d_v017_runtime_integration_test
./build/n3d_v018_evidence_test
./build/n3d_v019_runtime_primitives_test
./build/n3d_v020_verification_harness_test
./build/n3d_v021_subsystem_evidence_test
./build/n3d_v022_version_evidence_registry_test
./build/n3d_v023_cross_build_symbol_map_test
./build/n3d_v024_guard_state_graph_test
./build/n3d_v025_guard_writer_graph_test
./build/n3d_v026_guard_rng_coupling_test
./build/n3d_v027_projectile_lifecycle_test
./build/n3d_v029_scheduler_evidence_test
./build/n3d_v030_trace_closure_test
./build/n3d_v032_static_closure_test
./build/n3d_v033_push_scheduler_test
./build/n3d_v034_object_animation_evidence_test
./build/n3d_v035_rng_census_test
./build/n3d_v036_protected_hit_ordering_test
./build/n3d_v037_scheduler_catchup_test
./build/n3d_v038_three_day_findings_test
```

### Windows 11 + SDL3

With SDL3 installed through vcpkg:

```powershell
vcpkg install sdl3:x64-windows
cmake -S . -B build `
  -DCMAKE_TOOLCHAIN_FILE=C:/vcpkg/scripts/buildsystems/vcpkg.cmake
cmake --build build --config Release
build\Release\n3d_inspect.exe data\original
build\Release\nitemare3d.exe --data data\original --episode 1 --level 1
```

Or configure with `-DN3D_FETCH_SDL3=ON` if you want CMake to fetch SDL3.

The `nitemare3d` executable currently displays a top-down preview of the selected original 64x64 map using the original palette. That small viewer is deliberate: it validates the modern SDL path before the original 3-D renderer is transplanted.

## Original data

Original game assets are intentionally excluded from the public repository. Copy your own game files with:

```bash
python scripts/import_original_data.py /path/to/Nitemare3D
```

## Reverse-engineering toolchain

The v0.14 toolchain and analysis methodology are documented in [`docs/TOOLS_USED_V014.md`](docs/TOOLS_USED_V014.md). Not every listed tool is implied to have been used for every individual finding; executable/data evidence remains authoritative.

## Useful project-local tools

```bash
python tools/ne_inspect.py data/original/NITE3W.EXE
python tools/ne_renderer_audit.py data/original/NITE3W.EXE xrefs 'internal 3:D78C'
python tools/n3d_save_inspect.py CONFIG.SAV USER.SAV
n3d_inspect data/original
```

## Video audit coverage

Episode 1 and Episode 2 walkthrough material has durable audit coverage. Episode 3 has dedicated repository reports for E3M3, E3M4, E3M5, E3M6 and extended/finale material; where source videos contain cuts, the reports retain those limitations rather than claiming false 100% frame coverage.

E3M6 confirms the passability distinction: small/medium fire is traversable and large fire is impassable/lethal per original material. The Win16 audit now maps fire object IDs 0x3B/0x3C/0x3D to large/medium/small and confirms damage values of 100/10/2 HP per simulation update. The calibrated interval and damage-per-second remain open.

## Next engineering targets

1. Complete `wall ID/class -> flags -> handler -> renderer class` mapping.
2. Decode animated-wall sequence timing and `FUN_1010_65A6`.
3. Complete door/panel/control record/state semantics.
4. Finish GUARD state 02–14 naming plus movement/attack timing.
5. Bind enemy-to-player class transforms to visible enemies/projectiles.
6. Resolve GUARD25/class `0x20` reachability and resource identity.
7. Trace the complete Dracula `0x11 -> 0x14` sequence/sound/corpse chain.
8. Resolve the 4096-byte per-cell runtime state block and `OBJECT+14/+16/+18` semantics.
9. Integrate the recovered Win16 camera/vector/span pipeline and sprite/resource ordering into the runtime; validate it against deterministic original frames.
10. Finish wall-animation and special-resource mappings, DOS/VGA backend comparisons, BSF integrity/version-diff reconstruction, SFX/MIDI/UIF/ENDING.FLI edge cases and unresolved USER.SAV blocks.
