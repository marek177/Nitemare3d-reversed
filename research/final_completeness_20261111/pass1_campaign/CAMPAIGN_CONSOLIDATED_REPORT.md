# Nitemare 3D: aktualny dokazovy katalog



Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.



Najnovsi report: [aktualna analyticka davka](CRT_FAR_MALLOC_NATIVE_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Povodny Linux runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) zostava samostatnym auditom. Aktualne original-runtime testy: 39; presny rozsah: retained original packedDOS2 under DOSBox-X with debugger stops: startup/main, BSF/audio/VGA, resources/input, episodes, palettes/DAC, sound metadata/trace and fonts0/1/2; explicit CD intro/flip/read-map captures; AUTOTYPE IRQ/BDA/wait paths through main menu initial draw with414B descriptors and both VGA pages; foreground IRQ frames and explicit paused WORX SS/SP window, no captured private-stack keyIRQ; first XMS transfer and map-init return after episode1/difficulty1 selection, exact8192B MAP1 level0, sound474B negative-XMS-offset directory reconstruction, 57295B NONCODE endpoint snapshot; endpoint0D29:0A31 is pre-music-selection CALL, not game-loop entry; first post-map scheduler return, due buckets/world counter1to2/synchronized VGA flip, reconstructed world+HUD planes with actual DAC; native reset caller0D29:16CA writes DAC235/scene227 black through original OUT opcodes, first palette tick decrements80to79; complete native palette black/white/black cycle and RNG1to2745024/AX41/countdown201, followupEA0 returned; exact98 before/after MOV mapBYTE1 stores bind GUARD24/actor168/A5 andGUARD25/actor174/A4, restore-underlay044C andoccupy06A9; map-writer endpoint06AD is mid-function; no host/physical/independent-pixel/full-gameplay/save-load/Win16 parity; prefixes overlap; original0254 allowed/blocked sparse decision-to-return tails, with blocked door7 state2 snapshot, no demonstrated entry-state transition; subsequent separate whole native0598 source door7 and neighbor6 state1to2 proved with exact2BYTE world delta/DGROUP57392B unchanged and original-code replay; earlier sparse capture alone remains weaker evidence; separate whole native classification producers mapheader514B identity,512output entries/seeds0and7; secondcall DGROUP includes observed clockDWORD+1, identified RTC INC but native writerPC not captured; pureproducer replay compared with explicit clockdelta allowance; separate whole original012A+C0A native mode7 GUARD0/actor20 orientation update, relative2/frame0400h, exact2BYTE world delta and unchangedDGROUP57392B/nearDSF200bank52B; original no-stub replay matches final registers; separate original0277:09C1..09D7 class8 copy block transfers90B IMG1 object81h header fromfile8F5Ah toDSF200h, objectoffsettable400h+4*81h gives159B32h; native classrecord4WORDs and prior52Bprefix bind source to orientation consumer; not whole map-loader/file IO execution trace; separate original045C wholecall raw8192B equals IMG1wall1[BC0Ah,DC0Ah) and XMS source,request offset0/used0to8/finaltag0/cachedwall+1/pointercleared; currentmanagerreturn not directly trapped,prior same-request AX1 verified; no XMSreadback/render parity; separate original0402 wholecall/0350 XMS readback for wall16 tagFFFCC000,manager AX1,8192 destination bytes equal IMG1[3CD04h,3ED04h),ten slot headers/record/stats/frame checked; native zero-tag,eviction,fullDGROUP and renderer open; separate original11EE2DC0 whole native calendar call2026-11-12/month11,timezone+28800,DST0,DXAX6AF65F2F,common-table249C; original no-stub replay172instructions/all captured registers/frame/fullDGROUP57392B unchanged; no native DST transition/leap-table consumer/Win16 parity; separate whole original0BDE0018 CRTclock sample/ftime with coldTZcache0to1,originalgetenv absentTZ,actualDOSdate/time,10Btimeb+4preservedtail,seconds6AF66351/ms120/zone480/DST0/clockD273F4E0;643instruction original replay has only2OSresponse fixtures and noCRTstubs; native/replay allcapturedregisters/frame/DGROUP57392B match with exact1BYTE cache delta;restricted177B read/write hooks calibrated3TZreads/10outputB and zeroevents for this replay path only; separate native04D8 cyclicobjectcache62of128pointers/index0to1/600Bsource/1024BXMSreadbackAX1 then original015605DE draws30x20 source at82..96/86..95;67CPUstores/4plane changed20,15,16,16 andall262144VGAbytes match originalreplay plus independentunclipped/depth/transparency math;captured write-mode0/maskFF/no-setreset;not fullframe/fullclipping/lifecycle/Win16 parity;helperreturnsDX0,storedrecordFAR4F97E050 isactualsource; natural wholemode0 cacheinit76realallocations,probe257/count62,query14912/cap2048/handle1/lockphysical00170000,85calleeentry-returnrecords;531cacheownedfinalbytes matchmodel,notfullRAMcalleeclosure/managerfailureparity; natural firstsuccessful CRTprobe257KiB allocation/zero suffix/DOSfreeCF0,bufferalreadyzero; originalnofixturesuffix131675events/allcapturedregsCFDF match,263168bufferB/32guards/57388DGROUPB match withclock4Bexcluded,35residualIRQaudio/stackpositionsnotclosed; wholeoriginalCRT2065 firstcache8198B call,growsheap3232to16384 through actualDOS4AES3F96/BX400/CF0,returns3F96:0C9C.271originalreplayevents/12stores/18targetB/allcapturedregsCFDF match;1capturedDOSresponsefixture,42residualDOSIRQstackpositionsnotclosed. v1lacked4Atrace,uncounted..



