from pathlib import Path
import json,struct
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass74/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));vp=json.load(open(r/'pass73/evidence/viewport_tests.json'))['locations'];results=[];locations=[]
for l in vp:
 v=l['build'];q=[s.split('\t') for s in (o/f'DOS{v}.exe.xrefs.tsv').read_text().splitlines()];entry=next(s[3] for s in q if s[0]=='width' and s[2]=='WRITE');cs,ip=[int(x,16) for x in entry.split(':')];rows=[s for s in q if s[:2]==['instruction',entry]];calls=[s for s in rows if s[3].startswith(('e8','9a'))];assert len(calls) in [6,7];roles=(['filename'] if len(calls)==7 else [])+['open','length','fatal','read','close','setup'];prefix=['filename'] if len(calls)==7 else [];sites={cs*16+int(s[2].split(':')[1],16):k for s,k in zip(calls,roles)};width=int(l['input_width'],16);height=int(l['geometry_globals'][0],16);ds=next(s['actual_DS'] for s in spec if s['build']==v);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 locations.append(dict(build=v,entry=entry,width_global=hex(width),setup_entry=l['entry']))
 cases=[('open',handle,16,320) for handle in [65535,0,0x8000]]+[('size',1,size,320) for size in [15,17,65552]]+[('load',1,16,w) for w in [0,1,64,319,320,321]]+[('read_none',1,16,320),('read_one',1,16,320)]
 for mode,handle,length,W in cases:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+0xe000,struct.pack('<HH',0,0x600));state=dict(events=[],done=False,fatal=False,trap=None,defaults=None)
  expectedwidth=304 if mode in ['open','read_none'] else 320 if mode=='read_one' else W
  def code(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop();return
   k=sites.get(a)
   if k is None:return
   state['events'].append(k);sp=u.reg_read(UC_X86_REG_SP);args=struct.unpack('<3H',u.mem_read(ds*16+sp,6))
   if k=='setup':assert struct.unpack('<H',u.mem_read(ds*16+width,2))[0]==expectedwidth;return
   if k=='filename':u.reg_write(UC_X86_REG_AX,args[1]);u.reg_write(UC_X86_REG_SP,sp+2)
   elif k=='open':
    assert args[1]==0x8000;name=bytes(u.mem_read(ds*16+args[0],32)).split(b'\0')[0];assert name.lower()==b'config.sav';state['defaults']=bytes(u.mem_read(ds*16+width,16)).hex();assert struct.unpack('<H',u.mem_read(ds*16+width,2))[0]==304;u.reg_write(UC_X86_REG_AX,handle)
   elif k=='length':assert args[0]==handle;u.reg_write(UC_X86_REG_AX,length&65535);u.reg_write(UC_X86_REG_DX,length>>16)
   elif k=='fatal':state['fatal']=True;u.emu_stop();return
   elif k=='read':
    assert args==(handle,width,16);payload=struct.pack('<H',W)+bytes([0x11])*14
    if mode!='read_none':u.mem_write(ds*16+width,payload[:1] if mode=='read_one' else payload)
    u.reg_write(UC_X86_REG_AX,0 if mode=='read_none' else 1 if mode=='read_one' else 16)
   elif k=='close':assert args[0]==handle
   u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+(3 if k=='filename' else 5))
  def intr(u,n,_):state['trap']=n;u.emu_stop()
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  u.emu_start(cs*16+ip,0,count=200000);assert state['fatal']==(mode=='size');assert state['trap']==(0 if mode=='load' and W in [0,1] else None);assert state['done']==(not state['fatal'] and state['trap'] is None)
  if mode=='open':assert state['events']==prefix+['open','setup']
  elif mode=='size':assert state['events']==prefix+['open','length','fatal']
  else:assert state['events']==prefix+['open','length','read','close','setup']
  if not state['fatal']:assert struct.unpack('<H',u.mem_read(ds*16+height,2))[0]==expectedwidth//2
  results.append(dict(build=v,mode=mode,handle=handle,file_length=length,input_width=W,result_width=expectedwidth if not state['fatal'] else None,**state,passed=True))
 print(v,len(cases),'passed')
(o/'config_load_tests.json').write_text(json.dumps(dict(locations=locations,cases=results,passed=len(results),mocks='filename helper, CRT file operations and fatal boundary; original configuration loader and complete setup/projection/clipping chain execute'),indent=2)+'\n')
