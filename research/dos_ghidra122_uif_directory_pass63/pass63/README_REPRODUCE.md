# Reproduce
Extract the dependency ZIP into baseline58/ while preserving paths. Install unicorn==2.1.4 and run `python scripts/verify_uif_lookup.py`. Results go to pass63/evidence/lookup_tests.json. Tests require original MZ inputs and specs from baseline58.

Ghidra 12.2 PUBLIC 20261016 / JDK25.0.2 exports: use baseline58/project N3D_Runtime54/inputs, read-only/noanalysis, process DOS*.exe, scriptPath pass63/ghidra_scripts, postScript ExportXmsLifecycle.java with absolute pass63/evidence directory. Seeds identify exact functions. Runtime/JDK are not duplicated in this archive.
