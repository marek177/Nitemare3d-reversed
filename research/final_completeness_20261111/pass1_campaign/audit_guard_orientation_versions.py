"""python audit_guard_orientation_versions.py IMAGE REPLAY_DIR DECODER OUT"""
import csv,hashlib,json,sys
from pathlib import Path
image,replay,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()));out.mkdir(exist_ok=True)
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,Register
b=image.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();fmt=Formatter(FormatterSyntax.INTEL);root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');functions=json.loads((replay/'summary.json').read_text(encoding='utf-8'))['functions'];rows=[];bindings=[];inputs=[]
patterns=[bytes.fromhex(x) for x in ('558bec568b560a0bd2','c804000057568b7e0a8b7606ff760c','c80800005756c44e088bd9')]
def norm(raw,ip):
 todo=[ip];seen={};edges=[];code=bytearray(raw);refs=[]
 while todo:
  q=todo.pop()
  if q in seen:continue
  off=q-ip;assert 0<=off<len(raw);d=Decoder(16,raw[off:],ip=q);i=d.decode();assert not i.is_invalid;seen[q]=i;co=d.get_constant_offsets(i)
  if co.displacement_size and ((i.memory_base==Register.NONE and i.memory_index==Register.NONE) or (i.memory_segment==Register.DS and i.memory_base==Register.BX and (i.memory_displacement&65535)>=0x3000)):
   refs.append(dict(offset=off,kind='global_or_indexed_binding',original=fmt.format(i)));code[off+co.displacement_offset:off+co.displacement_offset+co.displacement_size]=bytes(co.displacement_size)
  if i.flow_control in (FlowControl.CALL,FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
   for o,n in ((co.immediate_offset,co.immediate_size),(co.immediate_offset2,co.immediate_size2)):
    if n:code[off+o:off+o+n]=bytes(n)
   refs.append(dict(offset=off,kind='call_or_branch_address',original=fmt.format(i)))
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append((off,i.near_branch_target-ip,'branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append((off,i.next_ip-ip,'fallthrough_or_call_return'))
 return bytes(code),sorted(edges),len(seen),refs
for label in ('10','11','12','15','17','18','19','20'):
 p=root/('N3D-'+label)/'unpacked_image.bin';v=p.read_bytes();ipath=p.with_name('instructions.json');inv=json.loads(ipath.read_text(encoding='utf-8'));look={r['image_offset']:r for r in inv}
 for f,pat in zip(functions,patterns):
  assert v.count(pat)==1,(label,f['name'],v.count(pat));start=v.index(pat);entry=look[start];owner='%04X:%04X'%(entry['cs'],entry['ip']);end=max(r['image_offset']+len(bytes.fromhex(r['bytes'])) for r in inv if owner in r['owners']);cs=(0xaea if f['name']=='actor_to_player_view_octant' else 0x4c7);rc,re,ri,_=norm(b[f['start']:f['end_exclusive']],f['start']-cs*16);vc,ve,vi,refs=norm(v[start:end],entry['ip'])
  rows.append(dict(version=label,function=f['name'],start=start,end_exclusive=end,cs=entry['cs'],ip=entry['ip'],instructions=vi,raw_equal_DOS20=v[start:end]==b[f['start']:f['end_exclusive']],normalized_equal_DOS20=vc==rc,CFG_equal_DOS20=ve==re,image_sha256=sha(v)))
  bindings.extend(dict(version=label,function=f['name'],**r) for r in refs)
 inputs.extend(dict(path=str(q),sha256=sha(q.read_bytes())) for q in (p,ipath))
for name,rs in [('function_comparisons',rows),('masked_bindings',bindings)]:
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
s=dict(comparisons=len(rows),version_labels=8,unique_images=len(set(r['image_sha256'] for r in rows)),raw_matches=sum(r['raw_equal_DOS20'] for r in rows),normalized_matches=sum(r['normalized_equal_DOS20'] for r in rows),CFG_matches=sum(r['CFG_equal_DOS20'] for r in rows),runtime_tests=0,new_deep_verified_bytes=0,scope='bounded3function byte/CFG comparisons, global/indexed bindings and call/branch addresses masked/listed, recordfield/mode constants preserved; no data/callee/natural initialized-state/Win16 parity',files=inputs+[dict(path=str(q.resolve()),sha256=sha(q.read_bytes())) for q in (image,replay/'summary.json',Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
