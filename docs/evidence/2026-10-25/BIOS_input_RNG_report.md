# BIOS input, page progression and natural RNG checkpoint

## Evidence and scope

The original packed DOS 2.0 game runs in owned DOSBox-X clean_run_c, session ses-1, loadbase0823. The controlled input fixture reads the actual BIOS queue head/tail and bounds, requires an empty queue and stopped CPU, writes the Enter scan/ASCII word1C0D into the free slot and then advances the tail. Every memory write response and the before/after pointers are preserved. This bypasses physical keyboard and IRQ9. No game code or RNG seed was patched.

Original INT16 wrapper11EE:39B0 was stopped at INT16 offset39BB. Captured AH11 calls return AX1C0D to the actual caller06B0:01D7 with queue pointers unchanged: these are availability checks, not consumption. The first queue-head memory-change watch stops in BIOS callbackF000:CFC5 after the AH10 read path; head advances1E→20 and equals tail20. The46-event bounded trace includes readiness, the copyright caller and its flush path. A BIOS callback update is not described as a native game store.

Read-only four-plane VGA captures and explicit layout checks reconstruct page contents after the input sequence: title house, Main Menu, Choose an Episode, Select Difficulty Level, then gameplay HUD LEVEL1. Episode1 and the default Be gentle! were selected by separate Enter fixtures. These observations establish that the prior copyright/menu runtime blocker has been passed for this run. They do not establish whole-game fidelity or pristine-stock asset provenance.

## Programmed versus latched VGA page

At revision22, programmed CRTC start4000 differs from captured real_start0. At revision23 both are4000. The new decoder emits separately labelled programmed/latched page-content projections with formula VRAM[4*(start+80*y+(x>>2))+(x&3)]. It accepts only the two established starts0/4000, the verified unchained byte-addressing layout, no panning/wrap/in-image split and a frozen DAC6 palette whose256 RGB mappings match emulator xlat32. It never calls these projections an assembled raster frame. Scanout timing and frame-boundary alignment remain unproven. The old zero-start decoder retains its strict rejection of nonzero starts.

The layout/integrity check accepts the captured4000 page and rejects panning, in-image split, CRTC/config start disagreement, unsupported start and corrupted VRAM. These are offline decoder guards, not original-versus-remake parity tests.

## One natural original RNG invocation

At revision55 the original naturally reaches0FBA:01A0 (runtime17DD:01A0). Its saved FAR return gives logical continuation083D:1D60; the hash-checked original direct CALL at083D:1D5B is9A A0 01 BA 0F.

State DS24B8/24BA before=00000001; after=0029E2C0; returned AX=0029 (41). These match low32(state*214013+2531011), then high15 extraction. A36-event original trace reaches the saved caller continuation, and SP increases by4 as expected for the FAR return. No seed write was made by the test. This is one observed invocation, not a complete RNG ledger and not paired remake parity.

## Remaining P0 work

Identify and trace the actual gameplay main-loop/OBJECT call ordering, extend the RNG ledger across controlled ticks and inputs, and pair original indices+DAC and gameplay state with the remake under the same inputs. The initial scene/page observation alone does not close these gates. All inherited candidate-function boundaries and indirect-call target domains retain their prior uncertainty. Win16 runtime and complete cross-version semantics remain unfinished.

Game binaries, assets, PNG, VRAM and full original traces stay local. Only this methodology, hashes, summaries and read-only decoder are suitable for publication.

