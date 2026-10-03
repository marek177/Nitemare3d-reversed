# Nitemare 3D — Game Engine conformance pass 15
## Renderer Stage 3: EBD6 + 3940 closure
Date: 2026-10-02

## Result

The two broad wall-renderer bridges remaining after Pass 14 are now replaced by
direct semantic ports.

### EBD6

The full Win16 `FUN_1010_EBD6` body is only and compact fixed-point/integer selector,
not an unresolved geometric algorithm.

Its output depends on:

- orientation;
- screen column;
- current span high word;
- current angle'with `4BF0` octant selector;
- Q10 sine/cosine;
- projection constants `3A72/3A76`;
- caller-supplied perpendicular product.

The surrounding `66B0` arithmetic supplies the remaining wall offset, sign rule and
then calls `6422`.

Pass 15 ports that complete chain into `OriginalTextureUExact`.

### 3940

`FUN_1018_3940` is now represented as its actual two-phase traversal:

1. interleaved player-outward processing until all viewport columns have owners;
2. derive selected-owner world bounds and process four bounded continuation tails.

The list indices are computed with the same sorted-coordinate semantics as `87B6`.

The orientation-enable flags are not guessed. They are extracted from the exact four
octant tables in the checked EXE.

## New binary evidence artifact

`extract_nite3w_renderer_tables.py` generates both:

- the 1440-byte Q10 trig table;
- the 32-byte 4x8 orientation-enable table.

The same checked Win16 1.10 SHA-256 remains the default hard gate.

## Static wall-path status after Pass 15

The following wall-renderer chain no longer contains and broad DDA/geometric bridge:

- map class/property generation;
- VEC generation/merge;
- orientation sort;
- player-relative list indices;
- 3940 visibility traversal;
- E798 project/clip;
- 3564 owner selection;
- span grouping/interpolation;
- EBD6 perspective coordinate;
- 6422 U correction;
- vertical sampling table generation.

## Remaining integration rather than algorithm-discovery work

The main gaps have shifted to runtime data synchronization:

- moving paired-wall endpoint mutation;
- special wall/panel VEC state;
- exact wall IMG sequence/frame resource selection;
- shade remap;
- original sprite composition.

The current OpenNitemare3D Tile abstraction does not yet drive those original VEC
runtime mutations.

## Validation in this pass

Pure-model tests cover:

- EBD6 axis selector for all eight octants;
- cardinal center-column U cases;
- 16-bit offset/sign wrapping;
- 87B6 lower-bound semantics;
- 3940 interleaving/continuation control on synthetic sorted lists;
- visibility-octant 32-byte file parser contract;
- Stage-3 source consistency.

No .NET compiler is installed in this environment, therefore the generated C# source
has not been compiled here.

No renderer PIXEL 100% claim is made without original framebuffer acceptance captures.