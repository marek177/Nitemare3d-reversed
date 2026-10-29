from pathlib import Path
import csv,json,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
meta=json.loads((root/'pass47/evidence/dispatch.json').read_text())['locations']
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];m=next(x for x in meta if x['build']==v);ds=q['actual_DS'];calls=[r for r in m['instructions'] if r['bytes'].startswith('9a') or r['bytes'].startswith('e8')];rb=bytes.fromhex(calls[6]['bytes']);cs=int.from_bytes(rb[3:],'little');entry=int.from_bytes(rb[1:3],'little');rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));idx=next(i for i,r in enumerate(rows) if r['address']==f'{cs:04x}:{entry:04x}');body=[]
 for r in rows[idx:]:
  body.append(r)
  if r['bytes']=='cb':break
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 for left,right in itertools.product([0,1,15,38,256,65535],repeat=2):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xf800;events=[];u.mem_write(ds*16+sp,struct.pack('<4H',0x600,0,left,right))
  def intr(uc,n,_):events.append(dict(interrupt=n,ax=uc.reg_read(UC_X86_REG_AX),bx=uc.reg_read(UC_X86_REG_BX),cx=uc.reg_read(UC_X86_REG_CX),dx=uc.reg_read(UC_X86_REG_DX)))
  u.hook_add(UC_HOOK_INTR,intr)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  u.emu_start(cs*16+entry,0x600,count=10000);expected=[dict(interrupt=0x63,ax=0x2100,bx=((left&255)<<4)|(right&255),cx=0,dx=0)];assert events==expected,(v,left,right,events,expected);assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,left=left,right=right,events=events,passed=True))
(root/'pass48/evidence/volume.json').write_text(json.dumps(dict(cases=len(results),scope='Original volume backend wrapper, stack allocation and interrupt marshalling. INT63 boundary hook records registers and leaves them unchanged; actual driver absent.',locations=locations,results=results),indent=2));print(len(results),'passed')
