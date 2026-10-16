#!/usr/bin/env python3
"""Original-byte proof for CS:5F3E–5FBE, DOS WORX 2.1 v1.9 and v2.0.

This is not a complete 5F17 streamer; 312E/4741/5A3F, remaining mode
routines, device timing, file errors and port I/O remain injected boundaries.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

HEADER=0x1C00
BUILD={
 'v19':('e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e',171296,0x15BB0),
 'v20':('e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297',171360,0x15BF0),
}
START=0x5F3E
END=0x5FBF
PIN='e215c15813b94fd64f3669f38064b99efca282cb86ccc55a102034f9a7ca1597'
SHIFT=[0x5F40,0x5F45,0x5F4C,0x5F54,0x5F5C,0x5F6E,0x5F7C,0x5F84,
       0x5F8C,0x5F94,0x5F9C,0x5FA7,0x5FB2]
ANCHORS={
 'check_remaining_low':(0x5F3E,'2e a1 df 48'),
 'or_remaining_high':(0x5F42,'2e 0b 06 e1 48'),
 'check_buffered_bytes':(0x5F49,'2e 83 3e ee 48 00'),
 'test_dsp_active':(0x5F51,'2e f6 06 40 47 01'),
 'clear_whole_dsp_flag':(0x5F59,'2e c6 06 40 47 00'),
 'dsp_pause_d0':(0x5F5F,'b0 d0'),
 'out_pic_0a':(0x5F64,'b0 05 e6 0a'),
 'mode_read1_setup':(0x5F68,'bb 01 00 0e 07 bf e3 48'),
 'mode_read1_count_check':(0x5F73,'3d 01 00 75 42'),
 'rem_read3_setup':(0x5F78,'bb 03 00 bf df 48'),
 'mode_0c_first':(0x5F81,'2e 80 3e e3 48 0c'),
 'mode_03_second':(0x5F89,'2e 80 3e e3 48 03'),
 'mode_08_third':(0x5F91,'2e 80 3e e3 48 08'),
 'mode_09_fourth':(0x5F99,'2e 80 3e e3 48 09'),
 'mode_02_fifth':(0x5FA4,'2e 80 3e e3 48 02'),
 'mode_01_sixth':(0x5FAF,'2e 80 3e e3 48 01'),
 'error_close_stc_ret':(0x5FBA,'e8 84 e7 f9 c3'),
}
BRANCHES={
 'nonzero_rem_to_mode':(0x5F47,0x75,0x5F81,2),
 'buffered_to_mode':(0x5F4F,0x75,0x5F81,2),
 'dsp_inactive_skip_stop':(0x5F57,0x74,0x5F68,2),
 'failed_read_to_error':(0x5F76,0x75,0x5FBA,2),
 'mode_0c':(0x5F87,0x74,0x5FD2,2),
 'mode_03':(0x5F8F,0x74,0x5FF3,2),
 'mode_08':(0x5F97,0x74,0x5FBF,2),
 'mode_09_not':(0x5F9F,0x75,0x5FA4,2),
 'mode_09_jump':(0x5FA1,0xE9,0x6092,3),
 'mode_02_not':(0x5FAA,0x75,0x5FAF,2),
 'mode_02_jump':(0x5FAC,0xE9,0x60E8,3),
 'mode_01_not':(0x5FB5,0x75,0x5FBA,2),
 'mode_01_jump':(0x5FB7,0xEB,0x6037,2),
}
CALLS={
 'dsp_5a3f':(0x5F61,0x5A3F),
 'read_mode_312e':(0x5F70,0x312E),
 'read_rem3_312e':(0x5F7E,0x312E),
 'error_close_4741':(0x5FBA,0x4741),
}

def segment(path:Path, build:str)->bytes:
    raw=path.read_bytes()
    if raw[:2]!=b'MZ' or len(raw)<HEADER or struct.unpack_from('<H',raw,8)[0]*16!=HEADER:
        raise ValueError(f'{build}: unexpected MZ header')
    image=raw[HEADER:]
    expected,length,base=BUILD[build]
    if len(image)!=length or hashlib.sha256(image).hexdigest()!=expected:
        raise ValueError(f'{build}: unpacked image SHA/length mismatch')
    return image[base:]

def verify(old:Path,new:Path)->dict:
    a=segment(old,'v19');b=segment(new,'v20')
    digest=hashlib.sha256(b[START:END]).hexdigest()
    if digest!=PIN:raise ValueError('5F3E code-span hash mismatch')
    diffs=[i for i in range(START,END) if a[i+4]!=b[i]]
    if diffs!=SHIFT or any(a[i+4]!=((b[i]+4)&0xFF) for i in diffs):
        raise ValueError('5F3E differs outside exact operand +4 mapping')
    for key,(ip,h) in ANCHORS.items():
        bs=bytes.fromhex(h)
        if b[ip:ip+len(bs)]!=bs:raise ValueError(f'wrong machine anchor {key}')
    edges=[]
    for key,(ip,opcode,dst,width) in BRANCHES.items():
        if b[ip]!=opcode:raise ValueError(f'{key}: wrong branch opcode')
        disp=struct.unpack_from('b' if width==2 else '<h',b,ip+1)[0]
        if ((ip+width+disp)&0xFFFF)!=dst:raise ValueError(f'{key}: incorrect branch target')
        edges.append({'id':key,'ip':f'{ip:04X}','target':f'{dst:04X}'})
    calls=[]
    for key,(ip,dst) in CALLS.items():
        if b[ip]!=0xE8 or (ip+3+struct.unpack_from('<h',b,ip+1)[0])&0xFFFF!=dst:
            raise ValueError(f'{key}: wrong call')
        calls.append({'id':key,'ip':f'{ip:04X}','target':f'{dst:04X}'})
    return {
      'version':'0.16','scope':'stream 5F3E–5FBE local CFG; mode bodies outside; read-only static proof',
      'dos_v19_unpacked_sha256':BUILD['v19'][0],
      'dos_v20_unpacked_sha256':BUILD['v20'][0],
      'span':{'first_ip':f'{START:04X}','end_exclusive':f'{END:04X}',
              'bytes':END-START,'sha256':digest},
      'operand_delta_v19_ip_plus4':[f'{i:04X}' for i in diffs],
      'non_operand_differences':0,
      'anchors':[{'id':k,'ip':f'{ip:04X}','length':len(bytes.fromhex(h))} for k,(ip,h) in ANCHORS.items()],
      'edges':edges,'calls':calls,
      'not_yet_reconstructed':['DOS 312E file read side effects','DSP 5A3F I/O and status timeouts',
        'close 4741','mode 01/02/03/09 continuations','full 5F17 output-buffer fill',
        'CF/IF/DF and stack across transitive callees','IRQ and physical device timing']
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('v19',type=Path);parser.add_argument('v20',type=Path)
    parser.add_argument('--json',type=Path)
    args=parser.parse_args()
    d=verify(args.v19,args.v20)
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True)
        args.json.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'spans':1,'anchors':len(d['anchors']),'branches':len(d['edges']),
                      'calls':len(d['calls']),'operand_shifts':len(d['operand_delta_v19_ip_plus4'])},indent=2))
if __name__=='__main__':main()
