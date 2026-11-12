# Nitemare 3D: aktualny dokazovy katalog



Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.



Najnovsi report: [aktualna analyticka davka](IMAGE_CACHE_RETRIEVAL_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Povodny Linux runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) zostava samostatnym auditom. Aktualne original-runtime testy: 33; presny rozsah: retained original packedDOS2 under DOSBox-X with debugger stops: startup/main, BSF/audio/VGA, resources/input, episodes, palettes/DAC, sound metadata/trace and fonts0/1/2; explicit CD intro/flip/read-map captures; AUTOTYPE IRQ/BDA/wait paths through main menu initial draw with414B descriptors and both VGA pages; foreground IRQ frames and explicit paused WORX SS/SP window, no captured private-stack keyIRQ; first XMS transfer and map-init return after episode1/difficulty1 selection, exact8192B MAP1 level0, sound474B negative-XMS-offset directory reconstruction, 57295B NONCODE endpoint snapshot; endpoint0D29:0A31 is pre-music-selection CALL, not game-loop entry; first post-map scheduler return, due buckets/world counter1to2/synchronized VGA flip, reconstructed world+HUD planes with actual DAC; native reset caller0D29:16CA writes DAC235/scene227 black through original OUT opcodes, first palette tick decrements80to79; complete native palette black/white/black cycle and RNG1to2745024/AX41/countdown201, followupEA0 returned; exact98 before/after MOV mapBYTE1 stores bind GUARD24/actor168/A5 andGUARD25/actor174/A4, restore-underlay044C andoccupy06A9; map-writer endpoint06AD is mid-function; no host/physical/independent-pixel/full-gameplay/save-load/Win16 parity; prefixes overlap; original0254 allowed/blocked sparse decision-to-return tails, with blocked door7 state2 snapshot, no demonstrated entry-state transition; subsequent separate whole native0598 source door7 and neighbor6 state1to2 proved with exact2BYTE world delta/DGROUP57392B unchanged and original-code replay; earlier sparse capture alone remains weaker evidence; separate whole native classification producers mapheader514B identity,512output entries/seeds0and7; secondcall DGROUP includes observed clockDWORD+1, identified RTC INC but native writerPC not captured; pureproducer replay compared with explicit clockdelta allowance; separate whole original012A+C0A native mode7 GUARD0/actor20 orientation update, relative2/frame0400h, exact2BYTE world delta and unchangedDGROUP57392B/nearDSF200bank52B; original no-stub replay matches final registers; separate original0277:09C1..09D7 class8 copy block transfers90B IMG1 object81h header fromfile8F5Ah toDSF200h, objectoffsettable400h+4*81h gives159B32h; native classrecord4WORDs and prior52Bprefix bind source to orientation consumer; not whole map-loader/file IO execution trace; separate original045C wholecall raw8192B equals IMG1wall1[BC0Ah,DC0Ah) and XMS source,request offset0/used0to8/finaltag0/cachedwall+1/pointercleared; currentmanagerreturn not directly trapped,prior same-request AX1 verified; no XMSreadback/render parity; separate original0402 wholecall/0350 XMS readback for wall16 tagFFFCC000,manager AX1,8192 destination bytes equal IMG1[3CD04h,3ED04h),ten slot headers/record/stats/frame checked; native zero-tag,eviction,fullDGROUP and renderer open.



## Aktualne meranie PASS1



