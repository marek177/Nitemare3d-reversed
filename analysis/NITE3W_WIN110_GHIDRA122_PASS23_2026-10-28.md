# Nitemare3D Win16 1.10 — Ghidra 12.2, pass23

## Finding
Confirmed (High): LOAD 1010:574C calls 1010:B128 after timer repair. B128 can overwrite loaded player fields under three nonzero byte flags. Integrated original-instruction execution of B128 and AAE6 passed1024 controlled cases without callee stubs. This is not a full game runtime or first-frame parity proof.

## Evidence
|Status|Claim|Source|Confidence|
|---|---|---|---|
|Confirmed|Any nonzero4BE4 sets bytes4C42/4C43=100|B128:B128..B134|High|
|Confirmed|Any nonzero4BE5 sets bytes4C1F/4C20/4C1D/4C44=100 and4C2A=15|B13E..B14C|High|
|Confirmed|Any nonzero4BE6 additionally sets4C29=3,4C28/4C45=15,4C42/4C43=100,4C22=99, plus the same resources/4C2A as4BE5|B169..B18D|High|
|Confirmed|4BE5 or4BE6 selects weapon0 only if current byte4C23=FF|B151..B15F,B192..B1A0;AAE6|High|
|Confirmed|Auto-selection sets byte4C23=0, WORD4C26=2, WORD4C3A=1|AB05,AB15,AB18|High|
|Unknown|Exact feature names and reachability of each flag in a real saved game|Flag setters and runtime not established here|Low|

## Behavior model
Apply4BE4 branch, then4BE5 branch, then4BE6 branch. The two later branches invoke originalAAE6(0) only while4C23=FF. Because each first enables mask bit0 and AAE6 immediately changes4C23, both flags together still select only once. Existing weapon values are retained, including fixture80. Existing4C26/4C3A remain unchanged unless auto-selection occurs. Writes are selective, not a reset of the entire player block.

AAE6 has a separate deferred switching branch: different requested weapon and WORD4C3A==0 writes pending byte4C24 and WORD4C3A=2. That branch is statically observed, not exercised by this integrated finalizer test.

## Verification
Original EXE SHA256:12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481. Unicorn2.1.4 real-mode controlled execution, relocated testCS2000,DS=SS1048. All71 instruction encodings checked against native Ghidra listing before test-selector relocation. Cartesian fixtures flags×3,currentweapon,initialpattern each in[0,1,128,255]:1024 cases. Entire94-byte player block checked against independent expected writes,336 projectile bytes and4 RNG bytes checked unchanged, far return andSP verified. No helper stubs. Word-width mismatch in the first expected model was exposed by execution and corrected from AB15/AB18 raw instructions before the final successful run.

## Implementation-ready findings
Preserve the exact branch order and byte truthiness. A load implementation must apply these conditional overwrites after timer rebasing; copying the save player block alone is insufficient when a flag is active. WORD writes to4C26/4C3A clear their high bytes. Keep flag namesTBD until setter evidence supports semantics.

## Unknowns and next test
Execute full loader with controlled read/seek/close and subsequent dispatcher to establish first-frame state. This test excludes earlier load loops, file I/O, final close helper, and next dispatcher. Projectile deadline/stale-depth effects and global RNG across full LOAD remain open. Previously measured1401 undefined executable bytes remain unresolved; this pass changes semantic comments only.

## Confidence
High for the local finalizer and integrated auto-selection path; no complete gameplay parity claim.
