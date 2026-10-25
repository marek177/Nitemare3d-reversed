"""Opt-in static byte checks for bounded DOS20 indirect provenance and delay loop.

This verifies local snippets and mathematical predicates, not runtime or parity.
"""
import argparse,hashlib,json,struct
IMAGE_SHA='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
CHECKS=[(0x768,0x784,'558becb80043cd2fa8807414b81043cd2f891e0e358c061035b80100e9040090b80000c9cb'),(0x768,0x802,'8cd88ec01e568e5e088b7606b40b26ff1e0e35'),(0x6b0,0x14b,'6a099ae239ee118be5a3523f8916543f68b0066800006a099af439ee11'),(0x6b0,0x110,'9cff1e523f'),(0x11ee,0x39e2,'558bec8b4606b435cd218cc28bc38be55dcb'),(0x11ee,0x39f4,'558bec8b46061ec55608b425cd211f33c08be55dcb'),(0x15bf,0x2e41,'5053515233c0cd1a03dacd1a3bd376fa5a595b58c3')]+[(0x768,o,'26ff1e0e35' if o==0x810 else 'ff1e0e35') for o in (0x7b0,0x7cb,0x7ec,0x810,0x82e,0x84c)]
def verify(raw):
 if len(raw)<28 or raw[:2]!=b'MZ':raise ValueError('Expected unpacked MZ executable')
 header=struct.unpack_from('<H',raw,8)[0]*16
 if header<28 or header>len(raw):raise ValueError('Invalid header')
 image=raw[header:]
 if len(image)!=171360 or hashlib.sha256(image).hexdigest()!=IMAGE_SHA:raise ValueError('Unknown image; address assertions rejected')
 for s,o,hexbytes in CHECKS:
  expected=bytes.fromhex(hexbytes)
  if image[s*16+o:s*16+o+len(expected)]!=expected:raise ValueError(f'Byte mismatch at {s:04X}:{o:04X}')
 comparisons=0
 for target in (0,1,32767,32768,65534,65535):
  for dx in range(65536):
   if ((dx<target) or (dx==target))!=(dx<=target):raise ValueError('Unsigned predicate mismatch')
   comparisons+=1
 return {'status':'VERIFIED_STATIC','image_sha256':IMAGE_SHA,'byte_spans_verified':len(CHECKS),'provenance_consumers':7,'synthetic_unsigned_comparisons':comparisons,'target_FFFF_local_exit_possible':False,'original_edge_case_execution':False,'complete_target_sets_proven':False,'gameplay_parity_proven':False}
if __name__=='__main__':
 from pathlib import Path
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('unpacked_exe');args=parser.parse_args()
 try:print(json.dumps(verify(Path(args.unpacked_exe).read_bytes()),indent=2))
 except (OSError,ValueError) as e:parser.exit(2,str(e)+'\n')

