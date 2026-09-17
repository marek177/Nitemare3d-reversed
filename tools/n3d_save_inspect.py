#!/usr/bin/env python3
from pathlib import Path
import sys

CONFIG_FIELDS = [
    (0x00,4,'render_width'),
    (0x04,2,'window_width'),
    (0x06,2,'window_height'),
    (0x08,1,'mouse_sensitivity'),
    (0x09,1,'joystick_sensitivity'),
    (0x0A,1,'music_volume'),
    (0x0B,1,'sfx_volume'),
    (0x0C,1,'mouse_enabled'),
    (0x0D,1,'music_enabled'),
    (0x0E,1,'sfx_enabled'),
    (0x0F,1,'joystick_enabled'),
    (0x10,1,'cheat_omniscient'),
    (0x11,1,'cheat_omnipotent'),
    (0x12,1,'cheat_omnifarious'),
    (0x13,1,'cheat_omnificent'),
]

USER_PARTS = [
    ('record_size',4),('slot_name',0x29),('episode',2),('level_zero_based',2),('saved_tick',4),
    ('map_64x64_x2',0x2000),('game_state_5e',0x5e),('runtime_6d60',0x6d60),
    ('runtime_2648',0x2648),('runtime_0a28',0x0a28),('runtime_0580',0x580),('aux_20',0x20),
    ('runtime_150',0x150),('runtime_8',0x8),('runtime_48',0x48),('cell_state_1000',0x1000),
    ('runtime_40',0x40),('runtime_100',0x100),('floor_palette_index',1),('ceiling_palette_index',1),
    ('environment_parameter',2),
]

def le(data, off, n):
    return int.from_bytes(data[off:off+n], 'little')

def inspect_config(path):
    b=Path(path).read_bytes()
    if len(b)!=20:
        raise SystemExit(f'CONFIG.SAV expected 20 bytes, got {len(b)}')
    print('CONFIG.SAV')
    for off,n,name in CONFIG_FIELDS:
        print(f'  {name:24s} = {le(b,off,n)}')

def inspect_user(path):
    b=Path(path).read_bytes()
    print('USER.SAV')
    if len(b)<4:
        raise SystemExit('too small')
    rec=le(b,0,4)
    print(f'  file_size              = {len(b)}')
    print(f'  record_size_header     = {rec} (0x{rec:X})')
    if rec != 0xD6E7:
        print('  WARNING: record size differs from known NITE3W V1.10 layout')
    off=0
    vals={}
    for name,n in USER_PARTS:
        chunk=b[off:off+n]
        if name=='slot_name':
            val=chunk.split(b'\0',1)[0].decode('latin1','replace')
        elif n in (1,2,4):
            val=int.from_bytes(chunk,'little')
        else:
            val=f'{n} bytes'
        vals[name]=val
        print(f'  0x{off:04X} {name:24s} {val}')
        off += n
    print(f'  interpreted level       = E{vals["episode"]}M{vals["level_zero_based"]+1}')

if __name__=='__main__':
    if len(sys.argv)<3:
        print('usage: n3d_save_inspect.py CONFIG.SAV USER.SAV')
        raise SystemExit(2)
    inspect_config(sys.argv[1])
    print()
    inspect_user(sys.argv[2])
