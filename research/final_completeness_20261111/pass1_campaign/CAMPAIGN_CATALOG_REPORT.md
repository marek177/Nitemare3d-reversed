# Nitemare 3D: aktualny dokazovy katalog



Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma 171360 B, SHA-256 `e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.



Najnovsi report: [aktualna analyticka davka](GUARD_VALIDATOR_REPORT.md). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Povodny Linux runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) zostava samostatnym auditom. Aktualne original-runtime testy: 27; presny rozsah: retained original packedDOS2 under DOSBox-X with debugger stops: startup/main, BSF/audio/VGA, resources/input, episodes, palettes/DAC, sound metadata/trace and fonts0/1/2; explicit CD intro/flip/read-map captures; AUTOTYPE IRQ/BDA/wait paths through main menu initial draw with414B descriptors and both VGA pages; foreground IRQ frames and explicit paused WORX SS/SP window, no captured private-stack keyIRQ; first XMS transfer and map-init return after episode1/difficulty1 selection, exact8192B MAP1 level0, sound474B negative-XMS-offset directory reconstruction, 57295B NONCODE endpoint snapshot; endpoint0D29:0A31 is pre-music-selection CALL, not game-loop entry; first post-map scheduler return, due buckets/world counter1to2/synchronized VGA flip, reconstructed world+HUD planes with actual DAC; native reset caller0D29:16CA writes DAC235/scene227 black through original OUT opcodes, first palette tick decrements80to79; complete native palette black/white/black cycle and RNG1to2745024/AX41/countdown201, followupEA0 returned; exact98 before/after MOV mapBYTE1 stores bind GUARD24/actor168/A5 andGUARD25/actor174/A4, restore-underlay044C andoccupy06A9; map-writer endpoint06AD is mid-function; no host/physical/independent-pixel/full-gameplay/save-load/Win16 parity; prefixes overlap; original0254 allowed/blocked sparse decision-to-return tails, with blocked door7 state2 snapshot, no demonstrated entry-state transition.



## Aktualne meranie PASS1



Mapa `pass1_xms_move_request/noncode_intervals.csv/json`: **57118 B PARTIAL, 149 B CLASSIFIED ONLY, 28 B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila 892 intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe`.



| Centralny katalog | Pocet |

|---|---:|

| Funkcne rozsahy | 150 |

| Nezavisle dekodovane instrukcie | 6257 |

| Instrukcne bajty | 15846 |

| Unia typovanych dat celeho obrazu | 58034 B |

| Ostatne katalogom neposudene bajty | 97480 B |

| Intervaly celeho obrazu | 766 |

| Typovane data v povodnom NON-CODE | 57116 B |

| Kod v povodnom NON-CODE | 0 B |

| Seeded replay pripady | 1013689 |

| Oddelene prefixove replay pripady | 65548 |

| Original-EXE runtime scenare s definovanymi zasahmi | 27 |

| Runtime BSS tabulky mimo file image (nezvysuju PASS1) | 4566 B |

| Runtime buffer refinements, uz zahrnute v PASS1 | 4122 B /16 intervalov |

| Nove DEEP VERIFIED | 0 B |



Rozdiel PARTIAL oproti typovanym NON-CODE datam je 2 B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.



## Artefakty a reprodukcia



`campaign_catalog/current_pass1_data_types.csv` ma 667 poli z 98 zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.



Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR pass1_xms_move_request GUARD_VALIDATOR_REPORT.md`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit 13269792d8cd7ebc06a072150f59b0a6b0c2b802, pozri `CAMPAIGN_GUARD_VALIDATOR_PUBLICATION_RECEIPT_20261112.json`. Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou. Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.



Samostatny Win110 paletovy doplnok: 4 rozsahy, 229 instrukcii / 641 B, 22 seeded pripadov. Nie je zahrnuty v DOS adresnej partition ani v DOS replay sucte; skutocny Win16 runtime 0.

## Coverage update: 13 areas

Historical percentages are orientation only; there is no measured complete semantic denominator for these areas. Accordingly **new percentage is N/A in every row**, not a fabricated revised percentage. Reproducible methodology is union of checked instruction-byte addresses, exact PASS320 membership, enumerated replay cases and independently verified native scenarios; these metrics are not converted into a semantic percentage. All areas remain PARTIAL unless a narrower item is explicitly labelled CLASSIFIED ONLY/UNKNOWN. No area is DEEP VERIFIED.

|Area|Prior orientation|New %|New confirmed evidence|Remaining unknown / blocker|Next concrete step|
|---|---:|---|---|---|---|
|EXE/segments|99|N/A|Original relocated native image checked again|Whole segment semantics unclosed|Close contextual DS/ES references|
|CRT/compiler|95|N/A|Missing-door diagnostic call identified|Error handler return contract|Decode FBA:000C and callees|
|WORX/audio|93|N/A|No new semantic closure|Private-stack key IRQ/audio output|Capture requested stack event|
|Data/tables|90|N/A|512 BSS bytes / two classification consumers|Producer and complete bit meanings|Trace table initialization writes|
|Resources|97|N/A|23 source/copy hashes unchanged|All resource producers not closed|Bind flag tables to resource source|
|Renderer|96|N/A|No new renderer closure|Clipping/complete scene parity|Close remaining renderer branches|
|Gameplay|96|N/A|Original collision validator and local door effects|Interaction0598 effects|Whole-call paired door snapshots|
|AI/bosses|94|N/A|Movement+validator shared-world replay|Modes/strategy helpers and bosses|Close 04C7:012A and 00B0|
|RNG/DEMO|93|N/A|Both RNG parities in bounded integration|Complete DEMO schedule|Trace demo input/frame coupling|
|SAVE/LOAD|92|N/A|No new closure|Round-trip behavior incomplete|Native deterministic save/load comparison|
|HUD/sprites|92|N/A|Actor coordinate alignment consumer|Animation and complete rendering|Bind remaining sprite branches|
|Cross-version|92|N/A|32 CFG/32 address-aware comparisons|Win16 and callee/data equivalence|Locate Win110 validator analog|
|Completeness/evidence|92|N/A|4 functions,10472 cases,1 native scenario added|28 UNKNOWN/149 CLASSIFIED ONLY and downstream gaps|Continue unknown and contradictory references|

No missing source blocks the current bounded batch. The blockers above are missing analytical evidence, not permission problems. Whole-campaign catalogue after integration: **150 functions, 6257 instructions, 15846 instruction bytes**, 58034 file data bytes, 97480 UNKNOWN_CONTENT bytes, **1013689 controlled cases**, **27 successful native scenarios** (overlapping prefixes), **4566 BSS table bytes**, 4122 already-covered runtime buffer bytes, 41 field-evidence rows. Counts describe local evidence scope, not complete game behavior.

