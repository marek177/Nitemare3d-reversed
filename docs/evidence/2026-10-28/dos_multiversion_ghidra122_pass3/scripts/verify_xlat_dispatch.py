from pathlib import Path
import struct,json
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[]
for q in json.loads((root/'pass3/evidence/xlat_proofs.json').read_text()):
 v=q['build'];b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 seg,off=map(lambda x:int(x,16),q['dispatch_start'].split(':'));source=int(q['source'].split(':')[1],16);data=bytes.fromhex(q['class_bytes']);targets=[int(t.split(':')[1],16) for t in q['targets']]
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10000,bytes(p));seen=[]
 def hook(uc,a,n,d):
  if not seg*16+off<=a<seg*16+source+5:seen.append(a-seg*16);uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook);cases=0
 for state in q['reachable_states']:
  for ch in range(256):
   seen.clear();u.mem_write(0x60000+0x2000-5,bytes([state]))
   for reg,val in [(UC_X86_REG_CS,seg),(UC_X86_REG_IP,off),(UC_X86_REG_DS,int(q['ds'],16)),(UC_X86_REG_SS,0x6000),(UC_X86_REG_BP,0x2000),(UC_X86_REG_AX,0xab00|ch)]:u.reg_write(reg,val)
   u.emu_start(seg*16+off,0,count=30)
   c=(data[ch-0x20]&15) if 0x20<=ch<=0x78 else 0;nextstate=data[c*8+state]>>4
   assert seen==[targets[nextstate]],(v,state,ch,seen,targets[nextstate])
   assert bytes(u.mem_read(0x60000+0x2000-5,1))==bytes([nextstate]);cases+=1
 results.append(dict(build=v,cases=cases,states=q['reachable_states'],passed=True,scope='dispatch fragment with injected incoming character/state; class table from original loaded image; not full formatter runtime'))
(root/'pass3/evidence/xlat_emulation.json').write_text(json.dumps(results,indent=2));print(sum(r['cases'] for r in results),'XLAT dispatch cases passed')
