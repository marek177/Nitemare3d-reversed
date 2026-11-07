"""Isolated original constructor type18/19 and all wall-class overrides."""
import sys,json,struct,hashlib
from pathlib import Path
sys.path.insert(0,'C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20/work/deps')
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
R=Path(__file__).resolve().parents[1];raw=Path('C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe').read_bytes();H=lambda b:hashlib.sha256(b).hexdigest();assert H(raw)=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';im=raw[int.from_bytes(raw[8:10],'little')*16:]
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);CS=0x83d;DS=0x2771;ACT=0x5000;OBJ=0x5100;MAP=0x5200
u.mem_write(CS*16+0x117a,im[CS*16+0x117a:CS*16+0x1275]);u.mem_write(DS*16+0x2562,struct.pack('<H',OBJ));u.mem_write(OBJ*16+18,struct.pack('<HH',0x100,MAP));u.mem_write(MAP*16+0x100,b'\x25');u.hook_add(UC_HOOK_CODE,lambda mu,a,s,d:mu.emu_stop() if a==0x60000 else None)
count=0;hist={}
for typ in (18,19):
 for cls in range(256):
  for x,y in ((0,0),(0,1),(1,0),(1,1)):
   actor=bytearray(range(26));actor[8:10]=b'\0\0';actor[19]=x;actor[20]=y;u.mem_write(ACT*16+0x100,bytes(actor));u.mem_write(OBJ*16+12,bytes([typ]));u.mem_write(DS*16+0xd30e+0x25,bytes([cls]));u.mem_write(DS*16+0x8000,struct.pack('<6H',0,0x6000,0x100,ACT,6,OBJ))
   for reg,val in [(UC_X86_REG_AX,0xaaaa),(UC_X86_REG_BX,0xbbbb),(UC_X86_REG_CX,0xcccc),(UC_X86_REG_DX,0xdddd),(UC_X86_REG_SI,0x1234),(UC_X86_REG_DI,0x5678),(UC_X86_REG_BP,0x7788),(UC_X86_REG_CS,CS),(UC_X86_REG_DS,DS),(UC_X86_REG_SS,DS),(UC_X86_REG_ES,DS),(UC_X86_REG_SP,0x8000),(UC_X86_REG_EFLAGS,0x602)]:u.reg_write(reg,val)
   u.emu_start(CS*16+0x117a,0xfffff,count=300)
   assert (u.reg_read(UC_X86_REG_CS),u.reg_read(UC_X86_REG_IP),u.reg_read(UC_X86_REG_SP))==(0x6000,0,0x8004)
   for reg,val in [(UC_X86_REG_SI,0x1234),(UC_X86_REG_DI,0x5678),(UC_X86_REG_BP,0x7788),(UC_X86_REG_DS,DS),(UC_X86_REG_CX,0xcccc),(UC_X86_REG_DX,0xdddd)]:assert u.reg_read(reg)==val
   mode=2 if cls in (0x42,0x46) else 1 if cls==0x43 else 3;state=8 if x or y else 7;expected=bytearray(actor);expected[10]=mode;expected[11]=state;expected[12]=2;expected[22]=0
   assert bytes(u.mem_read(ACT*16+0x100,26))==expected,(typ,cls,x,y,[(i,a,b) for i,(a,b) in enumerate(zip(u.mem_read(ACT*16+0x100,26),expected)) if a!=b]);key=f'mode{mode}_state{state}';hist[key]=hist.get(key,0)+1;count+=1
v={'status':'SYNTHETIC_ORIGINAL_CPU_ONLY','source_sha256':H(raw),'unicorn':unicorn.__version__,'cases':count,'types':[18,19],'wall_classes':256,'direction_component_zero_nonzero_pairs':4,'actor_all26_bytes_checked':True,'SI_DI_BP_DS_CX_DX_and_FAR_stack_checked':True,'mode_and_state_histogram':hist,'scope':'Original083D:117A constructor bytes in isolated16-bit CPU with canonical valid object/map pointers. No loader/UI/game/IRQ execution, all aliases, global writes or successfulC37 runtime claim.'}
(R/'outputs/mode3_start_20261106/constructor_cpu_validation.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v))



