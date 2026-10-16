#!/usr/bin/env python3
"""Extract the separate In Search of Dr. Riptide WORX AH->routine table.

Input is the IDA-style Riptide decomp/seg1c75.asm from xor2003/riptide-re.
This is a CROSS-GAME HYPOTHESIS ONLY. Never treat its offsets as N3D addresses.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

START = re.compile(r'^word_20950\s+dw\s+(.*)$')
END = re.compile(r'^word_209EE\s+dw\s+')
DW = re.compile(r'^\s*(?:(?:word_20950\s+)?dw)\s+(?:offset\s+)?([^\s;]+)', re.I)


def parse_table(asm: str):
    lines = asm.splitlines()
    state = False
    entries = []
    for line in lines:
        if not state:
            if START.search(line):
                state = True
            else:
                continue
        if END.match(line):
            break
        match = DW.match(line)
        if match:
            raw = match.group(1)
            entries.append({'ah': f'{len(entries):02X}', 'target': raw,
                            'valid_pointer_candidate': raw != '0'})
        elif line.strip() and not line.lstrip().startswith(';'):
            # Do not silently parse unrelated data if the source structure changes.
            if 'dw' not in line and not line.lstrip().startswith('word_209'):
                raise ValueError('Unexpected data inside Riptide dispatch region: ' + line)
    if not state:
        raise ValueError('Riptide word_20950 table not found')
    if len(entries) != 79:
        raise ValueError(f'Expected 79 Riptide entries 00..4E, found {len(entries)}')
    return entries


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('riptide_asm', type=Path)
    args = p.parse_args()
    entries = parse_table(args.riptide_asm.read_text(encoding='utf-8', errors='replace'))
    print(json.dumps({
        'provenance': 'xor2003/riptide-re decomp/seg1c75.asm (different game)',
        'entries': entries,
        'table_range_ah': '00..4E',
        'n3d_uses_51': True,
        'cannot_replace_n3d_int63_dispatch_without_new_binary_proof': True,
    }, indent=2))


if __name__ == '__main__':
    main()
