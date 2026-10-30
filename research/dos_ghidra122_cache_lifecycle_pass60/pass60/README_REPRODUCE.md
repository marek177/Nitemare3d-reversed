# Reproduce pass60

Extract dependencies/N3D_DOS_Ghidra122_xms_resource_store_pass58_20261029.zip to baseline58/ at this artifact's root. The included pass59/evidence/init_original_wrappers.json supplies already recovered per-build initializer/global metadata. With Python and Unicorn2.1.4 run:
```
python scripts/verify_cache_lifecycle.py
```
The script creates/updates pass60/evidence/lifecycle.json and asserts768 controlled scenarios. Original code runs twice per scenario. Only the indirect XMS driver call is simulated; all buffers and records are synthetic.

For caller xrefs run Ghidra12.2 PUBLIC20261016 with JDK25.0.2, open baseline58/project/N3D_Runtime54, folder /inputs, read-only/noanalysis, and run pass60/ghidra_scripts/ExportLifecycleCallers.java with pass60/evidence as its directory argument. Exact commands and results are preserved in pass60/ghidra.log and per-build caller TSVs. No project changes were made.
