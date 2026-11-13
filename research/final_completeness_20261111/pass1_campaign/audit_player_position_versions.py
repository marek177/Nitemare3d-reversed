"""VERSION_ROOT DECODER OUT: bounded position/cursor/kind helper code+CFG,explicit masked addresses/calls; semantic immediates retained."""
import csv,hashlib,json,sys
from pathlib import Path
root,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,FlowControl,Register,Mnemonic,OpKind,Formatter,FormatterSyntax
out.mkdir(exist_ok=True);sha=lambda x:hashlib.sha256(x).hexdigest();fmt=Formatter(FormatterSyntax.INTEL);rows=[];bindings=[];instructions=[];diffs=[];refs={};files=[]
patterns=[('player_near_geometry_cursors','558bec8b56063916'),('player_far_actor_cursors','558bec568b5e06391e'),('player_position_commit','c804000057568b7e068b7608'),('player_position_reindex','57568b3e'),('terrain_kind_search','558bec2aff8a5e0881fb0001'),('terrain_kind44_variant','c8020000a1')]
for v in ('20','10','11','12','15','17','18','19'):
 image=root/('N3D-'+v)/'unpacked_image.bin';b=image.read_bytes();inv=image.with_name('instructions.json');old={x['image_offset']:x for x in json.loads(inv.read_text(encoding='utf-8'))}
 for name,pat in patterns:
  pat=bytes.fromhex(pat);hits=[p for p in old if b.startswith(pat,p)]
  if name in ('terrain_kind_search','terrain_kind44_variant'):
   vv=[x for x in old.values() if bytes.fromhex(x['bytes']).startswith(bytes.fromhex('80bf')) and bytes.fromhex(x['bytes'])[-1:]==b'\x44'];assert len(vv)==1,(v,'kind44compare',vv)
   owners=vv[0]['owners'];assert len(owners)==1;owner=owners[0];vc,vi=[int(z,16) for z in owner.split(':')];vp=vc*16+vi
   if name=='terrain_kind44_variant':hits=[vp]
   else:
    calls=[]
    for x in old.values():
     if owner not in x['owners']:continue
     q=Decoder(16,bytes.fromhex(x['bytes']),ip=x['ip']).decode()
     if q.flow_control==FlowControl.CALL:calls.append(q)
    assert len(calls)==1;target=vc*16+calls[0].near_branch_target;hits=[p for p in hits if p==target]
  if name=='player_position_commit':hits=[p for p in hits if b[p+12:p+14]==bytes.fromhex('666a')]
  if name=='player_near_geometry_cursors':hits=[p for p in hits if b[p+10]==0x7c]
  if name=='player_position_reindex':hits=[p for p in hits if b[p+10:p+13]==bytes.fromhex('6633c0')]

  assert len(hits)==1,(v,name,hits);a=hits[0];cs=old[a]['cs'];start=old[a]['ip'];todo=[start];d={}
  while todo:
   ip=todo.pop()
   if ip in d:continue
   p=cs*16+ip;assert a<=p<a+600;i=Decoder(16,b[p:p+16],ip=ip).decode();assert not i.is_invalid and old[p]['bytes']==b[p:p+i.len].hex();d[ip]=i
   if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
   if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
  idx={ip:j for j,ip in enumerate(sorted(d))};norm=[];edges=[]
  for ip,i in sorted(d.items()):
   p=cs*16+ip;raw=b[p:p+i.len];patched=bytearray(raw);dec=Decoder(16,raw,ip=ip);check=dec.decode();co=dec.get_constant_offsets(check);j=idx[ip]
   if co.displacement_size and i.memory_segment==Register.DS and (i.memory_base==Register.NONE and i.memory_index==Register.NONE or i.memory_displacement>=0x2000):
    z,n=co.displacement_offset,co.displacement_size;patched[z:z+n]=bytes(n);bindings.append(dict(version=v,function=name,index=j,kind='global_or_pointer_table',raw=raw.hex(),asm=fmt.format(i)))
   if name=='player_position_commit' and ((i.mnemonic==Mnemonic.ADD and i.op0_register==Register.AX and i.op1_kind==OpKind.IMMEDIATE16 and i.immediate16>=0x1000) or (i.mnemonic==Mnemonic.MOV and i.op0_register==Register.CX and i.op1_kind==OpKind.IMMEDIATE16 and i.immediate16>=0x1000)):
    z,n=co.immediate_offset,co.immediate_size;patched[z:z+n]=bytes(n);bindings.append(dict(version=v,function=name,index=j,kind='gridbase_or_recordsegment',raw=raw.hex(),asm=fmt.format(i)))
   if i.flow_control in (FlowControl.CALL,FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
    for z,n in ((co.immediate_offset,co.immediate_size),(co.immediate_offset2,co.immediate_size2)):
     if n:patched[z:z+n]=bytes(n)
    bindings.append(dict(version=v,function=name,index=j,kind='call_or_branch',raw=raw.hex(),asm=fmt.format(i)))
    if i.flow_control!=FlowControl.CALL:edges.append((j,idx[i.near_branch_target],'branch'))
   if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):edges.append((j,idx[i.next_ip],'fallthrough_or_call_return'))
   norm.append(patched.hex());instructions.append(dict(version=v,function=name,cs=cs,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
  if v=='20':refs[name]=(norm,edges)
  rn,re=refs[name]
  if len(norm)!=len(rn):diffs.append(dict(version=v,function=name,index=-1,current='instruction_count:'+str(len(norm)),DOS20='instruction_count:'+str(len(rn)),current_instruction='Different layout;no positionalinstruction alignment claimed'))
  for j,(q,z) in enumerate(zip(norm,rn) if len(norm)==len(rn) else []):
   if q!=z:diffs.append(dict(version=v,function=name,index=j,current=q,DOS20=z,current_instruction=fmt.format(d[sorted(d)[j]])))
  rows.append(dict(version=v,function=name,start=a,end_exclusive=max(cs*16+i.next_ip for i in d.values()),instructions=len(d),code_bytes=sum(i.len for i in d.values()),normalized_equal_DOS20=norm==rn,CFG_equal_DOS20=edges==re))
 files.extend(dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inv))
def save(n,rr):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
save('versions',rows);save('masked_bindings',bindings);save('instructions',instructions)
if diffs:save('normalized_differences',diffs)
s=dict(versions=8,bodies=len(rows),normalized_matches=sum(x['normalized_equal_DOS20'] for x in rows),CFG_matches=sum(x['CFG_equal_DOS20'] for x in rows),normalized_differences=len(diffs),runtime_tests=0,separate_cases=0,new_deep_verified_bytes=0,scope='Byte-matched bounded code/CFG;explicit global,segment,gridbase/call masks;not allcallee,assets,naturalbounds orWin16parity.',files=files+[dict(path=str(Path(__file__).resolve()),sha256=sha(Path(__file__).read_bytes()))]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'}))
