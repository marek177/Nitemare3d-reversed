"""VERSION_ROOT DECODER OUT: original specialterrain andpickup bounded bodies/CFG/CS jump table;calls/data bindings explicit,not Win16 parity."""
import csv,json,hashlib,struct,sys
from pathlib import Path
root,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,FlowControl,Register,Formatter,FormatterSyntax,OpKind
out.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest();fmt=Formatter(FormatterSyntax.INTEL);rows=[];ins=[];bindings=[];differences=[];tables=[];files=[];refs={}
for v in ('20','10','11','12','15','17','18','19'):
 p=root/('N3D-'+v)/'unpacked_image.bin';b=p.read_bytes();inv=p.with_name('instructions.json');old={x['image_offset']:x for x in json.loads(inv.read_text(encoding='utf-8'))};files.extend(dict(path=str(q.resolve()),sha256=sha(q.read_bytes())) for q in (p,inv))
 def locate(pat):
  hits=[q for q in old if b.startswith(bytes.fromhex(pat),q)];assert len(hits)==1,(v,pat,hits);return old[hits[0]]['cs'],old[hits[0]]['ip']
 def decode(cs,start):
  todo=[start];d={};jt={}
  while todo:
   ip=todo.pop()
   if ip in d:continue
   assert start<=ip<start+1200,(v,hex(start),hex(ip));pos=cs*16+ip;i=Decoder(16,b[pos:pos+16],ip=ip).decode();assert old[pos]['bytes']==b[pos:pos+i.len].hex();d[ip]=i
   if i.flow_control==FlowControl.INDIRECT_BRANCH:
    assert i.memory_segment==Register.CS and i.memory_base==Register.BX;target=struct.unpack_from('<15H',b,cs*16+i.memory_displacement);jt[ip]=target;todo.extend(target)
   elif i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
   if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH,FlowControl.INDIRECT_BRANCH):todo.append(i.next_ip)
  return d,jt
 cs,start=locate('558bec8b0e');dispatch,_=decode(cs,start);direct=[i.near_branch_target for ip,i in sorted(dispatch.items()) if i.flow_control==FlowControl.CALL and i.op0_kind==OpKind.NEAR_BRANCH16];assert len(direct)==6
 names=('terrain_ep1_level7','terrain_ep1_level10_A','terrain_ep1_level10_B','terrain_ep2_level10','terrain_ep3_level1','terrain_ep3_level10');spec=[('special_terrain_dispatch',cs,start)]+[(n,cs,ip) for n,ip in zip(names,direct)];helper,_=decode(cs,direct[0]);sub=[i.near_branch_target for ip,i in sorted(helper.items()) if i.flow_control==FlowControl.CALL and i.op0_kind==OpKind.NEAR_BRANCH16];assert len(sub)==2;spec.extend((n,cs,ip) for n,ip in zip(('sound_event42','sound_bank_selection'),sub))
 cs,start=locate('c806000057568b7e06c646ff01');pickup,_=decode(cs,start);direct=[i.near_branch_target for ip,i in sorted(pickup.items()) if i.flow_control==FlowControl.CALL and i.op0_kind==OpKind.NEAR_BRANCH16];assert len(direct)==2;spec.extend([('pickup_apply',cs,start),('pickup_record_find',cs,direct[0]),('pickup_cell_clear',cs,direct[1])])
 for name,cs,start in spec:
  d,jt=decode(cs,start);idx={ip:j for j,ip in enumerate(sorted(d))};norm=[];edges=[]
  for ip,i in sorted(d.items()):
   pos=cs*16+ip;raw=b[pos:pos+i.len];patch=bytearray(raw);dec=Decoder(16,raw,ip=ip);ci=dec.decode();co=dec.get_constant_offsets(ci);j=idx[ip]
   if co.displacement_size and ((i.memory_segment==Register.DS and (i.memory_base==Register.NONE and i.memory_index==Register.NONE or i.memory_displacement>=0x2000)) or ip in jt):
    z,n=co.displacement_offset,co.displacement_size;patch[z:z+n]=bytes(n);bindings.append(dict(version=v,function=name,index=j,kind='data_binding',raw=raw.hex(),instruction=fmt.format(i)))
   if i.flow_control in (FlowControl.CALL,FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
    for z,n in ((co.immediate_offset,co.immediate_size),(co.immediate_offset2,co.immediate_size2)):
     if n:patch[z:z+n]=bytes(n)
    bindings.append(dict(version=v,function=name,index=j,kind='call_or_branch',raw=raw.hex(),instruction=fmt.format(i)))
    if i.flow_control!=FlowControl.CALL:edges.append((j,idx[i.near_branch_target],'branch'))
   if ip in jt:
    for k,dst in enumerate(jt[ip]):edges.append((j,idx[dst],'table'));tables.append(dict(version=v,function=name,index=k,record_kind=47+k,target_ip=dst,table_image=cs*16+i.memory_displacement+2*k))
   if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH,FlowControl.INDIRECT_BRANCH):edges.append((j,idx[i.next_ip],'fallthrough_or_call_return'))
   norm.append(patch.hex());ins.append(dict(version=v,function=name,cs=cs,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
  if v=='20':refs[name]=(norm,edges)
  rn,re=refs[name]
  if len(norm)!=len(rn):differences.append(dict(version=v,function=name,index=-1,current=str(len(norm)),DOS20=str(len(rn)),instruction='instruction count differs'))
  else:
   for j,(a,z) in enumerate(zip(norm,rn)):
    if a!=z:differences.append(dict(version=v,function=name,index=j,current=a,DOS20=z,instruction=fmt.format(d[sorted(d)[j]])))
  rows.append(dict(version=v,function=name,start=cs*16+start,instructions=len(d),code_bytes=sum(i.len for i in d.values()),normalized_equal_DOS20=norm==rn,CFG_equal_DOS20=edges==re))
def save(n,rr):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
save('versions',rows);save('instructions',ins);save('masked_bindings',bindings);save('pickup_tables',tables)
if differences:save('normalized_differences',differences)
s=dict(versions=8,bodies=len(rows),normalized_matches=sum(x['normalized_equal_DOS20'] for x in rows),CFG_matches=sum(x['CFG_equal_DOS20'] for x in rows),normalized_differences=len(differences),runtime_tests=0,new_deep_verified_bytes=0,scope='Byte-matched original bounded functions;global/CS-table/call addresses masked explicitly. Other immediates retained. Not allcallee/asset orWin16semantic parity.',files=files+[dict(path=str(Path(__file__).resolve()),sha256=sha(Path(__file__).read_bytes()))]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'}))
