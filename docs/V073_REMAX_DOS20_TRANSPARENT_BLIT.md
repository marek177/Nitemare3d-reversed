# Nitemare 3D RE MAX v0.73 — natural transparent VGA blit

**Date:** 19 October 2026

A natural original DOS2 call enters the transparent branch of VGA blitter `097A:07DE` and is captured through completion of the pixel loop without guest code/register/source/VRAM patching.

Observed call:
- source = 8D9B:23B4;
- x = 8, y = 4;
- width = 22;
- height = 96;
- source column stride = 96;
- page flag = 0;
- transparency key = palette index 0.

All 2,112 source pixels are checked against the source dump.

Results:
- 1,102 source pixels equal key 0 and skip the destination MOV;
- all 1,102 corresponding destination locations contain nonzero background before the call and preserve it afterward;
- 1,010 non-key pixels execute the destination write;
- 931 VGA bytes physically change; 79 writes are idempotent because the destination already contains the same value;
- the fully reconstructed expected VGA memory equals the complete 2,097,152-byte post-call snapshot with zero differences.

The verified linear equivalent is:

```
for col in 0..21:
  for row in 0..95:
    c = source[col*96 + row]
    if c != 0:
      framebuffer[(4+row)*320 + (8+col)] = c
```

The original implementation is planar VGA and uses the same 80-byte scanline/plane selection contract established by v0.67.

All 2,112 source bytes are also found exactly in the original IMG.1 payload at the captured offset. The concrete resource ID/descriptor chain remains open.

This closes one natural non-unit-height transparent UI blit with key 0. Other keys, page flag 1, gameplay sprite projection, occlusion, clipping and whole-renderer parity remain open.
