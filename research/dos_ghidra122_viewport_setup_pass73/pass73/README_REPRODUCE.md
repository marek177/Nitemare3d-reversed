# Reproduce
Extract the dependency ZIP into baseline58/, preserving paths. With unicorn==2.1.4 run `python scripts/verify_viewport_setup.py`; expected72 passing fixtures. Included pass72/evidence/clip_table_tests.json supplies builder globals. Output pass73/evidence/viewport_tests.json.

Ghidra12.2 PUBLIC20261016 / JDK25.0.2, baseline58/project N3D_Runtime54/inputs, process DOS*.exe readOnly/noanalysis, scriptPath pass73/ghidra_scripts, postScript ExportUifCallers.java with absolute pass73/evidence directory. Seeds and complete direct-reference consumer bodies are included. Runtime/JDK not duplicated.
