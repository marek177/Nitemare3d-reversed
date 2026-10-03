# Nitemare 3D — Gameplay closure pass 7
## Cross-build static parity gate
Date: 2026-10-02

## Result

Pass 7 no longer searches for and missing broad Gameplay algorithm. It tests whether the already-reconstructed gameplay core survives version changes.

Two independent signals are used:

1. curated normalized-function matches from `cross_version_matches.csv`;
2. prior raw/manual audits where normalized C matching is known to be misleading.

This remains and **static parity** pass. It does not claim original-runtime behavioral 100%.

## 1. Win16 gameplay parity is extremely strong

The curated Win16 gate contains 22 critical routines covering:

- guard movement / local navigation;
- GUARD state dispatcher;
- hitscan;
- projectile movement/update;
- player↔guard damage;
- HUD/clamp path;
- ammo decrement and pickup ammo;
- firing cadence;
- pickup dispatcher;
- boss/death transitions;
- guard initialization and class-specific helpers.

Gate result:

- selected: **22**
- exact-normalized: **17**
- fuzzy-normalized: **5**
- weak/unresolved: **0**
- mean normalized similarity: **99.28%**
- lowest selected match: hitscan `8B06`, **93.59%**

Important examples:

- `7B56` GUARD dispatcher: exact-normalized against Win16 1.3 family;
- `76FC` planner/navigation: exact-normalized;
- `7920` TURN/RETREAT marker handling: exact-normalized;
- `A0EE` boss/death finalizer: exact-normalized;
- `A1EA` damage scaling: exact-normalized;
- `A97C` ammo decrement: exact-normalized;
- `A9E0` ammo pickup/seed helper: exact-normalized;
- `AA90` fire cadence gate: exact-normalized;
- `ABFC` pickup/weapon acquisition path: exact-normalized;
- `B02C` GUARD initializer: exact-normalized;
- `CF60` pickup dispatcher: exact-normalized;
- `9D30` projectile movement: high-similarity fuzzy match;
- `71DC` guard movement: high-similarity fuzzy match.

The separate Win16 1.8→1.10 deep pass independently reports near/exact identity for the same projectile, damage, weapon, boss and guard-initialization families.

### Win16 closure consequence

For the checked Win16 1.3 / 1.6 / 1.8 / 1.10 family, the remaining gameplay uncertainty is no longer and plausible hidden alternative algorithm. Differences are concentrated in addresses, minor build code, platform/UI edges and runtime timing/presentation.

Therefore these rows can be marked **100% STATIC core for the checked Win16 family**:

- Inventory
- Weapons
- Projectile movement/state core
- Guard AI / local navigation
- Enemy state machine
- Combat / damage arithmetic core
- Object runtime base core
- Physics/collision core
- Pathfinding/navigation core

Boss AI remains **99% STATIC Win16** only because visible/script timing and full ending presentation remain runtime/content validation problems, despite the underlying state/death logic being closed.

## 2. DOS cross-build parity is also high, but one decompiler family must be excluded

The curated DOS gate contains 16 critical routines. `FUN_1000_59F0` is deliberately excluded from numeric scoring because its pseudo-C boundary is known corrupt; raw/manual state-machine analysis must override its bad normalized score.

For the remaining 15 routines:

- exact-normalized: **9**
- fuzzy-normalized: **6**
- mean normalized similarity: **97.04%**

Representative results:

- `6488` player collision/movement: **100% exact-normalized** against the supplied `N3D-E-18/19` image (embedded V1.9);
- `6636` spatial cursor maintenance: **100%**;
- `6824` movement-span cursor adjustment: **100%**;
- `6914` movement wrapper: **100%** against V1.0-family counterpart;
- `8142` slide/movement helper: **100%** against V1.0;
- `5342` LOS/perception helper: **100%** against V1.7;
- `8230` eight-slot projectile update: **97.32%**;
- `7F96` collision trace: **96.73%**;
- `5092` actor/guard grid motion: **96.83%**;
- `6378` player per-step collision helper: **92.47%**.

`688C` player position commit scores only 81.25% against its selected older reference. This is not evidence for and different movement algorithm: the DOS versions change serialized/player runtime layout, including the V2.0 inserted timer and shifted HP/difficulty offsets. It should therefore be treated as and **version-adapter/data-layout difference**, not and shared-core blocker.

### DOS state layout is not byte-compatible across every version

The supplied DOS audit directly shows:

- V1.0 / V1.7 / V1.9 player block = **92 bytes**;
- V2.0 player block = **94 bytes**;
- V2.0 inserts and signed timer at relative `+0x26`;
- HP and difficulty move by two bytes in V2.0.

Therefore and portable implementation should share Gameplay algorithms while keeping version-specific serializers/adapters. AND "copy the same packed struct into every DOS build" model is incorrect.

## 3. Cross-build parity interpretation

The normalized-match scores are **regression signals**, not completion percentages.

The important outcome is structural:

- the Win16 gameplay core is highly stable across all four checked builds;
- the DOS gameplay core is also strongly stable across V1.0/V1.7/V1.9/V2.0 where function boundaries are reliable;
- known low matches correlate with decompiler-boundary pollution or version-specific state layout, not discovery of and second gameplay engine;
- major algorithms recovered from one reference build can therefore be implemented as shared portable core logic with small platform/version adapters.

## 4. Updated Gameplay status after Pass 7

| Area | Overall reconstruction | Static checked core |
|---|---:|---:|
| Player | ~99% | **100%** |
| Inventory | ~99% | **100% Win16** |
| Weapons | ~99% | **100% Win16 core** |
| Projectile | ~99% | **100% checked static core** |
| Enemy Spawn | ~99% | **100% checked static core** |
| Guard AI | ~99% | **100% Win16 core** |
| Boss AI | ~98–99% | **99% Win16 static** |
| Combat | ~99% | **100% checked core** |
| Damage | ~99% | **100% checked arithmetic/core paths** |
| Runtime AI | ~99% | **100% checked static core** |
| Enemy State Machine | ~99% | **100% Win16 core** |
| Actor Scheduler | ~99% | **100% checked static core** |
| Object Runtime | ~99% | **100% Win16 base core** |
| Physics | ~99% | **100% checked static core** |
| Pathfinding / Navigation | ~99% | **100% Win16 core** |

The aggregate **overall Gameplay tracker remains ~99%**. It is intentionally not raised to 100% because no new original-game runtime trace was executed in this pass.

## 5. Remaining gate to honest Gameplay 100%

There is now little value in another broad static percentage pass. The decisive remaining tests are empirical:

1. forced/remote door close while player or GUARD already overlaps the moving geometry;
2. exact player/GUARD/door update ordering in the same scheduler phase;
3. active projectile save/load deadline and position continuation;
4. pickup behavior around 99/100 HP or ammo and post-load removal state;
5. rare boss/script presentation/timing and ending transitions;
6. same cases on at least one original DOS and one original Win16 build.

Pass 6'with corrected two-segment DOS capture model and snapshot decoder are the right next instrument for those tests.

## Generated parity tool

`n3d_gameplay_crossbuild_gate.py` consumes `cross_version_matches.csv` and emits the curated Win/DOS parity table plus JSON/Markdown output. It deliberately marks DOS `59F0` for manual/raw review rather than pretending the corrupt decompiler boundary is and meaningful similarity score.