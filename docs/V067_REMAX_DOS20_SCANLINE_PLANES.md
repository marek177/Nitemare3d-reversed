# Nitemare 3D RE MAX v0.67 — DOS2 PCX scanline/VGA plane addressing

**Date:** 19 October 2026

An existing original DOS2 CPU/VGA trace closes the addressing behavior of renderer routine `097A:07DE` for the Main Menu PCX background.

The trace contains 197 complete rows (y=0..196), each 320 pixels wide:
- 63,040 executed pixel writes at `097A:082F`;
- 63,237 map-mask OUT operations;
- zero observed address-model mismatches;
- zero observed VGA plane-mask mismatches.

For the verified x0=0 row calls:

```
plane = x & 3
cpu_offset = 80*y + (x >> 2)
raw_interleaved_vram = 4*cpu_offset + plane
```

The selected VGA plane masks cycle 01,02,04,08 through full written values 11h,22h,44h,88h. Four adjacent horizontal pixels share the same CPU byte offset and differ by plane.

The source row buffer in this capture begins at DS:E5FC and the destination is ES:A000. These are capture-specific addresses, not universal constants.

A previous complete final-asset comparison already established 64,000 indexed pixels with zero differences for this rendered asset, including the final three rows not instruction-covered here. This v0.67 closure is specifically the instruction-level addressing/mask proof for the 197 captured rows.

Open: runtime execution of the color-key branch, multi-pixel column heights, complete caller census, gameplay raycasting projection, clipping, shading and original-vs-port framebuffer equality.
