# V087 — veľká GitHub RE aktualizácia (21.10.2026)

**Typ:** integrácia poznania a bezpečných kontraktov, NIE nový hotový gameplay/renderer. Verzovanie spustiteľného preview ostáva 0.78, lebo Raycaster je naďalej diagnostické DDA.

## Pridané
- Aktuálna porovnávacia tabuľka výskumných oblastí a percent: RE_PROGRESS_20261021_SK.md.
- P0/P1 tabuľka experimentov a prijímacích brán: RE_P0_ACCEPTANCE_GATES_20261021_SK.md.
- C++20 typovaný originálny DS:3F50 model (7 pozorovaných bitov, všetkých 8 akčných masiek): src/re/N3DDos20InputMaskContract.hpp.
- CTest pre 128 held-key kombinácií, uvoľnenie a zachovanie neklasifikovaných bitov.
- Normalizovaný CSV auditor tools/n3d_input_mask_ledger.py a 12 syntetických odmietacích/akceptačných regresií.
- Cross-platform GitHub Actions (Linux/Windows), bez originálnych dát.

## Už overené v skorších commitoch; bez duplicity
- DOS2 V078/V079/V080 originálny U/IMG/XLAT a jedna presná 42-pixelová stena, nie komplet framebuffer.
- DOS2 V081–V084B E1M1 XY, heading, kolízie a Alt-strafe.
- V085/V086 8/8 akčných masiek, 1716 pôvodných guest-RAM vzoriek, 24 XTest prechodov.
- DEMO RNG a time-ordering, GUARD/OBJECT, Win16 NE/WinG/callgraph podľa existujúcich dôkazov.

## Bezpečné spustenie
~~~sh
cmake -S . -B build-v087 -DN3D_ENABLE_SDL3=OFF -DCMAKE_BUILD_TYPE=Debug
cmake --build build-v087 --target n3d_dos20_input_mask_contract_test
ctest --test-dir build-v087 -R n3d_dos20_input_mask_contract_test --output-on-failure
python3 -m unittest discover -s tests -p test_n3d_input_mask_ledger.py -v
~~~

Normalizovaný súkromný CSV má columns phase,expected_mask,observed_mask,stable. Príklad offline:
~~~sh
python3 tools/n3d_input_mask_ledger.py --csv /private/action-masks.csv --strict-stable
~~~
Nepriraďovať host polling v milisekundách k emulovaným DOS tickom. Tento C++ model nič nemení v pôvodnej hre ani neimplementuje FIRE/USE dispatcher. Žiadny test tu nepotvrdzuje end-to-end originál-vs-port paritu.
