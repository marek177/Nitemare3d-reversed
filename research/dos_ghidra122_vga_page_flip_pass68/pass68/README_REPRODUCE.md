# Reproduce
Extract the dependency ZIP into baseline58/, preserving paths. Install unicorn==2.1.4 and run `python scripts/verify_vga_page_flip.py`. Expected108 passing cases. Included pass67/evidence/glyph_raster_tests.json supplies per-build page globals.

Ghidra12.2 PUBLIC20261016 / JDK25.0.2, baseline58/project N3D_Runtime54/inputs, process DOS*.exe readOnly/noanalysis, scriptPath pass68/ghidra_scripts, postScript ExportUifCallers.java with absolute pass68/evidence directory. Seeds and complete direct xref consumer bodies are included; runtime/JDK not duplicated.
