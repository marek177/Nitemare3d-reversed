# V081 — DOS2 full wall-frame acceptance boundary

Date: 21 October 2026. Evidence integration only; no new original execution.

## Established evidence
V078 closes 1,520/1,520 original texture-U edge returns; V079 closes 1,808/1,808 CEDC returns given captured operands. V080 reproduces the original x=8 42-pixel wall writer with authentic DOS2 IMG U106 and original shade/XLAT, and a 2 MiB single-writer VRAM transition. This does not prove the other 303 columns against an independently captured original post-wall frame.

## Phase-alignment invariant
At image 267A the original reads the accumulator high word BEFORE image 2684 increments the 16.16 accumulator. A mid-render RAM dump already containing the incremented value cannot be fed directly as a pre-draw snapshot. For the tested x=8 case, pre-step accumulator 014E38F2 produces U106; the captured post-step 014B800F incorrectly produces U109, yielding 31/42 pixel mismatches. Never apply a global -3 texture-U patch.

## Required next acceptance capture
1. Pin original EXE, IMG, MAP, palette and DS snapshots by SHA256 and record exact guest CPU checkpoint at the entry of the wall renderer.
2. Capture an original indexed 320x200 frame immediately after the complete wall pass at BF5F, plus the original 768 RGB6 DAC components, page selection, frame/tick, camera and relevant cache state.
3. Replay the same pre-wall state in the native DOS renderer and compare 304 per-column owners, frame IDs, source U/V, shade, clipping, and 64,000 indexed pixels.
4. Emit first divergence with screen coordinate, wall owner, IMG stream/frame, source U/V, shade, VGA plane and address; do not treat missing pixels as zero.
5. Continue through sprites, transparency, HUD, page flip and palette only after wall-pass equivalence is independently established.

## Release gate
Do not replace production DDA in Raycaster.cpp until full wall pass, sprites and HUD reach synchronized zero-diff on representative original checkpoints. Current V080 evidence is single-writer parity, not whole-scene parity.
