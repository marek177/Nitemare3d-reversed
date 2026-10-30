from pathlib import Path
import json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass72/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));results=[];locations=[]
def signed(x,b):return x-(1<<b) if x&(1<<(b-1)) else x
def truncdiv(a,b):return (abs(a)//b)*(-1 if a<0 else 1)
for v in ['10','11','12','15','17','18']:
 q=[s.split('\t') for s in (o/f'DOS{v}.exe.xrefs.tsv').read_text().splitlines()];entry=next(s[3] for s in q if s[0]=='at');cs,ip=[int(x,16) for x in entry.split(':')];rows=[s for s in q if s[0]=='instruction'];height=int.from_bytes(bytes.fromhex(next(s[3] for s in rows if s[3].startswith('a1')))[1:3],'little');wordfirst=int.from_bytes(bytes.fromhex(next(s[3] for s in rows if s[3].startswith('be')))[1:3],'little');bytebase=int.from_bytes(bytes.fromhex(next(s[3] for s in rows if s[3].startswith('8895')))[2:4],'little');end=int.from_bytes(bytes.fromhex(next(s[3] for s in rows if s[3].startswith('81fe')))[2:4],'little');assert (end-wordfirst)//2==511;wordbase=wordfirst-2;ds=next(s['actual_DS'] for s in spec if s['build']==v);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+4*k);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 locations.append(dict(build=v,entry=entry,height_global=hex(height),byte_table=hex(bytebase),fraction_table=hex(wordbase),entries=511,exe_sha256=hashlib.sha256(b).hexdigest()))
 for H in [-32768,-1,0,1,64,100,200,511,512,32767]:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+height,struct.pack('<H',H&65535));u.mem_write(ds*16+bytebase-1,b'\xcc'*514);u.mem_write(ds*16+wordbase-2,b'\xcc'*1028);u.mem_write(ds*16+0xe000,struct.pack('<HH',0,0x600));state={'done':False}
  def hook(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  u.emu_start(cs*16+ip,0,count=100000);assert state['done'];bb=bytearray([0xcc])*512;ww=bytearray([0xcc])*1024;normal_differences=0
  for n in range(1,512):
   delta=max(n-H,0);num=signed((((delta&65535)<<6)&65535)<<16,32);value=truncdiv(num,n)>>1;bb[n]=(value>>16)&255;struct.pack_into('<H',ww,n*2,value&65535)
   if 0<=H<=511:assert value==((max(n-H,0)*64*65536)//n)//2
   step=0x400000//n;alternative=(max(n-H,0)*step)//2
   normal_differences+=value!=alternative
  assert bytes(u.mem_read(ds*16+bytebase,512))==bytes(bb);assert bytes(u.mem_read(ds*16+wordbase,1024))==bytes(ww);assert bytes(u.mem_read(ds*16+bytebase-1,1))==b'\xcc';assert bytes(u.mem_read(ds*16+bytebase+512,1))==b'\xcc';assert bytes(u.mem_read(ds*16+wordbase+1024,2))==b'\xcc'*2
  results.append(dict(build=v,height=H,entries_verified=511,differences_from_reciprocal_product=normal_differences,byte_sha256=hashlib.sha256(bb).hexdigest(),fraction_sha256=hashlib.sha256(ww).hexdigest(),passed=True))
 print(v,'10 passed')
(o/'clip_table_tests.json').write_text(json.dumps(dict(locations=locations,cases=results,passed=len(results),mocks='none; synthetic height and table memory, original routine executes unchanged'),indent=2)+'\n')
