from pathlib import Path
import csv,json,struct,itertools,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];lc=next(x for x in json.loads((root/'pass18/evidence/text_layout.json').read_text())['locations'] if x['build']==v)['calls'][7];cs,site=[int(x,16) for x in lc['address'].split(':')];entry=(site+3+struct.unpack('<h',bytes.fromhex(lc['bytes'])[1:])[0])&65535;b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);i=seg*16+off;struct.pack_into('<H',p,i,(struct.unpack_from('<H',p,i)[0]+0x1000)&65535)
 rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));body=[r for r in rows if r['address'].startswith(f'{cs:04x}:') and entry<=int(r['address'].split(':')[1],16)<entry+0x230];body=body[:next(i for i,r in enumerate(body) if r['bytes']=='cb')+1];calls=[r for r in body if r['bytes'].startswith('9a')];targets=[struct.unpack_from('<HH',bytes.fromhex(r['bytes']),1) for r in calls];parse_target=targets[0];fatal_target=targets[1];assert sum(t==parse_target for t in targets)==6
 kinds={cs*16+int(r['address'].split(':')[1],16):('parse' if t==parse_target else 'fatal' if t==fatal_target else 'effect') for r,t in zip(calls,targets)};locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',calls=calls,exe_sha256=hashlib.sha256(b).hexdigest()))
 numbers={'0':0,'1':1,'-1':65535,'+15':15,'0x10':0,'010':10,'09':9,'0Xf':0,' 12x':12,'':None,'x':None,'+':None,'-':None,'65535':65535,'65536':0,'32768':32768,'-32769':32767}
 tests=[]
 for command,number in itertools.product(['B','C','b','c','o','p'],numbers):
  value=numbers[number]
  if command in ['B','C','b','c'] and number in ['0x10','010','09','0Xf']:value={'0x10':16,'010':8,'09':0,'0Xf':15}[number]
  parsed=0 if value is None else 1;value=0 if value is None else value;value=value if value<32768 else value-65536
  tests.append((('%'+command+number+'%').encode(),command,value,parsed))
 for raw,command,value,parsed in tests:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));ds=q['actual_DS'];sp=0xf800;u.mem_write(0x50200,raw+b'\0'*16);u.mem_write(ds*16+0x9000,b'\x5a');u.mem_write(ds*16+0x9010,b'\xa5'*10);u.mem_write(ds*16+0x9020,struct.pack('<H',10));u.mem_write(ds*16+sp,struct.pack('<7H',0x600,0,0x200,0x5000,0x9000,0x9010,0x9020));state=dict(parse_calls=0,original_conversions=[],effects=[],fatal=False);pending={}
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def hook(uc,a,n,_):
   if a in pending:
    dest=pending[a];state['original_conversions'].append(dict(returned_AX=uc.reg_read(UC_X86_REG_AX),output_word=struct.unpack('<H',uc.mem_read(ds*16+dest,2))[0]));return
   if a not in kinds:return
   kind=kinds[a];stack=ds*16+uc.reg_read(UC_X86_REG_SP)
   if kind=='fatal':state['fatal']=True;uc.emu_stop();return
   if kind=='parse':
    src,fmt,dst=struct.unpack('<3H',uc.mem_read(stack,6));assert bytes(uc.mem_read(ds*16+fmt,3))==(b'%d\0' if command in ['o','p'] else b'%i\0');state['parse_calls']+=1;pending[a+5]=dst;return # Execute original sscanf and all CRT callees.
   else:
    state['effects'].append(dict(site=hex(a),stack_words=list(struct.unpack('<6H',uc.mem_read(stack,12)))));uc.reg_write(UC_X86_REG_AX,0x6d)
   uc.reg_write(UC_X86_REG_IP,a-cs*16+5)
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+entry,0x600,count=20000)
  limit={'b':15,'c':15,'o':255,'p':31}.get(command);numeric_bad=command is not None and (parsed!=1 or limit is not None and value>limit);scanned=raw[1:].split(b'%',1)[0].split(b'\0')[0];fatal=numeric_bad or len(scanned)>=8;assert state['fatal']==fatal,(v,raw,value,parsed,state)
  assert len(state['original_conversions'])==1
  if parsed:assert state['original_conversions'][0]==dict(returned_AX=1,output_word=value&65535)
  else:assert state['original_conversions'][0]['returned_AX']!=1
  color=u.mem_read(ds*16+0x9000,1)[0];bitmap=bytes(u.mem_read(ds*16+0x9016,4));assert bitmap==bytes(4)
  if not fatal:
   expected_color=(value&255) if command=='C' else 0x6d if command in ['c'] or raw==b'%d%' else 0x5a;assert color==expected_color,(v,raw,value,color)
   si=raw.find(b'%',1);si=len(raw) if si<0 else si;result=(u.reg_read(UC_X86_REG_DX)<<16)|u.reg_read(UC_X86_REG_AX);assert result==(0x50000000|(0x200+si));column=struct.unpack('<H',u.mem_read(ds*16+0x9020,2))[0];assert column==12+len(scanned)
   assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
   expected_effects=2 if command=='b' else 1 if command in ['B','c','o','p'] or raw==b'%d%' else 0;assert len(state['effects'])==expected_effects,(v,raw,value,state)
  if not fatal:
   es=[e['stack_words'] for e in state['effects']]
   if command=='B':assert es[0]==[10,5,300,180,value&255,0],(v,command,value,es)
   elif command=='b':assert es[0][:2]==[value&255,0] and es[1]==[10,5,300,180,0x6d,0],(v,command,value,es)
   elif command=='c':assert es[0][0]==value&255
   elif command=='o':assert es[0][:3]==[value&65535,0,0x9010]
   elif command=='p':assert es[0][:2]==[value&65535,0x9010]
   elif raw==b'%d%':assert es[0][0]==8
  results.append(dict(build=v,source_hex=raw.hex(),command=command,expected_signed_value=value,expected_conversion_success=bool(parsed),color_after=color,**state,passed=True))
out=root/'pass20/evidence';out.mkdir(parents=True,exist_ok=True);(out/'bsf_commands_original_scanf.json').write_text(json.dumps(dict(cases=len(results),scope='Original command parser plus original sscanf and CRT callees. Only effect dependencies mocked; fatal handler stopped before execution. No DOS/framebuffer.',locations=locations,results=results),indent=2));print(len(results),'passed')