Mapa `pass1_xms_move_request/noncode_intervals.csv/json`: **57118 B PARTIAL, 149 B CLASSIFIED ONLY, 28 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila 892 intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`.



| Centralny katalog | Pocet |

|---|---:|

| Funkcne rozsahy | 166 |

| Nezavisle dekodovane instrukcie | 7302 |

| Instrukcne bajty | 18459 |

| Unia typovanych dat celeho obrazu | 59469 B |

| Ostatne katalogom neposudene bajty | 93432 B |

| Intervaly celeho obrazu | 832 |

| Typovane data v povodnom NON-CODE | 57116 B |

| Kod v povodnom NON-CODE | 0 B |

| Seeded replay pripady | 1045051 |

| Oddelene prefixove replay pripady | 65548 |

| Original-EXE runtime scenare s definovanymi zasahmi | 33 |

| Runtime BSS tabulky mimo file image (nezvysuju PASS1) | 5148 B |

| Runtime buffer refinements, uz zahrnute v PASS1 | 4122 B /16 intervalov |

| Nove DEEP VERIFIED | 0 B |



Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.



## Artefakty a reprodukcia



`campaign_catalog/current_pass1_data_types.csv` ma 667 poli z 98 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.



Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_xms_move_request IMAGE_CACHE_RETRIEVAL_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit 9897d0a8983720a55024b871eb4b0542f0754295, pozri `CAMPAIGN_IMAGE_RECORD_PUBLICATION_RECEIPT_20261112.json`. Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou. Aktualny katalog alebo runtime scenare sa odvtedy zmenili; samotna zhoda mapy neznamena publikovanie novej davky. Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.



Samostatny Win110 paletovy doplnok: 4 rozsahy, 229 instrukcii / 641 B, 22 seeded pripadov. Nie je zahrnuty v DOS adresnej partition ani v DOS replay sucte; skutocny Win16 runtime 0.

## Coverage update: 13 areas

Central catalog:166 bounded functions,7302 independent starts,18459 unique instruction bytes,59469 typed file-data bytes,UNKNOWN_CONTENT93432. Controlled DOS2 scenarios1045051 after adding240; accepted native scenarios33 with overlapping prefixes. BSS5148B,field-role rows69. Original PASS320 partition unchanged:892 intervals,57295B=PARTIAL57118+CLASSIFIED ONLY149+UNKNOWN28;DEEP0. Map SHA256 `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`. No new semantic percentage has a valid denominator; new percentages are **N/A**.

|Area|Historical orientation|New % / method|New confirmed evidence|Remaining / blocker|Next concrete step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A,semantic denominator absent|None this batch|Prior map unknowns remain|Return to uncovered map fields|
|Data types and constants|95%|N/A;52 separate BSS bytes|Slot-vector/counters/order value observed|Allocation producer not fully closed|Decode0024 init/free modes|
|Tables and pointers|93%|N/A;10 pointers observed|Record resident-cache pointer lifecycle|Native eviction absent|Capture eviction/old record|
|Functions/ASM/CFG|90%|N/A;122 new starts/338B|Two bounded original routines,all starts exercised|Diagnostic handler behavior and callers open|Close allocation/caller dependency|
|RNG|97%|N/A,semantic denominator absent|None this batch|Prior RNG closure gaps|Retain independent RNG/runtime tasks|
|Scheduler|96%|N/A,semantic denominator absent|Unsigned DS4540 consumption|Producer/time-wrap semantics open|Bind DS4540 writer|
|DEMO/input|96%|N/A,semantic denominator absent|None this batch|DEMO paths not covered by startup prefix|Trace record/playback unknowns|
|Renderer/VGA|94%|N/A;8192B native buffer comparison|IMG1 wall16 == XMS destination|Buffer-to-renderer/screen relation open|Trace original pixel consumer|
|GUARD/bosses|93%|N/A,semantic denominator absent|None this batch|Prior AI/boss unknowns|Prioritize uncovered branches|
|Weapons/projectiles|92%|N/A,semantic denominator absent|None this batch|Prior damage/projectile unknowns|Close uncovered dispatch branches|
|Sprites/HUD/palette|92%|N/A,semantic denominator absent|Cache assignment/invalidation roles|Small-image consumer may differ|Identify0402 and04D8 callers|
|SAVE/LOAD|92%|N/A,semantic denominator absent|None this batch|No complete native round trip|Analyze unresolved serialization fields|
|Windows Win16|92%|N/A,semantic denominator absent|None;DOS CFG comparisons separate|Win16 XMS/graphics differs|Map actual Win16 consumer|

All13 areas remain PARTIAL. CLASSIFIED ONLY and UNKNOWN in the original map remain explicit,not silently promoted. Campaign remains active. Next priority also includes original NONCODE149 classified-only/28 unknown bytes; this code batch adds no PASS1 byte coverage.

