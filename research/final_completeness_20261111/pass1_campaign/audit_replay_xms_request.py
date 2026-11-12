"""python audit_replay_xms_request.py IMAGE INVENTORY DECODER EMULATOR OUT
Execute original constructor and wrapper; replace only external XMS manager and
stop at diagnostic entry. No manager emulation or error-handler closure claimed.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);lookup={r['image_offset']:r for r in json.loads(inventory.read_text())};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[]
for name,start,end in [('xms_append_kib',0x294,0x350),('xms_move_wrapper',0x7fe,0x826)]:
 todo=[start];decoded={};edges=[]
 while todo:
  ip=todo.pop()
  if ip in decoded:continue
  assert start<=ip<end;i=Decoder(16,b[0x7680+ip:0x7680+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 rows=[]
 for ip,i in sorted(decoded.items()):
  pos=0x7680+ip;raw=b[pos:0x7680+i.next_ip];assert lookup[pos]['bytes']==raw.hex();rows.append(dict(cs=0x768,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);save(name+'_cfg',edges);functions.append(dict(name=name,start=0x7680+start,end_exclusive=0x7680+end,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows)))
fields=[]
for name,a,e,typ,writers in [('length_bytes',0x1c070,0x1c074,'DWORD unsigned, KiB-rounded count','0768:02E4;0768:02E8'),('source_handle',0x1c074,0x1c076,'WORD constant zero: conventional source','0768:02ED'),('source_far',0x1c076,0x1c07a,'DWORD FAR16 segment:offset when source handle zero','0768:02F8'),('destination_handle',0x1c07a,0x1c07c,'WORD XMS handle from DS:3506','0768:0300'),('destination_offset',0x1c07c,0x1c080,'DWORD sign-extended used KiB shifted left 10','0768:031E;0768:0322')]:
 fields.append(dict(name='xms_move_request_'+name,start=a,end_exclusive=e,length=e-a,type=typ,status='PARTIAL',range_sha256=sha(b[a:e]),writers=writers,consumer='0768:07FE, XMS AH=0B via DS:SI',alias='[DS:2560]:0200, canonical segment 1BE7'))
save('data_fields',fields)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));pointer=0x27710+0x2560;assert struct.unpack_from('<H',b,pointer)[0]==0x1be7;assert any(int(r['image_offset'])==pointer for r in rel)
cases=[]
for load,count,used,limit,(ok,error),source in itertools.product((0,0x1000),(0,1,1023,1024,1025,65535),(0,1,32767,32768,65535),(0,1,64,65535),((1,0),(0,0),(0,0x7f),(0,0x80),(0,0xa7)),(0x12340001,0x8d9b65ca)):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));cs=load+0x768;ds=load+0x2771;descriptor=(load+0x1be7)*16+0x200;manager=0x60100;diagnostic=(load+0xfba)*16+0xc
 u.mem_write(ds*16+0x3506,struct.pack('<HHH',1,limit,used));u.mem_write(ds*16+0x350e,struct.pack('<HH',0x100,0x6000));u.mem_write(manager,b'\xcb');seed=b'\x5a'*16;u.mem_write(descriptor,seed)
 chunks=(count+1023)//1024;accepted=((used+chunks)&65535)<=limit;offset=((used if used<32768 else used-65536)<<10)&0xffffffff;expected=struct.pack('<IHIHI',chunks*1024,0,source,1,offset);state=dict(manager=0,diagnostic=False)
 def hook(uc,address,size,user):
  if address==manager:
   assert accepted and uc.reg_read(UC_X86_REG_AH)==0xb and uc.reg_read(UC_X86_REG_DS)==load+0x1be7 and uc.reg_read(UC_X86_REG_SI)==0x200
   assert bytes(uc.mem_read(descriptor,16))==expected;state['manager']+=1;uc.reg_write(UC_X86_REG_AX,ok);uc.reg_write(UC_X86_REG_BL,error)
  elif address==diagnostic:state['diagnostic']=True;uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,hook)
 for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 u.mem_write(ds*16+0xf000,struct.pack('<HHIH',0x100,0x5000,source,count));u.emu_start(cs*16+0x294,0x50100,count=2000)
 fatal=accepted and not ok and error>=128;assert state==dict(manager=int(accepted),diagnostic=fatal)
 assert bytes(u.mem_read(descriptor,16))==(expected if accepted else seed)
 assert struct.unpack('<H',bytes(u.mem_read(ds*16+0x350a,2)))[0]==(((used+chunks)&65535) if accepted and not fatal else used)
 if not fatal:
  assert (u.reg_read(UC_X86_REG_DX)<<16|u.reg_read(UC_X86_REG_AX))==(offset if accepted else 0xffffffff)
  assert u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SP)==0xf004 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x2345
  assert u.reg_read(UC_X86_REG_ES)==(ds if accepted else 0x7777)
 cases.append(dict(load=load,count=count,used_kib=used,limit_kib=limit,manager_ax=ok,manager_bl=error,source_far=source,accepted=accepted,diagnostic_entry=fatal,passed=True))
save('cases',cases)
s=dict(functions=functions,cases=len(cases),failures=0,typed_bytes=16,fields=5,runtime_tests=0,new_deep_verified_bytes=0,scope='original constructor and wrapper, external XMS manager stubbed; stops at diagnostic entry; no full error handler or XMS implementation verification',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
