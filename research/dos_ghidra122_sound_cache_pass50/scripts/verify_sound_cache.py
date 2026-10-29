from pathlib import Path
import csv,json,struct,hashlib,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent
out=root/'pass50';(out/'evidence').mkdir(parents=True,exist_ok=True)
results=[];locations=[]
for m in json.loads((root/'pass47/evidence/dispatch.json').read_text())['locations']:
 v=m['build'];ds=next(q['actual_DS'] for q in json.loads((root/'pass7/evidence/specs.json').read_text()) if q['build']==v)
 rows=list(csv.DictReader((root/f'pass7/audit/DOS{v}/instructions.tsv').open(),delimiter='\t'))
 calls=[r for r in m['instructions'] if r['bytes'].startswith(('9a','e8'))];raw=bytes.fromhex(calls[4]['bytes']);cs=int.from_bytes(raw[3:],'little');entry=int.from_bytes(raw[1:3],'little');idx=next(i for i,r in enumerate(rows) if r['address']==f'{cs:04x}:{entry:04x}');body=[]
 for r in rows[idx:]:
  body.append(r)
  if r['bytes']=='cb' and int(r['address'].split(':')[1],16)>=entry+250:break
 def operand(prefix,start):return int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith(prefix)))[start:start+2],'little')
 table=operand('81bf',2);ptrs=operand('bb',1);clock=operand('66a1',2);counters=[int.from_bytes(bytes.fromhex(r['bytes'])[3:5],'little') for r in body if r['bytes'].startswith('66ff06')];io={cs*16+int(r['address'].split(':')[1],16):r for r in body if r['bytes'].startswith(('9a','e8'))}
 b=(root/f'analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',resource_table=hex(table),cache_pointers=hex(ptrs),clock=hex(clock),counters=list(map(hex,counters)),instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 for size,offset,times,hit in itertools.product([0,8192,8193], [123,-123,0],[(10,20,30,40),(40,30,20,10),(100,100,100,100),(20,10,10,30)],[-1,0,3]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));ident=66;sp=0xd000
  u.mem_write(ds*16+sp,struct.pack('<3H',0x600,0,ident));u.mem_write(ds*16+table+ident*6,struct.pack('<Hi',size,offset));u.mem_write(ds*16+clock,struct.pack('<I',100));trace=[]
  for a in counters:u.mem_write(ds*16+a,struct.pack('<I',0))
  for j,t in enumerate(times):
   u.mem_write(ds*16+ptrs+j*4,struct.pack('<HH',0x200+j*0x100,0x6000));u.mem_write(0x60000+0x200+j*0x100,struct.pack('<IH',t,ident if j==hit else j+1))
  def hook(uc,a,n,_):
   if a not in io:return
   r=io[a];st=uc.reg_read(UC_X86_REG_SP);near=r['bytes'].startswith('e8');args=list(struct.unpack('<5H',uc.mem_read(ds*16+st+(2 if near else 0),10)));trace.append(dict(kind='negative_or_zero' if near else 'positive',args=args))
   if near:uc.reg_write(UC_X86_REG_SP,st+2)
   uc.reg_write(UC_X86_REG_IP,a-cs*16+(3 if near else 5))
  u.hook_add(UC_HOOK_CODE,hook)
  for r,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(r,val)
  u.emu_start(cs*16+entry,0x600,count=2000)
  ret=[u.reg_read(UC_X86_REG_AX),u.reg_read(UC_X86_REG_DX)]
  expected_index=hit if hit>=0 else min(range(4),key=lambda j:times[j])
  if size>8192:assert ret==[0,0] and not trace
  else:
   assert ret==[0x206+expected_index*0x100,0x6000],(v,size,offset,times,hit,ret)
   if hit>=0:assert not trace
   else:
    assert len(trace)==1;assert trace[0]['kind']==('positive' if offset>0 else 'negative_or_zero');assert trace[0]['args']==[ret[0],ret[1],abs(offset)&65535,(abs(offset)>>16)&65535,size]
   headers=[list(struct.unpack('<IH',u.mem_read(0x60200+j*0x100,6))) for j in range(4)]
   if hit>=0:assert headers[hit]==[times[hit],ident] # Hits do not refresh age.
   else:assert headers[expected_index]==[100,ident]
  assert [struct.unpack('<I',u.mem_read(ds*16+a,4))[0] for a in counters]==([int(size<=8192 and hit<0 and min(times)>=100),int(size<=8192 and hit<0)]), (v,counters)
  assert u.reg_read(UC_X86_REG_CS)==0
  results.append(dict(build=v,size=size,offset=offset,timestamps=times,hit=hit,returned=ret,io=trace,counters=[struct.unpack('<I',u.mem_read(ds*16+a,4))[0] for a in counters],passed=True))
(out/'evidence/cache.json').write_text(json.dumps(dict(scope='Original cache routine, synthetic four cache blocks; two data-transfer callees mocked. No assets or driver.',locations=locations,cases=len(results),results=results),indent=2));print(len(results),'passed')
