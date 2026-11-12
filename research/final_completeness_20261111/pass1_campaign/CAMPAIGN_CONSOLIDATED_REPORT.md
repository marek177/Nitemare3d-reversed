# Nitemare 3D: aktualny dokazovy katalog



Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.



Najnovsi report: [aktualna analyticka davka](GUARD_MAP_WRITER_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Povodny Linux runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) zostava samostatnym auditom. Aktualne original-runtime testy: 26; presny rozsah: retained original packedDOS2 under DOSBox-X with debugger stops: startup/main, BSF/audio/VGA, resources/input, episodes, palettes/DAC, sound metadata/trace and fonts0/1/2; explicit CD intro/flip/read-map captures; AUTOTYPE IRQ/BDA/wait paths through main menu initial draw with414B descriptors and both VGA pages; foreground IRQ frames and explicit paused WORX SS/SP window, no captured private-stack keyIRQ; first XMS transfer and map-init return after episode1/difficulty1 selection, exact8192B MAP1 level0, sound474B negative-XMS-offset directory reconstruction, 57295B NONCODE endpoint snapshot; endpoint0D29:0A31 is pre-music-selection CALL, not game-loop entry; first post-map scheduler return, due buckets/world counter1to2/synchronized VGA flip, reconstructed world+HUD planes with actual DAC; native reset caller0D29:16CA writes DAC235/scene227 black through original OUT opcodes, first palette tick decrements80to79; complete native palette black/white/black cycle and RNG1to2745024/AX41/countdown201, followupEA0 returned; exact98 before/after MOV mapBYTE1 stores bind GUARD24/actor168/A5 andGUARD25/actor174/A4, restore-underlay044C andoccupy06A9; map-writer endpoint06AD is mid-function; no host/physical/independent-pixel/full-gameplay/save-load/Win16 parity; prefixes overlap.



## Aktualne meranie PASS1



Mapa `pass1_xms_move_request/noncode_intervals.csv/json`: **57118 B PARTIAL, 149 B CLASSIFIED ONLY, 28 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila 892 intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`.



| Centralny katalog | Pocet |

|---|---:|

| Funkcne rozsahy | 146 |

| Nezavisle dekodovane instrukcie | 6034 |

| Instrukcne bajty | 15260 |

| Unia typovanych dat celeho obrazu | 58034 B |

| Ostatne katalogom neposudene bajty | 98066 B |

| Intervaly celeho obrazu | 745 |

| Typovane data v povodnom NON-CODE | 57116 B |

| Kod v povodnom NON-CODE | 0 B |

| Seeded replay pripady | 1003217 |

| Oddelene prefixove replay pripady | 65548 |

| Original-EXE runtime scenare s definovanymi zasahmi | 26 |

| Runtime BSS tabulky mimo file image (nezvysuju PASS1) | 4054 B |

| Runtime buffer refinements, uz zahrnute v PASS1 | 4122 B /16 intervalov |

| Nove DEEP VERIFIED | 0 B |



Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.



## Artefakty a reprodukcia



`campaign_catalog/current_pass1_data_types.csv` ma 667 poli z 98 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.



Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_xms_move_request GUARD_MAP_WRITER_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit 8dc64e98da7d78c427e21c3c49d3b8e4f7509117, pozri `CAMPAIGN_PALETTE_EFFECT_PUBLICATION_RECEIPT_20261112.json`. Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou. Aktualny katalog alebo runtime scenare sa odvtedy zmenili; samotna zhoda mapy neznamena publikovanie novej davky. Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.



Samostatny Win110 paletovy doplnok: 4 rozsahy, 229 instrukcii / 641 B, 22 seeded pripadov. Nie je zahrnuty v DOS adresnej partition ani v DOS replay sucte; skutocny Win16 runtime 0.

## Aktualizácia 13 oblastí

Nové sémantické percento = uzavreté jednotky/úplný inventár oblasti. Úplné menovatele stále chýbajú, preto N/A. Historické orientačné odhady sa nenahrádzajú odhadnutým číslom. Nové výsledky sú PARTIAL; UNKNOWN28B, CLASSIFIED ONLY149B a DEEP VERIFIED0 sa nemenia.

|Oblasť|Predošlý odhad|Nové % / metodika|Nový potvrdený dôkaz|Zostávajúce neznáme|Blokujúci problém|Najbližší krok|
|---|---:|---|---|---|---|---|
|Mapy a formáty|99 %|N/A,closure/inventár|všetky4targety majú presné BYTE1 writery;98zápisov|iné mapové cesty a alias writery|selected direct store formy nie exhaustive|šíriť trace cez ďalšie object/map operácie|
|Dátové typy a konštanty|95 %|N/A,closure/inventár|12caller-specific rolí,108B native rawrecord refinement|iné polia100/350records|iba2native GUARD sloty|zostávajúce record fields a consumers|
|Tabuľky a ukazovatele|93 %|N/A,closure/inventár|GUARD24→actor168 a25→174;FARcell pointer zcoord0/1|iné linky,lifecycle a invalidácia|2páry nie celá tabuľka|GUARD allocation/destruction/link callery|
|Funkcie / ASM / CFG|90 %|N/A,closure/inventár|0422whole controlbody683B/249instructions/6912replay|7mockcallee a4CFG gapB|callee effects neuzavreté|04C7:0254 a nadradená0D80|
|RNG|97 %|N/A,closure/inventár|mode6bothblocked parity branch staticky/replay|prirodzený mode6 RNG a global order|native bolmode8|native mode6 situácia a randtrace|
|Scheduler|96 %|N/A,closure/inventár|worldupdate vedie doGUARD callerFBA a98stores|cadence,inéstrategy/timer interactions|hustédebugstops|riedky multi-tick/strategy trace|
|DEMO a vstupy|96 %|N/A,closure/inventár|bez nového gameplay key input prebeholGUARDmove|DEMO a riadený pohyb/výstrel|iba no-input scéna|gameplay input a DEMOtrace|
|Renderer / VGA|94 %|N/A,closure/inventár|žiadny nový pixel parity dôkaz|renderer golden/clipping/scanout|storetrace nie pixel golden|object movement verzus spritedraw|
|GUARD / bossovia|93 %|N/A,closure/inventár|underlay restore/rebind,mode8 gate,mode6bounce model|0254collision,0D80AI,boss stratégia|2native mode8sloty a7stuby|0254validator a0D80strategy CFG|
|Zbrane / projektily|92 %|N/A,closure/inventár|žiadny nový damage dôkaz|projectile/collision/effects|bezvýstrelu|controlled projectile trace|
|Sprity / HUD / paleta|92 %|N/A,closure/inventár|actor phaseBYTEanimation base/span kontrakt|spriteID/phase timing a draw caller|framecounter nie celýrender|animation consumer a sprite selection|
|SAVE / LOAD|92 %|N/A,closure/inventár|4mapBYTE1writes označené dynamickéstate|serializácia actor/map underlay a rollback|metadata prefix nie celéSAVE|payload fields preactor/guard/map|
|Windows Win16|92 %|N/A,closure/inventár|8DOS normalized wholecallerCFG,žiadnyWin dôkaz|Winactor/collision equivalent|žiadnyWin16runtime|fixup-backed actor move mapping|

