#!/usr/bin/env python3
"""Check consistency of exported NEXT7 tables, not original EXE semantics."""
import argparse
import csv
from collections import Counter
import itertools
import json
from pathlib import Path

EXPECTED_FAMILIES = {
    'STACK_WORK_BUFFER':5, 'FIXED_DS_40':1, 'FIXED_DS_STRING':4,
    'FIXED_DS_16':2, 'LOCAL_FRAME_27':2, 'ALLOCATOR_90':2,
    'GLOBAL_TEXT_TO_STACK':10, 'RECORD_TEXT_TO_STACK':2, 'RECORD_FARPTR_41':1,
}


def check(path):
    with path.open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 29 or [int(r['index']) for r in rows] != list(range(29)):
        raise ValueError('expected 29 ordered unique site rows')
    if any(r['version'] != '2.0' for r in rows):
        raise ValueError('unexpected build scope')
    if len({r['img'] for r in rows}) != 29:
        raise ValueError('duplicate image site')
    if Counter(r['family'] for r in rows) != EXPECTED_FAMILIES:
        raise ValueError('unexpected local destination families')
    if any(r['indirect_OBJECT18_excluded_globally'] != 'NO' for r in rows):
        raise ValueError('export must not assert global OBJECT18 exclusion')
    transfers = Counter(r['logical_transfer_id'] for r in rows)
    if len(transfers) != 21 or Counter(transfers.values()) != {1:13, 2:8}:
        raise ValueError('expected 21 transfers: 13 single sites, 8 paired sites')
    dynamic = [r for r in rows if r['family'] == 'RECORD_FARPTR_41']
    if (dynamic[0]['img'] != '0E2A4' or dynamic[0]['local_copy_bytes'] != '41B' or
        dynamic[0]['pointer_owner_status'] != 'dynamic_record_owner_open'):
        raise ValueError('record destination must retain its open owner boundary')
    # Independently sum the report's immutable source-string lengths. Each
    # append replaces the preceding NUL. This is not a mutable-buffer proof.
    lengths = [130 + sum((size-1) for bit,size in zip(mask,(19,21,20,22)) if bit)
               for mask in itertools.product((False,True), repeat=4)]
    return {'scope':'exported_table_consistency_and_reported_length_arithmetic',
            'sites':len(rows), 'logical_transfers':len(transfers),
            'families':dict(Counter(r['family'] for r in rows)),
            'text_combinations':len(lengths), 'maximum_text_bytes_including_nul':max(lengths),
            'local_frame_bytes':258, 'minimum_spare_bytes':258-max(lengths),
            'original_executable_reverified':False, 'global_OBJECT18_aliases_closed':False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('table', nargs='?', type=Path,
        default=Path(__file__).resolve().parents[1] / 'docs/evidence/2026-10-20/NEXT7_TYPED_ALL29_DOS20.csv')
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.table), indent=2))
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f'FAIL: {exc}\n')
