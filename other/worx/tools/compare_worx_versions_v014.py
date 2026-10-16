#!/usr/bin/env python3
"""Pin the 6 selected WORX v2.1 routines across DOS Nitemare v1.9 and v2.0.

v1.9 embedded code is found 0x3C earlier in *MZ image bytes*, while
its old 16-bit memory displacement low bytes are +4 versus v2.0.  This
comparison is restricted to six proven spans; it is NOT global equivalence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

IMAGES={
 'v19':{'sha':'e29a8d058fdf3033241f4f711bca273fb168d750f8f972047e1be8f3d946529e','size':0x29D20},
 'v20':{'sha':'e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297','size':0x29D60},
}
HEADER=0x1C00
V20_BASE=0x15BF0
V19_BASE_EQUIV=V20_BASE-0x3C
# Separate exact original-v1.9 signatures, not recomputed expected values.
SPAN_AND_V19_SHA={
 'midi_gate_44b3':(0x44B3,0x44EE,'ac2b69484bab044d9f5d10f8937b7ea007d902598b9d72a514d0f54e9407c86b'),
 'midi_unknown_meta_4553':(0x4553,0x455D,'7b9fe2b4b9659eec83b5f8eb0edba55120aeaf30a26f4460fc4cba7ae9ffb8da'),
 'midi_eot_458c':(0x458C,0x45DD,'0b43500fd05ee1c5b7d05aa61b45c3cd92142b6375977bb58a9bbbeb5b942bdb'),
 'xms_refill_5863':(0x5863,0x58D8,'8c5bb36c8395ebeb75d8c4ec07c7c1e6d7ba45b919ddd4f23043b3fd6ea10282'),
 'stream_mode08_5fbf':(0x5FBF,0x5FD2,'27478bd2065adecd03c74b130de9e983c46510841375e54d0b4bab89ff5bc1ce'),
 'stream_mode0c_5fd2':(0x5FD2,0x5FF3,'0a9302004106c044b8fbf081335670d5fdb21f66f109d9ede61a788def4f06bd'),
}
# For v1.9, ONLY THESE absolute byte positions differ inside selected bodies.
# In each, the v1.9 memory address low byte is +04h, no wrap in this set.
EXPECTED_V19_SHIFTED_OFFSETS={
 'midi_gate_44b3': [0x44B7,0x44BE,0x44CB,0x44D0,0x44D7,0x44DD,0x44E7,0x44EC],
 'midi_unknown_meta_4553':[],
 'midi_eot_458c':[0x458F,0x4596,0x459D,0x45AE,0x45B6,0x45BE,0x45C2,0x45D7],
 'xms_refill_5863':[0x586F,0x5873,0x5878,0x587D,0x5884,0x588A,0x588E,0x5893,
                     0x5898,0x589D,0x58A6,0x58AA,0x58AF,0x58B4,0x58BB,0x58C1,0x58C6],
 'stream_mode08_5fbf':[0x5FC2,0x5FC7,0x5FCF],
 'stream_mode0c_5fd2':[0x5FD5,0x5FDA,0x5FDF,0x5FE7,0x5FEE],
}

def load_original(path:Path,kind:str)->bytes:
    b=path.read_bytes()
    image=b[HEADER:]
    expected=IMAGES[kind]
    if b[:2]!=b'MZ' or len(image)!=expected['size'] or hashlib.sha256(image).hexdigest()!=expected['sha']:
        raise ValueError(f'not the expected N3D {kind} original expanded image')
    return image

def compare(v19:Path,v20:Path)->dict:
    old=load_original(v19,'v19');new=load_original(v20,'v20')
    # Independent N3D FAR caller proof: old WORX = segment 15BB, offset +4;
    # new WORX = segment 15BF, offset -4. The image shift is precisely -3Ch.
    far_calls={
      'init': (0x11A2E, '9a 81 2e bb 15', 0x11A6A, '9a 7d 2e bf 15'),
      'shutdown': (0x10C30, '9a 6a 2f bb 15', 0x10C6C, '9a 66 2f bf 15'),
    }
    far_evidence=[]
    for name,(a,ahex,b,bhex) in far_calls.items():
        if old[a:a+5]!=bytes.fromhex(ahex) or new[b:b+5]!=bytes.fromhex(bhex):
            raise ValueError(f'cross-version caller mismatch: {name}')
        far_evidence.append({'function':name,'v19_image_at':f'{a:05X}',
                             'v19_call_bytes':ahex,'v20_image_at':f'{b:05X}',
                             'v20_call_bytes':bhex})
    summary=[]
    for name,(lo,hi,pin19) in SPAN_AND_V19_SHA.items():
        aa=old[V19_BASE_EQUIV+lo:V19_BASE_EQUIV+hi]
        bb=new[V20_BASE+lo:V20_BASE+hi]
        if hashlib.sha256(aa).hexdigest()!=pin19:
            raise ValueError(f'v1.9 body byte signature mismatch: {name}')
        changed=[lo+i for i,(a,b) in enumerate(zip(aa,bb)) if a!=b]
        if changed!=EXPECTED_V19_SHIFTED_OFFSETS[name]:
            raise ValueError(f'v1.9/v2.0 unexpected differences: {name}: {changed}')
        for ip in changed:
            if aa[ip-lo] != bb[ip-lo]+4:
                raise ValueError(f'diff not a +4 data-offset operand at {name}/{ip:04X}')
        summary.append({'name':name,'byte_count':hi-lo,'same_bytes':hi-lo-len(changed),
                        'shifted_address_low_bytes':len(changed),
                        'changed_ips':[f'{ip:04X}' for ip in changed]})
    return {'version19_image_sha256':IMAGES['v19']['sha'],
            'version20_image_sha256':IMAGES['v20']['sha'],
            'image_delta':-0x3C,'old_effective_ip_delta':+4,'far_call_proofs':far_evidence,
            'functions':summary,'functions_compared':len(summary),
            'changed_operand_bytes':sum(x['shifted_address_low_bytes'] for x in summary),
            'meaning':'Six selected instruction-body spans are byte-identical after pinning 41 +4 address-low-byte shifts; no proof for transitively called routines.'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('v19',type=Path);p.add_argument('v20',type=Path);p.add_argument('--json',type=Path)
    a=p.parse_args();result=compare(a.v19,a.v20)
    if a.json:
        a.json.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'functions_compared':result['functions_compared'],
                      'changed_operand_bytes':result['changed_operand_bytes'],
                      'all_changes_memory_offset_delta_four':True},indent=2))
if __name__=='__main__':main()
