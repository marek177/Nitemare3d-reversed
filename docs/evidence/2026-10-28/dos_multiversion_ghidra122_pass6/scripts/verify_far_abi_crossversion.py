from pathlib import Path
import struct,json,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;dsproof=json.loads((root/'pass3/evidence/xlat_proofs.json').read_text());results=[]
for q in json.loads((root/'pass6/evidence/specs.json').read_text()):
 v=q['build'];b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 cs,ip=map(lambda x:int(x,16),q['callback_entry'].split(':'));real_ds=int(next(x for x in dsproof if x['build']==v)['ds'],16)
 for ds,flag in itertools.product([0,real_ds,0x5000,0xffff],[0,1,255]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p))
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,real_ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  u.mem_write(real_ds*16+0xe000,struct.pack('<HHH',0x600,0,1));u.mem_write(ds*16+q['mode1_flag'],bytes([flag]));u.emu_start(cs*16+ip,0x600,count=10000)
  ax=u.reg_read(UC_X86_REG_AX);dx=u.reg_read(UC_X86_REG_DX);expected=(ds<<16)|q['mode1_flag'] if flag else 0
  assert (dx<<16)|ax==expected and u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_IP)==0x600 and u.reg_read(UC_X86_REG_SP)==0xe004
  results.append(dict(build=v,entry=q['callback_entry'],DS=hex(ds),flag=flag,AX=hex(ax),DX=hex(dx),passed=True))
(root/'pass6/evidence/far_abi_emulation.json').write_text(json.dumps(dict(cases=len(results),hooks=False,stubs=False,scope='original dispatcher mode1 with prepared far return frame; modes0,2..5 semantics not claimed',results=results),indent=2));print(len(results),'far ABI cases passed')
