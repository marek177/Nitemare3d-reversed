# OpenNitemare3D Pass 17 — Stage 4 + parity integration

Target base: `marek177/OpenNitemare3D` master commit `b01f4b2342629ecd39f62307526568af2b6ec034`.

## What this patch integrates

- recovered Stage-4 VEC/owner/span wall renderer;
- persistent paired-wall / class-3 VEC runtime;
- original IMG low-wall sequence/frame selection;
- Pass-12 320x200 palette-index capture (`frame.idx`);
- native 320x200 logical framebuffer when either Stage 4 or parity capture is enabled;
- preservation of the existing SPACE/OnUse path when Stage 4 replaces `RenderRaycaster()`;
- `GAME.PAL` PCX palette loading from the final 768 bytes, with the preceding `0x0C` PCX palette marker checked;
- parity manifest/state labels that report Stage 4 instead of incorrectly claiming the legacy DDA renderer.

## Apply

```bat
git checkout master
git reset --hard b01f4b2342629ecd39f62307526568af2b6ec034
git apply OpenNitemare3D_RendererStage4_Parity_Pass17.patch
```

The patch is a syntactically valid unified diff (`git apply --numstat` passes in the analysis environment).

## Required renderer tables

Extract from the checked Win16 1.10 executable:

```bat
py extract_nite3w_renderer_tables.py nite3w.exe data
```

Expected files:

- `data/N3D_TRIG_Q10.BIN` — 1440 B
- `data/N3D_VISIBILITY_OCTANTS.BIN` — 32 B

## Example capture

```bat
dotnet run -- ^
  --n3d-renderer-stage4 ^
  --n3d-trig data\N3D_TRIG_Q10.BIN ^
  --n3d-visibility-octants data\N3D_VISIBILITY_OCTANTS.BIN ^
  --parity-capture captures\case01 ^
  --parity-frame 0 ^
  --parity-exit
```

Candidate output includes `frame.idx` (64,000 bytes), `palette_candidate.rgb8`, `state.json`, `manifest.json`, and `capture.ok`.

## Deliberately still open

Pass 17 does **not** claim PIXEL 100%. The next blockers are:

1. shade-remap selection/wiring — Stage 4 currently calls the indexed wall writer with `paletteRemap = null`;
2. original sprite/object composition — Stage 4 is wall-only and does not use the original 100-slot / wall-occlusion sprite path yet;
3. recovered USE/key/card dispatcher -> paired-wall controller integration; Pass 17 only preserves the existing OpenNitemare3D `OnUse` behavior;
4. runtime actor occupancy -> original door auto-close occupancy callback;
5. shared original RNG call order for extended SEQDEF choices; Stage 4 intentionally refuses to substitute `System.Random`;
6. original-reference framebuffer captures and byte-for-byte comparison.

For wall-only cardinal/static acceptance cases, items 1–5 can be isolated incrementally; full renderer acceptance requires all of them.