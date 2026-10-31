# Omnificent provenance and natural RNG activation conditions — 2026-10-31

## Result and proof status

DS:4153 is bound to the original cheat-menu item **Omnificent (all-cunning)**. It is file offset15 of the16-byte CONFIG.SAV block loaded toDS:4144..4153. The supplied config contains01. Original code first defaults this byte to0 and then reads the file, producing1. The original Play Demo case subsequently clears it to0. These transitions are native execution, not debugger flag writes. The formatter uses markerI. The exact supported behavioral meaning is suppression of two actor detection/activation paths; a universal invisibility or all-AI claim is not proved. The author's [description](https://dgray.com/n3dpage.htm) confirms registered cheat modes exist, but is not evidence for this ABI or flag mapping.

The frozen native K prefix ends at render counter306, player tile(24,60), RNG state1, with no target-site hit. The later continuous measurement is a separate ongoing prefix and is not included or stitched into this snapshot. Thus the natural success predicate is recovered, but a successful original-game04C7:0C37 invocation is NOT claimed by this archived prefix.

## Exact provenance

The source is unpacked EXE SHA5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3; the executed packed file remains SHAa3fa02335e1d8bc531918f3bfaa66217aef65c81e562a2fdf1c749be652ca485. Fourteen inherited function memberships are byte matched and hashed. Boundaries remain UNKNOWN.

* 0277:0CA3 clears the default byte.0277:0CE5 calls11EE:1E14 with fd, buffer4144, length16; the observed return at0CEA isAX16 and the buffer SHA matches CONFIG.SAV. The byte changes0→1.0277:0D2A is the static16-byte write path; this is not a newly observed persistence write.
* 20B9:12A2 is an18-byte menu record, ID21h, with label pointer2771:1BAD.0D29:20EA reads SS:4153 into the record state;0D29:215D writes the committed low byte back. The failed local availability branch clears flags at218C. No complete registration implementation is inferred.
* 0D29:28BE caches four dwords on the stack. At28C9 the original MOV[4153],AL is stepped withAL0 and the byte changes1→0. Cached bytes match the input config.28F2 is the static four-dword restoration on Demo exit. Ascending16-byte interpretation assumesDF0; the observed context hasDF0, while a universal callerDF contract remains open.

The explicit-address census has eight references, four writers. This is not complete writer closure: configuration reads and REP MOVSD restoration are additional bulk mechanisms; aliases, save/load and external effects remain open. config_cheat_fields.csv lists all four bound menu fields.

## Natural canonical path to04C7:0C37

1. The original constructor083D:117A defaults actor mode+0A to0 and state+0B to7. Its bounded table083D:11B8 maps native type18/19 to11F6, setting mode3. Later byte-class and lifecycle paths can override it; type alone is not sufficient.
2. At state7,04C7:0F60 requires global4153==0. The original06D2 call must returnAL!=0. Then actor+0A must equal3;0F91 calls0C30, which reaches RNG site0C37.
3. With the actual zero argument flags of this path,06D2 requires both absolute signed tile deltas<=8 and an exact three-neighbor direction-mask intersection. This is a bitmask predicate, not a freely substituted geometric dot product. It calls0AEA:0CC0 with maximum8 steps. The destination must be reached before a blocking interior cell. The endpoint is accepted before its blocker check; the initial tile is not checked. Equal start/end does not succeed in the tested empty-grid domain.
4. The grid walk examines wall traitsDS:D00C and optionally object traitsDS:D10C. Two FAR call operands at0AEA:0DCE and0DD8 have unloaded-image placeholders. Their runtime dependencies/target domains are not closed. Successful range/facing alone therefore does not prove visibility.

Original CPU bytes for06D2 and0CC0 pass3,249 isolated Unicorn2.1.4 cases: all dx/dy from-9..9, eight directions and the skip-direction variant, with an empty grid, valid coordinates and no interrupts. SI/DI/BP/DS and FAR stack results are checked. These are SYNTHETIC_CPU_ONLY, not game runtime hits or a nonempty-grid/door proof.

## Scene selection and actual map evidence

The old Episode1/level1 snapshot has33 actors with no mode3 record. In the provided MAP files, candidate gargoyle IDs occur in Episode1 levels6/8 and Episode2 levels1/4/8. Native0277:00EC seeks514+8192*levelIndex and reads8192 bytes. Initial interleaved map-object matching explains31 of the33 earlier actors; the remaining two are explicitly not explained by that initial-tile join.

The first new scenario J wrongly omittedDEMO.1 under a hypothesis that the selector scanned demo.N. Source inspection and runtime names disproved it:0D29:2696 formats map.N using literals2771:2000/2005. J selectedmap.1 and attempted the missingdemo.1, never reaching the header; a later system-shell context was recorded. J is a failed input-selection experiment, not gameplay coverage. Its valid config/clear observations are retained separately.

Scenario K instead omitsMAP.1 only in a separate copy. The native availability scan choosesmap.2; all originalDEMO files remain unchanged. The original routine selects Episode2 levelIndex0. The native header isDEMO.2 SHAdeb7fe959b6b1c9f0f7f4a793a40e0ef75873b436c715bd9f74d4ef965ac304d, timing words10/5/20 and first record48E0/0002/counter26. No executable, actor, position, RNG or gameplay flag was patched. This is a controlled file-availability scenario, not an untouched full-directory startup.

The native initial snapshot has80 actors, including39 mode3/state7 records. Every one joins by tile position, type18/19 and direction to original MAP.2 IDs B4..BB and the supplied OBJECTS.2 labels GUARD11/12 (cemetery/garden wall gargoyles). The initial player is at(22,59); none is within the helper's axis8 gate. At the frozen counter306 endpoint, all39 remain state7 and outside that axis gate. This is a concrete unmet activation condition, not an unreachable-code proof.

K uses its actual loadbase08AB; addresses are normalized per run. Scenario L requests cycles=max in a preserved config, with the same input-file manifest, but a separate process/loadbase0823. No effective-speed, timing-equivalence or stitched trace claim is made. Periodic diagnostic pauses are documented; the subsequent controller keeps one live operation through wait timeouts and pauses only at its budget or a target breakpoint.

## Validation, corrections and resume

The read-only verifier correlates native config/clear/header proofs to raw RPC UUIDs, serverPID, read lengths/hashes and registers. It checks adjusted FAR segments, native cache content, file hashes and API writes limited to BIOS keyboard queue words. Raw records, original images/assets and complete input files remain local.

Actor count in these observations is the caller's globalDS:6276. Segment21FD is used for FAR actor/object pointers, not loaded intoDS by the local loop prefix. A wrong-segment zero-length read attempt was rejected and retained, not counted as a valid actor snapshot. Fourteen function-record overlays add only these bounded semantics; whole-function boundaries, callbacks and interprocedural side effects remain open.

The later K continuous operation must be checked by its saved operationID and actual pipe-serverPID before resumption. A control file or this frozen prefix is not current liveness proof. Remaining work: successful canonical04C7:0C37 call/consumer/FAR-return observation, other ten RNG sites, door callback targets, global writers/IRQ ordering, remaining DOS/Win16 functions and paired remake parity. The full GOAL is not complete.
