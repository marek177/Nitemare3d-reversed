# Nitemare 3D RE MAX v0.68 — UIF binding, page flip and complete palette fade-in

**Date:** 19 October 2026

Original DOS2 runtime now binds two concrete UIF assets to exact displayed VGA pages and closes the complete observed palette mode-2 fade-in.

## UIF record 6 — Main Menu

Runtime lookup with argument 6 resolves the 6-byte UIF descriptor at offset 0x24:
- length 38,613;
- file offset 99,751 (0x185A7);
- PCX 320×200, one plane, 320 bytes per row.

A manual PCX RLE decoder and Pillow produce the same 64,000 indexed pixels. All 64,000 indices match VGA page 0 exactly, and all 768 DAC components match the PCX palette after the original >>2 conversion.

## UIF record 4 — Please Wait

The next natural wrapper invocation carries argument 4. The newly visible page 1 matches UIF record 4 exactly: 64,000 indexed pixels, zero differences.

The observed page flip performs:
- swap of the A000/A400 page words;
- OUT 0x400C to CRTC port 0x3D4;
- resulting CRTC start 0x4000;
- page words become A400/A000.

## Palette mode 2 fade-in

The complete mode-2 transition performs 23 uploads × 768 DAC bytes:
- upload 1: black;
- 21 intermediate uploads following the recovered integer-step algorithm;
- upload 23: exact base palette.

All 16,128 intermediate-component comparisons match the reconstructed algorithm with zero deviations. The final upload matches an independent DAC snapshot.

The isolated trace contains 1,162,343 CPU instruction records and stops by USER_STOP after returning from the wrapper.

This is exact original asset→original framebuffer/page/palette evidence for these two menu assets. It is not original-vs-remake parity or gameplay raycaster closure.

Open: exact VBlank/wall-clock timing, other palette modes, all UIF records, gameplay projection/clipping/depth and remake framebuffer equality.
