from pathlib import Path
import struct,json,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[]
for src in sorted((root/'pass53/originals').glob('*.bin')):
 v=src.name[4:6];v='18' if v=='19' else v;b=src.read_bytes();h=struct.unpack_from('<14H',b);re=(root/f'analysis/inputs/DOS{v}.exe').read_bytes();rh=struct.unpack_from('<14H',re);payload=bytearray(re[rh[4]*16:]);entry=(0x1000+rh[11])*16+rh[10]
 for k in range(rh[3]):
  off,seg=struct.unpack_from('<HH',re,rh[12]+k*4);a=seg*16+off;struct.pack_into('<H',payload,a,(struct.unpack_from('<H',payload,a)[0]+0x1000)&65535)
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,b[h[4]*16:]);events=[];count=[0];reached=[False]
 def hook(uc,a,n,_):
  count[0]+=1
  if a==entry:reached[0]=True;uc.emu_stop()
 def intr(uc,n,_):events.append(n);uc.emu_stop()
 ch=u.hook_add(UC_HOOK_CODE,hook);ih=u.hook_add(UC_HOOK_INTR,intr)
 for r,val in [(UC_X86_REG_CS,0x1000+h[11]),(UC_X86_REG_IP,h[10]),(UC_X86_REG_SS,0x1000+h[7]),(UC_X86_REG_SP,h[8]),(UC_X86_REG_DS,0xff0),(UC_X86_REG_ES,0xff0)]:u.reg_write(r,val)
 u.emu_start((0x1000+h[11])*16+h[10],0,count=2000000);assert reached[0] and not events,(src.name,events,count)
 got=bytes(u.mem_read(0x10000,len(payload)));assert got==bytes(payload),src.name;diff=[i for i,(a,c) in enumerate(zip(got,payload)) if a!=c]
 result=dict(program=src.name,source_sha256=hashlib.sha256(b).hexdigest(),original_mz_relocation_count=h[3],original_size=len(b),reconstruction_size=len(re),unpacked_entry=f'{u.reg_read(UC_X86_REG_CS):04x}:{u.reg_read(UC_X86_REG_IP):04x}',instructions=count[0],interrupts=events,compared_bytes=len(payload),different_bytes=len(diff),first_differences=[hex(x) for x in diff[:20]],SS=hex(u.reg_read(UC_X86_REG_SS)),SP=hex(u.reg_read(UC_X86_REG_SP)),DS=hex(u.reg_read(UC_X86_REG_DS)),ES=hex(u.reg_read(UC_X86_REG_ES)))
 u.hook_del(ch);u.hook_del(ih);target_ds=next(q['actual_DS'] for q in json.loads((root/'pass7/evidence/specs.json').read_text()) if q['build']==v);dos=[];ds_reached=[False]
 def bootstrap(uc,a,n,_):
  if uc.reg_read(UC_X86_REG_DS)==target_ds:ds_reached[0]=True;uc.emu_stop()
 def dos_boundary(uc,n,_):
  ah=uc.reg_read(UC_X86_REG_AH);dos.append([n,ah])
  if n==0x21 and ah==0x30:uc.reg_write(UC_X86_REG_AX,0x1606)
  elif n==0x21 and ah==0x4a:uc.reg_write(UC_X86_REG_EFLAGS,uc.reg_read(UC_X86_REG_EFLAGS)&~1)
  else:uc.emu_stop()
 u.mem_write(0xff00+2,struct.pack('<H',0x9000));u.hook_add(UC_HOOK_CODE,bootstrap);u.hook_add(UC_HOOK_INTR,dos_boundary);u.emu_start(entry,0,count=1000000);assert ds_reached[0],(src.name,dos,u.reg_read(UC_X86_REG_CS),u.reg_read(UC_X86_REG_IP));result['bootstrap_DS']=hex(u.reg_read(UC_X86_REG_DS));result['bootstrap_SS']=hex(u.reg_read(UC_X86_REG_SS));result['bootstrap_stop']=f'{u.reg_read(UC_X86_REG_CS):04x}:{u.reg_read(UC_X86_REG_IP):04x}';result['bootstrap_mocked_dos_calls']=dos
 results.append(result);print(src.name,'reached',result['unpacked_entry'],'diff',len(diff),result['first_differences'][:5]);(root/'pass53/evidence'/f'{src.name}.unpacked.bin').write_bytes(got)
(root/'pass53/evidence/unpack.json').write_text(json.dumps(results,indent=2))