## Aktualne meranie PASS1



Mapa `pass1_xms_move_request/noncode_intervals.csv/json`: **57118 B PARTIAL, 149 B CLASSIFIED ONLY, 28 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila 892 intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`.



| Centralny katalog | Pocet |

|---|---:|

| Funkcne rozsahy | 183 |

| Nezavisle dekodovane instrukcie | 8123 |

| Instrukcne bajty | 20561 |

| Unia typovanych dat celeho obrazu | 59469 B |

| Ostatne katalogom neposudene bajty | 91330 B |

| Intervaly celeho obrazu | 875 |

| Typovane data v povodnom NON-CODE | 57116 B |

| Kod v povodnom NON-CODE | 0 B |

| Seeded replay pripady | 1064251 |

| Oddelene prefixove replay pripady | 65548 |

| Original-EXE runtime scenare s definovanymi zasahmi | 39 |

| Runtime BSS tabulky mimo file image (nezvysuju PASS1) | 5164 B |

| Runtime buffer refinements, uz zahrnute v PASS1 | 4636 B /18 intervalov |

| Nove DEEP VERIFIED | 0 B |



Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.



## Artefakty a reprodukcia



`campaign_catalog/current_pass1_data_types.csv` ma 667 poli z 98 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.



Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_xms_move_request CRT_FAR_MALLOC_NATIVE_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit 8f7e83f898226647a6977cc39d73666aed68eebd, pozri `CAMPAIGN_CRTLARGE_PUBLICATION_RECEIPT_20261112.json`. Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou. Aktualny katalog alebo runtime scenare sa odvtedy zmenili; samotna zhoda mapy neznamena publikovanie novej davky. Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.



Samostatny Win110 paletovy doplnok: 4 rozsahy, 229 instrukcii / 641 B, 22 seeded pripadov. Nie je zahrnuty v DOS adresnej partition ani v DOS replay sucte; skutocny Win16 runtime 0.

## Coverage update: 13 areas

Previous catalog183functions/8123starts/20561codeB/1063379controlled cases/38native. New function/code counts unchanged; controlled cases1064251=1063379+872,accepted native39=38+v2capture. The v1capture and native original-code replay are not additional central cases. Typed file data59469B,BSS5164B,central field-role rows108 unchanged; this batch's four field rows are scoped refinements, not extra unique-data coverage. Campaign UNKNOWN_CONTENT91330is not historical reclassification.

PASS320 remains892intervals/57295B =PARTIAL57118+CLASSIFIED ONLY149+UNKNOWN28+DEEP VERIFIED0. Map SHA256 `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`. New semantic percentages N/A because full per-area denominators are absent. Historical orientation percentages remain estimates.

|Area|Historical orientation|New % / exact method|New confirmed evidence|Remaining / blocker|Next concrete step|
|---|---:|---|---|---|---|
|Maps and formats|99%|N/A,semantic denominator absent|No new map semantics|Level replacement open|Natural populated cleanup/map replacement|
|Data types and constants|95%|N/A;12already-PARTIAL bytes refined|Shared marker start/end writer distinction;header/tag roles|177B still unresolved/only classified|New concrete data consumers|
|Tables and pointers|93%|N/A;35813starts finite census|Two distinct callback fields/ABIs;rotated heap list|Indirect/bulk writers and callbacks open|Address derivations/setter candidates|
|Functions/ASM/CFG|90%|N/A;872whole calls;64/71caller starts|Original malloc/scan/grow/resize integration|Nonnull callback body,PSP/corrupt/global heap domains open|Whole PSP growth and callback provenance|
|RNG|97%|N/A,semantic denominator absent|No RNG behavior inferred|DEMO/order domains open|Original RNG/DEMO transitions|
|Scheduler|96%|N/A;42native residual positions exported|Actual DOS4A boundary separated from IRQ effects|Paused timing/unassigned residuals open|Trace relevant IRQ/DOS memory effects|
|DEMO/input|96%|N/A,semantic denominator absent|No new input semantics|Playback/input order open|Natural DEMO execution|
|Renderer/VGA|94%|N/A;actual8198B wall allocation|Backing storage allocation before wall-header writes|No new pixel/clipping parity|Post-reset refill and clipped draws|
|GUARD/bosses|93%|N/A,semantic denominator absent|No new AI behavior|Boss/state branches open|Uncovered original state/attack paths|
|Weapons/projectiles|92%|N/A,semantic denominator absent|No new damage behavior|Projectile lifecycle open|Original impact/damage transitions|
|Sprites/HUD/palette|92%|N/A,semantic denominator absent|Heap metadata kept distinct from image headers/pixels|Other asset/lifetime paths open|Resource reset/refill/draw ordering|
|SAVE/LOAD|92%|N/A,semantic denominator absent|Natural initialization grows existing heap|Actual reload/cleanup ordering open|LOAD/populated reset capture|
|Windows Win16|92%|N/A,semantic denominator absent|No new Win16 parity proof|Heap/backend counterparts open|Map Win16 allocation/lifetime equivalents|

All13areas remain PARTIAL. No new cross-version behavioral equivalence is asserted. Full instruction-reference scans are finite inventories, not global absence proofs.

