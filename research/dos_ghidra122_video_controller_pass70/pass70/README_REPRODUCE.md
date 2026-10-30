# Reproduce
Extract the bundled dependency ZIP into baseline58/, preserving paths. With unicorn==2.1.4 run `python scripts/verify_vga_mode_controller.py`. Expected84 passing fixtures; all511 reciprocal dwords are compared in each successful-enter case.

Ghidra12.2 PUBLIC20261016 / JDK25.0.2, baseline58/project N3D_Runtime54/inputs, process DOS*.exe readOnly/noanalysis, scriptPath pass70/ghidra_scripts, postScript ExportXmsLifecycle.java with absolute pass70/evidence directory. Current seeds export controller and reciprocal functions. xrefs.tsv came from ExportUifCallers with mode_init seeds from pass69 and identifies controller callers of initialization. Runtime/JDK not duplicated.
