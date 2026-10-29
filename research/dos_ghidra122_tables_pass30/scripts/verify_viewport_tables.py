from pathlib import Path
import csv,json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
def s16(x):return (x+32768)%65536-32768
def s32(x):return (x+2147483648)%4294967296-2147483648
def div(a,b):return (abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1)
values=sorted(set(range(0,329,8))|set(range(0,18))|{199,255,319,321,32767,32768,32769,65518,65528,65534,65535})
meta=json.loads((root/'pass26/evidence/viewport_boundary.json').read_text())['locations']
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];m=next(x for x in meta if x['build']==v);ds=q['actual_DS'];source=int(m['source_width'],16);cs,entry=[int(x,16) for x in m['setter_entry'].split(':')];rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));calls=[r for r in m['instructions'] if r['bytes'].startswith('9a')];bcall=bytes.fromhex(calls[0]['bytes']);pcs=int.from_bytes(bcall[3:5],'little');pe=int.from_bytes(bcall[1:3],'little');idx=next(i for i,r in enumerate(rows) if r['address']==f'{pcs:04x}:{pe:04x}');body=[]
 for r in rows[idx:]:
  body.append(r)
  if r['bytes']=='cb':break
 stores=[r for r in body if r['bytes'].startswith('66a3')];assert len(stores)==4;outputs=[int.from_bytes(bytes.fromhex(r['bytes'])[2:4],'little') for r in stores];second=cs*16+int(calls[1]['address'].split(':')[1],16)
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 sb=bytes.fromhex(calls[1]['bytes']);tcs=int.from_bytes(sb[3:5],'little');te=int.from_bytes(sb[1:3],'little');ti=next(i for i,r in enumerate(rows) if r['address']==f'{tcs:04x}:{te:04x}');tb=[]
 for rr in rows[ti:]:
  tb.append(rr)
  if rr['bytes']=='cb':break
 wordbase=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in tb if r['bytes'].startswith('be')))[1:],'little');bybase=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in tb if r['bytes'].startswith('8895')))[2:],'little');end=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in tb if r['bytes'].startswith('81fe')))[2:],'little');count=(end-wordbase)//2;assert count==511
 locations.append(dict(table_entry=f'{tcs:04x}:{te:04x}',word_base=hex(wordbase),high_byte_base=hex(bybase),entries=count,table_instructions=tb,build=v,projection_entry=f'{pcs:04x}:{pe:04x}',output_dwords=[hex(x) for x in outputs],instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 for width in values:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xe000;u.mem_write(ds*16+sp,struct.pack('<HH',0x600,0));u.mem_write(ds*16+source,struct.pack('<H',width));seen=[];fault=[]
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  def hook(uc,a,n,_):
   if a==second:seen.append(a)
  def intr(uc,num,_):fault.append(dict(interrupt=num,cs=uc.reg_read(UC_X86_REG_CS),ip=uc.reg_read(UC_X86_REG_IP)));uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+entry,0x600,count=50000)
  w=s16(width);hh=w>>1;a=div(12000*w,20480);bb=s32(hh*33600);c=s32(bb<<4);expected=[a,bb,c];actual=[s32(struct.unpack('<I',u.mem_read(ds*16+x,4))[0]) for x in outputs]
  assert actual[:3]==expected,(v,width,actual,expected)
  if a==0:assert len(fault)==1 and fault[0]['interrupt']==0 and not seen,(v,width,fault,seen)
  else:
   expected.append(div(c,a));assert actual==expected and not fault and len(seen)==1,(v,width,actual,expected,fault)
   expectedtable=[]
   for j in range(1,count+1):
    delta=max(j-hh,0);numerator=s32(((delta<<6)&65535)<<16);val=div(numerator,j)>>1;expectedtable.append(val&0xffffff)
   words=struct.unpack('<'+str(count)+'H',u.mem_read(ds*16+wordbase,count*2));high=bytes(u.mem_read(ds*16+bybase+1,count));observed=[lo|(hi<<16) for lo,hi in zip(words,high)];assert observed==expectedtable,(v,width,next((j+1,a,b) for j,(a,b) in enumerate(zip(observed,expectedtable)) if a!=b))
   assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,width_bits=width,width_signed=w,height_signed=hh,outputs=actual,expected_completed=expected,divide_fault=fault,table_calls=len(seen),table_entries_verified=(count if a else 0),table_sha256=(hashlib.sha256(struct.pack('<'+str(count)+'I',*observed)).hexdigest() if a else None),passed=True))
(root/'pass30/evidence/tables.json').write_text(json.dumps(dict(cases=len(results),widths_per_build=len(values),scope='Complete original viewport setter and both dependencies, no mocked callees. Divide exception hook stops before DOS handler. All 511 packed 24-bit entries checked on each successful path.',locations=locations,results=results),indent=2));print(len(results),'passed;',sum(bool(r['divide_fault']) for r in results),'divide errors')
