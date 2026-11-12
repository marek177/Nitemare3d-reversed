"""python audit_replay_door_interaction.py IMAGE INVENTORY DECODER EMULATOR OUT
Whole original0598 and lookup0000, only sound dispatch substituted.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
todo=[0x598];decoded={};edges=[]
while todo:
 ip=todo.pop()
 if ip in decoded:continue
 assert 0x598<=ip<0x704;i=Decoder(16,b[ip:0x704],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
 if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
rows=[]
for ip,i in sorted(decoded.items()):
 raw=b[ip:i.next_ip];assert old[ip]['bytes']==raw.hex();rows.append(dict(cs=0,ip=ip,image_offset=ip,bytes=raw.hex(),instruction=fmt.format(i)))
save('door_interaction',rows);save('door_interaction_cfg',edges);rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];visited=set();paths=set()
def run(load,gate,state,kind,orientation,command,direction,neighbors,request,group):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));ds=load+0x2771;seg=load+0x21fd
 world=bytearray(0x573e);dg=bytearray(0xe030);record=0x3076;cell=0x5000;step=128 if orientation==2 else 2
 struct.pack_into('<H',world,0,3);dg[0x430e]=gate
 for n,offset in enumerate((cell,cell+step,cell-step)):
  q=record+18*n;desc=0x7000+32*n;desc2=0x7080+32*n
  struct.pack_into('<HHHHH',world,q,desc,desc2,offset,seg,state if n==0 else 0x1234+n)
  world[q+16]=request if n==0 else 0x55+n
  dg[desc+5]=0xa4;dg[desc2+5]=0xb0;dg[desc+6]=kind;dg[desc+7]=orientation;dg[desc+1]=direction
  world[offset]=0x71 if n==0 or neighbors&(1<<(n-1)) else 0x70
 dg[0xd00c+0x71]=8;expected_w=bytearray(world);expected_d=bytearray(dg);sound=[];newstate=state
 if not gate and state!=4:
  if state in (0,2):
   newstate=3
   if request:sound=[0x26]
   expected_w[record+16]=0
   for p in (0x7005,0x7085):expected_d[p]|=1
  elif state in (1,3):
   if kind not in (0x3d,0x3e) or ((((command&255)+1)&255)&6)>>1==direction:
    newstate=2
    if request:sound=[0x25]
  struct.pack_into('<H',expected_w,record+8,newstate)
  for n in (1,2):
   if neighbors&(1<<(n-1)):
    struct.pack_into('<H',expected_w,record+18*n+8,newstate)
    if newstate==3:
     for p in (0x7000+32*n+5,0x7080+32*n+5):expected_d[p]|=1
 u.mem_write(seg*16,bytes(world));u.mem_write(ds*16,bytes(dg));stack=struct.pack('<5H',0x100,0x5000,record,seg,command);u.mem_write(ds*16+0xf000,stack)
 for reg,value in [(UC_X86_REG_CS,load),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_AX,0xabcd),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,value)
 calls=[];trace=[];done=[]
 def hook(emu,address,size,data):
  if address==0x50100:done.append(True);emu.emu_stop();return
  if load*16+0x598<=address<load*16+0x704:visited.add(address-load*16);trace.append(address-load*16)
  if address==(load+0xc2b)*16+0x3d6:
   sp=emu.reg_read(UC_X86_REG_SP);ss=emu.reg_read(UC_X86_REG_SS);raw=bytes(emu.mem_read(ss*16+sp,10));ret,cs,ident,lo,hi=struct.unpack('<5H',raw);assert lo==hi==0;calls.append(ident)
   emu.reg_write(UC_X86_REG_AX,0xd2e3);emu.reg_write(UC_X86_REG_DX,0xcafe);emu.reg_write(UC_X86_REG_ES,0x7777);emu.reg_write(UC_X86_REG_SP,sp+4);emu.reg_write(UC_X86_REG_CS,cs);emu.reg_write(UC_X86_REG_IP,ret)
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(load*16+0x598,0,count=5000)
 assert done and calls==sound,(group,load,gate,state,kind,orientation,command,direction,neighbors,request,calls,sound)
 assert bytes(u.mem_read(seg*16,len(world)))==expected_w,'world mismatch'
 assert bytes(u.mem_read(ds*16,len(dg)))==expected_d,'DGROUP mismatch'
 assert bytes(u.mem_read(ds*16+0xf000,10))==stack
 assert u.reg_read(UC_X86_REG_SP)==0xf004 and u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SS)==ds
 assert [u.reg_read(q) for q in (UC_X86_REG_BP,UC_X86_REG_SI,UC_X86_REG_DI)]==[0x1234,0x2345,0x3456]
 paths.add(tuple(trace));cases.append(dict(group=group,load=load,gate=gate,state=state,kind=kind,orientation=orientation,command=command,direction=direction,neighbors=neighbors,request=request,result_state=newstate,sound_calls=';'.join(map(str,calls)),status='PASS'))
for load,gate,state,kind,orientation,command,neighbors,request in itertools.product((0x1000,0x824),(0,1),(0,1,2,3,4,5,65535),(0x32,0x3d,0x3e,0x40),(0,2),(0,1,7,255),range(4),(0,1)):
 run(load,gate,state,kind,orientation,command|((0xd2 if load==0x824 else 0x39)<<8),3 if neighbors&1 else 0,neighbors,request,'state_neighbor_matrix')
for command,direction in itertools.product(range(256),range(4)):
 run(0x824,0,1,0x3d,2,command|0xe300,direction,3,1,'all_low_command_bytes')
save('cases',cases);save('instruction_execution_coverage',[dict(ip=ip,executed=ip in visited) for ip in sorted(decoded)])
result=dict(functions=[dict(name='door_interaction',start=0x598,end_exclusive=0x704,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows))],cases=len(cases),failures=0,executed_instruction_starts=len(visited),unexecuted_instruction_starts=sorted(set(decoded)-visited),distinct_paths=len(paths),runtime_tests=0,new_deep_verified_bytes=0,scope='whole0598 and original lookup0000; only sound0C2B:03D6 substituted with recorded calls/volatile AX DX ES clobber; full map+DGROUP compared; synthetic valid neighbor records; missing-door and sound internals unclosed',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
