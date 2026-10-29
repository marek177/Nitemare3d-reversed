from pathlib import Path
import json,struct,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;results=[]
cache=json.loads((root/'pass50/evidence/cache.json').read_text())['locations'];xms=json.loads((root/'pass56/evidence/xms.json').read_text())['locations'];spec=json.loads((root/'pass7/evidence/specs.json').read_text())
for c in cache:
 v=c['build'];x=next(x for x in xms if x['build']==v);ds=next(q['actual_DS'] for q in spec if q['build']==v);cs,entry=[int(a,16) for a in c['entry'].split(':')];table=int(c['resource_table'],16);ptrs=int(c['cache_pointers'],16);clock=int(c['clock'],16);scratch=int(x['scratch_segment_global'],16);handle=int(x['source_handle_global'],16);driver=next(r for r in x['wrapper_instructions'] if r['bytes'].startswith('26ff1e'));driveraddr=int(x['wrapper_entry'].split(':')[0],16)*16+int(driver['address'].split(':')[1],16);fatal=next(r for r in x['instructions'] if r['bytes'].startswith('9a'));fataladdr=int(x['entry'].split(':')[0],16)*16+int(fatal['address'].split(':')[1],16)
 b=(root/f'analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+k*4);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 for length,source,(ax,bl),hit in itertools.product([1,1024,1025,8192],[0,-123,-65536,-2147483648],[(1,0),(0,128),(0,127)],[-1,3]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xc000;ident=66;calls=[];fatalstop=[False];offsets=[0x200+j*0x2200 for j in range(4)];snap=[];rounded=(length+1023)//1024*1024;destindex=hit if hit>=0 else 0;dest=offsets[destindex]+6;mag=(-source)&0xffffffff
  u.mem_write(ds*16+table+ident*6,struct.pack('<Hi',length,source));u.mem_write(ds*16+clock,struct.pack('<I',100));u.mem_write(ds*16+scratch,struct.pack('<H',0x5000));u.mem_write(ds*16+handle,struct.pack('<H',0x1234))
  for j,off in enumerate(offsets):
   u.mem_write(ds*16+ptrs+j*4,struct.pack('<HH',off,0x6000));u.mem_write(0x60000+off,struct.pack('<IH',j+10,ident if j==hit else j+1)+bytes([0xa5])*8192);snap.append(bytes(u.mem_read(0x60000+off,8198)))
  def hook(uc,a,n,_):
   if a==driveraddr:
    d=list(struct.unpack('<IHIHI',uc.mem_read(uc.reg_read(UC_X86_REG_DS)*16+uc.reg_read(UC_X86_REG_SI),16)));calls.append(d)
    if ax!=0:
     segment=d[4]>>16;off=d[4]&65535;uc.mem_write(segment*16+off,bytes(((d[2]+i)*17+3)&255 for i in range(d[0])))
    uc.reg_write(UC_X86_REG_AX,ax);uc.reg_write(UC_X86_REG_BL,bl);uc.reg_write(UC_X86_REG_IP,a-uc.reg_read(UC_X86_REG_CS)*16+5)
   elif a==fataladdr:fatalstop[0]=True;uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook)
  for rep in range(2):
   if rep==1:u.mem_write(ds*16+clock,struct.pack("<I",101))
   u.mem_write(ds*16+sp,struct.pack('<3H',0x600,0,ident))
   for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
   u.emu_start(cs*16+entry,0x600,count=3000)
   if fatalstop[0]:break
   assert u.reg_read(UC_X86_REG_AX)==dest and u.reg_read(UC_X86_REG_DX)==0x6000;assert u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  expectedfatal=hit<0 and ax==0 and bl>=128;assert fatalstop[0]==expectedfatal
  assert calls==([] if hit>=0 else [[rounded,0x1234,mag,0,0x60000000+dest]])
  for j,off in enumerate(offsets):
   got=bytes(u.mem_read(0x60000+off,8198))
   if hit>=0 or j!=0 or expectedfatal:assert got==snap[j]
   else:
    assert got[:6]==struct.pack('<IH',100,ident)
    expected=bytes(((mag+i)*17+3)&255 for i in range(rounded)) if ax!=0 else bytes([0xa5])*rounded
    assert got[6:6+rounded]==expected and got[6+rounded:]==bytes([0xa5])*(8192-rounded)
  results.append(dict(build=v,length=length,signed_source=source,source_magnitude=mag,driver_AX=ax,driver_BL=bl,initial_hit=hit,driver_calls=calls,fatal=expectedfatal,returned=None if expectedfatal else [dest,0x6000],second_request_reached=not expectedfatal,passed=True))
(root/'pass57/evidence/chain.json').write_text(json.dumps(dict(cases=len(results),scope='Original cache, original rounded XMS helper and original wrapper. Synthetic XMS driver performs deterministic descriptor-sized copy only for nonzero AX. Fatal handler stopped. No actual manager/asset/audio.',results=results),indent=2));print(len(results),'passed')
