"""python audit_worx_register_bank_versions.py IMAGE REPLAY_DIR DECODER OUT
Compare anchored WORX bank/consumers across retained DOS labels; do not assume Win parity.
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,replay,decoder,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(decoder.resolve()));out.mkdir(exist_ok=True)
from iced_x86 import Decoder,FlowControl,Register,OpKind
ref=image.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();anchor=ref[0x18103:0x18103+44];assert ref.count(anchor)==1
functions=json.loads((replay/'summary.json').read_text(encoding='utf-8'))['functions'];root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');rows=[];banks=[];inputs=[];bindings=[]
def cfg(raw,ip):
 todo=[ip];seen={};edges=[]
 while todo:
  q=todo.pop()
  if q in seen:continue
  assert 0<=q-ip<len(raw);i=Decoder(16,raw[q-ip:],ip=q).decode();assert not i.is_invalid;seen[q]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append((q-ip,i.near_branch_target-ip,'branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append((q-ip,i.next_ip-ip,'fallthrough'))
 code=bytearray(raw);refs=[]
 for q,i in seen.items():
  off=q-ip;d=Decoder(16,raw[off:],ip=q);j=d.decode();co=d.get_constant_offsets(j)
  if co.displacement_size and i.memory_segment==Register.CS:
   refs.append(dict(instruction_offset=off,kind='CS_memory_displacement',original=i.memory_displacement&65535));code[off+co.displacement_offset:off+co.displacement_offset+co.displacement_size]=bytes(co.displacement_size)
  if i.op0_kind==OpKind.REGISTER and i.op0_register in (Register.SI,Register.DI) and i.op_count==2 and i.op1_kind==OpKind.IMMEDIATE16:
   refs.append(dict(instruction_offset=off,kind='SI_DI_address_immediate',original=i.immediate16));code[off+co.immediate_offset:off+co.immediate_offset+co.immediate_size]=bytes(co.immediate_size)
  if i.flow_control in (FlowControl.CALL,FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
   if co.immediate_size:code[off+co.immediate_offset:off+co.immediate_offset+co.immediate_size]=bytes(co.immediate_size)
 return sorted(edges),len(seen),bytes(code),refs
for label in ('10','11','12','15','17','18','19','20'):
 p=root/('N3D-'+label)/'unpacked_image.bin';b=p.read_bytes();invpath=p.with_name('instructions.json');inv=json.loads(invpath.read_text(encoding='utf-8'));lookup={r['image_offset']:r for r in inv}
 hits=[q for q in range(len(b)) if b.startswith(anchor,q)];assert len(hits)==1,(label,hits);bank=hits[0]
 patterns={'worx_bank_override_SB_record':bytes.fromhex('535156571e06268b053d5342'),'worx_bank_program_voice':bytes.fromhex('5053575256be'),'worx_port_callback_set':bytes.fromhex('fa2e891e'),'worx_port_write_delayed':bytes.fromhex('50535152ba8803ee')}
 locations={}
 for name,pat in patterns.items():
  hs=[q for q in range(len(b)) if b.startswith(pat,q) and q in lookup]
  if name=='worx_bank_program_voice':hs=[q for q in hs if b[q+8:q+12]==bytes.fromhex('53b80b00')]
  assert len(hs)==1,(label,name,hs);locations[name]=hs[0]
 hs=[q for q in lookup if b[q]==0xe8 and b[q+3:q+6]==bytes.fromhex('33dbbe') and b[q+8:q+14]==bytes.fromhex('83c704b90b00')];assert len(hs)==1,(label,hs);locations['worx_bank_load_128x11']=hs[0]
 base=lookup[locations['worx_bank_program_voice']]['cs']*16;assert locations['worx_bank_program_voice']>=base
 assert struct.unpack_from('<H',b,locations['worx_bank_program_voice']+6)[0]==bank-base
 banks.append(dict(version=label,bank_start=bank,bank_end_exclusive=bank+1408,CS=base//16,bank_sha256=sha(b[bank:bank+1408]),raw_equal_DOS20=b[bank:bank+1408]==ref[0x18103:0x18683],image_sha256=sha(b)))
 for f in functions:
  start=locations[f['name']];entry=lookup[start];ip=entry['ip'];owner='%04X:%04X'%(entry['cs'],ip);owned=[r for r in inv if owner in r['owners']];end=max(r['image_offset']+len(bytes.fromhex(r['bytes'])) for r in owned)
  rc,re,rnorm,_=cfg(ref[f['start']:f['end_exclusive']],f['start']-0x15bf0);vc,ve,vnorm,operands=cfg(b[start:end],ip)
  bindings.extend(dict(version=label,function=f['name'],**x) for x in operands)
  rows.append(dict(version=label,function=f['name'],cs=entry['cs'],ip=ip,start=start,end_exclusive=end,instructions=ve,raw_equal_DOS20=b[start:end]==ref[f['start']:f['end_exclusive']],normalized_equal_DOS20=vnorm==rnorm,CFG_equal_DOS20=vc==rc))
 inputs.extend(dict(path=str(q),sha256=sha(q.read_bytes())) for q in (p,invpath))
for name,rs in [('function_comparisons',rows),('bank_comparisons',banks),('masked_address_bindings',bindings)]:
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
s=dict(version_labels=8,unique_images=len(set(x['image_sha256'] for x in banks)),functions_compared=len(rows),raw_function_matches=sum(x['raw_equal_DOS20'] for x in rows),normalized_matches=sum(x['normalized_equal_DOS20'] for x in rows),CFG_matches=sum(x['CFG_equal_DOS20'] for x in rows),bank_matches=sum(x['raw_equal_DOS20'] for x in banks),runtime_tests=0,new_deep_verified_bytes=0,scope='5function bytes/CFG and full1408B bank; entries independently anchored/inventory bounded; CS memory displacements,SI/DI address immediates and call/branch operands masked for normalized comparisons; no runtime initialized-bank/callback/hardware/Win16 parity',files=inputs+[dict(path=str(q.resolve()),sha256=sha(q.read_bytes())) for q in (image,replay/'summary.json',Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
