# Nitemare 3D RE MAX v0.42 — 18 October static sync

Repository update: 18 October 2026.
Evidence basis: static reports produced after repository v0.41, especially the 12-build pool/alias v0.59 audit, SAVE/LOAD v0.77, Win16 queue scheduler v0.57, Win16 import correction v0.78, and incoming-damage/feedback v0.79.
Boundary: all new conclusions below are static/local unless explicitly stated. No original gameplay process was executed. No framebuffer or audio zero-diff is claimed.

## 1. Cross-build incoming damage order
DOS 1.0 through 1.9 check protection/incompatible game-state conditions before the incoming-damage calculator. If that local gate returns, the class-dependent calculator and its RNG draw are not reached.
DOS 2.0 and all five audited Win16 builds call the calculator before those gates. A nonzero calculated result arms the feedback timer to 3, after which protection can still preserve HP.
Audited RNG branches: class 08 mask 7; class 09/0A mask 15; class 11..14 mask 31.

## 2. Damage feedback timer
The signed feedback timer at player block +0x26 is reconfirmed. Local sequence: 3->2 selector4, 2->1 selector4, 1->0 selector4, 0->-1 selector3, then inactive through this branch. It is serialized inside the 94-byte player block for DOS2/Win16.

## 3. SECRET SAVE/LOAD codec
SAVE always writes 32 bytes but locally initializes only N active panel-state bytes. If N<32 the local tail is not explicitly initialized. LOAD reads 32 bytes but restores only N active panel records, zero-extending each byte to a 16-bit state word.
The surrounding 32-byte I/O caller checks AX sign only, not AX==32; lower CRT/I/O short-read/write behavior remains open.

## 4. Door LOAD prefix preservation
DOS: 64 records x 18 bytes and first 8 live runtime bytes preserved/reapplied. Win16: 64 x 22 bytes and first 12 bytes preserved/reapplied. In both cases the remaining 10 bytes come from the serialized record.

## 5. Pool-family correction
Correct families: DOS dynamic wall 64x18 and class-3 geometry 32x14; Win16 dynamic wall 64x22 and class-3 geometry 32x22. Similar +08/+0C write shapes do not prove identical record families.
All 62 previously ambiguous selected writer sites were reclassified to bounded local families/operations.

## 6. OBJECT map-pointer producer graph
Two OBJECT map-pointer update routines now have 72 direct verified call edges across 12 builds: 60 to coordinate/map-binding recalculation and 12 to movement transfer. Indirect calls, bulk copies and pointer aliases remain open.

## 7. Win16 E2M10 queue consumer
The first message is displayed during enqueue/setup. On accepted mode-4 ACK the count is decremented. If records remain, the path forces render/HUD/present before displaying queue[countAfter]. Remaining records therefore appear in descending stored index order. The final ACK ends message mode without the intermediate forced-present call.
A local count==0 underflow edge exists, but natural reachability is not proven.

## 8. Win16 timing import relocation correction
For pre-relocation FAR CALL placeholders, the relevant NE import relocation is at CALL+1, not CALL+3. Audited timing imports use MMSYSTEM ordinals 604/605/606/607 and USER ordinal 13. Human-readable API names come from matching historical exports; ordinal evidence remains primary.

## 9. Current RE-first frontier
1. Complete GUARD/OBJECT writer and alias closure.
2. Weapon FSM 0–3 and Multi Plasma.
3. Projectile FB–FE lifecycle across genuine second nested pool entries.
4. DEMO seed=1 total RNG order.
5. Scheduler/IRQ/clock exact ordering.
6. SAVE/LOAD first post-restore frame, pointer reconstruction and short-I/O/error semantics.
7. Door/remote/SECRET first-passable tick and VEC/MAP synchronization.
8. Full indexed-framebuffer/palette zero-diff pipeline.
9. Win16 modal/message-pump/import callback interleaving.
10. WORX/audio hardware timing after static callgraph closure.

No project-wide parity percentage is increased by this repository sync alone.

## 10. Repository additions
- src/re/N3DV042Oct18Closures.hpp
- tests/v042_oct18_closures_test.cpp
- tools/n3d_v042_oct18_models.py
- tests/test_n3d_v042_oct18_models.py
- docs/V042_REMAX_OCT18_STATIC_SYNC.md
- docs/V042_STATIC_FACTS.csv
- README / DISCOVERIES / CMake / CI integration
