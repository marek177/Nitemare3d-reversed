"""IMAGE DECODER EMULATOR OUT: whole function comparisons and32 caller-only cases."""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,Register,Mnemonic,OpKind
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
fmt=Formatter(FormatterSyntax.INTEL);sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();out.mkdir(exist_ok=True);root=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');defs=json.loads((out.parent/'cache_reset_replay/summary.json').read_text())['functions'];source=(out.parent/'audit_image_record_versions.py').read_text(encoding='utf-8');exec(source[source.index('def norm('):source.index('for label in (')],globals());comparisons=[];asm=[];cases=[];files=[]
for label in ('10','11','12','15','17','18','19','20'):
 ipath=root/('N3D-'+label)/'instructions.json';vpath=ipath.with_name('unpacked_image.bin');v=vpath.read_bytes();inv=json.loads(ipath.read_text(encoding='utf-8'));lookup={r['image_offset']:r for r in inv};mapped={}
 patterns=[bytes.fromhex(h) for h in (('c8040000568b46060bc0','c80c000057566a02') if label=='10' else ('c806000057568b46060bc0','c806000057566a02'))]
 for f,pattern in zip(defs,patterns):
  hits=[p for p in lookup if v.startswith(pattern,p)];assert len(hits)==1;(start,)=hits;entry=lookup[start];cs,ip=entry['cs'],entry['ip'];owner='%04X:%04X'%(cs,ip);owned=sorted((r for r in inv if owner in r['owners']),key=lambda r:r['ip']);end=max(r['image_offset']+len(bytes.fromhex(r['bytes'])) for r in owned);rc,re,_,_=norm(b[f['start']:f['end_exclusive']],f['start']-(0x7680 if f['name'].startswith('cache_') else 0xd290));vc,ve,n,_=norm(v[start:end],ip);decoded=[]
  for r in owned:
   p=r['image_offset'];i=Decoder(16,bytes.fromhex(r['bytes']),ip=r['ip']).decode();assert v[p:p+i.len].hex()==r['bytes'];decoded.append(i);asm.append(dict(version=label,function=f['name'],cs=cs,ip=i.ip,image_offset=p,bytes=r['bytes'],instruction=fmt.format(i)))
  assert n==len(decoded);mapped[f['name']]=dict(cs=cs,ip=ip,start=start,end=end,decoded=decoded)
  comparisons.append(dict(version=label,function=f['name'],cs=cs,ip=ip,start=start,end_exclusive=end,instructions=n,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in owned),raw_equal_DOS20=v[start:end]==b[f['start']:f['end_exclusive']],normalized_equal_DOS20=vc==rc,CFG_equal_DOS20=ve==re,scope='DOS10 distinct anchors/callee linkage;no forced semantic equivalence of different bodies'))
 clean=mapped['level_resource_cleanup'];dispatch=mapped['cache_lifecycle_dispatch_012'];ins=clean['decoded'];calls=[i for i in ins if i.flow_control==FlowControl.CALL];assert (calls[0].far_branch_selector,calls[0].far_branch16)==(dispatch['cs'],dispatch['ip'])
 counts=[]
 for i in ins:
  if i.mnemonic==Mnemonic.CMP and i.memory_base==Register.NONE and i.memory_index==Register.NONE and i.memory_displacement>0x1000 and i.memory_displacement not in counts:counts.append(i.memory_displacement)
 assert len(counts)==3;wc,oc,ac=counts;wall=next(i.immediate(1) for i in ins if i.mnemonic==Mnemonic.MOV and i.op0_register==Register.SI and i.op1_kind==OpKind.IMMEDIATE16 and i.immediate(1)>0x1000)
 bank=next(i.memory_displacement for i in ins if i.mnemonic==Mnemonic.MOV and i.op0_register==Register.AX and i.memory_base==Register.BX and i.memory_displacement>0x1000);obj=bank-4;world=next(i.memory_displacement for i in ins if i.mnemonic==Mnemonic.MOV and i.op0_register==Register.ES)
 targets={calls[0].far_branch_selector*16+calls[0].far_branch16:'cache_reset'};near=calls[1].far_branch_selector*16+calls[1].far_branch16;targets[near]='near_mark'
 if label=='10':targets[calls[2].far_branch_selector*16+calls[2].far_branch16]='far_pixel_release';assert len(calls)==5
 else:assert len(calls)==4
 for layout in (-1,0,1,3):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,v);ds=0x7000;dg=bytearray([0x66]*0xe030);populated=layout>=0
  for off,value in [(wc,2 if populated else 0),(oc,2 if populated else 0),(ac,3 if populated else 0),(world,0x6000)]:struct.pack_into('<H',dg,off,value)
  expected_events=[('cache_reset',2)]
  if populated:
   for n in range(2):struct.pack_into('<H',dg,wall+8*n,0x9002+0x100*n);expected_events.append(('near_mark',0x9002+0x100*n))
   for n in range(2):
    ptr=0xa002+0x100*n;struct.pack_into('<HHHH',dg,obj+8*n,layout,0,0xb002+0x100*n,ptr)
    for k in range(layout):struct.pack_into('<I',dg,ptr+10*k+6,0x50002000+(n*4+k)*0x100)
    if label=='10':expected_events.extend(('far_pixel_release',0x50002000+(n*4+k)*0x100) for k in range(layout))
    expected_events.append(('near_mark',ptr))
   expected_events.extend([('near_mark',0xb002),('near_mark',0xb102)])
  u.mem_write(ds*16,bytes(dg))
  for n,cls in enumerate((0,0,1)):u.mem_write(0x60000+10+28*n,bytes([cls]))
  frame=struct.pack('<HH',0x100,0x5000);u.mem_write(ds*16+0xf000,frame);events=[];done=[]
  for reg,value in [(UC_X86_REG_CS,clean['cs']),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,value)
  def hook(emu,address,size,data):
   if address==0x50100:done.append(True);emu.emu_stop();return
   if address not in targets:return
   name=targets[address];sp=emu.reg_read(UC_X86_REG_SP);rip,rcs=struct.unpack('<HH',bytes(emu.mem_read(ds*16+sp,4)));n=4 if name=='far_pixel_release' else 2;value=int.from_bytes(bytes(emu.mem_read(ds*16+sp+4,n)),'little');events.append((name,value));emu.reg_write(UC_X86_REG_SP,sp+4);emu.reg_write(UC_X86_REG_CS,rcs);emu.reg_write(UC_X86_REG_IP,rip)
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(clean['start'],0xfffff,count=10000);assert done and events==expected_events,(label,layout,events,expected_events);expected=bytearray(dg)
  if populated:struct.pack_into('<H',expected,bank,0);struct.pack_into('<H',expected,bank+8,0)
  assert bytes(u.mem_read(ds*16,len(dg)))==expected and bytes(u.mem_read(ds*16+0xf000,4))==frame
  for reg,value in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf004),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)]:assert u.reg_read(reg)==value
  cases.append(dict(version=label,layout=layout,object_image_count=max(0,layout),far_pixel_release_calls=sum(n=='far_pixel_release' for n,p in events),near_mark_calls=sum(n=='near_mark' for n,p in events),events=json.dumps(events),status='PASS'))
 files.extend(dict(path=str(p),sha256=sha(p.read_bytes())) for p in (ipath,vpath))
for name,rows in [('function_comparisons',comparisons),('instructions',asm),('caller_cases',cases)]:
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary=dict(comparisons=len(comparisons),raw_matches=sum(r['raw_equal_DOS20'] for r in comparisons),normalized_matches=sum(r['normalized_equal_DOS20'] for r in comparisons),CFG_matches=sum(r['CFG_equal_DOS20'] for r in comparisons),cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='32separate original cleanup-caller cases,load0/DS=SS7000,cache/near-mark/FAR-release dependencies fixtures. DOS10 releases each object imageFAR before its metadata near block;later callers omit per-image release and rely on cache lifecycle. Distinct DOS10 dispatcher/cleanup bodies mapped,not normalized into equivalence. No natural/Win16 parity or centralDOS2case addition.',files=files+[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,out.parent/'cache_reset_replay/summary.json',out.parent/'audit_image_record_versions.py',Path(__file__))]);(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
