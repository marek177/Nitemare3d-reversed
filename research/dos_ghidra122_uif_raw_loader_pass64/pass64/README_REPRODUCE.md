# Reproduce
Extract the dependency ZIP into baseline58/. Copy the included pass63/evidence/lookup_tests.json into the preserved path. Run `python scripts/verify_uif_raw_loader.py` with unicorn==2.1.4. Expected: 48 cases pass. Boundary mocks do not transfer payload bytes.

Ghidra: 12.2 PUBLIC 20261016, JDK25.0.2, baseline58/project N3D_Runtime54/inputs, process DOS*.exe read-only/noanalysis, scriptPath pass64/ghidra_scripts, postScript ExportUifCallers.java with absolute pass64/evidence directory. Runtime/JDK are not duplicated. Seeds and complete exports are included.
