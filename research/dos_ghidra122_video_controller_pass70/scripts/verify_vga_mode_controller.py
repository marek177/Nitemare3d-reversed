from pathlib import Path
import json,struct,hashlib
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass70/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));results=[];locations=[]
for v in ['10','11','12','15','17','18']:
 q=[s.split('\t') for s in (o/f'DOS{v}.exe.ghidra.tsv').read_text().splitlines()];entry=next(s[2] for s in q if s[:2]==['decompile','controller']);cs,ip=[int(x,16) for x in entry.split(':')];rows=[s for s in q if s[:2]==['instruction','controller']];rr=[s for s in q if s[:2]==['instruction','reciprocal']];save=int.from_bytes(bytes.fromhex(next(s[3] for s in rows if s[3].startswith('a2')))[1:3],'little');calls=[s for s in rows if s[3].startswith('e8')];assert len(calls)==2;init=cs*16+int(calls[0][2].split(':')[1],16);fatal=cs*16+int(next(s[2] for s in rows if s[3].startswith('9a')).split(':')[1],16);start=int.from_bytes(bytes.fromhex(next(s[3] for s in rr if s[3].startswith('be')))[1:3],'little');end=int.from_bytes(bytes.fromhex(next(s[3] for s in rr if s[3].startswith('81fe')))[2:4],'little');count=(end-start)//4;assert count==511;ds=next(s['actual_DS'] for s in spec if s['build']==v);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+4*k);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 locations.append(dict(build=v,controller=entry,reciprocal=next(s[2] for s in q if s[:2]==['decompile','reciprocal']),saved_mode=hex(save),table_start=hex(start),table_end_exclusive=hex(end),entries=count,exe_sha256=hashlib.sha256(b).hexdigest()))
 cases=[(0,prev,post) for prev in [0,3,7,19] for post in [19,3]]+[(1,saved,19) for saved in [0,3,7,19]]+[(a,7,19) for a in [2,65535]]
 for action,prev,post in cases:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+save,bytes([prev if action==1 else 0x5a]));u.mem_write(ds*16+start-4,b'\xcc'*(end-start+8));state=dict(events=[],queries=0,done=False,fatal=False)
  def intr(u,n,_):
   assert n==16;ax=u.reg_read(UC_X86_REG_AX);ah=ax>>8
   if ah==15:
    mode=prev if state['queries']==0 else post;state['queries']+=1;state['events'].append(['query',mode]);u.reg_write(UC_X86_REG_AX,0x5000|mode)
   else:assert ah==0 and (ax&255)==prev;state['events'].append(['restore',ax&255])
  def code(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop();return
   if a==init:
    state['events'].append(['init']);assert bytes(u.mem_read(ds*16+save,1))==bytes([prev]);u.reg_write(UC_X86_REG_SP,u.reg_read(UC_X86_REG_SP)+2);u.reg_write(UC_X86_REG_IP,u.reg_read(UC_X86_REG_IP)+3)
   elif a==fatal:
    args=struct.unpack('<2H',u.mem_read(ds*16+u.reg_read(UC_X86_REG_SP),4));assert args[1]==post;state['events'].append(['fatal',post]);state['fatal']=True;u.emu_stop()
  u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_CODE,code)
  def run():
   state['done']=False;u.mem_write(ds*16+0xe000,struct.pack('<HHH',0,0x600,action))
   for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000)]:u.reg_write(reg,val)
   u.emu_start(cs*16+ip,0,count=100000)
  run();assert state['fatal']==(action==0 and post!=19);assert state['done']==(not state['fatal']);expected_table=b''.join(struct.pack('<I',0x400000//n) for n in range(1,512)) if action==0 and post==19 else b'\xcc'*(end-start);assert bytes(u.mem_read(ds*16+start,end-start))==expected_table;assert bytes(u.mem_read(ds*16+start-4,4))==b'\xcc'*4 and bytes(u.mem_read(ds*16+end,4))==b'\xcc'*4
  if action==0:assert state['events']==[['query',prev],['init'],['query',post]]+([['fatal',post]] if post!=19 else []);assert bytes(u.mem_read(ds*16+save,1))==bytes([prev])
  else:
   ev=[['restore',prev]] if action==1 and prev else [];assert state['events']==ev;run();assert state['events']==ev*2;assert bytes(u.mem_read(ds*16+save,1))==bytes([prev if action==1 else 0x5a])
  results.append(dict(build=v,action=action,previous_mode=prev,post_mode=post,events=state['events'],fatal=state['fatal'],table_entries_verified=511 if action==0 and post==19 else 0,passed=True))
 print(v,'14 passed')
(o/'mode_controller_tests.json').write_text(json.dumps(dict(locations=locations,cases=results,passed=len(results),mocks='BIOS INT10 responses; original mode initializer call mocked at call site; fatal stops; original reciprocal initializer executes'),indent=2)+'\n')
