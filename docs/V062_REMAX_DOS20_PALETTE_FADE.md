# Nitemare 3D RE MAX v0.62 — complete DOS2 palette fade

Two original DOS2 runtime captures together cover the complete observed case-3 fade.

The first capture records 15 complete DAC uploads. A resumed unmodified run records the remaining six and the normal return. Together this is exactly 21 uploads of 768 components, or 16,128 DAC component writes.

Across all 15,360 adjacent component comparisons, the rule is exact:

`c >= 3 ? c - 3 : c`.

It is not saturating subtraction. After 21 passes on the observed 6-bit domain, the final palette contains only values 0, 1 and 2 with counts 305 / 240 / 223. The reconstructed final palette FNV-64 is `78F3DAEBC5DDA37D`, matching the emulator palette hash after the fade.

The higher caller into the palette dispatcher and the normal return are also observed. The semantic meaning of its argument remains unassigned.

Open: the following operation, mode-2 behavior, continuous wall-clock/VBlank timing, other palette modes and canonical original-vs-port framebuffer/palette zero-diff.
