#!/usr/bin/env python3
"""Independent static pins for v0.14 WORX subroutines in original N3D DOS v2.0.

IMPORTANT: This verifies bytes, selected direct targets, and written code
contracts. It does not perform generic symbolic execution or certify nested
DOS/XMS/MIDI/IRQ hardware behavior.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

EXPECTED_IMAGE_SHA256 = 'e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
IMAGE_LENGTH = 0x29D60
HEADER_LENGTH = 0x1C00
CS_BASE = 0x15BF0
SLICES = {
  'midi_gate_44b3_44ed': (0x44B3, 0x44EE, '1b6482491c7267a330479d74304ec06b8dc6c91e92238760ae3557e184402485'),
  'midi_unknown_meta_4553_455c': (0x4553, 0x455D, '7b9fe2b4b9659eec83b5f8eb0edba55120aeaf30a26f4460fc4cba7ae9ffb8da'),
  'midi_eot_458c_45dc': (0x458C, 0x45DD, 'e806807be301665d3c35bfcc2c0e0774a8ac27cb20246d2907a41101d11d4c9e'),
  'xms_refill_5863_58d7': (0x5863, 0x58D8, 'cfc64ac08866c393dac6fd301c37d021ef7cda6468a425f06cc6e85541de2cdb'),
  'stream_mode08_5fbf_5fd1': (0x5FBF, 0x5FD2, 'ca04bd29d8fc3d621a02f0479dc3a679454be4722ea68d266ab0151e42701d50'),
  'stream_mode0c_5fd2_5ff2': (0x5FD2, 0x5FF3, 'f02fe09047cee6b1f211a92abbe8fbca88fc7046a9978fccf03a0fa7b248952f'),
}
ANCHORS = {
 'gate_push_cx':(0x44B3,'51'),
 'gate_active_bit':(0x44BB,'2e f7 87 62 2c 01 00'),
 'gate_delta_low_or_high':(0x44C8,'2e 8b 87 a2 2c 2e 0b 87 a4 2c'),
 'gate_delta_sub_sbb':(0x44D4,'2e 83 af a2 2c 01 2e 83 9f a4 2c 00'),
 'gate_esdi':(0x44E4,'2e 8b bf 22 2d 2e 8e 06 5f 2c'),
 'meta_skip_length_one_byte':(0x4553,'32 e4 26 8a 05 47 03 f8'),
 'eot_clear_current':(0x458C,'2e c7 87 62 2c 00 00'),
 'eot_scan_ffff':(0x459A,'2e f7 87 62 2c ff ff'),
 'eot_global_index_not_found_bx':(0x45AB,'2e ff 06 c0 2d'),
 'eot_replay_indicator':(0x45B3,'2e 80 3e 61 2c 00'),
 'eot_mode_one':(0x45C4,'3c 01 74 06'),
 'eot_stop_music':(0x45D4,'2e c6 06 62 2d 00'),
 'xms_register_saves':(0x5863,'50 53 51 52 56'),
 'xms_dest_256_stride':(0x5868,'8b c3 d1 e8 86 e0 05 ed 4c'),
 'xms_packet_length':(0x587A,'2e c7 06 cc 21 00 01'),
 'xms_prior_cursor':(0x5890,'2e 8b 87 cf 4b 2e 89 87 ed 54'),
 'xms_address_add_carry':(0x58A3,'2e 03 87 c6 20 2e a3 d2 21'),
 'xms_no_previous_high_word':(0x58B1,'2e c7 06 d4 21 00 00 2e 11 06 d4 21'),
 'xms_far_callback':(0x58BD,'b4 0b 8d 36 cc 21 2e ff 1e c8 21'),
 'xms_cmp_service_ax':(0x58C8,'3d 01 00 74 03 b8 00 00'),
 'xms_pop_orig_ax':(0x58D0,'0e 1f 5e 5a 59 5b 58 c3'),
 'stream_08_call_312e':(0x5FBF,'2e 8b 1e df 48 0e 07 bf 69 5e e8 62 d1'),
 'stream_08_only_low_sub':(0x5FCC,'2e 29 06 df 48 c3'),
 'stream_0c_sub_sbb':(0x5FD2,'2e 8b 0e db 48 2e 29 0e df 48 2e 83 1e e1 48 00'),
 'stream_0c_zero_on_borrow':(0x5FE4,'2e c7 06 df 48 00 00 2e c7 06 e1 48 00 00'),
}
# address, x86 instruction length, expected absolute 16-bit code target
EDGES = {
 'gate_active_JNE': (0x44C2,2,0x44C6),
 'gate_no_delta_JE': (0x44D2,2,0x44E2),
 'eot_next_track_LOOP': (0x45A6,2,0x459A),
 'eot_other_active_JNE': (0x45A1,2,0x45AB),
 'eot_repeat_JE': (0x45B9,2,0x45D4),
 'eot_replay_mode_JE': (0x45C6,2,0x45CE),
 'eot_reenter_44b4': (0x45B0,3,0x44B4),
 'eot_replay_4265_JMP': (0x45CB,3,0x44B4),
 'eot_replay_4389_JMP': (0x45D1,3,0x44B4),
 'eot_stop_JMP':(0x45DA,3,0x44B4),
 'stream_zero_on_borrow_JAE':(0x5FE2,2,0x5FF2),
}

def load_original(exe: Path) -> bytes:
    b=exe.read_bytes()
    if len(b)!=HEADER_LENGTH+IMAGE_LENGTH or b[:2]!=b'MZ' or struct.unpack_from('<H',b,8)[0]*16!=HEADER_LENGTH:
        raise ValueError('Not original fully expanded N3D DOS v2.0 MZ image')
    image=b[HEADER_LENGTH:]
    if hashlib.sha256(image).hexdigest()!=EXPECTED_IMAGE_SHA256:
        raise ValueError('Original N3D DOS v2.0 image hash mismatch')
    return image

def audit(exe:Path)->dict:
    image=load_original(exe)
    segment=image[CS_BASE:CS_BASE+65536]
    slices=[]
    for name,(lo,hi,expected_sha) in SLICES.items():
        blob=segment[lo:hi]
        digest=hashlib.sha256(blob).hexdigest()
        if digest!=expected_sha: raise ValueError(f'Unexpected machine bytes in {name}')
        slices.append({'id':name,'start_ip':f'{lo:04X}','end_exclusive':f'{hi:04X}',
                       'bytes':len(blob),'sha256':digest})
    anchors=[]
    for name,(ip,hex_bytes) in ANCHORS.items():
        want=bytes.fromhex(hex_bytes)
        if segment[ip:ip+len(want)]!=want: raise ValueError(f'Opcode mismatch: {name}')
        anchors.append({'id':name,'ip':f'{ip:04X}','bytes':hex_bytes})
    edges=[]
    for name,(ip,length,target) in EDGES.items():
        if length==2:
            opcode=segment[ip]
            if opcode not in (0x72,0x73,0x74,0x75,0x76,0x77,0xE2):
                raise ValueError(f'{name}: invalid short-branch opcode {opcode:02x}')
            disp=struct.unpack_from('b',segment,ip+1)[0]
        elif length==3:
            if segment[ip]!=0xE9: raise ValueError(f'{name}: not near JMP')
            disp=struct.unpack_from('<h',segment,ip+1)[0]
        else: raise AssertionError(length)
        landed=(ip+length+disp)&0xFFFF
        if landed!=target: raise ValueError(f'{name}: {landed:04X} != {target:04X}')
        edges.append({'id':name,'from_ip':f'{ip:04X}','to_ip':f'{landed:04X}'})
    return {'image_sha256':EXPECTED_IMAGE_SHA256,'target':'unpacked N3D DOS v2.0 / WORX 2.1',
            'proofs':{'slices':slices,'anchors':anchors,'branch_targets':edges},
            'new_static_subcontracts':list(SLICES),
            'limitations':['Selected straight-line and local branch subcontracts, not full transitive CFG',
                           'XMS/DOS external services and original IRQ timing not emulated',
                           'Complete MIDI 3A4D, 4265, 4389 and streaming modes 01/02/03/09 remain open',
                           '41/79 previously audited non-null INT63 handler count remains unchanged']}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('original_mz',type=Path)
    p.add_argument('--json',type=Path)
    a=p.parse_args()
    result=audit(a.original_mz)
    if a.json:
        a.json.parent.mkdir(parents=True,exist_ok=True)
        a.json.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'sha256':result['image_sha256'],'slices':len(result['proofs']['slices']),
                      'anchors':len(result['proofs']['anchors']),
                      'branches':len(result['proofs']['branch_targets'])},indent=2))
if __name__=='__main__': main()
