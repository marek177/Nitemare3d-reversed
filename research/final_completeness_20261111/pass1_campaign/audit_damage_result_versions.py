"""VERSION_ROOT DECODER OUT: byte/CFG comparisons for damage-result consumer, all masked call/data operands retained."""
import csv,hashlib,json,sys,struct
from pathlib import Path
root,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()))
from iced_x86 import Decoder,FlowControl,Register,OpKind,Formatter,FormatterSyntax
out.mkdir(exist_ok=True);sha=lambda x:hashlib.sha256(x).hexdigest();fmt=Formatter(FormatterSyntax.INTEL);results=[];bindings=[];instructions=[];files=[];reference=None;differences=[]
for version in ('20','10','11','12','15','17','18','19'):
 p=root/('N3D-'+version)/'unpacked_image.bin';b=p.read_bytes();inv=p.with_name('instructions.json');old={r['image_offset']:r for r in json.loads(inv.read_text(encoding='utf-8'))};pattern=bytes.fromhex('c802000057568b7e0a8b7606');hits=[i for i in range(len(b)) if b.startswith(pattern,i) and b[i+0x19:i+0x1e]==bytes.fromhex('83c4082ae4')];assert len(hits)==1;start=hits[0];cs=old[start]['cs'];entry=old[start]['ip'];todo=[entry];d={};table=[];tableip=None
 while todo:
  ip=todo.pop()
  if ip in d:continue
  pos=cs*16+ip;assert start<=pos<start+1000;i=Decoder(16,b[pos:pos+16],ip=ip).decode();assert not i.is_invalid and old[pos]['bytes']==b[pos:pos+i.len].hex();d[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
  if i.flow_control==FlowControl.INDIRECT_BRANCH:
   assert i.memory_segment==Register.CS and tableip is None;tableip=i.memory_displacement;table=list(struct.unpack_from('<19H',b,cs*16+tableip));todo.extend(set(table))
  elif i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
 offsets={ip:j for j,ip in enumerate(sorted(d))};norm=[];edges=[]
 for ip,i in sorted(d.items()):
  pos=cs*16+ip;raw=b[pos:pos+i.len];patched=bytearray(raw);dec=Decoder(16,raw,ip=ip);ii=dec.decode();co=dec.get_constant_offsets(ii);j=offsets[ip]
  if co.displacement_size and i.memory_displacement>=0x2000 and i.memory_segment in (Register.DS,Register.SS,Register.CS):
   a,n=co.displacement_offset,co.displacement_size;patched[a:a+n]=bytes(n);bindings.append(dict(version=version,index=j,kind='data_displacement',raw=raw.hex(),asm=fmt.format(i)))
  if i.flow_control in (FlowControl.CALL,FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
   for a,n in ((co.immediate_offset,co.immediate_size),(co.immediate_offset2,co.immediate_size2)):
    if n:patched[a:a+n]=bytes(n)
   bindings.append(dict(version=version,index=j,kind='call_or_branch',raw=raw.hex(),asm=fmt.format(i)))
   if i.flow_control!=FlowControl.CALL:edges.append((j,offsets[i.near_branch_target],'branch'))
  if i.flow_control==FlowControl.INDIRECT_BRANCH:
   a,n=co.displacement_offset,co.displacement_size;patched[a:a+n]=bytes(n);edges.extend((j,offsets[t],'table:'+str(k+3)) for k,t in enumerate(table))
  elif i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):edges.append((j,offsets[i.next_ip],'fallthrough_or_call_return'))
  norm.append(patched.hex());instructions.append(dict(version=version,cs=cs,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
 current=(norm,edges)
 if reference is None:reference=current
 for j,(current_hex,baseline_hex) in enumerate(zip(norm,reference[0])):
  if current_hex!=baseline_hex:differences.append(dict(version=version,instruction_index=j,current_masked_bytes=current_hex,DOS20_masked_bytes=baseline_hex,current_instruction=fmt.format(d[sorted(d)[j]])))
 end=max(cs*16+i.next_ip for i in d.values());results.append(dict(version=version,start=start,end_exclusive=end,instructions=len(d),code_bytes=sum(i.len for i in d.values()),normalized_code_CFG_equal_DOS20=current==reference,CFG_equal_DOS20=edges==reference[1],jump_table_start=cs*16+tableip,jump_table_sha256=sha(b[cs*16+tableip:cs*16+tableip+38]),span_sha256=sha(b[start:end])))
 files.extend(dict(path=str(q.resolve()),sha256=sha(q.read_bytes())) for q in (p,inv))
def save(n,rows):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save('normalized_differences',differences);save('versions',results);save('masked_bindings',bindings);save('instructions',instructions);s=dict(versions=8,normalized_matches=sum(x['normalized_code_CFG_equal_DOS20'] for x in results),CFG_matches=sum(x['CFG_equal_DOS20'] for x in results),normalized_instruction_differences=len(differences),runtime_tests=0,separate_cases=0,status_changes=0,new_deep_verified_bytes=0,scope='Bounded code shapes/CFG/jump-table dispatch; masked calltargets/global displacements retained. Not callee/runtime/Win16 parity.',files=files+[dict(path=str(Path(__file__).resolve()),sha256=sha(Path(__file__).read_bytes()))]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'}))
