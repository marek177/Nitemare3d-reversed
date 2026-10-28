from pathlib import Path
import struct,json,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent
results=[]
for v in ['10','11','12','15','17','18']:
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes(); h=struct.unpack_from('<14H',b);p=b[h[4]*16:]
 start=0; found=[]
 while True:
  pos=p.find(bytes.fromhex('c80200005633f68a94'),start)
  if pos<0:break
  start=pos+1
  end=p.find(bytes.fromhex('5ec9cb'),pos)
  if end<0 or end-pos>400:continue
  code=p[pos:end+3]
  if bytes.fromhex('81fe0001') not in code:continue
  found.append((pos,code))
 assert len(found)==2,(v,len(found))
 for layer,(pos,code) in enumerate(found):
  src=struct.unpack_from('<H',code,9)[0]
  k=code.rfind(bytes.fromhex('8884'));assert k>=0
  dst=struct.unpack_from('<H',code,k+2)[0]
  for seed in [0,0x7f,0x80,0xff]:
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10000+pos,code)
   u.mem_write(0x50000+src,bytes(range(256)));u.mem_write(0x60000,bytes([seed])*65536)
   for reg,val in [(UC_X86_REG_CS,0x1000),(UC_X86_REG_IP,pos),(UC_X86_REG_DS,0x5000),(UC_X86_REG_SS,0x6000),(UC_X86_REG_SP,0xff00)]:u.reg_write(reg,val)
   stopped=[]
   def hook(uc,a,n,data):
    if a==0x10000+pos+len(code)-1:stopped.append(a);uc.emu_stop()
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x10000+pos,0,count=100000)
   assert stopped,(v,layer,seed)
   actual=bytes(u.mem_read(0x50000+dst,256))
   def model(c):
    if layer==0:return (seed&128)|(4 if 1<=c<=0x30 else 0)|(16 if 0x2e<=c<=0x2f else 0)|(8 if 0x31<=c<=0x40 else 0)|(1 if 1<=c<=0x40 else 0)|(2 if 1<=c<=0x40 else 0)|(64 if 0x47<=c<=0x48 else 0)
    return (seed&128)|(1 if 6<=c<=0x3d else 0)|(2 if 8<=c<=0x2d else 0)|(4 if 0x2f<=c<=0x3d else 0)|(8 if 8<=c<=0x25 else 0)|(32 if c==0x2a else 0)|(64 if c==4 else 0)
   expected=bytes(map(model,range(256)));assert actual==expected,(v,layer,seed)
   results.append(dict(build=v,entry=f'1000:{pos:04x}',end=f'1000:{pos+len(code)-1:04x}',source=f'{src:04x}',destination=f'{dst:04x}',seed=seed,compared=256,matched=True,code_sha256=hashlib.sha256(code).hexdigest()))
(root/'evidence/class_flags_emulation.json').write_text(json.dumps(results,indent=2));print(len(results),'runs;',sum(r['compared'] for r in results),'matched outputs')
