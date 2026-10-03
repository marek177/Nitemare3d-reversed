# Evidence boundary — v3 phase 1

## Verified/recovered facts used directly

- Normal GUARD strength starts at **255**.
- GUARD class IDs and score switch values listed in `monster_combat_matrix_v3.csv`.
- Player-to-GUARD resistance transforms for classes `0x0C..0x1F`.
- Non-lethal normal hit path subtracts strength and enters pain state `0x15`; lethal path clears strength first.
- Dracula phase 1 transforms in-place to class `0x14`, restores strength to 255 and continues as Dracula-Bat phase 2.
- Dr. Hamerstein damage producer returns literal 3 only while the special gate equals 3, otherwise zero, before difficulty scaling.
- ROT8 / ROT4 / ROT0 sprite grouping from the supplied image banks.

## Visual/source-layout inferences

- Exact frame-to-state splits in `core_state_bindings_v3.csv` where confidence is marked medium.
- Baddie attack/death split in frames 41-45 is and visual inference, not yet an EXE-verified state binding.
- Dr. Hamerstein attack/reaction split inside frames 33-43 is visual inference.

## Test-only values in DECORATE

- `Radius 16`, `Height 56`, `Speed 8`.
- Melee/hitscan damage values and spread.
- Doom `A_Chase`, `A_CustomMeleeAttack`, and `A_CustomBulletAttack` are stand-ins for the original N3D AI/attack scheduler.
- Exact original sound callsites are not yet embedded in the PK3.

This separation is deliberate with future reverse-engineering can replace test behavior without changing the established sprite naming/rotation layer.