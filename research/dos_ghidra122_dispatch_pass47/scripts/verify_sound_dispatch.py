from pathlib import Path
import csv,json,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
meta=json.loads((root/'pass46/evidence/original_rng.json').read_text())['locations']
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];m=next(x for x in meta if x['build']==v);ds=q['actual_DS'];cs0=int(m['entry'].split(':')[0],16);ui=next(r for r in m['instructions'] if r['bytes'].startswith('e8'));ip=int(ui['address'].split(':')[1],16);ue=(ip+3+int.from_bytes(bytes.fromhex(ui['bytes'])[1:],'little',signed=True))&65535;rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));uii=next(i for i,r in enumerate(rows) if r['address']==f'{cs0:04x}:{ue:04x}');rb=bytes.fromhex(next(r['bytes'] for r in rows[uii:] if r['bytes'].startswith('9a')));cs=int.from_bytes(rb[3:],'little');entry=int.from_bytes(rb[1:3],'little');idx=next(i for i,r in enumerate(rows) if r['address']==f'{cs:04x}:{entry:04x}');body=[]
 for r in rows[idx:]:
  body.append(r)
  if r['bytes']=='cb':break
 enable=int(m['sound_enable'],16);resource=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('83bf')))[2:4],'little');backend=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('803e') and int.from_bytes(bytes.fromhex(r['bytes'])[2:4],'little')!=enable))[2:4],'little');priority=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('3806')))[2:4],'little');volume=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('a0')))[1:3],'little');calls=[r for r in body if r['bytes'].startswith('9a') or r['bytes'].startswith('e8')];roles=['busyA','stopA','busyB','stopB','cache','load','volume','playA','playB'];assert len(calls)==len(roles);sites={cs*16+int(r['address'].split(':')[1],16):(role,r) for role,r in zip(roles,calls)}
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',enable=hex(enable),resource_table=hex(resource),backend=hex(backend),priority=hex(priority),volume=hex(volume),instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 cases=[(1,1,be,bu,cur,inc,pan,vol,cached) for be,bu,(cur,inc),pan,vol,cached in itertools.product([0,1],[0,1],[(0,2),(3,2),(2,2),(3,260)],[0,1,2],[0,70,255],[0,1])]+[(0,1,1,1,3,2,0,70,1),(1,0,1,1,3,2,0,70,1)]
 for en,present,be,bu,cur,inc,pan,vol,cached in cases:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xe000;ident=66;u.mem_write(ds*16+sp,struct.pack('<5H',0x600,0,ident,pan,inc));trace=[]
  for a,n,fmt in [(enable,en,'B'),(resource+ident*6,present,'H'),(backend,be,'B'),(priority,cur,'B'),(volume,vol,'B')]:u.mem_write(ds*16+a,struct.pack('<'+fmt,n))
  def hook(uc,a,size,_):
   if a not in sites:return
   role,r=sites[a];st=uc.reg_read(UC_X86_REG_SP);extra=2 if r['bytes'].startswith('e8') else 0
   n=1 if role in ['cache','load'] else 2 if role in ['volume','playA','playB'] else 0;args=list(struct.unpack('<'+str(n)+'H',uc.mem_read(ds*16+st+extra,n*2))) if n else [];trace.append([role,args])
   if role.startswith('busy'):uc.reg_write(UC_X86_REG_AX,bu)
   elif role=='cache':uc.reg_write(UC_X86_REG_AX,0x200 if cached else 0);uc.reg_write(UC_X86_REG_DX,0x6000 if cached else 0)
   elif role=='load':uc.reg_write(UC_X86_REG_AX,0x200);uc.reg_write(UC_X86_REG_DX,0x6000)
   if extra:uc.reg_write(UC_X86_REG_SP,st+2);uc.reg_write(UC_X86_REG_IP,a-cs*16+3)
   else:uc.reg_write(UC_X86_REG_IP,a-cs*16+5)
  u.hook_add(UC_HOOK_CODE,hook)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  u.emu_start(cs*16+entry,0x600,count=2000);expected=[];accepted=en and present and not(bu and cur>(inc&255))
  if en and present:expected.append(['busyA' if be else 'busyB',[]])
  if accepted:
   if bu:expected.append(['stopA' if be else 'stopB',[]])
   expected.append(['cache',[ident]])
   if not cached:expected.append(['load',[ident]])
   if be:expected.append(['volume',[0 if pan==1 else vol*15//100,0 if pan==2 else vol*15//100]])
   expected.append(['playA' if be else 'playB',[0x200,0x6000]])
  # Volume caller only guarantees low-byte left argument; normalize high byte discarded by backend contract test.
  rawtrace=json.loads(json.dumps(trace))
  for item in trace:
   if item[0]=='volume':item[1]=[x&255 for x in item[1]]
  assert trace==expected,(v,en,present,be,bu,cur,inc,pan,vol,cached,trace,expected);assert u.mem_read(ds*16+priority,1)[0]==((inc&255) if accepted else cur);assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,enabled=en,present=present,backend=be,busy=bu,current_priority=cur,incoming_priority=inc,pan=pan,volume=vol,cached=cached,accepted=bool(accepted),trace=trace,raw_trace=rawtrace,passed=True))
(root/'pass47/evidence/dispatch.json').write_text(json.dumps(dict(cases=len(results),scope='Original enabled dispatcher with backend busy/stop/volume/play and resource cache/loader mocked. Synthetic resource entry. No audio hardware/output.',locations=locations,results=results),indent=2));print(len(results),'passed')
