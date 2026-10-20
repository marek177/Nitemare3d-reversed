# Nitemare 3D — DOS2 texture-U 22CA: 1,520 original CPU results exact (v0.78)

**20 October 2026 · Evidence: ORIGINAL_RUNTIME_BOUNDED + ORIGINAL_8086_STATIC + NATIVE_CXX20.**

## What was actually closed

The full original **340-byte** DOS v2.0 routine at unpacked load-image offsets `22CA..241D` was independently translated into [`N3DDos20TextureUEdge.hpp`](../src/re/N3DDos20TextureUEdge.hpp). The original 16-bit signed subtraction, near-endpoint comparisons, world-axis length, class-2 special cases, signed `NEG` wraparound, equality branches and final `AND (width-1)` remain explicit. It is **not** the CEDC perspective projector.

The native DOS translation was checked against the **actual original return AX** after `22CA` in the previously recovered five complete DOS2 304-column viewports. Input values were recovered from original CPU register prestates within `22CA`, correlated by original event ID with [v0.77 original U records](V077_DOS20_ORIGINAL_U_RUNTIME_WITNESS_SK.md).

| Evidence | Result |
|---|---:|
| Original 304-column viewport frames | **5 / 5** |
| Original DOS2 `22CA` return U values | **1,520 / 1,520 exact** |
| Nontrivial original boundary corrections | **23 / 23 exact** |
| Synthetic DOS-native vs independent Win16 `6422` combinations | **28,288 / 28,288 exact** |
| Synthetic nontrivial U corrections in cross-build test | 3,640 |
| Deliberately mutated original x=101 return | **FAILED, as expected** |
| Original-vs-remake CEDC *unadjusted* perspective U | **NOT VERIFIED** |
| Original-vs-remake entire 64,000 indexed framebuffer and 768 DAC | **NOT VERIFIED** |

### Pinned original references

- Original unpacked `N3D-E-20.EXE`, 116,606 bytes: SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.
- Original archived `N3D_DOS20_RENDER_RUNTIME_20261019.zip`: SHA-256 `26995d0ebf2e5e0bde8561b85d85ad6174278a2237b3c202c63444eec49f2207`.
- Original `22CA..241D` code bytes, 340/340 matching the EXE: SHA-256 `9c336cc655e850aa896451c94827b501486112cdbef90df1a02b5826447f17de`.
- Private derived 1,520-row effective-input CSV, **not stored in this repo**: SHA-256 `724151a85a119c40b3231b7d597aceb1958388c8136453cfd1ac7ea0b4b757ac`. Event IDs, screen X, original VEC owner, original source U and final U, signed endpoint distances and original length are checked against the original trace-derived v0.77 oracle.
- Of the 1,520 calls, 148 belong to the special class-2 orientation family; all orientations `0..3` occur. Observed original corrections modulo128: **16×−1, 5×+1, 2×−2**.

## Original instruction landmarks

| DOS2 image | Original operation |
|---|---|
| `22D8..22DE` | signed `screenX - VEC.screenX1 < 8` |
| `22E9..22F4` | signed `VEC.screenX2 - screenX < 8` |
| `2309..230D` | `VEC.flags & 0x08`: bypass special edge correction |
| `231B..232A` | signed world-axis length with original word wrapping |
| `232E..23B4` | class-2/orientation-0,3 specific cases |
| `23B4..2412` | remaining orientation-dependent branches |
| `2414..2418` | final `(width - 1) & signedU` |

The current original corpus uses physical IMG source width **128**. The `VEC.flags & 0x08` bypass is **statically reconstructed**, but is not claimed to have been executed in those five full frames. Synthetic tests cover that branch and widths 64/128.

## Code and test placement

- [`src/re/N3DDos20TextureUEdge.hpp`](../src/re/N3DDos20TextureUEdge.hpp): independently reconstructed DOS2 22CA model, no floating-point or DDA.
- [`src/re/N3DDos20WallMaterialBinding.hpp`](../src/re/N3DDos20WallMaterialBinding.hpp): the **DOS-native** CEDC→22CA path now calls the new `texture_u::correctBounded`; the Win16 cross-build candidate is still separate.
- [`tests/dos20_texture_u_edge_test.cpp`](../tests/dos20_texture_u_edge_test.cpp): 28,288 synthetic cases (including signed limits, orientation, class and flag variants) plus **opt-in** 1,520-row original-private runtime verification.
- [CI workflow](../.github/workflows/renderer-v078-original-u-edge.yml): C++20/CTest on Linux and Windows; strict GCC/UBSan synthetic check on Linux; no private original assets distributed in GitHub.
- [`cmake/RegressionTests.cmake`](../cmake/RegressionTests.cmake): opt-in user `N3D_DOS20_U_ORIGINAL_CSV` reference for original-data CTest.

### Private evidence replay (user-owned data only)

```bash
cmake -S . -B build-v078 -DN3D_ENABLE_SDL3=OFF \
  -DN3D_DOS20_U_ORIGINAL_CSV=/private/original_22ca_effective_inputs_private.csv
cmake --build build-v078 --target n3d_dos20_texture_u_edge_test
ctest --test-dir build-v078 -R 'n3d_dos20_texture_u' --output-on-failure
```

**The original-private CSV, five U buffers and the full proof report are delivered in the user artifact ZIP rather than checked into the public repository.**

### Scope and next divergence

This is **a bounded proof of the 22CA correction stage given original unadjusted U**, not a proof that the modern C++ CEDC generates that unadjusted U. The next meaningful parity job is to recover the same-tick original DOS2 camera/DS and CEDC input values for the five original original-U runs, compute candidate unadjusted U without borrowing the original CEDC outputs, then compare original IMG/frame/U/V/shade and the synchronized 64,000 indexed pixels + 768 DAC components.

**Production `src/renderer/Raycaster.cpp` and `src/main.cpp` remain unchanged diagnostic DDA; pixel-perfect whole-frame 1:1 remains OPEN.**
