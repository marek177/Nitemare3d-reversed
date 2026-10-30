from pathlib import Path
import json,struct
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INSN
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass68/evidence';spec=json.load(open(r/'baseline58/pass7/evidence/specs.json'));old=json.load(open(r/'pass67/evidence/glyph_raster_tests.json'))['locations'];results=[];locations=[]
for l in old:
 v=l['build'];ds=next(x['actual_DS'] for x in spec if x['build']==v);zero=int(l['page_zero_global'],16);nonzero=int(l['page_nonzero_global'],16);q=[s.split('\t') for s in (o/f'DOS{v}.exe.xrefs.tsv').read_text().splitlines()];entries=sorted(set(s[3] for s in q if s[0]=='page_zero_global' and s[2]=='READ_WRITE'));assert len(entries)==2;immediate,sync=entries;b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+4*k);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 initial=struct.unpack_from('<H',p,(ds-4096)*16+zero)[0],struct.unpack_from('<H',p,(ds-4096)*16+nonzero)[0];assert initial==(0xa400,0xa000);locations.append(dict(build=v,immediate=immediate,synchronized=sync,page_zero_global=hex(zero),page_nonzero_global=hex(nonzero),initial=list(map(hex,initial))))
 def fixture(entry,z,n,iflag,mode='ok'):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+zero,struct.pack('<H',z));u.mem_write(ds*16+nonzero,struct.pack('<H',n));state=dict(outs=[],ins=[],done=False);values=iter([9,8,0,0,8]*2)
  def inp(u,port,size,_):
   assert port==0x3da and size==1
   val=1 if mode=='wait_first' else 0 if mode=='wait_second' else next(values);state['ins'].append(val);return val
  def out(u,port,size,value,_):
   assert port==0x3d4 and size==2;state['outs'].append(dict(word=value,IF=bool(u.reg_read(UC_X86_REG_EFLAGS)&512),globals=struct.unpack('<H',u.mem_read(ds*16+zero,2))+struct.unpack('<H',u.mem_read(ds*16+nonzero,2))))
  def code(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop()
  u.hook_add(UC_HOOK_INSN,inp,None,1,0,UC_X86_INS_IN);u.hook_add(UC_HOOK_INSN,out,None,1,0,UC_X86_INS_OUT);u.hook_add(UC_HOOK_CODE,code)
  def run():
   state['done']=False;u.mem_write(ds*16+0xe000,struct.pack('<HH',0,0x600));cs,ip=[int(x,16) for x in entry.split(':')]
   for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_IP,ip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000),(UC_X86_REG_EFLAGS,2|512*iflag)]:u.reg_write(reg,val)
   u.emu_start(cs*16+ip,0,count=1000)
  run()
  if mode=='ok':
   assert state['done'];assert bool(u.reg_read(UC_X86_REG_EFLAGS)&512)==(True if entry==sync else bool(iflag));assert state['outs'][0]==dict(word=12|(((z>>8)<<4)&255)<<8,IF=False if entry==sync else bool(iflag),globals=(n,z));run();assert state['done'];assert state['outs'][1]['word']==12|(((n>>8)<<4)&255)<<8;assert state['outs'][1]['globals']==(z,n);assert state['ins']==([9,8,0,0,8]*2 if entry==sync else [])
  else:
   assert not state['done'];assert (len(state['outs'])==0 if mode=='wait_first' else len(state['outs'])==1);assert struct.unpack('<H',u.mem_read(ds*16+zero,2))[0]==n
  return dict(build=v,entry=entry,z=z,n=n,initial_IF=iflag,mode=mode,outs=state['outs'],reads=len(state['ins']),returned=state['done'],passed=True)
 for z,n in [(0xa400,0xa000),(0xa000,0xa400),(0xabcd,0x9001),(0xa000,0xa000)]:
  for iflag in [0,1]:
   for entry in entries:results.append(fixture(entry,z,n,iflag))
 for mode in ['wait_first','wait_second']:results.append(fixture(sync,0xa400,0xa000,0,mode))
 print(v,'18 passed')
(o/'page_flip_tests.json').write_text(json.dumps(dict(locations=locations,cases=results,passed=len(results),boundary='IN values mocked; OUT observed; no hardware VGA timing or scanout'),indent=2)+'\n')
