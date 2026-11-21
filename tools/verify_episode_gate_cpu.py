"""Isolated original-byte selector1/2 and invalid-selector contracts; no game coverage."""
import sys,json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R.parent/'goal-x20/work/deps'))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
raw=Path('C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe').read_bytes();h=hashlib.sha256(raw).hexdigest();assert h=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';im=raw[int.from_bytes(raw[8:10],'little')*16:];CS=0x83d;SS=0x3000;stop=0x60000;u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(CS*16+0x29ca,im[CS*16+0x29ca:CS*16+0x2ad7]);pcs=[]
def hook(mu,a,n,_):
 if a==stop:mu.emu_stop()
 else:pcs.append(a-CS*16)
u.hook_add(UC_HOOK_CODE,hook);digest=hashlib.sha256();cases=0
for ds in (0x2771,0x4000):
 for selector in (1,2,6,65535):
  for value in range(256) if selector in (1,2) else (0,):
   flags=0x202|(0x400 if value&1 else 0)
   for reg,val in [(UC_X86_REG_CS,CS),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,SS),(UC_X86_REG_ES,0x5000),(UC_X86_REG_SP,0x8000),(UC_X86_REG_BP,0x7777),(UC_X86_REG_SI,0x8888),(UC_X86_REG_DI,0x9999),(UC_X86_REG_CX,0xabcd),(UC_X86_REG_EFLAGS,flags)]:u.reg_write(reg,val)
   u.mem_write(SS*16+0x8000,struct.pack('<HHH',0,0x6000,selector));u.mem_write(SS*16+0x7ffa,struct.pack('<HH',0x1234,0x5678));u.mem_write(ds*16+0x363b,bytes([value]));pcs.clear();u.emu_start(CS*16+0x29ca,0xfffff,count=40)
   ax=u.reg_read(UC_X86_REG_AX);dx=u.reg_read(UC_X86_REG_DX);expected=(0x363b,ds) if selector==1 and value else (0,0) if selector==1 else (0x363c,ds) if selector==2 else (0x1234,0x5678)
   assert (ax,dx)==expected
   for reg,val in [(UC_X86_REG_SP,0x8004),(UC_X86_REG_CS,0x6000),(UC_X86_REG_IP,0),(UC_X86_REG_BP,0x7777),(UC_X86_REG_SI,0x8888),(UC_X86_REG_DI,0x9999),(UC_X86_REG_CX,0xabcd),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,SS),(UC_X86_REG_ES,0x5000)]:assert u.reg_read(reg)==val
   assert u.reg_read(UC_X86_REG_EFLAGS)&0x600==flags&0x600
   assert (0x2a7c in pcs)==(selector==1) and (0x2a90 in pcs)==(selector==2)
   digest.update(struct.pack('<HHHHH',ds,selector,value,ax,dx));cases+=1
table=struct.unpack('<6H',im[CS*16+0x29e0:CS*16+0x29ec]);assert table==(0x29f2,0x2a7c,0x2a90,0x2a9a,0x2aa8,0x2ab6)
v={'status':'SYNTHETIC_ORIGINAL_CPU_ONLY','cases':cases,'source_sha256':h,'span_sha256':hashlib.sha256(im[CS*16+0x29ca:CS*16+0x2ad7]).hexdigest(),'switch_targets':[f'{x:04X}' for x in table],'selector1':'DX:AX=DS:363B iff byteDS363B!=0, else0:0; pointer, not byte value','selector2':'DX:AX=DS:363C','invalid_selector_cases':'6 andFFFF expose incoming uninitialized stack locals atBP-4/BP-2; not a safe general query API','preserved_fixture':'BP,SI,DI,CX,DS,SS,ES,IF/DF; FAR frame/argument checked','case_digest_sha256':digest.hexdigest(),'scope':'Selectors0/3/4/5 invoke unexecuted callees; no arbitrary alias/IRQ/domain/nativeWin16 parity claim.'}
o=R/'outputs/episode3_p_continuation_20261107';o.mkdir(exist_ok=True);(o/'gate_CPU_validation.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
