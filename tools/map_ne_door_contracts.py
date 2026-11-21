"""Prove bounded DOS/NE door lookup/predicate relation with explicit field mapping."""
import argparse,json,csv,struct,hashlib
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--evidence-dir',type=Path,required=True);ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args();E=a.evidence_dir;O=a.output_dir;O.mkdir(parents=True,exist_ok=True)
bins=json.loads((E/'binary_inventory.json').read_text());inv=list(csv.DictReader((E/'function_inventory.csv').open(newline='',encoding='utf-8-sig')));graph=json.loads((E/'function_callgraph.json').read_text())['edges'];ref=next(x for x in bins if x['id']=='nite3d20');dr=Path(ref['source_path']).read_bytes();assert hashlib.sha256(dr).hexdigest()==ref['sha256'];di=dr[int.from_bytes(dr[8:10],'little')*16:];dp=di[0x1e0:0x1fc];np=bytearray(dp);np[9]=12;records=[]
def ne(raw):
 n=int.from_bytes(raw[60:64],'little');U=lambda p:int.from_bytes(raw[p:p+2],'little');assert raw[n:n+2]==b'NE';segs={};fix={};all_sources={}
 for s in range(1,U(n+28)+1):
  sector,size,flags,mem=struct.unpack_from('<4H',raw,n+U(n+34)+(s-1)*8)
  if sector:
   start=sector<<U(n+50);size=size or 65536;segs[s]={'file':start,'data':bytearray(raw[start:start+size]),'flags':flags}
 for s,g in segs.items():
  if not g['flags']&0x100:continue
  q=g['file']+len(g['data']);nr=U(q)
  for j in range(nr):
   typ,fl,src,t1,t2=struct.unpack_from('<BBHHH',raw,q+2+8*j);chain=[];seen=set();at=src
   while at!=65535 and at not in seen and at+2<=len(g['data']):
    seen.add(at);chain.append(at);at=65535 if fl&4 else int.from_bytes(g['data'][at:at+2],'little')
   for at in chain:all_sources[(s,at)]={'type':typ,'flags':fl}
   # Only nonadditive fixed internal selectors/pointers are reconstructed here.
   if fl&7 or t1&255==255 or typ not in (2,3):continue
   for at in chain:
    target=t1&255;fix[(s,at)]={'type':typ,'flags':fl,'record_file_offset':q+2+8*j,'target_segment':target,'target_offset':t2}
    g['data'][at:at+(2 if typ==2 else 4)]=struct.pack('<H',target) if typ==2 else struct.pack('<HH',t2,target)
 return segs,fix,U(n+14),all_sources
