# Reproduce
Extract the dependency ZIP into baseline58/, preserving paths. With unicorn==2.1.4 run `python scripts/verify_config_viewport_load.py`; expected84 passing fixtures. Included pass73/evidence/viewport_tests.json supplies per-build setup globals. Output pass74/evidence/config_load_tests.json.

Ghidra12.2 PUBLIC20261016 / JDK25.0.2, baseline58/project N3D_Runtime54/inputs, process DOS*.exe readOnly/noanalysis, scriptPath pass74/ghidra_scripts, postScript ExportUifCallers.java with absolute pass74/evidence directory. `at` references missing containing functions are reported explicitly and skipped for decompilation. Runtime/JDK not duplicated.
