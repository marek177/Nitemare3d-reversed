from pathlib import Path
import json,struct,itertools,hashlib
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass95/evidence';out=[];loc=[]
for l in json.load(open(o/'source_counters.json')):
 v=l['build'];ds=next(x['actual_DS'] for x in json.load(open(r/'baseline58/pass7/evidence/specs.json')) if x['build']==v);cs,counterip=[int(x,16) for x in l['counter'].split(':')];call=l['call'];z=bytes.fromhex(call[3]);ip=(int(call[2].split(':')[1],16)+3+int.from_bytes(z[1:3],'little',signed=True))&65535;b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 ins=list(Cs(CS_ARCH_X86,CS_MODE_16).disasm(bytes(p[(cs-4096)*16+ip:(cs-4096)*16+counterip]),ip));flags=[int.from_bytes(x.bytes[2:4],'little') for x in ins if x.bytes[:2]==b'\x80\x3e'];baseline=next(int.from_bytes(x.bytes[2:4],'little') for x in ins if x.bytes[:2]==b'\x66\xa3');far=next(x for x in ins if x.bytes[0]==0x9a);loc.append(dict(build=v,entry=f'{cs:04x}:{ip:04x}',flags=flags,baseline_global=baseline,crt_call=f'{cs:04x}:{far.address:04x}',exe_sha256=hashlib.sha256(b).hexdigest(),instructions=[dict(address=f'{cs:04x}:{x.address:04x}',bytes=x.bytes.hex(),text=x.mnemonic+' '+x.op_str) for x in ins]))
 for a,mode,base,profile in itertools.product([0,1],[0,1],[0,123,0xffffffff],[(0,1,2),(100,101,99),(0xfffffff0,16,17)]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+flags[0],bytes([a]));u.mem_write(ds*16+flags[1],bytes([mode]));u.mem_write(ds*16+baseline,struct.pack('<I',base));expectedbase=base;trace=[]
  for j,tick in enumerate(profile):
   sec,ms=[(0,0),(1,999),(0xffffffff,65535)][j];u.mem_write(0x46c,struct.pack('<I',tick));u.mem_write(ds*16+0xe000,struct.pack('<HH',0,0x600));state={'done':False,'crt':0}
   for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
   def hook(u,addr,size,_):
    if addr==0x6000:state['done']=True;u.emu_stop();return
    if addr==cs*16+far.address:
     ptr=struct.unpack('<H',u.mem_read(ds*16+u.reg_read(UC_X86_REG_SP),2))[0];u.mem_write(ds*16+ptr,struct.pack('<IH',sec,ms));state['crt']+=1;u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+5)
   hnd=u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+ip,0,count=500);u.hook_del(hnd);bios=a==0 and mode!=0
   if bios:
    if expectedbase==0:expectedbase=tick
    expected=((tick-expectedbase)*55)&0xffffffff
   else:expected=(sec*1000+ms)&0xffffffff
   actual=(u.reg_read(UC_X86_REG_DX)<<16)|u.reg_read(UC_X86_REG_AX);assert state['done'] and actual==expected and state['crt']==int(not bios),(v,a,mode,tick,actual,expected);assert struct.unpack('<I',u.mem_read(ds*16+baseline,4))[0]==expectedbase;assert u.reg_read(UC_X86_REG_SP)==0xe004;trace.append(dict(tick=tick,seconds=sec,subword=ms,result=actual,**state))
  out.append(dict(build=v,flag_a=a,mode=mode,initial_baseline=base,profile=profile,trace=trace,passed=True))
 print(v,'36 sequences passed')
(o/'clock_tests.json').write_text(json.dumps(dict(locations=loc,passed=len(out),native_calls=len(out)*3,cases=out,boundary='Original clock function; BIOS data words modeled, CRT structure producer mocked; no real OS or timing.'),indent=2)+'\n')
