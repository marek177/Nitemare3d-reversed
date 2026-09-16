#!/usr/bin/env python3
from __future__ import annotations
import argparse
from pathlib import Path

def load_push_ids(objects: Path) -> set[int]:
    result: set[int] = set()
    for line in objects.read_text(encoding='latin1').splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[3] == 'PUSH': result.add(int(parts[0], 16))
    return result

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('data', type=Path, nargs='?', default=Path('data/original')); args = ap.parse_args()
    total = 0; max_level = (0, 0, 0)
    for ep in (1, 2, 3):
        push_ids = load_push_ids(args.data / f'OBJECTS.{ep}'); raw = (args.data / f'MAP.{ep}').read_bytes(); level_count = int.from_bytes(raw[0:2], 'little')
        print(f'Episode {ep}: PUSH ids=' + ','.join(f'0x{x:02X}' for x in sorted(push_ids)))
        for lev in range(level_count):
            block = raw[514 + lev * 8192:514 + (lev + 1) * 8192]; found = []
            for i in range(4096):
                wall = block[i * 2]; obj = block[i * 2 + 1]
                if obj in push_ids: found.append((i % 64, i // 64, wall, obj))
            if found:
                total += len(found)
                if len(found) > max_level[2]: max_level = (ep, lev + 1, len(found))
                details = ' '.join(f'({x},{y}) obj=0x{o:02X} floor=0x{w:02X}' for x,y,w,o in found)
                print(f'  L{lev+1:02d}: {len(found):2d}  {details}')
    print(f'Total PUSH placements: {total}'); print(f'Maximum in one level: E{max_level[0]}L{max_level[1]} = {max_level[2]} (EXE limit is 12)'); return 0
if __name__ == '__main__': raise SystemExit(main())
