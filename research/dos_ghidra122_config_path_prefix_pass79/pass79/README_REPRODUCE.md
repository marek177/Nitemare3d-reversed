# Reproduce
Extract the bundled pass76 dependency into the working root; extract its pass58 dependency into baseline58/. Preserve paths. With unicorn==2.1.4 run `python scripts/verify_config_path_prefix.py`; expected44 passing fixtures. Included pass78/evidence/native_scan_tests.json supplies native scan entries/stack limits. It does not require a separate pass78 archive.

Ghidra12.2 PUBLIC20261016 / JDK25.0.2, pass76/project N3D_Runtime54/inputs, process DOS*.exe readOnly/noanalysis, scriptPath pass79/ghidra_scripts, postScript ExportXmsLifecycle.java with absolute pass79/evidence directory. Seeds cover17/18; other processed binaries have no selected functions. Runtime/JDK not duplicated.
