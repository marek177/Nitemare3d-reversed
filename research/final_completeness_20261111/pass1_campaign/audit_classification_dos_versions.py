"""python audit_classification_dos_versions.py DECODER OUT
Three bounded functions; mask only identified address operands, preserve flag constants.
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()));out.mkdir(exist_ok=True)
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,Register
root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');fmt=Formatter(FormatterSyntax.INTEL);sha=lambda b:hashlib.sha256(b).hexdigest();rows=[];bindings=[];files=[];refs={}
def find(b,name):
 pattern=bytes.fromhex('c80200005633f6' if name!='rtc_irq8_increment_cached_clock' else '66601e068bec1e');hits=[];q=0
 while True:
  q=b.find(pattern,q)
  if q<0:break
  if name=='rtc_irq8_increment_cached_clock' or b[q+11:q+16]==bytes.fromhex('2af683fa'+('01' if name=='tile_flags_generate' else '06')):hits.append(q)
  q+=1
 assert len(hits)==1,(name,hits);return hits[0]
def norm(b,start,ip,end,irq):
 code=bytearray(b[start:end]);todo=[ip];seen={};edges=[];refs=[]
 while todo:
  q=todo.pop()
  if q in seen:continue
  off=q-ip;assert 0<=off<len(code);d=Decoder(16,b[start+off:end],ip=q);i=d.decode();assert not i.is_invalid;seen[q]=i;co=d.get_constant_offsets(i)
  if co.displacement_size and ((i.memory_base==Register.SI and (i.memory_displacement&65535)>0x8000) or (i.memory_base==Register.NONE and i.memory_index==Register.NONE)):
   refs.append(dict(instruction_offset=off,kind='indexed_table_base' if i.memory_base==Register.SI else 'absolute_counter',original=i.memory_displacement&65535));code[off+co.displacement_offset:off+co.displacement_offset+co.displacement_size]=bytes(co.displacement_size)
  if irq and off==7:
   assert b[start+off]==0xb8;refs.append(dict(instruction_offset=off,kind='canonical_DGROUP_segment',original=i.immediate16));code[off+co.immediate_offset:off+co.immediate_offset+co.immediate_size]=bytes(co.immediate_size)
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append((off,i.near_branch_target-ip,'branch'));code[off+co.immediate_offset:off+co.immediate_offset+co.immediate_size]=bytes(co.immediate_size)
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append((off,i.next_ip-ip,'fallthrough'))
 return bytes(code),sorted(edges),len(seen),refs
for label in ('20','10','11','12','15','17','18','19'):
 p=root/('N3D-'+label)/'unpacked_image.bin';v=p.read_bytes();invpath=p.with_name('instructions.json');inv=json.loads(invpath.read_text(encoding='utf-8'));lookup={x['image_offset']:x for x in inv}
 for name in ('tile_flags_generate','occupancy_flags_generate','rtc_irq8_increment_cached_clock'):
  start=find(v,name);irq=name.startswith('rtc_')
  if irq:ip=2;end=start+37
  else:
   r=lookup[start];ip=r['ip'];owner='%04X:%04X'%(r['cs'],ip);end=max(x['image_offset']+len(bytes.fromhex(x['bytes'])) for x in inv if owner in x['owners'])
  code,edges,count,operands=norm(v,start,ip,end,irq)
  if label=='20':refs[name]=(v[start:end],code,edges)
  reference,refcode,refedges=refs[name]
  rows.append(dict(version=label,function=name,start=start,end_exclusive=end,span=end-start,instructions=count,raw_equal_DOS20=v[start:end]==reference,normalized_equal_DOS20=code==refcode,CFG_equal_DOS20=edges==refedges,image_sha256=sha(v)))
  for x in operands:bindings.append(dict(version=label,function=name,**x))
 files.extend(dict(path=str(q),sha256=sha(q.read_bytes())) for q in (p,invpath))
for name,rs in [('function_comparisons',rows),('masked_address_bindings',bindings)]:
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
s=dict(version_labels=8,unique_images=len(set(r['image_sha256'] for r in rows)),comparisons=len(rows),raw_matches=sum(r['raw_equal_DOS20'] for r in rows),normalized_matches=sum(r['normalized_equal_DOS20'] for r in rows),CFG_matches=sum(r['CFG_equal_DOS20'] for r in rows),new_deep_verified_bytes=0,runtime_tests=0,scope='bounded three-function raw/CFG/address-aware comparison, semantic range/bit masks preserved; masked DS/table bindings listed but natural initialization/behavior/Win16 unproved',files=files+[dict(path=str(Path(__file__).resolve()),sha256=sha(Path(__file__).read_bytes()))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