for b in bins:
 if b['kind']!='NE':continue
 raw=Path(b['source_path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==b['sha256'];at=raw.find(np);assert at>=0 and raw.find(np,at+1)<0
 row=next(x for x in inv if x['binary_id']==b['id'] and int(x['file_offset'],0)==at);fid=row['function_id'];s,o=[int(x,16) for x in row['entry'].split(':')];segs,fix,ds,all_sources=ne(raw);code=segs[s]['data'];assert code[o:o+28]==np
 assert not any(cs==s and o-3<=off<o+28 for cs,off in all_sources)
 cfg=json.loads((E/'function_cfg'/(fid.replace(':','_')+'.json')).read_text());assert len(cfg['instructions'])==14
 for i in cfg['instructions']:assert code[i['offset']:i['offset']+len(bytes.fromhex(i['bytes']))]==bytes.fromhex(i['bytes'])
 source_cfg=json.loads((E/'function_cfg/nite3d20_0000_01E0.json').read_text());assert [(i['from']-o,i['to']-o,i['kind'],i.get('condition')) for i in cfg['instruction_edges']]==[(i['from']-0x1e0,i['to']-0x1e0,i['kind'],i.get('condition')) for i in source_cfg['instruction_edges']]
 pairs=[]
 for edge in graph:
  if edge.get('callee')!=fid:continue
  cs,ip=[int(x,16) for x in edge['site'].split(':')]
  if cs!=s or ip<10:continue
  block=code[ip-10:ip+5]
  if len(block)!=15 or block[0]!=0x9a or block[5:10]!=bytes.fromhex('83c4045250') or block[10]!=0x9a:continue
  lo,ls=struct.unpack_from('<HH',block,1);po,ps=struct.unpack_from('<HH',block,11);assert (po,ps)==(o,s) and ls==s
  witnesses=[]
  for site in (ip-10,ip):
   f=fix[(s,site+3)];assert f['type']==2 and f['target_segment']==s;witnesses.append(f)
  assert {off for cs,off in all_sources if cs==s and ip-13<=off<ip+5}=={ip-7,ip+3}
  pairs.append({'lookup_site':f'{s:04X}:{ip-10:04X}','predicate_site':f'{s:04X}:{ip:04X}','lookup_entry':f'{ls:04X}:{lo:04X}','caller':edge['caller'],'NE_selector_fixups':witnesses})
 assert pairs and len({p['lookup_entry'] for p in pairs})==1
 ls,lo=[int(x,16) for x in pairs[0]['lookup_entry'].split(':')];lc=segs[ls]['data'][lo:lo+0x52];expected=bytearray(di[:0x52]);data_seg=int.from_bytes(lc[5:7],'little');base=int.from_bytes(lc[12:14],'little');literal=int.from_bytes(lc[0x45:0x47],'little');error_off,error_seg=struct.unpack_from('<HH',lc,0x48)
 expected[5:7]=struct.pack('<H',data_seg);expected[12:14]=struct.pack('<H',base);expected[0x23]=8;expected[0x29]=10;expected[0x2e]=22;expected[0x45:0x47]=struct.pack('<H',literal);expected[0x48:0x4c]=struct.pack('<HH',error_off,error_seg);assert lc==expected
 assert fix[(ls,lo+5)]['target_segment']==data_seg and fix[(ls,lo+0x4a)]['target_segment']==error_seg
 assert {off for cs,off in all_sources if cs==ls and lo-3<=off<lo+0x52}=={lo+5,lo+0x4a}
 assert bytes(segs[ds]['data'][literal:literal+16]).split(b'\0')[0]==b'Door not in map'
 lookup_fid=f"{b['id']}:{ls:04X}:{lo:04X}";lcfg=json.loads((E/'function_cfg'/(lookup_fid.replace(':','_')+'.json')).read_text());assert len(lcfg['instructions'])==38
 for i in lcfg['instructions']:assert segs[ls]['data'][i['offset']:i['offset']+len(bytes.fromhex(i['bytes']))]==bytes.fromhex(i['bytes'])
 records.append({'binary_id':b['id'],'source_sha256':b['sha256'],'predicate_function':fid,'lookup_function':lookup_fid,'predicate_file_offset':at,'predicate_body_sha256':hashlib.sha256(np).hexdigest(),'lookup_body_sha256':hashlib.sha256(lc).hexdigest(),'data_segment_logical_index':data_seg,'array_base':base,'diagnostic_offset':literal,'paired_callers':pairs,'predicate_membership':14,'lookup_membership':38,'evidence_status':'VERIFIED_STATIC','field_mapping':{'DOS_key_offset':4,'NE_key_offset':8,'DOS_state_offset':8,'NE_state_offset':12,'DOS_stride':18,'NE_stride':22},'contract':'Local truth set{0,4}, FAR key lookup and return frame agree under explicit field/array projection; record layouts differ','boundary_status':'UNKNOWN','runtime_NE':'NOT_OBSERVED'})
assert len(records)==5
v={'evidence_status':'VERIFIED_STATIC','records':records,'semantic_scope':'Projected local contracts; no full record bijection, native NE execution, whole function boundary, external error or game/render/timing parity proof','NE_loader_scope':'Only nonadditive internal fixed-selector fixups used by these witnesses; imported, additive and movable-entry cases are not generalized'}
(O/'NE_door_contract_mapping.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps({'NE_predicates':len(records),'paired_call_chains':sum(len(x['paired_callers']) for x in records),'lookup_instruction_memberships':38,'predicate_instruction_memberships':14}))
