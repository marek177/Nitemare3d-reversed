from pathlib import Path
import json,re,struct,hashlib,itertools,datetime
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass100/evidence';out=[];locations=[]
specs=json.load(open(r/'baseline58/pass7/evidence/specs.json'));prior=json.load(open(r/'pass96/evidence/crt_clock_tests.json'))['locations']
clocks={l['build']:l for l in json.load(open(r/'pass96/evidence/source_clocks.json'))}
values=[None,'','UTC0','EST5','EST5EDT','CET-1CEST','ABC+5:30:45DEF','ABC-5:30:45DEF','ABC0:30','ABC0:00:01','ABC+0','ABC5:','ABC5::','ABC5:30:59XYZ','ABC5:30:59,','ABC23:59:59DEF','ABC-23:59:59DEF']
for loc in prior:
 v=loc['build'];ds=next(s['actual_DS'] for s in specs if s['build']==v);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 text=(o/f'DOS{v}.exe.getenv.c').read_text();env=int(re.search(r'DAT_[0-9a-f]+_([0-9a-f]+)',text)[1],16)
 gate=next(line.split('\t')[2] for line in (r/'pass97/evidence/seeds.tsv').read_text().splitlines() if line.startswith(v+'\ttz_gate\t'));cs,ip=[int(x,16) for x in gate.split(':')]
 init=loc['timezone_init'];tz=loc['timezone_seconds'];dst=loc['dst_enable'];locations.append(dict(build=v,gate=gate,environ_pointer=env,timezone_seconds=tz,dst_enable=dst,init_gate=init,exe_sha256=hashlib.sha256(b).hexdigest()))
 for value,month in itertools.product(values,[1,7]):
  clock=clocks[v];u_clock_cs,u_clock_ip=[int(x,16) for x in clock['entry'].split(':')]
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+init,b'\0\0');u.mem_write(ds*16+env,struct.pack('<H',0xd000));u.mem_write(ds*16+0xd000,struct.pack('<3H',0xd100,0 if value is None else 0xd200,0));u.mem_write(ds*16+0xd100,b'OTHER=fixture\0');u.mem_write(ds*16+0xd200,('TZ='+(value or '')+'\0').encode())
  u.mem_write(ds*16+clock['flags'][1],b'\0')
  initial=[struct.unpack('<i',u.mem_read(ds*16+tz,4))[0],struct.unpack('<H',u.mem_read(ds*16+dst,2))[0]]
  state={'done':False,'instructions':0,'requests':[],'structure':None}
  def code(u,a,size,_):
   state['instructions']+=1
   if a==0x6000:state['done']=True;u.emu_stop()
   acs,aip=[int(z,16) for z in clock['crt_call'].split(':')]
   if a==acs*16+aip+5:
    ptr=struct.unpack('<H',u.mem_read(ds*16+u.reg_read(UC_X86_REG_SP),2))[0];state['structure']=list(struct.unpack('<I3H',u.mem_read(ds*16+ptr,10)))
  def intr(u,n,_):
   ah=u.reg_read(UC_X86_REG_AX)>>8;assert n==33;state['requests'].append(ah)
   if ah==42:u.reg_write(UC_X86_REG_CX,1994);u.reg_write(UC_X86_REG_DX,month<<8|1);u.reg_write(UC_X86_REG_AX,0)
   elif ah==44:u.reg_write(UC_X86_REG_CX,12<<8|34);u.reg_write(UC_X86_REG_DX,56<<8|78)
   else:raise AssertionError(('unexpected interrupt',v,value,n,ah))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr)
  def run(entry):
   ecs,eip=entry
   state['done']=False;u.mem_write(ds*16+0xe000,struct.pack('<HH',0,0x600))
   for reg,val in [(UC_X86_REG_CS,ecs),(UC_X86_REG_IP,eip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
   u.emu_start(ecs*16+eip,0,count=100000);assert state['done'] and u.reg_read(UC_X86_REG_SP)==0xe004
  run((u_clock_cs,u_clock_ip));clock_result=u.reg_read(UC_X86_REG_DX)<<16|u.reg_read(UC_X86_REG_AX);actual=[struct.unpack('<i',u.mem_read(ds*16+tz,4))[0],struct.unpack('<H',u.mem_read(ds*16+dst,2))[0]]
  if value:
   m=re.fullmatch(r'(.{3})([+-]?)(\d+)(?::(\d*))?(?::(\d*))?(.*)',value);assert m,value
   name,sign,hour,minute,second,suffix=m.groups();expected=(int(hour)*3600+int(minute or 0)*60+int(second or 0))*(-1 if sign=='-' else 1);expected_dst=ord(suffix[0]) if suffix else 0;assert actual==[expected,expected_dst],(v,value,actual,expected,expected_dst)
  else:assert actual==initial,(v,value,actual,initial)
  epoch=int(datetime.datetime(1994,month,1,12,34,56,tzinfo=datetime.timezone.utc).timestamp());active=int(month==7 and actual[1]!=0);secs=(epoch+actual[0]-3600*active)&0xffffffff
  assert state['structure']==[secs,780,int(actual[0]/60)&65535,active],(v,value,month,state)
  assert clock_result==(secs*1000+780)&0xffffffff
  assert state['requests']==[42,44]
  assert struct.unpack('<H',u.mem_read(ds*16+init,2))[0]==1
  # Gate is one-shot even if environment changes afterward.
  u.mem_write(ds*16+0xd200,b'TZ=ZZZ9ZZZ\0');run((cs,ip));after=[struct.unpack('<i',u.mem_read(ds*16+tz,4))[0],struct.unpack('<H',u.mem_read(ds*16+dst,2))[0]];assert after==actual;assert struct.unpack('<H',u.mem_read(ds*16+init,2))[0]==1
  out.append(dict(build=v,TZ=value,month=month,clock_result=clock_result,structure=state['structure'],requests=state['requests'],initial=initial,result=actual,second_gate_result=after,instructions=state['instructions'],passed=True))
 print(v,len(values)*2,'passed',flush=True)
(o/'timezone_init_tests.json').write_text(json.dumps(dict(passed=len(out),locations=locations,cases=out,scope='Original gate, initializer, getenv, string and arithmetic functions execute. Near environ table/string globals are modeled startup fixtures. DOS date/time interrupt replies are modeled. No application or CRT function mock.'),indent=2)+'\n')
