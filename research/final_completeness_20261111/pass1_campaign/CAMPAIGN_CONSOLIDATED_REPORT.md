# Nitemare 3D: aktualny dokazovy katalog

Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.

Najnovsi report: [aktualna analyticka davka](MAIN_MENU_SAVE_GATE_RUNTIME_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Povodny Linux runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) zostava samostatnym auditom. Aktualne original-runtime testy: 20; presny rozsah: retained original packedDOS2 under DOSBox-X with debugger stops: startup/main, BSF/audio/VGA, resources/input, episodes, palettes/DAC, sound metadata/trace and fonts0/1/2; explicit CD intro/flip/read-map captures; AUTOTYPE IRQ/BDA/wait paths through main menu initial draw with414B descriptors and both VGA pages; foreground IRQ frames and explicit paused WORX SS/SP window, no captured private-stack keyIRQ; no host/physical/gameplay/save-load/Win16 parity; prefixes overlap.

## Aktualne meranie PASS1

Mapa `pass1_near_heap_flags/noncode_intervals.csv/json`: **57102 B PARTIAL, 149 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila 888 intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `3021969d4e4348715816361fa387631e7d6cfd9fc9dcc136e26073f0f9984d1b`.

| Centralny katalog | Pocet |
|---|---:|
| Funkcne rozsahy | 138 |
| Nezavisle dekodovane instrukcie | 5389 |
| Instrukcne bajty | 13486 |
| Unia typovanych dat celeho obrazu | 58018 B |
| Ostatne katalogom neposudene bajty | 99856 B |
| Intervaly celeho obrazu | 721 |
| Typovane data v povodnom NON-CODE | 57100 B |
| Kod v povodnom NON-CODE | 0 B |
| Seeded replay pripady | 990555 |
| Oddelene prefixove replay pripady | 65548 |
| Original-EXE runtime scenare s definovanymi zasahmi | 20 |
| Runtime BSS tabulky mimo file image (nezvysuju PASS1) | 4054 B |
| Runtime buffer refinements, uz zahrnute v PASS1 | 4014 B /12 intervalov |
| Nove DEEP VERIFIED | 0 B |

Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.

## Artefakty a reprodukcia

`campaign_catalog/current_pass1_data_types.csv` ma 662 poli z 97 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.

Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_near_heap_flags MAIN_MENU_SAVE_GATE_RUNTIME_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit d571a31282b1a15914fa6c1559fb44a4d204d054, pozri `CAMPAIGN_MAIN_MENU_PUBLICATION_RECEIPT_20261112.json`. Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou. Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.

Samostatny Win110 paletovy doplnok: 4 rozsahy, 229 instrukcii / 641 B, 22 seeded pripadov. Nie je zahrnuty v DOS adresnej partition ani v DOS replay sucte; skutocny Win16 runtime 0.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|5reálnych SAVE súborov/9stride intervalov; DOS2 prefix49B|celý SAVE payload a EXE väzby k variantom|full SAVE/LOAD schema a map init|
| Dátové typy a konštanty |95 %|N/A|20menu focus BYTE polí a49B SAVE prefix; count/seek výsledky ignorované|ostatné record polia a payload54709B|textové metriky a header callery|
| Tabuľky a ukazovatele |93 %|N/A|3runtime menu tabuľky414B, FAR28DD:0E10 a firstfocusid1|iné descriptor varianty a cursor domény|textové caller domény|
| Funkcie / ASM / CFG |90 %|N/A|2nové funkcie439B/157inštrukcií;780menu/save replay|celá1946, follow-up1176 a Win ekvivalent|menu CFG a SAVE follow-up|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|WORX private SS/SP a timer phase/depth/EOI vetvy|herný scheduler, tempo a celý timer chain|timer08 entry/exit trace a väzba na main loop|
| DEMO a vstupy |96 %|N/A|3wait návraty,6make/break scanov,3BIOS dequeue; menu ready|menu navigácia, DEMO poradie a gameplay vstupy|menu a širšie vstupné domény|
| Renderer / VGA |94 %|N/A|menu initial draw;128000B oboch stránok aDAC zachované|host-surface/scanout, nezávislý menu pixel golden|scanout a prirodzený vstup|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|DAC768 zložiek;71 použitých farieb,192000 RGB6 komponentov bez rozdielu|nepoužitý255 sa líši; Win OS a host frame|prirodzený text/font metrics a scanout|
| SAVE / LOAD |92 %|N/A|DOS2 metadata reader proti5reálnym SAVEs;54758size gate|full SAVE/LOAD, seek/read error model a rollback|izolovaný metadata runtime a follow-up1176|
| Windows Win16 |92 %|N/A|Win1104funkcie/229inštrukcií,23fixupcalls,22replay|skutočnéWin16DS/API/runtime|CreatePalette/WinG trace|

