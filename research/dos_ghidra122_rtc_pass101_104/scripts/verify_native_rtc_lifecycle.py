from pathlib import Path
import json,struct,hashlib,itertools,re
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass102/evidence';out=[];locations=[]
for l in json.load(open(r/'pass101/evidence/irq_locations.json')):
 v=l['build'];b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 c=(r/f'pass101/evidence/DOS{v}.exe.rtc_setup.c').read_text();active=int(re.search(r'DAT_[0-9a-f]+_([0-9a-f]+)',c)[1],16);old=int(re.search(r'_DAT_[0-9a-f]+_([0-9a-f]+) = CONCAT22',c)[1],16);ds=l['actual_DS'];cs,ip=[int(z,16) for z in l['rtc_setup'].split(':')];isg,iip=[int(z,16) for z in l['entry'].split(':')];locations.append(dict(**l,active=active,saved_vector=old))
 for a,breg,pic,flags in itertools.product([0x20,0x70],[0,0xff],[0,0xff],[2,0x202]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+active,b'\0');u.mem_write(ds*16+l['cached'],struct.pack('<I',0x12345678));state={'done':False,'index':0,'cmos':{10:a,11:breg,12:0x40},'pic':pic,'vector':[0x4321,0x1234],'ports':[],'interrupts':[]}
  def code(u,addr,size,_):
   if addr==0x6000:state['done']=True;u.emu_stop()
  def inp(u,port,size,_):
   assert size==1
   if port==0x71:val=state['cmos'][state['index']]
   elif port==0xa1:val=state['pic']
   else:raise AssertionError(port)
   state['ports'].append(['in',port,val]);return val
  def outp(u,port,size,val,_):
   assert size==1;state['ports'].append(['out',port,val])
   if port==0x70:state['index']=val
   elif port==0x71:state['cmos'][state['index']]=val
   elif port==0xa1:state['pic']=val
   else:raise AssertionError(port)
  def intr(u,n,_):
   ax=u.reg_read(UC_X86_REG_AX);assert n==33 and ax&255==0x70
   if ax>>8==0x35:u.reg_write(UC_X86_REG_BX,state['vector'][0]);u.reg_write(UC_X86_REG_ES,state['vector'][1]);state['interrupts'].append(['get',*state['vector']])
   elif ax>>8==0x25:state['vector']=[u.reg_read(UC_X86_REG_DX),u.reg_read(UC_X86_REG_DS)];state['interrupts'].append(['set',*state['vector']])
   else:raise AssertionError(hex(ax))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_INSN,inp,None,1,0,UC_X86_INS_IN);u.hook_add(UC_HOOK_INSN,outp,None,1,0,UC_X86_INS_OUT)
  def run(arg,iflags):
   state['done']=False;u.mem_write(ds*16+0xe000,struct.pack('<3H',0,0x600,arg))
   for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000),(UC_X86_REG_EFLAGS,iflags)]:u.reg_write(reg,val)
   u.emu_start(cs*16+ip,0,count=10000);assert state['done'] and u.reg_read(UC_X86_REG_SP)==0xe004 and u.reg_read(UC_X86_REG_DS)==ds
   assert struct.unpack('<I',u.mem_read(ds*16+l['cached'],4))[0]==0x12345678
  snapshots=[]
  def snap(tag):snapshots.append(dict(stage=tag,active=u.mem_read(ds*16+active,1)[0],cmos=dict(state['cmos']),pic=state['pic'],vector=state['vector'][:],ports=len(state['ports']),interrupts=len(state['interrupts']),IF=bool(u.reg_read(UC_X86_REG_EFLAGS)&0x200)))
  run(0,flags);snap('installed');assert u.mem_read(ds*16+active,1)==b'\1';assert state['cmos']=={10:(a&0xf0)|6,11:breg|0x40,12:0x40};assert state['pic']==pic&0xfe;assert state['vector']==[iip,isg];assert struct.unpack('<2H',u.mem_read(ds*16+old,4))==(0x4321,0x1234);assert u.reg_read(UC_X86_REG_EFLAGS)&0x200
  ni,np=len(state['interrupts']),len(state['ports']);run(0,flags);snap('install_again');assert len(state['interrupts'])==ni and len(state['ports'])==np and bool(u.reg_read(UC_X86_REG_EFLAGS)&0x200)==bool(flags&0x200)
  run(1,flags);snap('removed');assert u.mem_read(ds*16+active,1)==b'\0';assert state['vector']==[0x4321,0x1234];assert state['pic']==pic|1;assert state['cmos']=={10:(a&0xf0)|6,11:breg&0xbf,12:0x40};assert u.reg_read(UC_X86_REG_EFLAGS)&0x200
  ni,np=len(state['interrupts']),len(state['ports']);run(1,flags);snap('remove_again');assert len(state['interrupts'])==ni and len(state['ports'])==np and bool(u.reg_read(UC_X86_REG_EFLAGS)&0x200)==bool(flags&0x200)
  run(2,flags);snap('unknown_arg');assert len(state['interrupts'])==ni and len(state['ports'])==np
  assert state['interrupts']==[['get',0x4321,0x1234],['set',iip,isg],['set',0x4321,0x1234]]
  expected=[['out',0x70,10],['in',0x71,a],['out',0x70,10],['out',0x71,(a&0xf0)|6],['out',0x70,11],['in',0x71,breg],['out',0x70,11],['out',0x71,breg|0x40],['out',0x70,12],['in',0x71,0x40],['in',0xa1,pic],['out',0xa1,pic&0xfe],['in',0xa1,pic&0xfe],['out',0xa1,pic|1],['out',0x70,11],['in',0x71,breg|0x40],['out',0x70,11],['out',0x71,breg&0xbf]]
  assert state['ports']==expected,(v,state['ports'],expected)
  out.append(dict(build=v,regA=a,regB=breg,PIC=pic,entry_flags=flags,snapshots=snapshots,ports=state['ports'],interrupts=state['interrupts'],passed=True))
 print(v,'16 lifecycles /80 calls passed',flush=True)
(o/'rtc_lifecycle_tests.json').write_text(json.dumps(dict(passed=len(out),native_calls=len(out)*5,locations=locations,cases=out,scope='Original RTC setup, CMOS helpers, DOS getvect/setvect wrappers execute. CMOS/PIC state and DOS interrupt-vector replies/effects are modeled; no application or CRT function mock. No asynchronous IRQ delivery.'),indent=2)+'\n')
