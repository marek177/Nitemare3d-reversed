# WORX Toolkit 2.1 — aktuálny zdrojový stav RE MAX v0.16 (16.10.2026)

**Toto sú čiastočné rekonštruované C++17 zdrojové súbory založené na pôvodných strojových bajtoch, NIE pôvodné zdrojáky Mystic Software.** `/worx/` v GitHub repozitári má obsahovať iba `.cpp/.hpp`; všetky README, testy, CMake, dôkazy sú v `/other/worx/`.

- Zostávajúci základ v0.15: MIDI status/running status/FF tempo/EOT a VLQ delta; callback teraz dostáva *skutočné AX pri 3A67*, nie AX z cache.
- **Nové v0.16:** `src/midi_routing.cpp`, `include/worx21/midi_routing.hpp`: lokálny `3A67` direct MPU / alternate synth, hardvérový shell `58F8` s maximom 65535 čítaní a FAR `3896` callbackom. Pri neimplementovaných cieľoch 3941/3E34/3B5B explicitný callback/exception.
- **Nové v0.16:** `src/stream_routing.cpp`, `include/worx21/stream_routing.hpp`: hlavičkový a typový 5F3E router, poradie DSP stop/read1/read3, otvorené continuation pre režimy 01/02/03/09; 08 a 0C používajú existujúce lokálne implementácie.
- **11/11 CTest skupín** lokálne prešlo na GCC aj Clang s pôvodnými DOS 1.9/2.0 EXE dostupnými cez premenné prostredia. Windows/MSVC build a živé DOSBox-X I/O parity netestované.
- 49 opcode kotiev / 30 lokálnych vetiev / 10 priamych CALL v troch nových pôvodných rozsahoch, 31 presne +4 byte operandov v1.9 oproti v2.0.
- Kompletná technická príloha `WORX21_FINDINGS_v016_SK.md`, otvorené body `WORX21_UNKNOWN_TO_100_SK.md`.

V repozitári priamo funguje `cmake -S other/worx -B build-worx && cmake --build build-worx && ctest --test-dir build-worx --output-on-failure`: `CMakeLists.txt` automaticky používa zdrojový strom `../../worx` a testy v `other/worx/tests`. Samostatný RE balík používa vlastné lokálne `include`/`src`. C++17.
