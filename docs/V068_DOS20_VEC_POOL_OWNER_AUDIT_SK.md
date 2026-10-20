# Nitemare 3D — DOS v2.0 VEC pool / owner audit, v0.68

Date: 2026-10-20. Evidence: **ORIGINAL_RUNTIME_BOUNDED**, offline analysis of an existing original DOS2 64 KiB global/stack snapshot. **NOT original-vs-remake pixel parity**, and no new DOSBox-X gameplay execution in this pass.

## Source fingerprints

- User's `N3D_DOS20_RENDER_SCALED_COLUMN_20261019.zip` SHA-256: `512521df5ddcafd623c65fe38b1e099bbe7e2d22f0dca7dabaf16e0272aa3e3b`.
- `proof/stack_segment.bin` SHA-256: `1878c03fbd7f40d06dd87691e608d6143c16de0dcb347894d0e0bd6c2a49d98e`, 65,536 bytes.
- Packed DOS2 `N3D.EXE` referenced in earlier original audit: `a3fa02335e1d8bc531918f3bfaa66217aef65c81e562a2fdf1c749be652ca485`.

## Recovered original DOS2 VEC-list layout

| Orientation | Count word | Pointer array (333 WORD) | Live records | Primary monotonic key |
|---|---|---|---:|---|
| 0 | `DS:57FA` | `DS:5802` | 148 | world Y1 |
| 1 | `DS:57FC` | `DS:5A9C` | 144 | world Y1 |
| 2 | `DS:57FE` | `DS:5D36` | 152 | world X1 |
| 3 | `DS:5800` | `DS:5FD0` | 148 | world X1 |

Every **592/592** live pointer is valid, unique, and references an axis-aligned, matching-orientation, 28-byte VEC. The 592 records are contiguous in this capture: first `0x62AC`, last `0xA350` (28-byte stride). All unused array tail pointers are zero. Secondary-key monotonicity is not proven: **14 inversions within tied primary coordinates** mean a guessed two-key sort cannot be substituted.

- VEC `+05` flag bytes: `07` ×574, `0B` ×12, `2B` ×6.
- VEC `+06` render classes: `01` ×542, `02` ×25, `09` ×1, `0D` ×2, `11` ×2, `19` ×2, `39` ×2, `3F` ×8, `40` ×8.
- **304/304** original viewport owner columns at `DS:4564` reference the recorded VEC lists; **9/9** owner runs reference valid original **18B** DOS span records starting `DS:4D6E`.

This extends v0.67 (which verified **36/36** projected endpoint words and **162/162** original span bytes for the same snapshot). The counts prove *one captured complete VEC-pool state*, **not** a newly run MAP-to-VEC construction.

## Critical negative geometric control: 300/304, not 1:1

A separate integer/rational front-facing nearest-segment intersection computes the same wall as the original **in 300 of 304 columns**. Four edge columns remain different:

| Screen x | Original owner | Geometric owner |
|---:|---|---|
| 18 | `89B8` | `899C` |
| 40 | `899C` | `7F38` |
| 175 | `9994` | `7F70` |
| 269 | `9978` | `99CC` |

This is a *control experiment*, not the active preview DDA implementation. No four-pixel patch has been applied. Investigate the original DOS2 `0x1021E` visibility traversal, `0xFEFA` conflict logic, endpoint inclusivity and stable-tie ordering. Do not guess a raycast replacement.

## Code / validation

The separately distributed **v0.68 evidence package** contains:

- `src/renderer/Dos20VecPoolEvidence.hpp` (read-only C++20 checked census; not live renderer);
- `tools/n3d_dos20_vec_pool_oracle.py` (Python stdlib SHA-gated oracle and geometric negative control);
- `tests/dos20_vec_pool_evidence_test.cpp` and `tests/test_n3d_dos20_vec_pool_oracle.py`;
- idempotent, conflict-refusing installer (does not touch `Raycaster.cpp`/`main.cpp`);
- `v068_pool_census.json`, test logs and SHA manifest. No commercial EXE/MAP/IMG or 64 KiB original dump.

**Locally verified:** CMake/CTest **79/79**, Python **13 synthetic + 1 original** checks, C++20 **UBSan** original run, install/second-run/conflict guards. The **v0.68 package is not integrated into main's active rendering path**.

## Open 1:1 parity gates

1. Regenerate the 592 original VECs from the **corresponding original MAP.1** with original map/EXE fingerprints. No MAP image is available in the evidence ZIP.
2. Instruction-exact DOS2 `0x1021E` list traversal / `0xFEFA` owner comparison, including the four disputed columns and more snapshots.
3. Full DOS2 wall-U/V sampling, shading, active IMG frame selection, moving doors, sprite/HUD composition.
4. Deterministic **original vs. reconstructed** framebuffer `64,000` indexed bytes **plus** `768` DAC bytes with **zero mismatch**.

The runnable `src/renderer/Raycaster.cpp` remains deliberately labeled diagnostic DDA preview. **Pixel-perfect 1:1 remains open.**
