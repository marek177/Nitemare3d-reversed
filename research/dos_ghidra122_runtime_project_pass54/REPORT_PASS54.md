# Pass 54 — clean runtime-image Ghidra project

## Finding
Created a separate Ghidra12.2 project from six reconstruction MZ images whose relocated payloads were proved identical to original-stub outputs in pass53. The Ghidra-loaded bytes are checked against those original outputs before analysis and after saving/reopening. This replaces the packed-file layout with the complete unpacked runtime layout, including correct segment relocation words and initialized bytes.

## Provenance and procedure
Original packed files were exported from the supplied database without reading patched memory (pass53). Their own decompression/relocation stub generated the reference images without mocked unpacking instructions. This pass imports the independently reconstructed MZ files using Ghidra's MZ loader at base1000, then compares every payload byte to that reference. Seven supplied version names represent six distinct images; DOS18.exe also covers the supplied DOS1.9 image.

A static DS context is configured to the startup-confirmed normal-runtime values3360,3395,339b,374a,3754,376d for DOS10,11,12,15,17,18 respectively. This is an analysis assumption, not proof DS is preserved on every path. The CRT initially has PSP DS, and specialized routines may override DS. The final verifier checks the resulting context at three known sound entries per build.

No comments, labels, prototypes or function bodies were copied from the packed project. Original databases and pass52's partial call repair remain separate. New automatic function recognition is not a semantic recovery claim.

## Verification artifacts
- Each prepared TSV reports full pre-analysis payload-byte equality and configured DS.
- Each analyzed TSV inventories memory blocks, automatically recognized functions and instructions.
- Each verified TSV reports post-reopen payload equality, DS at dispatcher/cache/fallback entries and focused decompilation results.
- Diagnostic C files contain generated output for those functions when recognized and decompilation completes.
- summary.json gives exact final counts and diagnostic totals; no completeness percentage is inferred.

Final checks target18 function entries: original sound dispatcher (pass47), cache (pass50), fallback (pass51) across six images. Successful C generation does not establish inferred argument types, control-flow fidelity, or hardware semantics. Retain original instruction and emulation evidence when interpreting these C outputs.

## Known diagnostics and corrected setup attempt
The first DOS11 pre-script failed because its context range crossed the separate HEADER address space. The script was corrected to set context independently on default-space memory blocks. DOS11 was then overwritten by a fresh import with the corrected pre-script before final verification. The initial log is preserved for traceability.

Autoanalysis emitted p-code/constructor warnings and address-resolution exceptions, including an out-of-bounds decompiler address. These are unresolved analysis defects, not proved execution faults in the game. Import/save completion and byte equality are separate from decompiler quality. The default autoanalysis configuration was used with a90-second per-file limit; any timeout or diagnostic status is recorded in the logs and summary. Do not assume all recognized functions are valid or that indirect calls are resolved.

## Outcome and next test
The project now provides the correct unpacked bytes and a documented normal-runtime DS assumption for further RE. Full-game behavior, audio, VGA state, timing and1:1 parity are still unverified. Next: inspect the remaining p-code failures at their instruction boundaries, recover segment context locally, and compare the sound function C outputs against the independently verified assembly and state transitions. Only transfer packed-project annotations after verifying the referenced bytes and boundaries.

Confidence: High for imported runtime-byte equivalence and the explicit DS checks; automatic function boundaries and generated C remain diagnostic until individually verified.

## Focused ABI correction
The first generated cache/fallback C incorrectly modeled return values as a single word. Applying a plain four-byte return type under the default calling-convention model generated an implicit return-buffer pointer, which is also incorrect for these routines. The final project therefore uses explicit custom return storage DX:2,AX:2, an unsigned four-byte packed result, and a single two-byte resource_id at stack+4 (far-return frame). This is supported by pass50/pass51 original-instruction executions. Twelve function interfaces are corrected; dispatcher return semantics are not changed. Final read-only verification checks both return storage and argument storage before decompiling again. Initial and intermediate ABI logs are preserved; only the final explicit-storage result is the intended interface.

The DOS11 replacement also exposed an inconsistent project index: its new database existed on disk while the index omitted it. Ghidra's index rebuild recovered the new entry and reported the superseded database as orphaned. index_before_rebuild.txt and verify_rebuilt_index.log record this. A subsequent reopen found DOS11 without another index rebuild. These recovery steps are project-maintenance findings, not game behavior.
