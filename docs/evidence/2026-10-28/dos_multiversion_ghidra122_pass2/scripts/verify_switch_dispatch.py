from pathlib import Path
import json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[]
for v in ['10','11','12','15','17','18']:
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);payload=bytearray(b[h[4]*16:])
 for i in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+i*4);p=seg*16+off;struct.pack_into('<H',payload,p,(struct.unpack_from('<H',payload,p)[0]+0x1000)&65535)
 for s in json.loads((root/'pass2/evidence'/('DOS'+v)/'switch_proofs.json').read_text()):
  win=s['window'];seg,off=map(lambda x:int(x,16),win[0]['address'].split(':'));branch=bytes.fromhex(win[1]['bytes']);boff=int(win[1]['address'].split(':')[1],16)
  default=(boff+len(branch)+int.from_bytes(branch[1:] if len(branch)==2 else branch[2:],'little',signed=True))&65535
  expected=[int(x.split(':')[1],16) for x in s['targets']];allowed={seg*16+int(x['address'].split(':')[1],16) for x in win}
  for index in [*range(len(expected)),len(expected),len(expected)+1,65535]:
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10000,bytes(payload))
   for reg,val in [(UC_X86_REG_CS,seg),(UC_X86_REG_IP,off),(UC_X86_REG_AX,index),(UC_X86_REG_BX,0xdead),(UC_X86_REG_DX,index)]:u.reg_write(reg,val)
   stopped=[]
   def hook(uc,a,n,data):
    if a not in allowed:stopped.append(a-seg*16);uc.emu_stop()
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start(seg*16+off,0,count=10)
   wanted=expected[index] if index<len(expected) else default
   assert stopped==[wanted],(v,s['source'],index,stopped,wanted)
  results.append(dict(build=v,source=s['source'],entries=len(expected),cases=len(expected)+3,passed=True,default=f'{seg:04x}:{default:04x}'))
(root/'pass2/evidence/switch_emulation.json').write_text(json.dumps(results,indent=2));print(len(results),'switches;',sum(r['cases'] for r in results),'dispatch cases passed')
