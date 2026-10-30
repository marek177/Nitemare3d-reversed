# Reproduce
Open pass76/project/N3D_Runtime54.gpr with Ghidra12.2; this is a separate repaired copy including its .rep folder. Do not detach the pair. Baseline remains in the dependency ZIP.

CPU evidence: extract dependencies/N3D_DOS_Ghidra122_xms_resource_store_pass58_20261029.zip into baseline58/, preserving paths. Install unicorn==2.1.4, run `python scripts/verify_parser_switch_recovery.py`; expected140 dispatch cases,892 original instruction byte comparisons.

Repair from baseline: copy baseline58/project to a separate destination, then run Ghidra12.2 PUBLIC20261016 / JDK25.0.2 analyzeHeadless on N3D_Runtime54/inputs, process DOS*.exe, noanalysis, scriptPath pass76/ghidra_scripts, postScript RebuildParserListing.java with absolute pass76/evidence directory. Omit readOnly to save the copy. To independently check saved state, run again with readOnly and CheckParserRecovery.java instead; it does not rebuild. Expected six decompile=true, mismatch=0 results.

Required pass75 metadata/reference instruction JSON are included under their original paths. The dependency archive contains all MZ inputs/specs and baseline native project. Runtime/JDK not duplicated.
