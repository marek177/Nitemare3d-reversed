from pathlib import Path
import json,struct,hashlib,csv
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass83/evidence';results=[]
for meta in json.load(open(r/'pass74/evidence/config_load_tests.json'))['locations']:
 l=dict(build=meta['build'],config_loader=meta['entry']);l['prefix']=next((x['prefix'] for x in json.load(open(r/'pass79/evidence/locations.json')) if x['build']==l['build']),None)
 v=l['build'];ds=next(x['actual_DS'] for x in json.load(open(r/'baseline58/pass7/evidence/specs.json')) if x['build']==v)
 b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 width=int(meta['width_global'],16)
 rows=[x.split('\t') for x in (r/f'pass74/evidence/DOS{v}.exe.xrefs.tsv').read_text().splitlines()];calls=[x for x in rows if x[:2]==['instruction',l['config_loader']] and x[3].startswith(('e8','9a'))];calls=calls[-6:];fcs=int(l['config_loader'].split(':')[0],16);fatal=int(calls[2][2].split(':')[1],16)+fcs*16
 z=bytes.fromhex(calls[0][3]);ocs=int.from_bytes(z[3:5],'little');oip=int.from_bytes(z[1:3],'little');audit=list(csv.DictReader(open(r/f'baseline58/pass7/audit/DOS{v}/instructions.tsv'),delimiter='\t'));store=next(x for x in audit if x['address'].split(':')[0]==f'{ocs:04x}' and oip<=int(x['address'].split(':')[1],16)<oip+0x200 and x['bytes'].startswith('888f'));table=int.from_bytes(bytes.fromhex(store['bytes'])[2:4],'little')
 for mode in ['normal','handle0','missing','short0','short1','short15','read_error','close_error','size15','size17','size65552','seek_end_error','seek_current_error','seek_restore_error']:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+(l['prefix'] or 0x7000),b'\0');u.mem_write(ds*16+0xe000,struct.pack('<HH',0,0x600));cs,ip=[int(x,16) for x in l['config_loader'].split(':')];state={'done':False,'fatal':False,'requests':[],'position':0};defaults=[None];handle=0 if mode=='handle0' else 5
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  def code(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop()
   if a==fatal:state['fatal']=True;u.emu_stop()
  def intr(u,n,_):
   ax=u.reg_read(UC_X86_REG_AX);dx=u.reg_read(UC_X86_REG_DX);cx=u.reg_read(UC_X86_REG_CX);assert n==33;state['requests'].append(dict(ax=ax,bx=u.reg_read(UC_X86_REG_BX),cx=cx,dx=dx));u.reg_write(UC_X86_REG_EFLAGS,u.reg_read(UC_X86_REG_EFLAGS)&~1)
   def fail():u.reg_write(UC_X86_REG_AX,5);u.reg_write(UC_X86_REG_EFLAGS,u.reg_read(UC_X86_REG_EFLAGS)|1)
   if ax==0x3d00:
    defaults[0]=bytes(u.mem_read(ds*16+width,16));assert defaults[0][:2]==struct.pack('<H',304);u.reg_write(UC_X86_REG_AX,handle)
    if mode=='missing':fail()
   elif ax==0x4400:u.reg_write(UC_X86_REG_DX,0)
   elif ax==0x4300:u.reg_write(UC_X86_REG_CX,0)
   elif ax>>8==0x42:
    length={'size15':15,'size17':17,'size65552':65552}.get(mode,16);pos=length if ax&255==2 else 0;u.reg_write(UC_X86_REG_AX,pos&65535);u.reg_write(UC_X86_REG_DX,pos>>16)
    if (mode=='seek_end_error' and ax&255==2) or (mode=='seek_current_error' and ax&255==1) or (mode=='seek_restore_error' and ax&255==0):fail()
    else:state['position']=pos
   elif ax>>8==0x3f:
    assert cx==16 and dx==width;count={'short0':0,'short1':1,'short15':15,'read_error':0,'seek_restore_error':0}.get(mode,16);u.mem_write(ds*16+dx,(struct.pack('<H',320)+b'\x11'*14)[:count]);u.reg_write(UC_X86_REG_AX,count)
    if mode=='read_error':fail()
    else:state['position']+=count
   elif ax>>8==0x3e:
    u.reg_write(UC_X86_REG_AX,0)
    if mode=='close_error':fail()
   else:raise AssertionError(hex(ax))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+ip,0,count=200000)
  fatal_expected=mode.startswith('size') or mode in ['seek_end_error','seek_current_error'];assert state['fatal']==fatal_expected and state['done']==(not fatal_expected),(v,mode,state)
  req=[x['ax']>>8 for x in state['requests']];prefix=[0x3d] if mode=='missing' else [0x3d,0x44,0x43]
  assert req==prefix+([] if mode in ['missing','handle0'] else ([0x42] if mode=='seek_current_error' else [0x42,0x42,0x42])+([] if fatal_expected else [0x3f,0x3e])),(mode,req)
  if not fatal_expected:
   count=0 if mode in ['missing','handle0','short0','read_error','seek_restore_error'] else 1 if mode=='short1' else 15 if mode=='short15' else 16;expected=bytearray(defaults[0]);expected[:count]=(struct.pack('<H',320)+b'\x11'*14)[:count];assert bytes(u.mem_read(ds*16+width,16))==expected
  expected_desc=1 if mode in ['handle0','close_error','size15','size17','size65552','seek_end_error','seek_current_error'] else 0;assert u.mem_read(ds*16+table+handle,1)[0]==expected_desc
  out=dict(build=v,mode=mode,exe_sha256=hashlib.sha256(b).hexdigest(),descriptor_byte=u.mem_read(ds*16+table+handle,1)[0],config_hex=bytes(u.mem_read(ds*16+width,16)).hex(),**state,passed=True);results.append(out)
 print(v,'14 passed')
(o/'config_chain_tests.json').write_text(json.dumps(dict(passed=len(results),cases=results,boundary='Original config loader/helper/CRT open,length,read,close and viewport chain; synthetic DOS INT21 responses; stop before fatal callee.'),indent=2)+'\n')
