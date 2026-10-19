# Nitemare 3D RE MAX v0.71 — DOS/Win16 GAME.PAL mapping

**Date:** 19 October 2026

The supplied DOS GAME.PAL is 1,924 bytes and is byte-identical to the compared DOS root copies. The Win16 game.pal is 5,459 bytes.

For both relevant formats, the final 768 bytes contain 256 RGB triples. The DOS suffix begins at file offset 0x484; the Win16 suffix at 0x1253.

The Win16 palette suffix is exactly:

`10 system colors + 236 preserved DOS game colors + 10 system colors`.

All 236 preserved game colors are byte-identical and remain in order, but their indices move into Win16 positions 10..245. Twenty DOS indices are omitted:
34, 68, 73, 129, 130, 131, 132, 135, 136, 138, 139, 142, 143, 152, 155, 194, 206, 210, 212, 213.

Without remapping, only palette index 0 has identical RGB between the two files. This explains why substituting the Win16 palette file directly into DOS produces visibly wrong colors.

SHA-pinned DOS2 machine code also confirms the base-palette loader seeks 768 bytes before EOF, reads 768 bytes, shifts each component right by two, then uploads all 768 components through VGA DAC ports 0x3C8/0x3C9.

One original DOS2 Please Wait DAC snapshot matches 762/768 components and 254/256 complete RGB triples from the base DOS suffix after >>2. Indices 227 and 235 are black in that transient snapshot; the exact later writer/effect remains open.

This closes the static/data index mapping and the DOS base-loader contract. It does not close Win16 fallback mapping for the 20 omitted indices, AnimatePalette timing, or original-vs-port framebuffer+DAC parity.
