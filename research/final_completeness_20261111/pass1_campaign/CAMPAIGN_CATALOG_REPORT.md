# Nitemare 3D: aktualny dokazovy katalog

Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.

Najnovsi report: [aktualna analyticka davka](XMS_REQUEST_RUNTIME_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Povodny Linux runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) zostava samostatnym auditom. Aktualne original-runtime testy: 21; presny rozsah: retained original packedDOS2 under DOSBox-X with debugger stops: startup/main, BSF/audio/VGA, resources/input, episodes, palettes/DAC, sound metadata/trace and fonts0/1/2; explicit CD intro/flip/read-map captures; AUTOTYPE IRQ/BDA/wait paths through main menu initial draw with414B descriptors and both VGA pages; foreground IRQ frames and explicit paused WORX SS/SP window, no captured private-stack keyIRQ; first XMS transfer return after episode1/difficulty1 selection and 57295B NONCODE endpoint snapshot; no full map-load/host/physical/gameplay/save-load/Win16 parity; prefixes overlap.

## Aktualne meranie PASS1

Mapa `pass1_xms_move_request/noncode_intervals.csv/json`: **57118 B PARTIAL, 149 B CLASSIFIED ONLY, 28 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila 892 intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`.

| Centralny katalog | Pocet |
|---|---:|
| Funkcne rozsahy | 141 |
| Nezavisle dekodovane instrukcie | 5541 |
| Instrukcne bajty | 13854 |
| Unia typovanych dat celeho obrazu | 58034 B |
| Ostatne katalogom neposudene bajty | 99472 B |
| Intervaly celeho obrazu | 725 |
| Typovane data v povodnom NON-CODE | 57116 B |
| Kod v povodnom NON-CODE | 0 B |
| Seeded replay pripady | 993211 |
| Oddelene prefixove replay pripady | 65548 |
| Original-EXE runtime scenare s definovanymi zasahmi | 21 |
| Runtime BSS tabulky mimo file image (nezvysuju PASS1) | 4054 B |
| Runtime buffer refinements, uz zahrnute v PASS1 | 4014 B /12 intervalov |
| Nove DEEP VERIFIED | 0 B |

Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.

## Artefakty a reprodukcia

`campaign_catalog/current_pass1_data_types.csv` ma 667 poli z 98 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.

Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_xms_move_request XMS_REQUEST_RUNTIME_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit 57386a3b2a144c855f06cc568339757a5f8ae33b, pozri `CAMPAIGN_XMS_PUBLICATION_RECEIPT_20261112.json`. Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou. Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.

Samostatny Win110 paletovy doplnok: 4 rozsahy, 229 instrukcii / 641 B, 22 seeded pripadov. Nie je zahrnuty v DOS adresnej partition ani v DOS replay sucte; skutocny Win16 runtime 0.

## Aktualizácia 13 oblastí

Predošlé orientačné percentá sú historické odhady, nie merané východiská. Pre každú oblasť je nová sémantická úplnosť N/A: počet uzavretých jednotiek / úplný inventár jednotiek oblasti; úplné menovatele a kritériá closure zatiaľ chýbajú. Merateľný PASS1 podiel nižšie je stav bajtovej klasifikácie, nie sémantická úplnosť. Všetky nové funkcie a dáta sú PARTIAL, DEEP VERIFIED nepribudlo. Nezmenené oblasti sú výslovne uvedené.

|Oblasť|Predošlý odhad|Nové % / metodika|Nový potvrdený výsledok|Zostávajúce neznáme|Blokujúci problém|Najbližší krok|
|---|---:|---|---|---|---|---|
|Mapy a formáty|99 %|N/A, closure/inventár|prirodzený game start epizóda1, index level0|celá map inicializácia|koncový bod map loader ešte nezachytený|pokračovať po prvom XMS prenose|
|Dátové typy a konštanty|95 %|N/A, closure/inventár|5 XMS polí /16B z UNKNOWN do PARTIAL|28 UNKNOWN B a149 CLASSIFIED ONLY B|žiadny prístup k nim v tomto scenári|sledovať zostávajúcich28B počas map init|
|Tabuľky a ukazovatele|93 %|N/A, closure/inventár|relokovaný DS:2560→1BE7:0200; FAR XMS arg|celý resource-cache lifecycle|alokácia/free a reverse direction neuzavreté|XMS handle init/free a read callery|
|Funkcie / ASM / CFG|90 %|N/A, closure/inventár|3 rozsahy /368B /152 inštrukcií;2656 replay|caller domény, diagnostika FBA:000C|externé závislosti v replay stubované|rozšíriť volací graf0768|
|RNG|97 %|N/A, closure/inventár|žiadny nový dôkaz RNG|natural srand/rand a DEMO poradie|prvý gameplay frame nezachytený|trace RNG callery po map init|
|Scheduler|96 %|N/A, closure/inventár|žiadny nový dôkaz schedulera|herná slučka a timer chain|runtime končí pred slučkou|dosiahnuť0D29:0A31|
|DEMO a vstupy|96 %|N/A, closure/inventár|3SPACE+3ENTER; voľba main1/episode15/difficulty19|iné voľby a DEMO|iba jeden prirodzený výber|ďalšie selector domény a DEMO trace|
|Renderer / VGA|94 %|N/A, closure/inventár|žiadny nový renderer parity dôkaz|scanout a full gameplay frame|žiadny nezávislý frame golden|zachytiť prvý herný frame|
|GUARD / bossovia|93 %|N/A, closure/inventár|žiadny nový AI dôkaz|bossové vetvy a actor runtime|map init nedokončený|actor entry/dispatch po map init|
|Zbrane / projektily|92 %|N/A, closure/inventár|žiadny nový damage dôkaz|kolízie a damage callery|chýba gameplay scenár|izolovaný damage trace|
|Sprity / HUD / paleta|92 %|N/A, closure/inventár|žiadny nový closure dôkaz|textové metriky a HUD frame|gameplay endpoint nezachytený|HUD draw pri prvom frame|
|SAVE / LOAD|92 %|N/A, closure/inventár|žiadny nový SAVE/LOAD dôkaz|54709B payload a rollback|metadata nie sú celý formát|follow-up0277:1176 a runtime SAVE|
|Windows Win16|92 %|N/A, closure/inventár|žiadny nový Win16 dôkaz|Win XMS ekvivalent / DS/API kontrakt|žiadny Win16 runtime|nájsť fixup-backed ekvivalent cache|

