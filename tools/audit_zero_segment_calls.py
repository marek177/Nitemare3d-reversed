"""Bounded census of immediate segment-zero FAR transfers in inherited DOS20 sites."""
import sys,json,struct,hashlib,argparse
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('unpacked_exe',type=Path);ap.add_argument('inherited_functions_json',type=Path);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
b=args.unpacked_exe.read_bytes();image=b[int.from_bytes(b[8:10],'little')*16:]
assert hashlib.sha256(b).hexdigest()=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3'
n,=struct.unpack_from('<H',b,6);ro,=struct.unpack_from('<H',b,24);rel={s*16+o for i in range(n) for o,s in [struct.unpack_from('<HH',b,ro+4*i)]}
fb=args.inherited_functions_json.read_bytes();fs=json.loads(fb);seen=set();rows=[]
for f in fs:
 for ins in f['instructions']:
  s=f['segment'];o=ins['offset']
  if (s,o) in seen:continue
  seen.add((s,o));at=s*16+o;c=image[at:at+5]
  if len(c)==5 and c[0] in (0x9a,0xea) and c[3:]==b'\0\0':
   target=struct.unpack_from('<H',c,1)[0];rows.append({'site':f'{s:04X}:{o:04X}','kind':'direct_far_call' if c[0]==0x9a else 'direct_far_jump','target':f'0000:{target:04X}','segment_word_MZ_relocation':at+3 in rel,'scope':'Immediate operand encoding; inherited instruction start, not universal target reachability or code-write closure'})
v={'status':'VERIFIED_STATIC_BOUNDED_ENCODING_CENSUS','source_sha256':hashlib.sha256(b).hexdigest(),'inherited_functions_sha256':hashlib.sha256(fb).hexdigest(),'unique_inherited_sites':len(seen),'zero_segment_immediate_far_transfers':len(rows),'all_have_MZ_segment_relocation':all(x['segment_word_MZ_relocation'] for x in rows),'rows':rows,'scope':'One DOS20 image, inherited instruction membership only; does not enumerate undiscovered code, indirect transfers or other DOS/NE versions'}
args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps({k:x for k,x in v.items() if k!='rows'}))
