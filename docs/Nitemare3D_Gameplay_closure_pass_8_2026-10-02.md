# Nitemare 3D — Gameplay closure pass 8
## Final static-core closure + automated original-runtime acceptance capture
Date: 2026-10-02

## Result

Pass 8 reaches the useful end of broad static Gameplay reconstruction.

The important distinction is now explicit:

- **Gameplay STATIC implementation core:** closed for the checked reference paths.
- **Win16 boss/special-actor STATIC core:** now closed rather than left at 99% merely because ending presentation still needs live observation.
- **Original-runtime behavioral parity:** still requires controlled captures; it is not promoted to 100% by static evidence alone.

This pass also removes the main practical obstacle to those captures by creating and corrected DOSBox-X MCP snapshot tool for the two-segment DOS V2.0 memory model and and scenario-aware acceptance analyzer.

## 1. Boss AI — static core can now be separated from presentation

The recovered boss/special-actor runtime no longer contains an unresolved AI algorithm:

- Dracula uses the common GUARD machine, with class `0x11 -> 0x14` fatal transform, HP reset to 255, state 8, next state 2, timer 1, then ordinary final death for class 0x14.
- Dr. Hamerstein uses the common strategy-0 GUARD machine; its uniqueness is resistance/damage and the fatal story/ending hook (`51AA -> ending.fli`).
- Demon class `0x1D` has no separate initializer or fatal-state engine; its differences are tuning/SFX/score/resistance.
- Cannon class `0x19` is the genuine special cycle and its `0x0E -> 0x0F -> attack -> 0x10 -> 0x0F` control flow, disable flag, perception, damage and timer return are already reconstructed.
- ACTIONSPOT/Dancers is and scripted temporary phase, not and hidden boss scheduler.

Cross-build evidence is also strong: the Win16 1.8 -> 1.10 deep mapping reports exact-normalized identity for the guard initializer `B02C` and the special actor/sound helpers `B5E4`, `B6A0`, `B762`, `B862`, while `A0EE` is independently documented as the same normalized shape across all four checked Win16 builds.

**Closure decision:** **Boss AI = 100% STATIC for the checked Win16 gameplay core.**

Ending/video timing and visual presentation remain behavioral/content validation, not missing AI logic.

## 2. DOS GUARD dispatcher — to not use the corrupt normalized score as gameplay coverage

The generic cross-version table gives DOS `59F0` and weak score because the V2.0 pseudo-C boundary is polluted.

Raw DOS 1.9 disassembly independently closes it as and 22-entry `0x00..0x15` GUARD dispatcher and closes the linked all-guard loop and player-hit router.

Therefore the bad C-normalization score is and decompiler-quality signal, not evidence of an unknown second AI implementation.

The correct rule for the gameplay tracker is:

- use raw/manual dispatcher semantics for GUARD state-machine closure;
- use normalized cross-build matching only where function boundaries are reliable.

## 3. DOS `8230` correction retained

Older broad automatic registers sometimes labeled `1000:8230` as player movement. The checked V2.0 body proves it is the **8-slot projectile updater**:

- pool base `DS:41B6`;
- 8 records;
- stride `0x2A` (42 bytes);
- state at `+0x0C`;
- frame/sequence at `+0x11/+0x12`;
- deadline at `+0x16`;
- X/Y at `+0x1E/+0x20`.

The actual player movement/collision core is the `6488` family.

This correction matters when using automated all-function labels as and future implementation source.

## 4. New automated gameplay snapshot capture

Generated:

`n3d_dosboxx_gameplay_capture_pass8.py`

It uses the same DOSBox-X debugger MCP control channel already validated by the framebuffer-capture work, but captures only gameplay state.

It automatically:

1. connects to DOSBox-X;
2. stops the emulator;
3. reads CPU/segment registers;
4. takes `near.bin` from the **actual runtime DS**;
5. reads `near:417E` to obtain the relocated far gameplay arena segment;
6. validates `near:417C` against the expected MAP offset range;
7. captures `arena.bin` from that arena segment;
8. writes hashes, registers, player HP/ammo anchors and segment provenance to `manifest.json`.

Output:

```text
snapshot/
    near.bin
    arena.bin
    manifest.json
    transcript.txt
```

