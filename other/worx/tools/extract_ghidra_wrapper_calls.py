#!/usr/bin/env python3
"""Extract decompiler-visible WORX calls in the N3D wrapper band.

The Ghidra .c text is known to contain overlapping/bogus decompilation elsewhere.
This extraction is secondary corroboration; no instruction-level proof claimed.
"""
import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
FN = re.compile(r'(?m)^[^\n{};]*?\b(?:FUN_2000_|switchdataD_2000_)([0-9a-f]{4})\([^\n;]*?\)\s*\n\{')
CALL = re.compile(r'func_0x00010bfc\(([^;]*?)\);', re.S)


def extract(code: str, inventory: list) -> dict:
    known = {int(x['start_image_hex'], 16): x for x in inventory}
    extracted = []
    for m in FN.finditer(code):
        image_start = 0x10000 + int(m.group(1), 16)
        if image_start not in known:
            continue
        end = code.find('\n}\n', m.end())
        if end == -1:
            continue
        body = code[m.end():end]
        calls = []
        for call in CALL.finditer(body):
            args = ' '.join(call.group(1).split())
            # Decompiler call ABI passes the far segment before AH.
            parts = args.split(',')
            ah = parts[1].strip() if len(parts) > 1 else None
            calls.append({'decompiled_argument_expression': args,
                          'AH_expression': ah,
                          'AH_literal': f'{int(ah, 0):02X}' if ah and re.fullmatch(r'0x[0-9a-fA-F]+|[0-9]+', ah) else None})
        extracted.append({
            'wrapper': known[image_start]['start_image_hex'],
            'wrapper_ends': known[image_start]['end_image_hex'],
            'confirmed_commands_from_pass23': known[image_start]['referenced_command_hex'],
            'decompiled_call_sites': calls,
            'direct_call_count': len(calls),
        })
    present = {int(x['wrapper'], 16) for x in extracted}
    missing = [x['start_image_hex'] for x in inventory if int(x['start_image_hex'], 16) not in present]
    mismatches = []
    for x in extracted:
        original = set(x['confirmed_commands_from_pass23'])
        reconstructed = {call['AH_literal'] for call in x['decompiled_call_sites'] if call['AH_literal']}
        if original and reconstructed and original != reconstructed:
            mismatches.append({'wrapper': x['wrapper'], 'inventory': sorted(original),
                               'decompiled': sorted(reconstructed)})
    return {
        'note': 'Secondary, imperfect Ghidra decompilation. NOT an original machine-code byte verification.',
        'wrapper_count_present_in_decompilation': len(extracted),
        'number_of_direct_INT63_wrapper_calls': sum(x['direct_call_count'] for x in extracted),
        'wrapper_entries_not_in_decompiler_extract': missing,
        'inventory_vs_decompiler_command_mismatches': mismatches,
        'entry_details': extracted,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('ghidra_c', type=Path, help='Your original N3D-E-20.EXE decompiler .c')
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    inventory = json.loads((HERE / 'data/n3d_v20_wrappers.json').read_text())['wrappers']
    report = extract(args.ghidra_c.read_text(encoding='utf-8', errors='replace'), inventory)
    result = json.dumps(report, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.write_text(result, encoding='utf-8')
        print(f"Wrote {args.output}; {report['wrapper_count_present_in_decompilation']} functions",
              f"{report['number_of_direct_INT63_wrapper_calls']} call expressions;",
              f"{len(report['inventory_vs_decompiler_command_mismatches'])} mismatches")
    else:
        print(result)


if __name__ == '__main__':
    main()
