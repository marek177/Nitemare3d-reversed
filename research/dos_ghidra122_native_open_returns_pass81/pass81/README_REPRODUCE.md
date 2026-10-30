# Reproduce
Extract dependencies/pass76 ZIP, then its baseline58 dependency so baseline58/analysis/inputs/DOS17.exe and DOS18.exe exist. Run `python scripts/verify_native_open_returns.py` with Unicorn2.1.4. Expected17 39 passed,18 39 passed. Script regenerates pass81/evidence/return_tests.json.
Ghidra12.2/JDK25: use included ExportXmsLifecycle.java and seeds.tsv against pass76/project N3D_Runtime54/inputs, readOnly/noanalysis.
