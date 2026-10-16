#!/usr/bin/env python3
"""WORX 2.1 v0.16: original DOS 1.9/2.0 CS:3A67-3B03,58F8-5925.

Read-only, SHA-gated static verifier. Tracks ALL locally enumerated jumps
and direct CALLs in these two spans. Far callback/port hardware, indirect
callee bodies, timing and guest FLAGS remain separate acceptance layers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

MZ_HEADER=0x1C00
BUILDS={
    'v19':{'image_sha256':'e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e',
           'length':171296,'cs_base':0x15BB0,'ip_adjust':4},
    'v20':{'image_sha256':'e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297',
           'length':171360,'cs_base':0x15BF0,'ip_adjust':0},
}
SPANS={
    'route_3a67_3b03':(0x3A67,0x3B04,'c056659b00258130f31a046144b03c67614ce0182810caba9d5ecd7d7319be0f'),
    'mpu_58f8_5925':(0x58F8,0x5926,'50ebb3fae7469934ad36d21c4805aacf9f098c4c6fb01cac2d152e3ed56facbe'),
}
# Addresses in the v2.0 WORX code segment; all opcode signatures are byte-pinned.
ANCHORS={
    'route_test':(0x3A67,'2e f6 06 bc 2d 06 75 3c'),
    'save_live_frame':(0x3A6F,'0e 1f 50 51 56'),
    'status_nibble_to_si':(0x3A74,'8a c4 32 e4 b1 04 d3 e8 8b f0'),
    'table_to_cx':(0x3A7E,'2e 8a 8c a4 2d 32 ed'),
    'no_data_gate':(0x3A85,'e3 20'),
    'status_from_globals':(0x3A87,'2e a0 c8 2d 2e 0a 06 c4 2d'),
    'status_call':(0x3A90,'e8 65 1e'),
    'data1_gate':(0x3A93,'e3 12 49'),
    'data1_from_global':(0x3A96,'2e a0 c5 2d'),
    'data1_call':(0x3A9A,'e8 5b 1e'),
    'data2_gate':(0x3A9D,'e3 08 49'),
    'data2_from_global':(0x3AA0,'2e a0 c6 2d'),
    'data2_call':(0x3AA4,'e8 51 1e'),
    'restore_frame_ret':(0x3AA7,'5e 59 58 c3'),
    'status_90_unsigned':(0x3AAB,'2e 80 3e c8 2d 90'),
    'status_b0_unsigned':(0x3AB3,'2e 80 3e c8 2d b0'),
    'status_c0_unsigned':(0x3AC1,'2e 80 3e c8 2d c0'),
    'pitch_gate':(0x3ACF,'2e f6 06 c9 2d 20'),
    'config_mode':(0x3AD7,'2e 80 3e 4d 2b 01'),
    'channel_09':(0x3ADF,'2e 80 3e c4 2d 09'),
    'channel_0b':(0x3AEA,'2e 80 3e c4 2d 0b'),
    'pitch_add_8bit':(0x3AF2,'2e a0 c5 2d 2e 02 06 a3 2d 2e a2 c5 2d'),
    'fm_call':(0x3AFF,'e8 59 00'),
    'clc_ret':(0x3B02,'f8 c3'),
    'mpu_save':(0x58F8,'50 51 52 8a e0 b9 ff ff ba 31 03'),
    'mpu_early_limit':(0x5903,'e3 1d 49 ec a8 40 75 f8'),
    'mpu_write':(0x590B,'8a c4 ba 30 03 ee'),
    'mpu_restore':(0x5911,'5a 59 58'),
    'callback_segment_gate':(0x5914,'2e 83 3e 98 38 00 74 05'),
    'callback_far_call':(0x591C,'2e ff 1e 96 38'),
    'success_ret':(0x5921,'c3'),
    'timeout_restore_ret':(0x5922,'5a 59 58 c3'),
}
# All local direct control transfers/conditional branches in two spans.
BRANCHES={
 '3a6d_jne':(0x3A6D,0x75,0x3AAB),
 '3a85_jcxz':(0x3A85,0xE3,0x3AA7),
 '3a93_jcxz':(0x3A93,0xE3,0x3AA7),
 '3a9d_jcxz':(0x3A9D,0xE3,0x3AA7),
 '3ab1_jbe':(0x3AB1,0x76,0x3ACF),
 '3ab9_ja':(0x3AB9,0x77,0x3AC1),
 '3abe_jmp':(0x3ABE,0xEB,0x3B02),
 '3ac7_ja':(0x3AC7,0x77,0x3B02),
 '3acc_jmp':(0x3ACC,0xEB,0x3B02),
 '3ad5_je':(0x3AD5,0x74,0x3AF2),
 '3add_jne':(0x3ADD,0x75,0x3AEA),
 '3ae5_je':(0x3AE5,0x74,0x3AFF),
 '3ae7_jmp':(0x3AE7,0xEB,0x3AF2),
 '3af0_jae':(0x3AF0,0x73,0x3AFF),
 '5903_jcxz':(0x5903,0xE3,0x5922),
 '5909_jne':(0x5909,0x75,0x5903),
 '591a_je':(0x591A,0x74,0x5921),
}
CALLS={
 'status_mpu':(0x3A90,0x58F8),
 'data1_mpu':(0x3A9A,0x58F8),
 'data2_mpu':(0x3AA4,0x58F8),
 'type_3941':(0x3ABB,0x3941),
 'type_3e34':(0x3AC9,0x3E34),
 'type_3b5b':(0x3AFF,0x3B5B),
}
SHIFTS={
 'route_3a67_3b03': [0x3A6A,0x3A81,0x3A89,0x3A8E,0x3A98,0x3AA2,
                       0x3AAE,0x3AB6,0x3AC4,0x3AD2,0x3ADA,0x3AE2,
                       0x3AED,0x3AF4,0x3AF9,0x3AFD],
 'mpu_58f8_5925':[0x5917,0x591F],
}

def extract_image(path:Path, build:str)->bytes:
    raw=path.read_bytes()
    if raw[:2]!=b'MZ' or len(raw)<MZ_HEADER+1 or struct.unpack_from('<H',raw,8)[0]*16!=MZ_HEADER:
        raise ValueError(f'{build}: expected original fully unpacked MZ with 0x1C00 header')
    image=raw[MZ_HEADER:]
    want=BUILDS[build]
    if len(image)!=want['length'] or hashlib.sha256(image).hexdigest()!=want['image_sha256']:
        raise ValueError(f'{build}: wrong original image hash or length')
    return image

def verify(old_exe:Path,new_exe:Path)->dict:
    old=extract_image(old_exe,'v19')
    new=extract_image(new_exe,'v20')
    old=old[BUILDS['v19']['cs_base']:]
    new=new[BUILDS['v20']['cs_base']:]
    span_report=[]
    for key,(first,last,expected_hash) in SPANS.items():
        sha=hashlib.sha256(new[first:last]).hexdigest()
        if sha!=expected_hash:raise ValueError(f'original code span changed: {key}')
        shifted=SHIFTS[key]
        differences=[i for i in range(first,last) if old[i+4]!=new[i]]
        if differences!=shifted:raise ValueError(f'cross-version bytes diverged outside relocation positions: {key}: {differences}')
        if any(old[i+4]!=((new[i]+4)&0xFF) for i in shifted):
            raise ValueError(f'{key}: shifted operands are not exactly +4')
        span_report.append({'id':key,'ip_start':f'{first:04X}','ip_end_exclusive':f'{last:04X}',
                            'length':last-first,'sha256':sha,
                            'relocated_low_operand_ips':[f'{ip:04X}' for ip in differences],
                            'other_changed_bytes':0})
    anchors=[]
    for label,(ip,hexval) in ANCHORS.items():
        signature=bytes.fromhex(hexval)
        if new[ip:ip+len(signature)]!=signature:raise ValueError(f'{label}: opcode anchor mismatch')
        anchors.append({'name':label,'ip':f'{ip:04X}','bytes':len(signature)})
    branches=[]
    for label,(ip,opcode,target) in BRANCHES.items():
        if new[ip]!=opcode:raise ValueError(f'{label}: wrong branch opcode')
        displ=struct.unpack_from('b',new,ip+1)[0]
        actual=(ip+2+displ)&0xFFFF
        if actual!=target:raise ValueError(f'{label}: branch target mismatch {actual:04X}')
        branches.append({'name':label,'ip':f'{ip:04X}','target':f'{target:04X}'})
    calls=[]
    for label,(ip,target) in CALLS.items():
        if new[ip]!=0xE8:raise ValueError(f'{label}: no near CALL')
        disp=struct.unpack_from('<h',new,ip+1)[0]
        actual=(ip+3+disp)&0xFFFF
        if actual!=target:raise ValueError(f'{label}: wrong CALL target {actual:04X}')
        calls.append({'name':label,'ip':f'{ip:04X}','target':f'{target:04X}'})
    return {
        'version':'0.16','provenance':'unpacked, original MZ image with code segment CS; static only',
        'v19_sha256_image':BUILDS['v19']['image_sha256'],
        'v20_sha256_image':BUILDS['v20']['image_sha256'],
        'v19_to_v20_ip_shift':4,
        'machine_spans':span_report,'opcode_anchors':anchors,'local_branches':branches,
        'near_calls':calls,'far_indirect':{'ip':'591C','pointer_offset':'3896','pointer_segment':'3898'},
        'original_mpu_poll_limit':65535,
        'closure':'local 3A67 routing + bounded 58F8 port loop; NOT child 3941/3E34/3B5B, callback hardware, IRQ, flags, timing',
        'corrected_v015_callback_ax':'3A4D rewrites original cached status AL to AH=status&F0 and AL=status&0F before 3A67',
        'not_proven':['hardware port IO conditions','indirect 3896 target semantics','3B5B FM/PC speaker subtree',
                      'MIDI device and global event interleaving','full FLAGS and private IRQ stack',
                      'input reachability of out-of-range values','byte-perfect real audio output'],
    }

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('v19',type=Path);parser.add_argument('v20',type=Path)
    parser.add_argument('--json',type=Path)
    args=parser.parse_args()
    report=verify(args.v19,args.v20)
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True)
        args.json.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    print(json.dumps({'spans':len(report['machine_spans']),
                       'anchors':len(report['opcode_anchors']),
                       'branches':len(report['local_branches']),
                       'calls':len(report['near_calls']),
                       'operand_shifts':sum(len(x['relocated_low_operand_ips']) for x in report['machine_spans'])},indent=2))
if __name__=='__main__':main()
