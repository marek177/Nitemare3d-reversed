# RE-MAX v0.66 — original DOS v2.0 GUARD41 death CPU trace

**Date:** 2026-10-20. **Evidence:** NEW ORIGINAL RUNTIME, original DOS v2.0 DEMO.1, one continuous 20,000-instruction CPU/memory trace. Not modern-port parity.

## Provenance

Original unmodified packed DOS2 N3D.EXE SHA256 a3fa02335e1d8bc531918f3bfaa66217aef65c81e562a2fdf1c749be652ca485 with matching original DEMO/MAP/IMG/OBJECTS. No RAM injection, cheats or game EXE modifications.

Emulator: DOSBox-X 2026.10.01 Heavy Debug, N3D Advanced History v3 + deferred-trace overlay v0.65, complete Linux ELF SHA256 11631a6cb93bc9cbf595d63165be2072bfd76c21530e9e744430f3282d19c42d. Xvfb, core normal, fixed 7000 cycles, SDL2, Main Menu -> Demo.

The deferred tracing gate required *both* runtime CS:IP 0CEB:1333 / opcode 26 88 64 10 *and* GUARD41 pointer ES:SI 2A21:2A78. The first recorded original CPU instruction had AX=006F: HP 111, AH=0. Private original binary trace SHA256 6bea0e04196ee540b46f1ea56ebadaa4abcc7c2b52d571882cbcb0026d071f4b.

## Exact recorded original instruction chronology

| Executed CPU instruction ordinal | Effect |
|---:|---|
| 1 | GUARD41 HP 111 -> 0 at linear 0x2CC98 |
| 52-53 | RNG 0xA6E9C9A6 -> 0x81EB59D1, AX=491, selector modulo 7 = 1 |
| 105-106 | RNG 0x81EB59D1 -> 0x0BB31550, AX=2995, selector modulo 7 = 6 |
| 158-159 | RNG 0x0BB31550 -> 0xAEA69ED3, AX=11942, selector modulo 7 = 0 |
| 215 | GUARD WORD +0x00, 0x0410 -> 0x0429 |
| 223 | GUARD timer +0x06, 2 -> 3 |
| 225 | GUARD next animation +0x0C, 05 -> 09 |
| 227 | GUARD active state +0x0B, 06 -> 00 |
| 256-257 | 32-bit score lower WORD 0 -> 100, upper WORD remains 0 |
| 3662 | Linked map marker 0xA5 -> 0x00 at linear 0x2F181 |

Original selector code at 1061:1C3F executed a backward branch to 1061:1C13 after trials #16 and #17. The third trial #18 executed the forward acceptance path at 1061:1C41. Thus 2 rejected + 1 accepted variants are confirmed by actual CPU branch transitions, not only by a mathematical RNG endpoint.

**Bounded original trace:** 20,000 CPU instruction records, 56,070 memory reads, 12,612 memory writes, total 88,682 events and 4,392,568 bytes. End reason INSTRUCTION_BUDGET, *not* SIZE_LIMIT. CPU and memory event ordinals are strictly sequential.

## Independent verification

Original private N3DTRC01 stream was reparsed. Exact start opcode/registers, 14 relevant actor/RNG/score/map writes with old/new/width, three RNG transitions, retry/accept control flow, event totals, and bounded stop all PASS.

Six mutated temporary copies (HP, RNG word, score, map, actor SI, branch target) were independently rejected. Do not mistake successful verifier tests for another original gameplay capture: they validate the single original trace stored privately.

The user-owned private bundle N3D_GUARD41_DOS20_DEATH_TRACE_V065_20261020.zip contains binary CPU trace, verification scripts, original capture summaries and images, event timeline, and SHA256 manifest. Raw trace includes historical game instruction bytes and should remain private; no original commercial binaries or raw trace are added in this repository.

## Closure boundary

**RUNTIME VERIFIED:** a complete instruction-exact DOS2 GUARD41 death path through HP zero, RNG choice and retries, timer/animation/state commit, score+100 and map-marker deletion for the observed natural DEMO route.

**OPEN:** the later GUARD state0->9->0x0A transition, RNG#19, post-death/drop/pool cleanup, other GUARD classes, DOS/Win16 variations, IRQ/timing edge cases, and original-versus-clean-room framebuffer, timing and audio parity. A screenshot or separate epilogue from another actor does not close those obligations. No global 1:1 percentage change is justified.

**Next test:** a new original DOS2 multi-tick trace should trigger on the correct GUARD actor record in the state0 handler (BX-based writer) and continue state0->9->0x0A through RNG#19 and post-death cleanup. An actor-specific gate is necessary because the same state-update code processes unrelated enemies.
