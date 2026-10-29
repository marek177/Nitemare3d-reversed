from pathlib import Path
import json,csv,struct,itertools,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
for x in json.loads((root/'pass56/evidence/xms.json').read_text())['locations']:
 v=x['build'];ds=next(q['actual_DS'] for q in json.loads((root/'pass7/evidence/specs.json').read_text()) if q['build']==v);cs,re=[int(a,16) for a in x['entry'].split(':')];rows=list(csv.DictReader((root/f'pass7/audit/DOS{v}/instructions.tsv').open(),delimiter='\t'));candidates=[i for i,r in enumerate(rows) if r['address'].startswith(f'{cs:04x}:') and int(r['address'].split(':')[1],16)<re and r['bytes']=='c8080000'];i=candidates[-1];entry=int(rows[i]['address'].split(':')[1],16);body=[]
 for r in rows[i:]:
  body.append(r)
  if r['bytes']=='cb' and int(r['address'].split(':')[1],16)>entry+100:break
 capacity=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('3b06')))[2:4],'little');used=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('0306')))[2:4],'little');scratch=int(x['scratch_segment_global'],16);handle=int(x['source_handle_global'],16);desc=int(x['descriptor_offset'],16);driver=next(r for r in x['wrapper_instructions'] if r['bytes'].startswith('26ff1e'));driveraddr=cs*16+int(driver['address'].split(':')[1],16);fatal=next(r for r in body if r['bytes'].startswith('9a'));fataladdr=cs*16+int(fatal['address'].split(':')[1],16)
 b=(root/f'analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+k*4);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 refs=[]
 for j,r in enumerate(rows):
  if r['address'].startswith(f'{cs:04x}:') and r['bytes'].startswith('e8'):
   ip=int(r['address'].split(':')[1],16)
   if (ip+3+int.from_bytes(bytes.fromhex(r['bytes'])[1:],'little',signed=True))&65535==entry:refs.append(j)
 assert len(refs)==2
 prep=next(r['address'] for r in reversed(rows[:refs[-1]]) if r['address'].startswith(f'{cs:04x}:') and r['bytes']=='c8140000')
 locations.append(dict(table_preparer_entry=prep,direct_call_sites=[rows[j]['address'] for j in refs],build=v,entry=f'{cs:04x}:{entry:04x}',capacity_global=hex(capacity),used_global=hex(used),descriptor_offset=hex(desc),instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 for length,(prior,cap),(ax,bl) in itertools.product([0,1,1024,1025,65535],[(0,0),(0,1),(1,1),(1,2),(31,32),(32767,32768),(32768,32769),(65535,0)],[(1,0),(0,128),(0,127)]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xc000;u.mem_write(ds*16+sp,struct.pack('<5H',0x600,0,0x200,0x6000,length))
  for a,n in [(capacity,cap),(used,prior),(scratch,0x5000),(handle,0x1234)]:u.mem_write(ds*16+a,struct.pack('<H',n))
  calls=[];fatalstop=[False]
  def hook(uc,a,n,_):
   if a==driveraddr:
    calls.append(list(struct.unpack('<IHIHI',uc.mem_read(uc.reg_read(UC_X86_REG_DS)*16+uc.reg_read(UC_X86_REG_SI),16))));uc.reg_write(UC_X86_REG_AX,ax);uc.reg_write(UC_X86_REG_BL,bl);uc.reg_write(UC_X86_REG_IP,a-uc.reg_read(UC_X86_REG_CS)*16+5)
   elif a==fataladdr:fatalstop[0]=True;uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook)
  for r,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(r,val)
  u.emu_start(cs*16+entry,0x600,count=2000);blocks=(length+1023)//1024;end=(prior+blocks)&65535;accepted=end<=cap;off=((prior if prior<32768 else prior-65536)*1024)&0xffffffff;isfatal=accepted and ax==0 and bl>=128
  assert fatalstop[0]==isfatal;assert calls==([[blocks*1024,0,0x60000200,0x1234,off]] if accepted else [])
  after=struct.unpack('<H',u.mem_read(ds*16+used,2))[0];assert after==(end if accepted and not isfatal else prior)
  ret=u.reg_read(UC_X86_REG_AX)|(u.reg_read(UC_X86_REG_DX)<<16)
  if not isfatal:
   assert ret==(off if accepted else 0xffffffff);assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  results.append(dict(build=v,length=length,prior_used=prior,capacity=cap,blocks=blocks,driver_AX=ax,driver_BL=bl,accepted=accepted,fatal=isfatal,after_used=after,returned=None if isfatal else ret,driver_descriptors=calls,synthetic_large_counter=prior>=32767,passed=True))
(root/'pass58/evidence/store.json').write_text(json.dumps(dict(cases=len(results),locations=locations,scope='Original rounded XMS store and original XMS wrapper; driver boundary mocked, fatal call stopped. Synthetic capacity/used counters and handle; no real XMS allocation/copy.',results=results),indent=2));print(len(results),'passed')
