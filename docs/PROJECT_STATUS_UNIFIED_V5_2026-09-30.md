# Nitemare 3D unified function project — v5 Win16 NE fixup/callgraph closure

Date: 2026-09-30

## What v5 changes

v5 resolves the Win16 NE relocation/fixup layer instead of interpreting the raw operands of `lcall` instructions as final addresses. In an NE image, relocation data follows segment data for segments flagged as containing fixups; each relocation record identifies a source type, target type, and a source chain. Non-additive records can therefore cover many call sites through a linked source chain.

The v5 parser expands those chains and combines them with CFG reachability from each indexed function entry. This is important because a linear interval from one Ghidra `FUN_*` start to the next can contain additional thunks/wrappers or secondary entry points after a `ret/lret`.

## Corrected disassembly parser

During this pass an internal analysis bug was found and fixed: GNU `objdump` could wrap the byte encoding of long 16-bit instructions onto another output line. The old parser could interpret the continuation bytes as a new instruction, causing CFG traversal to stop early. v5 forces `--insn-width=16` and rebuilds the Win16 machine layer before computing reachability.

For Win16 1.0 the corrected CFG contains 43,979 reachable instructions versus 20,282 linear-but-unreachable instructions inside the current Ghidra-derived intervals; 410/959 indexed functions contain some such trailing/non-reachable interval content.

## NE relocation/fixup expansion

| Win16 build | Relocation records | Expanded fixup source sites | Broken chains |
|---|---:|---:|---:|
| 1.0 | 443 | 6,038 | 0 |
| 1.3 | 443 | 6,041 | 0 |
| 1.6 | 444 | 6,073 | 0 |
| 1.8 | 446 | 6,077 | 0 |
| 1.10 | 446 | 6,082 | 0 |

In 1.0, for example, the expanded sites comprise 1,145 raw FAR-address call sites, 3,056 segment-only internal far-call fixups, 1,818 segment-reference data fixups and 19 offset16 fixups before CFG ownership is applied.

## CFG-owned direct call graph

After relocation resolution and reachability filtering:

| Win16 build | near direct | far internal | far import | indirect calls | static direct total |
|---|---:|---:|---:|---:|---:|
| 1.0 | 89 | 1,948 | 757 | 212 | 2,794 |
| 1.3 | 89 | 1,929 | 756 | 212 | 2,774 |
| 1.6 | 89 | 1,889 | 743 | 212 | 2,721 |
| 1.8 | 89 | 1,884 | 743 | 212 | 2,716 |
| 1.10 | 89 | 1,872 | 723 | 212 | 2,684 |

The indirect set is deliberately kept separate (`call *...`, `lcall *...`, vtable/function-pointer calls). v5 does not invent a static target for them.

## Example: raw operand versus true NE target

A call in Win16 1.3 may appear in the raw file as:

`9A FF FF 00 00`

The bytes are not the final API address. The NE relocation record and source chain identify the imported target. The same applies to segment-only internal fixups, where the offset half can already be present in the instruction while the selector word is a source-chain link to be replaced by the loader.

Concrete verified examples from the current binaries include:

- `FUN_1000_0374` -> `GDI!#103` (learned name `PTVISIBLE`)
- `FUN_1000_038c` -> `GDI!#104` (`RECTVISIBLE`)
- `FUN_1000_03a4` reachable entry path -> `GDI!#351` (`EXTTEXTOUT`)
- `FUN_1000_06ac` -> internal `FUN_1000_440e`, `FUN_1000_071c`, `FUN_1000_4432`, `FUN_1008_5fe0`, `FUN_1008_5fd0`, plus `KERNEL!#55` (`CATCH`)

## Import ordinal -> API-name recovery

The Win16 1.0 decompiler body is used as a semantic overlay, not as relocation truth. A module+ordinal is first resolved from the binary. API names are then learned only when call order/count in the mapped 1.3 body agrees with the 1.0 decompiler call sequence.

