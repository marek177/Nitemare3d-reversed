# WORX Toolkit 2.1 — RE MAX v0.14 (16.10.2026)

**Status:** fungujúca a testovaná čiastočná čistá rekonštrukcia interných WORX algoritmov, nie 100 % hotový driver. N3D DOS v2.0 original EXE je zdrojom verifikovaných machine bytes; N3D DOS v1.9 je nezávislý druhý build na cross-version porovnanie.

- **41/79 nenulových INT63 API obslúh** má doterajšie auditované kontrakty. Zvyšných 38 úplných telies nie je hotových; 3 ďalšie sloty sú v počiatočnom obraze nulové.
- **v0.14 pridáva nové strojovo auditované čiastkové funkcie:** MIDI track gate `44B3–44ED`, unknown meta skip `4553–455B`, EOT `458C–45DC`, XMS refill argument/indirect far-call shell `5863–58D7`, stream `08h` `5FBF–5FD1` a stream `0Ch` `5FD2–5FF2`.
- Nie je simulovaný úspech externých funkcií `XMS`, `DOS 312E`, `MIDI replay 4265/4389`. Ich backendy sú injektované a chýbajúce požadované volania vyvolávajú chybu.
- Šesť nových binárnych segmentov má SHA256 kontrolu, 25 strojových kotiev a 11 kontrolovaných priamych branch targetov.
- DOS v1.9 vs v2.0: presné mapovanie 6 rutín, 41 posunutých operandových bajtov (`old low= new low+4`), inak byte-identické v týchto rozsahoch; nie dôkaz pre inú časť knižnice.
- Overené na GCC aj Clang: **8/8 CTest skupín úspešných** s originálnymi v1.9 aj v2.0 binárkami cez env vstupy. Windows/MSVC ani originálny živý sound/IRQ runtime nebol vykonaný.

## Kde začať

`WORX21_FINDINGS_v014_SK.md` — nový technický a binárny dôkaz.

`WORX21_UNKNOWN_TO_100_SK.md` — presné neuzatvorené oblasti.

`src/audio_deep.cpp`, `include/worx21/audio_deep.hpp`, `tests/test_audio_deep.cpp` — nové implementácie a regresie.

`data/worx21_audio_deep_static_v014.json` — machine-byte ledger.

`data/worx21_crossversion_v19_v20_v014.json` — DOS verzie porovnané na 6 úsekoch.

## Ako zostaviť na Windows 11 cez Visual Studio (CMake)

```powershell
cmake -S . -B build -G "Visual Studio 17 2022" -A Win32
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
```

Zvoľ generátor zodpovedajúci nainštalovanému Visual Studio, ak je iný. C++17 je povinné. Binárne originály sú mimo distribuovaného zdrojového balíka.

**100 % akceptačný kontrakt:** všetky príslušné vetvy, pointery, globals, flags, priame a nepriame volania, návraty aj hardware I/O, timing a originál/clone porovnávanie pri rovnakom prostredí. Žiadne percento zvukovej parity sa neodvodzuje z počtu identifikovaných handlerov.
