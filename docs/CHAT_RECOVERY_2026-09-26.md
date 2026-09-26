# Chat recovery / reverse-engineering preservation plan — 2026-09-26

Goal: preserve every useful Nitemare 3-D reverse-engineering result from ChatGPT conversations mentioning **Nitemare3D**, **Nite3W**, **Nite3D**, or **N3D**, including threads that no longer load correctly in the ChatGPT UI.

## Important limitation

The repository can preserve everything present in the repository, accessible conversation context, or a user-supplied ChatGPT export. A conversation that the UI cannot load and that is not present in an export cannot be reconstructed verbatim from its title alone. Unseen chat statements must not be promoted to source code or VERIFIED evidence by guesswork.

## Recovery workflow

1. Export ChatGPT data and locate conversations.json.
2. Run: `python tools/extract_chat_re.py conversations.json -o recovered_n3d_chats.md`
3. Audit the ledger for reconstructed functions/pseudocode, addresses, structure sizes, state machines, renderer, collision/USE, GUARD AI, weapons/projectiles, MAP/IMG/OBJECTS/WALLS/BSF/DEMO/SND/UIF/FLI/USER.SAV, Win16/MFC, automap, HUD/palette, debug/cheat paths.
4. Cross-check each candidate against the latest executable/data evidence.
5. Merge only validated findings into canonical C/C++ and subsystem documentation.
6. Keep conflicting historical claims with a superseded marker instead of silently deleting them.

## Canonical evidence status

Use VERIFIED_EXE, VERIFIED_DATA, VERIFIED_SAVE_LAYOUT, BEHAVIORAL, INFERRED, PARTIAL and TODO.

## Already-preserved high-value corrections

- OBJECT record = 28 bytes, capacity 350.
- GUARD record = 26 bytes, capacity 100.
- Visible wall span = 20 bytes, capacity 50.
- VEC record = 28 bytes, capacity 1000.
- Renderer is MAP-boundary/VEC/span based; do not revert to a Wolf3D one-ray-per-column DDA model.
- USE input bit = 0x0200.
- Player X/Y globals = 0x4BF6 / 0x4BF8; tile X/Y = 0x4BF2 / 0x4BF4.
- Push movement = 8 updates × 8 world units = one 64-unit tile.
- DEMO record = 8 bytes.
- Player projectile pool = 8 × 42-byte records at USER.SAV +0xC403.
- ENDING.FLI = 488 frames.
- E1M3/E1M11 share the same local first-plane geometry/spawn fingerprint but differ in second-plane bytes.

## 2026-09-25/26 conversation topics to preserve and re-audit

- Win16/MFC initialization, system wrappers, error paths and memory ownership.
- Renderer/raycast reconstruction, including remaining lower wall blitter/backend work.
- Automap reconstruction.
- Exact HUD RGB/palette-index investigation.
- Debug menu/debug-mode/debug-tool support investigation.
- BSF chapter/version/integrity work.
- Static analysis of previously unknown/partial functions, including function body and variable/argument recovery.
- System-by-system percentage/status audit and prioritization of the least-known areas.
- Identification of previously unexamined subsystems.
- 1:1 reconstruction tracking: confirmed vs partial vs inferred vs unknown.

## Code-generation rule

Recovered chat code is provenance first. It becomes canonical C/C++ only after reconciliation with current RE evidence. This prevents superseded hypotheses (for example the old 80-byte OBJECT and 98-byte GUARD ideas) from contaminating the clean-room reconstruction.

## Target repositories

Primary archive/canonical RE repository: `marek177/Nitemare3d-reversed`.

Validated implementation work can then be synchronized into `marek177/OpenNitemare3D`.
