from pathlib import Path
import csv,json,struct,itertools,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;base=root/'baseline58';results=[];locations=[]
(root/'pass60/evidence').mkdir(parents=True,exist_ok=True)
meta=json.loads((root/'pass59/evidence/init_original_wrappers.json').read_text())['locations'];cache=json.loads((base/'pass50/evidence/cache.json').read_text())['locations']
for m in meta:
 v=m['build'];cs,entry=[int(a,16) for a in m['function_entry'].split(':')];rows=[r for r in csv.DictReader((base/f'pass7/audit/DOS{v}/instructions.tsv').open(),delimiter='\t') if r['address'].startswith(f'{cs:04x}:')];store=int(next(x for x in json.loads((base/'evidence/store.json').read_text())['locations'] if x['build']==v)['entry'].split(':')[1],16);body=[r for r in rows if entry<=int(r['address'].split(':')[1],16)<store];bbs=[r for r in body if r['bytes'].startswith('bb') and len(r['bytes'])==6];firstptr=int.from_bytes(bytes.fromhex(bbs[0]['bytes'])[1:],'little');cm=next(x for x in cache if x['build']==v);soundptr=int(cm['cache_pointers'],16);resource=int(cm['resource_table'],16);firstcount=(soundptr-firstptr)//4;dynamic=v!='10';varcount=soundptr+16
 b=(base/f'analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+k*4);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 scratch=None
 if dynamic:
  mov=next(r for r in body if r['bytes'].startswith('b8') and len(r['bytes'])==6 and int.from_bytes(bytes.fromhex(r['bytes'])[1:],'little')>0x1000);ip=int(mov['address'].split(':')[1],16);scratch=struct.unpack_from('<H',p,(cs-0x1000)*16+ip+1)[0]
 drivers={}
 for i,r in enumerate(rows):
  if r['bytes'] not in ['b40a','b40d']:continue
  for q in rows[i+1:]:
   if q['bytes'].startswith('ff1e'):drivers[cs*16+int(q['address'].split(':')[1],16)]=10 if r['bytes']=='b40a' else 13;break
   if q['bytes']=='cb':break
 ds=next(q['actual_DS'] for q in json.loads((base/'pass7/evidence/specs.json').read_text()) if q['build']==v);handle=int(m['handle'],16);hist=int(m['history'],16);used=int(m['used'],16);flag=int(m['enable'],16);cap=int(m['capacity'],16)
 locations.append(dict(build=v,entry=m['function_entry'],first_pointer_table=hex(firstptr),first_slots=firstcount,sound_pointer_table=hex(soundptr),sound_slots=4,dynamic_count_global=hex(varcount) if dynamic else None,dynamic_table_segment=hex(scratch) if dynamic else None,sha256=hashlib.sha256(b).hexdigest()))
 for mode,history,enabled,active,nvar,driverfail in itertools.product([1,2,3],[0,1],[0,1],[0,1],[0,1,3],[0,1]):
  if not dynamic and nvar!=0:continue
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xc000;trace=[];owners=[];blocks=[];varblocks=[]
  for a,n,fmt in [(handle,0x1234,'H'),(hist,history,'B'),(used,55,'H'),(flag,enabled,'B'),(cap,128,'H')]:u.mem_write(ds*16+a,struct.pack('<'+fmt,n))
  resource_before=b''.join(struct.pack('<Hi',1,-j*1024 if j%2 else j*123) for j in range(79));u.mem_write(ds*16+resource,resource_before)
  for j in range(firstcount):
   seg=0x7000+j*0x220;owner=0x6000+j*16;u.mem_write(ds*16+firstptr+j*4,struct.pack('<HH',0,seg));u.mem_write(seg*16,struct.pack('<IH',123+j,owner if active else 0)+bytes([0xa5])*8192);u.mem_write(ds*16+owner,struct.pack('<BBi',17,23,-1024)+struct.pack('<I',(seg<<16)|6)+bytes([0x5a])*6);owners.append((owner,bytes(u.mem_read(ds*16+owner,16))));blocks.append((seg*16,bytes(u.mem_read(seg*16,8198))))
  for j in range(4):
   seg=0x9000+j*0x220;u.mem_write(ds*16+soundptr+j*4,struct.pack('<HH',0,seg));u.mem_write(seg*16,struct.pack('<IH',222+j,66)+bytes([0xa5])*8192);blocks.append((seg*16,bytes(u.mem_read(seg*16,8198))))
  if dynamic:
   u.mem_write(ds*16+varcount,struct.pack('<H',nvar))
   for j in range(nvar):
    seg=0xa000+j*0x100;owner=0x6200+j*16;u.mem_write(scratch*16+j*4,struct.pack('<HH',0,seg));u.mem_write(seg*16,struct.pack('<H',owner if active else 0)+bytes([0xa5])*3072);u.mem_write(ds*16+owner,struct.pack('<BBi',17,23,-1024)+struct.pack('<I',(seg<<16)|2)+bytes([0x5a])*6);owners.append((owner,bytes(u.mem_read(ds*16+owner,16))));varblocks.append((seg*16,bytes(u.mem_read(seg*16,3074))))
  def hook(uc,a,n,_):
   if a not in drivers:return
   ah=uc.reg_read(UC_X86_REG_AH);assert ah==drivers[a];trace.append([ah,uc.reg_read(UC_X86_REG_DX)]);uc.reg_write(UC_X86_REG_AX,0 if driverfail else 1);uc.reg_write(UC_X86_REG_BL,128 if driverfail else 0);uc.reg_write(UC_X86_REG_IP,a-cs*16+4)
  u.hook_add(UC_HOOK_CODE,hook)
  for rep in range(2):
   u.mem_write(ds*16+sp,struct.pack('<3H',0x600,0,mode))
   for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
   u.emu_start(cs*16+entry,0x600,count=10000);assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  assert trace==([[13,0x1234],[10,0x1234]]*2 if mode==1 and history else [])
  assert struct.unpack('<H',u.mem_read(ds*16+used,2))[0]==(0 if mode==2 else 55);assert u.mem_read(ds*16+hist,1)[0]==history;assert struct.unpack('<H',u.mem_read(ds*16+handle,2))[0]==0x1234;assert u.mem_read(ds*16+flag,1)[0]==enabled;assert struct.unpack('<H',u.mem_read(ds*16+cap,2))[0]==128
  assert bytes(u.mem_read(ds*16+resource,len(resource_before)))==resource_before
  for a,old in blocks:
   expected=bytes(6)+old[6:] if mode==2 else old;assert bytes(u.mem_read(a,len(old)))==expected
  for a,old in varblocks:
   expected=bytes(2)+old[2:] if mode==2 else old;assert bytes(u.mem_read(a,len(old)))==expected
  for owner,old in owners:
   expected=bytearray(old)
   if mode==2 and dynamic and active:expected[6:10]=bytes(4)
   assert bytes(u.mem_read(ds*16+owner,16))==bytes(expected),(v,mode,history,active,nvar,hex(owner))
  results.append(dict(build=v,mode=mode,history=history,current_enable=enabled,active_owner=active,dynamic_slots=nvar,driver_failure=driverfail,trace=trace,repetitions=2,passed=True))
(root/'pass60/evidence/lifecycle.json').write_text(json.dumps(dict(cases=len(results),scope='Original mode dispatcher, cache reset and unlock/free wrappers. Indirect XMS driver boundary mocked, synthetic valid buffers/backrefs, each mode invoked twice. No real manager or caller reachability.',locations=locations,results=results),indent=2));print(len(results),'passed')
