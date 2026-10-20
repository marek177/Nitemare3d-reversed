# Nitemare 3D — DOS v2.0 experimental 304-column owner/span wall pipeline (2026-10-20)

**Status: IMPLEMENTED + SYNTHETIC C++20 CI TESTED.** This is **not** a verified full-scene original-vs-remake 1:1 pixel renderer. The active production `src/renderer/Raycaster.cpp` remains a diagnostic DDA preview; `src/main.cpp` is unchanged.

## Implementation: first actual DOS owner/span → wall raster connection

- [`src/re/N3DDos20SpanWallPipeline.hpp`](../src/re/N3DDos20SpanWallPipeline.hpp) accepts a complete **65,536-byte** original-style DOS2 renderer segment at the `post-span` checkpoint, plus the active VEC count and selected VGA write page.
- Reads `DS:4562` remaining/unowned count, `DS:4564` **320 WORD** column owner pointers (only x8..311 are drawn), `DS:4D64` span count (maximum 50), and `DS:4D6E` **18-byte** active DOS span records.
- Validates all 304 screen columns are covered contiguously by the spans, every pointer is an aligned valid 28-byte VEC from the `DS:62AC` pool, and each owner column references its span owner.
- Decodes each span's `+0A DWORD` **signed 16.16 slope** and `+0E DWORD` **current 16.16 phase**, advances the phase separately for every screen X and uses the **signed** high word as YQ4 displacement.
- Calls the existing [`N3DDos20IndexedWallColumn.hpp`](../src/re/N3DDos20IndexedWallColumn.hpp) for each prepared wall column. All columns' sources and destination regions are checked before any framebuffer/VRAM write.
- **Exact IMG face/U and shade/XLAT selection are still required from an external resolver.** No guessing using DDA, nearest grid intersection, or arbitrary half of 128×64 texture. The resolved source texture column and XLAT table are copied into the plan for safe rendering.
- The module does **not** independently regenerate MAP→VEC, perform CAB8 projection, run FEFA visibility or 213E span creation. Those are upstream unresolved/integration stages.

## Exact DOS vertical geometry recovered before this pass (2500 → 1A2E)

At each column, take `signed16(spanPhase >> 16)`, center YQ4=1280 and center Y=80:

```text
projectedBottomY = signed_arithmetic_shift_right(1280 + displacementQ4, 4)
heightIndex = 2 * (projectedBottomY - 80) + 1
verticalSourceStep16_16 = floor(0x400000 / heightIndex), n=1..511

if projectedBottomY < 155:
    firstY     = projectedBottomY - heightIndex
    pixelCount = heightIndex + 1
    sourceStart16_16 = 0
else:
    firstY     = 4
    pixelCount = 152
    sourceStart16_16 = floor(floor((heightIndex - 152) * 64 * 65536 / heightIndex)/2)
```

**Runtime anchored identity:** first E1M1 wall column x=8: phase `0x014B800F` → signed displacement **331** → bottomY **100** → n **41** → firstY **59** → **42 pixels** → step **`0x00018F9C`**. This matches the recorded DOS2 raster writer `097A:0599..05D5`. Earlier offline replay had 42/42 matching original writes; this new code is validated by *synthetic C++ fixtures* until an additional original snapshot replay is performed.

The culling or unsupported n>511 branches are **fail closed**; they are not used to claim general reachability of all game camera states. For clipped walls, the recovered reciprocal and clipped source-start table arithmetic is kept integer-only.

## Test coverage

[`tests/dos20_span_wall_pipeline_test.cpp`](../tests/dos20_span_wall_pipeline_test.cpp) supplies two synthetic original-layout memory fixtures:

- **1 span × 304 owned columns**: source phase 331 Q4, 42-pixel vertical samples on every x, exact `x=8` sampled row placement and VGA plane/page addressing;
- **9 spans × 304 columns**: independent 28B VEC identifiers, 16-bit owner pointers and 18B span data, per-span projected wall heights and 304-column coverage;
- **Signed span slope (+1/-1 Q4 per x)**: actual fractional phase advancement over 304 columns, not a repeated single-column fixture;
- **Clipped wall case**: projected bottomY 157, n=155, firstY4, count152 and nonzero original clipped-start fraction;
- **128×64 IMG**: preserves both complete 64×64 faces; wall palette index `0x1F` is written, unlike sprite transparency;
- **Negative tests**: owner mismatch/hole, span overflow, invalid near pointer, missing/invalid texture U, invalid buffer length/VGA page and no partial framebuffer writes even after plan mutation.

An optional private original-input test accepts a genuine `proof/stack_segment.bin` as CLI argument. It expects **9 original spans, 304 owner columns**, and the original x8 42-pixel vertical geometry; it does not incorporate or publish the original game data.

```bash
cmake -S . -B build-v075 -DN3D_ENABLE_SDL3=OFF -DCMAKE_BUILD_TYPE=Debug
cmake --build build-v075 --config Debug --target n3d_dos20_span_wall_pipeline_test
ctest --test-dir build-v075 -C Debug -R '^n3d_dos20_span_wall_pipeline_test$' --output-on-failure

# Optional user-owned original 64KiB capture:
./build-v075/n3d_dos20_span_wall_pipeline_test /private/stack_segment.bin
```

CI workflow [`renderer-v075-span-wall-pipeline.yml`](../.github/workflows/renderer-v075-span-wall-pipeline.yml) compiles and tests on Linux and Windows; no private EXE, IMG, MAP, memory snapshot or texture archive is distributed in the repo.

## Precise remaining blockers

1. **Match original dos2 IMG/frame/physical-U and shade remap** for each of 304 columns, including classes 2/3F/40, animated/moving/paired doors, then feed the explicit material callback.
2. Upstream **MAP→592 VEC → CAB8 projection → FEFA selection → 213E span creation** must be generated from the candidate runtime, not imported from original snapshot.
3. Use [v0.72 Stage Frame Gate](../tools/n3d_v072_stage_frame_gate.py) with one **synchronized original/candidate tick**, manifest, active IMG/PAL and saved VEC/owner/span data. The first differing pixel then drives original sample-phase/U/source-frame/shade correction.
4. Add DOS2 background, sprite `0x1F` transparency/occlusion, HUD, page-flip and palette phase in their original draw order.
5. **Acceptance remains unchanged:** exact **0/64000 differing indexed pixels** + **0/768 DAC components** across a documented scenario corpus before replacing DDA.

**Proof vocabulary:** `original runtime bounded` = already captured E1M1 x8 and original 9 span memory facts; `synthetic native integration` = these new CI-tested C++ consumer tests; `pixel-perfect original↔remake` = **NOT YET VERIFIED**.
