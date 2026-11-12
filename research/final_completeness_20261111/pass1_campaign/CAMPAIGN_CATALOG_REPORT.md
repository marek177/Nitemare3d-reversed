# Nitemare 3D: aktualny dokazovy katalog

Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.

Najnovsi report: [aktualna analyticka davka](SCHEDULER_FIRST_RUNTIME_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Povodny Linux runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) zostava samostatnym auditom. Aktualne original-runtime testy: 23; presny rozsah: retained original packedDOS2 under DOSBox-X with debugger stops: startup/main, BSF/audio/VGA, resources/input, episodes, palettes/DAC, sound metadata/trace and fonts0/1/2; explicit CD intro/flip/read-map captures; AUTOTYPE IRQ/BDA/wait paths through main menu initial draw with414B descriptors and both VGA pages; foreground IRQ frames and explicit paused WORX SS/SP window, no captured private-stack keyIRQ; first XMS transfer and map-init return after episode1/difficulty1 selection, exact8192B MAP1 level0, sound474B negative-XMS-offset directory reconstruction, 57295B NONCODE endpoint snapshot; endpoint0D29:0A31 is pre-music-selection CALL, not game-loop entry; first post-map scheduler return, due buckets/world counter1to2/synchronized VGA flip, reconstructed world+HUD planes with actual DAC; no host/physical/independent-pixel/full-gameplay/save-load/Win16 parity; prefixes overlap.

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
| Original-EXE runtime scenare s definovanymi zasahmi | 23 |
| Runtime BSS tabulky mimo file image (nezvysuju PASS1) | 4054 B |
| Runtime buffer refinements, uz zahrnute v PASS1 | 4014 B /12 intervalov |
| Nove DEEP VERIFIED | 0 B |

Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.

## Artefakty a reprodukcia

`campaign_catalog/current_pass1_data_types.csv` ma 667 poli z 98 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.

Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_xms_move_request SCHEDULER_FIRST_RUNTIME_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit bedd07a3c629d3efbc9f40be519c416bb0db1b0c, pozri `CAMPAIGN_NEWGAME_PUBLICATION_RECEIPT_20261112.json`. Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou. Aktualny katalog alebo runtime scenare sa odvtedy zmenili; samotna zhoda mapy neznamena publikovanie novej davky. Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.

Samostatny Win110 paletovy doplnok: 4 rozsahy, 229 instrukcii / 641 B, 22 seeded pripadov. Nie je zahrnuty v DOS adresnej partition ani v DOS replay sucte; skutocny Win16 runtime 0.

## Aktualizácia 13 oblastí

Nová úplnosť je pre každú oblasť `uzavreté jednotky / úplný inventár oblasti`. Úplné menovatele stále chýbajú, preto nové sémantické percentáN/A. Historické orientačné percentá sú len staré odhady. Všetky nové dôkazy ostávajú PARTIAL, UNKNOWN28 a CLASSIFIED ONLY149B sa nemenia, DEEP VERIFIED0.

|Oblasť|Predošlý odhad|Nové % / metodika|Nové potvrdenie|Zostávajúce neznáme|Blokujúci problém|Najbližší krok|
|---|---:|---|---|---|---|---|
|Mapy a formáty|99 %|N/A,closure/inventár|8192B level0 ostáva presný po scheduler kroku|ostatné mapy a dynamické zmeny|iba jedna mapa|ďalšie levely a actor/world trace|
|Dátové typy a konštanty|95 %|N/A,closure/inventár|28B geometry a4paragraph gaps presne opätovne auditované|padding vs alias dátová rola|neúplný pointer/context dôkaz|dynamické segmenty a prístupy do medzier|
|Tabuľky a ukazovatele|93 %|N/A,closure/inventár|deadline3DWORD a buckets2DWORD natívne potvrdené bez doublecount|reset/alias writeri a cache life|iba jedna cesta|reset a ďalšie scheduler iterácie|
|Funkcie / ASM / CFG|90 %|N/A,closure/inventár|celý prvý03C8 entry→caller16EA,14stavov|iné vetvy a update callee CFG|vnútorné účinky neizolované|trace po jednotlivých update callees|
|RNG|97 %|N/A,closure/inventár|žiadny nový RNG dôkaz; clocks nie sú RNG|seed/rand/DEMO poradie|chýba RNG trace|srand/rand callery počas tickov|
|Scheduler|96 %|N/A,closure/inventár|due1/1,deadline2/2,R0save,elapsed18 syncflip,world1→2|fallback500,immediateflip,non-due,multi-tick|breakpoint timing a jedna cesta|dlhší trace a ďalšie vetvy|
|DEMO a vstupy|96 %|N/A,closure/inventár|post-update input callee sa vrátila|gameplay input a DEMO kontrakt|bez nového gameplay key|make/break počas ďalších tickov|
|Renderer / VGA|94 %|N/A,closure/inventár|native world/HUD VRAM a actual visibleA000,latched0|pixel golden,scanout,clipping domény|iba paused-derived frame|nezávislý golden a renderer callee trace|
|GUARD / bossovia|93 %|N/A,closure/inventár|viditeľný sprit,bez AI behavior closure|AI dispatch a boss vetvy|sprite image nie je algoritmus|actor update a stavové prechody|
|Zbrane / projektily|92 %|N/A,closure/inventár|žiadny nový damage dôkaz|damage a collision domény|bez projectile input|riadený výstrel/kolízia|
|Sprity / HUD / paleta|92 %|N/A,closure/inventár|HUD/sprit vo VRAM;DAC227/235≠RAM,oba nepoužité|writer/účel dvoch paletových zmien|chýba port-write trace|sledovať03C8/03C9 palette writes|
|SAVE / LOAD|92 %|N/A,closure/inventár|žiadny nový SAVE dôkaz|54709B payload a rollback|prefix nie celý formát|izolovaný SAVE a0277:1176|
|Windows Win16|92 %|N/A,closure/inventár|žiadny nový Win16 dôkaz|scheduler/render/palette API ekvivalenty|žiadny Win16 beh|fixup-backed porovnanie funkcií|

