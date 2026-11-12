"""python audit_palette_effect_dos_versions.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

import re
from iced_x86 import Register
root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');prefix=re.compile(b'\x55\x8b\xec\x8b\x16..\x42\x83\x3e..\x02',re.S);helper=b[0x16b0:0x16cd];rows=[];bindings=[];inputs=[]
def normalize(raw,ip):
 code=bytearray(raw);todo=[ip];seen={};edges=[];refs=[]
 while todo:
  q=todo.pop()
  if q in seen:continue
  off=q-ip;assert 0<=off<len(raw);d=Decoder(16,raw[off:],ip=q);i=d.decode();assert not i.is_invalid;seen[q]=i;co=d.get_constant_offsets(i)
  if i.memory_base==Register.NONE and i.memory_index==Register.NONE and co.displacement_size:
   refs.append(dict(instruction_offset=off,kind='absolute_memory',original=str(i.memory_displacement)))
   code[off+co.displacement_offset:off+co.displacement_offset+co.displacement_size]=bytes(co.displacement_size)
  if i.flow_control in (FlowControl.CALL,FlowControl.INDIRECT_CALL):
   for o,n in [(co.immediate_offset,co.immediate_size),(co.immediate_offset2,co.immediate_size2)]:
    if n:code[off+o:off+o+n]=bytes(n)
   refs.append(dict(instruction_offset=off,kind='call_target_not_semantically_bound',original=fmt.format(i)))
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
   todo.append(i.near_branch_target);edges.append((off,i.near_branch_target-ip,'branch'));code[off+co.immediate_offset:off+co.immediate_offset+co.immediate_size]=bytes(co.immediate_size)
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append((off,i.next_ip-ip,'fallthrough_or_call_return'))
 return bytes(code),sorted(edges),refs,len(seen)
refcode,refedges,_,refcount=normalize(b[0xa0cc:0xa199],0x1cfc)
for label in ('10','11','12','15','17','18','19','20'):
 folder=root/('N3D-'+label);imagepath=folder/'unpacked_image.bin';invpath=folder/'instructions.json';v=imagepath.read_bytes();inv=json.loads(invpath.read_text());lookup={x['image_offset']:x for x in inv};locations=[m.start() for m in re.finditer(re.escape(helper),v)];assert len(locations)==1
 matched=[]
 for m in prefix.finditer(v):
  pos=m.start()
  if pos not in lookup:continue
  try:code,edges,refs,count=normalize(v[pos:pos+205],lookup[pos]['ip'])
  except (AssertionError,ValueError):continue
  if code==refcode and edges==refedges:matched.append((pos,refs,count,code,edges))
 assert len(matched)==1,(label,matched)
 pos,refs,count,code,edges=matched[0]
 for x in refs:bindings.append(dict(version_label=label,image_start=pos,**x))
 rows.append(dict(version_label=label,image_sha256=sha(v),instruction_inventory_sha256=sha(invpath.read_bytes()),single_colour_helper_start=locations[0],single_colour_helper_length=29,single_colour_helper_raw_equal=True,flash_start=pos,flash_end_exclusive=pos+205,flash_cs=lookup[pos]['cs'],flash_ip=lookup[pos]['ip'],flash_raw_equal_to_DOS20=v[pos:pos+205]==b[0xa0cc:0xa199],flash_normalized_code_sha256=sha(code),flash_cfg_edges=len(edges),flash_cfg_equal=True,flash_instruction_count=count,scope='byte-exact29B port helper and205B normalized flash layout/CFG; absolute memory and call addresses masked and listed, callee/field semantic binding not closed; no runtime/cross-platform parity'))
 inputs.extend([dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (imagepath,invpath)])
save('dos_version_comparison',rows);save('masked_operand_bindings',bindings)
s=dict(version_labels=8,unique_images=len(set(x['image_sha256'] for x in rows)),single_colour_helper_exact_matches=8,flash_normalized_cfg_matches=8,flash_instruction_count=refcount,failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='8DOS labels/7images; bounded static byte and normalizedCFG comparison only, masked operands explicitly retained; no proof of callee/field semantics, historical version packaging provenance or Win16 behavior',files=inputs+[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
