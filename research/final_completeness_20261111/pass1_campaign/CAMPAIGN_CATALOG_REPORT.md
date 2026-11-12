# Nitemare 3D: aktualny dokazovy katalog



Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.



Najnovsi report: [aktualna analyticka davka](DOOR_INTERACTION_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Povodny Linux runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) zostava samostatnym auditom. Aktualne original-runtime testy: 28; presny rozsah: retained original packedDOS2 under DOSBox-X with debugger stops: startup/main, BSF/audio/VGA, resources/input, episodes, palettes/DAC, sound metadata/trace and fonts0/1/2; explicit CD intro/flip/read-map captures; AUTOTYPE IRQ/BDA/wait paths through main menu initial draw with414B descriptors and both VGA pages; foreground IRQ frames and explicit paused WORX SS/SP window, no captured private-stack keyIRQ; first XMS transfer and map-init return after episode1/difficulty1 selection, exact8192B MAP1 level0, sound474B negative-XMS-offset directory reconstruction, 57295B NONCODE endpoint snapshot; endpoint0D29:0A31 is pre-music-selection CALL, not game-loop entry; first post-map scheduler return, due buckets/world counter1to2/synchronized VGA flip, reconstructed world+HUD planes with actual DAC; native reset caller0D29:16CA writes DAC235/scene227 black through original OUT opcodes, first palette tick decrements80to79; complete native palette black/white/black cycle and RNG1to2745024/AX41/countdown201, followupEA0 returned; exact98 before/after MOV mapBYTE1 stores bind GUARD24/actor168/A5 andGUARD25/actor174/A4, restore-underlay044C andoccupy06A9; map-writer endpoint06AD is mid-function; no host/physical/independent-pixel/full-gameplay/save-load/Win16 parity; prefixes overlap; original0254 allowed/blocked sparse decision-to-return tails, with blocked door7 state2 snapshot, no demonstrated entry-state transition; subsequent separate whole native0598 source door7 and neighbor6 state1to2 proved with exact2BYTE world delta/DGROUP57392B unchanged and original-code replay; earlier sparse capture alone remains weaker evidence.



## Aktualne meranie PASS1



Mapa `pass1_xms_move_request/noncode_intervals.csv/json`: **57118 B PARTIAL, 149 B CLASSIFIED ONLY, 28 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila 892 intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`.



| Centralny katalog | Pocet |

|---|---:|

| Funkcne rozsahy | 151 |

| Nezavisle dekodovane instrukcie | 6383 |

| Instrukcne bajty | 16208 |

| Unia typovanych dat celeho obrazu | 58034 B |

| Ostatne katalogom neposudene bajty | 97118 B |

| Intervaly celeho obrazu | 772 |

| Typovane data v povodnom NON-CODE | 57116 B |

| Kod v povodnom NON-CODE | 0 B |

| Seeded replay pripady | 1021881 |

| Oddelene prefixove replay pripady | 65548 |

| Original-EXE runtime scenare s definovanymi zasahmi | 28 |

| Runtime BSS tabulky mimo file image (nezvysuju PASS1) | 4566 B |

| Runtime buffer refinements, uz zahrnute v PASS1 | 4122 B /16 intervalov |

| Nove DEEP VERIFIED | 0 B |



Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.



## Artefakty a reprodukcia



`campaign_catalog/current_pass1_data_types.csv` ma 667 poli z 98 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.



Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_xms_move_request DOOR_INTERACTION_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit 0939609be3cd6363bd25706620485a19f30f2b86, pozri `CAMPAIGN_DOOR_INTERACTION_PUBLICATION_RECEIPT_20261112.json`. Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou. Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.



Samostatny Win110 paletovy doplnok: 4 rozsahy, 229 instrukcii / 641 B, 22 seeded pripadov. Nie je zahrnuty v DOS adresnej partition ani v DOS replay sucte; skutocny Win16 runtime 0.

## Coverage update: 13 areas

All areas remain **PARTIAL**. Previous orientation percentages below are historical, not measured baselines. New percentages are **N/A** because complete semantic denominators are absent. Method for every row: union of byte-checked bounded instruction addresses, original PASS320 interval membership, explicit matrix cases and independently verified native scenarios, without translating these counts into guessed semantic percentages. Narrow unresolved records remain CLASSIFIED ONLY/UNKNOWN; no DEEP VERIFIED additions.

|Area|Previous orientation|New %|New confirmed finding|Remaining unknown / blocker|Next concrete step|
|---|---:|---|---|---|---|
|EXE/segments|99|N/A|Native image/relocations rechecked|Full contextual reference semantics|Continue indexed DS/ES reference closure|
|CRT/compiler|95|N/A|Original door lookup used in model/native|Missing-door diagnostic return|Close FBA:000C|
|WORX/audio|93|N/A|SoundIDs25h/26h argument calls modelled|Native sound-request paths/private-stack IRQ|Capture nonzero request with original sound|
|Data/tables|90|N/A|Door adjacent state propagation/descriptor flag consumers|Flag producer and full state meanings|Trace table initialization and state update|
|Resources|97|N/A|23 original/copy hashes unchanged|Full producer closure|Bind tile flags to source data|
|Renderer|96|N/A|No new renderer closure|Clipping/full scene parity|Close remaining renderer branches|
|Gameplay|96|N/A|Native door7+6 states1to2, exact world delta|Native reverse transition and animation|Capture state0/2-to3|
|AI/bosses|94|N/A|Original GUARD interaction caller confirmed|Modes6/strategy1 helpers/bosses|Close04C7:012A and00B0|
|RNG/DEMO|93|N/A|No new RNG/DEMO closure|Complete scheduler/input coupling|Trace deterministic DEMO segment|
|SAVE/LOAD|92|N/A|No new closure|Round-trip behavior incomplete|Deterministic save/load comparison|
|HUD/sprites|92|N/A|Descriptor+5 invalidation-bit consumer|Actual redraw consequences|Trace consumers of descriptor flag01h|
|Cross-version|92|N/A|Real state4 semantic difference,64cases|Natural older-version and Win16 behavior|Find Win110 analog and state4 producer|
|Completeness/evidence|92|N/A|1function/8192cases/1native scenario added|28UNKNOWN/149CLASSIFIED ONLY, downstream gaps|Prioritize unresolved producers/references|

No source-access blocker for this batch. Remaining blockers are missing analytical/runtime evidence. No claim of full game parity, state-machine closure or campaign completion.

