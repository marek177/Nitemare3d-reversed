from pathlib import Path
import json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass63/evidence'; specs=json.load(open(r/'baseline58/pass7/evidence/specs.json'));loc=json.load(open(o/'lookup_static.json'));results=[]
for l in loc:
 v=l['build'];cs,ip=[int(x,16) for x in l['entry'].split(':')];rows=l['instructions'];flag=int.from_bytes(bytes.fromhex(next(x['bytes'] for x in rows if x['bytes'].startswith('803e')))[2:4],'little');seg=int.from_bytes(bytes.fromhex(next(x['bytes'] for x in rows if x['bytes'].startswith('ba')))[1:3],'little');calls=[x for x in rows if x['bytes'].startswith('9a')];assert len(calls)==5;sites={cs*16+int(x['address'].split(':')[1],16):k for x,k in zip(calls,['open','fatal_open','read','fatal_read','close'])};ds=next(s['actual_DS'] for s in specs if s['build']==v);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+4*k);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 l.update(flag=hex(flag),table_segment=hex(seg),exe_sha256=hashlib.sha256(b).hexdigest())
 for case,id in [(mode,id) for mode in ['cached','load'] for id in [0,31,32,65535]]+[('open_fail',4),('short_read',4)]:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+flag,bytes([0 if case=='cached' else 1]));data=bytes((i*13+7)%256 for i in range(192));u.mem_write(seg*16,data);state=dict(events=[],fatal=None,returned=False)
  def hook(u,a,size,_):
   if a==0x6000:state['returned']=True;u.emu_stop();return
   k=sites.get(a)
   if k is None:return
   state['events'].append(k);sp=u.reg_read(UC_X86_REG_SP);args=struct.unpack('<4H',u.mem_read(ds*16+sp,8));assert bytes(u.mem_read(ds*16+flag,1))==b'\0'
   if k=='open':
    assert args[1]==0x8000
    name=bytes(u.mem_read(ds*16+args[0],32)).split(b'\0')[0];assert name.lower()==b'uif.dat';u.reg_write(UC_X86_REG_AX,65535 if case=='open_fail' else 0x4444)
   elif k=='read':
    assert args==(0x4444,0,seg,192),args;u.mem_write(seg*16,data);u.reg_write(UC_X86_REG_AX,191 if case=='short_read' else 192)
   elif k.startswith('fatal'):state['fatal']=k;u.emu_stop();return
   elif k=='close':assert args[0]==0x4444
   u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+5)
  u.hook_add(UC_HOOK_CODE,hook)
  def run():
   state['returned']=False;u.mem_write(ds*16+0xe000,struct.pack('<HHH',0,0x600,id))
   for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
   u.emu_start(cs*16+ip,0,count=10000)
  run();expected='fatal_open' if case=='open_fail' else 'fatal_read' if case=='short_read' else None;assert state['fatal']==expected and state['returned']==(expected is None)
  if expected is None:
   assert (u.reg_read(UC_X86_REG_DX),u.reg_read(UC_X86_REG_AX))==(seg,(id*6)&65535);events=list(state['events']);run();assert state['events']==events
  assert bytes(u.mem_read(seg*16,192))==data
  results.append(dict(build=v,case=case,id=id,events=state['events'],fatal=expected,passed=True))
 print(v,'10 passed')
(o/'lookup_tests.json').write_text(json.dumps(dict(locations=loc,cases=results,passed=len(results)),indent=2)+'\n')
