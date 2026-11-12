# Nitemare 3D: aktualny dokazovy katalog

Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.

Najnovsi report: [aktualna analyticka davka](NEWGAME_MAP_XMS_CACHE_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Povodny Linux runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) zostava samostatnym auditom. Aktualne original-runtime testy: 22; presny rozsah: retained original packedDOS2 under DOSBox-X with debugger stops: startup/main, BSF/audio/VGA, resources/input, episodes, palettes/DAC, sound metadata/trace and fonts0/1/2; explicit CD intro/flip/read-map captures; AUTOTYPE IRQ/BDA/wait paths through main menu initial draw with414B descriptors and both VGA pages; foreground IRQ frames and explicit paused WORX SS/SP window, no captured private-stack keyIRQ; first XMS transfer and map-init return after episode1/difficulty1 selection, exact8192B MAP1 level0, sound474B negative-XMS-offset directory reconstruction, 57295B NONCODE endpoint snapshot; endpoint0D29:0A31 is pre-music-selection CALL, not game-loop entry; no first gameplay frame/host/physical/full-gameplay/save-load/Win16 parity; prefixes overlap.

## Aktualne meranie PASS1

Mapa `pass1_xms_move_request/noncode_intervals.csv/json`: **57118 B PARTIAL, 149 B CLASSIFIED ONLY, 28 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila 892 intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`.

| Centralny katalog | Pocet |
|---|---:|
| Funkcne rozsahy | 143 |
| Nezavisle dekodovane instrukcie | 5708 |
| Instrukcne bajty | 14344 |
| Unia typovanych dat celeho obrazu | 58034 B |
| Ostatne katalogom neposudene bajty | 98982 B |
| Intervaly celeho obrazu | 729 |
| Typovane data v povodnom NON-CODE | 57116 B |
| Kod v povodnom NON-CODE | 0 B |
| Seeded replay pripady | 994017 |
| Oddelene prefixove replay pripady | 65548 |
| Original-EXE runtime scenare s definovanymi zasahmi | 22 |
| Runtime BSS tabulky mimo file image (nezvysuju PASS1) | 4054 B |
| Runtime buffer refinements, uz zahrnute v PASS1 | 4014 B /12 intervalov |
| Nove DEEP VERIFIED | 0 B |

Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.

## Artefakty a reprodukcia

`campaign_catalog/current_pass1_data_types.csv` ma 667 poli z 98 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.

Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_xms_move_request NEWGAME_MAP_XMS_CACHE_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit 57386a3b2a144c855f06cc568339757a5f8ae33b, pozri `CAMPAIGN_XMS_PUBLICATION_RECEIPT_20261112.json`. Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou. Aktualny katalog alebo runtime scenare sa odvtedy zmenili; samotna zhoda mapy neznamena publikovanie novej davky. Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.

Samostatny Win110 paletovy doplnok: 4 rozsahy, 229 instrukcii / 641 B, 22 seeded pripadov. Nie je zahrnuty v DOS adresnej partition ani v DOS replay sucte; skutocny Win16 runtime 0.

## Aktualizácia 13 oblastí

Nové sémantické % = uzavreté jednotky / úplný inventár oblasti. Pre všetkých13 oblastí chýba úplný menovateľ, preto N/A; historické orientačné percentá sa nenahrádzajú vymysleným číslom. Nové výsledky sú PARTIAL. CLASSIFIED ONLY149B a UNKNOWN28B ostávajú; DEEP VERIFIED0B. Nasledujúci stav sa opiera o túto dávku, nie o domnelé vykonanie hernej slučky.

|Oblasť|Predošlý odhad|Nové % / metodika|Nové potvrdenie|Zostávajúce neznáme|Blokujúci problém|Konkrétny ďalší krok|
|---|---:|---|---|---|---|---|
|Mapy a formáty|99 %|N/A, closure/inventár|8192/8192B MAP1 level0 a map-init návrat|ostatné levely, init callee a gameplay význam|iba jedna prirodzená mapa|ďalšie levely a prvý gameplay frame|
|Dátové typy a konštanty|95 %|N/A, closure/inventár|79length WORD a68 zmenených offset DWORD, signed XMS token|zero token a index domény|consumer0684 neuzavretý|read cache consumer a0offset doména|
|Tabuľky a ukazovatele|93 %|N/A, closure/inventár|celá474B sound tabuľka rekonštruovaná;alias propagácia|4scratch cache sloty a životnosť|iba prvý cache fill|0768:0684 a invalidácia|
|Funkcie / ASM / CFG|90 %|N/A, closure/inventár|2telá490B/167inštrukcií,806replay|18stubovaných init callee, index guard|ABI závislosti nie sú closure|rozšíriť call graph z riadiaceho caller|
|RNG|97 %|N/A, closure/inventár|žiadny nový RNG dôkaz|prirodzené srand/rand a DEMO|prvý gameplay frame chýba|RNG trace po init návrate|
|Scheduler|96 %|N/A, closure/inventár|mode3CD4 0→1 pred music select;markerA31 opravený|skutočný loop a timer interaction|music selector nie je scheduler|sledovať0BDE:03C8 až po init|
|DEMO a vstupy|96 %|N/A, closure/inventár|prirodzený Newgame/episode1/difficulty1 až po init|DEMO a input v hre|iba menu vstupy|frame+input po scheduler vstupe|
|Renderer / VGA|94 %|N/A, closure/inventár|žiadny nový renderer parity výsledok|prvý frame a scanout|map loaded nie je frame|prvý world-draw a viditeľný flip|
|GUARD / bossovia|93 %|N/A, closure/inventár|žiadny nový AI dôkaz|actor init a boss vetvy|žiadny AI trace|actor dispatch pri gameplay|
|Zbrane / projektily|92 %|N/A, closure/inventár|žiadny nový damage dôkaz|kolízie a effect caller domény|žiadny damage trace|riadený input a projectile entry|
|Sprity / HUD / paleta|92 %|N/A, closure/inventár|žiadny nový closure dôkaz|HUD frame a text metrics|endpoint je pred hudbou|HUD/world frame capture|
|SAVE / LOAD|92 %|N/A, closure/inventár|žiadny nový SAVE dôkaz|payload54709B a rollback|metadata nie je celý formát|0277:1176 a izolovaný SAVE|
|Windows Win16|92 %|N/A, closure/inventár|žiadny nový Win dôkaz|Win cache/runtime ekvivalent|žiadny Win16 beh|fixup-backed cache porovnanie|

