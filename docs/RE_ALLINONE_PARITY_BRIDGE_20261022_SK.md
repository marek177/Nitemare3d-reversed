# Nitemare 3D — original runtime → static RE → modern Linux remake: P0 bridge (22.10.2026)

This note aligns **existing original execution proofs**, the new archived Ghidra writer graph, and V088/V089 diagnostic tooling. It does **not** claim full operational parity.

## Verification layers (never interchangeable)

| Grade | What is demonstrated | What is *not* demonstrated |
|---|---|---|
| S — original static | opcode/fixup/class/caller/writer graph under a pinned build | that an edge ran in the target scenario |
| R — original runtime | an observed input/state/register/write/event on the original | that a modern C++ implementation agrees |
| B — bounded replay | agreement for given original operands or one original writer | entire frame, all cache paths and all inputs |
| M — modern model/CI | deterministic self-consistency of a C++/Python contract | exact original scheduler, tick, audiovisual timing |
| P — paired parity | identical original/candidate state at a synchronized boundary with actual source provenance | full-game certification unless all representative cases have been covered |

## Current mismatch between capture schemas

**V088** requires tick-aligned ordered original/candidate records with integer X/Y, 0..359 heading, DOS input masks, health, weapon, ammo, actor/projectile counts and evidence envelopes. **V089** captures preview **frames**, **tile coordinates**, **radian angle**, preview-local key bits, pushable ticks and render activity; it intentionally does not invent HP/ammo/guards/projectiles. Their CSVs **cannot** be directly diffed by relabeling columns or converting units alone.

Required adapter is **new actual engine integration**, not a cosmetic converter:

- establish DOS original tick/IRQ/update/frame boundaries and an equivalent deterministic modern candidate tick;
- map original 16-bit coordinates, heading representation and observed key bits into the candidate engine using independently tested integer rules;
- capture matching gameplay fields at the same update boundary, with no absent field silently set to zero;
- record stable actor/object/slot IDs and scheduler epoch; pair event streams (RNG, FIRE/USE, memory read/write) separately from sampled state;
- retain original EXE SHA and a trusted monotonically ordered sample/event ID.

## Renderer release gate

Bounded owner, span, texture-U and native writer proof is real (e.g. V078/V079/V080), but the **production Raycaster.cpp remains diagnostic DDA**. Do not replace it until an independently captured **original after-wall-pass** indexed frame + 768 DAC values can be compared against the native candidate at the identical state. Full pixels **64,000/64,000** plus DAC **768/768** need zero mismatches; provide the first nonmatching owner, source U/V, shade, palette index, VRAM address and timing. Sprites, clipping, HUD, page switch and audio are distinct follow-up gates.

## Priority experiments

1. **FIRE and USE:** new E1M1 weapon pickup/press-rearm runtime → static FIRE writer and ammunition/pool scheduler → fixed-tick native replay.
2. **Projectile cached +0x18:** GHIDRA01–03 original-static alias → writer/reader runtime trace at natural collision, E2M10 reentry, LOAD first update.
3. **Renderer:** original post-wall VGA 320×200 index + DAC with camera/VEC/SPAN checkpoint → same-boundary wall replay; no masked holes.
4. **RNG/DEMO:** seed→last record→EOF with call ordinal + timer/scheduler/held mask; identical LCG tuples alone are insufficient.
5. **Win16:** WinG 1.0 v1.0–1.10 original startup/LOAD is now possible, but message/clock/DAC/audio timing differs from DOS and must be tested independently.
6. **Coverage:** representative deterministic actions on E1M1–E3M10 plus E1M11/DEMO, then special boss/door/secret/pushable cases.

Use [V088](GAMEPLAY_DIFF_V088_2026-10-22.md), [V089](PREVIEW_FRAME_TRACE_V089_2026-10-22.md), [cached target graph](RE_STATIC_GHIDRA_CACHE_20261022_SK.md), [FIRE report](RE_DOS20_FIRE_PICKUP_20261022_SK.md), [full frame gate](V081_RENDERER_WALL_FRAME_ACCEPTANCE_PLAN.md). No proprietary original binary or full unbounded RAM/VRAM is committed to public GitHub.
