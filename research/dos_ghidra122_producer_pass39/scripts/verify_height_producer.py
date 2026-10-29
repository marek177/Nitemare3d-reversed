from pathlib import Path
import csv,json,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
def s16(n):return (n+32768)%65536-32768
def s32(n):return (n+2147483648)%4294967296-2147483648
def div(a,b):
 n=abs(a)//abs(b)*(-1 if (a<0)!=(b<0) else 1)
 if not -2147483648<=n<=2147483647:raise OverflowError()
 return n
meta=json.loads((root/'pass26/evidence/viewport_boundary.json').read_text())['locations']
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];m=next(x for x in meta if x['build']==v);ds=q['actual_DS'];rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));idx=next(i for i,r in enumerate(rows) if r['bytes']=='c8100000' and rows[i+3]['bytes']=='8b7e0a');cs,entry=[int(x,16) for x in rows[idx]['address'].split(':')];body=[]
 for r in rows[idx:]:
  body.append(r)
  if r['bytes']=='cb':break
 baseline=int(m['output_base'],16)+16;b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',baseline=hex(baseline),instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 for (x0,x1),(y0,y1),offset in itertools.product([(0,0),(0,3),(0,4),(10,30),(30,10),(-32768,32767)],[(0,0),(100,101),(100,116),(116,100),(-32768,0)],[-1,0,1,3]):
  left=s16(x0+offset);right=s16(left+9);dx=s16(x1-x0);dy=s16(y1-y0);expected=None;expectfault=False
  try:
   slope=div(s32(dy<<16),dx) if dx else 0
   if dy==0:yl=yr=y0;acc=s32(s16(y0-1280)<<16)
   elif dx==0:yl=y0;yr=y1;acc=s32(s16(y0-1280)<<16)
   else:
    yl=s16(y0+div(s32(s16(left-x0)*dy),dx));yr=s16(y0+div(s32(s16(right-x0)*dy),dx));acc=s32((s16(y0-1280)<<16)+s32(s16(left-x0)*slope))
   expected=[yl&65535,yr&65535,slope&0xffffffff,acc&0xffffffff]
  except OverflowError:expectfault=True
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xe000;record=0x6400;u.mem_write(ds*16+record,b'\xa5'*18);u.mem_write(ds*16+record+2,struct.pack('<H',left&65535));u.mem_write(ds*16+record+6,struct.pack('<H',right&65535));u.mem_write(ds*16+baseline,struct.pack('<H',1280));u.mem_write(ds*16+sp,struct.pack('<7H',0x600,0,record,x0&65535,y0&65535,x1&65535,y1&65535));fault=[]
  def intr(uc,n,_):fault.append(n);uc.emu_stop()
  u.hook_add(UC_HOOK_INTR,intr)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  u.emu_start(cs*16+entry,0x600,count=1000);assert bool(fault)==expectfault
  if fault:assert fault==[0]
  else:
   actual=[struct.unpack('<H',u.mem_read(ds*16+record+n,2))[0] for n in [4,8]]+[struct.unpack('<I',u.mem_read(ds*16+record+n,4))[0] for n in [10,14]];assert actual==expected,(v,x0,x1,y0,y1,offset,actual,expected);assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,x0=x0,x1=x1,y0=y0,y1=y1,record_left=left,record_right=right,expected=expected,divide_fault=bool(fault),passed=True))
(root/'pass39/evidence/producer.json').write_text(json.dumps(dict(cases=len(results),scope='Complete original interpolation producer, no callee mocks. Synthetic endpoints and clipped span. Exception hook stops before DOS handler.',locations=locations,results=results),indent=2));print(len(results),'passed;',sum(r['divide_fault'] for r in results),'faults')
