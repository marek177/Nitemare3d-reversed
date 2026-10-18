# Nitemare 3D RE MAX v0.41 — latest static evidence consolidation

**Repository update date:** 18 October 2026  
**Research inputs consolidated:** late 17 October audits through scheduler v0.54/v0.55 and cross-build/data v0.73–v0.76.  
**Method:** RE-first. Original binaries/assets were fingerprinted in the underlying audits, but this repository update ships only reconstructed source, tests and evidence summaries. **No original gameplay process, CPU chronology trace, framebuffer zero-diff or audio zero-diff is added here.**

## 1. Critical E1M9 correction: radio clears WALL, not OBJECT

The most important correction since v0.40 is a MAP-layer fix.

In audited Win16 1.3–1.10, the radio/special path stores a pointer to the **WALL byte** in `OBJECT+0x0C`. Its mode-0 write clears `ES:[BX]`, therefore it clears the WALL ID. The adjacent OBJECT byte remains intact unless another writer changes it.

For the E1M9 radio targets this means, locally:

```
before: WALL B7 / OBJECT 86,91,95
after:  WALL 00 / OBJECT 86,91,95
```

The older hypothesis that the radio activation itself erased the OBJECT ID and therefore suppressed projectile GUARD-property lookup until a mover restored it is wrong for these audited Win16 builds.

This reopens the projectile-hit reachability question: the OBJECT-layer property bit used by the projectile path is not automatically removed by that mode-0 write.

Win16 1.0 differs: the local mode-0 body does not contain the same WALL=0 write. That makes repeated activation a separate version-specific reachability candidate because a second activation can overwrite the saved group with the already borrowed group if no intervening writer prevents it.

## 2. E1M9 resource provenance is much stronger

The asset audit ties the E1M9 initial groups to the actual MAP/IMG alias topology:

- Frankenstein group 17
- Skeleton group 9
- Mrs. H group 5
- Dancers group 12

Across ten audited historical IMG.1 variants, the E1M9 map block and the Dancers 90-byte SEQDEF remain stable for the tested facts. The Skeleton `GUARD+0C==9` candidate therefore no longer depends on choosing one arbitrary IMG.1 offset set.

The E1M9 special initializer is now also cross-build constrained more tightly:

- classes `0x09/0x0B/0x0C` select descriptor word slots `+0x04/+0x24/+0x14`;
- the chosen word feeds `GUARD+0x00`, with its low byte feeding `OBJECT+0x03`;
- the old `OBJECT+0x04` group is saved in `GUARD+0x0C` before replacement by the class-`0x21` donor;
- the loader creates `OBJECT+0x0C/+0x0E` as a far map-cell pointer, and the segment word has relocation evidence in all 12 audited builds;
- `GUARD+0x08` stores the allocated OBJECT index.

The remaining P0 is therefore no longer “what did the initializer probably mean?” but the complete writer/read lifecycle and natural hit path.

## 3. Projectile clock compare is 32-bit, rearm is split 16+16

The projectile due check reads the clock as a 32-bit value, but the subsequent flight and impact deadline rearm reads low and high clock words with separate 16-bit instructions.

Under DOS RTC timing, an IRQ between those two reads can conditionally compose a mixed timestamp. The canonical static arithmetic witness is:

```
before IRQ clock: 0x0001FFFF
after IRQ clock:  0x00020000
low read before + high read after -> 0x0002FFFF
+ impact interval 50             -> 0x00030031
coherent post-IRQ + 50           -> 0x00020032
difference                        = 65535 clock units
```

This is a real instruction-level hazard, not a claim that the interrupt occurred during a captured game. IF/CLI/STI and actual interrupt delivery remain timing/reachability blockers.

## 4. E2M10 ordering is now tighter

The special collision path invokes visual effect 7 **before** incrementing the 16-bit hit counter and testing signed divisibility by 20.

For the twentieth-hit path the bounded ordering is:

```
palette effect 7
-> hit counter increment
-> signed IDIV-20 remainder gate
-> player transfer
-> possible nested scheduler
-> gameplay state transition
```

The current non-nested projectile movement stops after an accepted E2M10 collision and does not start another substep in the same movement invocation. The remaining duplicate-hit/reentry problem is therefore about a **separate nested pool invocation**, not a loop continuation inside the same movement call.

## 5. Nested scheduler tail mixes shared and local time state

DOS v2.0 does not keep every scheduler sample local to one invocation.

A nested scheduler can overwrite the global frame scratch. After returning from the projectile pool, the suspended outer scheduler uses the **latest global frame scratch + 1** for the next-frame threshold, but writes the legacy epoch from its own older stack-local snapshot.

Therefore a port that “cleans up” the scheduler into purely local per-call time variables can diverge from original reentrant semantics.

The v0.41 code encodes the bounded writer-order contract without claiming a naturally observed E2M10 trace.

## 6. OBJECT+0x18, GUARD generation and damage correspondence

The 12-build renderer/guard/damage audit narrows the projection-cache chain:

- a successful projection writes `OBJECT+0x18` from a local projected coordinate;
- a generation-gated weapon scan requires `GUARD+02/+04 == current frame generation`, then applies state filters/LOS;
- projectile proximity damage uses per-axis `abs(delta)<10` and does not have the same local generation-equality gate at the damage callsite;
- the damage producer uses the same projection base and forms the pre-class scalar as modulo-16-bit `8*(OBJECT+18 - projectionBase) + RNG%25`.

The global **last writer** of `OBJECT+0x18`, culling/stale-cache reachability, bulk LOAD aliases and every indirect writer remain P0.

## 7. Renderer/frame compositor additions

The newly integrated compositor reference records these DOS-local facts:

- 100 sprite slots × 18 bytes;
- initialization writes only the status byte at each 18-byte stride, not a blanket memset of the record;
- projected work marks a slot status 0;
- the compositor processes status-0 slots and marks them completed;
- DOS v1.7+ has the bounded lazy-load branch when the descriptor pixel pointer is missing; DOS v1.0 follows a different local path;
- the canonical DOS v2.0 frame direct-child list is preserved in code.

This is **not** the complete sprite rasterizer, clipping, transparency, image loader or VGA presentation pipeline.

A separate renderer audit also corrected the old synthetic n=513 concern for the tested 27-unit camera-distance region after orientation filters: the finite audited sweep peaks at 511 there. At distance 26 a valid local arithmetic witness above 511 still exists, so global reachability remains open.

For a valid 64-unit secret-panel edge, 32 movement updates reach the endpoint but reassert state 2; cleanup occurs on update 33. A render pass between those updates can therefore observe the still-active degenerate VEC state if the surrounding scheduler conditions allow it.

## 8. Pool-capacity and asset provenance update

Original constructor gates plus MAP data give these source maxima:

| Pool | Capacity | Source maximum | Reserve |
| --- | ---: | ---: | ---: |
| WORLD OBJECT | 350 | 323 | 27 |
| GUARD | 100 | 99 | 1 |
| Door/WALL controller | 64 | 62 | 2 |
| SECRET panel | 32 | 32 | 0 |
| PUSH/movable | 12 | 11 | 1 |

Important exact cases:

- E3M8 contains **32/32 SECRET** panel candidates. A 33rd construction attempt is the error branch; the shipped source data itself fills the pool exactly.
- E2M10 contains **60/64** dynamic wall-pair controller candidates under the original wall-class property gate.
- E2M2 reaches 99 GUARD and 62 door-controller source candidates simultaneously.
- E1M8 reaches 11/12 PUSH candidates.

DOS and Win16 SECRET/door records are not ABI-identical: DOS uses 14-byte SECRET / 18-byte door records, while Win16 uses 22-byte records for both audited families. A single modern normalized struct must not be justified from stride equality assumptions.

## 9. DOS/Windows asset differences

For the specific fingerprinted `nitemare.zip` pair:

- E1M1 has 20 differing OBJECT bytes between DOS and Windows while the WALL layer and header are identical;
- six additional GUARD placements appear in the Windows E1M1 data (33 DOS vs 39 Win);
- E1M2–E1M11 and the audited MAP.2/MAP.3 blocks match for this pair;
- across six IMG wall/object banks, absolute offsets differ but the audited alias-sharing partition has zero mismatched alias pairs.

Therefore runtime resource ordinal values must be derived from the **matched MAP+IMG pair**, not treated as universal constants copied across distributions.

## 10. Current RE-first frontier

The known frontier is larger but better classified. Highest-value unresolved work remains:

1. E1M9 legal route and accepted hit: key/door/secret/radio/UI/cadence/projection/lookup chain.
2. Full `GUARD+0x08`, `GUARD+0x0B/+0x0C`, `OBJECT+0x0C/+0x0E`, `OBJECT+0x18` writer/alias census.
3. Projectile state/deadline/selector lifecycle across nested callbacks and any genuine second pool entry.
4. Complete scheduler IF/IRQ/clock/deadline writer graph.
5. DEMO seed=1 total RNG order, including render, animation, automap, GUARD and audio consumers.
6. Weapon FSM 0–3, especially Multi Plasma and full-pool/ammo behavior.
7. Door/remote/secret state machines and first-passable tick.
8. Full renderer pipeline to 64,000-byte indexed framebuffer + palette/page zero-diff.
9. SAVE/LOAD post-restore first tick and cross-ABI pointer/deadline reconstruction.
10. WORX/audio hardware timing after static callback closure.

The v0.76 research register currently tracks 38 known frontier items (21 P0, 14 P1, 3 P2). That is a working evidence set, not a proof that no additional unknown code exists.

## 11. Repository additions

- `src/re/N3DV041LatestStaticEvidence.hpp`
- `src/re/N3DV041FrameCompositor.hpp`
- `tests/v041_latest_static_evidence_test.cpp`
- `tests/v041_frame_compositor_test.cpp`
- `tools/n3d_v041_latest_static_models.py`
- `tests/test_n3d_v041_latest_static_models.py`
- `docs/V041_REMAX_LATEST_STATIC_CONSOLIDATION.md`
- `docs/V041_STATIC_FACTS.csv`
- README / DISCOVERIES / CMake / CI updates

No parity percentage is raised by this packaging alone.
