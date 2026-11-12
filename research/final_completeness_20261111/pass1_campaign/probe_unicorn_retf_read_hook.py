"""python probe_unicorn_retf_read_hook.py IMAGE EMULATOR OUT
Reproduce a tool-specific anomaly; not a game behavior or coverage test.
"""
import hashlib,json,struct,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
import unicorn
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_MEM_READ
from unicorn.x86_const import *
b=image.read_bytes();assert hashlib.sha256(b).hexdigest()=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
results=[]
for mode in ('none','global_read','source_bounded_read'):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,b);ds=0x2771;cs=0x156
 u.mem_write(ds*16+0x12c,struct.pack('<HH',0xa400,0xa000));u.mem_write(0x70000,bytes(65536))
 for reg,value in ((UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x3456),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
 u.mem_write(ds*16+0xf000,struct.pack('<12H',0x6000,cs,0x200,0x7000,0,0,0,1,1,1,0,0xffff))
 if mode=='global_read':u.hook_add(UC_HOOK_MEM_READ,lambda *args:None)
 if mode=='source_bounded_read':u.hook_add(UC_HOOK_MEM_READ,lambda *args:None,None,0x70000,0x7ffff)
 u.emu_start(cs*16+0x7de,cs*16+0x6000,count=100)
 results.append(dict(mode=mode,cs=u.reg_read(UC_X86_REG_CS),ip=u.reg_read(UC_X86_REG_IP),sp=u.reg_read(UC_X86_REG_SP),returned=(u.reg_read(UC_X86_REG_CS),u.reg_read(UC_X86_REG_IP),u.reg_read(UC_X86_REG_SP))==(cs,0x6000,0xf004)))
assert [r['returned'] for r in results]==[True,False,True]
out.mkdir(parents=True,exist_ok=True);result=dict(unicorn_version=unicorn.__version__,image_sha256=hashlib.sha256(b).hexdigest(),results=results,scope='tool-observation only: original one-pixel opaque blit, count100; unbounded read hook changes observed far-return execution, source-bounded hook does not; no claim about other fixtures or game correctness')
(out/'unicorn_read_hook_probe.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
