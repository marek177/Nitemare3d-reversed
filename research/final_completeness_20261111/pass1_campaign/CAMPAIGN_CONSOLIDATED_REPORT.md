# Nitemare 3D: aktualny dokazovy katalog

Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.

Najnovsi report: [aktualna analyticka davka](CRT_ENTRY_GAP_VERSIONS_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) je citatelny, ale dostupna Linux distribucia pre prilozeny ELF nebola zistena. Prirodzene runtime testy zostavaju 0.

## Aktualne meranie PASS1

Mapa `pass1_fcb_prefix/noncode_intervals.csv/json`: **57101 B PARTIAL, 150 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila 887 intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `899ba518a5b8b64b24837e4f40f14e0c918e0bbb2777d2e13ae0803bb42482ed`.

| Centralny katalog | Pocet |
|---|---:|
| Funkcne rozsahy | 109 |
| Nezavisle dekodovane instrukcie | 4068 |
| Instrukcne bajty | 10156 |
| Unia typovanych dat celeho obrazu | 57987 B |
| Ostatne katalogom neposudene bajty | 103217 B |
| Intervaly celeho obrazu | 639 |
| Typovane data v povodnom NON-CODE | 57099 B |
| Kod v povodnom NON-CODE | 0 B |
| Seeded replay pripady | 915637 |
| Oddelene prefixove replay pripady | 65548 |
| Prirodzene runtime testy | 0 |
| Nove DEEP VERIFIED | 0 B |

Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.

## Artefakty a reprodukcia

`campaign_catalog/current_pass1_data_types.csv` ma 661 poli z 96 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.

Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_fcb_prefix CRT_ENTRY_GAP_VERSIONS_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit ba27379dd28c9a689d15233b0fd7017867f50114, pozri `CAMPAIGN_PUBLICATION_RECEIPT_20261112.json`. Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou. Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Menovatele chýbajú, preto N/A. Počet verzií a zhoda medzery nie sú percento sémantickej úplnosti.

| Oblasť | Predošlý odhad | Nové % | Nové potvrdenie | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|entry proti unpack/MZ v 8 DOS|iné pôvodné EXE unpack|nezávislé overenie verzií|
| Dátové typy a konštanty |95 %|N/A|17 B medzera presne zhodná|padding sémantika|alias/writer dôkaz|
| Tabuľky a ukazovatele |93 %|N/A|entry hranice bez IP predpokladu|dynamické referencie|segmentové kontexty|
| Funkcie / ASM / CFG |90 %|N/A|byte signatúra CRT vstupu|predchádzajúca cesta|CFG pred entry|
| RNG |97 %|N/A|bez nového dôkazu|prirodzené poradie|DEMO trace|
| Scheduler |96 %|N/A|bez nového dôkazu|prirodzené callery|call graph|
| DEMO a vstupy |96 %|N/A|bez nového dôkazu|driver ABI|input closure|
| Renderer / VGA |94 %|N/A|bez nového dôkazu|setup|VGA init CFG|
| GUARD / bossovia |93 %|N/A|bez nového dôkazu|selector doména|descriptor flag8|
| Zbrane / projektily |92 %|N/A|bez nového dôkazu|damage callery|effect producer|
| Sprity / HUD / paleta |92 %|N/A|bez nového dôkazu|resource identity|resource parser|
| SAVE / LOAD |92 %|N/A|bez nového dôkazu|prirodzené I/O|stream trace|
| Windows Win16 |92 %|N/A|bez nového Win dôkazu|NE odlišný layout|Win entry vlastný audit|

