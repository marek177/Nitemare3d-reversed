"""IMAGE INVENTORY DECODER EMULATOR OUT: whole mode0, original six XMS adapters.
Allocator/probes/warning and external INT2F/manager responses are explicit fixtures.
Fatal paths stop at original error entry; do not force error handlers to return.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_INTR
from unicorn.x86_const import *
from cache_init_model import InitModel
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(exist_ok=True)
def save(name,rows):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
root=out.parent;dispatcher=list(csv.DictReader((root/'cache_reset_replay/cache_lifecycle_dispatch_012.csv').open()));old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};allowed=set()
for folder,names in [('cache_reset_replay',['cache_lifecycle_dispatch_012']),('xms_lifecycle_wrappers_replay',['xms_detect_entry','xms_query_capacity','xms_allocate_handle','xms_release_handle','xms_lock_handle','xms_unlock_handle'])]:
 for name in names:
  for row in csv.DictReader((root/folder/(name+'.csv')).open()):
   p=int(row['image_offset']);raw=bytes.fromhex(row['bytes']);assert b[p:p+len(raw)]==raw and old[p]['bytes']==raw.hex();allowed.add(p)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];call_rows=[];write_rows=[];visited=set();caseconfigs=[]
def config(**kw):
 c=dict(probe=257,crt_probe=0xa55a,enabled=1,detect_AL=0x80,capacity=2048,query_error=0,allocate_reply=[1,0,0x4321],lock_reply=[1,0,0x1234],release_reply=[1,0,0x3456],fail_allocation=-1,selector_override=False);c.update(kw)
 if c not in caseconfigs:caseconfigs.append(c)
for probe in (0,69,70,72,73,74,76,77,257,454,455,456,1023,32767,65535):config(probe=probe,enabled=0)
for enabled,detect in itertools.product((1,0x80),(0,1,0x7f,0x80,0x81,0xff)):config(enabled=enabled,detect_AL=detect,capacity=64)
for enabled,capacity in itertools.product((1,0x80),(0,1,63,64,65,2047,2048,2049,32767,32768,65535)):config(enabled=enabled,capacity=capacity)
for enabled,error in itertools.product((1,0x80),(0x7f,0x80,0xff)):config(enabled=enabled,capacity=0,query_error=error)
for enabled,reply in itertools.product((1,0x80),([0,0,0x3456],[0,0x7f,0x3456],[0,0x80,0x3456],[0,0xff,0x3456],[1,0,0],[0xffff,0x80,0xffff])):config(enabled=enabled,allocate_reply=reply)
for enabled,reply in itertools.product((1,0x80),([0,0,0x1234],[0,0x7f,0x1234],[0,0x80,0x1234],[0,0xff,0x1234],[1,0,0],[1,0,0x7fff],[1,0,0x8000],[0xffff,0x80,0xffff])):config(enabled=enabled,lock_reply=reply)
for reply in ([0,0,0x3456],[0,0x80,0x3456],[0,0xff,0x3456]):config(lock_reply=[0,0x80,0x1234],release_reply=reply)
for index in (0,9,10,13,14,75):config(enabled=0,fail_allocation=index)
config(enabled=0,probe=455,fail_allocation=141)
for enabled in (0,1):config(enabled=enabled,selector_override=True)
for load,c in itertools.product((0x824,0x1000),caseconfigs):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 ram=bytearray(0x100000);ram[load*16:load*16+len(raw)]=raw;ds=load+0x2771;base=ds*16;ram[base:base+0x10000]=b'\x66'*0x10000
 for i in range(14):p=0x60000+i*0x2010;ram[p:p+0x2006]=b'\x5a'*0x2006
 for i in range(128):p=0x80000+i*0xc20;ram[p:p+0xc02]=b'\x5a'*0xc02
 def word(a,v):struct.pack_into('<H',ram,base+a,v)
 word(0x2560,load+(0x1c08 if c['selector_override'] else 0x1be7));word(0xc9c,7);word(0x3506,0x5aa5);word(0x3508,0x4567);word(0x350a,0x2468);word(0x350e,0x1234);word(0x3510,0x5678);ram[base+0x3cce]=c['enabled'];ram[base+0x350c]=0x55
 targets={(load+0x11ee)*16+0x2065:'far_allocate',(load+0xfba)*16+0x58:'probe_kib',(load+0x11ee)*16+0x2990:'crt_probe',(load+0x476)*16+0x78:'warning',0x4f100:'manager'}
 for p in targets:ram[p]=0xcb
 fatal=(load+0xfba)*16+0xc;stack=0xf000;lo,hi=base+stack-64,base+stack+8;frame=struct.pack('<3H',0x200,0x4f00,0);ram[base+stack:base+stack+6]=frame
 expected=InitModel(ram,ds,c);expected.run();assert all(not(w['address']<hi and w['address']+w['size']>lo) for w in expected.writes)
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,bytes(ram));observed=[];calls=[];executed=[];stop=[]
 for reg,val in [(UC_X86_REG_CS,load+0x768),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,stack),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 def next_call(name,args):
  index=len(calls);assert index<len(expected.calls),(name,args);want=expected.calls[index];assert (want['name'],want['args'])==(name,args),(want,name,args);calls.append(want);return want
 def hook(e,address,size,data):
  if address==0x4f200:assert expected.fatal is None;stop.append('return');e.emu_stop();return
  if address==fatal:
   sp=e.reg_read(UC_X86_REG_SP);msg=struct.unpack('<H',bytes(e.mem_read(base+sp+4,2)))[0];next_call('fatal',[msg]);assert msg==expected.fatal;stop.append('fatal');e.emu_stop();return
  if address in targets:
   kind=targets[address];args=[];sp=e.reg_read(UC_X86_REG_SP)
   if kind in ('far_allocate','warning'):args=[struct.unpack('<H',bytes(e.mem_read(base+sp+4,2)))[0]]
   if kind=='manager':
    ah=e.reg_read(UC_X86_REG_AH);kind='manager_%02X'%ah
    if ah!=8:args=[e.reg_read(UC_X86_REG_DX)]
   assert e.reg_read(UC_X86_REG_DS)==ds
   want=next_call(kind,args)
   for reg,key in [(UC_X86_REG_AX,'AX'),(UC_X86_REG_DX,'DX'),(UC_X86_REG_BX,'BX')]:e.reg_write(reg,want[key])
   return
  p=address-load*16;assert p in allowed,hex(p);executed.append(p);visited.add(p)
 def intr(e,number,data):
  assert number==0x2f;ax=e.reg_read(UC_X86_REG_AX);want=next_call('detect_%04X'%ax,[])
  if ax==0x4300:e.reg_write(UC_X86_REG_AL,c['detect_AL'])
  else:assert ax==0x4310;e.reg_write(UC_X86_REG_ES,0x4f00);e.reg_write(UC_X86_REG_BX,0x100)
 def write(e,access,address,size,value,data):
  if lo<=address and address+size<=hi:return
  observed.append((address,size,value&((1<<(8*size))-1)))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((load+0x768)*16+0x24,0xfffff,count=20000);assert stop and calls==expected.calls
 actual=bytes(u.mem_read(0,len(ram)));assert actual[:lo]==expected.ram[:lo] and actual[hi:]==expected.ram[hi:],(load,c,[(hex(j),actual[j],expected.ram[j]) for j in range(len(ram)) if not(lo<=j<hi) and actual[j]!=expected.ram[j]][:20]);assert observed==[(w['address'],w['size'],w['value']) for w in expected.writes],(load,c,len(observed),len(expected.writes))
 if stop==['return']:
  for reg,val in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,stack+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)]:assert u.reg_read(reg)==val
  assert bytes(u.mem_read(base+stack,6))==frame
 cid=len(cases)
 for j,x in enumerate(calls):call_rows.append(dict(case=cid,index=j,**{k:json.dumps(v) if isinstance(v,list) else v for k,v in x.items()}))
 for j,x in enumerate(expected.writes):write_rows.append(dict(case=cid,index=j,**x))
 cases.append(dict(case=cid,load=load,**{k:json.dumps(v) if isinstance(v,list) else v for k,v in c.items()},stop=stop[0],fatal_message=expected.fatal,object_count=expected.get(0x3504),final_enabled=expected.get(0x3cce,1),saved_enabled=expected.get(0x350c,1),stored_handle=expected.get(0x3506),stored_limit=expected.get(0x3508),stored_used=expected.get(0x350a),allocator_calls=len(expected.allocations),calls=len(calls),nonstack_writes=len(observed),original_instruction_events=len(executed),whole_RAM_bytes_checked=len(ram)-(hi-lo),status='PASS'))
save('cases',cases);save('dependency_calls',call_rows);save('ordered_writes',write_rows)
prior=root/'xms_lifecycle_wrappers_replay/combined_dispatch_execution.csv';combined=list(csv.DictReader(prior.open()))
for row in combined:
 if int(row['image_offset']) in visited:row['executed']='True'
save('combined_dispatch_execution',combined);remaining=[int(x['image_offset']) for x in combined if x['function']=='cache_lifecycle_dispatch_012' and x['executed']=='False']
files=[image,inventory,image.parent/'relocations.csv',Path(__file__).with_name('cache_init_model.py'),Path(__file__),prior,root/'cache_reset_replay/summary.json',root/'xms_lifecycle_wrappers_replay/summary.json']
s=dict(functions=[],cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,mode0_executed_dispatch_starts=sorted(visited.intersection(int(x['image_offset']) for x in dispatcher)),remaining_unexecuted_dispatch_starts=remaining,stopped_fatal_cases=sum(x['stop']=='fatal' for x in cases),returned_cases=sum(x['stop']=='return' for x in cases),scope='Whole originalmode0+sixoriginalXMSadapters. Farallocator/probes/warning/INT2F/managerresponsesfixtures,no actualDOS/XMSallocation. Fatalentry stops,never forcedreturn. Exact1MiBRAM except72controlstackB andorderednonstackstores,dependencyargs/order,returnedframes/registers checked. Synthetic slot storage above640KiB is not nativecapacity evidence. Existingdispatcher/wrappers reused,no newfunctions.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in files])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k not in ('files','mode0_executed_dispatch_starts')},indent=2))
