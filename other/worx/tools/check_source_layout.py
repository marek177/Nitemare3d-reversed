#!/usr/bin/env python3
"""Verify /worx contains only reconstructed C++ source/header files."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
src=ROOT/'worx'
assert src.is_dir(), 'Missing /worx'
files=[p for p in src.rglob('*') if p.is_file()]
assert files, 'WORX source tree is empty'
assert all(p.suffix in ('.cpp','.hpp','.c','.h') for p in files), 'Non-source file detected in /worx'
assert not any(p.name.upper() in {'WORX.H','TCWORXL.LIB'} for p in files), 'Unverified WORX 2.01 vendor file'
assert (ROOT/'other/worx/tests').is_dir(), 'Missing /other/worx/tests'
print(f'PASS: {len(files)} source-only files under /worx')
