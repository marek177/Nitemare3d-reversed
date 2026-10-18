# DOS sprite pixel contract and Win16 renderer map

Analysis date: 2026-10-18. Base: main `1d47c86` (v0.42); the v0.41
compositor is unchanged there. No completeness percentage is raised.

## Evidence boundary

**Confirmed, high confidence:** this pass read `N3D-UNFU(8).exe`, 116606 bytes,
SHA-256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.
It exactly matches the DOS v2.0 fingerprint in
`Nitemare3D_renderer_pixel_path_audit_2026-09-23.md`. The MZ header is 512 bytes;
all DOS offsets below are relative to the load image, before runtime relocation.
`1000` is the existing export's analytical segment label, not a runtime CS.
The complete `1B3E..1D3C` function-body SHA-256 is
`9c6317d465f0e2c2c4c3a9919738c2d05e7da778b8f992f363ebefb210166937`.
No original binary is distributed by this change.

**Reported, not independently reverified here:** Win16 and DOS frame call maps,
slot initialization and lazy loading are retained from repository audits. The
v0.44 audit ZIP was also inventoried; it contains reports, models and writer
CSVs, no original renderer binary/disassembly. No Win16 binary was inspected in
this pass. Win16 claims below remain scoped to the prior audit, not new closures.

## Call map and records

| Build | Path | Evidence / limit |
|---|---|---|
| DOS 2.0 | frame BF3B→1021E, BF40→213E, BF52→19C6, BF5A→2500, BF5F→21F0, BF64→273C | v0.41 direct-child table; targets not redecoded here |
| DOS 2.0 | 213E spans; 202A interpolation; 25DC drawing block; 1A2E wall writer; 1B3E sprite writer | prior pixel audit; 1B3E directly decoded here |
| Win16 1.10 | 3:D78C → 1018:3940 → 3:6266 → 3:3DB8 → 3:66B0 → 3:6348 → 3:6914 | ordered frame children per prior pixel audit |
| Win16 1.10 | 6348→CC7C slot projection; 6914→3F80→374E linear sprite branch | prior audit; raw bytes needed for renewed verification |
| Win16 1.10 | 66B0→EBD6/6422→3E44→366A linear wall writer / planar branch | prior audit; existing Win16WallRasterCore.hpp covers bounded wall math |

DOS slot reads at 1B44..1B84 and 1C75..1C95 directly support:

| Slot offset | Read/use |
|---|---|
| +02 | actor far pointer, then actor +05 bit 10 |
| +06 | descriptor near pointer |
| +08 / +0A | horizontal endpoints |
| +0C / +0E | vertical endpoints |
| +10 | unsigned value compared against the per-column wall table |

Descriptor byte +00 is the horizontal source extent, byte +01 the vertical
source extent; descriptor +06/+08 is the source offset/segment. Do not conflate
this descriptor pointer with the actor far pointer. The prior Win16 slot view
has the same local offsets, but that alone does not establish ABI equivalence.
DOS span stride is 18; the Win16 wall span is 20. Sprite slots are a separate
18-byte record family, not wall spans.

## New instruction-derived C++ subset

`src/re/N3DDos20SpriteRaster.hpp` deliberately exposes local operations, without
connecting a guessed scaler to the scene renderer.

| Operation | Instructions | Exact contract |
|---|---|---|
| Wall gate | 1C89..1CDD | actor flag 10 bypasses; otherwise skip on unsigned wall > slot+10; equality draws |
| Transparency | 1CEE..1CF4 | source byte 1F skips the store; other bytes copy unchanged |
| Vertical setup | 1B84..1C07 | wrapped word count bottom-top+1; unsigned (sourceHeight<<16)/count before clipping; signed viewport tests |
| Bottom clip | 1BBA..1BC8 | if bottom>DS:454E, add viewportBottom-bottom to count |
| Top clip | 1BCB..1C04 | if top<DS:454C, adjust firstY/count and source start by low32(signed16(viewportTop-top)*step) |
| Source stepping | 1CF7..1CFE | add fraction, ADC integer offset, wrap both words; advance destination by 80 even for transparent pixels |
| VGA address | 1C9E..1CC7 | low8(y)*80 + logical(x>>2), word result; sequencer byte ROL8(11h,x&3) |

