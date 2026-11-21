# Original DEMO input and one natural eight-slot reuse cycle

## Independent original run and input provenance

A separate owned DOSBox-X process40072 was started with the same installed emulator build78fd1926272de172c2a87b9456aafce5eb54ea928ad1e5103a6d943bc26f0f57, a fresh pipe endpoint and an isolated copy of the game data. The packed original N3D.EXE is SHA256a3fa02335e1d8bc531918f3bfaa66217aef65c81e562a2fdf1c749be652ca485. The input-file manifest is local. The prior clean_run_c remains paused; its control files were preserved before changing the active endpoint.

The original menus were traversed using recorded BIOS queue fixtures. Extended Down50E0 selects the Demo item; keyboard/IRQ9 parity is not claimed. From then on, original DEMO playback supplies gameplay input. All debugger memory.write requests in demo_run_d are within the BIOS keyboard queue. There are no debugger writes to gameplay state, pool records or RNG seed. The agent did not advertise an input method, and computer-use found no targetable window for the owned hidden run; no UI keys were sent.

DEMO.1 is2206 bytes with SHA25625ae7e97f61d19bc3fa61d630ec13b9614a4f3193da84f7c1a3c3d519f795840. Its6-byte timing header is three little-endian words15,7,30. The remaining275 records are key word, flags word and render-counter dword. DEMO.2/3 have524/422 records and separately recorded hashes; this format inventory does not prove their runtime playback. Bit80 of the flags word feeds the fire path.

At original06B0:02E0, runtime filename demo.1, timing words and the first8-byte record exactly match the file. Mode words are1/4, render counter2 and RNG state1. No seed was forced. The first fire-flag record is at counter67. A stopped snapshot at173 has weapon index2/class1; that class's static path bypasses the allocator. A complete first-shot trace is not claimed. The allocator was first stopped at250 but a continuation script passed it before detailed recording, so that event is not presented as a complete allocation test. The fully captured calls below occur at468 and479.

## Two phased natural allocations

At counter468 the original reaches07ED:000E with weapon index1. The captured call selects the first free slot0. The external gate decrements ammo DS41B0 from37 to36 while all336 pool bytes remain unchanged. A breakpoint stops at003E before the state store. One CPU step executes that store, reaches0042 and changes only the selected state byte0→1; all other335 bytes still match the pre-gate pool.

A separate trace then follows remaining initialization to00C5 before RETF. AL=1 and the initialized record is captured. Stepping RETF reaches the saved caller0637:06DF and increases SP by4. The gate phase has2852 contiguous events, below its10000 capacity; the remaining initialization has51 contiguous events, below2000. Trace events naming the stop instruction are not confused with execution of that instruction; the state store and RETF have explicit step evidence.

At counter479 a second phased call again selects slot0. Ammo falls34→33, and the same pool-unchanged/gate, single-byte early-publication and return-frame checks pass. The two ammo values are from these two calls; other original shots occur between them, so no claim is made that37→33 contains only two shots.

## First movement, state2 and release

The first movement invocation after the captured allocation of slot0 has1825 contiguous events, below10000. It executes30 nested candidate-step calls, matching the loaded motion-count word30. Embedded position changes from(1243,2746) to(1213,2745), while state remains1. Its actual return and SP are checked. This is the first movement after this captured call, not the first shot or movement in the process.

A persistent memory-change watch on that same state byte then observes state2 with CPU at07ED:0324, immediately after the0320 state store. That checkpoint is before subsequent state2 initialization instructions, so it is not labelled a fully initialized collision record. Continuing the same live watch observes state0 with CPU at07ED:042F, immediately after the042C release store. The watch is removed before the next allocation test.

The42 bytes captured immediately after release exactly equal the same42 bytes at entry to the next allocation. They are not all zero. The next allocation uses the same slot0 address and changes its state byte before the remaining partial initialization. This is one concrete original same-slot reuse observation with retained bytes. It is not a universal generation/ABA or reentrancy invariant and does not close all aliases, active-pool capacity, empty-ammo, save/load or stale-depth damage paths.

## Input record and final state

At the second allocator return, counter479, original flags are0080 and playback mode remains4. The prefetched record is(0,0,480), uniquely record index131 in the file; its preceding record has the same0080 flags observed at runtime. This connects the observed reuse to the original file-input path without claiming a complete tick/RNG ledger or playback-to-EOF result.

Final active state is demo_run_d/ses-1, process40072, stopped revision91 at runtime0E5A:06DF (logical0637:06DF), with zero breakpoints and newly active slot0. Revalidate the live endpoint before continuing. The old clean_run_c process10784 remains separate and paused; do not infer its current registers from the new run.

## Acceptance limits and next work

One native game-file input cycle now has original evidence for ammo-before-state1 ordering, early state publication, first movement, state2, release and same-address reuse. Physical keyboard/IRQ9 parity, full DEMO EOF/RNG ordering, nested reentrancy/generation domains, all weapon/guard branches and paired original/remake state+indices+DAC acceptance remain OPEN. No gameplay behavior was changed.

Next: gather a seed-to-end ordered RNG/IRQ/tick ledger, exercise full-pool and empty-ammo failures, compare the captured write order with the remake, and trace save/load restoration and first post-load frame. Win16 runtime and global function-boundary/indirect-domain closure remain required. Public output contains findings, hashes and selected proof metadata only. Original binaries/assets, pool snapshots, PNG/VRAM and full instruction traces remain local.

