# Pass 76 — persistent Ghidra command-parser switch recovery

## Finding
All six parser functions now decompile in Ghidra12.2 after rebuilding their exact instruction listings, excluding switch data from the body, setting CS context and supplying raw-table-derived indirect-jump overrides. The repaired native project was saved separately, reopened read-only and successfully decompiled again without repair. This closes the five decompilation failures recorded in pass75; it does not prove complete parser semantics or whole-game parity.

## Evidence
| Status | Claim | Source | Confidence |
|---|---|---|---|
| Confirmed | 892 parser instructions match relocalized original MZ bytes and reference listings | verify_parser_switch_recovery.py, rebuild.tsv | High |
| Confirmed | Every140 table case dispatches to its recorded original target | Original parser execution, switch_recovery_tests.json | High |
| Confirmed | All six parsers decompile after repair | Final rebuild.tsv and C exports | High |
| Confirmed | Saved native project retains recovery | Fresh CheckParserRecovery read-only run, readback.tsv | High |
| Confirmed | Rebuilding listing and adding CS alone left five failures | ghidra.log, context.log before override | High |
| Inferred | Incorrect/incomplete indirect-branch recovery caused the prior decompiler excursions | Same listing+CS fails; adding explicit verified targets succeeds | High for this repair, not a general Ghidra diagnosis |
| Unknown | Complete correctness of inferred C types, prototypes and all branch effects | Decompilation success is not semantic verification | Further RE needed |

## Repair model
For each parser, use the supplied exact instruction ranges rather than a contiguous function range containing jump-table data. Clear and rebuild instructions only at known code addresses; set CS over the parser span; define the function body as the union of instruction byte ranges. Read the original near-target switch table with that build's actual subtraction base and bound, and write a Ghidra JumpTable override using unique target addresses. The complete case mapping remains independently retained by the original table and runtime test; the override supplies destinations, not invented labels.

The combination preserves code bytes. No executable bytes were patched. Table cases include repeated/default destinations. DOS1.0/1.1/1.2/1.5 have23 table entries; DOS1.7 and supplied1.8/1.9 have24. Supplied1.8/1.9 are identical binaries. Native baseline project remains unchanged; pass76/project/N3D_Runtime54.gpr and .rep are the repaired copy. Its familiar project basename is retained for direct opening.

## Verification
Reference instruction counts: DOS10=127; DOS11=149; DOS12=149; DOS15=149; DOS17=159; DOS18=159, total892. Every instruction's expected bytes are checked against the original MZ payload after its actual1000h relocation. The Ghidra rebuilt listing agrees byte-for-byte and has zero mismatches. All140 original computed dispatch cases execute with near argv fixtures and stop at the selected case entry. Startup helper calls are mocked before dispatch; branch bodies are not executed by this graph-recovery test. The width branch's behavior was independently exercised in pass75.

A separate persisted-project check makes no listing/context/override changes, verifies all892 instructions are within parser bodies, and decompiles each saved function. All six results are true with zero mismatches. This establishes persistence and local reconstruction only. It does not validate every decompiled statement, caller stack state, native sscanf, OS behavior, complete startup or full-game parity.

## Artifacts and limits
Each DOS*.instructions.tsv preserves selected instruction bytes; DOS*.switch.tsv preserves override destinations; DOS*.rebuild.tsv records instruction equality and final decompile status; DOS*.readback.tsv records the independent saved-project check. C exports include warnings and inferred prototypes as produced. Diagnostic logs preserve failed earlier attempts. All repairs are reproducible with the supplied Java scripts and dependency project. The native project copy is included in the ZIP; GitHub stores textual scripts, C and evidence rather than binary database files.

## Unknowns and next test
Audit remaining parser branches using verified cases and native conversion routines. Recover in-game viewport editing separately from CLI. Continue projection/scaler caller stack and renderer parity work; do not equate six successful decompilations with complete function recovery. Confidence High for byte/CFG destination recovery and project persistence; incomplete for all parser behaviors.
