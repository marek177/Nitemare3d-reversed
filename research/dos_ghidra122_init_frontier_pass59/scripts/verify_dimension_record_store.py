from pathlib import Path
import csv,json,struct,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;base=root/'baseline58';results=[];locations=[]
for m in json.loads((base/'evidence/store.json').read_text())['locations']:
 v=m['build'];cs=int(m['entry'].split(':')[0],16);callip=int(m['direct_call_sites'][0].split(':')[1],16);rows=list(csv.DictReader((base/f'pass7/audit/DOS{v}/instructions.tsv').open(),delimiter='\t'));ci=next(i for i,r in enumerate(rows) if r['address']==m['direct_call_sites'][0]);pi=max(i for i in range(ci) if rows[i]['address'].startswith(f'{cs:04x}:') and rows[i]['bytes']=='c8040000');body=[]
 for r in rows[pi:]:
  body.append(r)
  if r['bytes']=='cb' and int(r['address'].split(':')[1],16)>callip+12:break
 entry=int(rows[pi]['address'].split(':')[1],16);x=next(q for q in json.loads((base/'pass56/evidence/xms.json').read_text())['locations'] if q['build']==v);driver=next(r for r in x['wrapper_instructions'] if r['bytes'].startswith('26ff1e'));driveraddr=cs*16+int(driver['address'].split(':')[1],16);ds=next(q['actual_DS'] for q in json.loads((base/'pass7/evidence/specs.json').read_text()) if q['build']==v);cap=int(m['capacity_global'],16);used=int(m['used_global'],16);b=(base/f'analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+k*4);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(length_model='fixed8192' if v=='10' else 'byte_product',build=v,entry=f'{cs:04x}:{entry:04x}',instructions=body))
 for (width,height),prior,capacity in itertools.product([(1,1),(32,32),(255,255),(0,17),(16,64)],[0,1],[0,64]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xc000;record=0x6000;initial=struct.pack('<BBiI',width,height,123,0x60000200);u.mem_write(ds*16+record,initial);u.mem_write(ds*16+sp,struct.pack('<3H',0x600,0,record));trace=[]
  for a,n in [(cap,capacity),(used,prior),(int(x['scratch_segment_global'],16),0x5000),(int(x['source_handle_global'],16),0x1234)]:u.mem_write(ds*16+a,struct.pack('<H',n))
  def hook(uc,a,n,_):
   if a==driveraddr:
    trace.append(list(struct.unpack('<IHIHI',uc.mem_read(uc.reg_read(UC_X86_REG_DS)*16+uc.reg_read(UC_X86_REG_SI),16))));uc.reg_write(UC_X86_REG_AX,1);uc.reg_write(UC_X86_REG_BL,0);uc.reg_write(UC_X86_REG_IP,a-cs*16+5)
  u.hook_add(UC_HOOK_CODE,hook)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  u.emu_start(cs*16+entry,0x600,count=3000);length=8192 if v=='10' else width*height;blocks=(length+1023)//1024;ok=prior+blocks<=capacity;off=prior*1024
  assert trace==([[blocks*1024,0,0x60000200,0x1234,off]] if ok else []),(v,hex(entry),width,height,prior,capacity,trace);got=bytes(u.mem_read(ds*16+record,10));expected=bytearray(initial)
  if ok:struct.pack_into('<i',expected,2,-off)
  assert got==bytes(expected);assert u.reg_read(UC_X86_REG_AL)==int(ok);assert struct.unpack('<H',u.mem_read(ds*16+used,2))[0]==(prior+blocks if ok else prior);assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,width=width,height=height,prior_used=prior,capacity=capacity,accepted=ok,returned_AX=u.reg_read(UC_X86_REG_AX),record_after=got.hex(),trace=trace,passed=True))
(root/'pass59/evidence/dimension_record.json').write_text(json.dumps(dict(cases=len(results),scope='Original dimension-product record helper, original XMS store and move wrapper; indirect driver mocked to success; synthetic record and capacity.',locations=locations,results=results),indent=2));print(len(results),'passed')
