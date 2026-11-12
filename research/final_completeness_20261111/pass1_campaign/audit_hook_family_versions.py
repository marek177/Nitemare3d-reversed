"""python audit_hook_family_versions.py VERSION_CSV DECODER OUT
Find repeated FAR-hook initializers independently per image, then verify consumers.
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
manifest,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,Register,OpKind,FlowControl
sha=lambda b:hashlib.sha256(b).hexdigest();fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True);versions=[];slots=[];refs=[];raw_context=[]
for v in csv.DictReader(manifest.open(encoding='utf-8-sig')):
 path=Path(v['image_path']);b=path.read_bytes();assert sha(b)==v['image_sha256'];crt=int(v['entry_cs']);meta=json.loads((path.parent/'unpack.json').read_text());ds=meta['runtime_data_segment'];runs=[]
 for p in range(len(b)-27):
  off,seg=struct.unpack_from('<HH',b,p)
  if seg!=crt or b[p:p+4]*7!=b[p:p+28]:continue
  target=seg*16+off
  if b[target:target+4]==bytes.fromhex('b80200e9'):runs.append((p,off))
 assert len(runs)==1,(v['label'],runs)
 start,targetip=runs[0];slotbase=start-ds*16;target=crt*16+targetip;stub=Decoder(16,b[target+3:target+6],ip=targetip+3).decode();assert stub.flow_control==FlowControl.UNCONDITIONAL_BRANCH
 if v['label']=='20':assert b[:0x1bda2].find(bytes.fromhex('5823'))<0
 ipath=path.parent/'instructions.json';inventory=json.loads(ipath.read_text());direct=[];indexed=[];count=0
 for r in inventory:
  p=r['image_offset'];raw=bytes.fromhex(r['bytes']);assert p==r['cs']*16+r['ip'] and b[p:p+len(raw)]==raw
  i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);count+=1
  if not any(i.op_kind(n)==OpKind.MEMORY for n in range(i.op_count)):continue
  d=i.memory_displacement
  if not slotbase<=d<slotbase+28:continue
  unindexed=i.memory_base==Register.NONE and i.memory_index==Register.NONE
  row=dict(version=v['label'],slot_index=(d-slotbase)//4,displacement=d,cs=r['cs'],ip=r['ip'],image_offset=p,bytes=raw.hex(),instruction=fmt.format(i),unindexed=unindexed,default_DS=i.memory_segment==Register.DS,scope='explicit displacement candidate only; DS/context/indirect aliases unresolved')
  refs.append(row)
  if unindexed and i.memory_segment==Register.DS:direct.append(row)
  else:indexed.append(row)
 for n in range(7):
  slot=slotbase+n*4;needle=struct.pack('<H',slot);hits=[];p=0
  while True:
   p=b.find(needle,p)
   if p<0:break
   hits.append(p);p+=1
  slots.append(dict(version=v['label'],slot_index=n,ds_offset=slot,image_start=start+n*4,image_end_exclusive=start+n*4+4,initial_offset=targetip,initial_segment=crt,direct_DS_references=sum(x['displacement']==slot for x in direct),raw_WORD_hits_whole_image=len(hits),raw_WORD_hit_images=';'.join('%X'%p for p in hits),classification='PARTIAL candidate only; no promotion'))
  if n==4:
   for hit in hits:
    related=[r for r in inventory if r['image_offset']<hit+2 and r['image_offset']+len(bytes.fromhex(r['bytes']))>hit]
    for r in related:
     i=Decoder(16,bytes.fromhex(r['bytes']),ip=r['ip']).decode()
     raw_context.append(dict(version=v['label'],raw_hit_image=hit,word_value=slot,containing_instruction_image=r['image_offset'],bytes=r['bytes'],instruction=fmt.format(i),scope='raw numeric match only; may cross instruction boundary or join displacement and immediate'))
 versions.append(dict(version=v['label'],image_sha256=sha(b),inventory_sha256=sha(ipath.read_bytes()),unpack_metadata_sha256=sha((path.parent/'unpack.json').read_bytes()),verified_instruction_starts=count,crt_segment=crt,ds_segment=ds,hook_run_image=start,hook_run_ds=slotbase,target_ip=targetip,target_image=target,stub_hex=b[target:target+6].hex(),tail_target=stub.near_branch_target,direct_DS_refs=len(direct),other_memory_candidates=len(indexed),missing_direct_slot_indices=';'.join(str(n) for n in range(7) if not any(x['displacement']==slotbase+n*4 for x in direct))))
def save(name,rs):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
save('versions',versions);save('slots',slots);save('reference_candidates',refs)
if raw_context:save('slot4_raw_hit_context',raw_context)
s=dict(manifest_sha256=sha(manifest.read_bytes()),versions=len(versions),unique_images=len({v['image_sha256'] for v in versions}),verified_instruction_starts=sum(v['verified_instruction_starts'] for v in versions),slot_records=len(slots),canonical_slot4=[r for r in slots if r['version']=='20' and r['slot_index']==4][0],status_changes=0,runtime_tests=0,new_deep_verified_bytes=0,scope='cross-version explicit operand plus raw WORD candidate audit; not absence proof for runtime aliases, omitted code, writers or unreachable inventory')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
