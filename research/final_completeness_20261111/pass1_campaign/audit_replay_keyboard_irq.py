"""python audit_replay_keyboard_irq.py IMAGE INVENTORY DECODER EMULATOR OUT
Whole IRQ9 body plus BIOS key wrapper/poll/drain helpers. Dependencies explicit.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INSN,UC_HOOK_INTR
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[]
for name,cs,start,end in [('keyboard_irq9',0x6b0,0,0x134),('keyboard_bios_poll',0x6b0,0x1d0,0x1e2),('keyboard_bios_drain',0x6b0,0x1e2,0x203),('crt_bioskey_word',0x11ee,0x39b0,0x39d4)]:
 todo=[start];decoded={};edges=[];rows=[];missing=0
 while todo:
  ip=todo.pop()
  if ip in decoded:continue
  assert start<=ip<end;i=Decoder(16,b[cs*16+ip:cs*16+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 for ip,i in sorted(decoded.items()):
  pos=cs*16+ip;raw=b[pos:cs*16+i.next_ip]
  if pos in lookup:assert lookup[pos]['bytes']==raw.hex()
  else:missing+=1
  rows.append(dict(cs=cs,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i),historical_start_present=pos in lookup))
 save(name,rows);save(name+'_cfg',edges);functions.append(dict(name=name,start=cs*16+start,end_exclusive=cs*16+end,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),starts_missing_from_historical_inventory=missing))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
def make(load):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));return u
gp={UC_X86_REG_EAX:0x12345678,UC_X86_REG_EBX:0x23456789,UC_X86_REG_ECX:0x3456789a,UC_X86_REG_EDX:0x456789ab,UC_X86_REG_EBP:0x56789abc,UC_X86_REG_ESI:0x6789abcd,UC_X86_REG_EDI:0x789abcde}
def setup(u,cs,ss,flags):
 for reg,val in list(gp.items())+[(UC_X86_REG_CS,cs),(UC_X86_REG_DS,0x1234),(UC_X86_REG_ES,0x5678),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,0xf000),(UC_X86_REG_EFLAGS,flags)]:u.reg_write(reg,val)
mapping={1:(0,1),0x1d:(0,0x80),0x2a:(0,0x40),0x36:(0,0x20),0x38:(1,1),0x39:(1,2),0x48:(0,2),0x4b:(0,8),0x4d:(0,16),0x50:(0,4)}
for load,scan,previous,initial,flush,mode in itertools.product((0,0x1000),range(256),(0,0xe0,0xe1),(0xa55a,0x5aa5),(0,1),(0,4)):
 u=make(load);cs=load+0x6b0;ds=load+0x2771;ss=ds+(0x400 if load else 0);entry_flags=0x202|(0x400 if initial==0xa55a else 0)
 setup(u,cs,ss,entry_flags&~0x300);u.mem_write(ss*16+0xf000,struct.pack('<HHH',0x100,0x5000,entry_flags))
 u.mem_write(ds*16+0x3f50,struct.pack('<HHH',initial,0x100,0x6000));u.mem_write(0x60100,b'\xcf');u.mem_write(cs*16+0x1e2,b'\xcb')
 u.mem_write(ds*16+0x34ba,bytes([previous]));u.mem_write(ds*16+0x3cd1,bytes([flush]));u.mem_write(ds*16+0x3cd4,struct.pack('<HH',0x55aa,mode))
 expected=initial;code=scan&127;pressed=not(scan&128)
 if code in mapping and not(code in (0x2a,0x36) and previous==0xe0):
  byte,mask=mapping[code];mask<<=byte*8;expected=(initial&~mask)|(mask if pressed else 0)
 state=dict(old_calls=0,flush_calls=0,in_reads=0)
 def port(uc,number,size,user):assert (number,size)==(0x60,1);state['in_reads']+=1;return scan
 def hook(uc,address,size,user):
  if address==0x60100:
   state['old_calls']+=1;assert int.from_bytes(uc.mem_read(ds*16+0x3f50,2),'little')==expected
   assert bytes(uc.mem_read(ds*16+0x34ba,1))==bytes([scan]) and not(uc.reg_read(UC_X86_REG_EFLAGS)&1024)
  elif address==cs*16+0x1e2:state['flush_calls']+=1;uc.mem_write(ds*16+0x3f50,b'\0\0')
 u.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_IN);u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16,0x50100,count=1000)
 assert (u.reg_read(UC_X86_REG_CS),u.reg_read(UC_X86_REG_IP),u.reg_read(UC_X86_REG_SP))==(0x5000,0x100,0xf006)
 assert all(u.reg_read(reg)==val for reg,val in gp.items()) and u.reg_read(UC_X86_REG_DS)==0x1234 and u.reg_read(UC_X86_REG_ES)==0x5678 and u.reg_read(UC_X86_REG_SS)==ss
 assert u.reg_read(UC_X86_REG_EFLAGS)&0xffff==entry_flags
 result=int.from_bytes(u.mem_read(ds*16+0x3f50,2),'little');assert result==(0 if flush else expected)
 assert int.from_bytes(u.mem_read(ds*16+0x3cd4,2),'little')==(0 if mode==4 else 0x55aa) and state==dict(old_calls=1,flush_calls=flush,in_reads=1)
 cases.append(dict(kind='whole_irq',load=load,scan=scan,previous=previous,initial_flags=initial,flush=flush,mode=mode,expected_flags=result,passed=True))

# BIOS wrapper itself runs; INT16 device results are mocked. Every AH byte,
# AX zero/nonzero and ZF0/1 combination is included at two relocation bases.
bios_cases=[]
for load,command,ax,zf in itertools.product((0,0x1000),range(256),(0,0x3920),(0,1)):
 u=make(load);cs=load+0x11ee;ds=load+0x2771;setup(u,cs,ds,2);u.mem_write(ds*16+0xf000,struct.pack('<HHH',0x100,0x5000,command))
 calls=[]
 def intr(uc,number,user):
  assert number==0x16 and uc.reg_read(UC_X86_REG_AX)>>8==command;calls.append(command);uc.reg_write(UC_X86_REG_AX,ax);f=uc.reg_read(UC_X86_REG_EFLAGS);uc.reg_write(UC_X86_REG_EFLAGS,(f&~64)|(zf*64))
 u.hook_add(UC_HOOK_INTR,intr);u.emu_start(cs*16+0x39b0,0x50100,count=100)
 low=command&15;expected=0 if zf and low==1 else ax if low==2 or ax else 65535
 assert u.reg_read(UC_X86_REG_AX)==expected and calls==[command]
 bios_cases.append(dict(load=load,command=command,interrupt_ax=ax,zf=zf,result=expected,passed=True))
save('cases',cases);save('bios_wrapper_cases',bios_cases)
summary=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=functions,cases=len(cases)+len(bios_cases),irq_cases=len(cases),bios_wrapper_cases=len(bios_cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='whole original IRQ with port60 input, old BIOS ISR and conditional drain helper mocked; native PUSHAD/IRET/register+flag restoration verified; separate complete CRT BIOS wrapper with INT16 device results mocked; poll/drain helpers byte/CFG decoded but not independently replayed here',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
