"""python render_campaign_status.py OUTPUTS_DIR; current snapshot from authoritative JSON/CSV."""

import csv,json,sys

from pathlib import Path

root=Path(sys.argv[1]);folder=sys.argv[2] if len(sys.argv)>2 else 'pass1_xms_move_request';report=sys.argv[3] if len(sys.argv)>3 else 'DAMAGE_SOUND_FRAME_CHAIN_REPORT.md'

s=json.loads((root/'campaign_catalog/summary.json').read_text());p=json.loads((root/folder/'independent_partition_check.json').read_text())

receipt_path=root/'CAMPAIGN_REACTIONCHAIN_PUBLICATION_RECEIPT_20261113.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_DAMAGECONSUMER_PUBLICATION_RECEIPT_20261113.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_CRTSEEK_PUBLICATION_RECEIPT_20261113.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_MUSICPAIR_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_FARFREE_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_FARMALLOC_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_CRTLARGE_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_FARFREE_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_FARMALLOC_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_CRTLARGE_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_CACHEINIT_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_XMSADAPTER_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_CACHECLEANUP_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_OBJECTDRAW_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_FTIME_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_CALENDAR_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_IMAGE_RETRIEVAL_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_IMAGE_RECORD_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_IMAGE_GROUP_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_GUARD_ORIENTATION_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_WORX_BANK_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_CLASSIFICATION_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_DOOR_INTERACTION_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_GUARD_VALIDATOR_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_GUARD_VALIDATOR_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_GUARD_MOVE_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_PALETTE_EFFECT_PUBLICATION_RECEIPT_20261112.json'
if not receipt_path.exists():receipt_path=root/'CAMPAIGN_SCHEDULER_PUBLICATION_RECEIPT_20261112.json'

if not receipt_path.exists():receipt_path=root/'CAMPAIGN_NEWGAME_PUBLICATION_RECEIPT_20261112.json'

if not receipt_path.exists():receipt_path=root/'CAMPAIGN_XMS_PUBLICATION_RECEIPT_20261112.json'

if not receipt_path.exists():receipt_path=root/'CAMPAIGN_MAIN_MENU_PUBLICATION_RECEIPT_20261112.json'

if not receipt_path.exists():receipt_path=root/'CAMPAIGN_WORX_STACK_PUBLICATION_RECEIPT_20261112.json'

if not receipt_path.exists():receipt_path=root/'CAMPAIGN_KEYBOARD_FONT1_PUBLICATION_RECEIPT_20261112.json'

if not receipt_path.exists():receipt_path=root/'CAMPAIGN_INTRO_FONT0_PUBLICATION_RECEIPT_20261112.json'

if not receipt_path.exists():receipt_path=root/'CAMPAIGN_VGA_PUBLICATION_RECEIPT_20261112.json'

if not receipt_path.exists():receipt_path=root/'CAMPAIGN_RUNTIME_PUBLICATION_RECEIPT_20261112.json'

if not receipt_path.exists():receipt_path=root/'CAMPAIGN_PUBLICATION_RECEIPT_20261112.json'

if not receipt_path.exists():receipt_path=root/'CAMPAIGN_PUBLICATION_RECEIPT.json'

publication=json.loads(receipt_path.read_text())

publication_state='Hash aktualnej mapy sa zhoduje s publikovanou analytickou snimkou.' if publication.get('map_sha256')==p['map_sha256'] else 'Aktualna mapa bola od publikovanej snimky zmenena; nova lokalna davka tym nie je automaticky publikovana.'

if publication.get('runtime_tests')!=s['runtime_tests'] or publication.get('catalog_functions')!=s['functions']:publication_state+=' Aktualny katalog alebo runtime scenare sa odvtedy zmenili; samotna zhoda mapy neznamena publikovanie novej davky.'

types=list(csv.DictReader((root/'campaign_catalog/current_pass1_data_types.csv').open(encoding='utf-8-sig')))

assert s['latest_pass1_map_sha256']==p['map_sha256']

assert sum(s['primary_type_bytes'].values())==s['image_bytes']

assert s['pass1_partial_bytes_without_typed_data']==p['status_bytes']['PARTIAL']-s['original_noncode_intersection_data_bytes']

