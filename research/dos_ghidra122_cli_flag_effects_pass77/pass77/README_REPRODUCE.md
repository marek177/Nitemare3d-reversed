# Reproduce
Extract dependencies/N3D_DOS_Ghidra122_parser_recovery_pass76_20261030.zip into the working root; it supplies the repaired pass76/project and pass75 metadata. Extract that archive's dependencies/N3D_DOS_Ghidra122_xms_resource_store_pass58_20261029.zip into baseline58/. Preserve paths.

With unicorn==2.1.4 run `python scripts/verify_cli_flag_effects.py`; expected168 passing fixtures. This pass directly reads recovered Ghidra evidence from pass76; it does not alter the native project. All parser helper calls are mocked as documented. New output pass77/evidence/flag_tests.json; option_map.csv provides static classifications beyond tested direct flags.
