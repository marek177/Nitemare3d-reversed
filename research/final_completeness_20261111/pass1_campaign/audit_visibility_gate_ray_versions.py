"""VERSION_ROOT CALLER_CSV DECODER OUT: actual caller-bound visibility gate/ray code+CFG; explicit global/map-base/call bindings."""
import csv,hashlib,json,sys
from pathlib import Path
root,callerpath,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,FlowControl,Register,Mnemonic,OpKind,Formatter,FormatterSyntax
out.mkdir(exist_ok=True);sha=lambda x:hashlib.sha256(x).hexdigest();caller=list(csv.DictReader(callerpath.open(encoding='utf-8')));fmt=Formatter(FormatterSyntax.INTEL);rows=[];bindings=[];instructions=[];diffs=[];refs={};files=[]
for v in ('20','10','11','12','15','17','18','19'):
 image=root/('N3D-'+v)/'unpacked_image.bin';b=image.read_bytes();inv=image.with_name('instructions.json');old={x['image_offset']:x for x in json.loads(inv.read_text(encoding='utf-8'))};cr=[x for x in caller if x['version']==v];assert len(cr)==182;row=cr[146];raw=bytes.fromhex(row['bytes']);assert b[int(row['image_offset']):int(row['image_offset'])+len(raw)]==raw;i=Decoder(16,raw,ip=int(row['ip'])).decode();assert i.flow_control==FlowControl.CALL;entries={'source_player_visibility_gate':(int(row['cs']),i.near_branch_target)}
 for name in ('source_player_visibility_gate','grid_visibility_ray'):
  cs,start=entries[name];a=cs*16+start;todo=[start];d={}
  while todo:
   ip=todo.pop()
   if ip in d:continue
   p=cs*16+ip;assert a<=p<a+1200;i=Decoder(16,b[p:p+16],ip=ip).decode();assert not i.is_invalid and old[p]['bytes']==b[p:p+i.len].hex();d[ip]=i
   if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
   if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
  if name=='source_player_visibility_gate':
   calls=[i for i in d.values() if i.flow_control==FlowControl.CALL];assert len(calls)==1;entries['grid_visibility_ray']=(calls[0].far_branch_selector,calls[0].far_branch16)
  idx={ip:j for j,ip in enumerate(sorted(d))};norm=[];edges=[]
  for ip,i in sorted(d.items()):
   p=cs*16+ip;raw=b[p:p+i.len];patched=bytearray(raw);dec=Decoder(16,raw,ip=ip);check=dec.decode();co=dec.get_constant_offsets(check);j=idx[ip]
   if co.displacement_size and i.memory_segment in (Register.DS,Register.SS) and i.memory_displacement>=0x2000:
    z,n=co.displacement_offset,co.displacement_size;patched[z:z+n]=bytes(n);bindings.append(dict(version=v,function=name,index=j,kind='global_or_classification_base',raw=raw.hex(),asm=fmt.format(i)))
   if i.mnemonic==Mnemonic.ADD and i.op0_register==Register.BX and i.op1_kind==OpKind.IMMEDIATE16 and i.immediate16>=0x1000:
    z,n=co.immediate_offset,co.immediate_size;patched[z:z+n]=bytes(n);bindings.append(dict(version=v,function=name,index=j,kind='map_grid_near_base',raw=raw.hex(),asm=fmt.format(i)))
   if i.flow_control in (FlowControl.CALL,FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
    for z,n in ((co.immediate_offset,co.immediate_size),(co.immediate_offset2,co.immediate_size2)):
     if n:patched[z:z+n]=bytes(n)
    bindings.append(dict(version=v,function=name,index=j,kind='call_or_branch',raw=raw.hex(),asm=fmt.format(i)))
    if i.flow_control!=FlowControl.CALL:edges.append((j,idx[i.near_branch_target],'branch'))
   if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):edges.append((j,idx[i.next_ip],'fallthrough_or_call_return'))
   norm.append(patched.hex());instructions.append(dict(version=v,function=name,cs=cs,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
  if v=='20':refs[name]=(norm,edges)
  rn,re=refs[name]
  for j,(q,z) in enumerate(zip(norm,rn)):
   if q!=z:diffs.append(dict(version=v,function=name,index=j,current=q,DOS20=z))
  rows.append(dict(version=v,function=name,start=a,end_exclusive=max(cs*16+i.next_ip for i in d.values()),instructions=len(d),code_bytes=sum(i.len for i in d.values()),normalized_equal_DOS20=norm==rn,CFG_equal_DOS20=edges==re))
 files.extend(dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inv))
def save(n,rr):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
save('versions',rows);save('masked_bindings',bindings);save('instructions',instructions)
if diffs:save('normalized_differences',diffs)
s=dict(versions=8,bodies=16,normalized_matches=sum(x['normalized_equal_DOS20'] for x in rows),CFG_matches=sum(x['CFG_equal_DOS20'] for x in rows),normalized_differences=len(diffs),runtime_tests=0,separate_cases=0,new_deep_verified_bytes=0,scope='Actualcaller-bound code/CFG;global/CSmapbase/call bindings explicit;not full data-layout,doorcallee,naturalOOBorWin16parity.',files=files+[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (callerpath,Path(__file__))]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'}))
