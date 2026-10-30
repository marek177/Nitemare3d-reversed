# Reproduce pass59

The dependency ZIP contains the exact recovered pass58 snapshot, including six reconstruction EXEs, Ghidra project, original-unpacker reference images, prior metadata and instruction exports. Extract dependencies/N3D_DOS_Ghidra122_xms_resource_store_pass58_20261029.zip into baseline58/ at this artifact's root.

Python tests require Unicorn2.1.4. From the artifact root run:
```
python scripts/verify_xms_init_phase.py
python scripts/verify_xms_init_original_wrappers.py
python scripts/verify_dimension_record_store.py
```
The initialization experiment intentionally begins at the post-heap phase with an established synthetic frame. The second script removes the wrapper-call mocks used by the first. It still mocks the manager/multiplex boundary; do not describe it as a real XMS driver test.

For fresh Ghidra exports use Ghidra12.2 PUBLIC20261016 with JDK25.0.2, project baseline58/project/N3D_Runtime54, folder /inputs. Run ExportXmsLifecycle.java and ExportAnalysisFrontier.java as read-only post-scripts with evidence directory argument. The exact commands/logs in this artifact used this workspace's absolute paths; adjust them to the extracted root. Native Linux decompile/sleigh binaries must be executable after archive extraction.

No modified Ghidra project is shipped by this pass: the dependency is the previously verified pass58 project. New outputs are instruction/C exports, tests, state traces and frontier inventory. Earlier diagnostic logs record the native permission issue; final_ghidra.log and the final TSVs are authoritative for successful fresh decompilation.
