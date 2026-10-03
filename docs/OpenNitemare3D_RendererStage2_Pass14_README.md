# OpenNitemare3D — Pass 14
## Renderer Stage 2: exact MAP class/property VEC generation + E798 projection

Prepared for the current `marek177/OpenNitemare3D` master family.

This package supersedes the Stage-1 map-boundary/projection bridges for the wall path.

## Major correction: the renderer tables come from MAP.N header

The old shorthand "MAP/WALLS property tables" was too broad.

The checked Win16 1.10 loader reads exactly `0x202` bytes from `MAP.N`:

```text
+0000  WORD level count
+0002  256 bytes wall ID -> wall class
+0102  256 bytes object ID -> object class
```

The first level begins immediately at:

```text
+0202
```

and every level is exactly:

```text
0x2000 = 8192 bytes = 64*64*2
```

The runtime wall-property table is then GENERATED from the 256 wall classes by
`FUN_1010_24BC`. The object-property table is generated similarly by `2556`.

So Stage 2 no longer guesses wall solidity from `Tile.obstacle`.

## Exact wall property derivation

For each wall ID, from its class byte `c`:

```text
bit 0x04 : class 01..30
bit 0x10 : class 2E..2F
bit 0x08 : class 31..40
bit 0x01 : set when (0x04|0x08) is nonzero
bit 0x02 : class 01..40
bit 0x40 : class 47..48
```

This is the direct semantic result of the original bitwise initializer.

## Exact object property derivation

From object class `c`:

```text
bit 0x01 : 06..3D
bit 0x02 : 08..2D
bit 0x04 : 2F..3D
bit 0x08 : 08..25
bit 0x20 : class 2A
bit 0x40 : class 04
```

The MAP-to-VEC scanner specifically needs object class `03` boundary behavior.

## Exact MAP -> VEC generation

`OriginalMapTables.BuildVectors()` ports:

```text
FUN_1018_4046
FUN_1018_3D54
FUN_1018_3E82
FUN_1018_4006
FUN_1018_3CFC
FUN_1010_2334
```

It preserves:

- the four orientation scans;
- swapped scan axes for orientations 2/3;
- neighbor direction per orientation;
- property bit 04/08/10 decisions;
- object-class-3 boundary test;
- dynamic/special neighbor boundary test;
- the original merge-state conditions;
- 64-unit endpoint extension;
- half-cell vectors for classes 31..40;
- curtain-class exceptions 3F/40;
- fallback wall-ID lookup to class 30;
- per-class texture-offset arithmetic.

The current OpenNitemare3D `textureID` is still retained only as bridge metadata
for fetching the IMG bitmap. The VEC wall ID/class/property behavior itself now uses
raw `MAP.N` bytes.

## Exact E798 projection

Stage 2 adds `OriginalProjectionExact.cs`, a semantic port of the checked Win16 1.10
`FUN_1010_E798` path:

```text
world endpoint - player
Q10 rotation
near depth 0x4000
vertical Q4 projection
vertical early reject
cardinal near-plane correction
signed horizontal projection
C001 / 3FFF clamp
strict endpoint swap
inclusive viewport overlap
```

## Exact Q10 trigonometry

The original uses lookup tables, not `Math.Sin/Math.Cos`.

Generate the exact table once from the checked Win16 1.10 EXE:

```bat
py extract_nite3w_trig_q10.py ^
  "C:\N3D\nite3w(10).exe" ^
  "data\N3D_TRIG_Q10.BIN"
```

Checked EXE:

```text
SHA-256:
12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481
```

The extractor reads the NE automatic data segment at file offset `0x2C040` and
reconstructs all 360 sine + 360 cosine Q10 values via the exact lookup addresses used
by `ECAC/ECF8`.

Sanity anchors:

```text
sin 0   = 0
sin 45  = 724
sin 90  = 1024
cos 0   = 1024
cos 45  = 724
cos 90  = 0
```

Output is exactly 1440 bytes.

Stage 2 refuses to enable without this exact table. It does not silently replace the
original lookup table with floating-point trig.

## Enable

```bat
dotnet run -- ^
  --n3d-renderer-stage2 ^
  --n3d-trig "data\N3D_TRIG_Q10.BIN"
```

Optional:

```text
--n3d-renderer-stats <json>
```

## What remains a bridge

Stage 2 deliberately leaves one major wall-pixel geometry bridge:

```text
FUN_1010_EBD6 perspective wall-U mapping
```

The final endpoint correction `6422` is exact, but the preceding inverse wall
intersection is still computed geometrically.

Also still pending:

- exact `3940` early-stop + continuation bounds rather than the current equivalent
  player-outward full traversal;
- original sprite slot renderer / wall occlusion;
- shade remap integration;
- dynamic runtime replacement of VEC endpoints for moving paired walls.

## Apply from clean master

```bat
git apply OpenNitemare3D_RendererStage2_from_master_Pass14.patch
```

If Pass 12 or Pass 13 was already applied, copy the five Stage-2 `.cs` files manually
and merge the three small Program/GameWindow/Player changes rather than forcing the
clean-master patch.

## Best next step

Stage 3 should port `EBD6` literally and then reproduce `3940`'s exact early-stop /
continuation traversal. That will remove the remaining broad static bridge in the
wall-only renderer before attaching sprites.