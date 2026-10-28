from pathlib import Path
import csv,json,struct
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;out=[]
for v in ['10','11','12','15','17','18']:
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 count=0
 for q in json.loads((root/'pass4/evidence'/('DOS'+v)/'switch_proofs.json').read_text()):
  win=q['window'];seg,off=map(lambda x:int(x,16),win[0]['address'].split(':'));branch=bytes.fromhex(win[2]['bytes']);boff=int(win[2]['address'].split(':')[1],16);default=(boff+len(branch)+int.from_bytes(branch[1:] if len(branch)==2 else branch[2:],'little',signed=True))&65535
  expected=[int(x.split(':')[1],16) for x in q['targets']];allowed={seg*16+int(x['address'].split(':')[1],16) for x in win}
  for idx in [*range(len(expected)),len(expected),len(expected)+1,65535]:
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10000,bytes(p));u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_DI,idx);u.reg_write(UC_X86_REG_AX,0xbeef);seen=[]
   def hook(uc,a,n,d):
    if a not in allowed:seen.append(a-seg*16);uc.emu_stop()
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start(seg*16+off,0,count=10);assert seen==[expected[idx] if idx<len(expected) else default];count+=1
 for q in csv.DictReader((root/'pass4/evidence'/('DOS'+v)/'flow_specs.tsv').open(),delimiter='\t'):
  seg,off=map(lambda x:int(x,16),q['source'].split(':'));target=int(q['target'].split(':')[1],16);bb=bytes.fromhex(q['bytes'])
  for zf in [0,1]:
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10000,bytes(p));u.reg_write(UC_X86_REG_CS,seg);u.reg_write(UC_X86_REG_EFLAGS,2|(zf<<6));u.emu_start(seg*16+off,0,count=1)
   taken=bool(zf) if bb[1]==0x84 else not bool(zf);assert u.reg_read(UC_X86_REG_CS)==seg and u.reg_read(UC_X86_REG_IP)==(target if taken else off+4);count+=1
 out.append(dict(build=v,cases=count,passed=True))
(root/'pass4/evidence/dispatch_emulation.json').write_text(json.dumps(out,indent=2));print(sum(x['cases'] for x in out),'dispatch/conditional cases passed')
