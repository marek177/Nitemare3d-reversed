# Nitemare 3D Win16 NE fixup/callgraph closure v5

Date: 2026-09-30

## Scope

v5 resolves the Win16 NE relocation/fixup layer instead of treating raw `lcall` operands as final addresses. It also corrects the internal 16-bit disassembly parser and applies CFG reachability so calls after a real `ret/lret` are not automatically attributed to the preceding Ghidra `FUN_*` interval.

## Disassembly parser correction

GNU `objdump` can wrap long instruction encodings across output lines. The previous parser could treat continuation bytes as another instruction. v5 forces `--insn-width=16` and rebuilds the Win16 machine layer before CFG analysis.

Win16 1.0 now has 43,979 reachable instructions plus 20,282 linear-but-unreachable instructions inside the current Ghidra-derived intervals. 410/959 indexed entries contain some trailing/non-reachable interval content.

## NE fixup expansion

| build | relocation records | expanded fixup sites | broken chains |
|---|---:|---:|---:|
| 1.0 | 443 | 6,038 | 0 |
| 1.3 | 443 | 6,041 | 0 |
| 1.6 | 444 | 6,073 | 0 |
| 1.8 | 446 | 6,077 | 0 |
| 1.10 | 446 | 6,082 | 0 |

The parser expands non-additive source chains and distinguishes FAR-address import fixups from segment-only internal far-pointer fixups.

## CFG-owned direct call graph

| build | near direct | far internal | far import | indirect | static direct total |
|---|---:|---:|---:|---:|---:|
| 1.0 | 89 | 1,948 | 757 | 212 | 2,794 |
| 1.3 | 89 | 1,929 | 756 | 212 | 2,774 |
| 1.6 | 89 | 1,889 | 743 | 212 | 2,721 |
| 1.8 | 89 | 1,884 | 743 | 212 | 2,716 |
| 1.10 | 89 | 1,872 | 723 | 212 | 2,684 |

Indirect calls (`call *...`, `lcall *...`, vtable/function-pointer dispatch) remain separate; v5 does not invent static targets for them.

## Resolved examples

- `FUN_1000_0374 -> GDI!#103` (learned name `PTVISIBLE`)
- `FUN_1000_038c -> GDI!#104` (`RECTVISIBLE`)
- reachable entry path of `FUN_1000_03a4 -> GDI!#351` (`EXTTEXTOUT`)
- `FUN_1000_06ac` resolves internal calls to `FUN_1000_440e`, `FUN_1000_071c`, `FUN_1000_4432`, `FUN_1008_5fe0`, `FUN_1008_5fd0`, plus `KERNEL!#55` (`CATCH`)

## Import ordinal names

Names are a semantic overlay learned from Win16 1.0 decompiler call order only after the binary relocation resolves module+ordinal.

Current unique map:

- High: 100
- Medium-High: 117
- Review: 29
- total: 246

All 246 import symbols used by reachable Win16 1.0 import calls now have a candidate name. Review entries keep conflicting vote evidence and are not promoted to confirmed semantics.

Strong examples include `GDI!#104=RECTVISIBLE`, `GDI!#351=EXTTEXTOUT`, `GDI!#38=ESCAPE`, `KERNEL!#55=CATCH`, and `MMSYSTEM!#701=MCISENDCOMMAND`.

## Hidden / secondary entry evidence

The interval from one Ghidra function start to the next is often not one source function. v5 keeps a separate candidate ledger.

| build | candidates | High | Medium-High | Medium |
|---|---:|---:|---:|---:|
| 1.0 | 282 | 0 | 223 | 59 |
| 1.3 | 291 | 9 | 223 | 59 |
| 1.6 | 302 | 18 | 224 | 60 |
| 1.8 | 304 | 19 | 224 | 61 |
| 1.10 | 311 | 24 | 225 | 62 |

High means a reachable relocation-backed internal far call lands on an offset that is not an indexed function start. Medium-High/Medium code islands have a fresh prologue plus relocation-backed calls that are unreachable from the preceding indexed entry. They remain candidates for thunks/wrappers/secondary functions until separately closed.

## Validation

Against the Win16 1.0 decompiler-derived internal call graph, v5 shares 1,603 distinct internal caller/callee pairs; 1,601 common pairs also have identical call counts. The decompiler extraction has 154 additional pairs, many in interval-contaminated regions filtered by CFG. Four v5 pairs are not represented by the decompiler call-edge extraction and remain review cases.

## Artifacts

The external v5 dossier package contains the full expanded fixup table, CFG-refined fixups, resolved direct callgraph, indirect-call ledger, import-name evidence, corrected machine disassembly, and hidden-entry candidate ledger.

Next: promote High hidden entry points into standalone machine dossiers, map them across all Win16 builds, then separate compiler/MFC thunks from Nitemare 3D gameplay functions.

## Follow-up v6

The High-only binary entry/boundary closure and revised graph are recorded in
[WIN16_HIGH_HIDDEN_ENTRY_CLOSURE_V6_2026-10-01.md](WIN16_HIGH_HIDDEN_ENTRY_CLOSURE_V6_2026-10-01.md).
The figures above remain the historical v5 baseline.
