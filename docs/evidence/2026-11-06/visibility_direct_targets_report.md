# Visibility direct-call correction — 2026-11-06

The two immediate FAR CALLs at 0AEA:0DCE and 0AEA:0DD8 resolve to logical 0000:0000 and 0000:01E0. Both segment operands have MZ relocation entries (linear offsets48241 and48251). A zero segment in this unloaded image denotes the first code segment; it is not an unresolved callback placeholder. At loadbase B, their ordinary relocated targets are B:0000 and B:01E0. Global code-write closure is still open.

0000:0000 searches an array at segment21FD, offset3076, stride18, bounded by the signed word at offset0000. It compares the caller's FAR tile address with record+4/+6 and returns the matching record in DX:AX. Its missing-record branch calls0FBA:000C with42h; that branch's ultimate behavior is not closed here. 0000:01E0 returns AL1 for record word+8 equal0 or4, AL0 otherwise. No recovered door-state names are asserted.

The original helper06D2, grid0CC0 and these two callees execute together in35 synthetic CPU cases with one interior tile and a matching record. Trait2 alone passes; trait2|4 blocks; trait2|8 passes exactly for state0/4; trait2|4|8 blocks regardless of the tested state. SI/DI/BP/DS and the FAR return frame remain checked. These cases use the skip-direction variant. The3249 empty-grid cases also pass again. The first new harness attempt stopped at address0 because Unicorn's old until=0 sentinel collided with the real target; the corrected wrapper uses an unused end address and retains the explicit FAR-return stop hook.

This corrects the unresolved-target wording in the2026-10-31 Omnificent report and static-provenance JSON. Historical ZIPs remain immutable. Native runtime call bytes, all wall-state lifecycle transitions, aliases, IRQs, absent-record behavior and successful04C7:0C37 execution remain open.

On2026-11-06 the previous PID62904 is absent from the current process inventory; its saved control file is historical state, not a live session. No attempt is made to resume a nonexistent process. Runtime must start a new independently identified run before collecting further game coverage. The full DOS/Win16 GOAL remains incomplete.

Reproduce using the published verify_visibility_door_targets.py alongside verify_actor_visibility_cpu.py, a privately supplied hash-matched unpacked image, Unicorn2.1.4, and --output-dir. No original executable or asset bytes are included in this supplement.
