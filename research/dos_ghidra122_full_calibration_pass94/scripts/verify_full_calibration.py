from pathlib import Path
import json,struct,itertools
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass94/evidence';results=[]
for l in json.load(open(o/'locations.json')):
 v=l['build'];ds=next(x['actual_DS'] for x in json.load(open(r/'baseline58/pass7/evidence/specs.json')) if x['build']==v);meta=next(x for x in json.load(open(o/'calibration_locations.json')) if x['build']==v);cs,ip=[int(x,16) for x in l['entry'].split(':')];helper=[tuple(int(x,16) for x in e.split(':')) for e in l['helpers']];work=helper[2];counter=helper[3];rows=[x.split('\t') for x in (o/f'DOS{v}.exe.ghidra.tsv').read_text().splitlines() if x.startswith('instruction\t')];wrows=[x for x in rows if x[1]=='work'];cr=[x for x in rows if x[1]=='counter'];flag=int.from_bytes(bytes.fromhex(cr[0][3])[2:4],'little');cache=int.from_bytes(bytes.fromhex(next(x[3] for x in cr if x[3].startswith('a1')))[1:3],'little');wc=int.from_bytes(bytes.fromhex(wrows[0][3])[3:5],'little');calls={int(x[2].split(':')[0],16)*16+int(x[2].split(':')[1],16):x for x in l['calls']+wrows if 'CALL' in x[4]};b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 for first,second,start,rate in itertools.product([0,1,64,65,65536],[0,100],[100,0xfffffff0],[18,70]):
  use_second=first<65;m=second if use_second else first;stream=[start,(start+first*10+9)&0xffffffff]+([0x12345678,(0x12345678+second*10+9)&0xffffffff] if use_second else []);u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+flag,b'\1');u.mem_write(ds*16+meta['rate_global'],struct.pack('<h',rate));u.mem_write(ds*16+wc,b'\0'*4);u.mem_write(ds*16+0xe000,struct.pack('<HH',0,0x600));state={'done':False,'fatal':False,'reads':0,'work':0,'flip':0,'work_subcalls':0}
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  def hook(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop();return
   if a==counter[0]*16+counter[1]:u.mem_write(ds*16+cache,struct.pack('<I',stream[state['reads']]));state['reads']+=1
   if a==work[0]*16+work[1]:state['work']+=1
   x=calls.get(a)
   if x is None:return
   z=bytes.fromhex(x[3]);xcs,xip=[int(x,16) for x in x[2].split(':')];target=(xcs,(xip+3+int.from_bytes(z[1:3],'little',signed=True))&65535) if z[0]==0xe8 else (int.from_bytes(z[3:5],'little'),int.from_bytes(z[1:3],'little'))
   if target in [work,counter]:return
   if x is l['calls'][-1]:state['fatal']=True;u.emu_stop();return
   if x[1]=='work':state['work_subcalls']+=1
   elif z[0]==0x9a:state['flip']+=1
   u.reg_write(UC_X86_REG_AX,0)
   if z[0]==0xe8:u.reg_write(UC_X86_REG_SP,u.reg_read(UC_X86_REG_SP)+2)
   u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+len(z))
  def intr(u,n,_):raise AssertionError((v,n,hex(u.reg_read(UC_X86_REG_CS)),hex(u.reg_read(UC_X86_REG_IP)),state))
  u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+ip,0,count=10000);assert state['reads']==len(stream) and state['work']==11+10*use_second;assert state['work_subcalls']==state['work']*6 and state['flip']==10*use_second;assert state['fatal']==(m==0) and state['done']==(m!=0);assert bytes(u.mem_read(ds*16+wc,4))==bytes(4)
  expected=None
  if m:
   a=max(m,1000//rate);x=max(1,(a+2)//4)&65535;y=max(1,((a*360+1400)&0xffffffff)//2800)&65535;expected=[x,y,x*2&65535];actual=[struct.unpack('<H',u.mem_read(ds*16+meta[k],2))[0] for k in ['si_global','di_global','twice_si_global']];assert actual==expected;assert u.reg_read(UC_X86_REG_SP)==0xe004
  results.append(dict(build=v,first_average=first,second_average=second,start=start,rate=rate,result=expected,**state,passed=True))
 print(v,'40 passed')
(o/'full_calibration_tests.json').write_text(json.dumps(dict(passed=len(results),cases=results,boundary='Original full calibration, work counter increment and cached-counter reader; synthetic sampled counter values, setup/render/work subcalls/flip mocked, fatal callee stop.'),indent=2)+'\n')
