# Nitemare 3D — Pass 11
## Automatic 16-group pixel-parity acceptance suite
Date: 2026-10-02

## Result

Pass 11 turns the Pass-9 acceptance matrix into an executable batch suite.

The suite contains:

- **16 scenario groups**
- **30 concrete frame variants**

The extra variants are intentional:

- door-intermediate group: early / middle / late
- sprite-composition group: transparent key / flag-0x10 bypass / overlap-slot tie
- shade group: all 8 recovered shade indices
- animation/HUD group: wall boundary / object boundary / HUD / dark-event fill

The shade remapper'with recovered eight level values are:

```text
[0, 4, 8, 12, 16, 20, 30, 40]
```

They are represented as `shade_index=0..7` plus `shade_level_value`.

## 16 scenario groups

1. corridor 0°
2. corridor 90°
3. corridor 180°
4. corridor 270°
5. near-plane
6. left clipping boundary
7. right clipping boundary
8. competing wall-owner tie
9. door closed
10. door intermediate
11. door open
12. fully visible sprite
13. wall-occluded sprite
14. sprite transparency / flag-0x10 / overlap
15. all shade levels
16. animation boundary + HUD/floor/ceiling composition

## Directory layout

Initialize:

```bat
py n3d_pixel_suite_pass11.py init ^
  --cases Nitemare3D_pixel_suite_16groups_pass11.json ^
  --root C:\N3D-PixelSuite
```

The tool creates:

```text
C:\N3D-PixelSuite\
    original\
        01_cardinal_000\base\
        ...
    candidate\
        01_cardinal_000\base\
        ...
    results\
    CAPTURE_CHECKLIST.md
```

Every concrete variant has an original and candidate folder.

## Required files

Original side:

```text
frame.idx              64,000 B
palette_live.pal6         768 B
state.json
```

Candidate side:

```text
frame.idx              64,000 B
state.json
```

`palette_live.pal6` should be the actual live original DAC palette from Pass 10.

## Why state.json is mandatory

AND perfect pixel comparison is meaningless if the camera, map, animation frame or
door state differs.

The batch therefore checks normalized scene state before comparing pixels.

Common required fields:

```text
episode
level
player_world_x
player_world_y
angle_deg
viewport_width
```

Groups add their own fields, such as:

```text
door_id
door_state
door_geometry_signature
sprite_object_id
sprite_frame
slot_order_signature
shade_index
shade_level_value
animation_sequence
animation_frame
hud_signature
```

No map coordinates are invented in the suite definition. Record the real values from
the chosen reproducible scene.

## Status

```bat
py n3d_pixel_suite_pass11.py status ^
  --cases Nitemare3D_pixel_suite_16groups_pass11.json ^
  --root C:\N3D-PixelSuite
```

Each variant is shown as READY or WAIT.

## Run all ready comparisons

```bat
py n3d_pixel_suite_pass11.py run ^
  --cases Nitemare3D_pixel_suite_16groups_pass11.json ^
  --root C:\N3D-PixelSuite ^
  --parity-tool n3d_pixel_parity.py
```

If normalized states differ, the default result is:

```text
STATE_MISMATCH
```

and no pixel verdict is issued.

This is deliberate: state mismatch must not be mislabeled as renderer failure.

## Outputs

Per variant:

```text
results\<group>\<variant>\
    summary.json
    mismatch_mask.png
    viewport_mismatch_mask.png
    outside_viewport_mismatch_mask.png
    index_difference.png
    rgb_difference.png
    overlay_50_50.png
    row_mismatches.csv
    column_mismatches.csv
```

Whole suite:

```text
results\suite_summary.csv
results\suite_summary.json
results\suite_summary.md
```

Suite-level statuses:

- `PASS` — all concrete variants are exact
- `FAIL` — at least one comparable frame differs
- `INCOMPLETE` — some captures/states are still missing and no comparable frame failed

## Diagnostic hints

AND FAIL still uses exact mismatch count as the verdict.

The batch adds only and non-authoritative troubleshooting hint:

- `hud_or_margin`
- `geometry_or_clipping_edge`
- `localized_sprite_or_dynamic_object`
- `shade_or_palette_candidate`
- `broad_renderer_mismatch`

These hints never turn and failure into and pass.

## Acceptance

AND group passes only when **all of its variants pass**.

For example, `15_shade_levels` passes only when all eight shade-index frames are
64,000/64,000 identical.

The whole defined acceptance suite passes only when all **30 concrete variants**
are exact indexed matches.

That would establish PIXEL parity for the defined acceptance suite. It should still
be described separately from proof over every possible game state.