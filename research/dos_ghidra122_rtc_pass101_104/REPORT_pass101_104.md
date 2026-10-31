# Nitemare3D DOS — passes101–104, 2026-10-31

Six distinct supplied EXEs represent labels1.0,1.1,1.2,1.5,1.7 and byte-identical1.8/1.9. This batch closes specific cached-clock unknowns with fresh Ghidra12.2 mapping and native Unicorn execution.

- Pass101: recover the previously unlisted RTC ISR;576 IRQ/context/wrap cases followed by native cached reader.
- Pass102:96 RTC lifecycles,480 original setup calls; exact CMOS/PIC/vector changes and partial teardown.
- Pass103:5376 isolated state1 animation deadline cases; unsigned comparisons, one-frame advance and rescheduling from now.
- Pass104:144 original reader/ISR interleavings;24 return mixed values at16-bit carry boundaries.

Total6192 test cases/lifecycles, with distinct scopes: do not equate these counts with game parity or function coverage.36 fresh Ghidra decompilations (30 runtime helpers and6 animation-slot functions) accompany native evidence; ISR decompiler stack warnings make instruction traces authoritative.

Read pass101–104/REPORT.md for confirmed/inferred/unknown distinctions, exact addresses, fixtures and implementation constraints. The full JSON case sets are in this ZIP; the repository stores compact summaries plus scripts, C/instruction exports, provenance and hashes.

Reproduce: install unicorn==2.1.4 capstone==5.0.7; from archive root run the four scripts under scripts/. Original MZ input EXEs, mapping JSON and prior counter evidence needed by those scripts are bundled. Ghidra reproduction uses the included pass76 project dependency, then pass101 and pass103 Java scripts/seeds; headless creates missing ISR functions only in read-only temporary sessions. Ghidra12.2/JDK25 binaries are not bundled.

Remaining work: real IRQ timing and whole-frame caller traces; actual animation descriptors/state2/helpers; other cached-time readers; renderer, projectiles and remaining gameplay code. Full reverse engineering and1:1 gameplay parity are not claimed.
