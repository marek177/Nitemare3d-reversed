"""Exact bounded predicate/CFG matching; no inference from release labels."""
import argparse,csv,json,hashlib,struct
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--evidence-dir',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);args=ap.parse_args();E=args.evidence_dir;O=args.output_dir;O.mkdir(parents=True,exist_ok=True)
bins=json.loads((E/'binary_inventory.json').read_text());inv=list(csv.DictReader((E/'function_inventory.csv').open(newline='',encoding='utf-8-sig')))
reference=next(b for b in bins if b['id']=='nite3d20');r=Path(reference['source_path']).read_bytes();assert hashlib.sha256(r).hexdigest()==reference['sha256'];h=int.from_bytes(r[8:10],'little')*16;pattern=r[h+0x1e0:h+0x1fc];assert hashlib.sha256(pattern).hexdigest()=='f1869a55b1fe9d0c6f8884bf9d8c68df98f5cff1f8480c06b8a3c93d50c75a2a'
records=[];unmatched=[];normalized_reference=None
for b in bins:
 raw=Path(b['source_path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==b['sha256'];starts=[];pos=0
 while True:
  pos=raw.find(pattern,pos)
  if pos<0:break
  starts.append(pos);pos+=1
 if b['kind']!='DOS':
  unmatched.append({'binary_id':b['id'],'sha256':b['sha256'],'exact_body_matches':len(starts),'status':'UNKNOWN','scope':'No identical byte body does not prove absent predicate or different algorithm'});continue
 assert len(starts)==1,(b['id'],starts);at=starts[0];owners=[x for x in inv if x['binary_id']==b['id'] and int(x['file_offset'],0)==at];assert len(owners)==1
 row=owners[0];fid=row['function_id'];s,o=[int(x,16) for x in row['entry'].split(':')];cfg=json.loads((E/'function_cfg'/(fid.replace(':','_')+'.json')).read_text());assert len(cfg['instructions'])==14
 instructions=[]
 for i in sorted(cfg['instructions'],key=lambda x:x['offset']):
  code=bytes.fromhex(i['bytes']);assert raw[i['file_offset']:i['file_offset']+len(code)]==code;assert 0<=i['offset']-o<28;assert pattern[i['offset']-o:i['offset']-o+len(code)]==code;instructions.append({'relative_offset':i['offset']-o,'bytes':i['bytes']})
 edges=[{'from':x['from']-o,'to':x['to']-o,'kind':x['kind'],'condition':x.get('condition')} for x in cfg['instruction_edges']];norm={'instructions':instructions,'edges':edges}
 if normalized_reference is None:normalized_reference=norm
 assert norm==normalized_reference
 ro=int.from_bytes(raw[24:26],'little');n=int.from_bytes(raw[6:8],'little');head=int.from_bytes(raw[8:10],'little')*16;rel=[head+seg*16+off for j in range(n) for off,seg in [struct.unpack_from('<HH',raw,ro+j*4)]];assert not any(at<=q<at+28 for q in rel)
 records.append({'binary_id':b['id'],'source_sha256':b['sha256'],'function_id':fid,'file_offset':at,'entry':row['entry'],'instruction_count':14,'body_envelope_bytes':28,'membership_bytes':27,'body_sha256':hashlib.sha256(pattern).hexdigest(),'normalized_CFG_sha256':hashlib.sha256(json.dumps(norm,sort_keys=True).encode()).hexdigest(),'evidence_status':'VERIFIED_STATIC','boundary_status':'UNKNOWN','scope':'Identical bounded code/CFG, valid FAR argument local ABI and state predicate; global record identity, natural reachability, timing, runtime callers and game parity not equated'})
assert len(records)==8
v={'evidence_status':'VERIFIED_STATIC','records':records,'unmatched_NE':unmatched,'version_label_status':'Retains inventory INFERRED release labels; hash identities are authoritative','semantic_scope':'Local AL=(word argument+8 in{0,4}) with same instruction/FLAGS/stack semantics; not native execution or full function boundary proof'}
(O/'predicate_crossversion_mapping.json').write_text(json.dumps(v,indent=2),encoding='utf-8')
rows=[{'source_binary':'nite3d20','source_function':'nite3d20:0000:01E0','target_binary':x['binary_id'],'target_function':x['function_id'],'match_status':'VERIFIED_STATIC','match_scope':'14-instruction local predicate and CFG exact; whole boundaries/global record meaning/runtime parity open','proof':'../lookup_edges_20261106/predicate_crossversion_mapping.json'} for x in records if x['binary_id']!='nite3d20']
with (O/'predicate_version_function_mapping.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps({'DOS_bodies_and_CFGs_verified':len(records),'new_pairwise_rows':len(rows),'NE_unknown':len(unmatched)}))
