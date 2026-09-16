#!/usr/bin/env python3
"""Copy an original Nitemare 3D Windows installation into data/original."""
from __future__ import annotations
import argparse, shutil
from pathlib import Path
FILES = ['NITE3W.EXE','WING.DLL','DISPDIB.DLL','MAP.1','MAP.2','MAP.3','IMG.1','IMG.2','IMG.3','OBJECTS.1','OBJECTS.2','OBJECTS.3','WALLS.1','WALLS.2','WALLS.3','DEMO.1','DEMO.2','DEMO.3','SND.DAT','UIF.DAT','GAME.PAL','ENDING.FLI','NITE3D.BSF']
def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('source', type=Path); ap.add_argument('--dest', type=Path, default=Path('data/original')); args = ap.parse_args(); args.dest.mkdir(parents=True, exist_ok=True)
    by_upper = {p.name.upper(): p for p in args.source.iterdir() if p.is_file()}; missing = []
    for name in FILES:
        src = by_upper.get(name)
        if src is None: missing.append(name); continue
        shutil.copy2(src, args.dest / name); print(f'copied {name}')
    if missing: print('missing:', ', '.join(missing))
    return 0
if __name__ == '__main__': raise SystemExit(main())
