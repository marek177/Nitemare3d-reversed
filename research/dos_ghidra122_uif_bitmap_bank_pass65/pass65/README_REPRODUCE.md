# Reproduce
Extract dependencies/N3D_DOS_Ghidra122_xms_resource_store_pass58_20261029.zip into baseline58/, preserving paths. With unicorn==2.1.4 run `python scripts/verify_uif_bitmap_bank.py`. Expected: 48 cases pass, output pass65/evidence/bitmap_bank_tests.json.

Ghidra exports: Ghidra12.2 PUBLIC20261016 / JDK25.0.2; baseline58/project N3D_Runtime54/inputs; process DOS*.exe readOnly/noanalysis; scriptPath pass65/ghidra_scripts; postScript ExportUifCallers.java with absolute pass65/evidence directory. Seeds are included. Helper instruction evidence comes from baseline pass7 disassembly and is cross-checked by execution of original MZ bytes. Runtime/JDK not duplicated.
