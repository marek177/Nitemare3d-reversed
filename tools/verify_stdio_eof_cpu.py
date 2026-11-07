from pathlib import Path
import sys,json,struct,hashlib
R=Path.cwd();sys.path.insert(0,str(R.parent/'goal-x20/work/deps'))
from unicorn import *
from unicorn.x86_const import *
raw=Path('C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe').read_bytes();assert hashlib.sha256(raw).hexdigest()=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';im=raw[int.from_bytes(raw[8:10],'little')*16:];u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);CS=0x11ee;DS=0x3000
for a,b in [(0x6fc,0x7df),(0x834,0x8c9)]:u.mem_write(CS*16+a,im[CS*16+a:CS*16+b])
rows=[];calls=[];ret=0

def hook(m,a,n,z):
 if a==0x60000:m.emu_stop()
 if a==CS*16+0x1e14:
  sp=m.reg_read(UC_X86_REG_SP);f=bytes(m.mem_read(DS*16+sp,10));ip,cs,fd,ptr,count=struct.unpack('<5H',f);assert (fd,ptr,count)==(5,0x4000,512);calls.append((fd,ptr,count));m.reg_write(UC_X86_REG_AX,ret);m.reg_write(UC_X86_REG_SP,sp+4);m.reg_write(UC_X86_REG_CS,cs);m.reg_write(UC_X86_REG_IP,ip)
u.hook_add(UC_HOOK_CODE,hook)
for ret in [0,65535]:
 for seed in [0,0xa7]:
  for df in [0,0x400]:
   u.mem_write(DS*16,bytes(65536));u.mem_write(DS*16+0x217a,struct.pack('<HHHBB',0x4000,0,0x4000,0x0d,5));u.mem_write(DS*16+0x221a,struct.pack('<BBH',1,0,512));u.mem_write(DS*16+0x2000,bytes([seed]));u.mem_write(DS*16+0x8000,struct.pack('<6H',0,0x6000,0x2000,1,1,0x217a))
   for r,v in [(UC_X86_REG_CS,CS),(UC_X86_REG_DS,DS),(UC_X86_REG_SS,DS),(UC_X86_REG_ES,DS),(UC_X86_REG_SP,0x8000),(UC_X86_REG_BP,0x7777),(UC_X86_REG_EFLAGS,0x202|df)]:u.reg_write(r,v)
   calls.clear();u.emu_start(CS*16+0x6fc,0xfffff,count=500);assert u.reg_read(UC_X86_REG_CS)==0x6000 and u.reg_read(UC_X86_REG_IP)==0 and u.reg_read(UC_X86_REG_SP)==0x8004 and u.reg_read(UC_X86_REG_AX)==0;assert bytes(u.mem_read(DS*16+0x2000,1))==bytes([seed]);flag=u.mem_read(DS*16+0x2180,1)[0];assert flag&(0x10 if ret==0 else 0x20) and len(calls)==1;rows.append({'low_level_return':ret,'seed':seed,'DF':bool(df),'returned_AX':0,'destination_unchanged':True,'stream_flags':flag})
O=R/'outputs/stdio_eof_20261107';(O/'CPU_validation.json').write_text(json.dumps({'status':'SYNTHETIC_ORIGINAL_LIBRARY_CPU_WITH_ONE_STUBBED_LOW_LEVEL_READ','cases':rows,'scope':'Original06FC/0834 instructions; only1E14 return is stubbed with validFAR frame. Not native DOS EOF, all buffering modes, arbitrary aliases or IRQ closure.'},indent=2));print('PASS:8 controlled EOF/error cases')
