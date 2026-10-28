from pathlib import Path
import csv,json,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_MEM_WRITE,UC_HOOK_INSN
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];loc=next(x for x in json.loads((root/'pass23/evidence/blit_boundaries.json').read_text())['locations'] if x['build']==v);cs,entry=[int(x,16) for x in loc['entry'].split(':')];primary,alternate=[int(x,16) for x in loc['page_globals']];b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=loc['entry'],exe_sha256=hashlib.sha256(b).hexdigest()))
 for width,height,transparent in itertools.product([0,1],[0,1],[65535,31]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(0x60000,bytes([10])*65536);ds=q['actual_DS'];sp=0xe000;u.mem_write(ds*16+primary,struct.pack('<H',0x7000));u.mem_write(ds*16+sp,struct.pack('<12H',0x600,0,0,0x6000,0,0,0,1,width,height,0,transparent));state=dict(mask=0,writes=[],stopped=False)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def port(uc,port,size,value,_):
   if port==0x3c5:state['mask']=value&15
  def write(uc,access,a,size,value,_):
   if 0x70000<=a<0x80000:
    state['writes'].append((state['mask'],a-0x70000,value))
    if len(state['writes'])==64:state['stopped']=True;uc.emu_stop()
  u.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(cs*16+entry,0x600,count=10000)
  if width==height==1:assert state['writes']==[(1,0,10)] and u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4
  else:
   assert state['stopped'] and len(state['writes'])==64 and u.reg_read(UC_X86_REG_CS)==cs
   expected=[(1,(i*80)&65535,10) for i in range(64)] if height==0 else [(1<<(i%4),i//4,10) for i in range(64)];assert state['writes']==expected
  results.append(dict(build=v,kind='zero_counts',width=width,height=height,transparent=transparent,stopped_after_writes=state['stopped'],write_trace=state['writes'],returned=u.reg_read(UC_X86_REG_CS)==0,passed=True))
 # Complete one-zero-dimension cases: 16-bit LOOP/DEC wraps through65536 iterations.
 for width,height in [(0,1),(1,0)]:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(0x60000,bytes([10])*65536);ds=q['actual_DS'];sp=0xe000;u.mem_write(ds*16+primary,struct.pack('<H',0x7000));u.mem_write(ds*16+sp,struct.pack('<12H',0x600,0,0,0x6000,0,0,0,1,width,height,0,65535));state=dict(mask=0,count=0)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def port(uc,port,size,value,_):
   if port==0x3c5:state['mask']=value&15
  def write(uc,access,a,size,value,_):
   if 0x70000<=a<0x80000:
    i=state['count'];expected=(1,(i*80)&65535,10) if height==0 else (1<<(i%4),i//4,10);assert (state['mask'],a-0x70000,value)==expected;state['count']+=1
  u.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(cs*16+entry,0x600,count=2000000);assert state['count']==65536 and u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,kind='zero_count_complete',width=width,height=height,opaque=True,writes=state['count'],returned=True,passed=True))
 # Nonzero draws long enough to cross destination16-bit offset end; entire call completes.
 for x,y,page,transparent in itertools.product([0,3,65535],[0,255],[0,1],[65535,31]):
  width=2;height=1000;stride=1007;u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));source=bytes((i%61 for i in range(4096)));u.mem_write(0x60000,source);ds=q['actual_DS'];sp=0xe000;u.mem_write(ds*16+primary,struct.pack('<H',0x7000));u.mem_write(ds*16+alternate,struct.pack('<H',0x8000));u.mem_write(ds*16+sp,struct.pack('<12H',0x600,0,0,0x6000,x,y,0,stride,width,height,page,transparent));state=dict(mask=0,writes=[])
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def port(uc,port,size,value,_):
   if port==0x3c5:state['mask']=value&15
  def write(uc,access,a,size,value,_):
   if 0x70000<=a<0x90000:state['writes'].append((state['mask'],a,value))
  u.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(cs*16+entry,0x600,count=50000);base=(y&255)*80+(x>>2);segment=0x80000 if page else 0x70000;expected=[(1<<((x+c)&3),segment+((base+((x&3)+c)//4+r*80)&65535),source[c*stride+r]) for c in range(width) for r in range(height) if transparent==65535 or source[c*stride+r]!=31];assert state['writes']==expected,(v,x,y,page,transparent);assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,kind='destination_wrap',x=x,y=y,page=page,transparent=transparent,width=width,height=height,writes=len(expected),write_trace_sha256=hashlib.sha256(json.dumps(expected).encode()).hexdigest(),passed=True))
out=root/'pass24/evidence';out.mkdir(parents=True,exist_ok=True);(out/'blit_zero_wrap.json').write_text(json.dumps(dict(cases=len(results),scope='Original blitter. Zero-count prefix cases stopped at64 writes; single-zero opaque cases complete65536 writes; nonzero2x1000 draw completes. OUT/write observation, ordinary memory, no full VGA/DAC.',locations=locations,results=results),indent=2));print(len(results),'passed')
