from pathlib import Path
import csv,json,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
def s16(n):return (n+32768)%65536-32768
def s32(n):return (n+2147483648)%4294967296-2147483648
def div(a,b):return (abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1)
meta=json.loads((root/'pass26/evidence/viewport_boundary.json').read_text())['locations'];caller=json.loads((root/'pass33/evidence/caller.json').read_text())['locations'];proj=json.loads((root/'pass29/evidence/projection.json').read_text())['locations']
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];m=next(x for x in meta if x['build']==v);ca=next(x for x in caller if x['build']==v);pr=next(x for x in proj if x['build']==v);ds=q['actual_DS'];rb=bytes.fromhex(next(r['bytes'] for r in ca['instructions'] if r['bytes'].startswith('9a')));cs=int.from_bytes(rb[3:],'little');entry=int.from_bytes(rb[1:3],'little');rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));idx=next(i for i,r in enumerate(rows) if r['address']==f'{cs:04x}:{entry:04x}');body=[]
 for r in rows[idx:]:
  body.append(r)
  if r['bytes']=='cb':break
 flag=int.from_bytes(bytes.fromhex(body[2]['bytes'])[2:4],'little');trigb=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('660fbf06')))[4:6],'little');triga=trigb-2;daddr=int(pr['output_dwords'][3],16);caddr=int(pr['output_dwords'][2],16);center=int(m['output_base'],16)+12
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',flag=hex(flag),trig_a=hex(triga),trig_b=hex(trigb),center=hex(center),c=hex(caddr),d=hex(daddr),instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xe000;fault=[]
 def intr(uc,n,_):fault.append(n);uc.emu_stop()
 u.hook_add(UC_HOOK_INTR,intr)
 for f,kind,scale,x,(ta,tb),bias in itertools.product([0,1,65535],[0,2,3,4],[0,1,152,65535],[0,160,319],[(100,200),(-100,-200),(0,0)],[0,1234567]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.hook_add(UC_HOOK_INTR,intr)
  for addr,val,fmt in [(flag,f,'H'),(triga,ta&65535,'H'),(trigb,tb&65535,'H'),(center,160,'H'),(caddr,81715200,'I'),(daddr,459074,'I')]:u.mem_write(ds*16+addr,struct.pack('<'+fmt,val))
  u.mem_write(ds*16+sp,struct.pack('<5HI',0x600,0,kind,x,scale,bias));fault.clear()
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  u.emu_start(cs*16+entry,0x600,count=1000);expected=None;expectfault=False
  try:
   usex=bool(f)!=(kind in (2,3));term=div(s32(s16(x-160)*459074),scale) if usex else div(81715200,scale)
   numerator=s32(term+bias) if usex and f else s32(bias-term) if usex else s32(term-bias);expected=div(numerator,tb if f else ta)
   if not -2147483648<=expected<=2147483647:expectfault=True
  except ZeroDivisionError:expectfault=True
  assert bool(fault)==expectfault,(v,f,kind,scale,x,ta,bias,fault,expected)
  if fault:assert fault==[0]
  else:
   actual=s32(u.reg_read(UC_X86_REG_AX)|(u.reg_read(UC_X86_REG_DX)<<16));assert actual==expected,(v,f,kind,scale,x,actual,expected);assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,flag=f,kind=kind,scale=scale,x=x,trig_a=ta,trig_b=tb,bias=bias,expected=expected,fault=bool(fault),passed=True))
(root/'pass35/evidence/projection_helper.json').write_text(json.dumps(dict(cases=len(results),scope='Complete original five-word projection helper; no callee mocks, synthetic arithmetic globals and arguments. CPU exception stops before DOS handler.',locations=locations,results=results),indent=2));print(len(results),'passed;',sum(r['fault'] for r in results),'divide faults')
