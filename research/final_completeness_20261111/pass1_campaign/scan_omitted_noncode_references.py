"""python scan_omitted_noncode_references.py IMAGE MAP INVENTORY DECODER OUT
Raw candidates are not proved code or references, and never change classification.
"""
import csv,hashlib,json,sys
from pathlib import Path
image,mapping,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,OpKind,Register,MemorySizeExt
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());occupied=set()
for r in old:
    a=r['image_offset'];raw=bytes.fromhex(r['bytes']);assert b[a:a+len(raw)]==raw;occupied.update(range(a,a+len(raw)))
remaining=[r for r in csv.DictReader(mapping.open(encoding='utf-8-sig')) if r['status'] in ('UNKNOWN','CLASSIFIED ONLY')];wanted={p:r for r in remaining for p in range(int(r['start']),int(r['end_exclusive']))}
fmt=Formatter(FormatterSyntax.INTEL);rows=[];scanned=0
for a in range(0x1bda2):
    if a in occupied or 0x11ee7<=a<0x11ef8:continue
    scanned+=1;i=Decoder(16,b[a:a+15],ip=0).decode()
    if i.is_invalid or any(p in occupied for p in range(a,a+i.len)):continue
    if not any(i.op_kind(k)==OpKind.MEMORY for k in range(i.op_count)) or i.memory_segment not in (Register.DS,Register.SS):continue
    p=0x27710+i.memory_displacement
    if p not in wanted:continue
    r=wanted[p];rows.append(dict(candidate_image=a,bytes=b[a:a+i.len].hex(),instruction=fmt.format(i),segment='DS' if i.memory_segment==Register.DS else 'SS',indexed=i.memory_base!=Register.NONE or i.memory_index!=Register.NONE,nominal_reference_image=p,operand_width=MemorySizeExt.size(i.memory_size),remaining_start=r['start'],remaining_end_exclusive=r['end_exclusive'],context_start=max(0,a-8),context_hex=b[max(0,a-8):a+24].hex(),scope='raw decode at unowned byte; not proven code, instruction start, segment context, or reachability'))
out.mkdir(parents=True,exist_ok=True)
if rows:
    with (out/'raw_candidates.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),map_sha256=sha(mapping.read_bytes()),inventory_sha256=sha(inventory.read_bytes()),unowned_byte_starts_scanned=scanned,raw_candidates=len(rows),status_changes=0,runtime_tests=0,new_deep_verified_bytes=0,scope='historical code domain only, every unowned byte; hypothetical DS/SS=DGroup address mapping; excludes overlap with supplied inventory; indirect runtime targets not covered')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
