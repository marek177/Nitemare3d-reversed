from pathlib import Path
import json,struct,itertools
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass103/evidence';out=[]
pairs=[(100,99),(100,100),(100,101),(0,0),(0xffffffff,0),(0xffffffff,0xffffffff),(2,0xfffffffe),(0xfffffffe,8)]
for l in json.load(open(o/'locations.json')):
 v=l['build'];ds=l['actual_DS'];cs,ip=[int(z,16) for z in l['entry'].split(':')];sc,si=[int(z,16) for z in l['stop'].split(':')];b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 for (now,deadline),frame,count,delay in itertools.product(pairs,[0,1,254,255],[0,1,2,255,256,0x8000,0xffff],[0,1,10,0xffff]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+l['cached'],struct.pack('<I',now));u.mem_write(ds*16+0xd000,struct.pack('<2H',count,delay));u.mem_write(0x91003,bytes([frame]));u.mem_write(0x91008,struct.pack('<I',deadline));state={'done':False,'writes':[]}
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x9000),(UC_X86_REG_SI,0x1000),(UC_X86_REG_CX,0xd000),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  def code(u,a,size,_):
   if a==sc*16+si:state['done']=True;u.emu_stop()
  def mem(u,access,a,size,val,_):state['writes'].append([a,size,val])
  def intr(u,n,_):raise AssertionError(n)
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,mem);u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+ip,0,count=100)
  due=deadline<=now;next_frame=(frame+1)&255;signed_count=count if count<0x8000 else count-0x10000
  if next_frame>=signed_count:next_frame=0
  expected_frame=next_frame if due else frame;expected_deadline=(now+delay)&0xffffffff if due else deadline
  actual_frame=u.mem_read(0x91003,1)[0];actual_deadline=struct.unpack('<I',u.mem_read(0x91008,4))[0]
  assert state['done'] and actual_frame==expected_frame and actual_deadline==expected_deadline,(v,now,deadline,frame,count,delay,state)
  assert all(a in [0x91003,0x91008,0x9100a] for a,size,val in state['writes'])
  assert not state['writes'] if not due else len(state['writes']) in [3,4]
  out.append(dict(build=v,now=now,deadline=deadline,frame=frame,count=count,delay=delay,due=due,frame_after=actual_frame,deadline_after=actual_deadline,passed=True))
 print(v,'896 cases passed',flush=True)
(o/'deadline_tests.json').write_text(json.dumps(dict(passed=len(out),cases=out,scope='Only original animation state1 deadline/update basic-block region executes; entry registers, descriptor and slot record are fixtures. Stops before render/position helper. No IRQ interleaving; not a complete scheduler or function test.'),indent=2)+'\n')
