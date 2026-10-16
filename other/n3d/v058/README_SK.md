# Nitemare 3-D — RE MAX v0.58 (lokálny analytický balík)

**Dátum:** 16. 10. 2026. Čisto statická rekonštrukcia prvkov `GUARD hit → score / SFX / variant RNG` zo **súkromných, SHA-256-identifikovaných originálov**. Žiadny originálny gameplay CPU trace ani dôkaz úplnej behaviorálnej/timing/pixel 1:1 parity. Nejde o číslo aktuálnej GitHub release.

## Balík

- `REPORT_SK.md` — výsledky s hranicami dôkazu, call-order, nové edge cases, inštrukčné kotvy.
- `tools/verify_v058.py` — read-only trojprofilový verifikátor; z pôvodných bajtov dekóduje **25 score + 24 death-sound + 24 state-7-sound** vetiev pre každý build. Kontroluje **5 kompletných funkčných tiel × 3 buildy**, maskuje iba doložené operandové/table pozície a padding; testuje lokálne poradie zásahu.
- `evidence_v058.json` — iba neoriginálne metadáta, odvodené hodnoty, relatívne ciele a počty; **bez originálnych bajtov EXE**.
- `class_score_sound_v058.csv` — 256 tried, 3 výsledkové hodnoty s defaultmi. `rng%N+K` vyjadruje podmienený *lokálny* výber.
- `branch_event_order_v058.csv` — dôkazové poradie čiastočných vetiev zásahu.
- `model_v058.py`, `src/N3DV058GuardDeathContract.hpp` — explicitne obmedzené clean-room referenčné kontrakty.
- `tests/` — dátovo nezávislé syntetické Python/C++17 testy.
- `UNKNOWN_FRONTIER_v058.csv` — ďalšie otázky v poradí RE-first.

## Spustenie na súkromných origináloch (Windows PowerShell)

```powershell
py tools/verify_v058.py `
  --dos20 "C:\N3D\N3D_REMAX_EXEPACK_UNPACKED_RAW_20261014.bin" `
  --win110 "C:\N3D\nite3w_v110.exe" `
  --winalt "C:\N3D\nite3w_v18.exe" `
  --out .
py -m unittest discover -s tests -p "test_v058.py" -v
```

C++17 (MSVC developer prompt alebo g++):

```bash
g++ -std=c++17 -Wall -Wextra -Werror -O2 tests/test_cpp_v058.cpp -o test_v058
./test_v058
```

## Adresovanie

- `DOS IMG:` = offset v **unpacked headerless MZ load-image**, nie runtime segment DOSBox-X.
- `Win NE3:` = offset **logického 3. segmentu NE súboru**, nie runtime Windows selector.
- Win16 raw FAR operandové hodnoty sú relatívne linkované; **úplný NE relocation fixup audit nie je obsahom tejto iterácie**.
- Overiť podpis originálu pred aplikovaním binárnych offsetov; verifikátor odmieta iné buildy.
- Syntetické testy ani tieto zistenia nepredstavujú pôvodnú 1:1 runtime paritu.

**Pôvodné komerčné EXE, mapy, SND a IMG nie sú súčasťou balíka.** Žiadny GitHub commit nebol vykonaný.
