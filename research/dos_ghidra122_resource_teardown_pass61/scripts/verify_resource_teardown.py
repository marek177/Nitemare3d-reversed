from pathlib import Path
import json,struct,itertools
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR
from unicorn.x86_const import *
root=Path(__file__).resolve().parent.parent;base=root/'baseline58';out=root/'pass61/evidence';out.mkdir(parents=True,exist_ok=True);results=[];locations=[]
life=json.loads((root/'pass60/evidence/lifecycle.json').read_text())['locations'];ini=json.loads((root/'pass59/evidence/init_original_wrappers.json').read_text())['locations']
for line in (out/'seeds.tsv').read_text().splitlines():
 v,role,entrytxt=line.split('\t')
 if role!='loader':continue
 cs,entry=[int(a,16) for a in entrytxt.split(':')];rows=[]
 for l in (out/f'DOS{v}.exe.ghidra.tsv').read_text().splitlines():
  q=l.split('\t')
  if q[0]=='instruction' and q[1]=='loader':rows.append(dict(address=q[2],bytes=q[3],disassembly=q[4]))
 calls=[r for r in rows if r['bytes'].startswith('9a')];assert len(calls)==(5 if v=='10' else 4);f=bytes.fromhex(calls[1]['bytes']);fcs=int.from_bytes(f[3:],'little');fip=int.from_bytes(f[1:3],'little');faddr=fcs*16+fip
 import csv
 old=list(csv.DictReader((base/f'pass7/audit/DOS{v}/instructions.tsv').open(),delimiter='\t'));fi=next(i for i,r in enumerate(old) if r['address']==f'{fcs:04x}:{fip:04x}');freebody=[]
 for r in old[fi:]:
  freebody.append(r)
  if r['bytes']=='cb':break
 heap=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in freebody if r['bytes'].startswith('be')))[1:3],'little')
 counters=[int.from_bytes(bytes.fromhex(r['bytes'])[2:4],'little') for r in rows if r['bytes'].startswith(('393e','833e'))];assert len(counters)==3
 table=[int.from_bytes(bytes.fromhex(r['bytes'])[1:3],'little') for r in rows if r['bytes'].startswith(('be','bf'))];assert table[-1]==10
 faraddr=None;farentry=None
 if v=='10':
  z=bytes.fromhex(calls[2]['bytes']);faraddr=int.from_bytes(z[3:],'little')*16+int.from_bytes(z[1:3],'little');farentry=f"{int.from_bytes(z[3:],'little'):04x}:{int.from_bytes(z[1:3],'little'):04x}"
 classbase=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in rows if r['bytes'].startswith('8b87')))[2:4],'little');objseg=int.from_bytes(bytes.fromhex(next(r['bytes'] for r in rows if r['bytes'].startswith('8e06')))[2:4],'little');ds=next(q['actual_DS'] for q in json.loads((base/'pass7/evidence/specs.json').read_text()) if q['build']==v);lc=next(x for x in life if x['build']==v);im=next(x for x in ini if x['build']==v);rcs,rip=[int(a,16) for a in im['function_entry'].split(':')];resetaddr=rcs*16+rip
 b=(base/f'analysis/inputs/DOS{v}.exe').read_bytes();h=struct.unpack_from('<14H',b);p=bytearray(b[h[4]*16:])
 for k in range(h[3]):
  off,s=struct.unpack_from('<HH',b,h[12]+k*4);z=s*16+off;struct.pack_into('<H',p,z,(struct.unpack_from('<H',p,z)[0]+0x1000)&65535)
 locations.append(dict(second_table_model='nested10_then_array_free' if v=='10' else 'stride8_direct',far_free_entry=farentry,build=v,entry=entrytxt,heap_free=f'{fcs:04x}:{fip:04x}',heap_anchor=hex(heap),count_globals=list(map(hex,counters)),first_table=hex(table[0]),second_table=hex(table[1]),class_pointer_table=hex(classbase),object_segment_global=hex(objseg),heap_free_instructions=freebody))
 for ca,cb,co,active in itertools.product([-1,0,2],[-1,0,2],[-1,0,5],[0,1]):
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x200000);u.mem_write(0x10000,bytes(p));sp=0xc000;trace=[];fartrace=[];events=[];interrupts=[];ids=[2,2,5,3,5];aa=[0x6002 if active else 0,0x6102];bb=([0x6602,0x6702] if v=='10' else [0x6402 if active else 0,0x6502]);classes={2:0x7002,3:0x7202 if active else 0,5:0};ptrs=set(aa+bb+list(classes.values()))-{0}
  for a,n in zip(counters,[ca,cb,co]):u.mem_write(ds*16+a,struct.pack('<H',n&65535))
  for j,ptr in enumerate(aa):u.mem_write(ds*16+table[0]+j*8,struct.pack('<H',ptr))
  for j,ptr in enumerate(bb):
   if v=='10':u.mem_write(ds*16+table[1]+j*8,struct.pack('<H4xH',2 if j==0 else 1,ptr))
   else:u.mem_write(ds*16+table[1]+j*8,struct.pack('<H',ptr))
  fars=[0xc0000202 if active else 0x202,0xc1000202,0xc2000202]
  if v=='10':
   for j,packed in enumerate(fars):
    at=bb[0]+j*10 if j<2 else bb[1];u.mem_write(ds*16+at,bytes([0xa5])*6+struct.pack('<I',packed))
    if packed>>16:u.mem_write((packed>>16)*16+(packed&65535)-2,bytes([0xa0]))
  for cls,ptr in classes.items():u.mem_write(ds*16+classbase+cls*8,struct.pack('<H',ptr))
  for ptr in ptrs:u.mem_write(ds*16+ptr-2,bytes([0xa0,0x5a]))
  u.mem_write(ds*16+heap+6,struct.pack('<HH',0x5000,0xfffe));u.mem_write(ds*16+objseg,struct.pack('<H',0xb000));u.mem_write(ds*16+10,bytes([127]))
  for j,cls in enumerate(ids):u.mem_write(0xb0000+10+j*0x1c,bytes([cls]))
  for j in range(lc['first_slots']):seg=0x7000+j*0x220;u.mem_write(ds*16+int(lc['first_pointer_table'],16)+j*4,struct.pack('<HH',0,seg));u.mem_write(seg*16,struct.pack('<IH',333+j,0))
  for j in range(4):seg=0x9000+j*0x220;u.mem_write(ds*16+int(lc['sound_pointer_table'],16)+j*4,struct.pack('<HH',0,seg));u.mem_write(seg*16,struct.pack('<IH',444+j,66))
  if lc['dynamic_count_global']:u.mem_write(ds*16+int(lc['dynamic_count_global'],16),bytes(2))
  u.mem_write(ds*16+int(im['used'],16),struct.pack('<H',55));seen=set();expected=[]
  basefree=(aa if ca>0 else [])+(bb if cb>0 else [])
  if co>0:
   for cls in ids:
    if classes[cls] and cls not in seen:expected.append(classes[cls]);seen.add(cls)
  expected=basefree+expected+basefree
  def hook(uc,a,n,_):
   if a==resetaddr:
    st=uc.reg_read(UC_X86_REG_SP);mode=struct.unpack('<H',uc.mem_read(ds*16+st+4,2))[0];assert mode==2;events.append(['reset',mode])
   if a==faraddr:st=uc.reg_read(UC_X86_REG_SP);fartrace.append(struct.unpack('<I',uc.mem_read(ds*16+st+4,4))[0]);events.append(['far_free',fartrace[-1]])
   if a==faddr:st=uc.reg_read(UC_X86_REG_SP);trace.append(struct.unpack('<H',uc.mem_read(ds*16+st+4,2))[0]);events.append(['near_free',trace[-1]]);assert struct.unpack('<H',uc.mem_read(ds*16+int(im['used'],16),2))[0]==0
  def intr(uc,n,_):interrupts.append(n);uc.emu_stop()
  u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,intr)
  for rep in range(2):
   u.mem_write(ds*16+sp,struct.pack('<2H',0x600,0))
   for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,sp)]:u.reg_write(reg,val)
   u.emu_start(cs*16+entry,0x600,count=20000);assert not interrupts and u.reg_read(UC_X86_REG_CS)==0 and u.reg_read(UC_X86_REG_SP)==sp+4 and u.reg_read(UC_X86_REG_DS)==ds
  assert sum(e[0]=='reset' for e in events)==2 and events[0]==['reset',2]
  assert fartrace==(fars*2 if v=='10' and cb>0 else [])
  if v=='10':
   for packed in fars:
    if packed>>16:assert u.mem_read((packed>>16)*16+(packed&65535)-2,1)[0]==(0xa1 if cb>0 else 0xa0)
  assert trace==expected,(v,ca,cb,co,active,trace,expected)
  for a,n in zip(counters,[ca,cb,co]):assert struct.unpack('<H',u.mem_read(ds*16+a,2))[0]==(n&65535)
  for cls,ptr in classes.items():assert struct.unpack('<H',u.mem_read(ds*16+classbase+cls*8,2))[0]==(0 if co>0 else ptr)
  for j,ptr in enumerate(aa):assert struct.unpack('<H',u.mem_read(ds*16+table[0]+j*8,2))[0]==ptr
  for j,ptr in enumerate(bb):assert struct.unpack('<H',u.mem_read(ds*16+table[1]+j*8+(6 if v=='10' else 0),2))[0]==ptr
  actualfreed=set(trace)-{0}
  for ptr in ptrs:assert u.mem_read(ds*16+ptr-2,1)[0]==(0xa1 if ptr in actualfreed else 0xa0)
  assert struct.unpack('<H',u.mem_read(ds*16+heap+8,2))[0]==(min(actualfreed)-2 if actualfreed else 0xfffe);assert struct.unpack('<H',u.mem_read(ds*16+int(im['used'],16),2))[0]==0
  results.append(dict(build=v,first_count=ca,second_count=cb,object_count=co,nonnull_variant=active,events=events,heap_free_arguments=trace,far_free_arguments=fartrace,interrupts=interrupts,passed=True))
(out/'teardown.json').write_text(json.dumps(dict(cases=len(results),scope='Original higher-level teardown, original mode2 reset and original near-heap free execute twice. No callee/interrupt mocks; synthetic heap/buffers/records, no full allocator or asset files.',locations=locations,results=results),indent=2));print(len(results),'passed')
