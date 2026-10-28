from pathlib import Path
import struct,json
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[]
for v in ['10','11','12','15','17','18']:
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=b[h[4]*16:]
 signature=bytes.fromhex('c802000057568b7e0a8b7606ff760c57ff7608569a');pos=p.find(signature);assert pos>=0 and p.find(signature,pos+1)<0
 gate=pos+0x1c;assert p[gate:gate+2]==b'\x2a\xe4';jump=pos+0x2b;assert p[jump:jump+2]==b'\x0f\x8f'
 nonlethal=jump+4+struct.unpack_from('<h',p,jump+2)[0];lethal=pos+0x33
 # Equivalent linear alias is valid here: both branch endpoints are in one 64K offset window.
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10000,p);u.mem_write(0x60000+0xf008,struct.pack('<H',0x5000))
 observed=[]
 def hook(uc,a,n,data):
  if a in [0x10000+nonlethal,0x10000+lethal]:observed.append(a);uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 cases=0
 for hp in range(256):
  for damage in [0,1,127,128,254,255]:
   observed.clear();u.mem_write(0x50210,bytes([hp]))
   for reg,val in [(UC_X86_REG_CS,0x1000),(UC_X86_REG_IP,gate),(UC_X86_REG_SS,0x6000),(UC_X86_REG_BP,0xf000),(UC_X86_REG_SI,0x200),(UC_X86_REG_AX,0xab00|damage)]:u.reg_write(reg,val)
   u.emu_start(0x10000+gate,0,count=20)
   want=hp<=damage
   assert observed==[0x10000+(lethal if want else nonlethal)]
   assert bytes(u.mem_read(0x50210,1))==bytes([0 if want else hp]);cases+=1
 results.append(dict(build=v,function_linear_alias=f'1000:{pos:04x}',gate_linear_alias=f'1000:{gate:04x}',cases=cases,model='zero-extend AL; compare HP byte <= AL; clear HP to zero on <=; else branch without modifying HP in tested prefix',scope='callee return AX injected; no damage generation or full death/pain path executed'))
(root/'pass2/evidence/damage_gate_emulation.json').write_text(json.dumps(results,indent=2));print(sum(r['cases'] for r in results),'damage gate cases passed')
