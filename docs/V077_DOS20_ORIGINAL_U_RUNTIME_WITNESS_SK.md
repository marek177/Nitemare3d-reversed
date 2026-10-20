# Nitemare 3D — renderer v0.77: five original DOS2 texture-U runtime frames

**2026-10-20 | Evidence: REAL ARCHIVED DOSBOX-X CPU EXECUTION. Pixel-perfect remake: STILL OPEN.**

## What was actually verified

The private user-owned original unpacked DOS v2.0 EXE and pre-existing DOSBox-X Advanced History N3DTRC01 CPU traces allow original wall texture-U to be recovered at actual original instruction returns. This is the original program's **measured per-column U**, not a C# or C++ projection approximation and not a fresh original DOSBox-X run in this pass.

SHA-256 original unpacked `N3D-E-20.EXE` (116606B):

`552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`

SHA-256 original `N3D_DOS20_RENDER_RUNTIME_20261019.zip`:

`26995d0ebf2e5e0bde8561b85d85ad6174278a2237b3c202c63444eec49f2207`

Actual load image: DOS2 image load-linear base `0x8240`. The FAR CALL at image `0x26A6` is relocated from `0x0C7D:070C` in unpacked EXE to `0x14A1:070C` in live guest RAM. The SHA-gated oracle explicitly validates this expected relocation and full bytes of the seven relevant executed instructions, rather than misclassifying genuine relocation as corrupted code.

| DOS v2.0 image offset | Observed register/action |
|---|---|
| `26A6` | original FAR call `CEDC`, VEC orientation argument |
| `26AB/26B0` | verified CEDC AX return, local 16-bit wall coordinate in SI |
| `26C9` | unadjusted `U` in SI, original IMG source frame width in AX; call `22CA` |
| `22D6` | original 28B VEC near pointer in SI and screen X in CX |
| `26CC` | returned AX from `22CA`, first finished U witness |
| `26CF` | `MOV SI,AX`; second matching finished U witness |

## New 1:1 reference corpus from authentic game

| Original captured session | Complete frames | Original full viewport U values | Original U edge fixes |
|---|---:|---:|---:|
| `1792437350-9-000` | **4** | 1,216 | 3 + 5 + 5 + 9 |
| `1792437554-9-000` | **1** | 304 | 1 |
| **Total** | **5** | **1,520** | **23** |

Each complete frame has **exactly screen x=8..311, 304 signed/integer raster columns**, with the original per-column U recorded after `22CA`. The caller's IMG width was **128** for all 1,520 records. The union of original observations covers VEC orientations **0,1,2,3**. A total of 1,808 original U call returns were parsed (288 additional returns are in two partial frames and not misrepresented as complete views).

Most returned U values equal the unadjusted U masked by `127`, but **23 do not**. Actual corrections: **16× −1 mod128, 5× +1 mod128 and 2× −2 mod128**. Observed boundary cases include `0→127`, `64→63`, `62→63`, `65→63`. Therefore dropping DOS routine `22CA` and using only `U & 127` is demonstrably inaccurate even if CEDC's perspective coordinate were otherwise correct. These 23 differences are direct original-game observations, NOT a comparison to the modern renderer.

Original complete U SHA-256 fingerprints (304 bytes per frame):

| Captured session/frame | Original U SHA-256 | Corrections screen X |
|---|---|---|
| 7350/0 | `3b8be6cc9002203c999b79134875d21aa5e62454a29842a6ca8899cc2f0487fc` | 101,166,249 |
| 7350/1 | `fc35c6e849ce0f9c9424d413a2b9a968b46e1bc5b2a1ef8351ead56d8803cfbf` | 79,115,116,146,217 |
| 7350/2 | `2dce095102a2e72b3fb59d98ebe13e7fdc1295419b9783913640c8171fce37e6` | 59,99,130,200,288 |
| 7350/3 | `536fdff61ed5d0e94f9d7a0b9cd176e50ac423e2aa50b175a5b86885ab3d0af8` | 37,80,81,113,138,172,184,261,266 |
| 7554/0 | `571f69e3baee78962f8655d795d688b5acd3a0abe7b8f19d21eaf6392bd4367c` | 101 |

Original file contents are **not checked into the GitHub repo**. The user's v0.77 ZIP artifact contains the five derived 304B U vectors, original-output CSVs (X, VEC pointer, orientation, before/after U and CPU event IDs), original-private replay tests and proof manifests; it does not contain EXE, MAP, IMG, entire trace, palette or VRAM data.

## How to repeat against your own original files

Tools: [original v0.77 U oracle](../tools/n3d_v077_dos20_u_witness.py), [numeric U diff](../tools/n3d_v077_original_u_diff.py).

```bash
python3 tools/n3d_v077_dos20_u_witness.py \
  --exe /private/N3D-E-20.EXE \
  --trace-zip /private/N3D_DOS20_RENDER_RUNTIME_20261019.zip \
  --session session-1792437350-9-000 \
  --out /tmp/n3d-u-v077
python3 tools/n3d_v077_dos20_u_witness.py \
  --exe /private/N3D-E-20.EXE \
  --trace-zip /private/N3D_DOS20_RENDER_RUNTIME_20261019.zip \
  --session session-1792437554-9-000 \
  --out /tmp/n3d-u-v077
```

**Tests:** local private original replay passed **13/13** Python tests including five expected 304B U hashes; GitHub's separate asset-free synthetic suite runs on Linux and Windows. A wrong source EXE, wrong trace SHA, mismatched return AX, bad source width or unexpected near-code site is rejected. A numeric original↔candidate U compare is not a game-state synchronization proof.

## What's still required for full 1:1

1. Instrument the **C++ DOS-native `N3DDos20WallMaterialBinding.hpp` perspective-U** (including frame ID, class, curtain flips and exact 16/32-bit overflow semantics) at the *same original frame and tick*. The observed original U sequence is now available as a rigorous 304-column reference for five views.
2. Produce a same-tick, same-EXE/data SHA authentic candidate frame manifest. Current original CPU U traces alone do not prove candidate scene state or final indexed framebuffer correctness.
3. On first differing U, inspect the original `CEDC -> 25DC -> 22CA` route and original actual VEC world/screen metadata, not patch one wall screen X.
4. After U is matched, verify source IMG texel indexes, V sampling, DOS shade, sprite/HUD order, and **64,000 indexed pixels + 768 DAC components with zero diff**.

**Current state: original U = MEASURED for five full frames; modern candidate U = NOT COMPARED; full pixel-perfect 1:1 = NOT VERIFIED.** Keep live `Raycaster.cpp` diagnostic DDA until a true paired acceptance passes.
