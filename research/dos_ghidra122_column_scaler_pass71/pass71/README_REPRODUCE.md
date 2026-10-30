# Reproduce
Extract the dependency ZIP into baseline58/, preserving paths. With unicorn==2.1.4 run `python scripts/verify_texture_column_scaler.py`; expected300 passing cases, output pass71/evidence/column_scaler_tests.json.

Ghidra12.2 PUBLIC20261016 / JDK25.0.2, baseline58/project N3D_Runtime54/inputs, process DOS*.exe readOnly/noanalysis, scriptPath pass71/ghidra_scripts, postScript ExportUifCallers.java with absolute pass71/evidence directory. Seeds include direct references and `at` locations for indexed readers. The exporter uses getFunctionContaining for `at`; this addresses missing direct-reference discovery. Runtime/JDK not duplicated.
