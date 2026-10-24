# Implementačná hranica — 22.–24.10.2026

| ID | Modul | Source evidence | Predpoklad / vstupy | Akceptácia | Stav |
|---|---|---|---|---|---|
| P0-01 | raw saves | Archívne DOS/Win vzorky; verzia musí byť identifikovaná | binary blob | byte-for-byte identity | návrh |
| P0-02 | input | V085/V086 live | key transition ledger | bitmask trace, timestamp policy | čiastočný dôkaz |
| P0-03 | projectile pool | V056/V083 | original slot trace | exact 0→1→2→0 sample | čiastočný dôkaz |
| P0-04 | RNG/DEMO | V063/V076 | seed + exact input chronology | first divergence | otvorené |
| P0-05 | renderer | V078–V080 | paired original image/DS/IMG | 64000+768 zero diff | otvorené |
| P0-06 | Win16 load | V059 | exact Win build + save blob | first CPU and rendered frame | otvorené |
| P0-07 | GUARD | V050/V058 | actor list and tick | same order, state, damage | otvorené |
| P0-08 | MAP 0x25–0x28 | V053/V054 | cross-build versioned map | exact semantics by version | otvorené |

Public repo does not contain original commercial binary data. A test that passes without matched original evidence is marked **synthetic**, never original-vs-port parity.
