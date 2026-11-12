"""python audit_guard_move_dos_versions.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

from iced_x86 import Register
def normalize(raw,ip):
 code=bytearray(raw);todo=[ip];seen={};edges=[];refs=[]
 while todo:
  q=todo.pop()
  if q in seen:continue
  off=q-ip;assert 0<=off<len(raw);d=Decoder(16,raw[off:],ip=q);i=d.decode();assert not i.is_invalid;seen[q]=i;co=d.get_constant_offsets(i)
  if i.memory_base==Register.NONE and i.memory_index==Register.NONE and co.displacement_size:
   refs.append(dict(instruction_offset=off,kind='absolute_memory',original=str(i.memory_displacement)))
   code[off+co.displacement_offset:off+co.displacement_offset+co.displacement_size]=bytes(co.displacement_size)
  if i.len==3 and raw[off]==0xb9:
   refs.append(dict(instruction_offset=off,kind='map_segment_immediate_not_semantically_bound',original=str(i.immediate16)));code[off+co.immediate_offset:off+co.immediate_offset+co.immediate_size]=bytes(co.immediate_size)
  if i.flow_control in (FlowControl.CALL,FlowControl.INDIRECT_CALL):
   for o,n in [(co.immediate_offset,co.immediate_size),(co.immediate_offset2,co.immediate_size2)]:
    if n:code[off+o:off+o+n]=bytes(n)
   refs.append(dict(instruction_offset=off,kind='call_target_not_semantically_bound',original=fmt.format(i)))
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
   todo.append(i.near_branch_target);edges.append((off,i.near_branch_target-ip,'branch'));code[off+co.immediate_offset:off+co.immediate_offset+co.immediate_size]=bytes(co.immediate_size)
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append((off,i.next_ip-ip,'fallthrough_or_call_return'))
 return bytes(code),sorted(edges),refs,len(seen)

root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');pattern=bytes.fromhex('c80a000057568b7e0a8b7606ff760c57ff760856');refcode,refedges,refrefs,refcount=normalize(b[0x5092:0x5341],0x422);rows=[];bindings=[];inputs=[]
for label in ('10','11','12','15','17','18','19','20'):
 folder=root/('N3D-'+label);ipath=folder/'unpacked_image.bin';vpath=folder/'instructions.json';v=ipath.read_bytes();inv=json.loads(vpath.read_text());lookupv={x['image_offset']:x for x in inv};assert v.count(pattern)==1;start=v.index(pattern);entry=lookupv[start];owner='%04X:%04X'%(entry['cs'],entry['ip']);owned=[x for x in inv if owner in x['owners']];end=max(x['image_offset']+len(bytes.fromhex(x['bytes'])) for x in owned)
 raw=v[start:end];code,edges,refs,count=normalize(raw,entry['ip'])
 for x in refs:bindings.append(dict(version_label=label,image_start=start,**x))
 rows.append(dict(version_label=label,image_sha256=sha(v),inventory_sha256=sha(vpath.read_bytes()),start=start,end_exclusive=end,span=end-start,cs=entry['cs'],ip=entry['ip'],instruction_count=count,normalized_code_sha256=sha(code),normalized_equal_to_DOS20=code==refcode,cfg_edges=len(edges),cfg_equal_to_DOS20=edges==refedges,raw_equal_to_DOS20=raw==b[0x5092:0x5341],scope='bounded raw/normalized byte and CFG comparison; absolute operands/call/branch addresses and MOVCX map segment masked and listed; semantic callee binding and whole-game behavior not proven'))
 inputs.extend([dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (ipath,vpath)])
save('dos_version_comparison',rows);save('masked_operand_bindings',bindings)
s=dict(version_labels=8,unique_images=len(set(x['image_sha256'] for x in rows)),normalized_code_matches=sum(x['normalized_equal_to_DOS20'] for x in rows),cfg_matches=sum(x['cfg_equal_to_DOS20'] for x in rows),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='8DOSlabels/7images, bounded GUARD movement caller comparison; masked address bindings not semantic closure, no Win16 runtime or whole-game parity',files=inputs+[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
