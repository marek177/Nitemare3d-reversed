# Nitemare 3D RE MAX v0.64 — DOS2 E1M1 SAVE/LOAD pre-update boundary

A natural DOS2 E1M1 run reaches the first sliding side panel, traverses the opened passage, and later produces a real first-slot USER.SAV.

A controlled second LOAD stops the original game at the main-update entry before the first gameplay update. Six saved fields then match live DS exactly:

| Field | USER.SAV | DS | Value |
|---|---:|---:|---:|
| HP | 0x206A | 0x4189 | 62 |
| ammo | 0x206D | 0x418C | 46 |
| score | 0x2063 | 0x4182 | 50 |
| X | 0x2043 | 0x4162 | 1755 |
| Y | 0x2045 | 0x4164 | 3779 |
| angle | 0x2037 | 0x4156 | 275 |

The first-slot DOS2 USER.SAV length is 54,758 bytes.

This is the strongest DOS2 pre-first-update restore boundary for these fields so far. It does not close RNG restore, projectile deadlines, all GUARD/OBJECT records, transient caches, short-I/O behavior or the first executed post-load update.

The same natural playthrough also demonstrates reachability of the first sliding panel through USE/Space. Exact secret-panel per-tick timing remains open.
