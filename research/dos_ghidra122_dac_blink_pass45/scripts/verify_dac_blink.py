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
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',counter=hex(counter),state=hex(state),mode=hex(mode),level=hex(level),second_index=hex(other),instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 for md,lv,reset,timer,on,rv in itertools.product([0,2,3],[8,9],[0,1],[0,1],[0,1],[0,239]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xe000;ports=[];deps=[]
  for addr,val,fmt in [(mode,md,'H'),(level,lv,'H'),(counter,timer,'H'),(state,on,'B'),(other,17,'B')]:u.mem_write(ds*16+addr,struct.pack('<'+fmt,val))
  u.mem_write(ds*16+sp,struct.pack('<3H',0x600,0,reset))
  def out(uc,port,size,value,_):ports.append([port,size,value])
  def hook(uc,a,size,_):
   if a not in sites:return
   kind=sites[a];deps.append(kind)
   if kind=='rng':uc.reg_write(UC_X86_REG_AX,rv);uc.reg_write(UC_X86_REG_IP,a-cs*16+5)
   else:uc.reg_write(UC_X86_REG_SP,uc.reg_read(UC_X86_REG_SP)+2);uc.reg_write(UC_X86_REG_IP,a-cs*16+3)
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
  assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,mode=md,level=lv,reset=reset,timer=timer,state=on,rng=rv,result_timer=et,result_state=eo,ports=ports,dependencies=deps,passed=True))
(root/'pass45/evidence/blink.json').write_text(json.dumps(dict(cases=len(results),scope='Original palette-animation state machine and original DAC writer; RNG return and UI helper mocked. Synthetic state; gameplay trigger meaning unresolved.',locations=locations,results=results),indent=2));print(len(results),'passed')
