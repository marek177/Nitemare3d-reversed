from pathlib import Path
import json,csv,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INSN
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
meta=json.loads((root/'pass43/evidence/loader.json').read_text())['locations'];pal=json.loads((root/'pass42/evidence/palette.json').read_text())['locations']
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];m=next(x for x in meta if x['build']==v);pm=next(x for x in pal if x['build']==v);ds=q['actual_DS'];calls=[r for r in m['instructions'] if r['bytes'].startswith('9a') or r['bytes'].startswith('e8')];rb=bytes.fromhex(calls[5]['bytes']);cs=int.from_bytes(rb[3:],'little');de=int.from_bytes(rb[1:3],'little');rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));di=next(i for i,r in enumerate(rows) if r['address']==f'{cs:04x}:{de:04x}');end=next(i for i in range(di,len(rows)) if rows[i]['bytes']=='cb');idx=end+1;entry=int(rows[idx]['address'].split(':')[1],16);body=[]
 for r in rows[idx:]:
  body.append(r)
  if r['bytes']=='cb':break
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 for index,rgb in itertools.product([0,1,255,256,65535],[(0,0,0),(63,21,42),(255,255,255),(256,257,258),(65535,32768,32767)]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xe000;before={}
  for key,n in [('source_palette',768),('lookup',16),('dirty',1)]:
   a=ds*16+int(pm[key],16);u.mem_write(a,b'\xa5'*n);before[a]=bytes(u.mem_read(a,n))
  ports=[]
  def out(uc,port,size,value,_):ports.append([port,size,value])
  u.hook_add(UC_HOOK_INSN,out,None,1,0,UC_X86_INS_OUT);u.mem_write(ds*16+sp,struct.pack('<6H',0x600,0,index,*rgb))
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  u.emu_start(cs*16+entry,0x600,count=1000);expected=[[0x3c8,1,index&255]]+[[0x3c9,1,x&255] for x in rgb];assert ports==expected;assert all(bytes(u.mem_read(a,len(data)))==data for a,data in before.items());assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,index=index,rgb=rgb,ports=ports,software_palette_unchanged=True,passed=True))
(root/'pass44/evidence/single.json').write_text(json.dumps(dict(cases=len(results),scope='Complete original single-entry DAC writer, no mocks. OUT trace only; no VGA/DAC device.',locations=locations,results=results),indent=2));print(len(results),'passed')
