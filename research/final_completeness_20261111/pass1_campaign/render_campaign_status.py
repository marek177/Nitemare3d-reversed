"""python render_campaign_status.py OUTPUTS_DIR; current snapshot from authoritative JSON/CSV."""
import csv,json,sys
from pathlib import Path
root=Path(sys.argv[1]);folder=sys.argv[2] if len(sys.argv)>2 else 'pass1_fcb_prefix';report=sys.argv[3] if len(sys.argv)>3 else 'CRT_ENTRY_GAP_VERSIONS_REPORT.md'
s=json.loads((root/'campaign_catalog/summary.json').read_text());p=json.loads((root/folder/'independent_partition_check.json').read_text())
types=list(csv.DictReader((root/'campaign_catalog/current_pass1_data_types.csv').open(encoding='utf-8-sig')))
assert s['latest_pass1_map_sha256']==p['map_sha256']
assert sum(s['primary_type_bytes'].values())==s['image_bytes']
assert s['pass1_partial_bytes_without_typed_data']==p['status_bytes']['PARTIAL']-s['original_noncode_intersection_data_bytes']
latest=(root/report).read_text(encoding='utf-8');table=latest[latest.index('## Aktualizácia 13 oblastí'):latest.index('## Runtime testy na vykonanie')]
text=f'''# Nitemare 3D: aktualny dokazovy katalog

Kampan ani PASS1 nie su dokoncene. DOS 2.0 obraz ma {s['image_bytes']} B, SHA-256 `{s['image_sha256']}`. Tato snimka je generovana z aktualnych strojovych vystupov; starsie analyticke reporty zostavaju historickymi davkami.

Najnovsi report: [aktualna analyticka davka]({report}). Predosle dokazy: [DSP status wrapper](PASS1_DSP_STATUS_REPORT.md), [debug logger](PASS1_DEBUG_LOGGER_REPORT.md), [CRT unloaded hooks](CRT_UNLOADED_HOOKS_REPORT.md), [Win110 trig calleri](WIN110_TRIG_CALLERS_REPORT.md). [Runtime balik](RUNTIME_BUNDLE_PROBE_REPORT.md) je citatelny, ale dostupna Linux distribucia pre prilozeny ELF nebola zistena. Prirodzene runtime testy zostavaju 0.

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
| Prirodzene runtime testy | {s['runtime_tests']} |
| Nove DEEP VERIFIED | {s['new_deep_verified_bytes']} B |

Rozdiel PARTIAL oproti typovanym NON-CODE datam je {s['pass1_partial_bytes_without_typed_data']} B: relokacny WORD DS:2358 v slote DS:2356 s neuzavretou typovou rolou. Centralne neposudene bajty neprepisuju historicke klasifikacie inych auditov. Katalog poloh kodu je ohraniceny touto kampanou, nie uplny inventar vsetkych funkcii hry.

## Artefakty a reprodukcia

`campaign_catalog/current_pass1_data_types.csv` ma {len(types)} poli z {len(set(r['source'] for r in types))} zdrojov. `functions.csv`, `independent_instructions.csv`, `byte_intervals.csv/json`, `summary.json` a `untyped_partial_relocation_check.json` obsahuju hranice, typy a dokazy. Aktualna opravena dvojbajtova mapa je `[2570E,2770E)`; stary posunuty rozsah sa neimportuje.

Reprodukcia: analyticky skript uvedeny v aktualnom reporte, `promote_pass1_fields.py`, `verify_pass1_partition.py`, `independent_decode_and_catalog.py`, potom `render_campaign_status.py OUTPUTS_DIR {folder} {report}`. Presne vstupy a obmedzenia su v reportoch jednotlivych davok. Posledna overena publikacia je commit 52924ebf849dd79d15af9d7c164b8304f50cae87, pozri `CAMPAIGN_PUBLICATION_RECEIPT.json`. Novsia lokalna analyticka davka sa tym automaticky nepovazuje za publikovanu.

'''+table
for name in ['CAMPAIGN_CONSOLIDATED_REPORT.md','CAMPAIGN_CATALOG_REPORT.md']:
    target=root/name;history=root/(target.stem+'_BEFORE_DEBUG_LOGGER.md')
    if target.exists() and not history.exists():history.write_bytes(target.read_bytes())
    target.write_text(text,encoding='utf-8')
print(json.dumps(dict(reports=2,fields=len(types),sources=len(set(r['source'] for r in types)),pass1_map_sha256=p['map_sha256'])))






























