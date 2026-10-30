from pathlib import Path
import json,struct,hashlib,itertools
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass91/evidence';out=[];locations=[];s16=lambda n:(n+32768)%65536-32768
for meta in [dict(build=v) for v in ['10','11','12','15','17','18']]:
 v=meta['build'];ds=next(x['actual_DS'] for x in json.load(open(r/'baseline58/pass7/evidence/specs.json')) if x['build']==v);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 for field,divisor,label in [('field04',50,'Mouse'),('field05',200,'Joystick')]:
  source=next(x for x in json.load(open(o/'input_locations.json')) if x['build']==v and x['label']==label);entry=source['entry'];cs,ip=[int(x,16) for x in entry.split(':')];offset=source['sensitivity_global'];locations.append(source)
  for sens,a,bval in itertools.product([0,1,50,100,128,255],[-32768,-1,0,1,100,16384,32767],[-32768,-1000,-1,0,1,100,257,1000,32767]):
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+offset,bytes([sens]));u.mem_write(ds*16+0xe000,struct.pack('<4H',0,0x600,a&65535,bval&65535));state={'done':False}
   for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
   def hook(u,addr,size,_):
    if addr==0x6000:state['done']=True;u.emu_stop()
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+ip,0,count=100);product=s16(sens*bval);q=(abs(product)//divisor)*(1 if product>=0 else -1);expected=min(q,s16(a*2));actual=s16(u.reg_read(UC_X86_REG_AX));assert state['done'] and actual==expected,(v,label,sens,a,bval,actual,expected);assert u.reg_read(UC_X86_REG_SP)==0xe004
   out.append(dict(build=v,label=label,sensitivity=sens,arg1=a,arg2=bval,result=actual,passed=True))
 print(v,'756 passed')
(o/'sensitivity_tests.json').write_text(json.dumps(dict(locations=locations,passed=len(out),cases=out,boundary='Original helper executes without mocked calls or interrupts; explicit DS=SS,SPe000 sensitivity-byte fixtures.'),indent=2)+'\n')
