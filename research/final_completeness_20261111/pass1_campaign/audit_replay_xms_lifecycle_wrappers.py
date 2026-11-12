"""IMAGE INVENTORY DECODER EMULATOR OUT: original XMS wrappers and whole shutdown.
Only INT2F responses and external manager RETF are fixtures; no XMS memory service.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(exist_ok=True)
old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
specs=[('xms_detect_entry',0x784,0x7a9),('xms_query_capacity',0x7aa,0x7c2),('xms_allocate_handle',0x7c2,0x7e3),('xms_release_handle',0x7e4,0x7fe),('xms_lock_handle',0x826,0x844),('xms_unlock_handle',0x844,0x85e)]
functions=[];starts={};seen=set()
for name,lo,hi in specs:
 todo=[lo];d={};edges=[]
 while todo:
  ip=todo.pop()
  if ip in d:continue
  assert lo<=ip<hi;i=Decoder(16,b[0x7680+ip:0x7680+hi],ip=ip).decode();assert not i.is_invalid;d[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 rows=[]
 for ip,i in sorted(d.items()):
  p=0x7680+ip;raw=b[p:0x7680+i.next_ip];assert old[p]['bytes']==raw.hex();rows.append(dict(cs=0x768,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)));starts[p]=name
 save(name,rows);save(name+'_cfg',edges);functions.append(dict(name=name,start=0x7680+lo,end_exclusive=0x7680+hi,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(x['bytes'])) for x in rows)))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];events=[];shutdown_seen=set()
def run(load,kind,argument=0,ok=1,error=0,flag=1,enabled=1,detect=0x80,repeats=1):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 ds=load+0x2771;base=ds*16;ram=bytearray(0x100000);ram[load*16:load*16+len(raw)]=raw;ram[base:base+0x10000]=b'\x66'*0x10000
 def word(a,v):struct.pack_into('<H',ram,base+a,v)
 word(0x3506,argument);word(0x350e,0x1234 if kind=='xms_detect_entry' else 0x100);word(0x3510,0x5678 if kind=='xms_detect_entry' else 0x6000);ram[base+0x350c]=flag;ram[base+0x3cce]=enabled
 # Mutable data remains observable, but fixture manager itself consists only of RETF.
 ram[0x60100]=0xcb
 expected=bytearray(ram)
 if kind=='xms_detect_entry' and detect&0x80:struct.pack_into('<HH',expected,base+0x350e,0x100,0x6000)
 cs=load+0x768;ip=0x24 if kind=='shutdown' else next(a for n,a,z in specs if n==kind);stack=0xf000;lo=base+stack-64;hi=base+stack+8;calls=[];intrs=[];writes=[];executed=[];returns=[]
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,bytes(ram))
 def hook(e,address,size,data):
  if address==0x50100:returns.append(True);e.emu_stop();return
  if address==0x60100:
   ah=e.reg_read(UC_X86_REG_AH);dx=e.reg_read(UC_X86_REG_DX);assert e.reg_read(UC_X86_REG_DS)==ds
   want={'xms_query_capacity':8,'xms_allocate_handle':9,'xms_release_handle':10,'xms_lock_handle':12,'xms_unlock_handle':13}
   if kind=='shutdown':assert ah==(13 if len(calls)%2==0 else 10) and dx==argument
   else:
    assert ah==want[kind]
    if kind!='xms_query_capacity':assert dx==argument
   calls.append(dict(AH=ah,input_DX=dx,fixture_AX=ok,fixture_BX=0x7800|error,fixture_DX=0x3456))
   e.reg_write(UC_X86_REG_AX,ok);e.reg_write(UC_X86_REG_BX,0x7800|error);e.reg_write(UC_X86_REG_DX,0x3456);return
  p=address-load*16;executed.append(p)
  if p in starts:seen.add(p)
  else:assert kind=='shutdown' and 0x76a4<=p<0x7913;shutdown_seen.add(p)
 def intr(e,number,data):
  assert kind=='xms_detect_entry' and number==0x2f;ax=e.reg_read(UC_X86_REG_AX);intrs.append(ax)
  if len(intrs)==1:assert ax==0x4300;e.reg_write(UC_X86_REG_AL,detect)
  else:assert len(intrs)==2 and ax==0x4310;e.reg_write(UC_X86_REG_ES,0x6000);e.reg_write(UC_X86_REG_BX,0x100)
 def write(e,access,address,size,value,data):
  if lo<=address and address+size<=hi:return
  writes.append((address,size,value&((1<<(8*size))-1)))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_MEM_WRITE,write)
 for repeat in range(repeats):
  frame=struct.pack('<3H',0x100,0x5000,1 if kind=='shutdown' else argument);u.mem_write(base+stack,frame)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,stack),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_AX,0xa55a),(UC_X86_REG_DX,0x2468),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
  u.emu_start(cs*16+ip,0xfffff,count=2000);assert len(returns)==repeat+1
  for reg,val in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_SP,stack+4)]:assert u.reg_read(reg)==val
  assert bytes(u.mem_read(base+stack,6))==frame
 actual=bytes(u.mem_read(0,len(ram)));assert actual[:lo]==expected[:lo] and actual[hi:]==expected[hi:]
 ax=u.reg_read(UC_X86_REG_AX);dx=u.reg_read(UC_X86_REG_DX)
 if kind=='xms_detect_entry':
  assert intrs==([0x4300,0x4310] if detect&0x80 else [0x4300]);assert ax==bool(detect&0x80);assert dx==0x2468;wantwrites=[(base+0x350e,2,0x100),(base+0x3510,2,0x6000)] if detect&0x80 else []
 elif kind=='shutdown':assert len(calls)==(2*repeats if flag else 0);wantwrites=[]
 else:
  assert len(calls)==1;wantwrites=[]
  if kind=='xms_query_capacity':ea,ed=ok,0 if ok else error<<8
  elif kind=='xms_allocate_handle':ea,ed=(0x3456,0) if ok else (0,(error<<8)|0x56)
  elif kind=='xms_lock_handle':ea,ed=(0x7800|error,0x3456) if ok else (0,error<<8)
  elif kind=='xms_unlock_handle':ea,ed=ok,0 if ok else error<<8
  else:ea,ed=0,0 if ok else error<<8
  assert (ax,dx)==(ea,ed),(kind,ok,error,hex(ax),hex(dx),hex(ea),hex(ed))
 assert writes==wantwrites
 cid=len(cases)
 for j,c in enumerate(calls):events.append(dict(case=cid,index=j,**c))
 cases.append(dict(case=cid,load=load,kind=kind,argument=argument,fixture_AX=ok,fixture_BL=error,gate_350C=flag,current_enabled_3CCE=enabled,detect_AL=detect,repeats=repeats,manager_calls=len(calls),multiplex_calls=len(intrs),returned_AX=ax,returned_DX=dx,whole_RAM_bytes_checked=len(ram)-(hi-lo),nonstack_writes=len(writes),original_instruction_events=len(executed),status='PASS'))
for load,detect in itertools.product((0x824,0x1000),(0,1,0x7f,0x80,0x81,0xff)):run(load,'xms_detect_entry',detect=detect)
for load,kind,ok,error in itertools.product((0x824,0x1000),[x[0] for x in specs[1:]],(0,1,0xffff),(0,0x7f,0x80,0xff)):
 for arg in ((0,) if kind=='xms_query_capacity' else (0,1,0x7fff,0xffff)):run(load,kind,arg,ok,error)
for load,arg,ok,error,flag,enabled,repeats in itertools.product((0x824,0x1000),(0,1,0xffff),(0,1),(0,0x80,0xff),(1,0x80),(0,1),(1,2)):run(load,'shutdown',arg,ok,error,flag,enabled,repeats=repeats)
for load,arg,enabled,repeats in itertools.product((0x824,0x1000),(0,1,0xffff),(0,1),(1,2)):run(load,'shutdown',arg,flag=0,enabled=enabled,repeats=repeats)
assert seen==set(starts)
save('cases',cases);save('manager_events',events);save('instruction_execution_coverage',[dict(image_offset=p,function=starts[p],executed=p in seen) for p in sorted(starts)])
prior=out.parent/'cache_reset_replay/instruction_execution_coverage.csv'
prior_summary=out.parent/'cache_reset_replay/summary.json'
combined=list(csv.DictReader(prior.open()))
for row in combined:
 if int(row['image_offset']) in shutdown_seen:row['executed']='True'
save('combined_dispatch_execution',combined)
remaining=[int(x['image_offset']) for x in combined if x['function']=='cache_lifecycle_dispatch_012' and x['executed']=='False']
gaps=[]
for name,lo,hi in specs:
 occupied=set()
 for row in csv.DictReader((out/(name+'.csv')).open()):
  a=int(row['image_offset']);occupied.update(range(a,a+len(bytes.fromhex(row['bytes']))))
 for a in range(0x7680+lo,0x7680+hi):
  if a not in occupied:gaps.append(dict(function=name,image_offset=a,byte=b[a],status='outside retained entryCFG;not globally proven padding'))
save('span_gaps',gaps)
s=dict(functions=functions,cases=len(cases),failures=0,all_new_starts_executed=True,wrapper_starts=len(starts),wrapper_code_bytes=sum(x['instruction_bytes'] for x in functions),shutdown_dispatch_executed_starts=sorted(shutdown_seen),remaining_unexecuted_dispatch_starts=remaining,runtime_tests=0,new_deep_verified_bytes=0,scope='Six original XMS wrappers plus whole mode1 caller. External INT2F/manager responses only fixtures; no XMS allocation/free/lock side effects. Full1MiB except72controlstackB checked, exactnonstackwrites, frames/registers; repeated shutdown tests stalegate but not natural doublefree. Existing dispatcher reused,not newly counted.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',prior,prior_summary,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
