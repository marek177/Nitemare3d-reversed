# Nitemare 3D RE MAX v0.65 — Win16 v1.10 USER.SAV X/Y/yaw causal closure

Eight original Win16 v1.10 E1M1 save scenarios and four one-field mutation/load experiments now close three USER.SAV fields functionally.

Observed natural saves:

| Scenario | yaw @0x2037 | X @0x2043 | Y @0x2045 |
|---|---:|---:|---:|
| idle | 0 | 1440 | 3616 |
| forward | 0 | 1440 | 3396 |
| backward | 0 | 1440 | 3620 |
| right | 105 | 1440 | 3616 |
| left | 250 | 1440 | 3616 |
| short right | 35 | 1440 | 3616 |
| short left | 330 | 1440 | 3616 |
| right then forward | 30 | 1494 | 3419 |

Causal mutation/load tests modify only one little-endian 16-bit word in a private copy of USER.SAV, restart Windows 3.11 + NITE3W and load through the original menu:

- 0x2037: 0 -> 90 or 180 produces the corresponding large view rotation;
- 0x2043: 1440 -> 1568 produces a lateral scene displacement;
- 0x2045: 3616 -> 3488 produces a longitudinal scene displacement.

Therefore for Win16 v1.10:
- USER.SAV 0x2037 is the saved yaw/heading in degrees modulo 360;
- USER.SAV 0x2043 is saved X;
- USER.SAV 0x2045 is saved Y.

All eight USER.SAV files are 55,015 bytes.

Still open: exact Win16 runtime writer instructions for these fields, unit scale versus map cells, cross-version save-layout identity, first-post-load RNG/cache chronology and audio restoration.
