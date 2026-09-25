# Implementation sync — 2026-09-22

This document maps the consolidated reverse-engineering findings in `DISCOVERIES.md` to implementation work in the companion repositories:

- `marek177/nite3d-dos`
- `marek177/OpenNitemare3D`

It is intentionally implementation-oriented and does not replace the central discovery log.

## Shared parity targets

### Player
- Preserve 0..100 health behaviour.
- Reconstruct collision radius/flags, wall collision, OBJECT/GUARD collision and sliding.
- Keep Windows address observations (`0x4BF6/0x4BF8`, ammo-related `0x4C1F/0x4C20/0x4C44`) as reverse-engineering anchors only.

### OBJECT
- Do not use the historical 28-byte runtime assumption.
- Current evidence points to roughly `0x50` / 80-byte runtime iteration stride.
- Movement-related fields around `+0x10/+0x12` are supported by current analysis.
- Resolve `+0x14/+0x18` before hard-coding semantics.

### GUARD
- Current runtime evidence indicates roughly 98-byte guard records.
- Finish type/state/HP/movement/attack/pain/death/timer/SFX mapping.
- Keep static map records separate from runtime guard state.

### Dracula / transformed Bat
- Distinguish normal Bat type `0x08` from transformed internal Bat `GUARD13/type 0x14`.
- Current code-level evidence indicates Dracula transitions to `0x14` and the transformed form receives 255 HP.
- Treat this as a separate runtime form until contradicted by stronger evidence.

### Combat
- Complete per-guard HP tables.
- Correlate weapon, range, difficulty and guard type with damage.
- Audit boss-specific behaviour separately, especially Dr. Hammerstein.
- Complete attack/pain/death SND.DAT mapping per enemy type.

### USE / interaction
- Trace the `0x0200` interaction-related path through doors, switches, warps, push/special walls and keyed interactions.
- Do not reduce USE to a generic door command.

### Warp / special walls
Track and test:
- `WARP`
- `WARP_L1`
- `WARP_L2`
- `WARP_1..n`
- elevator/level warp variants
- `JAMB`
- vertical/horizontal door families
- `SPECIAL1`
- `ONE_SHOOT`
- `REVWALL`
- `CONTROL`
- `LEVEL_UP`

`WARP_L1/WARP_L2` currently have key-dependent behaviour evidence, but final script/state semantics are still unresolved.

### Renderer
- Preserve the 320-pixel-wide framebuffer-oriented behaviour where appropriate.
- Continue analysis of the approximately 52-byte renderer-side record stride.
- Trace the write chain around the currently identified renderer anchors before declaring parity.

### Resource formats
Maintain compatible handling for:
- `MAP.1..3`
- `IMG.1..3`
- `WALLS.1..3`
- `OBJECTS.1..3`

Round-trip tools/ports should preserve IDs, episode indexing, object/guard placement, spawn/orientation, doors, special walls, warp semantics and original executable limits where known.

### DEMO
- Keep `DEMO.1 -> E1M11` as the current strongest mapping.
- Continue command/value reconstruction for forward/back, turn, fire and use.
- Preserve termination-on-key behaviour and MIDI/music side effects.
- Do not mark DEMO.2/DEMO.3 map mappings confirmed yet.

### Audio
- Validate SND.DAT extraction against actual in-game playback.
- Investigate incorrect/failing VOC entries.
- Complete music/SFX ID mapping and enemy attack/pain/death sound mapping.

### ENDING.FLI
- Analysed file: 488 frames.
- Relevant chunks: `COLOR_64`, `BRUN`, `LC`, `BLACK`, `COPY`.
- Preserve palette state and delta dependencies during decode/edit/re-encode.

### USER.SAV
Complete serialization mapping for:
- player state,
- episode/map state,
- inventory/ammo,
- OBJECT/GUARD state,
- timers/flags,
- exact field offsets and sizes.

### BSF / executable versions
Continue systematic comparison across 1.0, 1.7, 1.8, 1.9 and 2.0:
1. enumerate all `nite3d.bsf` XREFs,
2. identify parent functions,
3. trace open/read/seek/close,
4. reconstruct verification byte-for-byte,
5. document version differences.

## Repository-specific next work

### nite3d-dos
Focus on behavioural reconstruction and DOS/Windows differences. Windows addresses are reference evidence only and must never be treated as DOS offsets.

### OpenNitemare3D
Focus on implementing verified behaviour in C# while keeping unverified guesses explicitly marked. Highest value: collision, runtime OBJECT/GUARD models, combat, USE/warp interactions, DEMO and savegame parity.

## Confidence rule

Only promote a finding to confirmed when it is supported by the original Nitemare 3D executable/data or reproducible runtime observation. Ports, GZDoom recreations and related raycasters are comparison material, not proof.


## 2026-09-25 Win16 MFC / memory synchronization

The current repository now contains the relocation-aware Win16 MFC reconstruction and its modern compatibility layer. Canonical entry point: `docs/WIN16_MFC_RE_SUMMARY.md`. Static artifacts cover `CRuntimeClass16`, 31 runtime classes, CWnd layout/vtable/lifecycle anchors, HWND/HDC/HGDIOBJ/HMENU HandleMaps, evidence levels and explicit coverage states. Runtime validation remains separately tracked and requires the Win3.1 debugger checklist/capture template. The modern C++20 layer now includes `HandleRegistry`, `NativeHandleWrapper`, `WindowWrapper`, `WindowRegistry`, nested/RAII temporary scopes and the recovered z-order mapping. Historical 16:16 pointers, NE fixups and raw MFC object layouts are evidence only and are not reproduced as the x64 ABI.

### HandleMap packing follow-up

The host-side clean-room model now explicitly uses 2-byte packing for the recovered Win16 binary records. This preserves the executable-derived `HandleMap16` size of `0x26` bytes instead of accepting the 40-byte layout produced by default GCC/Clang host alignment. Compile-time checks pin the member offsets to `0x00`, `0x10`, `0x20`, `0x22`, and `0x24`. The evidence audit reproduced the 40-vs-38-byte mismatch and the packed correction on GCC and Clang; a fresh full-project build was not executed during this synchronization. Implementation commits on this review branch: `af1676f45ce45d0e95673ec789eb7200941b3b31` and `ab19bb0eaa5777077be06eb7ac7b2ba07c2fc27f`.

