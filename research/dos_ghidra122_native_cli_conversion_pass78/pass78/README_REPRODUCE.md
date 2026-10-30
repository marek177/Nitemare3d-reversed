# Reproduce
Extract the bundled pass76 dependency into the working root. Extract its dependency pass58 ZIP into baseline58/. Preserve paths. With unicorn==2.1.4 run `python scripts/verify_native_sscanf.py` (120 cases), then `python scripts/verify_cli_native_conversion.py` (215 cases). Explicit CRT stack-limit fixtures are documented in the report and metadata.

Ghidra12.2 PUBLIC20261016 / JDK25.0.2: pass76/project N3D_Runtime54/inputs, process DOS*.exe readOnly/noanalysis, scriptPath pass78/ghidra_scripts, postScript ExportXmsLifecycle.java with absolute pass78/evidence directory. All six wrapper decompilations succeed. Runtime/JDK not duplicated.
