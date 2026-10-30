from pathlib import Path
import json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass65/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));results=[];locations=[]
for v in ['10','11','12','15','17','18']:
 lines=[s.split('\t') for s in (o/f'DOS{v}.exe.xrefs.tsv').read_text().splitlines()];ref=next(q for q in lines if q[0]=='raw_loader');entry=ref[3];cs,ip=[int(x,16) for x in entry.split(':')];rows=[q for q in lines if q[0]=='instruction'];raw=cs*16+int(ref[1].split(':')[1],16)
 def imm(prefix,start=2):return int.from_bytes(bytes.fromhex(next(q[3] for q in rows if q[3].startswith(prefix)))[start:start+2],'little')
 current=imm('881e');gate=imm('38bf');table=imm('898f');seg=imm('68',1);segptr=imm('8e06');ds=next(s['actual_DS'] for s in spec if s['build']==v)
 calls=[q for q in rows if q[3].startswith('9a')];assert len(calls)==2;hb=bytes.fromhex(calls[1][3]);helper=f'{int.from_bytes(hb[3:5],"little"):04x}:{int.from_bytes(hb[1:3],"little"):04x}'
 b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+4*k);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 locations.append(dict(build=v,entry=entry,current=hex(current),gate=hex(gate),pointer_table=hex(table),data_segment=hex(seg),segment_global=hex(segptr),bit_reverse_helper=helper,exe_sha256=hashlib.sha256(b).hexdigest()))
 for arg in [0,1,2,0x101]:
  for cached in [False,True]:
   bank=arg&255;start=bank*1200;payload=bytearray([0xa5,0x5a]);expected=bytearray(payload);ptrs=[start]
   for j in range(1,128):
    a,bw=[(0,9),(1,1),(2,8),(2,9),(3,16)][j%5];n=a*((bw+7)//8);dat=bytes((j*17+k*31)&255 for k in range(n));ptrs.append(start+len(payload));payload.extend(bytes([a,bw])+dat);expected.extend(bytes([a,bw])+bytes(int(f'{x:08b}'[::-1],2) for x in dat))
   assert len(payload)<1200
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+segptr,struct.pack('<H',seg));u.mem_write(ds*16+gate+bank,bytes([1 if cached else 0]));u.mem_write(seg*16+start,bytes(payload));u.mem_write(ds*16+table+bank*512,b'\xcc'*512);state=dict(loads=0,returned=False)
   def hook(u,a,size,_):
    if a==0x6000:state['returned']=True;u.emu_stop();return
    if a!=raw:return
    sp=u.reg_read(UC_X86_REG_SP);args=struct.unpack('<3H',u.mem_read(ds*16+sp,6));assert args==(arg,start,seg),args;assert bytes(u.mem_read(ds*16+gate+bank,1))==b'\1';state['loads']+=1;u.mem_write(seg*16+start,bytes(payload));u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+5)
   u.hook_add(UC_HOOK_CODE,hook)
   def run():
    state['returned']=False;u.mem_write(ds*16+0xe000,struct.pack('<HHH',0,0x600,arg))
    for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
    u.emu_start(cs*16+ip,0,count=1000000);assert state['returned']
   run();assert bytes(u.mem_read(ds*16+current,1))==bytes([bank]);assert state['loads']==(0 if cached else 1)
   if not cached:
    assert bytes(u.mem_read(seg*16+start,len(payload)))==bytes(expected)
    got=struct.unpack('<256H',u.mem_read(ds*16+table+bank*512,512));assert list(got[::2])==ptrs and set(got[1::2])=={seg}
   else:assert bytes(u.mem_read(ds*16+table+bank*512,512))==b'\xcc'*512
   snapshot=bytes(u.mem_read(seg*16+start,len(payload)));run();assert bytes(u.mem_read(seg*16+start,len(payload)))==snapshot and state['loads']==(0 if cached else 1)
   results.append(dict(build=v,arg=arg,bank=bank,cached=cached,record_count=128,loads=state['loads'],passed=True))
 print(v,'8 passed')
(o/'bitmap_bank_tests.json').write_text(json.dumps(dict(locations=locations,cases=results,passed=len(results)),indent=2)+'\n')
