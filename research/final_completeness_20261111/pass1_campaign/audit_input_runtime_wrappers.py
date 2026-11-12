"""python audit_input_runtime_wrappers.py IMAGE INVENTORY DECODER OUT"""
import csv,hashlib,json,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);functions=[]
for name,cs,ip,end,role in [('crt_get_interrupt_vector',0x11ee,0x39e2,0x39f4,'DOS API wrapper, compiler-runtime location; exact compiler/library provenance open'),('crt_set_interrupt_vector',0x11ee,0x39f4,0x3a09,'DOS API wrapper, compiler-runtime location; exact compiler/library provenance open'),('aux_int33_probe',0x831,0xe,0x28,'game-side INT33 register-block wrapper, external INT86 dependency'),('aux_int33_reset_close',0x831,0x28,0x3f,'game-side INT33 register-block wrapper, external INT86 dependency')]:
 rows=[];p=cs*16+ip
 for i in Decoder(16,b[p:cs*16+end],ip=ip):
  assert not i.is_invalid and lookup[p]['bytes']==b[p:p+i.len].hex();rows.append(dict(cs=cs,ip=i.ip,image_offset=p,bytes=b[p:p+i.len].hex(),instruction=fmt.format(i)));p+=i.len
 assert p==cs*16+end and rows[-1]['bytes']=='cb'
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 functions.append(dict(name=name,start=cs*16+ip,end_exclusive=p,instruction_bytes=p-cs*16-ip,instructions=len(rows),role=role))
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,runtime_tests=0,new_deep_verified_bytes=0,scope='four straight-line static wrappers; runtime session counted separately; INT86 body and close-mode runtime unclosed')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
