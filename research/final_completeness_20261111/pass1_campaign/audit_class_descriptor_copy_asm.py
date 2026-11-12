"""python audit_class_descriptor_copy_asm.py IMAGE INVENTORY DECODER OUT
Decode producer witnesses, not an invented independent function boundary.
"""
import csv,hashlib,json,sys
from pathlib import Path
image,inventory,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()));out.mkdir(exist_ok=True)
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};fmt=Formatter(FormatterSyntax.INTEL);rows=[]
for label,a,z in [('class_record_stores',0x969,0x997),('bank_allocate_copy',0x997,0x9d9),('object_key_table_read',0x885,0x8b8)]:
 for i in Decoder(16,b[0x2770+a:0x2770+z],ip=a):
  assert not i.is_invalid;p=0x2770+i.ip;raw=b[p:0x2770+i.next_ip];assert old[p]['bytes']==raw.hex();rows.append(dict(block=label,cs=0x277,ip=i.ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i),scope='bounded static witness inside0686, not whole-function closure'))
with (out/'producer_witness_asm.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(witness_instructions=len(rows),new_central_functions=0,new_deep_verified_bytes=0,scope='record stride/field stores,90BYTEallocation+copy,object payload-table seek400h; static internal blocks only',files=[dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (image,inventory,Path(__file__))])
(out/'witness_summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8')
