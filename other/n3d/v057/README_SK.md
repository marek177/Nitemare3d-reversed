# Nitemare3D RE MAX NEXT v0.57 — statický balík

Lokálna read-only analýza troch vlastných originálnych hash-identified EXE; čisté Python/C++17 modely bez originálnych dát. Žiadne spustenie pôvodnej hry, žiadne nepreukázané tvrdenie o pixelovej alebo časovej parite.

## Súbory

- `REPORT_SK.md` — kompletný slovenský výsledok, presná mapa adries, hranice istoty.
- `verify_v057.py` — vyžaduje 3 presné SHA; kontroluje pôvodné opcode okná, celé porovnávacie telá, všetky class/state tabuľky a nested DOS wall lookup.
- `model_v057.py` — dokumentované referenčné lokálne kontrakty a explicitné callback placeholdery.
- `src/N3DV057GeometryCombat.hpp` — samostatný C++17 kontrakt.
- `tests/test_v057.py` — syntetické bezautorské testy (41 testov).
- `tests/test_cpp_v057.cpp` — compile/run C++17 kontrola.
- `evidence_v057.json` — byte-witness register a hash scope z overenia originálov.
- `damage_class_matrix_v057.csv`, `hit_state_routes_v057.csv`, `geometry_edge_scenarios_v057.csv` — modelové scenáre a rozbočovače.
- `UNKNOWN_FRONTIER_v057.csv` — presné ďalšie neprieskumné ciele.
- `TEST_RESULTS.txt` — príkazy/výsledky spustenia testov.
- `MANIFEST_SHA256.json` — checksum priložených analytických súborov.

## Overenie

Originálne súbory patria majiteľovi a **nie sú** súčasťou balíka. `verify_v057.py` sa odmietne spustiť na nesprávnej verzii či nesprávne rozbalenom súbore. Modely vedia pracovať bez originálu, ale porovnanie syntetických vstupov nie je pôvodný gameplay runtime dôkaz.

Na Windows sa v adresárovej štruktúre balíka dá spustiť:

```powershell
py -m unittest discover -s tests -p test_v057.py -v
py verify_v057.py --dos20 C:\N3D\DOS20_UNPACKED.bin --win110 C:\N3D\NITE3W110.EXE --winalt C:\N3D\NITE3W_ALT.EXE --out evidence_local.json
```

Hranice: Win16 vnorené dve wall rutiny, full nested damage effects, original gameplay trace a 100 % parity zostávajú OPEN.
