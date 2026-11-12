# Nitemare 3D: aktualny dokazovy katalog



Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.



Najnovsi report: [aktualna analyticka davka](PALETTE_EFFECT_NATIVE_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Povodny Linux runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) zostava samostatnym auditom. Aktualne original-runtime testy: 25; presny rozsah: retained original packedDOS2 under DOSBox-X with debugger stops: startup/main, BSF/audio/VGA, resources/input, episodes, palettes/DAC, sound metadata/trace and fonts0/1/2; explicit CD intro/flip/read-map captures; AUTOTYPE IRQ/BDA/wait paths through main menu initial draw with414B descriptors and both VGA pages; foreground IRQ frames and explicit paused WORX SS/SP window, no captured private-stack keyIRQ; first XMS transfer and map-init return after episode1/difficulty1 selection, exact8192B MAP1 level0, sound474B negative-XMS-offset directory reconstruction, 57295B NONCODE endpoint snapshot; endpoint0D29:0A31 is pre-music-selection CALL, not game-loop entry; first post-map scheduler return, due buckets/world counter1to2/synchronized VGA flip, reconstructed world+HUD planes with actual DAC; native reset caller0D29:16CA writes DAC235/scene227 black through original OUT opcodes, first palette tick decrements80to79; complete native palette black/white/black cycle and RNG1to2745024/AX41/countdown201, followupEA0 returned; no host/physical/independent-pixel/full-gameplay/save-load/Win16 parity; prefixes overlap.



## Aktualne meranie PASS1



Mapa `pass1_xms_move_request/noncode_intervals.csv/json`: **57118 B PARTIAL, 149 B CLASSIFIED ONLY, 28 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila 892 intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`.



| Centralny katalog | Pocet |

|---|---:|

| Funkcne rozsahy | 145 |

| Nezavisle dekodovane instrukcie | 5785 |

| Instrukcne bajty | 14577 |

| Unia typovanych dat celeho obrazu | 58034 B |

| Ostatne katalogom neposudene bajty | 98749 B |

| Intervaly celeho obrazu | 735 |

| Typovane data v povodnom NON-CODE | 57116 B |

| Kod v povodnom NON-CODE | 0 B |

| Seeded replay pripady | 996305 |

| Oddelene prefixove replay pripady | 65548 |

| Original-EXE runtime scenare s definovanymi zasahmi | 25 |

| Runtime BSS tabulky mimo file image (nezvysuju PASS1) | 4054 B |

| Runtime buffer refinements, uz zahrnute v PASS1 | 4014 B /12 intervalov |

| Nove DEEP VERIFIED | 0 B |



Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.



## Artefakty a reprodukcia



`campaign_catalog/current_pass1_data_types.csv` ma 667 poli z 98 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.



Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_xms_move_request PALETTE_EFFECT_NATIVE_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit 4e3731f2bbe25e4a0c2e93f04bdd314e3adf939f, pozri `CAMPAIGN_SCHEDULER_PUBLICATION_RECEIPT_20261112.json`. Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou. Aktualny katalog alebo runtime scenare sa odvtedy zmenili; samotna zhoda mapy neznamena publikovanie novej davky. Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.



Samostatny Win110 paletovy doplnok: 4 rozsahy, 229 instrukcii / 641 B, 22 seeded pripadov. Nie je zahrnuty v DOS adresnej partition ani v DOS replay sucte; skutocny Win16 runtime 0.

## Aktualizácia 13 oblastí

Pre každú oblasť nové sémantické percento = uzavreté jednotky/úplný inventár. Menovatele stále chýbajú, preto N/A; staré orientačné odhady sa neprezentujú ako meranie. Nové funkcie/runtime dôkazy sú PARTIAL. UNKNOWN28B a CLASSIFIED ONLY149B ostávajú, DEEP VERIFIED0B.

|Oblasť|Predošlý odhad|Nové % / metodika|Nový dôkaz|Zostávajúce neznáme|Blokujúci problém|Najbližší krok|
|---|---:|---|---|---|---|---|
|Mapy a formáty|99 %|N/A,closure/inventár|4konkrétne BYTE1 endpoint zmeny po dlhšom behu|writer,A4/A5,world axes|iba endpointy|presný writer breakpoint pre4adresy|
|Dátové typy a konštanty|95 %|N/A,closure/inventár|countdownWORD/phaseBYTE/sceneDACBYTE,4B BSS refinement|všetci alias writeri,lifecycle|nie celý BSS inventár|state a scene-index callery|
|Tabuľky a ukazovatele|93 %|N/A,closure/inventár|DAC235+scene227, RAM/DAC divergence vysvetlená|iné scene-index hodnoty a alias227=235|iba jeden native sceneindex|ďalšie map header domény|
|Funkcie / ASM / CFG|90 %|N/A,closure/inventár|2telá233B/77instructions,2288replay|EA0 downstream a neuzavreté callees|runtime path nie celá hra|audio/cache a map-writer telá|
|RNG|97 %|N/A,closure/inventár|prirodzený palette seed1→2745024/AX41;12native-CRT modelchains|globálne poradie,seedy,DEMO,SAVE|iba palette RNG event|RNG call trace počas world/DEMO|
|Scheduler|96 %|N/A,closure/inventár|palette reset a tick80→79, prirodzený flash cyklus|presné intervaly,skip/catchup a iné vetvy|nepočítaný každýtick/debug timing|riedky multi-tick trace|
|DEMO a vstupy|96 %|N/A,closure/inventár|dlhší bez-input gameplay do palette cycle end|DEMO a pohyb/výstrel|iba startup menu keys|riadené gameplay vstupy a DEMO|
|Renderer / VGA|94 %|N/A,closure/inventár|24nativeOUT aDACblack/white/black,index-helper8DOS rawmatch|pixelgolden,clipping a scanout|headless paused readback|nezávislý renderer golden a clippingcases|
|GUARD / bossovia|93 %|N/A,closure/inventár|mapBYTE1 tokeny sa zmenili,writer nepriradený|AIobjekty/boss stavy|endpoint nie actor trace|breakpointy A4/A5 map writerov|
|Zbrane / projektily|92 %|N/A,closure/inventár|žiadny nový damage dôkaz|damage/collision domény|bez výstrelu|controlled firing a projectile trace|
|Sprity / HUD / paleta|92 %|N/A,closure/inventár|DAC227/235writer uzavretý pretestedcestu;gates/counter/RNGcycle|ďalšie epizódy,inépalety/callee role|jedna natívna mapa|gatedep2/ep3/sceneindex runtime|
|SAVE / LOAD|92 %|N/A,closure/inventár|žiadny nový SAVE dôkaz|payload54709B,rollback,RNGserialization|prefix nie celý formát|SAVE/LOAD schema a izolovaný runtime|
|Windows Win16|92 %|N/A,closure/inventár|DOS8label helper/CFG compare,žiadny novýWin dôkaz|Win paletteAPI/flash ekvivalent|žiadnyWin16runtime|fixup-backed Win effect mapping|

