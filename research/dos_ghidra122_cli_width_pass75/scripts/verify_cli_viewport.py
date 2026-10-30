from pathlib import Path
import json,struct,csv
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass75/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));locations=json.load(open(o/'parser_locations.json'));results=[];listing=[]
for l in locations:
 v=l['build'];cs,ip=[int(x,16) for x in l['entry'].split(':')];end=int(l['end'].split(':')[1],16);rows=[q for q in csv.DictReader(open(r/f'baseline58/pass7/audit/DOS{v}/instructions.tsv'),delimiter='\t') if q['address'].split(':')[0]==f'{cs:04x}' and ip<=int(q['address'].split(':')[1],16)<=end];listing.append(dict(build=v,entry=l['entry'],instructions=rows));calls=[q for q in rows if q['bytes'].startswith(('9a','e8'))];align=int(l['align_instruction'].split(':')[1],16);scan=max((q for q in calls if int(q['address'].split(':')[1],16)<align),key=lambda q:int(q['address'].split(':')[1],16));setup=next(q for q in calls if int(q['address'].split(':')[1],16)>align);sites={cs*16+int(q['address'].split(':')[1],16):q for q in calls};ds=next(s['actual_DS'] for s in spec if s['build']==v);width=int(l['width_global'],16);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 for value in [0,1,7,8,15,64,319,320,321,32767,65535,None]:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+0x5000,struct.pack('<3H',0x5100,0x5120,0x5140));u.mem_write(ds*16+0x5100,b'n3d\0');u.mem_write(ds*16+0x5120,('-'+l['option']).encode()+b'\0');u.mem_write(ds*16+0x5140,(str(value if value!=65535 else -1) if value is not None else 'bad').encode()+b'\0');u.mem_write(ds*16+0xe000,struct.pack('<4H',0,0x600,3,0x5000));state=dict(done=False,trap=None,events=[]);expected=(304 if value is None else value)&0xfff8
  def code(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop();return
   q=sites.get(a)
   if q is None:return
   state.setdefault('calls',[]).append(q['address']);address=q['address'];sp=u.reg_read(UC_X86_REG_SP);near=q['bytes'].startswith('e8');args=struct.unpack('<4H',u.mem_read(ds*16+sp,8))
   if address==setup['address']:
    state['events'].append('setup');assert struct.unpack('<H',u.mem_read(ds*16+width,2))[0]==expected;return
   if address==calls[0]['address']:state['events'].append('config_stub');u.mem_write(ds*16+width,struct.pack('<H',304))
   elif address==scan['address']:
    state['events'].append('scan_stub');assert args[2]==width;assert bytes(u.mem_read(ds*16+args[1],3))==b'%d\0'
    if value is not None:u.mem_write(ds*16+width,struct.pack('<H',value))
   u.reg_write(UC_X86_REG_AX,1 if address==scan['address'] and value is not None else 0)
   if near:u.reg_write(UC_X86_REG_SP,sp+2)
   u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+(3 if near else 5))
  def intr(u,n,_):state['trap']=n;u.emu_stop()
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  u.emu_start(cs*16+ip,0,count=250000);assert state['events']==['config_stub','scan_stub','setup'],(v,value,state,hex(u.reg_read(UC_X86_REG_IP))); assert state['trap']==(0 if expected==0 else None);assert state['done']==(expected!=0);assert struct.unpack('<H',u.mem_read(ds*16+width,2))[0]==expected
  results.append(dict(build=v,option=l['option'],value=value,result_width=expected,**state,passed=True))
 print(v,'12 passed')
(o/'parser_instructions.json').write_text(json.dumps(listing,indent=2)+'\n');(o/'cli_tests.json').write_text(json.dumps(dict(cases=results,passed=len(results),mocks='all parser call sites except original viewport setup; numeric conversion result injected; original dispatch/alignment and full setup chain execute'),indent=2)+'\n')
