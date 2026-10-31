from pathlib import Path
import json,struct,itertools
from unicorn import *
from unicorn.x86_const import *
r=Path(__file__).resolve().parent.parent;o=r/'pass104/evidence';out=[]
counters={l['build']:l for l in json.load(open(r/'pass95/evidence/source_counters.json'))};clocks={l['build']:l for l in json.load(open(r/'pass95/evidence/clock_tests.json'))['locations']}
for l in json.load(open(r/'pass101/evidence/irq_locations.json')):
 v=l['build'];ds=l['actual_DS'];ccs,cip=[int(z,16) for z in counters[v]['counter'].split(':')];ics,iip=[int(z,16) for z in l['entry'].split(':')];rows=[s.split('\t') for s in (r/f'pass95/evidence/DOS{v}.prior_helpers.tsv').read_text().splitlines()];rows=[s for s in rows if s[:2]==['instruction','counter']];low=next(int(s[2].split(':')[1],16) for s in rows if s[3].startswith('a1'));high=next(int(s[2].split(':')[1],16) for s in rows if s[3].startswith('8b16'));ret=next(int(s[2].split(':')[1],16) for s in rows if s[3]=='cb')
 b=(r/f'baseline58/analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,seg=struct.unpack_from('<HH',b,h[12]+4*k);z=seg*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+4096)&65535)
 for before,where in itertools.product([0,1,0xfffe,0xffff,0x1234ffff,0x7fffffff,0xfffffffe,0xffffffff],['before_low','between_words','after_high']):
  point=dict(before_low=low,between_words=high,after_high=ret)[where];u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));u.mem_write(ds*16+l['cached'],struct.pack('<I',before));u.mem_write(ds*16+clocks[v]['flags'][1],b'\1');state={'paused':False,'done':False,'ports':[]}
  def code(u,a,size,_):
   if a==0x6000:state['done']=True;u.emu_stop()
   elif a==ccs*16+point and not state['paused']:state['paused']=True;u.emu_stop()
  def inp(u,port,size,_):state['ports'].append(['in',port,size,0x40]);assert port==0x71;return 0x40
  def outp(u,port,size,val,_):state['ports'].append(['out',port,size,val])
  def intr(u,n,_):raise AssertionError(('unexpected interrupt',n))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_INSN,inp,None,1,0,UC_X86_INS_IN);u.hook_add(UC_HOOK_INSN,outp,None,1,0,UC_X86_INS_OUT)
  def entry():
   u.mem_write(ds*16+0xe000,struct.pack('<2H',0,0x600))
   for reg,val in [(UC_X86_REG_CS,ccs),(UC_X86_REG_IP,cip),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xe000),(UC_X86_REG_EFLAGS,0x202)]:u.reg_write(reg,val)
  entry();u.emu_start(ccs*16+cip,0,count=1000);assert state['paused'] and not state['done'];assert u.reg_read(UC_X86_REG_IP)==point
  # Model CPU hardware entry; run original ISR through IRET into interrupted reader.
  saved_flags=u.reg_read(UC_X86_REG_EFLAGS)&0xffff;sp=u.reg_read(UC_X86_REG_SP);u.mem_write(ds*16+sp-6,struct.pack('<3H',point,ccs,saved_flags));u.reg_write(UC_X86_REG_SP,sp-6);u.reg_write(UC_X86_REG_EFLAGS,saved_flags&~0x300);u.reg_write(UC_X86_REG_CS,ics);u.reg_write(UC_X86_REG_IP,iip);u.emu_start(ics*16+iip,0,count=1000)
  after=(before+1)&0xffffffff;result=u.reg_read(UC_X86_REG_DX)<<16|u.reg_read(UC_X86_REG_AX);expected=after if where=='before_low' else before if where=='after_high' else (after&0xffff0000)|(before&0xffff)
  assert state['done'] and result==expected and u.reg_read(UC_X86_REG_SP)==0xe004
  assert struct.unpack('<I',u.mem_read(ds*16+l['cached'],4))[0]==after
  assert state['ports']==[['out',112,1,12],['in',113,1,64],['out',160,1,32],['out',32,1,32]]
  state['done']=False;entry();u.emu_start(ccs*16+cip,0,count=1000);second=u.reg_read(UC_X86_REG_DX)<<16|u.reg_read(UC_X86_REG_AX);assert state['done'] and second==after
  out.append(dict(build=v,where=where,interrupted_at=f'{ccs:04x}:{point:04x}',before=before,after=after,returned=result,next_read=second,torn=result not in [before,after],passed=True))
 print(v,'24 interrupt placements passed',flush=True)
(o/'counter_interrupt_tests.json').write_text(json.dumps(dict(passed=len(out),cases=out,scope='Original reader interrupted by original RTC ISR at controlled instruction boundary; hardware-entry stack/IF/TF and CMOS reply modeled. No function mocks; proves possible interleaving, not observed real DOS occurrence/frequency.'),indent=2)+'\n')
