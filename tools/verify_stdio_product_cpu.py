from pathlib import Path
import sys,json,hashlib,struct
R=Path.cwd();sys.path.insert(0,str(R.parent/'goal-x20/work/deps'))
from unicorn import *
from unicorn.x86_const import *
raw=Path('C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe').read_bytes();assert hashlib.sha256(raw).hexdigest()=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';im=raw[int.from_bytes(raw[8:10],'little')*16:];u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);CS=0x11ee;DS=0x3000;u.mem_write(CS*16+0x6fc,im[CS*16+0x6fc:CS*16+0x7df]);pcs=[]
def hook(m,a,n,z):
 if a==0x60000:m.emu_stop()
 else:pcs.append(a-CS*16)
u.hook_add(UC_HOOK_CODE,hook);rows=[]
for size,count in [(0,0),(0,65535),(65535,0),(256,256),(512,128),(32768,2),(2,32768),(4096,16)]:
 for df in [0,0x400]:
  u.mem_write(DS*16,bytes([0xa7])*65536);u.mem_write(DS*16+0x8000,struct.pack('<6H',0,0x6000,0x2000,size,count,0x217a))
  for r,v in [(UC_X86_REG_CS,CS),(UC_X86_REG_DS,DS),(UC_X86_REG_SS,DS),(UC_X86_REG_ES,DS),(UC_X86_REG_SP,0x8000),(UC_X86_REG_BP,0x7777),(UC_X86_REG_SI,0x1111),(UC_X86_REG_DI,0x2222),(UC_X86_REG_EFLAGS,0x202|df)]:u.reg_write(r,v)
  pcs.clear();u.emu_start(CS*16+0x6fc,0xfffff,count=100);assert pcs==[0x6fc,0x6fd,0x6ff,0x702,0x703,0x704,0x707,0x70a,0x70c,0x76b,0x7d9,0x7da,0x7db,0x7dd,0x7de];assert u.reg_read(UC_X86_REG_AX)==0 and u.reg_read(UC_X86_REG_SP)==0x8004 and u.reg_read(UC_X86_REG_CS)==0x6000;assert u.mem_read(DS*16+0x2000,1)==b'\xa7';assert u.mem_read(DS*16+0x217a,8)==b'\xa7'*8;rows.append({'size':size,'count':count,'DF':bool(df),'DX_high_product':u.reg_read(UC_X86_REG_DX),'returned_AX':0,'no_stream_access_path':True})
O=R/'outputs/stdio_product_20261107';O.mkdir(exist_ok=True);(O/'validation.json').write_text(json.dumps({'status':'SYNTHETIC_ORIGINAL_CPU_ONLY','cases':rows,'scope':'Sixteen zero-low-product fixtures; no calls or stream accesses on verified path. General nonzero product, malformed streams, aliases, IRQ/nativeWin16/remake remainopen.'},indent=2));print('PASS:16 zero-low-product original CPU cases')
