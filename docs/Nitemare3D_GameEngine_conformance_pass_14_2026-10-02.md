# Nitemare 3D — Game Engine conformance pass 14
## Renderer Stage 2: MAP class/property VEC scan + exact E798 projection
Date: 2026-10-02

## New static closure

Pass 14 corrects an important implementation assumption from Stage 1.

The renderer'with 256-entry wall class and object class tables are loaded from the
`MAP.N` 0x202-byte header:

- word level count;
- 256 wall classes;
- 256 object classes.

The wall/object property tables are then generated in RAM from those class bytes.

Therefore OpenNitemare3D does not need to infer these renderer properties from its
hardcoded Tile abstraction or parse WALLS.N for this purpose.

## MAP-to-VEC migration

AND literal semantic C# port has been prepared for the map scanner and VEC constructors:

- 4046 four-direction map scan;
- 3D54 full boundary vector;
- 3E82 half-cell/special vector;
- 4006 64-unit merge;
- 3CFC directional class test;
- 2334 class->wall-ID lookup.

This closes the Stage-1 `tile.obstacle` VEC-generation approximation.

## Projection migration

`OriginalProjectionExact` replaces the Stage-1 transformed-space clip bridge with the
recovered E798 integer/cardinal behavior.

It uses:

- 64-unit world coordinates;
- exact original Q10 sin/cos table;
- near depth 0x4000;
- recovered projection constants;
- E798 cardinal clipping branches;
- C001/3FFF X clamp;
- strict endpoint ordering;
- inclusive viewport overlap.

## Q10 table extraction

The checked NITE3W 1.10 EXE has SHA-256:

`12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481`

Its automatic data segment starts at file offset `0x2C040`.

AND new extractor emits the exact 1440-byte 360-sine + 360-cosine table.

Stage 2 intentionally fails fast if the exact table is absent.

## Remaining wall-only gaps

The major remaining wall bridge is now `EBD6` perspective texture-U reconstruction.

The Stage-2 orientation traversal also walks the relevant sorted lists fully rather
than duplicating every `3940` early-stop/continuation bound. Owner selection itself
uses the original conflict matrix.

Sprites, shade remap and moving-wall runtime endpoint mutation remain later integration
stages.

## Validation performed

Pure-model tests in this pass cover:

- MAP property formulas over all 256 possible class values;
- object property formulas over all 256 class values;
- 3CFC direction/class matrix;
- full/half VEC endpoint formulas;
- class lookup with wrap;
- E798 cardinal projection examples;
- Q10 binary file parser format;
- Stage-2 artifact consistency.

No .NET compiler exists in this environment, with the C# patch has not been compiled
here. No runtime pixel-parity claim is made.

## Status

- reverse-engineered Game Engine static core: 100%
- OpenNitemare3D VEC generation: Stage-2 exact static policy prepared
- E798 projection: exact semantic port prepared
- EBD6 texture-U: next exact port
- full 3940 traversal: next exact port
- sprite renderer: later
- PIXEL 100%: runtime/capture gate remains