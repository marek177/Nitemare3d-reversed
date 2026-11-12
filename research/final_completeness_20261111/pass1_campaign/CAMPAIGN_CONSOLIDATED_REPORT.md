# Nitemare 3D: aktualny dokazovy katalog

Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.

Najnovsi report: [aktualna analyticka davka](VGA_BLOCK_BLIT_RUNTIME_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Povodny Linux runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) zostava samostatnym auditom. Aktualne original-runtime testy: 14; presny rozsah: retained original packed DOS2 EXE scenarios under DOSBox-X built-in DOS with debugger stops: startup/B3, main/defaults35C, BSF/audio/VGA, post-VGA slot/resource, keyboard/auxiliary, episode/asset names, palette/DAC readback, sound directory/CPU trace, UIF font2, optional intro missing-file return and explicit added CD asset back-buffer four-plane readback with paused read-map intervention/restoration; only independently retained proofs counted; no gameplay/audio-output/visible-frame/Win16 runtime parity; repeated prefixes overlap.

## Aktualne meranie PASS1

Mapa `pass1_near_heap_flags/noncode_intervals.csv/json`: **57102 B PARTIAL, 149 B CLASSIFIED ONLY, 44 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila 888 intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `3021969d4e4348715816361fa387631e7d6cfd9fc9dcc136e26073f0f9984d1b`.

| Centralny katalog | Pocet |
|---|---:|
| Funkcne rozsahy | 130 |
| Nezavisle dekodovane instrukcie | 4993 |
| Instrukcne bajty | 12456 |
| Unia typovanych dat celeho obrazu | 57988 B |
| Ostatne katalogom neposudene bajty | 100916 B |
| Intervaly celeho obrazu | 682 |
| Typovane data v povodnom NON-CODE | 57100 B |
| Kod v povodnom NON-CODE | 0 B |
| Seeded replay pripady | 974287 |
| Oddelene prefixove replay pripady | 65548 |
| Prirodzene runtime testy | 14 |
| Runtime BSS tabulky mimo file image (nezvysuju PASS1) | 3030 B |
| Nove DEEP VERIFIED | 0 B |

Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.

## Artefakty a reprodukcia

`campaign_catalog/current_pass1_data_types.csv` ma 662 poli z 97 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.

Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_near_heap_flags VGA_BLOCK_BLIT_RUNTIME_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit 338a23e550909f2fb57acd21439bb4407fcdbb69, pozri `CAMPAIGN_VGA_PUBLICATION_RECEIPT_20261112.json`. Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou. Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.

Samostatny Win110 paletovy doplnok: 4 rozsahy, 229 instrukcii / 641 B, 22 seeded pripadov. Nie je zahrnuty v DOS adresnej partition ani v DOS replay sucte; skutocny Win16 runtime 0.

## Aktualizácia 13 oblastí

Nové % = uzavreté jednotky / úplný inventár oblasti. Úplné menovatele chýbajú, preto N/A. Iniciačný runtime nie je percento gameplay completeness.

| Oblasť | Predošlý odhad | Nové % | Aktuálny dôkaz (staršie riadky zachované) | Zostávajúce neznáme / blokátor | Najbližší konkrétny krok |
|---|---:|---|---|---|---|
| Mapy a formáty |99 %|N/A|CD DSTOPEN.IMG:128B header,19781B RLE,769B tail; 64000 pixelov|iné PCX/IMG domény; stride/planes ignorované|prirodzená paleta a page flip|
| Dátové typy a konštanty |95 %|N/A|ABI10WORD polí; source stride, signed key a y lowBYTE; staršie asset intervaly zachované|neuzavreté caller domény a globálne invarianty|callery a rozsahy zdrojových dát|
| Tabuľky a ukazovatele |93 %|N/A|128 runtime FAR pointerov font2 presne zhodných s parserom|iné skupiny a signed char indexy|úplný textový caller kontrakt|
| Funkcie / ASM / CFG |90 %|N/A|blitter174B/78 inštrukcií;2884 úplných replay;6 prefixov;8DOS CFG zhôd|callery07DE, nulové domény a Win ekvivalent|caller a page producer audit|
| RNG |97 %|N/A|bez RNG runtime|prvý srand/rand|RNG caller trace|
| Scheduler |96 %|N/A|clock init prebehol medzi bodmi|main loop/scheduler|loop vstup|
| DEMO a vstupy |96 %|N/A|prirodzený INT9 install a aux probeFFFFh|key IRQ/DEMO poradie/close|prvý vstupný tick|
| Renderer / VGA |94 %|N/A|prirodzený DOSBox back-buffer64000 pixelov vo4 rovinách byte-exact|viditeľný flip, RGB paleta a text/menu|display-start po prirodzenom flipe|
| GUARD / bossovia |93 %|N/A|bez AI runtime|map init|selector doména|
| Zbrane / projektily |92 %|N/A|bez damage runtime|effect callery|damage trace|
| Sprity / HUD / paleta |92 %|N/A|nový CD back-buffer; starší DOS DAC readback zachovaný|CD palette vs GAME.PAL; Win OS a celý frame|Win capture a paired frame|
| SAVE / LOAD |92 %|N/A|BSF native file-check vrátený|SAVE/LOAD a chybové I/O|diskové scenáre|
| Windows Win16 |92 %|N/A|Win1104funkcie/229inštrukcií,23fixupcalls,22replay|skutočnéWin16DS/API/runtime|CreatePalette/WinG trace|

