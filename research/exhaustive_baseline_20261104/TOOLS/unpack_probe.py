from unicorn import *
from unicorn.x86_const import *
import struct,pathlib,json,hashlib
out=pathlib.Path('N3D_FUNCTION_RESEARCH');(out/'VERSIONS/DOS').mkdir(parents=True,exist_ok=True)
results=[]
for p in sorted(pathlib.Path('inputs/nite3/dos').iterdir()):
 if not p.name.lower().startswith('n3d'):continue
 b=p.read_bytes();h=struct.unpack_from('<14H',b);base=0x1000;psp=base-16;start=(base+h[11])*16+h[10]
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(base*16,b[h[4]*16:]);u.mem_write(psp*16,b'\xcd\x20');u.mem_write(psp*16+2,struct.pack('<H',0x9000))
 for reg,val in [(UC_X86_REG_CS,base+h[11]),(UC_X86_REG_IP,h[10]),(UC_X86_REG_SS,base+h[7]),(UC_X86_REG_SP,h[8]),(UC_X86_REG_DS,psp),(UC_X86_REG_ES,psp)]:u.reg_write(reg,val)
 state={'file':str(p),'sha256':hashlib.sha256(b).hexdigest(),'initial_cs':h[11],'initial_ip':h[10],'load_segment':base,'instructions':0,'status':'timeout'}
 def hook(u,a,s,d):
  state['instructions']+=1
  cs=u.reg_read(UC_X86_REG_CS);ip=u.reg_read(UC_X86_REG_IP)
  if a!=start and cs<base+h[11] and state['instructions']>50:
   state.update(status='handoff_captured',entry_cs=cs-base,entry_ip=ip,ds=u.reg_read(UC_X86_REG_DS)-base,ss=u.reg_read(UC_X86_REG_SS)-base,sp=u.reg_read(UC_X86_REG_SP));u.emu_stop()
 def intr(u,n,d):state.update(status='unexpected_interrupt',interrupt=n);u.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,intr)
 try:u.emu_start(start,0x1fffff,count=3000000)
 except UcError as e:state.update(status='error',error=str(e))
 if state['status']=='handoff_captured':
  # Fixed 512 KiB memory snapshot; load-base relocation values retained, never called original file.
  image=bytes(u.mem_read(base*16,0x80000));dest=out/'VERSIONS/DOS'/(p.name+'.loaded.bin');dest.write_bytes(image);state.update(image=str(dest),image_sha256=hashlib.sha256(image).hexdigest(),image_size=len(image))
 results.append(state)
(out/'VERSIONS/DOS/unpack_manifest.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
