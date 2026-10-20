#!/usr/bin/env python3
"""D02-N SHA-bound original DOS2 4-pass VEC producer/static call-graph oracle.

Direct opcode contracts only; no executable, original assets or runtime dump
are redistributed. These checks do NOT certify indirect writers, unknown
resource tables, DOS/Win cross-parity, or actual full-pool reproduction.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

SHA='552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301'
FILE_BYTES=116606
HEADER_BYTES=512
WINDOWS={
0x32e2:'576633c0bb06e0',          # level startup clears data fields
0x3304:'9a1c0ed90f',            # far VEC builder
0x3309:'9a5e00d90f',            # far VEC list partition/sorter
0x10592:'558bec8b4608',         # door-orientation dispatcher
0x105a3:'2effa71808',           # CS door jump table
0x105ea:'c80600005756',         # ordinary VEC init
0x105fc:'880432d2885403',       # +00 and +03 writes
0x1060a:'8a870ed3884406',       # +06 wall class
0x10611:'8a870cd0884405',       # +05 wall flags
0x10618:'8a4610884407',         # +07 VEC orientation
0x1061e:'66c7440800000000',     # +08 DWORD 0
0x106f2:'c80400005756',         # door VEC helper
0x10701:'880532c9884d01',       # special id and ordinal reset
0x10854:'558bec568b5606',       # prior VEC extend helper
0x10892:'c81c00005756',         # per-orientation producer
0x108b9:'8b46e603460a',         # currentCount + baseCount
0x108bf:'3de803',               # 1000 limit
0x108d2:'b8fd218ec0',           # original map segment ES=21FD
0x10971:'8bd9c1e30603df03db', # 64*y + x, 2 bytes per map cell
0x1097d:'268a873e37',           # read WALL byte
0x109d3:'268a9f3e37',           # read adjacent WALL byte
0x109dd:'32870cd0',             # XOR wall properties
0x109e1:'2408',                 # property bit 08 difference
0x109ef:'8a870cd0',             # current wall props
0x109f3:'2410',                 # wall property 0x10
0x10a1f:'268a9f3f37',           # read OBJECT byte
0x10a26:'80bf0ed403',           # OBJECT class 3
0x10a7c:'268a873f37',           # read adjacent OBJECT byte
0x10ab3:'f6870cd004',           # wall property bit04 builder gate
0x10abd:'f6870cd004',           # neighbor wall property bit04
0x10af4:'6b46e61c',             # previous VEC 28B stride
0x10b01:'e850fd',               # previous VEC extend
0x10b0a:'8b7ee6ff46e6',        # new VEC and count++
0x10b19:'6bc71c',               # currentCount*28
0x10b25:'e8c2fa',               # near ordinary VEC builder
0x10b43:'e84cfa',               # near door class orientation gate
0x10b6a:'e885fb',               # near special door builder
0x10b8e:'ff46f2',               # inner++
0x10b91:'837ef240',             # 64 map cells inner
0x10b99:'ff46ec',               # outer++
0x10b9c:'837eec40',             # 64 map cells outer
0x10bac:'566a0068ac62',         # four-pass outer builder
0x10bb5:'e8dafc',               # pass 0
0x10bc8:'e8c7fc',               # pass 1
0x10bdb:'e8b4fc',               # pass 2
0x10bee:'e8a1fc',               # pass 3
0x10bf6:'89366e62',             # only literal DS:626E writer
0xfda6:'558bec5756',           # original sort comparator
0xfdde:'8b450e39470e',         # alternate coordinate key Y
0xfdee:'575633ff',             # group/sort setup
0xfdf2:'893efe57',             # reset orientation2 count
0xfdfa:'893efc57',             # reset orientation1 count
0xfdfe:'893efa57',             # reset orientation0 count
0xfe02:'beac62',               # iterate VEC pool
0xfe2c:'ff06fa57',             # orientation0 count++
0xfe3c:'ff06fc57',             # orientation1 count++
0xfe4c:'ff06fe57',             # orientation2 count++
0xfe5c:'ff060058',             # orientation3 count++
0xfe60:'813efa574d01',         # 333-item array bound
}


def target_near(load:bytes,off:int)->int:
    if off<0 or off+3>len(load) or load[off]!=0xe8:
        raise ValueError("Invalid or truncated near CALL")
    delta=struct.unpack_from('<h',load,off+1)[0]
    return off+3+delta

def target_far(load:bytes,off:int)->int:
    if off<0 or off+5>len(load) or load[off]!=0x9a:
        raise ValueError("Invalid or truncated far CALL")
    ip,seg=struct.unpack_from('<HH',load,off+1)
    return 16*seg+ip

def audit_file(filename:Path)->dict:
    entire=filename.read_bytes()
    digest=hashlib.sha256(entire).hexdigest()
    if digest!=SHA or len(entire)!=FILE_BYTES or entire[:2]!=b'MZ':
        raise ValueError(f'Original DOS2 identity mismatch sha={digest} bytes={len(entire)}')
    load=entire[HEADER_BYTES:]
    for off,p in WINDOWS.items():
        expected=bytes.fromhex(p)
        observed=load[off:off+len(expected)]
        if observed!=expected:
            raise ValueError(f'Original opcode differs at {off:05X}: {observed.hex()} != {p}')
    edges={
       0x3304:0x10bac, 0x3309:0xfdee,
       0x10b01:0x10854, 0x10b25:0x105ea,
       0x10b43:0x10592, 0x10b6a:0x106f2,
       0x10bb5:0x10892, 0x10bc8:0x10892,
       0x10bdb:0x10892, 0x10bee:0x10892,
    }
    for off,target in edges.items():
        actual=target_far(load,off) if load[off]==0x9a else target_near(load,off)
        if actual!=target:
            raise ValueError(f'CALL target differs at {off:05X} -> {actual:05X}')
    entries=[]
    csbase=0xFD90
    for i in range(16):
        local=struct.unpack_from('<H',load,0x105a8+2*i)[0]
        normalized=csbase+local
        if normalized!=(0x105cc if i%2==0 else 0x105da):
            raise ValueError(f'Unexpected door orientation table entry {i}')
        entries.append({'wall_class':f'0x{0x31+i:02X}','branch':f'0x{normalized:05X}',
                        'orientation':'2/3' if i%2==0 else '0/1'})
    # literal DS:626E operand census, not comprehensive indirect/alias writers
    locations=[i-2 for i in range(len(load)-1) if load[i:i+2]==b'\x6e\x62']
    writers=[i for i in locations if i>=0 and load[i:i+4]==bytes.fromhex('89366e62')]
    if writers!=[0x10bf6]:
        raise ValueError('unexpected literal absolute DS:626E write')
    return {'build':'DOS 2.0 unpacked EXE', 'sha256':digest,
            'opcode_windows':len(WINDOWS),'direct_call_edges':len(edges),
            'count_literal_refs':len(locations),'count_literal_writer':['0x10BF6'],
            'passes':[{'orientation':i,'call':f'0x{off:05X}'} for i,off in enumerate((0x10bb5,0x10bc8,0x10bdb,0x10bee))],
            'map_dimensions':'64x64','map_cell_bytes':2,
            'vec_stride_bytes':28,'vec_max_records':1000,
            'next_sort_function':'0xFDEE','sort_comparator':'0xFDA6',
            'door_orientation_table':entries,
            'evidence_class':'VERIFIED ORIGINAL STATIC (bounded)',
            'original_game_executed_in_this_pass':False,
            'full_vec_source_parity_verified':False,
            'resource_runtime_tables_verified':False,
            'pixel_parity_verified':False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('exe',type=Path)
    parser.add_argument('--json',type=Path)
    args=parser.parse_args()
    d=audit_file(args.exe)
    if args.json:
        args.json.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
    print(f"PASS D02-N: {d['opcode_windows']} ASM windows, {d['direct_call_edges']} CALL edges; 4 producer passes")
if __name__=='__main__':main()
