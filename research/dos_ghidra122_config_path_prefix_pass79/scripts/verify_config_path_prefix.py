from pathlib import Path
import json,struct
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass79/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));loc=json.load(open(o/'locations.json'));native=json.load(open(r/'pass78/evidence/native_scan_tests.json'))['locations'];results=[]
for l in loc:
 v=l['build'];ds=next(x['actual_DS'] for x in spec if x['build']==v);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 def new():
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));return u
 def regs(u,entry,args):
  cs,ip=[int(x,16) for x in entry.split(':')];u.mem_write(ds*16+0xe000,struct.pack('<'+'H'*(len(args)+2),0,0x600,*args))
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  return cs*16+ip
 def cstr(u,off):return bytes(u.mem_read(ds*16+off,200)).split(b'\0')[0].decode()
 for prefix in ['', 'C:\\N3D\\','C:\\N3D','./data/','data path/']:
  for name in ['CONFIG.SAV','USER.SAV','MAP.1']:
   u=new();u.mem_write(ds*16+l['prefix'],prefix.encode()+b'\0');u.mem_write(ds*16+0x5000,name.encode()+b'\0');state={'done':False}
   def hook(u,a,size,_):
    if a==0x6000:state['done']=True;u.emu_stop()
   u.hook_add(UC_HOOK_CODE,hook);start=regs(u,l['helper'],[0x5000]);u.emu_start(start,0,count=100000);ptr=u.reg_read(UC_X86_REG_AX);assert state['done'] and cstr(u,ptr)==prefix+name;expectedptr=0xdffe-0x52 if v=='17' else l['buffer'];assert ptr==expectedptr
   u.mem_write(ds*16+0x5000,b'NEXT\0');state['done']=False;u.emu_start(regs(u,l['helper'],[0x5000]),0,count=100000);assert state['done'] and u.reg_read(UC_X86_REG_AX)==ptr and cstr(u,ptr)==prefix+'NEXT'
   results.append(dict(build=v,case='direct_concat',prefix=prefix,name=name,pointer=ptr,storage='returned stack local' if v=='17' else 'global',passed=True))
 rows=next(x['instructions'] for x in json.load(open(r/'pass75/evidence/parser_instructions.json')) if x['build']==v);calls=[x for x in rows if x['bytes'].startswith(('9a','e8'))];cs=int(l['parser'].split(':')[0],16);sites={cs*16+int(x['address'].split(':')[1],16):x for x in calls};configcs,configip=[int(x,16) for x in l['config_loader'].split(':')];ni=next(x for x in native if x['build']==v);scs,sip=[int(x,16) for x in ni['entry'].split(':')];openaddr=int(l['open_call'].split(':')[0],16)*16+int(l['open_call'].split(':')[1],16)
 for inputs in [['C:\\N3D\\'],['C:\\N3D'],['a b/'],[''],['  foo/'],['../data/'],['foo/','bar/']]:
  u=new();u.mem_write(ds*16+l['prefix'],b'\0');u.mem_write(ds*16+int(ni['stack_limit_global'],16),struct.pack('<H',0x8000));texts=['n3d']
  for path in inputs:texts+=['-a',path]
  ptrs=[0x5000+j*0x100 for j in range(len(texts))];u.mem_write(ds*16+0x4800,struct.pack('<'+'H'*len(ptrs),*ptrs))
  for ptr,text in zip(ptrs,texts):u.mem_write(ds*16+ptr,text.encode()+b'\0')
  state=dict(done=False,opens=[],scan_calls=0,interrupts=[])
  def hook(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop();return
   if a==openaddr:
    args=struct.unpack('<2H',u.mem_read(ds*16+u.reg_read(UC_X86_REG_SP),4));assert args[1]==0x8000;state['opens'].append(cstr(u,args[0]));u.reg_write(UC_X86_REG_AX,65535);u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+5);return
   q=sites.get(a)
   if q is None:return
   z=bytes.fromhex(q['bytes']);near=z[0]==0xe8
   if not near:
    tc=int.from_bytes(z[3:5],'little');ti=int.from_bytes(z[1:3],'little')
    if (tc,ti)==(configcs,configip):return
    if (tc,ti)==(scs,sip):state['scan_calls']+=1;return
   u.reg_write(UC_X86_REG_AX,0)
   if near:u.reg_write(UC_X86_REG_SP,u.reg_read(UC_X86_REG_SP)+2)
   u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+(3 if near else 5))
  def intr(u,n,_):state['interrupts'].append(n);u.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,intr);u.emu_start(regs(u,l['parser'],[len(texts),0x4800]),0,count=500000);prefix='';expected=['config.sav']
  for text in inputs:
   if text.split():prefix=text.split()[0]
   expected.append(prefix+'config.sav')
  assert state['done'] and not state['interrupts'] and state['scan_calls']==len(inputs);assert state['opens']==expected,(v,inputs,state,expected);assert cstr(u,l['prefix'])==prefix
  results.append(dict(build=v,case='native_cli_prefix',inputs=inputs,**state,passed=True))
 print(v,'22 passed')
(o/'path_tests.json').write_text(json.dumps(dict(cases=results,passed=len(results),boundary='direct helper unmocked; CLI uses native sscanf/helper/config defaults and setup; open returns missing, other startup/final helpers mocked; valid CRT stack-limit fixture'),indent=2)+'\n')
