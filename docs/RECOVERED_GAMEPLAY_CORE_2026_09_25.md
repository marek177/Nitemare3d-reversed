# Recovered gameplay core — 2026-09-25

This update records newly consolidated Nite3W reverse-engineering findings without presenting unresolved behavior as original source.

## Confirmed
- Runtime capacities: 350 OBJECT records (28 B), 100 GUARD records (26 B), 8 projectile slots (42 B).
- GUARD state range 0x00–0x15 and strategies 0–4.
- Shared RNG: state = state * 0x343FD + 0x269EC3; result = (state >> 16) & 0x7FFF.
- Corrected Win16 score table: class 8/26=25, 9=75, 10/32=50, 11/15/16/23/27/28=100, 12/29/30=250, 13/18/19=150, 14/20/24/31=200, 17/25=0, 21=-1000, 22=1000.
- Damage seed uses render-derived OBJECT+0x18, not world distance.
- Fire IDs 0x3B/0x3C/0x3D cause 100/10/2 HP per slow simulation update.
- USE-like input bit is 0x0200.
- Win16 DEMO events are 8 bytes and timestamped by generation.
- Event bytes 51A4..51AB are preserved separately.
- MAP.1–3 contain 1,266 playable GUARD placements; E1M11 demo adds 50.

## Analytical score baseline
Exactly one score award per playable placement gives 145,775. Avoiding the two Penelope -1000 penalties gives 147,775. This is not the true theoretical maximum because score is reached through the damage path.

## Still open
Projectile owner/friendly fire, exact projectile OBJECT+0x18 freshness, full animation tokens, complete wall/USE side effects, pixel-perfect renderer parity, full ending callback, and true maximum achievable score.

## Coverage ledger

The current subsystem-level working estimates are intentionally stored separately from recovered gameplay semantics:

- `docs/RE_COVERAGE_2026_09_25.md`
- `src/re/N3DAnalysisStatus_2026_09_25.hpp`

This separation prevents a percentage/status update from silently changing reconstructed engine behavior.

Code: `src/re/N3DRecoveredCore_2026_09_25.hpp/.cpp`
