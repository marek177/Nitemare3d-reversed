# Reproduce pass61

From this artifact's root, extract dependencies/N3D_DOS_Ghidra122_xms_resource_store_pass58_20261029.zip to baseline58/. Python with Unicorn2.1.4 can then run:
```
python scripts/verify_resource_teardown.py
```
Input metadata is included at pass59/evidence/init_original_wrappers.json and pass60/evidence/lifecycle.json. The script reads the fresh pass61 Ghidra instruction exports and produces pass61/evidence/teardown.json. All324 scenarios execute original code twice; no callee or interrupt mocks are used, but heap/records are controlled fixtures.

Ghidra12.2 PUBLIC20261016 with JDK25.0.2 can reproduce the read-only exports from baseline58/project/N3D_Runtime54, folder /inputs. ExportXmsLifecycle.java consumes pass61/evidence/seeds.tsv and emits function instructions/C. ExportTeardownCallers.java emits incoming direct-call contexts. Logs retain the exact workspace commands and decompiler status. No modified project is shipped by this pass.
