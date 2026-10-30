# Reproduce
Extract the dependency ZIP into baseline58/, preserving paths. With unicorn==2.1.4 run `python scripts/verify_column_clip_tables.py`; expected60 passing fixtures, output pass72/evidence/clip_table_tests.json. Each fixture checks all511 entries in both arrays.

Ghidra12.2 PUBLIC20261016 / JDK25.0.2, baseline58/project N3D_Runtime54/inputs, process DOS*.exe readOnly/noanalysis, scriptPath pass72/ghidra_scripts, postScript ExportUifCallers.java with absolute pass72/evidence directory. Seeds use `at` getFunctionContaining to export builders. Runtime/JDK not duplicated.
