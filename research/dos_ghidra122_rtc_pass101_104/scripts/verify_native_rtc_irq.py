from pathlib import Path
import json,struct,hashlib,itertools
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass101/evidence';out=[]
locations=json.load(open(o/'irq_locations.json'));counters={x['build']:x['counter'] for x in json.load(open(r/'pass95/evidence/source_counters.json'))};clocks={x['build']:x for x in json.load(open(r/'pass95/evidence/clock_tests.json'))['locations']}
regs=[UC_X86_REG_EAX,UC_X86_REG_EBX,UC_X86_REG_ECX,UC_X86_REG_EDX,UC_X86_REG_ESI,UC_X86_REG_EDI,UC_X86_REG_EBP]
for l in locations:
 v=l['build'];b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 ds=l['actual_DS'];cs,ip=[int(x,16) for x in l['entry'].split(':')];l['exe_sha256']=hashlib.sha256(b).hexdigest()
 for cached,flags,ack in itertools.product([0,1,0xfffe,0xffff,0xfffffffe,0xffffffff,0x7fffffff,0x12345678],[0x2,0x202,0x402,0x602,0x247,0x647],[0,0xff]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+l['cached'],struct.pack('<I',cached));u.mem_write(ds*16+0xe000,struct.pack('<3H',0,0x600,flags));state=dict(done=False,ports=[],cache_writes=[])
  initial=[(0x10203040+i*0x11121314)&0xffffffff for i in range(len(regs))]
  for reg,val in zip(regs,initial):u.reg_write(reg,val)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000),(UC_X86_REG_DS,0x700),(UC_X86_REG_ES,0x800),(UC_X86_REG_EFLAGS,(flags&~0x300)|2)]:u.reg_write(reg,val)
  def code(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop()
  def mem(u,access,a,size,val,_):
   if ds*16+l['cached']<=a<ds*16+l['cached']+4:state['cache_writes'].append([a-ds*16,size,val])
  def inp(u,port,size,_):state['ports'].append(['in',port,size,ack]);assert port==0x71 and size==1;return ack
  def outp(u,port,size,val,_):state['ports'].append(['out',port,size,val])
  def intr(u,n,_):raise AssertionError(('unexpected interrupt',n))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,mem);u.hook_add(UC_HOOK_INSN,inp,None,1,0,UC_X86_INS_IN);u.hook_add(UC_HOOK_INSN,outp,None,1,0,UC_X86_INS_OUT);u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+ip,0,count=1000)
  actual=struct.unpack('<I',u.mem_read(ds*16+l['cached'],4))[0];expected=(cached+1)&0xffffffff
  assert state['done'] and actual==expected,(v,cached,actual)
  assert state['ports']==[['out',0x70,1,12],['in',0x71,1,ack],['out',0xa0,1,32],['out',0x20,1,32]]
  assert state['cache_writes']==[[l['cached'],4,expected]]
  assert [u.reg_read(reg) for reg in regs]==initial
  assert u.reg_read(UC_X86_REG_DS)==0x700 and u.reg_read(UC_X86_REG_ES)==0x800
  assert u.reg_read(UC_X86_REG_SP)==0xe006 and (u.reg_read(UC_X86_REG_EFLAGS)&0xfff)==flags
  # Original consumer in RTC mode reads exactly the ISR-produced value.
  ccs,cip=[int(z,16) for z in counters[v].split(':')];u.mem_write(ds*16+clocks[v]['flags'][1],b'\1');u.mem_write(ds*16+0xe000,struct.pack('<2H',0,0x600));state['done']=False
  for reg,val in [(UC_X86_REG_CS,ccs),(UC_X86_REG_IP,cip),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  u.reg_write(UC_X86_REG_DS,ds);u.emu_start(ccs*16+cip,0,count=1000);consumer=u.reg_read(UC_X86_REG_DX)<<16|u.reg_read(UC_X86_REG_AX)
  assert state['done'] and consumer==expected and u.reg_read(UC_X86_REG_SP)==0xe004
  assert len(state['cache_writes'])==1 and len(state['ports'])==4
  out.append(dict(consumer=consumer,build=v,before=cached,after=actual,flags=flags,ack_fixture=ack,**state,passed=True))
 print(v,'96 passed',flush=True)
(o/'irq_tests.json').write_text(json.dumps(dict(passed=len(out),locations=locations,cases=out,scope='Original RTC ISR including IRET executes. Interrupt-entry stack frame and CMOS input byte are fixtures; external IRQ delivery/frequency is not simulated.'),indent=2)+'\n')
