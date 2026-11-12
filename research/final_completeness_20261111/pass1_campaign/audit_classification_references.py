"""python audit_classification_references.py IMAGE INVENTORY DECODER OUT
Literal base references only; no exclusion proof for indirect aliases.
"""
import csv,hashlib,json,sys
from pathlib import Path
image,inventory,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()));out.mkdir(exist_ok=True)
from iced_x86 import Decoder,Formatter,FormatterSyntax,Register
b=image.read_bytes();inv=json.loads(inventory.read_text(encoding='utf-8'));fmt=Formatter(FormatterSyntax.INTEL);rows=[]
names={0xd00c:'tile_flags',0xd10c:'occupancy_flags',0xd30e:'tile_type_mapping',0xd40e:'occupancy_type_mapping'}
for r in inv:
 p=r['image_offset'];raw=bytes.fromhex(r['bytes']);assert b[p:p+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();base=i.memory_displacement&65535
 if base not in names or i.memory_base==Register.NONE:continue
 rows.append(dict(table=names[base],DS_base=base,cs=r['cs'],ip=r['ip'],image_offset=p,bytes=raw.hex(),instruction=fmt.format(i),owners=';'.join(r['owners']),scope='indexed literal displacement; DS/SS context and dynamic index domain require per-caller proof'))
with (out/'indexed_table_references.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(references=len(rows),by_table={n:sum(x['table']==n for x in rows) for n in names.values()},inventory_instruction_starts=len(inv),scope='literal indexed base census, not all indirect/context-dependent references or global absence proof',files=[dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (image,inventory,Path(__file__))])
(out/'reference_summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
