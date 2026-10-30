# Reproduce
Extract the dependency ZIP into baseline58/, preserving paths. Install unicorn==2.1.4 and run `python scripts/verify_uif_text_metrics.py`. Expected: 156 cases pass. Included pass65/evidence/bitmap_bank_tests.json supplies per-build globals.

Ghidra exports use 12.2 PUBLIC20261016, JDK25.0.2 and baseline58/project N3D_Runtime54/inputs, process DOS*.exe readOnly/noanalysis, scriptPath pass66/ghidra_scripts, postScript ExportUifCallers.java with absolute pass66/evidence directory. Seeds are included. Center instruction listings are extracted from baseline audit and cross-checked by original execution. Runtime/JDK not duplicated.
