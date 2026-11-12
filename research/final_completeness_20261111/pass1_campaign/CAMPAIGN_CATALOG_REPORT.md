# Nitemare 3D: aktualny dokazovy katalog



Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.



Najnovsi report: [aktualna analyticka davka](IMAGE_GROUP_DESCRIPTOR_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Povodny Linux runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) zostava samostatnym auditom. Aktualne original-runtime testy: 31; presny rozsah: retained original packedDOS2 under DOSBox-X with debugger stops: startup/main, BSF/audio/VGA, resources/input, episodes, palettes/DAC, sound metadata/trace and fonts0/1/2; explicit CD intro/flip/read-map captures; AUTOTYPE IRQ/BDA/wait paths through main menu initial draw with414B descriptors and both VGA pages; foreground IRQ frames and explicit paused WORX SS/SP window, no captured private-stack keyIRQ; first XMS transfer and map-init return after episode1/difficulty1 selection, exact8192B MAP1 level0, sound474B negative-XMS-offset directory reconstruction, 57295B NONCODE endpoint snapshot; endpoint0D29:0A31 is pre-music-selection CALL, not game-loop entry; first post-map scheduler return, due buckets/world counter1to2/synchronized VGA flip, reconstructed world+HUD planes with actual DAC; native reset caller0D29:16CA writes DAC235/scene227 black through original OUT opcodes, first palette tick decrements80to79; complete native palette black/white/black cycle and RNG1to2745024/AX41/countdown201, followupEA0 returned; exact98 before/after MOV mapBYTE1 stores bind GUARD24/actor168/A5 andGUARD25/actor174/A4, restore-underlay044C andoccupy06A9; map-writer endpoint06AD is mid-function; no host/physical/independent-pixel/full-gameplay/save-load/Win16 parity; prefixes overlap; original0254 allowed/blocked sparse decision-to-return tails, with blocked door7 state2 snapshot, no demonstrated entry-state transition; subsequent separate whole native0598 source door7 and neighbor6 state1to2 proved with exact2BYTE world delta/DGROUP57392B unchanged and original-code replay; earlier sparse capture alone remains weaker evidence; separate whole native classification producers mapheader514B identity,512output entries/seeds0and7; secondcall DGROUP includes observed clockDWORD+1, identified RTC INC but native writerPC not captured; pureproducer replay compared with explicit clockdelta allowance; separate whole original012A+C0A native mode7 GUARD0/actor20 orientation update, relative2/frame0400h, exact2BYTE world delta and unchangedDGROUP57392B/nearDSF200bank52B; original no-stub replay matches final registers; separate original0277:09C1..09D7 class8 copy block transfers90B IMG1 object81h header fromfile8F5Ah toDSF200h, objectoffsettable400h+4*81h gives159B32h; native classrecord4WORDs and prior52Bprefix bind source to orientation consumer; not whole map-loader/file IO execution trace.



## Aktualne meranie PASS1



Mapa `pass1_xms_move_request/noncode_intervals.csv/json`: **57118 B PARTIAL, 149 B CLASSIFIED ONLY, 28 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila 892 intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`.



| Centralny katalog | Pocet |

|---|---:|

| Funkcne rozsahy | 161 |

| Nezavisle dekodovane instrukcie | 6992 |

| Instrukcne bajty | 17629 |

| Unia typovanych dat celeho obrazu | 59469 B |

| Ostatne katalogom neposudene bajty | 94262 B |

| Intervaly celeho obrazu | 822 |

| Typovane data v povodnom NON-CODE | 57116 B |

| Kod v povodnom NON-CODE | 0 B |

| Seeded replay pripady | 1040549 |

| Oddelene prefixove replay pripady | 65548 |

| Original-EXE runtime scenare s definovanymi zasahmi | 31 |

| Runtime BSS tabulky mimo file image (nezvysuju PASS1) | 5088 B |

| Runtime buffer refinements, uz zahrnute v PASS1 | 4122 B /16 intervalov |

| Nove DEEP VERIFIED | 0 B |



Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.



## Artefakty a reprodukcia



`campaign_catalog/current_pass1_data_types.csv` ma 667 poli z 98 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.



Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_xms_move_request IMAGE_GROUP_DESCRIPTOR_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit 9fa80d424266f32c493dabff0d0d1390f62731da, pozri `CAMPAIGN_GUARD_ORIENTATION_PUBLICATION_RECEIPT_20261112.json`. Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou. Aktualny katalog alebo runtime scenare sa odvtedy zmenili; samotna zhoda mapy neznamena publikovanie novej davky. Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.



Samostatny Win110 paletovy doplnok: 4 rozsahy, 229 instrukcii / 641 B, 22 seeded pripadov. Nie je zahrnuty v DOS adresnej partition ani v DOS replay sucte; skutocny Win16 runtime 0.

## Coverage update: 13 areas

All areas remain **PARTIAL**. This table restores the named13-area ledger retained in [CRT_UNLOADED_HOOKS_REPORT.md](CRT_UNLOADED_HOOKS_REPORT.md),including its historical orientation column. Positional percentages must not be reassigned to differently named categories; the alternative category layout in preceding recent batch tables is not a measured replacement of that ledger. New percentages are **N/A** because full semantic denominators are missing. Method for every row: exact byte-address unions/originalPASS320 membership,enumerated matrices and independently verified native scenarios. No guessed semantic percentages; narrowCLASSIFIED ONLY/UNKNOWN remain explicit; newDEEP0.

|Area|Prior orientation|New %|New confirmed evidence|Unknown / blocker|Next concrete step|
|---|---:|---|---|---|---|
|Maps and formats|99|N/A|1536IMG headers,116equal-header alias groups|Actual045C payload format|Reconstruct original045C|
|Data types and constants|95|N/A|FourWORD class record,90BYTEdescriptor,8BnewBSS|HeaderWORD0/tail38B|Close descriptor field consumers|
|Tables and pointers|93|N/A|IMGobject directory/class8near pointers/native copy|Full allocation/lifetime/tableextent|Trace bank allocation/free and dedup reuse|
|Functions / ASM / CFG|90|N/A|Whole0584:98decoded/95executed starts|IO/allocator/diagnostic/045C callees|Close original dependencies|
|RNG|97|N/A|No new RNG closure|Full caller/scheduler coupling|Continue original RNG integration|
|Scheduler|96|N/A|No new scheduler closure|Complete tick/IRQ ordering|Capture deterministic scheduler contexts|
|DEMO and input|96|N/A|No new DEMO closure|Time/input coupling|Trace deterministic DEMO playback|
|Renderer / VGA|94|N/A|Frame bank source bound to IMG1|SelectedWORD-to-draw behavior|Trace decoded10B record usage|
|GUARD / bosses|93|N/A|GUARDclass8 resource provenance|Other classes/boss state banks|Verify more natural class consumers|
|Weapons / projectiles|92|N/A|No new weapon closure|Projectile damage/collision branches|Continue original projectile functions|
|Sprites / HUD / palette|92|N/A|90B bank bound to prior frame0400h|Sprite payload/animation semantics|Close decoder and actual draw linkage|
|SAVE / LOAD|92|N/A|No new save/load closure|Bank regeneration/state round-trip|Capture repeated level/load resource reuse|
|Windows Win16|92|N/A|No new Win16 evidence; DOSdispatch results separate|Win16 decoder/format/caller equivalence|Locate Win110 decoder analog|

No source-access blocker. Missing semantic/native evidence remains; campaign completion is not established.

