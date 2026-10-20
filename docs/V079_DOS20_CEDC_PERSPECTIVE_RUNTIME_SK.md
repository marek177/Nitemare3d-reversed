# Nitemare 3D — DOS v2.0 original CEDC -> 25DC perspective-U proof (v0.79)

**20 October 2026. Evidence: archived original CPU instruction/operand replay + independently tested C++20. Not original-vs-remake pixel-perfect framebuffer parity.**

## Original source fingerprints

- Exact unpacked DOS2 N3D-E-20.EXE, 116,606 B: SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.
- Earlier real DOSBox-X CPU trace archive: SHA256 `26995d0ebf2e5e0bde8561b85d85ad6174278a2237b3c202c63444eec49f2207`.
- DOS2 executable-image CEDC..CFB0 (213 B): SHA256 `0be64391d8b1fe22990a9f14401c3270b6f4a96f7f6330895123215d06c74402`.
- Load image base in the two captured sessions: `0x8240`; MZ file offset = image offset + `0x200`. The extractor validates the **full bytes of executed instructions**, not 16-byte prestate lookahead. Far-call relocation at `0x26A6` is explicitly checked.
- No new original emulator execution occurred during this v0.79 offline pass.

## Original CEDC dispatch, all four runtime branches covered

| DS:415C selector | Orientation | Numerator before final signed IDIV | Original runtime calls |
|---|---|---|---:|
| nonzero | 0/1 | `screenTerm + product32` | **1,030** |
| nonzero | 2/3 | `verticalTerm - product32` | **474** |
| zero | 0/1 | `verticalTerm - product32` | **187** |
| zero | 2/3 | `product32 - screenTerm` | **117** |
| **Total** | | | **1,808** |

Where `screenTerm = IDIV_s32(signed32_low((signed16(screenX-centerX))*DS:368A), spanYQ4)` and `verticalTerm = IDIV_s32(DS:3686, spanYQ4)`. Signed 32-bit intermediate additions/subtractions wrap, IDIV truncates toward zero, and the original caller consumes AX's low 16 bits. Final divisor is DS:41B4 (cosine) when selector is nonzero, otherwise DS:41B2 (sine). Division faults are rejected by the host model.

### Measured exact results

| Original stage | Measured |
|---|---:|
| CEDC intermediate / quotient / AX result | **1,808 / 1,808 exact** |
| Caller 25DC raw U before 22CA | **1,808 / 1,808 exact** |
| Independently captured caller 16x16 IMUL at image 2643 | **1,804 / 1,804 available exact** |
| Independently captured caller local/world offset at 2603/2620 | **1,804 / 1,804 available exact** |
| Original caller executed NEG SI | **1,172** |
| Linked pre-22CA CPU returns from five complete 304-column frames | **1,520 / 1,520 exact** |
| Original 22CA nontrivial boundary corrections | **23** |

Four early calls started before the span-setup IMUL and world-local writer were inside the trace; their caller inputs are derived from original intermediate states and explicitly distinguished from the 1,804 directly witnessed cases.

Private derived 1,808-row operand CSV SHA256: `1db25ccff303dafd2b87d168629af21c10d1dec17e7f6eb5031eb5d4edcbc220`. The v0.78 1,520-row original 22CA CSV SHA256: `724151a85a119c40b3231b7d597aceb1958388c8136453cfd1ac7ea0b4b757ac`. Both private evidence files and the original archive-to-CSV extractor are distributed in the user ZIP, **not** committed to GitHub.

## Code integrated in the repository

- [DOS2 CEDC integer projection](../src/re/N3DDos20CedcProjection.hpp): original four-way signed 16/32 math, wrap, IDIV and explicit unsupported/fault cases.
- [DOS-native material binder](../src/re/N3DDos20WallMaterialBinding.hpp): delegates CEDC to the new native model; then applies 25DC's 16-bit local/NEG followed by the previously original-confirmed [22CA edge-U](../src/re/N3DDos20TextureUEdge.hpp).
- [C++20 CEDC tests](../tests/dos20_cedc_projection_test.cpp): synthetic overflow, signed division, four branches and **opt-in** private original CPU CSV, with CMake `N3D_DOS20_CEDC_ORIGINAL_CSV`.
- [Independent Python SHA-gated original-input verifier](../tools/n3d_v079_cedc_verify.py), [Python synthetic cases](../tests/test_n3d_v079_cedc_verify.py), and [Linux+Windows GitHub workflow](../.github/workflows/renderer-v079-cedc-perspective.yml).

### Private original witness rerun

```bash
python3 tools/n3d_v079_cedc_verify.py --cedc-csv /private/original_cedc_operands.csv --edge-csv /private/original_22ca_effective_inputs_private.csv --out /tmp/n3d_v079_result.json
cmake -S . -B build-v079 -DN3D_ENABLE_SDL3=OFF -DN3D_DOS20_CEDC_ORIGINAL_CSV=/private/original_cedc_operands.csv
cmake --build build-v079 --target n3d_dos20_cedc_projection_test
ctest --test-dir build-v079 -R n3d_dos20_cedc --output-on-failure
```

**Remaining blocker:** These exact CEDC results use **original captured CPU operands**, not independently computed modern camera/VEC/IMG source data. The modern remake still lacks proven synchronized original-versus-candidate 64,000 indexed pixel + 768 RGB6 DAC zero-diff. Original `Raycaster.cpp` DDA remains diagnostic; `src/main.cpp` unchanged.
