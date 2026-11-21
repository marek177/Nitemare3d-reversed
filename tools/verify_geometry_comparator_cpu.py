import sys,json,struct,hashlib
from pathlib import Path
sys.path.insert(0,'C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20/work/deps')
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
R=Path(__file__).resolve().parents[1];raw=Path('C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe').read_bytes();assert hashlib.sha256(raw).hexdigest()=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';im=raw[int.from_bytes(raw[8:10],'little')*16:];CS=0xfd9;DS=0x2771;u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(CS*16+0x16,im[CS*16+0x16:CS*16+0x5e]);u.hook_add(UC_HOOK_CODE,lambda mu,a,s,d:mu.emu_stop() if a==0x60000 else None);cases=0;signs={-1:0,0:0,1:0}
def signed(x):return (x&65535)-65536 if x&32768 else x&65535
def run(a,b):
 global cases
 for p,values in [(0x2000,a),(0x2020,b)]:
  r=bytearray(28);struct.pack_into('<4H',r,12,values[0]&65535,values[1]&65535,values[2]&65535,0);u.mem_write(DS*16+p,bytes(r))
 u.mem_write(DS*16+0x1000,struct.pack('<HH',0x2000,0x2020));frame=struct.pack('<4H',0,0x6000,0x1000,0x1002);u.mem_write(DS*16+0x8000,frame);df=0x400 if cases&1 else 0
 for r,val in [(UC_X86_REG_EAX,0x1234aaaa),(UC_X86_REG_BX,0xbbbb),(UC_X86_REG_CX,0xcccc),(UC_X86_REG_DX,0xdddd),(UC_X86_REG_SI,0x1234),(UC_X86_REG_DI,0x5678),(UC_X86_REG_BP,0x7788),(UC_X86_REG_CS,CS),(UC_X86_REG_DS,DS),(UC_X86_REG_SS,DS),(UC_X86_REG_ES,DS),(UC_X86_REG_SP,0x8000),(UC_X86_REG_EFLAGS,0x202|df)]:u.reg_write(r,val)
 u.emu_start(CS*16+0x16,0xfffff,count=100);axis=0 if a[0]&65535==a[2]&65535 else 1;x=signed(a[axis]);y=signed(b[axis]);want=(x>y)-(x<y);assert u.reg_read(UC_X86_REG_AX)==want&65535 and u.reg_read(UC_X86_REG_EAX)>>16==0x1234
 assert (u.reg_read(UC_X86_REG_CS),u.reg_read(UC_X86_REG_IP),u.reg_read(UC_X86_REG_SP))==(0x6000,0,0x8004) and bytes(u.mem_read(DS*16+0x8000,8))==frame
 for r,val in [(UC_X86_REG_SI,0x1234),(UC_X86_REG_DI,0x5678),(UC_X86_REG_BP,0x7788),(UC_X86_REG_CX,0xcccc),(UC_X86_REG_DS,DS),(UC_X86_REG_SS,DS),(UC_X86_REG_ES,DS)]:assert u.reg_read(r)==val
 assert u.reg_read(UC_X86_REG_EFLAGS)&0x400==df
 if want==0:assert u.reg_read(UC_X86_REG_EFLAGS)&0x8c5==0x44
 else:
  lhs=y&65535;rhs=x&65535;z=(lhs-rhs)&65535;f=(1 if lhs<rhs else 0)|(4 if (z&255).bit_count()%2==0 else 0)|(16 if (lhs^rhs^z)&16 else 0)|(64 if z==0 else 0)|(128 if z&32768 else 0)|(2048 if ((lhs^rhs)&(lhs^z))&32768 else 0);assert u.reg_read(UC_X86_REG_EFLAGS)&0x8d5==f
 cases+=1;signs[want]+=1;return want
for vertical in (False,True):
 for a in (-32768,-1,0,1,32767):
  for b in (-32768,-1,0,1,32767):run((a,a,a if vertical else a+1),(b,b,b if vertical else b+1))
seed=1
for i in range(1024):
 seed=(seed*1664525+1013904223)&0xffffffff;a=signed(seed&65535);b=signed(seed>>16);run((a,a,a if i&1 else a+1),(b,b,b if i&1 else b+1))
a=(10,0,10);b=(0,20,1);mixed=[run(a,b),run(b,a)];assert mixed==[1,1]
v={'status':'SYNTHETIC_ORIGINAL_CPU_ONLY','function':'0FD9:0016','cases':cases,'source_sha256':hashlib.sha256(raw).hexdigest(),'unicorn':unicorn.__version__,'result_sign_histogram':signs,'signed_extrema_and_duplicate_keys_checked':True,'preserved_registers_defined_FLAGS_DF_and_FAR_frame_checked':True,'mixed_orientation_witness':{'A':a,'B':b,'compare_A_B':mixed[0],'compare_B_A':mixed[1],'meaning':'Axis depends on first record, so arbitrary mixed-orientation records do not establish a total ordering.'},'scope':'Valid distinct near pointer/record fixture, no IRQ/alias/fault/native qsort stability or universal comparator target-domain claim.'};(R/'outputs/wall_sort_20261106/comparator_cpu_validation.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v))