latest=(root/report).read_text(encoding='utf-8');table=latest[latest.index('## Coverage update: 13 areas'):latest.index('## Required next runtime tests')]

win=s.get('win110_palette_supplement');win_note=('Samostatny Win110 paletovy doplnok: '+str(win['functions'])+' rozsahy, '+str(win['instructions'])+' instrukcii / '+str(win['instruction_bytes'])+' B, '+str(win['replay_cases_separate'])+' seeded pripadov. Nie je zahrnuty v DOS adresnej partition ani v DOS replay sucte; skutocny Win16 runtime 0.\n\n') if win else ''

text=f'''# Nitemare 3D: aktualny dokazovy katalog



Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma {s['image_bytes']} B, SHA-256 `{s['image_sha256']}`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.



Najnovsi report: [aktualna analyticka davka]({report}). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Povodny Linux runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) zostava samostatnym auditom. Aktualne original-runtime testy: {s['runtime_tests']}; presny rozsah: {s['runtime_tests_scope']}.



## Aktualne meranie PASS1



Mapa `{folder}/noncode_intervals.csv/json`: **{p['status_bytes']['PARTIAL']} B PARTIAL, {p['status_bytes']['CLASSIFIED ONLY']} B CLASSIFIED ONLY, {p['status_bytes']['UNKNOWN']} B UNKNOWN, 0 B DEEP VERIFIED**, spolu presne 57 295 B. Nezavisla kontrola overila {p['intervals']} intervalovych SHA, presne clenstvo baseline, nulove diery a prekryvy. Integrita partition nie je dokaz uplnej semantiky. SHA mapy: `{p['map_sha256']}`.



| Centralny katalog | Pocet |

|---|---:|

| Funkcne rozsahy | {s['functions']} |

| Nezavisle dekodovane instrukcie | {s['independent_instruction_count']} |

| Instrukcne bajty | {s['independent_instruction_bytes']} |

| Unia typovanych dat celeho obrazu | {s['data_bytes_with_local_evidence']} B |

| Ostatne katalogom neposudene bajty | {s['primary_type_bytes']['UNKNOWN_CONTENT']} B |

| Intervaly celeho obrazu | {s['interval_count']} |

| Typovane data v povodnom NON-CODE | {s['original_noncode_intersection_data_bytes']} B |

| Kod v povodnom NON-CODE | {s['original_noncode_intersection_code_bytes']} B |

| Seeded replay pripady | {s['controlled_instruction_replay_cases']} |

| Oddelene prefixove replay pripady | {s.get('direction_index_prefix_replay_cases',0)} |

| Original-EXE runtime scenare s definovanymi zasahmi | {s['runtime_tests']} |

| Runtime BSS tabulky mimo file image (nezvysuju PASS1) | {s.get('runtime_bss_table_bytes_outside_file',0)} B |

| Runtime buffer refinements, uz zahrnute v PASS1 | {s.get('runtime_buffer_refinement_bytes_already_in_pass1',0)} B /{s.get('runtime_buffer_refinement_records',0)} intervalov |

| Nove DEEP VERIFIED | {s['new_deep_verified_bytes']} B |



Rozdiel PARTIAL oproti typovanym NON-CODE datam je {s['pass1_partial_bytes_without_typed_data']} B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.



## Artefakty a reprodukcia



`campaign_catalog/current_pass1_data_types.csv` ma {len(types)} poli z {len(set(r['source'] for r in types))} zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.



Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR {folder} {report}`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Overena publikovana analyticka snimka je commit {publication['commit']}, pozri `{receipt_path.name}`. {publication_state} Historicke poznamky v davkovych reportoch uvadzaju stav v case ich vzniku.



'''+win_note+table

for name in ['CAMPAIGN_CONSOLIDATED_REPORT.md','CAMPAIGN_CATALOG_REPORT.md']:

    target=root/name;history=root/(target.stem+'_BEFORE_DEBUG_LOGGER.md')

    if target.exists() and not history.exists():history.write_bytes(target.read_bytes())

    target.write_text(text,encoding='utf-8')

print(json.dumps(dict(reports=2,fields=len(types),sources=len(set(r['source'] for r in types)),pass1_map_sha256=p['map_sha256'])))





























































