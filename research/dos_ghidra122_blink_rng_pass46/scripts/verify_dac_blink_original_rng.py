from pathlib import Path
import csv,json,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INSN
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];ds=q['actual_DS'];rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));i=next(i for i,r in enumerate(rows) if r['bytes'].startswith('c706') and r['bytes'].endswith('5000') and rows[i+1]['bytes']=='32c0');start=max(j for j in range(i-30,i) if rows[j]['bytes']=='55' and rows[j+1]['bytes']=='8bec');cs,entry=[int(x,16) for x in rows[start]['address'].split(':')];body=[];nret=0
 for r in rows[start:]:
  body.append(r)
  if r['bytes']=='cb':
   nret+=1
   if nret==2:break
 counter=int.from_bytes(bytes.fromhex(rows[i]['bytes'])[2:4],'little');state=int.from_bytes(bytes.fromhex(rows[i+2]['bytes'])[1:3],'little');level=int.from_bytes(bytes.fromhex(body[2]['bytes'])[2:4],'little');mode=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('833e')))[2:4],'little');other=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('a0')))[1:3],'little');calls=[r for r in body if r['bytes'].startswith('9a') or r['bytes'].startswith('e8')];rngcall=next(r for r in calls if r['bytes'].startswith('9a') and sum(t['bytes']==r['bytes'] for t in calls)==1);ui=[r for r in calls if r['bytes'].startswith('e8')];assert len(ui)==1;sites={cs*16+int(r['address'].split(':')[1],16):kind for kind,r in [('rng',rngcall),('ui',ui[0])]}
 rb=bytes.fromhex(rngcall['bytes']);rcs=int.from_bytes(rb[3:],'little');re=int.from_bytes(rb[1:3],'little');ri=next(i for i,r in enumerate(rows) if r['address']==f'{rcs:04x}:{re:04x}');rb=bytes.fromhex(rows[ri]['bytes']);ccs=int.from_bytes(rb[3:],'little');ce=int.from_bytes(rb[1:3],'little');ci=next(i for i,r in enumerate(rows) if r['address']==f'{ccs:04x}:{ce:04x}');rngbody=[]
 for r in rows[ci:]:
  rngbody.append(r)
  if r['bytes']=='cb':break
 seedaddr=min(int.from_bytes(bytes.fromhex(r['bytes'])[2:4],'little') for r in rngbody if r['bytes'].startswith('ff36'))
 us=ui[0];uiip=int(us['address'].split(':')[1],16);ue=(uiip+3+int.from_bytes(bytes.fromhex(us['bytes'])[1:],'little',signed=True))&65535;uiidx=next(i for i,r in enumerate(rows) if r['address']==f'{cs:04x}:{ue:04x}');soundcall=next(r for r in rows[uiidx:] if r['bytes'].startswith('9a'));sb=bytes.fromhex(soundcall['bytes']);scs=int.from_bytes(sb[3:],'little');se=int.from_bytes(sb[1:3],'little');si=next(i for i,r in enumerate(rows) if r['address']==f'{scs:04x}:{se:04x}');soundflag=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in rows[si:] if r['bytes'].startswith('803e')))[2:4],'little')
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',counter=hex(counter),state=hex(state),mode=hex(mode),level=hex(level),second_index=hex(other),instructions=body,rng_state=hex(seedaddr),rng_instructions=rngbody,sound_enable=hex(soundflag),sha256=hashlib.sha256(b).hexdigest()))
 for md,lv,reset,timer,on,seed in itertools.product([0,2,3],[8,9],[0,1],[0,1],[0,1],[0,239]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xe000;ports=[];deps=[];u.mem_write(ds*16+seedaddr,struct.pack('<I',seed));u.mem_write(ds*16+soundflag,b'\0');newseed=(seed*0x343fd+0x269ec3)&0xffffffff;rv=(newseed>>16)&0x7fff
  for addr,val,fmt in [(mode,md,'H'),(level,lv,'H'),(counter,timer,'H'),(state,on,'B'),(other,17,'B')]:u.mem_write(ds*16+addr,struct.pack('<'+fmt,val))
  u.mem_write(ds*16+sp,struct.pack('<3H',0x600,0,reset))
  def out(uc,port,size,value,_):ports.append([port,size,value])
  def hook(uc,a,size,_):
   if a not in sites:return
   kind=sites[a];deps.append(kind)
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INSN,out,None,1,0,UC_X86_INS_OUT)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  u.emu_start(cs*16+entry,0x600,count=2000);et=timer;eo=on;ed=[];color=None
  if md!=2 and not(md==3 and lv+1<10):
   if reset:et=80;eo=0;color=0;ed=[]
   elif timer:et=timer-1
   elif on:et=160+rv%240;eo=0;color=0;ed=['rng','ui']
   else:et=3;eo=1;color=255
  ep=[]
  if color is not None:
   for index in [235,17]:ep += [[0x3c8,1,index]]+[[0x3c9,1,color]]*3
  assert ports==ep and deps==ed and struct.unpack('<H',u.mem_read(ds*16+counter,2))[0]==et and u.mem_read(ds*16+state,1)[0]==eo,(v,md,lv,reset,timer,on,rv,ports,ep,deps,ed)
  assert struct.unpack('<I',u.mem_read(ds*16+seedaddr,4))[0]==(newseed if 'rng' in ed else seed)
  assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,mode=md,level=lv,reset=reset,timer=timer,state=on,seed=seed,rng=rv,result_timer=et,result_state=eo,ports=ports,dependencies=deps,passed=True))
(root/'pass46/evidence/original_rng.json').write_text(json.dumps(dict(cases=len(results),scope='Original animation, DAC writer, RNG wrapper/CRT generator/multiply and companion wrapper execute with no callee mocks. Sound enabled flag0 exits sound dispatcher; synthetic state, complete audio and scene cadence not executed.',locations=locations,results=results),indent=2));print(len(results),'passed')
