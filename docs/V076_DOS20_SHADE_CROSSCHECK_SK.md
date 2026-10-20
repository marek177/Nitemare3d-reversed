# Nitemare 3D DOS v2.0 — shade 0x16CE independent cross-check (20 Oct 2026)

**Scope:** C++20 research verification only, not live-original gameplay replay or full renderer 1:1.

## Statics used

The original DOS2 routine at image `0x16CE` constructs its 256-index palette-remap table from the **stable game base palette** in 6-bit RGB, using the active shade selector `WORD DS:6278` and the levels `[0,4,8,12,16,20,30,40]`. Source RGB components are individually decremented and clipped at zero; all 256 RGB6 candidate colors are compared using **Manhattan** distance; an equal-distance tie **retains the first palette index**. Source palette is `DS:4A64..4D63`; one historical output-table alias is `DS:D20C` (must not assume the same segment as `SS:BX` without proof).

**Subtle regression:** with duplicate RGB entries, even shade level 0 is not an identity mapping. Do not replace it with `XLAT[source]=source` by assumption, and do not use the *live faded DAC* in place of the stable base palette.

## Native code and independent differential check

- [N3DDos20ShadeRemap.hpp](../src/re/N3DDos20ShadeRemap.hpp): independently implemented compact shade-builder accepting RGB6 palette or 65,536-byte DS.
- [N3DDos20ShadeXLAT.hpp](../src/re/N3DDos20ShadeXLAT.hpp): separate pre-existing richer implementation with RGB8→RGB6 conversion, fail-closed prepared table semantics and optional original DS:D20C equality check.
- [dos20_shade_remap_test.cpp](../tests/dos20_shade_remap_test.cpp): compares **256 table outputs × all 8 shade levels** for both implementations, against a third straightforward integer reference, including duplicate-color ties, saturation, bad shade index and invalid RGB6 component, and DOS segment offsets.
- Existing [dos20_shade_xlat_test.cpp](../tests/dos20_shade_xlat_test.cpp) and [dos20_wall_material_binding_test.cpp](../tests/dos20_wall_material_binding_test.cpp) further check material binding and orientation-dependent shade selection.

Both implementations are deliberately research modules, not an instruction-exact machine-code clone: a full original-memory capture of `DS:D20C` from the *same* verified renderer tick remains needed to establish byte-perfect shade-table parity in the original runtime.

## DOS2 material binding and perspective U

The companion [V076 IMG + perspective-U binder research](V076_DOS20_WALL_IMG_U_SHADE_BINDING_SK.md) contains a materially larger native candidate. It binds 28B VEC IDs (+03 frame, +04 cache selector) to IMG wall directories, aliased sequence streams and column-major 64/128×64 frames, applies the local DOS shade override for orientations 0/1 when `DS:430E==0`, and offers **DOS-native CEDC/22CA** texture-U computation alongside the older Win16 EBD6 cross-build candidate. Both rely on integer math and explicit 128×64 half selection. That binder has **not** yet proven complete original-vs-remake zero-diff for the same gameplay state.

## 1:1 gate

No synced original DOS2 indexed frame and modern port indexed frame have passed the strict **64,000-byte pixels + 768-byte VGA DAC** gate. Keep `Raycaster.cpp` as diagnostic DDA preview. Next high-value evidence is the exact original `DS:D20C` remap for shade cases, original wall-U values per column, and matching IMG frame IDs from the same tick.
