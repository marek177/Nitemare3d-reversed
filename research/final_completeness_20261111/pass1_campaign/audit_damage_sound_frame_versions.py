"""VERSION_ROOT CALLER_INSTRUCTIONS_CSV DECODER OUT: bind sound/frame callees from proven caller positions,compare original CFG/table/operands."""
import csv,hashlib,json,struct,sys
from pathlib import Path
root,callerpath,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,Register
out.mkdir(exist_ok=True);sha=lambda x:hashlib.sha256(x).hexdigest();fmt=Formatter(FormatterSyntax.INTEL);caller=list(csv.DictReader(callerpath.open(encoding='utf-8')));records=[];bindings=[];instructions=[];tables=[];diffs=[];refs={};files=[]
for v in ('20','10','11','12','15','17','18','19'):
 image=root/('N3D-'+v)/'unpacked_image.bin';b=image.read_bytes();inv=image.with_name('instructions.json');old={x['image_offset']:x for x in json.loads(inv.read_text(encoding='utf-8'))};cr=[x for x in caller if x['version']==v];assert len(cr)==182
 def target(row):
  raw=bytes.fromhex(row['bytes']);pos=int(row['image_offset']);assert b[pos:pos+len(raw)]==raw;i=Decoder(16,raw,ip=int(row['ip'])).decode();assert i.flow_control==FlowControl.CALL
  if raw[0]==0x9a:return i.far_branch_selector,i.far_branch16
  return int(row['cs']),i.near_branch_target
 entries={'death_sound_event':target(cr[31]),'state7_sound_event':target(cr[84]),'apply_frame_state':target(cr[53])};decoded={}
 for name in ('death_sound_event','state7_sound_event','source_pan_sector','source_relative_bearing','apply_frame_state'):
  cs,entry=entries[name];start=cs*16+entry;todo=[entry];d={};tableip=None;ts=[]
  while todo:
   ip=todo.pop()
   if ip in d:continue
   p=cs*16+ip;assert start<=p<start+600;i=Decoder(16,b[p:p+16],ip=ip).decode();assert not i.is_invalid and old[p]['bytes']==b[p:p+i.len].hex();d[ip]=i
   if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
   if i.flow_control==FlowControl.INDIRECT_BRANCH:
    assert name in ('death_sound_event','state7_sound_event') and tableip is None;tableip=i.memory_displacement;ts=list(struct.unpack_from('<24H',b,cs*16+tableip));todo.extend(ts)
   elif i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
  calls=[i for ip,i in sorted(d.items()) if i.flow_control==FlowControl.CALL]
  if name=='death_sound_event':entries['source_pan_sector']=(calls[-2].far_branch_selector,calls[-2].far_branch16)
  if name=='source_pan_sector':entries['source_relative_bearing']=(cs,calls[0].near_branch_target)
  idx={ip:j for j,ip in enumerate(sorted(d))};norm=[];edges=[]
  for ip,i in sorted(d.items()):
   p=cs*16+ip;raw=b[p:p+i.len];patched=bytearray(raw);dec=Decoder(16,raw,ip=ip);check=dec.decode();co=dec.get_constant_offsets(check);j=idx[ip]
   if co.displacement_size and ((i.memory_segment==Register.DS and i.memory_displacement>=0x2000) or i.flow_control==FlowControl.INDIRECT_BRANCH):
    a,n=co.displacement_offset,co.displacement_size;patched[a:a+n]=bytes(n);bindings.append(dict(version=v,function=name,index=j,kind='global_or_CS_table_base',raw=raw.hex(),asm=fmt.format(i)))
   if i.flow_control in (FlowControl.CALL,FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
    for a,n in ((co.immediate_offset,co.immediate_size),(co.immediate_offset2,co.immediate_size2)):
     if n:patched[a:a+n]=bytes(n)
    bindings.append(dict(version=v,function=name,index=j,kind='call_or_branch',raw=raw.hex(),asm=fmt.format(i)))
    if i.flow_control!=FlowControl.CALL:edges.append((j,idx[i.near_branch_target],'branch'))
   if i.flow_control==FlowControl.INDIRECT_BRANCH:edges.extend((j,idx[t],'type:'+str(k+8)) for k,t in enumerate(ts))
   elif i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):edges.append((j,idx[i.next_ip],'fallthrough_or_call_return'))
   norm.append(patched.hex());instructions.append(dict(version=v,function=name,cs=cs,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
  if v=='20':refs[name]=(norm,edges)
  rn,re=refs[name]
  for j,(a,e) in enumerate(zip(norm,rn)):
   if a!=e:diffs.append(dict(version=v,function=name,index=j,current=a,DOS20=e))
  records.append(dict(version=v,function=name,start=start,end_exclusive=max(cs*16+i.next_ip for i in d.values()),instructions=len(d),code_bytes=sum(i.len for i in d.values()),normalized_equal_DOS20=norm==rn,CFG_equal_DOS20=edges==re))
  tables.extend(dict(version=v,function=name,type=j+8,start=cs*16+tableip+2*j,target_instruction_index=idx[t]) for j,t in enumerate(ts))
 files.extend(dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inv))
def save(n,rows):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save('versions',records);save('instructions',instructions);save('masked_bindings',bindings);save('event_table_bindings',tables)
if diffs:save('normalized_differences',diffs)
s=dict(versions=8,bodies=len(records),normalized_matches=sum(x['normalized_equal_DOS20'] for x in records),CFG_matches=sum(x['CFG_equal_DOS20'] for x in records),normalized_differences=len(diffs),runtime_tests=0,separate_cases=0,new_deep_verified_bytes=0,scope='Caller-bound original code/CFG/table semantics;explicit maskedcall/global operands;not callee/Win16/audio parity.',files=files+[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (callerpath,Path(__file__))]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'}))
