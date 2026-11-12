# Nitemare 3D: aktualny dokazovy katalog



Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.



Najnovsi report: [aktualna analyticka davka](WORX_REGISTER_BANK_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Povodny Linux runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) zostava samostatnym auditom. Aktualne original-runtime testy: 29; presny rozsah: retained original packedDOS2 under DOSBox-X with debugger stops: startup/main, BSF/audio/VGA, resources/input, episodes, palettes/DAC, sound metadata/trace and fonts0/1/2; explicit CD intro/flip/read-map captures; AUTOTYPE IRQ/BDA/wait paths through main menu initial draw with414B descriptors and both VGA pages; foreground IRQ frames and explicit paused WORX SS/SP window, no captured private-stack keyIRQ; first XMS transfer and map-init return after episode1/difficulty1 selection, exact8192B MAP1 level0, sound474B negative-XMS-offset directory reconstruction, 57295B NONCODE endpoint snapshot; endpoint0D29:0A31 is pre-music-selection CALL, not game-loop entry; first post-map scheduler return, due buckets/world counter1to2/synchronized VGA flip, reconstructed world+HUD planes with actual DAC; native reset caller0D29:16CA writes DAC235/scene227 black through original OUT opcodes, first palette tick decrements80to79; complete native palette black/white/black cycle and RNG1to2745024/AX41/countdown201, followupEA0 returned; exact98 before/after MOV mapBYTE1 stores bind GUARD24/actor168/A5 andGUARD25/actor174/A4, restore-underlay044C andoccupy06A9; map-writer endpoint06AD is mid-function; no host/physical/independent-pixel/full-gameplay/save-load/Win16 parity; prefixes overlap; original0254 allowed/blocked sparse decision-to-return tails, with blocked door7 state2 snapshot, no demonstrated entry-state transition; subsequent separate whole native0598 source door7 and neighbor6 state1to2 proved with exact2BYTE world delta/DGROUP57392B unchanged and original-code replay; earlier sparse capture alone remains weaker evidence; separate whole native classification producers mapheader514B identity,512output entries/seeds0and7; secondcall DGROUP includes observed clockDWORD+1, identified RTC INC but native writerPC not captured; pureproducer replay compared with explicit clockdelta allowance.



## Aktualne meranie PASS1



Mapa `pass1_xms_move_request/noncode_intervals.csv/json`: **57118 B PARTIAL, 149 B CLASSIFIED ONLY, 28 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila 892 intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`.



| Centralny katalog | Pocet |

|---|---:|

| Funkcne rozsahy | 157 |

| Nezavisle dekodovane instrukcie | 6657 |

| Instrukcne bajty | 16840 |

| Unia typovanych dat celeho obrazu | 59469 B |

| Ostatne katalogom neposudene bajty | 95051 B |

| Intervaly celeho obrazu | 796 |

| Typovane data v povodnom NON-CODE | 57116 B |

| Kod v povodnom NON-CODE | 0 B |

| Seeded replay pripady | 1029235 |

| Oddelene prefixove replay pripady | 65548 |

| Original-EXE runtime scenare s definovanymi zasahmi | 29 |

| Runtime BSS tabulky mimo file image (nezvysuju PASS1) | 5080 B |

| Runtime buffer refinements, uz zahrnute v PASS1 | 4122 B /16 intervalov |

| Nove DEEP VERIFIED | 0 B |



Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.



## Artefakty a reprodukcia



`campaign_catalog/current_pass1_data_types.csv` ma 667 poli z 98 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.



Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_xms_move_request WORX_REGISTER_BANK_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit c6c3bb79e4d254e91e2f2eee09d11ce8f1dedc88, pozri `CAMPAIGN_WORX_BANK_PUBLICATION_RECEIPT_20261112.json`. Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou. Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.



Samostatny Win110 paletovy doplnok: 4 rozsahy, 229 instrukcii / 641 B, 22 seeded pripadov. Nie je zahrnuty v DOS adresnej partition ani v DOS replay sucte; skutocny Win16 runtime 0.

## Coverage update: 13 areas

All areas remain **PARTIAL**. Prior percentages are historical orientation only; new percentages are **N/A** because complete semantic denominators are missing. Method for every row: exact instruction/data byte unions, PASS320 membership, enumerated controlled cases and independently verified native scenarios, without translating counts into guessed semantic percentages. Narrow CLASSIFIED ONLY/UNKNOWN items remain explicit; new DEEP0.

|Area|Prior orientation|New %|New confirmed evidence|Unknown / blocker|Next concrete step|
|---|---:|---|---|---|---|
|EXE/segments|99|N/A|Independent WORX bank/entry segment anchors across8labels|Other callbacks/DS contexts|Continue address-as-data targets|
|CRT/compiler|95|N/A|No new CRT closure; stale leap-table pattern not promoted|149classified storage/padding roles|Find actual consumers/proven unused object provenance|
|WORX/audio|93|N/A|128×11 bank,programmer,original delayed writer integration|Resolver4630/real callback/acoustic output|Close resolver and natural bank load|
|Data/tables|90|N/A|1435new file-data bytes outsideNONCODE|DGROUP mask block still lacks consumer|Trace alternate/contextual references|
|Resources|97|N/A|11-of16 source record conversion|Source resource identity/lifetime|Trace original4630 input|
|Renderer|96|N/A|1812D raw mask reference now has sound-data context|DS0130 mask users unresolved|Keep interval CLASSIFIED ONLY|
|Gameplay|96|N/A|No new gameplay closure|Complete damage/projectile/door state updates|Continue original gameplay callees|
|AI/bosses|94|N/A|No new AI closure|GUARD strategy/motion/boss branches|Close04C7:012A/00B0|
|RNG/DEMO|93|N/A|No new closure|Native time/input ordering|Capture RTC entry/IRET|
|SAVE/LOAD|92|N/A|No new closure|Recreated state/resource round-trip|Deterministic native comparison|
|HUD/sprites|92|N/A|No new closure|Remaining sprite/HUD branches|Continue true rendering callers|
|Cross-version|92|N/A|40CFG/normalized,8whole-bank byte matches|Natural initialized state/Win16|Locate Win110 sound bank/consumer analog|
|Completeness/evidence|92|N/A|3new functions,1435new dataB,6166executions|28unknown/149classified and downstream scopes|Prioritize remaining actual consumers|

No source-access blocker. The true limitations are missing segment/caller/runtime evidence. These are not grounds to mark the campaign complete.

