from pathlib import Path
import json,struct,hashlib,itertools
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass81/evidence';out=[]
for v,cs,entry,ds,limit,table,errno,rawerr in [('17',0x21d1,0x1c72,0x3754,0x20ec,0x20ee,0x20dc,0x20ea),('18',0x21ea,0x1c76,0x376d,0x2126,0x2128,0x2116,0x2124)]:
 b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 cases=[dict(error=e,handle=5,device=0,attr=0,flags=0x8000) for e in [2,3,5,6,12,19,32]]+[dict(error=0,handle=n,device=d,attr=a,flags=f) for n,d,a,f in itertools.product([0,5,19,20],[0,128],[0,1],[0x8000,0x8008])]
 for c in cases:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+0x5000,b'config.sav\0');u.mem_write(ds*16+limit,struct.pack('<H',20));u.mem_write(ds*16+table,b'\xa5'*20);u.mem_write(ds*16+errno,b'\x77\x77');u.mem_write(ds*16+rawerr,b'\x66');u.mem_write(ds*16+0xe000,struct.pack('<5H',0,0x600,0x5000,c['flags'],0));state={'done':False,'requests':[]}
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,entry),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  def code(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop()
  def intr(u,n,_):
   ax=u.reg_read(UC_X86_REG_AX);assert n==33;state['requests'].append({'ax':ax,'bx':u.reg_read(UC_X86_REG_BX),'cx':u.reg_read(UC_X86_REG_CX),'dx':u.reg_read(UC_X86_REG_DX)});u.reg_write(UC_X86_REG_EFLAGS,u.reg_read(UC_X86_REG_EFLAGS)&~1)
   if ax==0x3d00:
    u.reg_write(UC_X86_REG_AX,c['error'] or c['handle'])
    if c['error']:u.reg_write(UC_X86_REG_EFLAGS,u.reg_read(UC_X86_REG_EFLAGS)|1)
   elif ax==0x4400:u.reg_write(UC_X86_REG_DX,c['device'])
   elif ax==0x4300:u.reg_write(UC_X86_REG_CX,c['attr'])
   elif ax>>8==0x3e:u.reg_write(UC_X86_REG_AX,0)
   else:raise AssertionError(hex(ax))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+entry,0,count=10000);assert state['done'];ret=u.reg_read(UC_X86_REG_AX);t=bytes(u.mem_read(ds*16+table,20));err=struct.unpack('<H',u.mem_read(ds*16+errno,2))[0];raw=u.mem_read(ds*16+rawerr,1)[0]
  fail=c['error'] or c['handle']>=20;assert ret==(65535 if fail else c['handle']);assert u.reg_read(UC_X86_REG_SP)==0xe004
  if fail:assert t==b'\xa5'*20
  else:
   expected=0x41 if c['device'] else 1|(0x10 if c['attr'] else 0)|(0x20 if c['flags']&8 else 0);tt=bytearray(b'\xa5'*20);tt[c['handle']]=expected;assert t==tt;assert err==0x7777 and raw==0x66
  req=[x['ax']>>8 for x in state['requests']];assert req==([0x3d] if c['error'] else [0x3d,0x44]+([] if c['device'] else [0x43])+([0x3e] if c['handle']>=20 else []))
  if c['handle']>=20 and not c['error']:assert err==24 and raw==0
  out.append(dict(build=v,exe_sha256=hashlib.sha256(b).hexdigest(),fixture=c,ax=ret,errno=err,raw_error=raw,**state,passed=True))
 print(v,len(cases),'passed')
(o/'return_tests.json').write_text(json.dumps({'passed':len(out),'cases':out,'boundary':'Original CRT open and error mapper, no mocked calls; INT21 replies synthetic, limit20 and sentinel descriptor/error fixtures.'},indent=2)+'\n')
