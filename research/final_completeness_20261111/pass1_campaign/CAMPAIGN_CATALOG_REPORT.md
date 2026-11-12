# Nitemare 3D: aktualny dokazovy katalog

Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.

Najnovsi report: [aktualna analyticka davka](WORX_PRIVATE_STACK_RUNTIME_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Povodny Linux runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) zostava samostatnym auditom. Aktualne original-runtime testy: 19; presny rozsah: retained original packed DOS2 under DOSBox-X with debugger stops: startup/main, BSF/audio/VGA, resources/input, episodes, palettes/DAC, sound metadata/trace, UIF fonts0/1/2; explicit CD back-buffer/flip and read-map intervention; AUTOTYPE IRQ make/break, BIOS3920, wait exit; hardware frames identify0BDE:00C6, explicit paused WORX stack-switch window verifies privateSS/SP but does not capture nested keyIRQ on that stack; no host/physical/gameplay/Win16 parity; prefixes overlap.

## Aktualne meranie PASS1

Mapa `pass1_near_heap_flags/noncode_intervals.csv/json`: **57102 B PARTIAL, 149 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila 888 intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `3021969d4e4348715816361fa387631e7d6cfd9fc9dcc136e26073f0f9984d1b`.

| Centralny katalog | Pocet |
|---|---:|
| Funkcne rozsahy | 136 |
| Nezavisle dekodovane instrukcie | 5232 |
| Instrukcne bajty | 13047 |
| Unia typovanych dat celeho obrazu | 58018 B |
| Ostatne katalogom neposudene bajty | 100295 B |
| Intervaly celeho obrazu | 711 |
| Typovane data v povodnom NON-CODE | 57100 B |
| Kod v povodnom NON-CODE | 0 B |
| Seeded replay pripady | 989775 |
| Oddelene prefixove replay pripady | 65548 |
| Original-EXE runtime scenare s definovanymi zasahmi | 19 |
| Runtime BSS tabulky mimo file image (nezvysuju PASS1) | 4054 B |
| Runtime buffer refinements, uz zahrnute v PASS1 | 3600 B /9 intervalov |
| Nove DEEP VERIFIED | 0 B |

Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.

## Artefakty a reprodukcia

`campaign_catalog/current_pass1_data_types.csv` ma 662 poli z 97 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.

Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_near_heap_flags WORX_PRIVATE_STACK_RUNTIME_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit 596db1ae2293ee6c17d280dfae6d9cbea42eb30c, pozri `CAMPAIGN_WORX_STACK_PUBLICATION_RECEIPT_20261112.json`. Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou. Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.

Samostatny Win110 paletovy doplnok: 4 rozsahy, 229 instrukcii / 641 B, 22 seeded pripadov. Nie je zahrnuty v DOS adresnej partition ani v DOS replay sucte; skutocny Win16 runtime 0.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|CD DSTOPEN.IMG:128B header,19781B RLE,769B tail; 64000 pixelov|iné PCX/IMG domény; stride/planes ignorované|textové resource a menu dáta|
| Dátové typy a konštanty |95 %|N/A|nových30B direct stack/control polí mimo NON-CODE;512B kandidat len CLASSIFIED|492B candidate backing bez potvrdenej kapacity|textové metriky a header callery|
| Tabuľky a ukazovatele |93 %|N/A|nových128 font1FAR; všetky384FAR pointery skupín0/1/2 byte-exact|pointer index0 a signed-char indexy|textové caller domény|
| Funkcie / ASM / CFG |90 %|N/A|2nové funkcie203B/87inštrukcií;1152 stack/timer replay|old interruptedPC, audio callees a Win ekvivalent|celý timer chain a nested IRQ|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|WORX private SS/SP a timer phase/depth/EOI vetvy|herný scheduler, tempo a celý timer chain|timer08 entry/exit trace a väzba na main loop|
| DEMO a vstupy |96 %|N/A|nové frame návraty0BDE:00C6; paused WORX SS kontext|presný old alternateIRQ PC a DEMO poradie|menu a širšie vstupné domény|
| Renderer / VGA |94 %|N/A|programmed4000→real4000 v neskoršom bode;4roviny a AC overené|host-surface/úplný scanout, text/menu|scanout a prirodzený vstup|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|DAC768 zložiek;71 použitých farieb,192000 RGB6 komponentov bez rozdielu|nepoužitý255 sa líši; Win OS a host frame|prirodzený text/font metrics a scanout|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|Win1104funkcie/229inštrukcií,23fixupcalls,22replay|skutočnéWin16DS/API/runtime|CreatePalette/WinG trace|

