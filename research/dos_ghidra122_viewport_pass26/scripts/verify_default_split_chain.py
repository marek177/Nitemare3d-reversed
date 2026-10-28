from pathlib import Path
import json,struct,itertools,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_INSN
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];setter=next(x for x in json.loads((root/'pass26/evidence/viewport_boundary.json').read_text())['locations'] if x['build']==v);split=next(x for x in json.loads((root/'pass25/evidence/blit_callers.json').read_text())['locations'] if x['build']==v and x['kind']=='split');page=next(x for x in json.loads((root/'pass23/evidence/blit_boundaries.json').read_text())['locations'] if x['build']==v);scs,sip=[int(x,16) for x in setter['setter_entry'].split(':')];cs,entry=[int(x,16) for x in split['entry'].split(':')];b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 for x,w,hh in itertools.product([8,290,139],[1,16],[0,1,152,153,255]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));ds=q['actual_DS'];sp=0xe000;u.mem_write(ds*16+int(setter['source_width'],16),struct.pack('<H',304));u.mem_write(ds*16+sp,struct.pack('<HH',0x600,0))
  for reg,val in [(UC_X86_REG_CS,scs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def dependency(uc,a,n,_):uc.reg_write(UC_X86_REG_IP,a-scs*16+5)
  handles=[]
  for r in setter['instructions']:
   if r['bytes'].startswith('9a'):
    a=scs*16+int(r['address'].split(':')[1],16);handles.append(u.hook_add(UC_HOOK_CODE,dependency,None,a,a))
  u.emu_start(scs*16+sip,0x600,count=1000);assert struct.unpack('<H',u.mem_read(ds*16+int(setter['boundary'],16),2))[0]==155
  for handle in handles:u.hook_del(handle)
  source=bytes(i%61 for i in range(w*hh))
  if source:u.mem_write(0x60200,source)
  u.mem_write(ds*16+0x9000,bytes([w,hh])+bytes(4)+struct.pack('<I',0x60000200));u.mem_write(ds*16+int(page['page_globals'][0],16),struct.pack('<H',0x7000));u.mem_write(ds*16+sp,struct.pack('<6H',0x600,0,x,4,0x9000,0));state=dict(mask=0,writes=[])
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def port(uc,port,size,value,_):
   assert port in [0x3c4,0x3c5] and size==1
   if port==0x3c5:state['mask']=value&15
  def write(uc,access,a,size,value,_):
   if 0x70000<=a<0x80000:state['writes'].append((state['mask'],a-0x70000,value))
  u.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(cs*16+entry,0x600,count=max(10000,w*hh*20));n=min(152,hh);expected=[]
  for lo,hi,transparent in [(0,n,0),(n,hh,None)]:
   for col in range(w):
    for row in range(lo,hi):
     value=source[col*hh+row]
     if transparent is None or value!=transparent:expected.append((1<<((x+col)&3),((4+row)*80+(x+col)//4)&65535,value))
  assert state['writes']==expected,(v,x,w,hh,len(state['writes']),len(expected));assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,viewport_width=304,boundary=155,x=x,y=4,width=w,height=hh,writes=len(expected),write_trace_sha256=hashlib.sha256(json.dumps(expected).encode()).hexdigest(),passed=True))
out=root/'pass26/evidence';(out/'default_split_chain.json').write_text(json.dumps(dict(cases=len(results),scope='Original viewport setter -> split wrapper -> original blitter. Only two setter downstream dependencies mocked. Synthetic graphics, OUT/memory-write observation, no full VGA/DAC.',results=results),indent=2));print(len(results),'passed')
