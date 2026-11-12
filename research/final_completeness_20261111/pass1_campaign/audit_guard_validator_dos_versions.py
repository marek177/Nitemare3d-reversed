"""python audit_guard_validator_dos_versions.py IMAGE INVENTORY DECODER EMULATOR OUT"""
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
def normalize(raw,ip,mask_classification_bases=True):
 code=bytearray(raw);todo=[ip];seen={};edges=[];refs=[]
 while todo:
  q=todo.pop()
  if q in seen:continue
  off=q-ip;assert 0<=off<len(raw);d=Decoder(16,raw[off:],ip=q);i=d.decode();assert not i.is_invalid;seen[q]=i;co=d.get_constant_offsets(i)
  if i.memory_base==Register.NONE and i.memory_index==Register.NONE and co.displacement_size:
   refs.append(dict(instruction_offset=off,kind='absolute_memory',original=str(i.memory_displacement)))
   code[off+co.displacement_offset:off+co.displacement_offset+co.displacement_size]=bytes(co.displacement_size)
  if mask_classification_bases and off in (0x50,0x5b) and i.memory_base==Register.BX and co.displacement_size==2:
   refs.append(dict(instruction_offset=off,kind='indexed_classification_table_base',original=str(i.memory_displacement&65535)));code[off+co.displacement_offset:off+co.displacement_offset+co.displacement_size]=bytes(co.displacement_size)
  if i.len==3 and raw[off] in (0xb8,0xb9):
   refs.append(dict(instruction_offset=off,kind='address_like_MOV_register_immediate_masked',original=str(i.immediate16)));code[off+co.immediate_offset:off+co.immediate_offset+co.immediate_size]=bytes(co.immediate_size)
  if i.flow_control in (FlowControl.CALL,FlowControl.INDIRECT_CALL):
   for o,n in [(co.immediate_offset,co.immediate_size),(co.immediate_offset2,co.immediate_size2)]:
    if n:code[off+o:off+o+n]=bytes(n)
   refs.append(dict(instruction_offset=off,kind='call_target_not_semantically_bound',original=fmt.format(i)))
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
   todo.append(i.near_branch_target);edges.append((off,i.near_branch_target-ip,'branch'));code[off+co.immediate_offset:off+co.immediate_offset+co.immediate_size]=bytes(co.immediate_size)
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append((off,i.next_ip-ip,'fallthrough_or_call_return'))
 return bytes(code),sorted(edges),refs,len(seen)


root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');rows=[];bindings=[];inputs=[]
definitions=[('guard_cell_probe',0x4ec4,0x5092,bytes.fromhex('c80c000057568b7e0e8bc72b06')),('door_record_for_cell',0,0x52,None),('door_state_zero_or_four',0x1e0,0x1fc,b[0x1e0:0x1fc]),('door_state_one',0x1fc,0x212,b[0x1fc:0x212])]
for label in ('10','11','12','15','17','18','19','20'):
 folder=root/('N3D-'+label);ipath=folder/'unpacked_image.bin';vpath=folder/'instructions.json';v=ipath.read_bytes();inv=json.loads(vpath.read_text());look={x['image_offset']:x for x in inv}
 for name,refstart,refend,pattern in definitions:
  if pattern is None:start=0
  else:assert v.count(pattern)==1;start=v.index(pattern)
  entry=look[start];owner='%04X:%04X'%(entry['cs'],entry['ip']);owned=[x for x in inv if owner in x['owners']];end=max(x['image_offset']+len(bytes.fromhex(x['bytes'])) for x in owned)
  refip=0x254 if name=='guard_cell_probe' else refstart;refcode,refedges,_,_=normalize(b[refstart:refend],refip);code,edges,refs,count=normalize(v[start:end],entry['ip']);strict_ref=normalize(b[refstart:refend],refip,False)[0];strict_code=normalize(v[start:end],entry['ip'],False)[0]
  for x in refs:bindings.append(dict(version_label=label,function=name,image_start=start,**x))
  rows.append(dict(version_label=label,function=name,image_sha256=sha(v),inventory_sha256=sha(vpath.read_bytes()),start=start,end_exclusive=end,span=end-start,cs=entry['cs'],ip=entry['ip'],instruction_count=count,normalized_code_sha256=sha(code),normalized_equal_to_DOS20=code==refcode,strict_keep_indexed_bases_equal=strict_code==strict_ref,cfg_edges=len(edges),cfg_equal_to_DOS20=edges==refedges,raw_equal_to_DOS20=v[start:end]==b[refstart:refend],scope='bounded raw/normalizedbytes andCFG; absolute memory/call/branch operands and address-likeMOVAX/CX immediates and twoidentifiedindexedclassificationtable bases masked/listed; strict_keep_indexed_bases comparison retained, semantic bindings notclosed'))
 inputs.extend([dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (ipath,vpath)])
save('dos_version_comparison',rows);save('masked_operand_bindings',bindings)
flag_bases=[x for x in bindings if x['kind']=='indexed_classification_table_base'];assert len(flag_bases)==16
for label in ('10','11','12','15','17','18','19','20'):
 values=[int(x['original']) for x in flag_bases if x['version_label']==label];assert values[1]-values[0]==256
save('indexed_flag_table_bindings',flag_bases)
s=dict(version_labels=8,unique_images=len(set(x['image_sha256'] for x in rows)),function_comparisons=len(rows),strict_keep_indexed_base_matches=sum(x['strict_keep_indexed_bases_equal'] for x in rows),normalized_matches=sum(x['normalized_equal_to_DOS20'] for x in rows),cfg_matches=sum(x['cfg_equal_to_DOS20'] for x in rows),raw_matches=sum(x['raw_equal_to_DOS20'] for x in rows),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='4functions x8DOSlabels/7images, boundedbyte/CFG only; masked data/callee bindings and Win16behavior unclosed',files=inputs+[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
