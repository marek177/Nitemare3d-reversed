from pathlib import Path
import json,struct
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INSN,UC_HOOK_INTR
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass69/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));results=[];locations=[]
for line in (o/'seeds.tsv').read_text().splitlines():
 v,_,entry=line.split('\t');cs,ip=[int(x,16) for x in entry.split(':')];ds=next(s['actual_DS'] for s in spec if s['build']==v);b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+4*k);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 locations.append(dict(build=v,entry=entry))
 for seed in range(8):
  initial=[(seed*37+i*53)&255 for i in range(5)]
  for iflag in [0,1]:
   u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(0xa0000,b'\xcc'*0x8000);u.mem_write(ds*16+0xe000,struct.pack('<HH',0,0x600));state=dict(events=[],done=False);values=iter(initial)
   def intr(u,n,_):assert n==16 and u.reg_read(UC_X86_REG_AX)==19;state['events'].append(['bios',19])
   def inp(u,port,size,_):assert size==1;value=next(values);state['events'].append(['in',port,size,value]);return value
   def out(u,port,size,value,_):state['events'].append(['out',port,size,value])
   def code(u,a,size,_):
    if a==0x6000:state['done']=True;u.emu_stop()
   u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_INSN,inp,None,1,0,UC_X86_INS_IN);u.hook_add(UC_HOOK_INSN,out,None,1,0,UC_X86_INS_OUT);u.hook_add(UC_HOOK_CODE,code)
   for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000),(UC_X86_REG_EFLAGS,2|1024|512*iflag)]:u.reg_write(reg,val)
   u.emu_start(cs*16+ip,0,count=100000);assert state['done'];expected=[['bios',19]]
   for indexport,index,value,trans in [(0x3c4,4,initial[0],(initial[0]&0xf7)|4),(0x3ce,5,initial[1],initial[1]&0xef),(0x3ce,6,initial[2],initial[2]&0xfd)]:expected.extend([['out',indexport,1,index],['in',indexport+1,1,value],['out',indexport+1,1,trans]])
   expected.extend([['out',0x3c4,2,0xf02]]*2)
   for index,value,trans in [(0x14,initial[3],initial[3]&0xbf),(0x17,initial[4],initial[4]|0x40)]:expected.extend([['out',0x3d4,1,index],['in',0x3d5,1,value],['out',0x3d5,1,trans]])
   assert state['events']==expected,(v,state['events'],expected)
   memory=bytearray([0xcc])*0x8000;memory[:16000]=b'\0'*16000;memory[0x4000:0x4000+16000]=b'\0'*16000;assert bytes(u.mem_read(0xa0000,0x8000))==bytes(memory);assert u.reg_read(UC_X86_REG_DS)==ds;assert u.reg_read(UC_X86_REG_EFLAGS)&1024==0;assert bool(u.reg_read(UC_X86_REG_EFLAGS)&512)==bool(iflag)
   results.append(dict(build=v,seed=seed,initial_register_values=initial,initial_IF=iflag,initial_DF=1,events=state['events'],passed=True))
 print(v,'16 passed')
(o/'mode_init_tests.json').write_text(json.dumps(dict(locations=locations,cases=results,passed=len(results),boundary='BIOS INT10 observed/no-op; five IN values mocked; original clear routine executes on flat mapped CPU memory'),indent=2)+'\n')
