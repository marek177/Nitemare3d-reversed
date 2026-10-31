from pathlib import Path
import json,struct,itertools,datetime,hashlib
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass96/evidence';out=[];locations=[]
for l in json.load(open(o/'source_clocks.json')):
 v=l['build'];ds=next(x['actual_DS'] for x in json.load(open(r/'baseline58/pass7/evidence/specs.json')) if x['build']==v);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 far=bytes.fromhex(next(x['bytes'] for x in l['instructions'] if x['bytes'].startswith('9a')));tc=int.from_bytes(far[3:5],'little');ti=int.from_bytes(far[1:3],'little');ins=[]
 for x in Cs(CS_ARCH_X86,CS_MODE_16).disasm(bytes(p[(tc-4096)*16+ti:(tc-4096)*16+ti+0x300]),ti):
  ins.append(x)
  if x.bytes[0]==0xcb:break
 init=next(x for x in ins if x.bytes[0]==0x9a);isg=int.from_bytes(init.bytes[3:5],'little');iip=int.from_bytes(init.bytes[1:3],'little');z=bytes(p[(isg-4096)*16+iip:(isg-4096)*16+iip+5]);assert z[:2]==b'\x83\x3e';initglobal=int.from_bytes(z[2:4],'little');tzglobals=[int.from_bytes(x.bytes[2:4],'little') for x in ins if x.bytes[:2]==b'\xff\x36'][:2];timezone=min(tzglobals);dst=next(int.from_bytes(x.bytes[2:4],'little') for x in ins if x.bytes[:2]==b'\x83\x3e');locations.append(dict(build=v,clock=l['entry'],crt_entry=f'{tc:04x}:{ti:04x}',timezone_init=initglobal,timezone_seconds=timezone,dst_enable=dst,exe_sha256=hashlib.sha256(b).hexdigest(),instructions=[dict(address=f'{tc:04x}:{x.address:04x}',bytes=x.bytes.hex(),text=x.mnemonic+' '+x.op_str) for x in ins]))
 dates=[(1970,1,1,0,0,0),(1994,5,1,12,34,56),(1999,12,31,23,59,59),(2000,2,29,1,2,3),(2026,10,31,7,8,9),(2038,1,19,3,14,7)]
 for date,tz,centi in itertools.product(dates,[0,3600,25200],[0,1,78,99]):
  yy,mo,dd,hh,mi,ss=date;u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+l['flags'][1],b'\0');u.mem_write(ds*16+initglobal,struct.pack('<H',1));u.mem_write(ds*16+timezone,struct.pack('<i',tz));u.mem_write(ds*16+dst,b'\0\0');u.mem_write(ds*16+0xe000,struct.pack('<HH',0,0x600));cs,ip=[int(x,16) for x in l['entry'].split(':')];state={'done':False,'requests':[],'structure':None}
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  def code(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop()
   acs,aip=[int(z,16) for z in l['crt_call'].split(':')]
   if a==acs*16+aip+5:
    ptr=struct.unpack('<H',u.mem_read(ds*16+u.reg_read(UC_X86_REG_SP),2))[0];state['structure']=list(struct.unpack('<I3H',u.mem_read(ds*16+ptr,10)))
  def intr(u,n,_):
   ax=u.reg_read(UC_X86_REG_AX);assert n==33;state['requests'].append(ax>>8)
   if ax>>8==0x2a:u.reg_write(UC_X86_REG_CX,yy);u.reg_write(UC_X86_REG_DX,mo<<8|dd);u.reg_write(UC_X86_REG_AX,0)
   elif ax>>8==0x2c:u.reg_write(UC_X86_REG_CX,hh<<8|mi);u.reg_write(UC_X86_REG_DX,ss<<8|centi)
   else:raise AssertionError((v,n,hex(ax)))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+ip,0,count=100000);epoch=int(datetime.datetime(*date,tzinfo=datetime.timezone.utc).timestamp());expected=((epoch+tz)*1000+centi*10)&0xffffffff;actual=u.reg_read(UC_X86_REG_DX)<<16|u.reg_read(UC_X86_REG_AX);assert state['done'] and actual==expected,(v,date,tz,centi,hex(actual),hex(expected));assert state['requests']==([0x2a,0x2c,0x2a] if hh==mi==0 else [0x2a,0x2c]);assert u.reg_read(UC_X86_REG_SP)==0xe004;assert state['structure']==[(epoch+tz)&0xffffffff,centi*10,tz//60,0]
  out.append(dict(build=v,date=date,timezone_seconds=tz,hundredths=centi,result=actual,**state,passed=True))
 print(v,'72 passed')
(o/'crt_clock_tests.json').write_text(json.dumps(dict(locations=locations,passed=len(out),cases=out,boundary='Original clock and CRT chain unmocked; DOS date/time replies modeled; timezone initialized fixture, DST disabled.'),indent=2)+'\n')
