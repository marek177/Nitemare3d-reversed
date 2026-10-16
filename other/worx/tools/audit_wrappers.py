#!/usr/bin/env python3
"""Check the N3D v2.0 75-entry wrapper inventory and report selector gaps."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_report():
    wrapper_data = json.loads((ROOT / 'data/n3d_v20_wrappers.json').read_text(encoding='utf-8'))
    wrappers = wrapper_data['wrappers']
    errors = []
    if len(wrappers) != 75:
        errors.append(f"expected 75, got {len(wrappers)}")
    for index, w in enumerate(wrappers):
        s = int(w['start_image_hex'], 16)
        e = int(w['end_image_hex'], 16)
        if e - s + 1 != w['size_bytes']:
            errors.append(f"bad size at wrapper {index}")
        if index and s != int(wrappers[index-1]['end_image_hex'], 16) + 1:
            errors.append(f"non-contiguous entry at wrapper {index}")
    if wrappers and sum(w['size_bytes'] for w in wrappers) != 4843:
        errors.append('size sum not 4843')
    described = {int(code, 16) for w in wrappers for code in w['referenced_command_hex']}
    MAX_AH = max(described)
    not_described = [f"{c:02X}" for c in range(MAX_AH + 1) if c not in described]
    unmapped = [w['start_image_hex'] for w in wrappers if not w['referenced_command_hex']]
    return {
        'source': wrapper_data['source'],
        'N3D_wrapper_count': len(wrappers),
        'wrapper_size_bytes': sum(w['size_bytes'] for w in wrappers),
        'first_image_offset': wrappers[0]['start_image_hex'],
        'last_image_offset': wrappers[-1]['end_image_hex'],
        'number_of_distinct_AH_commands_in_descriptions': len(described),
        'max_described_AH_command': f'{MAX_AH:02X}',
        'undocumented_in_N3D_wrapper_descriptions_00_to_max': not_described,
        'wrappers_without_literal_opcode_in_role_description': unmapped,
        'IMPORTANT': 'Undescribed command != nonexistent/unsupported/unreachable; symbolic coverage != behavior parity.',
        'errors': errors,
        'status': 'INVENTORY_CONSISTENT' if not errors else 'INVENTORY_INCONSISTENT',
    }


def main():
    result = build_report()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not result['errors'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
