from pathlib import Path
import json,struct
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass73/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));clip=json.load(open(r/'pass72/evidence/clip_table_tests.json'))['locations'];results=[];locations=[]
def s16(x):return (x&65535)-65536 if x&32768 else x&65535
def s32(x):return (x&0xffffffff)-0x100000000 if x&0x80000000 else x&0xffffffff
def div(a,b):return abs(a)//abs(b)*(-1 if (a<0)!=(b<0) else 1)
for l in clip:
 v=l['build'];q=[s.split('\t') for s in (o/f'DOS{v}.exe.xrefs.tsv').read_text().splitlines()];entry=next(s[3] for s in q if s[0]=='clip_builder');rows=[s for s in q if s[:2]==['instruction',entry]];cs,ip=[int(x,16) for x in entry.split(':')];inputaddr=int.from_bytes(bytes.fromhex(next(s[3] for s in rows if s[3].startswith('a1')))[1:3],'little');stores=[]
 for s in rows:
  z=bytes.fromhex(s[3])
  if z.startswith(b'\xa3'):stores.append(int.from_bytes(z[1:3],'little'))
  elif z.startswith((b'\x89\x1e',b'\x89\x16')):stores.append(int.from_bytes(z[2:4],'little'))
 assert len(stores)==9;calls=[s for s in rows if s[3].startswith('9a')];assert len(calls)==2;cb=bytes.fromhex(calls[0][3]);proj=f'{int.from_bytes(cb[3:5],"little"):04x}:{int.from_bytes(cb[1:3],"little"):04x}';pr=[s for s in q if s[:2]==['instruction',proj]];pstores=[int.from_bytes(bytes.fromhex(s[3])[2:4],'little') for s in pr if s[3].startswith('66a3')];assert len(pstores)==4;ds=next(s['actual_DS'] for s in spec if s['build']==v);bytebase=int(l['byte_table'],16);wordbase=int(l['fraction_table'],16);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 locations.append(dict(build=v,entry=entry,input_width=hex(inputaddr),geometry_globals=list(map(hex,stores)),projection_entry=proj,projection_globals=list(map(hex,pstores)),clip_entry=l['entry']))
 for W in [-2,0,1,2,3,64,159,160,161,319,320,321]:
  H=W>>1;left=s16((320-W)//2);top=left>>1;center=s16(top+(H>>1));geometry=[H,left,W,s16(left+W-1),top,s16(top+H-1),s16(left+H),center,s16(center<<4)];f=div(W*12000,0x5000);a=s32(H*0x8340);b32=s32(a<<4);expected=[f,a,b32]+([div(b32,f)] if f else [])
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+inputaddr,struct.pack('<H',W&65535));u.mem_write(ds*16+bytebase,b'\xcc'*512);u.mem_write(ds*16+wordbase,b'\xcc'*1024)
  for aaddr in pstores:u.mem_write(ds*16+aaddr,b'\xcc'*4)
  u.mem_write(ds*16+0xe000,struct.pack('<HH',0,0x600));state=dict(done=False,trap=None,sequence=[]);pcs,pip=[int(x,16) for x in proj.split(':')];ccs,cip=[int(x,16) for x in l['entry'].split(':')]
  def hook(u,address,size,_):
   if address==0x6000:state['done']=True;u.emu_stop()
   elif address==pcs*16+pip:state['sequence'].append('projection')
   elif address==ccs*16+cip:state['sequence'].append('clip_tables')
  def intr(u,n,_):state['trap']=n;u.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,intr)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  u.emu_start(cs*16+ip,0,count=200000);assert [s16(struct.unpack('<H',u.mem_read(ds*16+aa,2))[0]) for aa in stores]==geometry
  for aa,val in zip(pstores,expected):assert s32(struct.unpack('<I',u.mem_read(ds*16+aa,4))[0])==val
  if not f:
   assert state['trap']==0 and not state['done'] and state['sequence']==['projection'];assert bytes(u.mem_read(ds*16+bytebase,512))==b'\xcc'*512;assert bytes(u.mem_read(ds*16+pstores[3],4))==b'\xcc'*4
  else:
   assert state['trap'] is None and state['done'] and state['sequence']==['projection','clip_tables']
   for n in range(1,512):
    num=s32((((max(n-H,0)&65535)<<6)&65535)<<16);value=div(num,n)>>1;assert u.mem_read(ds*16+bytebase+n,1)[0]==(value>>16)&255;assert struct.unpack('<H',u.mem_read(ds*16+wordbase+n*2,2))[0]==value&65535
  results.append(dict(build=v,width=W,geometry=geometry,projection=expected,**state,passed=True))
 print(v,'12 passed')
(o/'viewport_tests.json').write_text(json.dumps(dict(locations=locations,cases=results,passed=len(results),mocks='none; original setup, projection and clipping builders execute; exceptions observed with Unicorn interrupt hook'),indent=2)+'\n')
