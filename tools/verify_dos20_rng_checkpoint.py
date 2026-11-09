"""Read-only, opt-in static RNG census. No original game bytes distributed."""
import argparse,hashlib,json,struct
EXPECTED_IMAGE='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
EXPECTED_SITES=[int(x,16) for x in '2478 525E 5582 5666 56A6 573F 58A7 85AD 8860 886C 887C 9A68 9A77 9C98 9CC2 9D6E 9F0C 9F36 9FE3 A047 A12B B276'.split()]
def verify(raw):
 if len(raw)<28 or raw[:2]!=b'MZ':raise ValueError('Expected unpacked MZ executable')
 header=struct.unpack_from('<H',raw,8)[0]*16
 if header<28 or header>len(raw):raise ValueError('Invalid MZ header')
 image=raw[header:]
 if len(image)!=171360 or hashlib.sha256(image).hexdigest()!=EXPECTED_IMAGE:raise ValueError('Unrecognized load image; no address claims permitted')
 pattern=bytes.fromhex('9aa001ba0f');sites=[i for i in range(len(image)) if image.startswith(pattern,i)]
 if sites!=EXPECTED_SITES:raise ValueError('RNG census mismatch')
 return {'evidence_status':'VERIFIED_STATIC','image_sha256':EXPECTED_IMAGE,'literal_direct_call_sites':[f'{x:04X}' for x in sites],'count':len(sites),'complete_dynamic_callgraph':False,'runtime_or_remake_parity':False}
if __name__=='__main__':
 from pathlib import Path
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('unpacked_exe');args=parser.parse_args()
 try:print(json.dumps(verify(Path(args.unpacked_exe).read_bytes()),indent=2))
 except (ValueError,OSError) as e:parser.exit(2,str(e)+'\n')

