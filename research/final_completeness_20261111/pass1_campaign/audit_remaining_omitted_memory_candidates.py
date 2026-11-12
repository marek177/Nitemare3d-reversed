"""python audit_remaining_omitted_memory_candidates.py IMAGE MAP INVENTORY CENTRAL DECODER OUT
Search exact literal displacement references in bytes outside both instruction inventories.
Candidates are not proof of executable code, DS context or use. Never promotes status.
"""
import collections,csv,hashlib,json,struct,sys
from pathlib import Path
image,mapping,inventory,central,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()));out.mkdir(exist_ok=True)
from iced_x86 import Decoder,Formatter,FormatterSyntax,Register,OpKind,MemorySizeExt
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
remaining=[r for r in csv.DictReader(mapping.open(encoding='utf-8-sig')) if r['status'] in ('UNKNOWN','CLASSIFIED ONLY')];old=json.loads(inventory.read_text(encoding='utf-8'));seen=set()
for r in old:seen.update(range(r['image_offset'],r['image_offset']+len(bytes.fromhex(r['bytes']))))
for r in csv.DictReader(central.open(encoding='utf-8-sig')):seen.update(range(int(r['image_offset']),int(r['image_offset'])+len(bytes.fromhex(r['bytes']))))
fmt=Formatter(FormatterSyntax.INTEL);rows=[];done=set();targets={}
for r in remaining:
 a,z=int(r['start']),int(r['end_exclusive'])
 if a<0x27710:continue
 for p in range(max(0,a-3),z):targets.setdefault(p-0x27710,[]).append((a,z))
for disp,intervals in sorted(targets.items()):
 needle=struct.pack('<H',disp);p=0
 while True:
  p=b.find(needle,p,0x1bda2)
  if p<0:break
  for start in range(max(0,p-13),p+1):
   if start in seen:continue
   d=Decoder(16,b[start:start+15],ip=start);i=d.decode()
   if i.is_invalid or i.len<3 or any(q in seen for q in range(start,start+i.len)):continue
   co=d.get_constant_offsets(i)
   if co.displacement_size!=2 or start+co.displacement_offset!=p or i.memory_segment not in (Register.DS,Register.SS):continue
   if not any(i.op_kind(n)==OpKind.MEMORY for n in range(i.op_count)):continue
   if i.memory_base==Register.BP or i.memory_index==Register.BP:continue
   width=MemorySizeExt.size(i.memory_size);raw=b[start:start+i.len];ref=0x27710+disp
   for a,z in intervals:
    if not(ref<z and ref+max(1,width)>a) or (start,a,z) in done:continue
    done.add((start,a,z));rows.append(dict(interval_start=a,interval_end_exclusive=z,candidate_instruction_image=start,bytes=raw.hex(),instruction=fmt.format(i),segment_register='SS' if i.memory_segment==Register.SS else 'DS',literal_displacement=disp,operand_width=width,indexed=i.memory_base!=Register.NONE or i.memory_index!=Register.NONE,scope='raw omitted-byte candidate only; instruction boundary, CS/DS context, CFG and execution unproved'))
  p+=1
with (out/'candidates.csv').open('w',newline='',encoding='utf-8') as f:
 fields=list(rows[0]) if rows else ['candidate_instruction_image','scope'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
summary=dict(remaining_intervals=len(remaining),remaining_bytes=sum(int(r['length']) for r in remaining),literal_displacements_searched=len(targets),old_instruction_starts=len(old),instruction_bytes_excluded=len(seen),raw_candidates=len(rows),candidate_intervals=len(set((r['interval_start'],r['interval_end_exclusive']) for r in rows)),status_changes=0,new_deep_verified_bytes=0,runtime_tests=0,scope='exact literal displacements outside old+central instruction bytes below first NONCODE tail; not exhaustive indirect/omitted executable search or absence proof',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,mapping,inventory,central,Path(__file__))])
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
