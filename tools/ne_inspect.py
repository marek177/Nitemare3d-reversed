#!/usr/bin/env python3
"""Minimal 16-bit Windows NE inspector used for NITE3W.EXE reconstruction."""
from __future__ import annotations
import argparse, struct
from pathlib import Path

def u16(data: bytes, off: int) -> int: return struct.unpack_from('<H', data, off)[0]
def u32(data: bytes, off: int) -> int: return struct.unpack_from('<I', data, off)[0]
def pstring(data: bytes, off: int) -> str:
    n = data[off]
    return data[off + 1:off + 1 + n].decode('latin1', errors='replace')

def inspect(path: Path) -> str:
    data = path.read_bytes()
    if len(data) < 0x40 or data[:2] != b'MZ': raise ValueError('Not an MZ executable')
    ne = u32(data, 0x3C)
    if data[ne:ne + 2] != b'NE': raise ValueError('MZ file does not contain an NE header')
    seg_count = u16(data, ne + 0x1C); mod_count = u16(data, ne + 0x1E)
    seg_tab_rel = u16(data, ne + 0x22); mod_tab_rel = u16(data, ne + 0x28); imp_names_rel = u16(data, ne + 0x2A)
    align_shift = u16(data, ne + 0x32); target_os = data[ne + 0x36]; expected_win = u16(data, ne + 0x3E)
    mod_tab = ne + mod_tab_rel; imp_names = ne + imp_names_rel
    modules = [pstring(data, imp_names + u16(data, mod_tab + i * 2)) for i in range(mod_count)]
    seg_tab = ne + seg_tab_rel
    segments = []
    for i in range(seg_count):
        sector, length, flags, min_alloc = struct.unpack_from('<HHHH', data, seg_tab + i * 8)
        segments.append((i + 1, sector << align_shift, length or 65536, flags, min_alloc))
    lines = [f'File: {path.name}', f'Size: {len(data)} bytes', f'NE header: 0x{ne:X}', f'Target OS code: {target_os} (2 = Windows)', f'Expected Windows version word: 0x{expected_win:04X}', f'Segments: {seg_count}', f'Imported modules ({mod_count}): {", ".join(modules)}', '', 'Segments:', '  #   file offset   length   flags   minalloc']
    for idx, off, length, flags, minalloc in segments: lines.append(f'  {idx:2d}  0x{off:08X}  {length:6d}  0x{flags:04X}  {minalloc:6d}')
    return '\n'.join(lines)

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument('exe', type=Path); args = ap.parse_args(); print(inspect(args.exe)); return 0
if __name__ == '__main__': raise SystemExit(main())
