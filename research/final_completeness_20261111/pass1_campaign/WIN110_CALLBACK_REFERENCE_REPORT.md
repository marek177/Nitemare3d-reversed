# Win1.10 — hľadanie producentov callbackového bloku

11. 11. 2026. Nová ohraničená kontrola historického inventára, **PARTIAL**, bez runtime testov a bez nových DEEP VERIFIED bajtov.

## Metodika

`scan_win110_callback_references.py` číta `reachable.asm` zo staršej analýzy `analyzuj-staticky-do-najva-ej-hlbky/outputs/nite3w - 110`. Názov reachable nepreberá ako dôkaz dosiahnuteľnosti. Zdrojový výpis SHA-256 `d24c60c587e2fb20898fe1384e37d3d118524f2f66646d298e5a24872244dcd3` obsahuje 60 231 jedinečných adries. Pre každú kontroluje surové bajty v autentickom NE segmente a dĺžku/platnosť nezávislým iced-x86 dekóderom. Všetkých 60 231 týchto kontrol prešlo; neurčuje to úplnosť CFG, neprekrývanie inštrukcií ani sémantickú správnosť staršieho inventára.

Na rozdiel od hľadania textu adresy používa `InstructionInfoFactory.used_memory()`: vyberie pamäťové operandy bez base/index registra, ktorých čítaný či zapisovaný interval pretína `[20D0,20DC)`. Zachováva segmentový register a veľkosť prístupu. Kontrola sa týka efektívneho offsetu, nie potvrdenej runtime identity dátového segmentu.

## Výsledok

| Metrika | Výsledok |
|---|---:|
| Historické inštrukčné začiatky skontrolované proti EXE/dekóderu | 60 231 |
| Chyby bajtov, segmentu alebo dĺžky | 0 |
| Priame pamäťové referencie na callbackový interval | 9 |
| Priame zapisujúce referencie v tomto inventári | 0 |
| Zapisujúce pamäťové operandy s base/index, bez vyriešenia aliasov | 27 484 |
| Kandidáti podľa samotného dvojbajtového vzoru | 10 |

Deväť priamych referencií sa zhoduje s lokálnou analýzou: čítania na `2:3831`, `3840`, `3843`, `3849`, `3852`, `3855`, `385C`, `396B`, `3974`. Tri z nich čítajú FAR pointer šírky 4 B, ostatné WORD. Všetky používajú DS. Žiadny nový priamy producent v tomto inventári nebol nájdený.

Desiaty vzorový kandidát `1:22E5` obsahuje bajty `9A D8 20 00 00`: ide o FAR CALL operand s relokáciou, nie pamäťový prístup DS:20D8. Demonštruje, prečo sa samotné vyhľadanie dvojbajtovej adresy nemôže počítať ako dátový xref.

**Nula priamych zápisov nie je dôkaz nemennosti pointera.** Zostávajú vypočítané adresy, REP/bulk inicializácia, zápisy mimo tohto inventára, externé volania a segmentové aliasy. Počet 27 484 je počet pamäťových operandov zapisujúceho typu s registrom, nie počet možných aliasov callbacku; obsahuje aj bežné stack operandy. Nemožno ho použiť ako menovateľ sémantického pokrytia.

## Artefakty a pokračovanie

`win110_callback_refs/direct_memory_references.csv` obsahuje presné bajty, adresy, riadky zdroja, width, access enum a segmentový register. `literal_candidates.csv` drží kandidátov oddelene. `validation_issues.csv` má iba hlavičku; súčty a hashe sú v `summary.json`.

Reprodukcia: `python scan_win110_callback_references.py WIN110_EXE HISTORICAL_ASM ABSOLUTE_DECODER_DIRECTORY OUT_DIRECTORY`.

Najbližší krok: sledovať pointerové a blokové zápisy pri startup ceste vrátane funkcií spúšťaných z inicializačných tabuliek; prvý writer je vhodnejšie overiť watchpointom než vyhlasovať globálnu nemennosť z neúplného statického inventára. Konkrétne runtime kroky a otvorený DS ABI sú v `WIN110_CALLBACK_REPORT.md`. DOS PASS320 mapa, DOS bajtový katalóg a percentá zostávajú bez zmeny.
