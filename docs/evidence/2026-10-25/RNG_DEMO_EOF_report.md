# Original RNG and DEMO ledger to first EOF

## Scope and provenance

The completed case is rng_run_f in owned DOSBox-X process18800. The game input manifest is local and the packed original EXE remains SHA256a3fa02335e1d8bc531918f3bfaa66217aef65c81e562a2fdf1c749be652ca485. Address analysis uses hash-pinned unpacked DOS2 image5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3. Emulator SHA256 is78fd1926272de172c2a87b9456aafce5eb54ea928ad1e5103a6d943bc26f0f57 and its version resource reads2026.10.01; this is not an attribution of the custom build to a public release. PDB identity and read-only VGA capture checks remain separate proof artifacts.

The earlier rng_run_e process40940 and its pipe were authoritatively missing on continuation. Its220-event prefix is retained as interrupted, with72 completed RNG calls and75 DEMO post-read observations. Its cause of termination is UNKNOWN. The new run starts independently; no records from the two processes are stitched into one execution. A prior atomic control-file replacement failure in run_e had been recovered using its saved operationID; that did not restart the game. The later process disappearance is a distinct condition.

Both independent game-file manifests match. Their first75 applied input records contain exactly the same72 ordered RNG caller/counter/result/state observations, despite baseline RTC values24372 and27148. This is replication of that prefix, not two completed full runs or proof of every timing/IRQ invariant.

## Completed measured window

The original menu route selects Demo using recorded BIOS queue fixtures. Measurement begins at06B0:02E0 after the original opens demo.1 and loads the6-byte timing header and first8-byte record. These bytes match DEMO.1 SHA25625ae7e97f61d19bc3fa61d630ec13b9614a4f3193da84f7c1a3c3d519f795840, timing words15/7/30 and first record(48E0,0002,8). Original RNG state is1 and render counter is2. No debugger seed or gameplay-state write is made.

Persistent execution breakpoints observe RNG core11EE:31F8, seed setter11EE:31E6, the DEMO post-read point06B0:0307 and its close path. Each RNG entry/return records the actual stack return frame, register snapshot, state words, RTC, render counter, flags and prefetched input. Dynamic one-shot return breakpoints check each completed core return. Saved operation IDs are retained across observation waits.

The resulting734-event ledger contains229 completed RNG calls, zero observed seed-setter calls and275 DEMO post-read observations. Every key/flags application and next-record prefetch matches the supplied file in order. The first274 post-read calls return8; the last returns0 after applying record274. Initial prefetch plus those274 successful next-record reads accounts for all275 records. EOF is first observed at render counter1074. The RNG chain ends at3496228196 (D0643564), with no unexplained sampled state change and no pending RNG call.

This completes one original RNG-core/input-event window from the observed seed1 checkpoint to first EOF. It is not a complete instruction/IRQ trace, global closure of every possible RNG-state writer or a paired remake result. No nested RNG entry was observed in this case.

## Observed caller continuations

All229 core returns reach their saved immediate caller, with SP increased by4. The wrapper's outer return address is read from its stack frame and checked against a literal FAR call to0FBA:01A0 in the hash-pinned source; it is not guessed from a gameplay name. The CSV stores all ordered observations. Counts by outer continuation are:

| Continuation | Calls |
|---|---:|
|04C7:0A3B|22|
|083D:01E2|24|
|083D:1C7C|93|
|04C7:0917|2|
|04C7:0AD4|15|
|083D:1C18|62|
|083D:19A3|2|
|04C7:05F3|5|
|083D:1D60|2|
|083D:1B6B|1|
|083D:18CD|1|

The source-backed state recurrence is low32(state*214013+2531011), with AX=(state>>16)&7FFF. The independent read-only verifier checks the transition in reverse using the multiplier's inverse modulo2^32, verifies the actual AX and return frame, correlates memory responses and registers with raw RPC records, and verifies record prefetch against the original DEMO bytes.

Entry IF is set for all229 RNG calls. RTC changes by1 within5 entry-to-return intervals and by0 in the other224. This is interval context; it does not locate each IRQ instruction. Low16 BP/BX/SI/DI match entry/return in all229 cases; low16 CX matches in none. These are case observations, not a global ABI/liveness proof. The captured disk configuration hash is inventory only; loading that exact file as the effective configuration is not independently proved.

## EOF is not local playback termination

The local06B0:0204 span is independently length-checked:388 bytes and136 decoded instructions including two padding NOPs, versus134 inherited member instructions. Function-boundary ownership remains UNKNOWN. Static mode4 code does not branch on the next-record read's returnAX at0307.

After EOF, all measurement breakpoints are removed. A separate32-event trace follows the original reader from0307 to its saved continuation06B0:039C. With an empty BIOS queue, it returns the last key74E0, retains flags0090 and leaves the prefetched last record unchanged. SP increases by12 across argument cleanup, saved-SI restoration and FAR return. The actual runtime check confirms RNG stateD0643564 and mode words1/4 remain unchanged after this probe. No automatic local termination is inferred from the file ending; later caller/game-mode termination is a separate question.

An EOF-context VGA page projection is retained locally. Its programmed start is4000 while latched start is0. It is not a frame-aligned scanout capture or a renderer parity result.

## Validation and remaining gates

The standalone verifier accepts the full734-event window with require-eof enabled and raw RPC correlation. Negative tests reject an altered RNG AX, altered key, missing event, modified DEMO bytes and a prefix falsely presented as EOF. All14 debugger memory writes in rng_run_f are menu BIOS-queue fixtures; none occurs during the measured window. Original binaries/assets, complete input bytes, pool/VRAM snapshots and raw instruction traces remain local.

Next: obtain every-IRQ/tick instruction ordering where required, close RNG writer/indirect domains, exercise full-pool and empty-ammo failures, compare these ordered events and slot effects with the remake, and verify save/load first-frame behavior. Complete DOS/Win16 function boundaries, semantics and remaining P0 branches remain unfinished. RNG_DEMO and whole-game parity gates therefore stay OPEN.

Repository refresh: Nitemare3d-reversed/main is nowf5c37abbbdc3ff8bd806af10fb1eb6dd01e9df68, whose only new file change relative to497c6fd is README.md introduction/evidence limits. OpenNitemare3D/main remains1668039e5239e3b094a8302df183fd5cff315bdb. The initial inventory is retained rather than silently replaced.
