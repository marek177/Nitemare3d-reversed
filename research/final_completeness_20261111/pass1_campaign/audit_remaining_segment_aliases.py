"""python audit_remaining_segment_aliases.py IMAGE INVENTORY CANDIDATES DECODER_DIR OUT
Resolve only explicit local FAR-address constructions; no global reachability claim.
"""
import csv,hashlib,json,sys
from pathlib import Path
image,inventory,candidates,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
sha=lambda b:hashlib.sha256(b).hexdigest()
b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());index={r['image_offset']:r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
# Exact local byte witnesses. These describe address formation, not every possible entry path.
patterns={
 0x374d:(0x3747,'68280a68fd21684e26ff76f69ab800ba0f','stack FAR argument to write wrapper'),
 0x3a45:(0x3a3f,'68280a68fd21684e26579a9e00ba0f','stack FAR argument to read wrapper'),
 0x554f:(0x553c,'b8fd218ec02680bffe3600755a26c687fe3601b84e268c46fe33ff393e76627e468bf08e46fe26807c0a00','ES explicit 21FD; AX->SI; segment retained in local'),
 0x5f2c:(0x5f2c,'b84e26b9fd218bf0894efe33ff393e76627e228e46fe266b44081c','CX explicit 21FD; SI pointer; ES reload'),
 0x618b:(0x6186,'b8fd218ec0b84e268bd88c46fe33ff393e76627e438e5efe807f0b0a','ES explicit 21FD; AX->BX; DS reload from local'),
 0x61de:(0x61de,'b84e26b9fd218bf0894efe','CX explicit 21FD; AX->SI; FAR pair retained in locals'),
 0x6263:(0x6263,'b84e26b9fd218bf0894efe833e7662007e578e46fe266b44081c','CX explicit 21FD; AX->SI; ES reload'),
 0x69a7:(0x69a7,'b84e26b9fd218bf0894ef6','CX explicit 21FD; AX->SI; FAR pair retained in locals'),
 0x93b8:(0x93b8,'b84e26b9fd218bf0894ef8833e7662000f8e5d018e46f8266b5c081c','CX explicit 21FD; AX->SI; ES reload'),
 0x94c3:(0x94c3,'b84e26b9fd218bf0894ef8833e7662007e548ed96b44081c','CX explicit 21FD; AX->SI; DS=CX'),
 0x999a:(0x999a,'b84e26b9fd218bf0894efa833e7662000f8e2d028e46fa26807c0b0a','CX explicit 21FD; AX->SI; ES reload'),
 0xa9dc:(0xa9dc,'c746fa4e26c746fcfd21390676627e3c8b76fa8b7efe8e46fc','adjacent local FAR pair 21FD:264E; ES reload'),
}
refs=list(csv.DictReader(candidates.open()));immediates=[r for r in refs if r['kind']=='IMMEDIATE_DS_CANDIDATE']
assert {int(r['instruction_image']) for r in immediates}==set(patterns) and len(immediates)==12
rows=[];asm=[]
for r in immediates:
 p=int(r['instruction_image']);a,h,why=patterns[p];raw=bytes.fromhex(h);assert b[a:a+len(raw)]==raw
 pos=a
 for i in Decoder(16,raw,ip=a-index[p]['cs']*16):
  assert not i.is_invalid and pos in index
  saved=index[pos];assert bytes.fromhex(saved['bytes'])==b[pos:pos+i.len]
  asm.append(dict(candidate_instruction=p,image_offset=pos,cs=saved['cs'],ip=i.ip,bytes=b[pos:pos+i.len].hex(),instruction=fmt.format(i)));pos+=i.len
 assert pos==a+len(raw)
 rows.append(dict(instruction_image=p,witness_start=a,witness_end_exclusive=pos,witness_sha256=sha(raw),encoded_offset=0x264e,explicit_segment=0x21fd,constructed_image_address=0x2461e,naive_default_ds_address=0x29d5e,resolution='explicit alternate-segment address construction; not evidence for DS:264E',evidence=why,scope='local sequence only; alternate entries, indexed bounds and natural execution not proved'))
out.mkdir(parents=True,exist_ok=True)
for name,data in [('resolved_candidates',rows),('witness_instructions',asm)]:
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),candidate_csv_sha256=sha(candidates.read_bytes()),resolved_local_address_constructions=len(rows),remaining_indexed_candidates=len(refs)-len(rows),constructed_image_address=0x2461e,status_changes=0,new_deep_verified_bytes=0,runtime_tests=0,scope='disambiguates numeric immediate matches only; does not prove absence of other users of DS:264E')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
