from pathlib import Path
import struct,json
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[]
for v in ['10','11','12','15','17','18']:
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 pos=p.find(bytes.fromhex('558bec5733ff393e'));assert pos>=0
 countoff=struct.unpack_from('<H',p,pos+8)[0];espos=p.find(b'\xb8',pos,pos+40);es=struct.unpack_from('<H',p,espos+1)[0]
 end=p.find(bytes.fromhex('5fc9cb'),pos)+3;assert end>pos
 for count,index,query in [(1,0,0),(4,0,2),(4,3,255),(4,2,73),(4,-1,129),(0,-1,1),(-1,-1,1),(4,-1,256)]:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0x10000,bytes(p));u.mem_write(0x50000+countoff,struct.pack('<H',count&65535))
  records=bytearray(28*max(count,1));
  for j in range(count):records[j*28+12]=(query+1)%256;records[j*28+10]=0x30+j
  if index>=0:records[index*28+12]=query;records[index*28+10]=0xe7
  u.mem_write(es*16,bytes(records));u.mem_write(0x60000+0xff04,struct.pack('<H',query))
  for reg,val in [(UC_X86_REG_CS,0x1000),(UC_X86_REG_IP,pos),(UC_X86_REG_DS,0x5000),(UC_X86_REG_SS,0x6000),(UC_X86_REG_SP,0xff00)]:u.reg_write(reg,val)
  reason=[]
  def hook(uc,a,n,data):
   op=bytes(uc.mem_read(a,1))
   if op in [b'\xcb',b'\x9a']:reason.append('return' if op==b'\xcb' else 'error_call');uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x10000+pos,0,count=20000)
  ax=u.reg_read(UC_X86_REG_AX)
  assert reason==(['return'] if index>=0 else ['error_call']),(v,count,index,reason)
  if index>=0:assert ax==0xe7,(v,ax)
  results.append(dict(build=v,linear_alias=f'1000:{pos:04x}',count=count,match_index=index,query=query,record_segment=hex(es),count_offset=hex(countoff),observed=reason[0],AX=ax if index>=0 else None))
(root/'evidence/record_lookup_emulation.json').write_text(json.dumps(results,indent=2));print(len(results),'record lookup cases passed')