Current unique import-symbol name map:

- 100 High confidence
- 117 Medium-High confidence
- 29 Review
- total 246 symbols used by reachable Win16 1.0 import calls

All 246 reachable unique import symbols in 1.0 now have a candidate name. `Review` means conflicting call-sequence votes exist; the majority name is retained for triage but is not promoted to confirmed semantics.

Examples with strong evidence:

- `GDI!#104 = RECTVISIBLE`
- `GDI!#351 = EXTTEXTOUT`
- `GDI!#38 = ESCAPE`
- `KERNEL!#55 = CATCH`
- `MMSYSTEM!#701 = MCISENDCOMMAND`
- `WING!#1009 = WINGSTRETCHBLT` (Medium-High, single direct wrapper observation)
- `WING!#1010 = WINGBITBLT` (Medium-High, single direct wrapper observation)
- `KERNEL!#1 = FATALEXIT` (Medium-High, call-order recovery from the 1.0 body)

## Function-boundary / hidden-entry evidence

CFG reachability confirms that the old “from this FUN start to the next FUN start” interval is not equivalent to one source function in many places.

Example: the linear interval beginning at `FUN_1000_03a4` contains the real `EXTTEXTOUT` wrapper and then additional code islands after its `lret`. Those later relocation-backed calls are no longer attributed to `FUN_1000_03a4` in the v5 call graph.

A separate candidate ledger now records:

| Build | unique hidden/secondary candidates | High | Medium-High | Medium |
|---|---:|---:|---:|---:|
| 1.0 | 282 | 0 | 223 | 59 |
| 1.3 | 291 | 9 | 223 | 59 |
| 1.6 | 302 | 18 | 224 | 60 |
| 1.8 | 304 | 19 | 224 | 61 |
| 1.10 | 311 | 24 | 225 | 62 |

High candidates are relocation-backed internal far-call targets that do not match an indexed function start. Medium-High/Medium candidates are unindexed prologue code islands containing relocation-backed calls that are unreachable from the preceding indexed entry. These are candidates for wrappers/thunks/secondary functions, not yet canonical source-function identities.

## Validation against the Win16 1.0 C call graph

For internal `FUN_* -> FUN_*` edges, the corrected static direct graph shares 1,603 distinct caller/callee pairs with the decompiler-derived graph; 1,601 of those common pairs also have identical call counts. The C export has 154 additional internal pairs, many located in contaminated/linear-only regions that v5 intentionally does not mark reachable. Four v5 pairs are not represented by the decompiler call-edge extraction and remain explicit review cases.

This comparison is a validation aid, not a rule that either representation is automatically correct.

## New v5 artifacts

- `win16_ne_fixup_sites_v5.csv` — every expanded NE relocation source site.
- `win16_ne_fixup_sites_cfg_refined_v5.csv` — relocation sites plus CFG ownership/reachability.
- `win16_resolved_far_calls_cfg_named_v5.csv` — reachable resolved far calls with learned API names.
- `win16_static_direct_callgraph_v5.csv` — unified near + far direct call graph.
- `win16_indirect_calls_v5.csv` — unresolved indirect/vtable/function-pointer call sites.
- `win16_import_ordinal_name_map_v5.csv` — module+ordinal API-name evidence with confidence/votes.
- `win16_hidden_entry_candidates_aggregated_v5.csv` — conservative hidden/secondary-entry ledger.
- `win16_10_machine_functions_cfg_v5.csv` — fresh 1.0 machine disassembly with reachable offsets.

## Next closure target

1. turn High hidden/secondary-entry candidates into standalone machine dossiers;
2. map those entry points across all five Win16 builds;
3. separate compiler/MFC import thunks from Nitemare 3D gameplay routines;
4. resolve the 29 Review import-name mappings against independent Win16 export/ordinal tables;
5. then revisit the materially modified Win16 functions using the corrected CFG-aware call graph.