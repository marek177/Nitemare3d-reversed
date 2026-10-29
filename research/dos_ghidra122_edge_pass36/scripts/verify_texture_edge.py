from pathlib import Path
import csv,json,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
def s16(n):return (n+32768)%65536-32768
caller=json.loads((root/'pass33/evidence/caller.json').read_text())['locations']
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];ca=next(x for x in caller if x['build']==v);ds=q['actual_DS'];r=next(r for r in ca['instructions'] if r['bytes'].startswith('e8'));cs,ip=[int(x,16) for x in r['address'].split(':')];entry=(ip+3+int.from_bytes(bytes.fromhex(r['bytes'])[1:],'little',signed=True))&65535;rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));idx=next(i for i,r in enumerate(rows) if r['address']==f'{cs:04x}:{entry:04x}');body=[]
 for r in rows[idx:]:
  body.append(r)
  if r['bytes']=='cb':break
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',instructions=body,sha256=hashlib.sha256(b).hexdigest()));u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xe000;obj=0x6500
 for kind,orient,flags,x,d,width in itertools.product([2,3],range(5),[0,8],[99,100,107,108,112,113,120,121],[-17,-16,-1,0,15,16,17],[0,1,63,64,65]):
  data=bytearray(26);data[5]=flags;data[6]=kind;data[7]=orient
  for off,val in [(12,0),(14,0),(16,16),(18,16),(20,100),(24,120)]:struct.pack_into('<H',data,off,val)
  u.mem_write(ds*16+obj,bytes(data));u.mem_write(ds*16+sp,struct.pack('<6H',0x600,0,obj,x,d&65535,width))
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  u.emu_start(cs*16+entry,0x600,count=1000);ln=s16(x-100)<8;rn=s16(120-x)<8;adjusted=d
  if (ln or rn) and not flags&8 and orient<4:
   special=kind==2 and orient in (0,3)
   if orient in (0,2) and not special:
    if (rn and d>=0) or x==120:adjusted=-1
    elif (ln and -16>d) or x==100:adjusted=-16
   elif orient in (1,3) and not special:
    if (ln and d<0) or x==100:adjusted=0
    elif (rn and 16<=d) or x==120:adjusted=15
   elif orient==0:
    if (rn and d<0) or x==120:adjusted=0
    elif (ln and 16<=d) or x==100:adjusted=15
   else:
    if (ln and d>=0) or x==100:adjusted=-1
    elif (rn and -16>d) or x==120:adjusted=-16
  expected=(width-1)&(adjusted&65535);actual=u.reg_read(UC_X86_REG_AX);assert actual==expected,(v,kind,orient,flags,x,d,width,actual,expected)
  assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,kind=kind,orientation=orient,flags=flags,x=x,input=d,width=width,adjusted=adjusted,result=actual,passed=True))
(root/'pass36/evidence/edge.json').write_text(json.dumps(dict(cases=len(results),scope='Complete original second helper, no callee mocks. Synthetic object record, positive span16 and signed edge inputs; output matches independent branch model.',locations=locations,results=results),indent=2));print(len(results),'passed')
