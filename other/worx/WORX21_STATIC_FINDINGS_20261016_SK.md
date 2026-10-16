# WORX Toolkit 2.1 — priama statická analýza N3D DOS 2.0

**Dátum:** 16. október 2026. **Metóda:** najprv originálny 16-bitový assembler, až potom rekonštrukcia C++17. Žiadna chyba odhadom neoznačená za uzavretú.

## Binárny vstup a identity

- Originál (nepriložený): `N3D_DOS_v2.0_IDA.EXE` (178 528 B), MZ header `0x1C00`, MZ image `0x29D60` (171 360 B), SHA-256 obrazu `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`.
- WORX code segment `15BFh`; `INT63` handler `15BF:30E6` (image `0x18CD6`), dispatch table `15BF:2020` (image `0x17C10`).
- SHA-256 tabuľky `AH 00h..51h`: `38aeeb4ae7790a72808a6855f3ce9691f777f15975260abc0901efd5e70ebf5d`.
- Audited selectors **82** (`00h..51h`); static targets **79 nonzero**, **3 null** (`00h`, `27h`, `28h`), **37 byte-audited leaf** and **42 nonzero entrypoint-only**.
- **Nulls are original static image, not proof they stay zero after initialization.** A literal-byte search did not find `6E 20` or `70 20` (the slot displacement bytes) anywhere in the embedded WORX code span; computed writes/dynamic patching remain unexcluded.

## Exact INT 63h ABI witness (orig machine bytes)

Input `AH` is moved to `AL`, zero-extended, doubled to a word index, and used for `CALL WORD PTR CS:[SI+2020h]`. **No explicit selector-range bound check** in the audited dispatch stub. Any value outside audited 00..51 is **unassessed**. Before dispatch, handler pushes `AX BX CX DX BP DI SI DS ES`; handler sets `DS=CS`, `ES=DX`, `CLD`. After dispatch, it stores `AX/DX` at `CS:30E2/30E4`, restores saved registers and reloads `AX/DX`. `IRET` restores caller FLAGS unless saved frame is modified.

`CS:[3ED4]` is incremented upon entry and decremented before `IRET`. Driver reentrancy and interrupt interleavings are **not** modeled by the simple synchronous C++ backend. The C++ interface exposes `carry` only, not all flags or segment registers; these are still parity gaps.

## Implemented original-machine-audited leaf bodies (37)

| AH | WORX CS entry | Statically observed effect |
|---|---|---|
| `02h` | `0x485A` | write BX to 2DF0; zero AH; write AX to 2010 |
| `03h` | `0x308E` | read16(2C47), then clear |
| `08h` | `0x45E5` | read masked CS byte 2DEA |
| `09h` | `0x309A` | BX*0x04A9 -> 32-bit counter copies 2C4B/2C4F, status reset; returns AX=04A9 |
| `0Ah` | `0x30C1` | restore 32-bit time counter 2C4B from 2C4F; reset 2C53 |
| `0Bh` | `0x30DB` | read zero-extended CS byte 2C53 |
| `0Eh` | `0x45DD` | read masked CS byte 2D62 |
| `13h` | `0x3004` | write AL to CS:2DBC |
| `16h` | `0x3009` | write AL to CS:2DBD |
| `1Ch` | `0x33AF` | return CS byte 2DCA bit 0 |
| `1Dh` | `0x3E5B` | write BL to 2C61; DS modified but ISR restores |
| `1Fh` | `0x45F2` | write 1 to CS:2D62 |
| `20h` | `0x372F` | DSP detected: SB mixer port writes 22h,BL; else AX=FFFF |
| `21h` | `0x3771` | DSP detected: SB mixer port writes 04h,BL; else AX=FFFF |
| `22h` | `0x3750` | DSP detected: SB mixer port writes 26h,BL; else AX=FFFF |
| `24h` | `0x2F5F` | return AX=1234, DX=5678 |
| `26h` | `0x2E76` | write 1 to CS:2C0C |
| `2Ah` | `0x41B3` | AX=low16(CS:[2012]*64)/CS:[201A] or product if divisor=0; DX remainder |
| `2Bh` | `0x41CD` | AX=low16(CS:[2014]*64)/CS:[201C] or product if divisor=0; DX remainder |
| `2Ch` | `0x41E7` | return CS byte[2016 + incoming AL]; internal CLC |
| `2Dh` | `0x45ED` | return CS word 2C56 |
| `30h` | `0x4470` | return CS word 2C49 (internal CLC not propagated by IRET) |
| `31h` | `0x4CE1` | write (AL&3F) at word CS:[4BBF + 2*BX] |
| `32h` | `0x5675` | return 0xFFFF |
| `36h` | `0x5664` | read word CS:[4BEF + 2*AL] |
| `37h` | `0x4866` | return CS word 2DF0 |
| `3Eh` | `0x3ED7` | write BL to CS:3ED6 |
| `43h` | `0x34BB` | write BX to CS:34B9 |
| `44h` | `0x4C61` | write 2 to word CS:[4BAF + 2*BX] |
| `46h` | `0x389A` | install DX:BX callback at CS:3896/3898 |
| `47h` | `0x4C6B` | write 0 to word CS:[4BEF + 2*BX] |
| `4Ah` | `0x2208` | SB mixer write index 0Ah, value BL; AX low=BL, DX=base+5 |
| `4Bh` | `0x21DC` | SB mixer write index 0Ch, value BL; AX low=BL, DX=base+5 |
| `4Ch` | `0x21EC` | SB mixer write index 2Eh, value (BL | BL<<4); AX low=value, DX=base+5 |
| `4Fh` | `0x5A3F` | poll SB DSP write status, then OUT (base+0Ch), AL |
| `50h` | `0x5A1E` | poll SB DSP read status, then IN (base+0Ah), AX=AL |
| `51h` | `0x3DB3` | set 3DB1=1;2B96=AL;2B95=FF;2BC7=00 |

The table is **not** an assertion that all dependent driver initialization, device I/O, interrupts, or audio is simulated. `KnownLeafBackend` handles only these commands for a caller-supplied `CSState` and optional `PortIO`, and refuses every unsupported command. For example, `4Fh/50h` execute exactly up to 65,535 DSP-ready-status polls and **still perform** their final OUT/IN if polling is exhausted. The port model is supplied externally; physical hardware timing is not recreated.

## Data / code boundary correction

The original classification `17C00..18A04 = static table region` was **overly broad**. Dispatch table and other data begin there, but targets from `AH 48h/4Ah/4Bh/4Ch` at `CS:2218/2208/21DC/21EC` execute code in that zone (`image 0x17DCC–0x17E08` etc). Therefore, identify code by actual instruction and control flow, not only broad coarse byte ranges.

## Binary-static tests actually performed

1. Exact original image identity and 82 dispatch words were read from the original MZ image; 37 leaf address spans and terminating `RET` markers checked.
2. SHA-256 of each audited leaf body preserved in `data/n3d_v20_int63_dispatch.json` for subsequent independent byte comparison.
3. C++17 reference builds with `CMake` and 3/3 CTest test suites pass, including port exhaustion, AX/DX propagation, timer arithmetic, indexed 16-bit state memory and preserved caller carry (complete IF state remains outside the model).
4. Optional Python unit test re-reads exact proprietary original when `WORX_N3D_V20_EXE` points at it; test **ran successfully in this analysis**. The original EXE itself is intentionally **not shipped**.

This is a **substantial partial functional reconstruction**, not a 100 % byte/audio/IRQ/real-machine parity certification.
