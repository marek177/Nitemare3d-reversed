from pathlib import Path
import json,struct,hashlib
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass85/evidence';results=[]
for m in json.load(open(r/'pass84/evidence/save_tests.json'))['locations']:
 v=m['build'];rows=[x.split('\t') for x in (o/f'DOS{v}.refs.tsv').read_text().splitlines()];xref=next(x for x in rows if x[0]=='save');entry=xref[4];cs,ip=[int(x,16) for x in entry.split(':')];calls=[x for x in rows if x[:2]==['instruction',entry] and x[3].startswith(('e8','9a'))];assert len(calls)==5;sites={cs*16+int(x[2].split(':')[1],16):(i,x) for i,x in enumerate(calls)};ds=next(x['actual_DS'] for x in json.load(open(r/'baseline58/pass7/evidence/specs.json')) if x['build']==v)
 b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 for selection,subresult in [(6,0),(21,0),(22,0),(14,1),(35,1),(14,0),(35,0),(14,256),(14,255),(262,1),(36,1),(0,1)]:
  expected_sub=2 if selection==14 else 3 if selection==35 else None;repeat=selection not in [6,21,22] and not(expected_sub is not None and subresult&255);u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+0xe000,struct.pack('<HH',0,0x600));state={'done':False,'selections':[],'subcalls':[],'saves':0,'renders':0}
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
  def code(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop();return
   q=sites.get(a)
   if q is None:return
   i,x=q;ret=0
   if i==0:state['renders']+=1
   elif i==1:ret=selection if not state['selections'] else 6;state['selections'].append(ret)
   elif i in [2,3]:state['subcalls'].append(i);ret=subresult
   else:state['saves']+=1
   u.reg_write(UC_X86_REG_AX,ret);near=x[3].startswith('e8')
   if near:u.reg_write(UC_X86_REG_SP,u.reg_read(UC_X86_REG_SP)+2)
   u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+(3 if near else 5))
  u.hook_add(UC_HOOK_CODE,code);u.emu_start(cs*16+ip,0,count=10000);assert state['done'] and state['saves']==1;assert state['selections']==([selection,6] if repeat else [selection]);assert state['renders']==len(state['selections']);assert state['subcalls']==([] if expected_sub is None else [expected_sub]);assert u.reg_read(UC_X86_REG_SP)==0xe004
  results.append(dict(build=v,entry=entry,selection=selection,subresult=subresult,exe_sha256=hashlib.sha256(b).hexdigest(),**state,passed=True))
 print(v,'12 passed')
(o/'dispatch_tests.json').write_text(json.dumps(dict(passed=len(results),cases=results,boundary='Original save-caller dispatcher; rendering, selection, subdialogs and save calls mocked. Original save I/O separately tested in84.'),indent=2)+'\n')
