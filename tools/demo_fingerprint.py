#!/usr/bin/env python3
"""Data-only Nitemare 3D MAP/DEMO fingerprint helper.

This intentionally does NOT guess final collision semantics. It extracts the
verified player-start markers (object IDs 1..4), local MAP bytes, forward rays,
and DEMO input timing so candidates can be filtered before exact physics replay.
"""
from __future__ import annotations
import argparse, struct
from pathlib import Path

MAP_HEADER = 514
LEVEL_SIZE = 8192
CELL_COUNT = 4096
DIRS = {0:(0,-1), 90:(1,0), 180:(0,1), 270:(-1,0)}


def load_levels(path: Path):
    data = path.read_bytes()
    count = struct.unpack_from('<H', data, 0)[0]
    return [data[MAP_HEADER+i*LEVEL_SIZE:MAP_HEADER+(i+1)*LEVEL_SIZE] for i in range(count)]


def find_spawn(level: bytes):
    hits=[]
    for n in range(CELL_COUNT):
        obj=level[n*2+1]
        if 1 <= obj <= 4:
            hits.append((n%64,n//64,obj,(obj-1)*90,level[n*2]))
    return hits


def cell(level,x,y):
    if not (0 <= x < 64 and 0 <= y < 64): return None
    o=2*(y*64+x)
    return level[o],level[o+1]


def forward_ray(level,x,y,angle,length=12):
    dx,dy=DIRS[angle]
    return [cell(level,x+dx*k,y+dy*k) for k in range(length)]


def load_demo(path: Path):
    data=path.read_bytes()
    header=struct.unpack_from('<3H',data,0)
    rec=[]
    for o in range(6,len(data),8):
        event=data[o]
        mask=struct.unpack_from('<H',data,o+1)[0]
        pad=data[o+3]
        tick=struct.unpack_from('<I',data,o+4)[0]
        rec.append((tick,event,mask,pad))
    return header,rec


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('directory',type=Path,help='directory containing MAP.1..3 and DEMO.1..3')
    ap.add_argument('--ray',type=int,default=12)
    a=ap.parse_args()
    for ep in (1,2,3):
        for li,level in enumerate(load_levels(a.directory/f'MAP.{ep}'),1):
            sp=find_spawn(level)
            print(f'E{ep}M{li}: spawn={sp}')
            if len(sp)==1:
                x,y,obj,angle,_=sp[0]
                print('  forward:', ' '.join('--' if c is None else f'{c[0]:02X}/{c[1]:02X}' for c in forward_ray(level,x,y,angle,a.ray)))
    for d in (1,2,3):
        h,r=load_demo(a.directory/f'DEMO.{d}')
        uses=sum(1 for _,_,m,_ in r if m & 0x0200)
        fires=sum(1 for _,_,m,_ in r if m & 0x0080)
        print(f'DEMO.{d}: header={h}, records={len(r)}, final_tick={r[-1][0]}, USE-records={uses}, FIRE-records={fires}')
        print('  first:', r[:20])

if __name__=='__main__': main()
