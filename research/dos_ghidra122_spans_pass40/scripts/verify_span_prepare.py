from pathlib import Path
import csv,json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[];locations=[]
def div(a,b):return abs(a)//abs(b)*(-1 if (a<0)!=(b<0) else 1)
meta=json.loads((root/'pass26/evidence/viewport_boundary.json').read_text())['locations'];prod=json.loads((root/'pass39/evidence/producer.json').read_text())['locations']
patterns=[[],[0]*8,[1]*8,[0,0,1,1,0,2,2,0],[1,2,1,2],[1,1,2,2,1,1],[0,1,0,1,0]]+[[1+(i%2) for i in range(n)] for n in [48,49,50,51]]
for q in json.loads((root/'pass7/evidence/specs.json').read_text()):
 v=q['build'];m=next(x for x in meta if x['build']==v);pr=next(x for x in prod if x['build']==v);ds=q['actual_DS'];cs=int(pr['entry'].split(':')[0],16);rows=list(csv.DictReader((root/'pass7/audit'/('DOS'+v)/'instructions.tsv').open(),delimiter='\t'));idx=next(i for i,r in enumerate(rows) if r['address'].startswith(f'{cs:04x}:') and r['bytes']=='c8080000' and rows[i+3]['bytes']=='33f6');entry=int(rows[idx]['address'].split(':')[1],16);body=[]
 for r in rows[idx:]:
  body.append(r)
  if r['bytes']=='cb':break
 countaddr=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('8936')))[2:],'little');recbase=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('bf')))[1:],'little');ownerbase=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in body if r['bytes'].startswith('05')))[1:],'little');far=[r for r in body if r['bytes'].startswith('9a')];assert len(far)==2;notify,fatal=[cs*16+int(r['address'].split(':')[1],16) for r in far];base=int(m['output_base'],16)
 b=(root/'analysis/inputs'/('DOS'+v+'.exe')).read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+k*4);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(build=v,entry=f'{cs:04x}:{entry:04x}',count=hex(countaddr),records=hex(recbase),ownership=hex(ownerbase),instructions=body,sha256=hashlib.sha256(b).hexdigest()))
 for seq in patterns:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xe000;left=8;right=left+len(seq)-1;u.mem_write(ds*16,b'\0'*32);u.mem_write(ds*16+base+4,struct.pack('<HH',left,right));u.mem_write(ds*16+base+16,struct.pack('<H',1280));u.mem_write(ds*16+recbase,b'\xa5'*(52*18));ptrs=[0,0x6000,0x6040];endpoints={0:(0,0,0,0),1:(0,1792,63,1855),2:(0,2496,63,2433)}
  for owner in [1,2]:u.mem_write(ds*16+ptrs[owner]+20,struct.pack('<4H',*endpoints[owner]))
  for i,owner in enumerate(seq):u.mem_write(ds*16+ownerbase+2*(left+i),struct.pack('<H',ptrs[owner]))
  u.mem_write(ds*16+sp,struct.pack('<HH',0x600,0));notes=[];fault=[]
  def hook(uc,a,size,_):
   if a==notify:
    st=uc.reg_read(UC_X86_REG_SP);notes.append(list(struct.unpack('<2H',uc.mem_read(ds*16+st,4))));uc.reg_write(UC_X86_REG_IP,a-cs*16+5)
   elif a==fatal:fault.append(True);uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
  u.emu_start(cs*16+entry,0x600,count=100000);runs=[];current=0;start=None
  for i,owner in enumerate(seq):
   if owner!=current:
    if start is not None:runs.append((current,start,left+i-1))
    start=left+i;current=owner
  if start is not None:runs.append((current,start,right))
  expectedfatal=len(runs)>=50;assert bool(fault)==expectedfatal,(v,seq,len(runs),fault);count=struct.unpack('<H',u.mem_read(ds*16+countaddr,2))[0];assert count==min(len(runs),50)
  expectednotes=[];cur=0
  for owner in seq:
   if owner!=cur:expectednotes.append([0,ptrs[owner]]);cur=owner
   if len(expectednotes)==50:break
  assert notes==expectednotes
  verified=[]
  if not fault:
   assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
   for k,(owner,l,r) in enumerate(runs):
    x0,y0,x1,y1=endpoints[owner];dx=x1-x0;dy=y1-y0;slope=div(dy<<16,dx) if dx else 0;yl=y0+div((l-x0)*dy,dx) if dx and dy else y0;yr=y0+div((r-x0)*dy,dx) if dx and dy else y1 if dy else y0;acc=((y0-1280)<<16)+(l-x0)*slope if dx and dy else (y0-1280)<<16;expected=struct.pack('<5H2I',ptrs[owner],l,yl&65535,r,yr&65535,slope&0xffffffff,acc&0xffffffff);actual=bytes(u.mem_read(ds*16+recbase+k*18,18));assert actual==expected,(v,seq,k,actual.hex(),expected.hex());verified.append(actual.hex())
   if not runs:
    raw=bytes(u.mem_read(ds*16+recbase,18));assert struct.unpack_from('<H',raw)[0]==0 and struct.unpack_from('<H',raw,2)[0]==0xa5a5 and struct.unpack_from('<H',raw,6)[0]==right
  results.append(dict(build=v,owners=seq,count=count,fatal=bool(fault),notifications=notes,record_hex=verified,passed=True))
(root/'pass40/evidence/spans.json').write_text(json.dumps(dict(cases=len(results),scope='Original span preparer and original interpolation producer; notification call mocked with no side effects, fatal stopped before handler. Synthetic ownership and endpoints.',locations=locations,results=results),indent=2));print(len(results),'passed')
