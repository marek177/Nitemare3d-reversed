from pathlib import Path
import json,struct,hashlib
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass86/evidence';out=[];loc=[];mapping={10:(4,8),11:(5,11),12:(7,10),13:(6,9)}
for meta in json.load(open(r/'pass86/evidence/input_locations.json')):
 v=meta['build'];ds=next(x['actual_DS'] for x in json.load(open(r/'baseline58/pass7/evidence/specs.json')) if x['build']==v);entry=meta['commit_entry'];cs,ip=[int(x,16) for x in entry.split(':')];b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 code=bytes(p[(cs-4096)*16+ip:(cs-4096)*16+ip+0x180]);ins=[]
 for x in Cs(CS_ARCH_X86,CS_MODE_16).disasm(code,ip):
  ins.append(x)
  if x.bytes[0]==0xcb:break
 assert ins[-1].bytes[0]==0xcb
 sg=next(int.from_bytes(x.bytes[2:4],'little') for x in ins if x.bytes[:2]==b'\x8e\x06');calls={cs*16+x.address:x for x in ins if x.bytes[0] in [0x9a,0xe8]};loc.append(dict(build=v,entry=entry,record_segment_global=sg,instructions=[dict(address=f'{cs:04x}:{x.address:04x}',bytes=x.bytes.hex(),text=x.mnemonic+' '+x.op_str) for x in ins]))
 cases=[(rid,n) for rid in mapping for n in [-32768,-32767,-257,-256,-255,-1,0,1,255,256,257,32767]]+[(0,0),(99,123)]
 for rid,n,old_enabled in [(a,b,c) for a,b in cases for c in [0,1]]:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+sg,struct.pack('<H',0x5000));u.mem_write(0x50000+0x1212,bytes([rid,0])+struct.pack('<h',n)+bytes(0x12-4)+b'\0');initial=bytes([0x30,1,0x77,0x66,17,18,19,20,0,0,0,0,0x55,0x44,0x33,0x22]);initial=initial[:9]+bytes([old_enabled])+initial[10:];u.mem_write(ds*16+meta['config'],initial);u.mem_write(ds*16+0xe000,struct.pack('<HH',0,0x600));state={'done':False,'calls':[]}
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  def hook(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop();return
   x=calls.get(a)
   if x is None:return
   state['calls'].append(dict(site=f'{cs:04x}:{x.address:04x}',config=bytes(u.mem_read(ds*16+meta['config'],16)).hex(),args=bytes(u.mem_read(ds*16+u.reg_read(UC_X86_REG_SP),8)).hex()));u.reg_write(UC_X86_REG_AX,0)
   if x.bytes[0]==0xe8:u.reg_write(UC_X86_REG_SP,u.reg_read(UC_X86_REG_SP)+2)
   u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+len(x.bytes))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+ip,0,count=10000);expected=bytearray(initial)
  if rid in mapping:mag,en=mapping[rid];expected[mag]=abs(n)&255;expected[en]=int(n>0)
  assert state['done'] and bytes(u.mem_read(ds*16+meta['config'],16))==expected,(v,rid,n,state);assert u.reg_read(UC_X86_REG_SP)==0xe004 and u.reg_read(UC_X86_REG_DS)==ds
  expected_calls=([0] if expected[9]==0 and initial[9]!=0 else [])+([1] if expected[7]!=initial[7] else [])+[2,3]+([4] if expected[9]!=0 and initial[9]==0 else [])
  ordered=list(calls);actual=[ordered.index(int(c['site'].split(':')[0],16)*16+int(c['site'].split(':')[1],16)) for c in state['calls']];assert actual==expected_calls,(v,rid,n,actual,expected_calls)
  for i,c in zip(actual,state['calls']):assert c['config']==(initial if i<2 else expected).hex()
  out.append(dict(build=v,old_enabled=old_enabled,record_id=rid,value=n,result=expected.hex(),exe_sha256=hashlib.sha256(b).hexdigest(),**state,passed=True))
 print(v,len(cases)*2,'passed')
(o/'commit_tests.json').write_text(json.dumps(dict(locations=loc,passed=len(out),cases=out,boundary='Original staged copy/record conversion/commit; all side-effect callees mocked; synthetic record segment, DS=SS DF0.'),indent=2)+'\n')
