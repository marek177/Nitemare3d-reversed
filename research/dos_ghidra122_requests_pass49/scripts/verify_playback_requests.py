from pathlib import Path
import csv,json,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
meta=json.loads((root/'pass47/evidence/dispatch.json').read_text())['locations'];roles={0:('busyA',8),1:('stopA',7),2:('busyB',28),3:('stopB',21),7:('playA',6),8:('playB',27)}
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];m=next(x for x in meta if x['build']==v);ds=q['actual_DS'];rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));calls=[r for r in m['instructions'] if r['bytes'].startswith('9a') or r['bytes'].startswith('e8')];b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 for ci,(role,cmd) in roles.items():
  rb=bytes.fromhex(calls[ci]['bytes']);cs=int.from_bytes(rb[3:],'little');entry=int.from_bytes(rb[1:3],'little');idx=next(i for i,r in enumerate(rows) if r['address']==f'{cs:04x}:{entry:04x}');body=[]
  for r in rows[idx:]:
   body.append(r)
   if r['bytes']=='cb':break
  locations.append(dict(build=v,role=role,command=cmd,entry=f'{cs:04x}:{entry:04x}',instructions=body,sha256=hashlib.sha256(b).hexdigest()))
  for (off,seg),fill,ret in itertools.product([(0,0),(0,0x6000),(0x200,0x6000)],[0,165],[0,1,65535]):
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xf800;u.mem_write(ds*16+sp-0x100,bytes([fill])*0x120);u.mem_write(ds*16+sp,struct.pack('<4H',0x600,0,off,seg));events=[]
   def intr(uc,n,_):
    events.append(dict(interrupt=n,**{name:uc.reg_read(reg) for name,reg in [('ax',UC_X86_REG_AX),('bx',UC_X86_REG_BX),('cx',UC_X86_REG_CX),('dx',UC_X86_REG_DX),('si',UC_X86_REG_SI),('di',UC_X86_REG_DI)]}))
    for reg,val in [(UC_X86_REG_AX,ret),(UC_X86_REG_BX,0x1234),(UC_X86_REG_DX,0x5678),(UC_X86_REG_DI,0x9abc)]:uc.reg_write(reg,val)
   u.hook_add(UC_HOOK_INTR,intr)
   for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
   u.emu_start(cs*16+entry,0x600,count=10000);isplay=role.startswith('play');null=isplay and off==0 and seg==0
   if null:assert not events and u.reg_read(UC_X86_REG_AX)==65535
   else:
    assert len(events)==1;ev=events[0];assert (ev['interrupt'],ev['ax'],ev['bx'],ev['dx'],ev['di'])==(99,cmd<<8,0,seg if isplay else 0,off if isplay else 0),(v,role,events);assert u.reg_read(UC_X86_REG_AX)==ret
    # Generic wrapper does not initialize input CX/SI: preserved stack fill reaches driver.
    assert ev['cx']==fill*257 and ev['si']==fill*257,(v,role,events,fill)
   assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
   results.append(dict(build=v,role=role,pointer=[off,seg],stack_fill=fill,driver_ax=ret,returned_ax=u.reg_read(UC_X86_REG_AX),events=events,passed=True))
(root/'pass49/evidence/requests.json').write_text(json.dumps(dict(cases=len(results),scope='Original six backend wrappers, generic request and CRT interrupt marshalling; driver INT63 hook injects return registers. No real driver/audio.',locations=locations,results=results),indent=2));print(len(results),'passed')
