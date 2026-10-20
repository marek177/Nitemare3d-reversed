# DOS2 wall snapshot replay

`n3d_dos20_wall_replay` connects the existing material binder, native CEDC/22CA texture-U calculation, palette XLAT and span wall writer in a runnable C++20 tool. It does not regenerate geometry from MAP data: VECs, owners and spans come from the supplied post-span DS checkpoint.

## Build and run

```sh
cmake -S . -B build -DN3D_ENABLE_SDL3=OFF -DCMAKE_BUILD_TYPE=Debug
cmake --build build --config Debug --target n3d_dos20_wall_replay
build/n3d_dos20_wall_replay --ds DS.bin --img IMG.1 --vec-count 1 --background-frame background.idx --reference-frame original.idx --output-dir replay
```

On multi-configuration builds the executable is under `build/Debug/`. Supply the actual active VEC count, not the example value. `--page 0|1` defaults to zero. The output directory must not exist. DS must contain exactly 65,536 bytes; each indexed framebuffer must contain 64,000 bytes. Use matching DOS 2.0 checkpoint, IMG episode, background and reference inputs. The tool validates structure but does not authenticate the build or verify capture synchronization.

The checkpoint must retain the DS material cache selectors, native camera state, shade state, palette and complete contiguous owner/span records expected by the existing recovered pipeline. A generic memory dump from an arbitrary frame phase is not sufficient. No commercial assets are included.

## Outputs and interpretation

| File | Meaning |
|---|---|
| `candidate.idx` | 320 by 200 indexed candidate, with supplied background preserved outside generated walls |
| `generated.mask` | 64,000 bytes: one only where this invocation wrote a wall pixel |
| `candidate.u` | 304 physical texture-U values for screen columns 8 through 311 |
| `candidate.u-valid` | 304 validity bytes; culled columns have no valid material U |
| `columns.csv` | Per-column owner/span, selected image frame, U, shade and raster coverage |
| `report.json` | Coverage, optional masked pixel differences and explicit evidence limits |

With a reference, equality covers only generated wall pixels. Differences outside that mask are not accepted as remake output: they remain supplied background. Without a reference, or with zero generated pixels, equality is null. Exit status is 0 for a valid replay, 1 for a generated-wall pixel mismatch, and 2 for invalid inputs or an unavailable comparison. The tool does not overwrite inputs or an existing output directory.

`full_frame_parity_proven`, `original_recording_authenticated` and `input_state_synchronization_verified` remain false. Palette XLAT uses the DS base palette; no live DAC parity verdict is produced. Sprites, HUD, MAP-to-VEC geometry, scheduler timing and the active diagnostic DDA game renderer are outside this tool's scope. Animation requests beyond the available sequence are clamped by the existing binder and counted in the report; this does not establish original animation timing.

## Validation and remaining evidence

Sixteen synthetic CLI checks exercise the joined raster path, frame selection, exact one-pixel mismatch reporting, mask isolation, absent reference, all-culled coverage, malformed DS/shade/cache/CEDC inputs, output preservation and CLI validation. They run the compiled executable and verify input files remain unchanged. Existing CEDC and material-binding tests remain separate arithmetic/component checks.

No authenticated original snapshot replay was performed for this integration change. A synchronized original DS/IMG/background/reference capture is still required to establish even scoped original wall equality; full indexed-frame and DAC acceptance remains a separate gate. The integration adds no new original-runtime evidence beyond the witnesses documented by its component headers.

## Localizing a divergence

`first_wall_mismatch_pixel` is the lowest linear framebuffer index (top to bottom, then left to right), independent of the renderer's column traversal. `first_wall_mismatch` records its x/y, candidate and reference palette indices, owner VEC pointer, span index, wall ID and physical U. This localizes an observed difference without assigning a cause. `wall_mismatch_bounds` gives inclusive left/top/right/bottom limits across all generated-wall differences. Both objects are null when there is no observed difference, including absent reference or zero coverage; consult `wall_pixels_equal` to distinguish these cases.

`columns.csv` appends `compared_pixels` and `mismatch_pixels`. Without a reference or for a culled column, compared count is zero and mismatch count is empty. With a drawn column and reference, zero mismatches is explicit. Counts must reconcile with the masked aggregate, never with supplied background pixels. A three-point synthetic regression checks opposite frame corners within the wall region and verifies row-major first-difference selection despite column-major drawing.

## Patterned texture regression

Three additional joined-executable cases use synthetic texels `(17*U+3*V) mod 256` instead of solid colors. Independent integer formulas for the fixture camera predict all 304 physical U values and every generated pixel. Coverage includes 64-wide textures, both faces of 128-wide textures, fractional vertical carry, clipped walls with a nonzero starting V and opaque palette index zero. These are deterministic integration regressions, not original-runtime witnesses or proof of general camera geometry.
