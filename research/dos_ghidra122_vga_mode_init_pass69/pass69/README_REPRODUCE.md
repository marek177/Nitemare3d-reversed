# Reproduce
Extract the bundled dependency ZIP into baseline58/, preserving paths. With unicorn==2.1.4 run `python scripts/verify_vga_mode_init.py`; expected96 passing cases, output pass69/evidence/mode_init_tests.json. BIOS and VGA IN boundaries are synthetic; original clearing code executes on flat mapped CPU memory.

Ghidra12.2 PUBLIC20261016 / JDK25.0.2, baseline58/project N3D_Runtime54/inputs, process DOS*.exe readOnly/noanalysis, scriptPath pass69/ghidra_scripts, postScript ExportXmsLifecycle.java with absolute pass69/evidence directory. Seeds and complete original clear instructions included. Runtime/JDK not duplicated.
