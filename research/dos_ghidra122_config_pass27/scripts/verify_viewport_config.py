from pathlib import Path
import csv,json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent
meta=json.loads((root/'pass26/evidence/viewport_boundary.json').read_text())['locations']; specs=json.loads((root/'pass7/evidence/specs.json').read_text()); results=[];locations=[]
for q in specs:
 v=q['build'];m=next(x for x in meta if x['build']==v);ds=q['actual_DS'];source=int(m['source_width'],16);cs,se=[int(x,16) for x in m['setter_entry'].split(':')];rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'))
 marker='66c706'+struct.pack('<H',source).hex()+'30010000';i=next(i for i,r in enumerate(rows) if r['bytes']==marker);start=i-1;body=[]
 for r in rows[start:]:
  body.append(r)
  if r['bytes']=='cb':break
 entry=int(body[0]['address'].split(':')[1],16);calls=[r for r in body if r['bytes'].startswith('9a') or r['bytes'].startswith('e8')];assert len(calls) in (6,7)
 roles=(['path'] if len(calls)==7 else [])+['open','length','fatal','read','close','setter'];sites={cs*16+int(r['address'].split(':')[1],16):(role,r) for role,r in zip(roles,calls)}
 dep={cs*16+int(r['address'].split(':')[1],16) for r in m['instructions'] if r['bytes'].startswith('9a')}
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',calls=[dict(role=role,**r) for role,r in zip(roles,calls)],instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 scenarios=[dict(name='open_'+str(handle),handle=handle,length=16,width=0,readcount=16) for handle in [0,65535,32768]]
 scenarios += [dict(name='width_'+str(w),handle=3,length=16,width=w,readcount=16) for w in [0,1,7,8,160,304,320,328,32767,32768,65535]]
 scenarios += [dict(name='short_'+str(n),handle=3,length=16,width=65535,readcount=n) for n in [0,1,2,15]]
 scenarios += [dict(name='badlength_'+str(n),handle=3,length=n,width=304,readcount=16) for n in [0,15,17,65552]]
 for sc in scenarios:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xe000;u.mem_write(ds*16+sp,struct.pack('<HH',0x600,0));trace=[];fatal=[]
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def hook(uc,a,n,_):
   if a in dep:trace.append('setter_dependency');uc.reg_write(UC_X86_REG_IP,a-cs*16+5);return
   if a not in sites:return
   role,r=sites[a];trace.append(role)
   if role=='setter':return
   if role=='fatal':fatal.append(True);uc.emu_stop();return
   if role=='path':uc.reg_write(UC_X86_REG_AX,0x500)
   if role=='open':uc.reg_write(UC_X86_REG_AX,sc['handle'])
   if role=='length':uc.reg_write(UC_X86_REG_AX,sc['length']&65535);uc.reg_write(UC_X86_REG_DX,sc['length']>>16)
   if role=='read':
    st=uc.reg_read(UC_X86_REG_SP);args=struct.unpack('<3H',uc.mem_read(ds*16+st,6));assert args==(3,source,16),args
    payload=struct.pack('<H',sc['width'])+bytes(range(2,16));uc.mem_write(ds*16+source,payload[:sc['readcount']]);uc.reg_write(UC_X86_REG_AX,sc['readcount'])
   if r['bytes'].startswith('e8'):uc.reg_write(UC_X86_REG_SP,uc.reg_read(UC_X86_REG_SP)+2);uc.reg_write(UC_X86_REG_IP,a-cs*16+3)
   else:uc.reg_write(UC_X86_REG_IP,a-cs*16+5)
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+entry,0x600,count=3000)
  expectedfatal=sc['handle']==3 and sc['length']!=16;assert bool(fatal)==expectedfatal
  width=struct.unpack('<H',u.mem_read(ds*16+source,2))[0]
  if not fatal:
   expected=304
   if sc['handle']==3:
    raw=bytearray(struct.pack('<H',304));raw[:min(sc['readcount'],2)]=struct.pack('<H',sc['width'])[:min(sc['readcount'],2)];expected=struct.unpack('<H',raw)[0]
   assert width==expected,(v,sc,width,expected)
   assert trace.count('setter_dependency')==2 and u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,scenario=sc,trace=trace,result_width=width,fatal=bool(fatal),passed=True))
out=root/'pass27/evidence/config.json';out.write_text(json.dumps(dict(cases=len(results),scope='Original settings initializer and original viewport setter; file/path/fatal and setter dependencies mocked. Read mocks write exactly returned byte count. Fatal hook stops before handler.',locations=locations,results=results),indent=2));print(len(results),'passed')