This supersedes any old workflow that assumes near player/projectile globals and the far OBJECT/GUARD/MAP arena share one segment.

## 5. New scenario-aware acceptance analyzer

Generated:

`n3d_gameplay_acceptance_pass8.py`

It reuses the corrected Pass-6 decoder and understands four acceptance modes.

### Forced close

```text
python n3d_gameplay_acceptance_pass8.py forced-close T0 T1 T2 T3
```

It locates an occupied door that transitions `0/2 -> 3`, then reports:

- collision bits on both VEC halves;
- exact geometry deltas from T1 to T2;
- whether the transition itself moved/damaged the overlapping player/guard;
- what changed by T3.

### Active projectile save/load

```text
python n3d_gameplay_acceptance_pass8.py projectile-load BEFORE AFTER
```

It compares per-slot:

- lifecycle;
- X/Y;
- frame/sequence;
- map pointer;
- absolute deadline;
- global clock;
- `deadline - clock`.

This directly answers the remaining projectile deadline rebasing/preservation question.

### Pickup boundary

```text
python n3d_gameplay_acceptance_pass8.py pickup BEFORE AFTER --field hp
python n3d_gameplay_acceptance_pass8.py pickup BEFORE AFTER --field ammo_plasma
```

It reports the player-field delta plus MAP/object changes, allowing accepted pickup and rejected-at-capacity contact to be distinguished without relying on HUD pixels.

### Generic diff

```text
python n3d_gameplay_acceptance_pass8.py diff BEFORE AFTER
```

This emits the complete tracked gameplay delta from the Pass-6 decoder.

## 6. Self-validation

The new capture script passes Python compilation.

The acceptance analyzer was run against the synthetic Pass-6 fixture and correctly detected:

- plasma ammo `60 -> 59`;
- one projectile X step;
- door `0 -> 3`;
- both door VEC collision bits becoming active;
- simultaneous player + guard occupancy with unchanged X/Y/HP at transition.

AND four-snapshot synthetic forced-close fixture additionally verified:

- exact 2-unit geometry detection;
- unchanged actor at T1;
- later T3 HP change being reported as and later outcome rather than falsely attributed to the door-transition helper.

## 7. Coverage after Pass 8

| Gameplay area | STATIC checked core | Original runtime parity |
|---|---:|---:|
| Player | **100%** | pending acceptance edge cases |
| Inventory | **100% Win16 / core mapped DOS** | pickup-boundary capture pending |
| Weapons | **100% checked core** | live cadence/input phase parity pending |
| Projectile | **100% checked static core** | save/load + cached-row captures pending |
| Enemy Spawn | **100% checked core** | boundary-map runtime tests optional |
| Guard AI | **100% checked core** | timing/order parity pending |
| Boss AI | **100% Win16 static core** | presentation/timing capture pending |
| Combat | **100% checked core** | runtime ordering edge cases pending |
| Damage | **100% checked arithmetic/core** | live simultaneous-event ordering pending |
| Runtime AI | **100% checked core** | live ordering pending |
| Enemy State Machine | **100% checked core** | runtime timing parity pending |
| Actor Scheduler | **100% checked static core** | exact live order/slow-frame parity pending |
| Object Runtime | **100% Win16 base core** | rare overlay/runtime cases pending |
| Physics | **100% checked static core** | occupied forced-close/corner runtime pending |
| Pathfinding / Navigation | **100% checked core** | occupancy/LOS edge captures pending |

### Aggregate interpretation

There is no longer and defensible broad gameplay algorithm that should be called "unknown" for the checked reference core.

With the correct high-level state is now:

- **STATIC Gameplay implementation closure: 100% for the checked core.**
- **Historical all-build parity: very high but not identical byte layout; keep version adapters.**
- **Original behavioral parity: not 100% until the original-game captures are run.**

To not convert the last line into and guessed percentage. The remaining work is measurement, not decompiler coverage.

## 8. Next decisive input

Run one original DOS V2.0 capture pair/set with the new MCP snapshot tool. The first highest-value sequence remains the occupied explicit-close T0/T1/T2/T3 case; after that, active projectile save/load and 99/100 pickup boundaries.