The AL-only multiply matters: the literal local instruction wraps y at 256.
This is not evidence that such an input is reachable after viewport clipping.
The segment comes from DS:012E. No page*16 formula is added: selection of that
segment/page is outside this subset. The emitted sequencer values are
11/22/44/88, whose low four bits select planes 0/1/2/3.

The wall table is read through SS at 47E4+2*x; there is no wall-depth write in
the decoded sprite function. Later slot stores can overwrite earlier sprite
pixels. The integration test feeds samples through the existing ascending slot
walk; it does not recover projection's bucket allocation or prove global
back-to-front sorting.

`setupVertical` returns raw clipped count words, including zero/negative signed
results. `nullopt` only represents the original division-by-zero precondition.
No host loop executes these degenerate counts. Original LOOP with CX=0 can run
65536 iterations; caller exclusion/reachability must be proven before adopting
a modern empty-span interpretation.

## Win16 comparison: retained evidence only

The previous pixel audit reports Win16 1.10 key 29, linear pitch 320, wall
visibility table 58FE and actor flag 10 bypass. Its wall writer copies every
sample, with optional shade remap 8094; sprite transparency must not leak into
the wall writer. Those values must not be generalized to all Win16 releases or
all DOS releases. This change does not introduce a guessed shared palette key,
Win16 comparison signedness, or generic sprite resize algorithm.

## Open binary proof obligations

1. DOS horizontal setup 1C07..1C75 and outer loop 1D01..1D36: translate the exact
   stack arithmetic, conditional clipping order and source termination together.
   The right-clip branch jumps past the left-clip branch; generic rectangle
   intersection would silently change behavior for sprites spanning both edges.
2. Recover slot insertion/bucket collisions and producer bounds for all slot
   coordinates; establish reachability of zero/negative counts and wrap cases.
3. Recover descriptor allocation/loading/relocation, selected source frame,
   segment boundary behavior, page/segment selection and presentation.
4. Materialize the fingerprinted Win16 1.10 binary, decode 374E/3F80 and compare
   signedness, clipping and sample phase instruction by instruction. Expand to
   other DOS/Win16 versions only after build identification.
5. Full wall/span/projection integration, exact tables/palette and rounding remain
   separate from this local sprite contract. Static reconstruction can continue;
   original indexed-framebuffer captures are ultimately needed to demonstrate
   pixel parity, not to infer missing code in this pass.

## Reproduction and regression scope

Run `python3 tools/n3d_dos20_sprite_verify.py /path/to/N3D-UNFU.exe` on the exact
image above. It rejects a different SHA before checking the function hash and
10 instruction anchors. To independently decode:
strip the MZ header according to e_cparhdr, then run GNU objdump with
`-D -b binary -m i8086 --start-address=0x1b3e --stop-address=0x1d3d`.

The CMake target `n3d_dos20_sprite_raster_test` is automatically registered with
CTest. Synthetic fixtures cover signed top/bottom clipping, fractional phase,
DIV-zero precondition, source carry/wrap, unsigned visibility/equality/bypass,
all 256 source indexes, all 64000 viewport addresses, and overlapping slot
samples preserving transparent/occluded background and the wall table.
These tests validate the bounded contract; they are not an original-frame oracle.

Validation performed in this pass: direct GCC C++20 builds of the new sprite,
existing v0.41 compositor and existing Win16 wall raster tests all passed.
The new sprite test also passed ASan/UBSan with leak detection disabled because
this host prevents LeakSanitizer process inspection. The binary verifier passed
on the exact image and rejected a one-byte mutation. `git diff --check` passed.
CMake/whole-project CTest could not run here because `cmake` is absent; the new
CTest registration and dedicated GitHub workflow provide repeatable checks.
