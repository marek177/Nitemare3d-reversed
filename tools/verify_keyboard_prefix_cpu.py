from pathlib import Path
import sys,json,hashlib,struct
R=Path.cwd();sys.path.insert(0,str(R.parent/'goal-x20/work/deps'))
from unicorn import *
from unicorn.x86_const import *
raw=Path('C:/Users/Marek-Medved/Documents/Codex/2026-10-25/goal-x20-3/work/decoded/nite3d20/output.000.exe').read_bytes();assert hashlib.sha256(raw).hexdigest()=='5ad15f66a4478de21e4c74799a74d35d606f3bdb7406a5b40168cfbd5ba2c9a3';im=raw[int.from_bytes(raw[8:10],'little')*16:];u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);CS=0x6b0;DS=0x2771;SS=0x4000;u.mem_write(CS*16,im[CS*16:CS*16+0x10a]);scan=0
u.hook_add(UC_HOOK_INSN,lambda m,p,n,z:scan,None,1,0,UC_X86_INS_IN)
u.hook_add(UC_HOOK_CODE,lambda m,a,n,z:m.emu_stop(),None,CS*16+0x10a,CS*16+0x10a)
mask={1:(0,1),0x1d:(0,128),0x2a:(0,64),0x36:(0,32),0x38:(1,1),0x39:(1,2),0x48:(0,2),0x4b:(0,8),0x4d:(0,16),0x50:(0,4)};count=0;h=hashlib.sha256()
for scan in range(256):
 for prior in [0,0xe0]:
  for seed in range(256):
   before=bytes([seed,seed^0xa5]);want=bytearray(before);key=scan&127
   if key in mask and not (key in [0x2a,0x36] and prior==0xe0):
    i,m=mask[key];want[i]=(want[i]&(~m&255))|(m if scan<128 else 0)
   u.mem_write(DS*16+0x3f50,before);u.mem_write(DS*16+0x34ba,bytes([prior]))
   for r,v in [(UC_X86_REG_CS,CS),(UC_X86_REG_SS,SS),(UC_X86_REG_DS,0x5000),(UC_X86_REG_ES,0x6000),(UC_X86_REG_SP,0x8000),(UC_X86_REG_EFLAGS,0x602)]:u.reg_write(r,v)
   u.emu_start(CS*16,0xfffff,count=200);out=bytes(u.mem_read(DS*16+0x3f50,2));assert out==want and u.reg_read(UC_X86_REG_IP)==0x10a;h.update(bytes([scan,prior,seed])+out);count+=1
O=R/'outputs/keyboard_cpu_20261107';O.mkdir(exist_ok=True);(O/'validation.json').write_text(json.dumps({'status':'SYNTHETIC_ORIGINAL_CPU_PREFIX_ONLY','cases':count,'scan_codes':256,'initial_field_pairs':256,'prior_prefix_values':[0,224],'case_digest_sha256':h.hexdigest(),'scope':'Port60 return stubbed; original prefix stops before010A and chainedhandler. Fieldpairs correlated (second=first XOR A5), not all65536 pairs. No nativeIRQ/vector/timing or fullIRET/register parity claim.'},indent=2));print('PASS',count)
