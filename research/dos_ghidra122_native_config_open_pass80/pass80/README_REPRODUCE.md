# Reproduce
Extract the included pass76 dependency ZIP and its baseline58 dependency. Recreate baseline58/ with its analysis/inputs and pass7/evidence paths. Keep pass79/evidence/locations.json from this bundle at the same relative path.
Run `python scripts/verify_config_native_open.py` with Unicorn2.1.4. Expected:20 passed.
The Ghidra export script and seeds are included; use Ghidra12.2/JDK25 against pass76/project N3D_Runtime54/inputs with -readOnly -noanalysis and ExportXmsLifecycle.java, output pass80/evidence.
