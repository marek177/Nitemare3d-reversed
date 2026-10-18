# Nitemare 3D RE MAX v0.43 — runtime + GUARD + renderer sync

**Date:** 18 October 2026  
**Scope:** synchronize main with the newest October 18 runtime evidence, v0.80/v0.81 GUARD static closures, the DOS v2.0 sprite-pixel contract, and the E1M9 radio lifecycle correction.

## Evidence boundary

This release deliberately separates three evidence levels:

- **Original static:** SHA-gated original DOS/Win16 opcode/data/relocation audits.
- **Original runtime:** DOSBox-X DEBUGBOX execution of the original DOS game for the specifically identified test builds and scenarios.
- **Bounded reconstructed model:** C++/Python contracts and tests that encode only the proven local behavior.

No whole-project parity percentage is raised merely by packaging these findings. Full original-vs-port zero-diff acceptance, DEMO total RNG chronology, pixel-perfect framebuffer parity and live audio parity remain open.

## 1. Original runtime: natural E1M1 door USE

A natural DOS 1.2 E1M1 run reached a classic door without patching player or door memory. The original USE path executed and door record index 8 changed:

- state +08: 1 -> 2
- flag +10: 0 -> 1
- the other eight 18-byte door records remained byte-identical in the before/after dump.

This closes only the observed USE-to-open-start transition for that reachable scenario. It does not claim the full natural 2->0->3->1 lifecycle, first-passable tick, player-blocked close, all door families, audio output or DEMO timing.

## 2. Original runtime: world update traversal

A 32,768-instruction DOSBox-X CPU trace of E1M1 captured a complete pass over a live 26-byte record queue with 33 records. The runtime dispatcher visited all 33 entries in the same order as the memory snapshot; the traced types were 31 records of type 07 and two of type 08 in that sampled state.

This is scenario evidence, not a universal GUARD population rule. It materially strengthens scheduler/update-order confidence because the queue layout and executed dispatch order now agree in live original execution.

## 3. Original runtime: normal DOS shutdown

The tested DOS shutdown now has an execution-backed chain rather than only a static call graph. The captured normal Quit path includes:

1. return to BIOS video mode 3;
2. audio/WORX shutdown with observed music-stop dispatch;
3. PIT programming with divisor FFFFh (65535);
4. restore calls for INT08 and INT63;
5. mouse reset through INT33 AX=0000;
6. restore of INT09;
7. RTC periodic-disable path and restore of INT70;
8. game-cache XMS unlock and free;
9. post-cleanup read/decode/print of the exit BSF resource;
10. CRT callback traversal;
11. restore of INT00;
12. final INT21 AH=4Ch with exit code 0.

The runtime trace also proves that the RTC ISR can still execute during the earlier audio-cleanup phase before the later RTC-disable step. That ordering must not be simplified away in an exact compatibility mode.

## 4. Exit BSF resource

For the tested shutdown build, the exit resource is 474 decoded bytes. The independently reconstructed XOR decode matches the runtime buffer byte-for-byte and uses a key period of 52.

The print loop checks both current and next byte before emitting current through a %c-like CRT path. For this nonzero 474-byte payload, the final LF immediately before the loader-added NUL is not emitted by that loop; 473 payload bytes are passed to the character-print path.

The commercial text itself is not reproduced in this repository.

## 5. Runtime failure path: late BSF-open error

A controlled late BSF-open failure after normal central cleanup reached a second cleanup. The stale game-cache handle caused repeated XMS unlock/free requests to fail; the caller ignored those failures and continued. The original then exited through the same CRT family with exit code 1.

This proves that the observed cleanup path is not universally idempotent. A clean-room port should document exact compatibility behavior separately from any intentional safety fix.

## 6. GUARD v0.80: complete local contact-damage switch

The 12-build audit closes the local 23-entry incoming-player-damage switch:

- class 08: RNG & 7
- class 09/0A: RNG & 15
- class 0B: base / 4
- class 0C/1D/1E: full base
- class 0D/0E/0F/10/15/17/18/1A/1B/1C: base / 2
- class 11..14: RNG & 31
- class 16: 33 when episode != 3 and event-latch byte is zero, otherwise 100
- class 19: 100
- classes outside 08..1E: base / 2

