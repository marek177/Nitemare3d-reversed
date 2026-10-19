# v0.60 — DOS1.9 indirect candidates and depth-reference producer

The two archived RE MAX NEXT reports in [evidence](evidence/2026-10-19/)
advance local static coverage. They analyze an archived linear ASM export;
they do not reverify a complete original executable or prove executable CFG.

| Finding | Supported scope | Remaining obligation |
|---|---|---|
| 77 indirect candidates individually reviewed | Linear decoded sites, including likely data | Recursive CFG and pointer/alias provenance |
| 23 CS jump tables, 408 WORD entries, 225 distinct targets | Numeric reconstruction reported by source | 56 targets lack linear instruction boundaries |
| 13 XMS sites | Two locally initialized driver-entry pointer families | External driver behavior and global aliases |
| INT08 saved-vector chain | Local acquisition, call and restore | IRQ timing |
| `IMG:1353E` table at `IMG:134DC` | Eight localized WORD entries | XLAT LUT upper-nibble domain at `DS:22C8`; indices 8–15 not excluded |
| `DS:4550` producer `IMG:03378` | Viewport arithmetic for width 0–320 | Parser/LOAD/indirect writers and out-of-domain widths |

Within width domain 0–320, the reported instruction model gives
`floor((320-W)/4)+floor(W/4)`: 80 for W divisible by four, otherwise 79.
Initial W=304 therefore gives 80. This is a depth reference, not proof of a
constant 80 under every reachable state.

`IMG:0B47A` writes the pre-cap SAR4 projection depth to the actor WORD +18;
`IMG:08592` reads it and subtracts the reference. A cull path can bypass that
local writer. Natural stale-depth hits and the complete last-writer graph remain
OPEN. Byte-sized +18 proximity fields and XMS-record +18 accesses are separate.

Important correction: `IMG:07E86` reads `ES:[350C]`, not literally DS.
Earlier `ES←DS` preserves the XMS pointer context while DS is changed.
Six FF-opcode sites are likely data; none is declared formally DEAD.

The reconstructed 116044-byte ASM slice hash is
`1699be5dc6db8a18d1131c369eb0cbaffd7c748127d6170d6f8dc04a07fa81de`.
It is not an EXE fingerprint. Confidence is limited to the source's local static
analysis; no original runtime or new global completion percentage is claimed.
