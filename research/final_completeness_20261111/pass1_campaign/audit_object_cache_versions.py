"""python audit_object_cache_versions.py IMAGE REPLAY_DIR DECODER OUT"""
import csv,hashlib,json,sys
from pathlib import Path
image,replay,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()));out.mkdir(exist_ok=True)
from iced_x86 import Decoder,FlowControl,Formatter,FormatterSyntax,Register
b=image.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();fmt=Formatter(FormatterSyntax.INTEL);root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');defs=json.loads((replay/'summary.json').read_text(encoding='utf-8'))['functions'];patterns=[bytes.fromhex(h) for h in ('c806000057568e06',)];rows=[];bindings=[];files=[]
def norm(raw,ip):
 todo=[ip];seen={};edges=[];code=bytearray(raw);refs=[]
 while todo:
  q=todo.pop()
  if q in seen:continue
  off=q-ip;assert 0<=off<len(raw);d=Decoder(16,raw[off:],ip=q);i=d.decode();assert not i.is_invalid;seen[q]=i;co=d.get_constant_offsets(i)
  if co.displacement_size and i.memory_base==Register.NONE and i.memory_index==Register.NONE:
   refs.append(dict(offset=off,kind='absolute_binding',original=fmt.format(i)));code[off+co.displacement_offset:off+co.displacement_offset+co.displacement_size]=bytes(co.displacement_size)
  if i.flow_control in (FlowControl.CALL,FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
   refs.append(dict(offset=off,kind='call_branch_binding',original=fmt.format(i)))
   for o,n in ((co.immediate_offset,co.immediate_size),(co.immediate_offset2,co.immediate_size2)):
    if n:code[off+o:off+o+n]=bytes(n)
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append((off,i.near_branch_target-ip,'branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append((off,i.next_ip-ip,'fallthrough_or_call_return'))
 return bytes(code),sorted(edges),len(seen),refs
for label in ('10','11','12','15','17','18','19','20'):
 p=root/('N3D-'+label)/'unpacked_image.bin';v=p.read_bytes();ipath=p.with_name('instructions.json');inv=json.loads(ipath.read_text(encoding='utf-8'));lookup={r['image_offset']:r for r in inv}
 for f,pat in zip(defs,patterns):
  hits=[i for i in lookup if v.startswith(pat,i)]
  if f['name']=='image_record_index_or_cache':hits=[i for i in hits if v[i+13:i+20]==bytes.fromhex('8b760856ff7606')]
  row=dict(version=label,function=f['name'],status='COMPARED',candidate_count=len(hits),cs=None,ip=None,start=None,end_exclusive=None,instructions=None,raw_equal_DOS20=None,normalized_equal_DOS20=None,CFG_equal_DOS20=None,image_sha256=sha(v))
  if label=='10' and f['name']=='image_record_index_or_cache':row['status']='UNMAPPED_DOS10_SPLIT_DECODERS';rows.append(row);continue
  if len(hits)!=1:row['status']='UNMAPPED_OR_AMBIGUOUS';rows.append(row);continue
  start=hits[0];entry=lookup[start];owner='%04X:%04X'%(entry['cs'],entry['ip']);end=max(r['image_offset']+len(bytes.fromhex(r['bytes'])) for r in inv if owner in r['owners']);refcs=0x768;rc,re,_,_=norm(b[f['start']:f['end_exclusive']],f['start']-refcs*16);vc,ve,n,refs=norm(v[start:end],entry['ip']);row.update(cs=entry['cs'],ip=entry['ip'],start=start,end_exclusive=end,instructions=n,raw_equal_DOS20=v[start:end]==b[f['start']:f['end_exclusive']],normalized_equal_DOS20=vc==rc,CFG_equal_DOS20=ve==re);rows.append(row);bindings.extend(dict(version=label,function=f['name'],**r) for r in refs)
 files.extend(dict(path=str(q),sha256=sha(q.read_bytes())) for q in (p,ipath))
for name,rs in [('function_comparisons',rows),('masked_bindings',bindings)]:
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
s=dict(attempted=len(rows),compared=sum(r['status']=='COMPARED' for r in rows),unmapped=sum(r['status']!='COMPARED' for r in rows),raw_matches=sum(r['raw_equal_DOS20'] is True for r in rows),normalized_matches=sum(r['normalized_equal_DOS20'] is True for r in rows),CFG_matches=sum(r['CFG_equal_DOS20'] is True for r in rows),runtime_tests=0,new_deep_verified_bytes=0,scope='independent prologue+inventory bounds, absolute/call/branch addresses masked; string addresses/constants retained; objectcache counterparts bounded by retained owners; no allocation/XMS environment equivalence; no initializeddata/callee/Win16 parity',files=files+[dict(path=str(q.resolve()),sha256=sha(q.read_bytes())) for q in (image,replay/'summary.json',Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
