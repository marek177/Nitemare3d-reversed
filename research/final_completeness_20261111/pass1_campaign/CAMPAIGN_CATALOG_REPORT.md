# Nitemare 3D: konsolidovaný katalóg

Obraz DOS 2.0: 171 344 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Táto snímka nahrádza staršie headline súčty; história je v `CAMPAIGN_CATALOG_HISTORY_BEFORE_CONSOLIDATION.md`. Kampaň ani PASS1 nie sú dokončené.

## Aktuálne meranie

PASS1 mapa `pass1_id_card_selector/noncode_intervals.csv/json`: **49 867 B PARTIAL, 7 384 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezávislá kontrola overila 405 intervalových SHA, presné členstvo pôvodnej baseline a nulové diery/prekryvy. To dokazuje integritu partition, nie úplnú sémantiku.

Opravená mapa je `[2570E,2770E)`, potvrdená SAVE dĺžkou 2000h od 21FD:373E. Starší scan-only rozsah bol posunutý o bajt; posledný nedoložený bajt sa vrátil do UNKNOWN. Podrobnosti sú v PASS1_FLAGS_MAP_BOUNDARY_REPORT.md.

| Centrálny code/data katalóg | Výsledok |
|---|---:|
| Funkčné rozsahy | 34 |
| Nezávisle dekódované inštrukcie | 1 150 |
| Inštrukčné bajty | 2 666 |
| Únia typovaných dát v celom obraze | 50 671 B |
| Ostatné, katalógom neposúdené bajty | 119 144 B |
| Intervaly celého obrazu | 190 |
| Typované dáta v pôvodnom NON-CODE | 49 823 B |
| Kód v pôvodnom NON-CODE | 0 B |
| Prijaté riadené replay prípady | 2 603 |
| Prirodzené runtime testy | 0 |
| Nové DEEP VERIFIED | 0 B |

2 666 + 50 671 + 118 023 = 171 360. Dátové prekryvy sa počítajú ako únia. Rozdiel medzi PARTIAL 49 867 B a typovanými NON-CODE dátami 49 823 B je **44 B**: všetky sú na overených relokačných WORDoch, ale ich konkrétna dátová rola zostáva otvorená. Neoznačujú sa automaticky za FAR pointery. Centrálne UNKNOWN bajty neprepisujú historické klasifikácie iných auditov.

## Artefakty a reprodukcia

`campaign_catalog/current_pass1_data_types.csv` má **164 polí z 29 zdrojov**, typy, presné hranice, SHA rozsahov a zdrojových CSV. Starý posunutý mapový rozsah sa neimportuje. Katalóg obsahuje aj `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json`.

`python independent_decode_and_catalog.py ABSOLUTE_DECODER_DIR OUTPUTS_DIR` kontroluje identitu obrazu, ledger, bajty/CS:IP/platnosť/dĺžky inštrukcií, jedinečné vlastníctvo kódu, neprítomnosť code/data konfliktov a SHA dátových polí. Overuje zhodu typovaných NON-CODE polí s aktuálnym PARTIAL stavom a pôvod zvyšných 44 B na relokačných sites. `verify_pass1_partition.py` kontroluje PASS1 partition osobitne.

Nový funkčný rozsah v konsolidácii je bit reversal helper 57 B/23 inštrukcií. Prijaté replay prípady: 47 starších + 1 532 error mapper + 1 024 bit reversal = 2 603. Ide o dosadený stav v emulátore, nie prirodzený beh hry. Zamietnuté SMC experimenty sa nepripočítavajú. Čiastočné ASM okná ostatných dávok sa nepreberajú automaticky ako celé funkcie.

## Aktualizácia 13 oblastí

Nové sémantické percento je všade N/A: úplný inventár kontraktov/polí/vetiev chýba. Metodika je uzavreté jednotky / úplný inventár oblasti, runtime parity osobitne. Historické percentá sú orientačné odhady.

| Oblasť | Predošlý odhad | Nové % | Potvrdenie | Neznáme / blokátor | Ďalší krok |
|---|---:|---|---|---|---|
| Mapy a formáty | 99 % | N/A | opravená mapa a flagy | prirodzené súbory | serializačná stopa |
| Dátové typy a konštanty | 95 % | N/A | 45 polí/22 zdrojov | 44 relokačných B bez typu | roly segmentov |
| Tabuľky a ukazovatele | 93 % | N/A | aktuálna typová únia | writeri/lifetime | pointer watchpointy |
| Funkcie / ASM / CFG | 90 % | N/A | 34 rozsahov, 1 150 inštrukcií | kontrakty/dosiahnuteľnosť | caller stopy |
| RNG | 97 % | N/A | bez nového dôkazu | caller inventár | RNG ledger |
| Scheduler | 96 % | N/A | staršie PIT dôkazy zachované | tick ordering | PIT spotrebitelia |
| DEMO a vstupy | 96 % | N/A | bez nového dôkazu | determinizmus | párová DEMO stopa |
| Renderer / VGA | 94 % | N/A | bit reversal začlenený | clipping/orientácia | payload spotrebiteľ |
| GUARD / bossovia | 93 % | N/A | nominálne pole 100×26 | AI/lifecycle | inicializátory |
| Zbrane / projektily | 92 % | N/A | bez nového dôkazu | kolízie/sloty | kolízne vetvy |
| Sprity / HUD / paleta | 92 % | N/A | UI pointer polia začlenené | textový lifetime | SS čítania po návrate |
| SAVE / LOAD | 92 % | N/A | mapové/flagové rozsahy | LOAD parity | párový stav |
| Windows Win16 | 92 % | N/A | staršie NE dôkazy zachované | callback DS/import ABI | runtime selektory |

44 nulových UNKNOWN bajtov v piatich intervaloch nemá dokázaný účel. Ani ich uzavretie by nedokončilo PASS1: 7 384 B je CLASSIFIED ONLY a PARTIAL polia nemajú úplné sémantické kontrakty. GitHub snímka je staršia než konsolidácia a tieto nové lokálne súbory ešte nie sú publikované. PE32 port sa nevykonáva.


Latest type refinement: PASS1_SEGMENT_GLOBALS_REPORT.md pins 12 segment globals via 52 independently decoded direct segment-register loads. Byte statuses unchanged; current untyped PARTIAL relocation bytes: 96.


Latest pointer evidence: PASS1_CRT_HOOK_SLOTS_REPORT.md proves six FAR hook slots via exact indirect CALL sites; slot 2356 remains unresolved. Current typed-source count 123/25, untyped PARTIAL relocation bytes 84.


Latest text evidence: PASS1_MESSAGE_FIELDS_REPORT.md proves 12 FAR message pointer/text pairs through direct caller instructions. Current type catalog 147 fields / 26 sources, untyped PARTIAL relocation bytes 60.


Latest pointer evidence: PASS1_SPLIT_STRINGS_REPORT.md confirms five split WORD FAR text fields via ES:DI scans. Current source catalog: 157 fields / 27 sources; untyped PARTIAL relocation bytes 50.


Latest CRT pointer evidence: PASS1_CRT_PROGRAM_POINTER_REPORT.md pins mutable DS:2144, its initial empty string, environment writer and LDS consumer. Untyped PARTIAL relocation bytes: 48.


Latest selector evidence: PASS1_ID_CARD_SELECTOR_REPORT.md pins two FAR ID-card labels and their format string. Local index bounds and natural callers remain open. Untyped PARTIAL relocation bytes 44, distinct from the 44 UNKNOWN bytes.