The signed distance helper result is guarded before division; positive distance uses floor(100/distance), nonpositive uses base 100. Difficulty 0 halves, difficulty 2 doubles, other values leave the scalar unchanged. The local result remains within 0..200 for the audited input domain.

Natural AI reachability of every class/caller remains a separate proof obligation.

## 7. GUARD v0.81: historical initializer and area wake

Across the audited builds there are two initializer families:

- **OLD19:** DOS 1.0–1.2 and Win16 1.0, classes 08..1A in the explicit table.
- **NEW26:** DOS 1.5–2.0 and Win16 1.3–1.10, classes 08..21.

Dancers class 21 therefore starts as state7/next2 in OLD19 but state0/next0 in NEW26, before the shared movement override. Alien #2 class1F remains state7/next2 through both families.

The area-wake helper accepts only strategy0, same area, unused latch and state7/8; accepted wake consumes RNG%8, stores the remainder as timer and enters state1. Thus OLD19 Dancers have a conditional extra RNG-wake path that NEW26 Dancers do not have if all other wake predicates match. Natural E1M9 reachability of those predicates remains open.

## 8. E1M9 radio lifecycle correction

The integrated E1M9 lifecycle branch preserves the corrected MAP ownership:

- audited Win16 1.3–1.10 radio mode0 clears the WALL byte;
- the adjacent OBJECT byte is preserved by that local write;
- GUARD+0C is overloaded and must not be treated as an unconditional saved-group field;
- mode1 restoration applies only to records still in state14.

This removes an old false assumption that radio activation itself deleted the OBJECT property source needed by projectile lookup.

## 9. DOS v2.0 sprite pixel contract

The integrated renderer branch contributes an instruction-backed subset of the DOS v2.0 sprite writer:

- unsigned wall-depth comparison, with actor flag 0x10 bypass;
- source texel 0x1F transparency;
- exact local vertical setup and clipping arithmetic;
- 16.16 source-step carry/wrap;
- planar VGA offset using the original AL-only y multiply;
- sequencer values for the four VGA planes;
- status-driven integration with the existing 100x18-byte compositor model.

This is not the complete renderer. Horizontal setup, full projection/bucket ownership, descriptor loading, page selection and original indexed-framebuffer zero-diff remain open.

## 10. Repository additions

This v0.43 main sync integrates the two tested research branches and adds a new bounded runtime/static evidence layer:

- src/re/N3DDos20SpriteRaster.hpp
- tests/dos20_sprite_raster_test.cpp
- tools/n3d_dos20_sprite_verify.py
- docs/RENDERER_STATIC_PIXEL_CONTRACT.md
- .github/workflows/sprite-pixel-contract.yml
- src/re/E1M9RadioLifecycle.hpp
- tests/e1m9_radio_lifecycle_test.cpp
- docs/E1M9_STATIC_LIFECYCLE.md
- corrected GUARD and gameplay documentation from the E1M9 branch
- src/re/N3DV043RuntimeClosure.hpp
- tests/v043_runtime_closure_test.cpp
- docs/V043_REMAX_RUNTIME_STATIC_SYNC.md
- docs/V043_EVIDENCE_FACTS.csv
- README / DISCOVERIES / CMake / CI integration

## 11. Remaining highest-priority work

1. DEMO seed=1 complete RNG consumer order.
2. Weapon FSM 0–3, especially Multi Plasma.
3. Projectile FB–FE lifecycle through genuine nested second pool entries.
4. E1M9 legal route, accepted shot, Skeleton/Dancers state and lookup lifetime.
5. Scheduler/IRQ split-read and reentrant chronology beyond the sampled traces.
6. SAVE/LOAD first post-load tick and all pointer/deadline rebinding.
7. Full classic/secret/remote door lifecycle and first-passable tick.
8. Renderer horizontal/projection integration and 64,000-byte indexed framebuffer + palette zero-diff.
9. Win16 runtime shutdown/message-loop/destructor chronology.
10. Live audible WORX/MPU/OPL/SB timing.

