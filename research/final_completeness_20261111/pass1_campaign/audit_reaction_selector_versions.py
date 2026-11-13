"""VERSION_ROOT DECODER OUT: exact original reaction-selector/score instruction+table bindings across DOS versions."""
import csv,hashlib,json,struct,sys
from pathlib import Path
root,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,Register
out.mkdir(exist_ok=True);sha=lambda x:hashlib.sha256(x).hexdigest();fmt=Formatter(FormatterSyntax.INTEL);records=[];instructions=[];bindings=[];tables=[];differences=[];refs={};files=[]
for v in ('20','10','11','12','15','17','18','19'):
 image=root/('N3D-'+v)/'unpacked_image.bin';b=image.read_bytes();inv=image.with_name('instructions.json');old={x['image_offset']:x for x in json.loads(inv.read_text(encoding='utf-8'))}
 for name,pattern,extra in [('target_score_delta','558bec33c9c45e0a2ae4268a4706',None),('death_frame_index','558bec5756c45e0626807f1200',0x59),('hurt_frame_index','558bec5756c45e0626807f1200',0x49)]:
  pat=bytes.fromhex(pattern);hits=[p for p in old if b.startswith(pat,p) and (extra is None or b[p+31:p+35]==bytes([0x80,0x7f,extra,0]))];assert len(hits)==1,(v,name,hits);start=hits[0];cs=old[start]['cs'];entry=old[start]['ip'];todo=[entry];d={};jump=[];tableip=None
  while todo:
   ip=todo.pop()
   if ip in d:continue
   p=cs*16+ip;assert start<=p<start+500;i=Decoder(16,b[p:p+16],ip=ip).decode();assert not i.is_invalid and old[p]['bytes']==b[p:p+i.len].hex();d[ip]=i
   if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
   if i.flow_control==FlowControl.INDIRECT_BRANCH:
    assert name=='target_score_delta' and tableip is None;tableip=i.memory_displacement;jump=list(struct.unpack_from('<25H',b,cs*16+tableip));todo.extend(jump)
   elif i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
  idx={ip:j for j,ip in enumerate(sorted(d))};norm=[];edges=[]
  for ip,i in sorted(d.items()):
   p=cs*16+ip;raw=b[p:p+i.len];patched=bytearray(raw);dec=Decoder(16,raw,ip=ip);check=dec.decode();co=dec.get_constant_offsets(check);j=idx[ip]
   if co.displacement_size and ((i.memory_segment==Register.DS and i.memory_displacement>=0x2000) or i.flow_control==FlowControl.INDIRECT_BRANCH):
    a,n=co.displacement_offset,co.displacement_size;patched[a:a+n]=bytes(n);bindings.append(dict(version=v,function=name,index=j,kind='data_or_CS_table_base',raw=raw.hex(),asm=fmt.format(i)))
   if i.flow_control in (FlowControl.CALL,FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
    for a,n in ((co.immediate_offset,co.immediate_size),(co.immediate_offset2,co.immediate_size2)):
     if n:patched[a:a+n]=bytes(n)
    bindings.append(dict(version=v,function=name,index=j,kind='call_branch',raw=raw.hex(),asm=fmt.format(i)))
    if i.flow_control!=FlowControl.CALL:edges.append((j,idx[i.near_branch_target],'branch'))
   if i.flow_control==FlowControl.INDIRECT_BRANCH:edges.extend((j,idx[t],'type:'+str(k+8)) for k,t in enumerate(jump))
   elif i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):edges.append((j,idx[i.next_ip],'fallthrough_or_call_return'))
   norm.append(patched.hex());instructions.append(dict(version=v,function=name,cs=cs,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
  current=(norm,edges)
  if v=='20':refs[name]=current
  ref=refs[name]
  for j,(a,e) in enumerate(zip(norm,ref[0])):
   if a!=e:differences.append(dict(version=v,function=name,index=j,current=a,DOS20=e))
  records.append(dict(version=v,function=name,start=start,end_exclusive=max(cs*16+i.next_ip for i in d.values()),instructions=len(d),code_bytes=sum(i.len for i in d.values()),normalized_equal_DOS20=norm==ref[0],CFG_equal_DOS20=edges==ref[1]))
  tables.extend(dict(version=v,type=k+8,table_image=cs*16+tableip+2*k,target_instruction_index=idx[t]) for k,t in enumerate(jump))
 files.extend(dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inv))
def save(n,r):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(r[0]));w.writeheader();w.writerows(r)
save('versions',records);save('instructions',instructions);save('masked_bindings',bindings);save('score_table_bindings',tables)
if differences:save('normalized_differences',differences)
s=dict(versions=8,bodies=len(records),normalized_matches=sum(x['normalized_equal_DOS20'] for x in records),CFG_matches=sum(x['CFG_equal_DOS20'] for x in records),normalized_differences=len(differences),runtime_tests=0,separate_cases=0,new_deep_verified_bytes=0,scope='Original byte-matched code/CFG/table-branch mappings with explicit masked call/global bindings; not actualDOS/Win16/gameplay parity.',files=files+[dict(path=str(Path(__file__).resolve()),sha256=sha(Path(__file__).read_bytes()))]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'}))
