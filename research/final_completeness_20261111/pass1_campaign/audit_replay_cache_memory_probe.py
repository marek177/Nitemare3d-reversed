"""IMAGE INVENTORY DECODER EMULATOR OUT: original descending conventional-memory probe.
Only CRT allocation/free callees are fixtures; no actual heap capacity or zeroing proof.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(exist_ok=True);old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};fmt=Formatter(FormatterSyntax.INTEL);todo=[0x58];dec={};edges=[]
while todo:
 ip=todo.pop()
 if ip in dec:continue
 assert 0x58<=ip<0x9d;i=Decoder(16,b[0xfba0+ip:0xfba0+0x9d],ip=ip).decode();assert not i.is_invalid;dec[ip]=i
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
 if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
rows=[]
for ip,i in sorted(dec.items()):
 p=0xfba0+ip;raw=b[p:0xfba0+i.next_ip];assert old[p]['bytes']==raw.hex();rows.append(dict(cs=0xfba,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
def save(name,data):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
save('descending_memory_probe',rows);save('descending_memory_probe_cfg',edges);rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];vis=set();callrows=[]
patterns=[('threshold',x) for x in (0,1,63,64,257,1022,1023,1024)]+[('sparse',900),('none',-1)]
for load,(pattern,limit),(off,seg) in itertools.product((0x824,0x1000),patterns,((0x10,0),(0,0x1234),(0xfffe,0xf000))):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 ram=bytearray(0x100000);ram[load*16:load*16+len(raw)]=raw;ds=load+0x2771;base=ds*16;stack=0xf000;lo,hi=base+stack-64,base+stack+8;frame=struct.pack('<HH',0x200,0x4f00);ram[base+stack:base+stack+4]=frame;alloc=(load+0x11ee)*16+0x2a16;free=(load+0x11ee)*16+0x2a0a;ram[alloc]=ram[free]=0xcb
 accepted=[k for k in range(1023,-1,-1) if pattern!='none' and (k<=limit if pattern=='threshold' else k in (0,257,900))];winner=accepted[0] if accepted else None;attempts=list(range(1023,(winner if winner is not None else 0)-1,-1));calls=[];frees=[];done=[];writes=[]
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,bytes(ram))
 for reg,val in [(UC_X86_REG_CS,load+0xfba),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,stack),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 def hook(e,address,size,data):
  if address==0x4f200:done.append(True);e.emu_stop();return
  sp=e.reg_read(UC_X86_REG_SP)
  if address==alloc:
   size,element_size=struct.unpack('<IH',bytes(e.mem_read(base+sp+4,6)));k=attempts[len(calls)];assert (size,element_size)==(k*1024,1);calls.append(k);success=k==winner;e.reg_write(UC_X86_REG_AX,off if success else 0);e.reg_write(UC_X86_REG_DX,seg if success else 0);return
  if address==free:
   actual=struct.unpack('<HH',bytes(e.mem_read(base+sp+4,4)));assert winner is not None and calls[-1]==winner and actual==(off,seg);frees.append(actual);return
  p=address-load*16;assert p in {x['image_offset'] for x in rows};vis.add(p)
 def write(e,access,address,size,value,data):
  if not(lo<=address and address+size<=hi):writes.append((address,size,value))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((load+0xfba)*16+0x58,0xfffff,count=25000);assert done and calls==attempts and len(frees)==bool(winner is not None) and not writes
 assert u.reg_read(UC_X86_REG_AX)==(winner if winner is not None else 0)
 for reg,val in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,stack+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)]:assert u.reg_read(reg)==val
 actual=bytes(u.mem_read(0,len(ram)));assert actual[:lo]==ram[:lo] and actual[hi:]==ram[hi:] and bytes(u.mem_read(base+stack,4))==frame
 cid=len(cases)
 for j,k in enumerate(calls):callrows.append(dict(case=cid,index=j,count_dword=k*1024,element_size_word=1,successful=k==winner))
 cases.append(dict(case=cid,load=load,pattern=pattern,threshold_KiB=limit,returned_pointer_offset=off,returned_pointer_segment=seg,attempts=len(calls),first_request_KiB=calls[0],last_request_KiB=calls[-1],successful_allocation=winner is not None,free_calls=len(frees),returned_AX=u.reg_read(UC_X86_REG_AX),whole_RAM_bytes_checked=len(ram)-(hi-lo),status='PASS'))
assert vis=={x['image_offset'] for x in rows};save('cases',cases);save('allocation_attempts',callrows)
s=dict(functions=[dict(name='descending_memory_probe',start=0xfbf8,end_exclusive=0xfc3d,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(x['bytes'])) for x in rows))],cases=len(cases),failures=0,all_starts_executed=True,runtime_tests=0,new_deep_verified_bytes=0,scope='Original0FBA0058..009D descending probe with CRT allocation/freefixtures: requests1023..0KiB,DWORDcounttimesWORDsize1; largest successful candidate freed; zero result ambiguous zero-size success vs allfailed. Not OS totalfree or truecalloc/free implementation. Full1MiBexcept72controlstackB checked; no nonstackwrites by probe under fixtures.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
