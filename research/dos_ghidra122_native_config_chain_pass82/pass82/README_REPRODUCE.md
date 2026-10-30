# Reproduce
Extract pass76 dependency and its baseline58 dependency. Preserve pass79/evidence/locations.json and pass74/evidence/DOS17.exe.xrefs.tsv,DOS18.exe.xrefs.tsv as included here. Run `python scripts/verify_native_config_chain.py` (Unicorn2.1.4). Expected12 passed for each binary.
Ghidra12.2/JDK25 exports: included script/seeds against pass76/project N3D_Runtime54/inputs, -readOnly -noanalysis.
