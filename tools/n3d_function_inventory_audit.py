#!/usr/bin/env python3
"""Audit user-supplied per-version function inventories exported from Ghidra/IDA.

CSV required columns: version, entry, status, evidence.
Never infer function count from linear disassembly or undefined bytes.
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
import sys

VALID = {'confirmed', 'candidate', 'unresolved'}
def parse(path):
    grouped = defaultdict(dict)
    errors = []
    with Path(path).open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.DictReader(stream)
        required = {'version', 'entry', 'status', 'evidence'}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ValueError('CSV requires: version,entry,status,evidence')
        for line, row in enumerate(reader, 2):
            version, entry, status = (row[k] or '').strip() for k in ('version','entry','status')
            evidence = (row['evidence'] or '').strip()
            if not version or not entry or status not in VALID:
                errors.append({'line': line, 'reason': 'invalid version, entry or status'})
                continue
            key = entry.upper()
            if key in grouped[version]:
                errors.append({'line': line, 'reason': 'duplicate version/entry', 'version': version, 'entry': key})
                continue
            if status == 'confirmed' and not evidence:
                errors.append({'line': line, 'reason': 'confirmed requires evidence', 'version': version, 'entry': key})
                continue
            grouped[version][key] = {'status': status, 'evidence': evidence}
    return grouped, errors

def audit(path):
    groups, errors = parse(path)
    versions = {}
    for version in sorted(groups):
        records = groups[version]
        counts = Counter(v['status'] for v in records.values())
        versions[version] = {
            'total_rows': len(records),
            'confirmed': counts['confirmed'],
            'candidate': counts['candidate'],
            'unresolved': counts['unresolved'],
            'entries': sorted(records)}
    return {'schema':'n3d-function-inventory-v1', 'source':'supplied_csv_only',
            'versions':versions,'errors':errors,
            'note':'Entry counts are not proven function totals; export completeness and segmentation require independent audit.'}

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('inventory', type=Path)
    p.add_argument('--json-out', type=Path)
    a = p.parse_args(argv)
    try:
        report = audit(a.inventory)
        result = json.dumps(report, sort_keys=True, indent=2) + '\n'
        if a.json_out:
            a.json_out.write_text(result, encoding='utf-8')
        else:
            print(result, end='')
        return 1 if report['errors'] else 0
    except (OSError, ValueError, UnicodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
