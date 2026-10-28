from pathlib import Path
import json,struct,csv,itertools,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];loc=next(x for x in json.loads((root/'pass10/evidence/checksum_open_locations.json').read_text()) if x['build']==v)
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 cs,site=[int(x,16) for x in loc['lowopen_callsite'].split(':')];raw=p[cs*16-0x10000+site:cs*16-0x10000+site+5];assert raw[0]==0x9a;entry=struct.unpack_from('<H',raw,1)[0];assert struct.unpack_from('<H',raw,3)[0]==cs
 rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));body=[r for r in rows if r['address'].startswith(f'{cs:04x}:') and entry<=int(r['address'].split(':')[1],16)<entry+0x50]
 test=next(bytes.fromhex(r['bytes']) for r in body if r['bytes'].startswith('f606'));defaultaddr=struct.unpack_from('<H',test,2)[0];maxaddr=int(loc['maxhandle_address'],16);ds=q['actual_DS'];sp=0xe000
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',default_mode_address=hex(defaultaddr),maxhandle_address=hex(maxaddr),exe_sha256=hashlib.sha256(b).hexdigest()))
 for flags,default,readonly,device,err,handle in itertools.product([0,0x4000,0x8000],[0,0x80],[0,1],[False,True],[0,2,5],[5,25]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+sp,struct.pack('<6H',0x600,0,0x9100,flags,0,0x1a4));u.mem_write(ds*16+defaultaddr,bytes([default]));u.mem_write(ds*16+maxaddr,struct.pack('<H',20));u.mem_write(ds*16+maxaddr+2+handle,b'\x55')
  for r,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(r,val)
  trace=[]
  def intr(uc,n,_):
   ax=uc.reg_read(UC_X86_REG_AX);assert n==0x21;trace.append(hex(ax));carry=0
   if ax==0x3d00:uc.reg_write(UC_X86_REG_AX,err if err else handle);carry=bool(err);assert uc.reg_read(UC_X86_REG_DX)==0x9100
   elif ax==0x4400:uc.reg_write(UC_X86_REG_DX,0x80 if device else 0);assert uc.reg_read(UC_X86_REG_BX)==handle
   elif ax==0x4300:uc.reg_write(UC_X86_REG_CX,readonly)
   elif ax>>8==0x3e:assert uc.reg_read(UC_X86_REG_BX)==handle;uc.reg_write(UC_X86_REG_AX,0)
   else:raise AssertionError((v,hex(ax)))
   uc.reg_write(UC_X86_REG_EFLAGS,(uc.reg_read(UC_X86_REG_EFLAGS)&~1)|int(carry))
  u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+entry,0x600,count=20000)
  ax=u.reg_read(UC_X86_REG_AX);value=u.mem_read(ds*16+maxaddr+2+handle,1)[0]
  assert ax==(65535 if err or handle>=20 else handle),(v,flags,trace,ax)
  if err or handle>=20:assert value==0x55
  else:
   text=(flags&0x8000)==0 and ((flags&0x4000)!=0 or not default&0x80);expected=1|(0x80 if text else 0)|(0x40 if device else 0)|(0x10 if readonly and not device else 0);assert value==expected,(v,flags,value,expected)
  assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4
  results.append(dict(build=v,flags=hex(flags),default_mode=hex(default),readonly=readonly,device=device,open_error=err,handle=handle,returned_AX=ax,handle_flags=value,trace=trace,passed=True))
out=root/'pass11/evidence';out.mkdir(parents=True,exist_ok=True);(out/'lowopen_matrix.json').write_text(json.dumps(dict(cases=len(results),scope='Complete original CRT low-level open, only DOS INT21 interface mocked. No game/OS startup.',locations=locations,results=results),indent=2));print(len(results),'passed')
