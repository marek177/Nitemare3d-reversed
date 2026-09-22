# Nitemare 3D Reverse Engineering — Discoveries

Last consolidated: 2026-09-22

This document consolidates findings from the ongoing reverse-engineering work. Items still requiring runtime proof are explicitly described as unresolved.

## Current practical status
Overall practical understanding is approximately 45–50%. Behavioural reconstruction is substantially further along than exact EXE reconstruction. Runtime debugging and systematic XREF/function mapping are now higher-value than additional strings-only scans.

## Runtime structures and addresses

### Player
- Player X/Y commit locations observed around 0x4BF6 / 0x4BF8.
- Player health behaves as a bounded 0..100 gameplay value.
- Ammo-related locations under investigation: 0x4C1F, 0x4C20, 0x4C44.
- Collision reconstruction must cover radius/flags, walls, OBJECT/GUARD collision and sliding.

### OBJECT
- Earlier 28-byte record assumptions should not be used for runtime reconstruction.
- Runtime iteration indicates an approximately 0x50 / 80-byte stride.
- Counter/iteration evidence around 3:D1EA.
- Movement-related fields observed around +0x10/+0x12.
- +0x14/+0x18 remain important unresolved fields.

### GUARD
- Guard iteration indicates an approximately 98-byte runtime structure.
- Counter/iteration evidence around 0x7E5E.
- Type, state, HP, movement, attack, pain/death and sound relationships remain key reconstruction targets.

## Dracula -> Bat
A strong code-level finding is a distinct Dracula transformation path. Dracula changes into an internal Bat form identified in the audit as GUARD13 / type 0x14. This is distinct from normal Bat type 0x08. The transformed form shares sound-related evidence with Bat, and the transformation path restores/sets 255 HP. A source-port should therefore keep the transformed form distinct from a normal map-spawned Bat.

## Combat, HP and difficulty
Enemy HP is processed per guard. Exact HP and shots-to-kill tables still need full reconstruction. Damage must be correlated with weapon, range, difficulty, guard type and special/immunity behaviour. Dr. Hammerstein should be audited separately as a boss-class enemy. Enemy damage differs with difficulty, but exact scaling/tables still require runtime/code confirmation.

## USE / interaction
0x0200 is an important interaction/USE-related value in the current reconstruction. Trace the USE chain across doors, switches, teleport/warp walls, push/special interactions, keyed interactions and special walls. It should not be reduced to ordinary door opening.

## Warp system
Known families include WARP, WARP_L1, WARP_L2, episode-specific WARP_1..n and elevator/level warp variants. WARP_L1/WARP_L2 have evidence of key-dependent behaviour. Exact state/script semantics still require final XREF/runtime confirmation.

Wall-name families found during the audit include JAMB, vertical/horizontal door variants, SPECIAL1, ONE_SHOOT, REVWALL, CONTROL, LEVEL_UP and episode-specific warp/elevator entries. Animated walls may use two or more animation ticks/frames.

## Renderer
- 320-pixel-wide framebuffer-oriented rendering path.
- Windows build uses WinG/display-related APIs.
- Renderer iteration evidence around 0x5E7E, with relevant code around 3:62F8.
- Observed renderer-related record stride approximately 52 bytes.
- Important vectors/code locations under study: 4:34E1, 4:3919, 4:4073.

Wolf3D, Catacomb and Hovertank-era engines are useful comparison material, but Nitemare 3D-specific behaviour must be verified independently.

## MAP / IMG / WALLS / OBJECTS
The three episodes use MAP.1..3, IMG.1..3, WALLS.1..3 and OBJECTS.1..3. The goal is round-trip editing/generation compatible with the original executable, preserving wall IDs, object/guard placement, doors, warp semantics, episode indexing, spawn/orientation, special walls and original EXE limits.

E1M11 is used by DEMO.1. Compared material indicates E1M11 and E1M3 are effectively identical.

## DEMO
DEMO.1 is associated with E1M11. Reconstruction targets a compact input stream mapping values to forward/back, turn, fire and use. Playback termination on key input and music/MIDI changes are also relevant. DEMO.2 and DEMO.3 map identification still requires definitive runtime confirmation.

## SND.DAT
Audio extraction must be validated against actual in-game playback. Producing a playable VOC is insufficient if rate, format or chunk interpretation differs from the game. Current work includes MIDI/music mapping, SFX extraction, enemy attack/pain/death mapping, comparison with known-good extraction and investigation of failing/incorrect VOC entries. Target: guard type -> attack/pain/death SND.DAT IDs.

## ENDING.FLI
The analyzed ENDING.FLI contains 488 frames. Relevant chunks include COLOR_64, BRUN, LC, BLACK and COPY. Correct editing must preserve palette state and delta-frame dependencies; decoding/replacing frames independently can produce wrong results.

## USER.SAV
The save format is partially reconstructed. Targets include player state, map/episode state, inventory/ammo, serialized object/guard state, timers/flags, exact offsets and field sizes.

## BSF/version audit
Executable versions under comparison include 1.0, 1.7, 1.8, 1.9 and 2.0. A major target is the XREF set to nite3d.bsf: identify parent functions, follow open/read/seek/close operations, reconstruct the verification/comparison algorithm, then compare it across versions. The end goal is a byte-exact description rather than a strings-based inference.

## Highest-value next steps
1. Build a master function map across 1.7/1.8/1.9/2.0.
2. Resolve XREFs for guard strength/state/timer.
3. Finish framebuffer write-chain reconstruction.
4. Trace OBJECT and GUARD runtime structures dynamically.
5. Resolve weapon cadence/damage and enemy HP.
6. Complete enemy SFX mapping.
7. Trace USE/door/switch/teleport/push behaviour.
8. Validate USER.SAV serialization.
9. Finish DEMO command/value mapping.
10. Document executable-version differences.

## Reconstruction targets
Player collision/sliding; OBJECT runtime; GUARD movement/AI; player damage/death; weapon cadence; enemy pain/death, HP and SFX; USE interactions; doors/teleporters; map/resource round-trip support; and savegame compatibility where practical.

## Confidence policy
Do not mark inferred values confirmed merely because they match a ZDoom/GZDoom recreation, another raycaster or visual gameplay. Treat those as behavioural hints. Confirmation should come from the original Nitemare 3D executable/data or reproducible runtime observation.

This file is the central consolidated reverse-engineering notebook. Detailed subsystem documents can link here while retaining exact offsets, disassembly excerpts, tests and confidence levels.
