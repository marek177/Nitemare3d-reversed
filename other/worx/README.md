# WORX Toolkit 2.1 — RE-1TO1-MAX v0.16

**Aktuálna verzia:** 16. október 2026. Cieľom je čistá rekonštrukcia pôvodného WORX 2.1 správania z DOS hry Nitemare 3D, vrátane vzácnych vetiev, časovania a zvukových výstupov. Tento balík je **čiastočná staticky overená implementácia**, nie kompletný náhradný DOS driver.

Začni dokumentom **[README_CURRENT_SK.md](README_CURRENT_SK.md)**; všetky nové machine-byte dôkazy a testovateľné funkcie sú vo **[WORX21_FINDINGS_v016_SK.md](WORX21_FINDINGS_v016_SK.md)**. Zostávajúce blokery sú vo **[WORX21_UNKNOWN_TO_100_SK.md](WORX21_UNKNOWN_TO_100_SK.md)**.

Projekt má 11 CTest testovacích skupín a nové CLI audity `tools/audit_midi_routing_v016.py`, `tools/audit_stream_routing_v016.py` a staršie audity v0.14/v0.15. Kód je v `src/` a `include/worx21/`; používa C++17 a CMake. Do archívu nie sú pribalené originálne komerčné EXE ani zvukové dáta.

**Dôkazový stav:** auditované čiastkové algoritmy WORX NIE SÚ to isté ako úplné `INT63` obsluhy. Počet predtým auditovaných API kontraktov sa nemení (41 zo 79 nenulových); ďalších 38 API obslúh a podstatná časť transitive závislostí ostáva otvorená. Bežný DOSBox runtime originálu a 100 % zvuková/IRQ parita neboli touto verziou potvrdené.
