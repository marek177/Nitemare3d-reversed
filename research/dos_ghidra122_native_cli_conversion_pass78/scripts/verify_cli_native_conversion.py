from pathlib import Path
import json,struct
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass78/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));loc=json.load(open(r/'pass75/evidence/parser_locations.json'));native=json.load(open(o/'native_scan_tests.json'))['locations'];disp=json.load(open(r/'pass76/evidence/switch_recovery_tests.json'))['cases'];results=[]
values={'123':(1,123),'bad':(0,None),'':(65535,None),'+':(65535,None),'65536':(1,0),'-1':(1,65535)}
for l in loc:
 v=l['build'];cs,ip=[int(x,16) for x in l['entry'].split(':')];rows=next(x['instructions'] for x in json.load(open(r/'pass75/evidence/parser_instructions.json')) if x['build']==v);calls=[x for x in rows if x['bytes'].startswith(('e8','9a'))];sites={cs*16+int(x['address'].split(':')[1],16):x for x in calls};mapping={x['option']:x['target'] for x in disp if x['build']==v};usage=next(x for x in calls if x['address']>=mapping['g']);ub=bytes.fromhex(usage['bytes']);ui=int(usage['address'].split(':')[1],16);usage_target=(ui+3+int.from_bytes(ub[1:3],'little',signed=True))&65535;ni=next(x for x in native if x['build']==v);scanentry=ni['entry'];scs,sip=[int(x,16) for x in scanentry.split(':')];limit=int(ni['stack_limit_global'],16);ds=next(x['actual_DS'] for x in spec if x['build']==v);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 cases=[(c,[text]) for c in 'cdefl' for text in values]+([('q',args) for args in [['ff','7'],['bad','7'],['z','7'],['','7'],['ff','bad'],['ff',''],['ff','+']]] if v!='10' else [])
 for option,argslist in cases:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+limit,struct.pack('<H',0x8000));ptrs=[0x5100,0x5120]+[0x5140+j*0x40 for j in range(len(argslist))];u.mem_write(ds*16+0x5000,struct.pack('<'+'H'*len(ptrs),*ptrs))
  for ptr,text in zip(ptrs,['n3d','-'+option]+argslist):u.mem_write(ds*16+ptr,text.encode()+b'\0')
  u.mem_write(ds*16+0xe000,struct.pack('<4H',0,0x600,len(ptrs),0x5000));state=dict(done=False,usage=False,scans=[],pending=None,tail=None,interrupts=[])
  def code(u,a,size,_):
   if state['pending'] and a==state['pending']['return_address']:
    item=state.pop('pending');item['return_AX']=u.reg_read(UC_X86_REG_AX);item['after']=struct.unpack('<H',u.mem_read(ds*16+item['dest'],2))[0];state['scans'].append(item);state['pending']=None
   if a==0x6000:state['done']=True;u.emu_stop();return
   q=sites.get(a)
   if q is None:return
   z=bytes.fromhex(q['bytes']);near=z[0]==0xe8;sp=u.reg_read(UC_X86_REG_SP);args=struct.unpack('<3H',u.mem_read(ds*16+sp,6));target=(int(q['address'].split(':')[1],16)+3+int.from_bytes(z[1:3],'little',signed=True))&65535 if near else None
   if not near and int.from_bytes(z[3:5],'little')==scs and int.from_bytes(z[1:3],'little')==sip:
    fmt=bytes(u.mem_read(ds*16+args[1],3)).split(b'\0')[0].decode();state['pending']=dict(format=fmt,dest=args[2],before=struct.unpack('<H',u.mem_read(ds*16+args[2],2))[0],return_address=a+5);return
   if near and target==usage_target:state['usage']=True;u.emu_stop();return
   if q['address']==calls[-2]['address']:state['tail']=list(args)
   u.reg_write(UC_X86_REG_AX,0)
   if near:u.reg_write(UC_X86_REG_SP,sp+2)
   u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+(3 if near else 5))
  def intr(u,n,_):state['interrupts'].append(n);u.emu_stop()
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  u.emu_start(cs*16+ip,0,count=1000000);assert not state['interrupts'] and state['pending'] is None
  if option!='q':expected=[values[argslist[0]]];fail=option=='l' and expected[0][0]==0
  else:
   first={'ff':(1,255),'bad':(1,0xbad),'z':(0,None),'':(65535,None)}[argslist[0]];expected=[first];fail=first[0]!=1
   if not fail:
    second={'7':(1,7),'bad':(0,None),'':(65535,None),'+':(65535,None)}[argslist[1]];expected.append(second);fail=second[0]!=1
  assert state['usage']==fail and state['done']==(not fail),(v,option,argslist,state);assert len(state['scans'])==len(expected)
  for index,(item,(ret,val)) in enumerate(zip(state['scans'],expected)):
   assert item['format']==('%x' if option=='q' and index==0 else '%d');assert item['return_AX']==ret and item['after']==(item['before'] if val is None else val),(v,option,argslist,item)
  if state['tail'] and option in ['e','l']:
   idx=0 if option=='e' else 1;val=expected[0][1];assert state['tail'][idx]==(1 if val is None else val)
  results.append(dict(build=v,option=option,inputs=argslist,**state,passed=True))
 print(v,len(cases),'passed')
(o/'cli_native_tests.json').write_text(json.dumps(dict(cases=results,passed=len(results),mocks='parser startup/final helpers and usage stop; original sscanf and CRT internals execute unchanged with explicit stack-limit fixture'),indent=2)+'\n')
