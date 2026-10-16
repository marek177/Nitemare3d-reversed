#!/usr/bin/env python3
"""RE MAX v0.15: static original-byte identity, CFG and DOS v1.9/v2.0 MIDI event differential.

Works read-only on two proprietary, fully unpacked DOS EXE input paths supplied
by the researcher; neither image is bundled or uploaded to the source repo.

This is evidence for a bounded instruction-local shell. It does NOT certify
indirect 3A4D hardware behavior, IRQ interleaving, full controller dispatch,
open 4265/4389 replay, or complete original runtime 1:1 parity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

BUILD = {
    'v19': {'sha': 'e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e',
            'length': 171296, 'base': 0x15BB0, 'ip_shift': 4},
    'v20': {'sha': 'e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297',
            'length': 171360, 'base': 0x15BF0, 'ip_shift': 0},
}
HEADER = 0x1C00
SPANS = {
    'v20_channel_shell': (0x44EE,0x4553,'076f7d28f35cb4698837258c227d45cfbfd66768f4e962af8ecc55965a032e43'),
    'v20_dispatch_prefix':(0x3A4D,0x3A6F,'4f9f432eebb7b3fad17fb6f78d7326be3b91e7a13346a91c289b652aa20b2785'),
    'v20_ff_meta_prefix':(0x4546,0x4553,'34e9254bf4fe3bac4d2e6357d1202e61f17dc1b2331e9635de5f5f7cdf2ec73c'),
    'v20_nibble_parameter_table':(0x2DA4,0x2DB4,'d26fc4d220107edf18cf2cb41451a4cecb3ddcded0a0647b38dbf9950e6285c2'),
}
ANCHORS = {
 'ff_precedes_status_bit':(0x44F1,'3c ff 74 51 a8 80 74 06'),
 'status_cache_word_store':(0x44F9,'2e 89 87 63 2d 47'),
 'running_status_load':(0x44FF,'2e 8b 87 63 2d'),
 'status_high_nibble':(0x4504,'32 e4 b1 04 d3 e8 8b f0'),
 'status_parameter_table':(0x450C,'2e 8a 8c a4 2d 32 ed'),
 'cached_ax_for_dispatch':(0x4513,'2e 8b 87 63 2d'),
 'first_data_bh':(0x4518,'e3 0b 26 8a 3d 47 49 e3 04'),
 'second_data_bl':(0x4521,'26 8a 1d 47'),
 'call_3a4d':(0x4525,'e8 25 f5'),
 'call_45f9':(0x4528,'e8 ce 00'),
 'reload_index_after_callbacks':(0x452B,'2e 8b 1e c0 2d d1 e3'),
 'write_cursor':(0x4532,'2e 89 bf 22 2d'),
 'write_delta_low':(0x4539,'2e 89 87 a2 2c'),
 'write_delta_high':(0x453E,'2e 89 97 a4 2c'),
 'reenter_44b4':(0x4543,'e9 6e ff'),
 'ff_meta_type':(0x4546,'47 26 8a 05 47 3c 2f 74 3d 3c 51 74 0a'),
 'dispatch_split_status':(0x3A4D,'8a e0 80 e4 f0 24 0f'),
 'dispatch_write_channel':(0x3A54,'2e a2 c4 2d'),
 'dispatch_write_status':(0x3A58,'2e 88 26 c8 2d'),
 'dispatch_write_data_bh':(0x3A5D,'2e 88 3e c5 2d'),
 'dispatch_write_data_bl':(0x3A62,'2e 88 1e c6 2d'),
 'dispatch_gate_to_nested_3a67':(0x3A67,'2e f6 06 bc 2d 06 75 3c'),
}
BRANCH = {
 'ff_JE':(0x44F3,2,0x4546),
 'running_JE':(0x44F7,2,0x44FF),
 'no_params_JCXZ':(0x4518,2,0x4525),
 'one_param_JCXZ':(0x451F,2,0x4525),
 'meta_EOT_JE':(0x454D,2,0x458C),
 'meta_tempo_JE':(0x4551,2,0x455D),
 'reenter_JMP':(0x4543,3,0x44B4),
}
DIRECT_CALL = {'dispatch_3a4d':(0x4525,0x3A4D),'delta_vlq_45f9':(0x4528,0x45F9)}
# Byte positions in v2.0 IP-space where the v1.9 relocated data operands
# differ. All of them satisfy old_byte == (new_byte+4)&0xFF.
EXPECTED_SHIFTED = {
    'channel_shell': [0x44FC,0x4502,0x450F,0x4516,0x452E,0x4535,0x453C,0x4541],
    'dispatch_prefix': [0x3A56,0x3A5B,0x3A60,0x3A65,0x3A6A],
    'meta_prefix': [],
}
PARAM_COUNTS=bytes([0,0,0,0,0,0,0,0,2,2,2,2,1,1,2,0])


def image(path:Path, build:str)->bytes:
    raw=path.read_bytes()
    if raw[:2]!=b'MZ' or len(raw)<HEADER+1 or struct.unpack_from('<H',raw,8)[0]*16!=HEADER:
        raise ValueError(f'{build}: not original unpacked MZ with 0x1C00 header')
    data=raw[HEADER:]
    if len(data)!=BUILD[build]['length'] or hashlib.sha256(data).hexdigest()!=BUILD[build]['sha']:
        raise ValueError(f'{build}: image bytes/hash do not match pinned original')
    return data


def verify(v19:Path,v20:Path)->dict:
    i19=image(v19,'v19');i20=image(v20,'v20')
    old=i19[BUILD['v19']['base']:BUILD['v19']['base']+65536]
    new=i20[BUILD['v20']['base']:BUILD['v20']['base']+65536]
    spans=[]
    for name,(lo,hi,digest) in SPANS.items():
        actual=hashlib.sha256(new[lo:hi]).hexdigest()
        if actual!=digest:raise ValueError(f'{name}: original hash drift')
        spans.append({'id':name,'ip_start':f'{lo:04X}','ip_end_exclusive':f'{hi:04X}',
                      'length':hi-lo,'sha256':actual})
    anchors=[]
    for name,(ip,hexbytes) in ANCHORS.items():
        want=bytes.fromhex(hexbytes)
        if new[ip:ip+len(want)]!=want:raise ValueError(f'{name}: original opcode anchor changed')
        anchors.append({'id':name,'ip':f'{ip:04X}','signature':hexbytes})
    edges=[]
    for name,(ip,width,target) in BRANCH.items():
        if width==2:
            opcode=new[ip]
            if opcode not in (0x74,0x75,0xE3):raise ValueError(f'{name}: wrong conditional')
            offset=struct.unpack_from('b',new,ip+1)[0]
        else:
            if new[ip]!=0xE9:raise ValueError(f'{name}: wrong jump opcode')
            offset=struct.unpack_from('<h',new,ip+1)[0]
        landed=(ip+width+offset)&0xFFFF
        if landed!=target:raise ValueError(f'{name}: branch target {landed:04X}')
        edges.append({'id':name,'from_ip':f'{ip:04X}','target':f'{landed:04X}'})
    calls=[]
    for name,(ip,target) in DIRECT_CALL.items():
        if new[ip]!=0xE8:raise ValueError(f'{name}: not near CALL')
        disp=struct.unpack_from('<h',new,ip+1)[0]
        landed=(ip+3+disp)&0xFFFF
        if landed!=target:raise ValueError(f'{name}: CALL target mismatch {landed:04X}')
        calls.append({'id':name,'from_ip':f'{ip:04X}','target':f'{landed:04X}'})
    tab=new[0x2DA4:0x2DB4]
    if tab!=PARAM_COUNTS or old[0x2DA8:0x2DB8]!=tab:
        raise ValueError('status-nibble parameter length table mismatch')
    comparisons=[]
    for name,(lo,hi) in {'channel_shell':(0x44EE,0x4553),
                         'dispatch_prefix':(0x3A4D,0x3A6F),
                         'meta_prefix':(0x4546,0x4553)}.items():
        expect=EXPECTED_SHIFTED[name]
        differences=[lo+n for n,(a,b) in enumerate(zip(old[lo+4:hi+4],new[lo:hi])) if a!=b]
        if differences!=expect:raise ValueError(f'{name}: new crossversion divergence {differences}')
        for ip in differences:
            if old[ip+4]!=(new[ip]+4)&0xFF:
                raise ValueError(f'{name}: nonreloc difference {ip:04X}')
        comparisons.append({'id':name,'v20_start_ip':f'{lo:04X}',
                            'v19_start_ip':f'{lo+4:04X}',
                            'bytes_compared':hi-lo,
                            'modified_operand_ips':[f'{ip:04X}' for ip in differences],
                            'non_operand_differences':0})
    return {'version':'0.15','domain':'original unpacked DOS MZ image bytes, not run-time CS:IP',
            'original_v19_sha256':BUILD['v19']['sha'],
            'original_v20_sha256':BUILD['v20']['sha'],
            'cs_base_v19':f"{BUILD['v19']['base']:05X}",
            'cs_base_v20':f"{BUILD['v20']['base']:05X}",
            'v19_ip_minus_v20_ip':4,
            'status_nibble_data_length':list(tab),
            'v20_spans':spans,'v20_anchors':anchors,
            'v20_branch_targets':edges,'v20_near_calls':calls,
            'crossversion_matches':comparisons,
            'proof_boundary':['Original bytes/straight-line branch shells only',
               '3A4D hardware or software downstream after 3A67 explicitly injected',
               'Actual caller DX/DS/FLAGS, IRQ and callback nonreturn behavior not certified',
               'Out-of-range track/global alias tests are synthetic, not reachability proof',
               'Single-event model stops at JMP 44B4; zero-delta recursive scheduling open',
               'No source binaries bundled or published']}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_v19',type=Path)
    p.add_argument('original_v20',type=Path)
    p.add_argument('--json',type=Path)
    args=p.parse_args()
    result=verify(args.original_v19,args.original_v20)
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True)
        args.json.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'spans':len(result['v20_spans']),
                       'anchors':len(result['v20_anchors']),
                       'branches':len(result['v20_branch_targets']),
                       'calls':len(result['v20_near_calls']),
                       'operand_differences':sum(len(x['modified_operand_ips']) for x in result['crossversion_matches'])},indent=2))

if __name__=='__main__':main()
