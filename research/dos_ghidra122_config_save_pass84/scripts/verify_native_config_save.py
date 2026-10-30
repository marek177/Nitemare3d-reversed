from pathlib import Path
import json,struct,hashlib
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass84/evidence';results=[];locations=[]
entries={'10':'1273:0c4e','11':'1275:0c74','12':'1275:0c86','15':'1277:0cae','17':'1277:0d06','18':'1277:0d04'}
for m in json.load(open(r/'pass74/evidence/config_load_tests.json'))['locations']:
 v=m['build'];ds=next(x['actual_DS'] for x in json.load(open(r/'baseline58/pass7/evidence/specs.json')) if x['build']==v);entry=entries[v];cs,ip=[int(x,16) for x in entry.split(':')];width=int(m['width_global'],16)
 b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 locations.append(dict(build=v,entry=entry,config=width))
 for mode in ['existing','handle0','open_error','short0','short7','write_error','close_error','create','create_error','reopen_error','truncate_error']:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+0xe000,struct.pack('<HH',0,0x600));payload=struct.pack('<8H',320,0x1234,0x5678,0x9abc,0xdef0,0x102,0x304,0x506);u.mem_write(ds*16+width,payload)
  pre=next((x['prefix'] for x in json.load(open(r/'pass79/evidence/locations.json')) if x['build']==v),None)
  if pre:u.mem_write(ds*16+pre,b'\0')
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  state={'done':False,'requests':[],'written':[]};handle=0 if mode=='handle0' else 5
  def code(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop()
  def intr(u,n,_):
   ax=u.reg_read(UC_X86_REG_AX);dx=u.reg_read(UC_X86_REG_DX);cx=u.reg_read(UC_X86_REG_CX);assert n==33;req=dict(ax=ax,bx=u.reg_read(UC_X86_REG_BX),cx=cx,dx=dx);state['requests'].append(req);u.reg_write(UC_X86_REG_EFLAGS,u.reg_read(UC_X86_REG_EFLAGS)&~1)
   def fail(e=5):u.reg_write(UC_X86_REG_AX,e);u.reg_write(UC_X86_REG_EFLAGS,u.reg_read(UC_X86_REG_EFLAGS)|1)
   if ax>>8==0x3d:
    req['path']=bytes(u.mem_read(ds*16+dx,100)).split(b'\0')[0].decode('latin1');u.reg_write(UC_X86_REG_AX,handle)
    if mode=='open_error':fail()
    if mode in ['create','create_error','reopen_error'] and sum(x['ax']>>8==0x3d for x in state['requests'])==1:fail(2)
    elif mode=='reopen_error':fail()
   elif ax==0x4400:u.reg_write(UC_X86_REG_DX,0)
   elif ax==0x4300:u.reg_write(UC_X86_REG_CX,0)
   elif ax>>8==0x3c:
    u.reg_write(UC_X86_REG_AX,handle)
    if mode=='create_error':fail()
   elif ax>>8==0x40:
    if cx:
     assert cx==16 and dx==width;req['payload']=bytes(u.mem_read(ds*16+dx,cx)).hex();count={'short0':0,'short7':7,'write_error':0}.get(mode,16);state['written'].append(req['payload'][:count*2]);u.reg_write(UC_X86_REG_AX,count)
     if mode=='write_error':fail()
    else:
     u.reg_write(UC_X86_REG_AX,0)
     if mode=='truncate_error':fail()
   elif ax>>8==0x3e:
    u.reg_write(UC_X86_REG_AX,0)
    if mode=='close_error':fail()
   else:raise AssertionError((v,mode,hex(ax)))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+ip,0,count=100000);assert state['done'],(v,mode,state);assert bytes(u.mem_read(ds*16+width,16))==payload
  seq=[x['ax']>>8 for x in state['requests']];expected=[0x3d,0x44,0x40,0x43,0x40,0x3e]
  if mode=='handle0':expected=expected[:4]
  elif mode=='open_error':expected=[0x3d]
  elif mode=='create':expected=[0x3d,0x3c,0x3e,0x3d,0x43,0x40,0x3e]
  elif mode=='create_error':expected=[0x3d,0x3c]
  elif mode=='reopen_error':expected=[0x3d,0x3c,0x3e,0x3d]
  assert seq==expected,(v,mode,seq)
  for req in state['requests']:
   if req['ax']>>8==0x3d:assert req['path']=='config.sav' and req['ax']==0x3d01
   if req['ax']>>8 in [0x40,0x3e]:assert req['bx']==handle
   if 'payload' in req:assert req['payload']==payload.hex()
  count=0 if mode in ['short0','write_error'] else 7 if mode=='short7' else 16
  assert state['written']==([] if mode in ['handle0','open_error','create_error','reopen_error'] else [payload[:count].hex()])
  assert u.reg_read(UC_X86_REG_SP)==0xe004
  results.append(dict(build=v,mode=mode,exe_sha256=hashlib.sha256(b).hexdigest(),**state,passed=True))
 print(v,'11 passed')
(o/'save_tests.json').write_text(json.dumps(dict(locations=locations,passed=len(results),cases=results,boundary='Original save/helper/CRT chain; synthetic INT21 responses, no function mocks.'),indent=2)+'\n')
