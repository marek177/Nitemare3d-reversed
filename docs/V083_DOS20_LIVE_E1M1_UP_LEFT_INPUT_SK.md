# Nitemare 3D DOS v2.0 — V083: nový živý E1M1 test ↑+← a postupného uvoľnenia

**21.10.2026. Dôkazový stupeň: FRESH_ORIGINAL_DOS2_LIVE_RUNTIME.** Tento záznam sumarizuje skutočný DOSBox-X + pôvodný N3D-E-20.EXE, nie predikciu remaku ani syntetickú animáciu.

## Overenie a vstup

- Pôvodný rozbalený EXE SHA256 `552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301`.
- E1M1 spustená v izolovanom DOSBox-X Advanced History na virtuálnom displeji; skutočné XTest jednorazové key-down/key-up.
- Kontrola 18-B podpisu pôvodnej FEFA a 16-B podpisu 1021E v živom guest RAM. DS=2F95, vstupy player XY=4162/4164, heading=4156, sin/cos Q10=41B2/41B4, render count=4540.
- Začiatok: hráč `(1440,3616)`, heading 0, VEC=592, spany=9.
- Read-only host `/proc/PID/mem` polling: **486 vzoriek**, **šesť z šiestich** prijatých XTest udalostí. Median polling interval 13,51 ms, maximum 662,46 ms. Polling nie je emulovaný presný tick.

## Pôvodný runtime výsledok

| Fáza | Vzorky | X/Y pred → po | Smer pred → po | Render čítač + |
|---|---:|---|---|---:|
| Bez vstupu | 53 | 1440,3616 → 1440,3616 | 0 → 0 | 13 |
| **↑ + ←** | 126 | 1440,3616 → 1371,3495 | 0 → 252 | 18 |
| **← bez ↑** | 53 | 1371,3495 → 1371,3495 | 252 → 228 | 4 |
| Obe uvoľnené | 117 | 1371,3495 → 1371,3495 | 228 → 228 | 22 |
| Iba ↑ | 100 | 1371,3495 → 1371,3604 | 228 → 228 | 11 |
| ↑ uvoľnená | 37 | 1371,3604 → 1371,3604 | 228 → 228 | 7 |

**Kľúčové pozorovania:** ľavé otáčanie **22/22 pozorovaných krokov −6 modulo 360**, vrátane `0→354`. Uvoľnenie ↑ pri ponechanej ← v tomto stave ukončilo XY posun, nie rotáciu. Po uvoľnení oboch kláves zostali XY a heading nemenné počas 117 vzoriek a +22 render čítača. Pri smere 228 spôsobilo samostatné ↑ Y+109 bez zmeny X; tento konkrétny výsledok nevylučuje kolíziu alebo sklz pri stene.

Všetkých **23 rôznych pozorovaných headingov** malo v odčítaných vzorkách jednoznačnú zhodnú dvojicu `sinQ10/cosQ10`. Kotvy: heading 0 `(0,1024)`, 354 `(-107,1018)`, 270 `(-1024,0)`.

## Kontrast v0.82

Predchádzajúci originálny runtime s → ukázal v samostatnej fáze 7×+6 bez pohybu XY. Tento nový v0.83 overuje opačnú rotáciu a obrátené poradie uvoľnenia. Odlišný počiatočný stav a počet host vzoriek nedovoľujú porovnávať rýchlosť otáčania za sekundu ako presný tickový kontrakt.

## Dôkazy, testovateľnosť a limity

Používateľovi dodaný súkromný ZIP `N3D_DOS20_E1M1_LIVE_UP_LEFT_Runtime_V083_20261021.zip` obsahuje originálny odvodený 486-riadkový CSV, JSON s udalosťami, **skutočne vykonaný** XTest+read-only-RAM experiment (jednorazový PID/base), druhý nezávislý audit a **8/8 lokálnych mutačných testov**, SHA manifest. ZIP SHA256 `74f4bed58291af33d2c16af1e7eb5da9c7b3869cbbaa4d1cd258af05d93384dc`. Pôvodný komerčný EXE/IMG/MAP ani 64 KiB guest RAM dump v ZIP-e nie sú. RAW CSV/JSON sa na verejný GitHub nenahráva.

**Neuzavreté:** presné poradie vstupného dispatchera v jednom emulovanom ticku, ďalšie smery a kolízne body, spätná kontrola s totožnou deterministickou sekvenciou v C++ remake. Žiadna 1:1 behaviorálna ani pixelová parita originál↔remake nie je deklarovaná. Produkčný `Raycaster.cpp` a `src/main.cpp` ostávajú bez zásahu.
