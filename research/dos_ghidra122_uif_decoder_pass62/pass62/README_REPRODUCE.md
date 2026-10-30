# Reproduce pass 62

Extract this archive into a work directory. Extract `dependencies/N3D_DOS_Ghidra122_xms_resource_store_pass58_20261029.zip` into `baseline58/` in the same directory. Preserve paths. Python requires unicorn==2.1.4. Run `python scripts/verify_uif_decoder.py`; output is `pass62/evidence/uif_decoder_tests.json`.

Ghidra exports were made read-only with Ghidra 12.2 PUBLIC 20261016 and JDK 25.0.2, using the baseline runtime project and the provided Java export script / seeds. The runtime and JDK archives are not duplicated. Evidence TSV contains exact original instruction bytes and decompilation status. The historical export role `resource_reload` identifies the UI image decoder, as corrected in REPORT.md.
