# Reproduce
Extract the bundled dependency ZIP into baseline58/, preserving paths. With unicorn==2.1.4 run `python scripts/verify_uif_glyph_raster.py`. Expected: 162 cases pass; output pass67/evidence/glyph_raster_tests.json. This uses a stated sequencer map-mask model, not a complete VGA emulator.

Ghidra12.2 PUBLIC20261016 / JDK25.0.2 exports use baseline58/project N3D_Runtime54/inputs, process DOS*.exe readOnly/noanalysis, scriptPath pass67/ghidra_scripts, postScript ExportXmsLifecycle.java with absolute pass67/evidence directory. Seeds are included. Runtime/JDK not duplicated.
