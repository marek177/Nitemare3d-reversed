"""python audit_replay_worx_private_stack.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INSN
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(parents=True,exist_ok=True)
old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[]
for name,start,end in [('worx_private_stack_tick',0x40e7,0x4150),('worx_timer_irq_dispatch',0x4150,0x41b3)]:
 todo=[start];decoded={};edges=[];rows=[]
 while todo:
  ip=todo.pop()
  if ip in decoded:continue
  assert start<=ip<end;i=Decoder(16,b[0x15bf0+ip:0x15bf0+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 for ip,i in sorted(decoded.items()):
  pos=0x15bf0+ip;raw=b[pos:0x15bf0+i.next_ip];assert lookup[pos]['bytes']==raw.hex();rows.append(dict(cs=0x15bf,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);save(name+'_cfg',edges);functions.append(dict(name=name,start=0x15bf0+start,end_exclusive=0x15bf0+end,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows)))
init=[]
for r in old:
 if r['cs']==0x15bf and 0x2ebc<=r['ip']<0x2ecc:
  raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;init.append(r)
save('stack_initializer_context',init)
vector=[]
for r in old:
 if r['cs']==0x15bf and 0x2ee0<=r['ip']<0x2f03:
  raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;vector.append(r)
save('timer_vector_installer_context',vector)
assert struct.unpack_from('<H',b,0x15bf0+0x3ed4)[0]==65535
save('initial_control_constants',[dict(cs_offset=off,image_offset=0x15bf0+off,original_word=struct.unpack_from('<H',b,0x15bf0+off)[0],scope='file initial value, not an arbitrary runtime state') for off in (0x2db4,0x2db6,0x3ed4,0x3edd,0x3edf,0x3ee1,0x3ee3,0x40e5)])
fields=[]
for name,start,end,typ in [('saved_and_private_SS_SP_words',0x3edd,0x3ee5,'WORD4_savedSP_savedSS_privateSP_privateSS'),('minimum_direct_stack_slots',0x40cd,0x40e1,'WORD9_saved_registers_plus_shared_PUSH_CS_and_NEAR_return_slot'),('skipped_tick_counter',0x40e5,0x40e7,'WORD_skipped_private_callback_counter')]:
 a=0x15bf0+start;z=0x15bf0+end;fields.append(dict(name=name,start=a,end_exclusive=z,length=z-a,type=typ,status='PARTIAL',range_sha256=sha(b[a:z]),scope='direct native references; stack slots assume initializedSP40E1, not proof of full private stack capacity'))
save('data_fields',fields)
(out/'data_fields.json').write_text(json.dumps(fields,indent=2)+'\n')
save('stack_capacity_candidate',[dict(start=0x19ad5,end_exclusive=0x19cd5,length=512,type='candidate_private_stack_zero_region_lower_bound_unproven',status='CLASSIFIED ONLY',range_sha256=sha(b[0x19ad5:0x19cd5]),scope='adjacent zero extent and stack top; full512B capacity not proven and not added to typed data union')])
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
def make(load):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));return u
regs={UC_X86_REG_AX:0x1234,UC_X86_REG_BX:0x2345,UC_X86_REG_CX:0x3456,UC_X86_REG_DX:0x4567,UC_X86_REG_BP:0x5678,UC_X86_REG_SI:0x6789,UC_X86_REG_DI:0x789a,UC_X86_REG_DS:0x1234,UC_X86_REG_ES:0x2345}
def prepare(u,cs,ss,flags):
 for reg,value in list(regs.items())+[(UC_X86_REG_CS,cs),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,0xf000),(UC_X86_REG_EFLAGS,flags)]:u.reg_write(reg,value)
 u.mem_write(cs*16+0x3ee1,struct.pack('<HH',0x40e1,cs))
for load,stack,counter,unit,pending,music,digital in itertools.product((0,0x1000),(0x6000,0x7000),(0,65535,65536,0x7fffffff,0x80000000,0xffffffff),(0,1,65535),(0,0xa5),(0,0x20),(0,1)):
 u=make(load);cs=load+0x15bf;prepare(u,cs,stack,2);u.mem_write(stack*16+0xf000,struct.pack('<H',0x6000));u.mem_write(cs*16+0x2c49,struct.pack('<HI',unit,counter));u.mem_write(cs*16+0x2c53,bytes([pending]));u.mem_write(cs*16+0x2dbc,bytes([music]));u.mem_write(cs*16+0x3ed6,bytes([digital]))
 calls=[];targets={cs*16+0x555d:'music',cs*16+0x5df2:'digital'}
 for a in targets:u.mem_write(a,b'\xc3')
 def hook(uc,address,size,user):
  if address in targets:
   calls.append(targets[address]);assert uc.reg_read(UC_X86_REG_SS)==cs and uc.reg_read(UC_X86_REG_DS)==cs and uc.reg_read(UC_X86_REG_SP)==0x40cd and uc.reg_read(UC_X86_REG_EFLAGS)&512
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(cs*16+0x40e7,cs*16+0x6000,count=500)
 expected=(counter-unit)&0xffffffff;assert int.from_bytes(u.mem_read(cs*16+0x2c4b,4),'little')==expected and bytes(u.mem_read(cs*16+0x2c53,1))==bytes([1 if expected&0x80000000 else pending])
 assert calls==(['music'] if music else [])+(['digital'] if digital else []) and all(u.reg_read(reg)==value for reg,value in regs.items())
 assert (u.reg_read(UC_X86_REG_SS),u.reg_read(UC_X86_REG_SP),u.reg_read(UC_X86_REG_IP))==(stack,0xf002,0x6000) and not(u.reg_read(UC_X86_REG_EFLAGS)&512)
 assert bytes(u.mem_read(cs*16+0x3edd,4))==struct.pack('<HH',0xf000,stack)
 assert int.from_bytes(u.mem_read(cs*16+0x40cd,2),'little')==(0x413b if digital else 0x4130 if music else cs)
 cases.append(dict(kind='private_callback',load=load,stack=stack,counter=counter,unit=unit,pending=pending,music=music,digital=digital,result_counter=expected,passed=True))
private_count=len(cases)
irq_cases=[]
for load,threshold,phase,depth,flags,digital,missed in itertools.product((0,0x1000),(0,1,3),(0,2,65535),(0,65535),(0,0x16,0x20,0x36),(0,1),(7,65535)):
 u=make(load);cs=load+0x15bf;ss=0x7000;frame_flags=0x602;prepare(u,cs,ss,frame_flags&~0x300);u.mem_write(ss*16+0xf000,struct.pack('<HHH',0x100,0x5000,frame_flags));u.mem_write(cs*16+0xa,struct.pack('<HH',0x100,0x6000));u.mem_write(0x60100,b'\xcf')
 u.mem_write(cs*16+0x2db4,struct.pack('<HH',phase,threshold));u.mem_write(cs*16+0x3ed4,struct.pack('<H',depth));u.mem_write(cs*16+0x40e5,struct.pack('<H',missed));u.mem_write(cs*16+0x2dbc,bytes([flags]));u.mem_write(cs*16+0x3ed6,bytes([digital]));u.mem_write(cs*16+0x2c49,struct.pack('<HI',100,50));u.mem_write(cs*16+0x2c53,b'\xa5')
 targets={cs*16+0x4476:'mixer',cs*16+0x555d:'music',cs*16+0x5df2:'digital',0x60100:'old_timer'};calls=[];ports=[]
 for a in targets:
  if a!=0x60100:u.mem_write(a,b'\xc3')
 def hook(uc,address,size,user):
  if address in targets:calls.append(targets[address])
 def port(uc,p,size,value,user):ports.append((p,size,value))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT);u.emu_start(cs*16+0x4150,0x50100,count=1000)
 nextphase=(phase+1)&65535;chain=nextphase>=threshold;private=not chain and depth==65535
 expected_calls=(['mixer'] if flags&0x16 else [])+(['old_timer'] if chain else (['music'] if private and flags&0x20 else [])+(['digital'] if private and digital else []))
 assert calls==expected_calls and ports==([] if chain else [(0x20,1,0x20)])
 assert int.from_bytes(u.mem_read(cs*16+0x2db4,2),'little')==(0 if chain else nextphase) and int.from_bytes(u.mem_read(cs*16+0x3ed4,2),'little')==depth
 assert int.from_bytes(u.mem_read(cs*16+0x40e5,2),'little')==((missed+1)&65535 if not chain and not private else missed)
 assert int.from_bytes(u.mem_read(cs*16+0x2c4b,4),'little')==(0xffffffce if private else 50)
 assert (u.reg_read(UC_X86_REG_CS),u.reg_read(UC_X86_REG_IP),u.reg_read(UC_X86_REG_SS),u.reg_read(UC_X86_REG_SP))==(0x5000,0x100,ss,0xf006) and all(u.reg_read(reg)==value for reg,value in regs.items())
 assert u.reg_read(UC_X86_REG_EFLAGS)&65535==frame_flags
 irq_cases.append(dict(kind='timer_irq_with_native_private_callback',load=load,threshold=threshold,phase=phase,depth=depth,flags=flags,digital=digital,missed=missed,chain=chain,private=private,passed=True))
save('cases',cases);save('timer_irq_cases',irq_cases)
summary=dict(functions=functions,cases=private_count+len(irq_cases),private_callback_cases=private_count,timer_irq_cases=len(irq_cases),typed_data_bytes=30,capacity_candidate_bytes_not_added_to_typed_union=512,failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='whole original private-stack callback plus timer IRQ with callback kept native; mixer/music/digital bodies and old timer handler mocked, OUT observed; IF/DF and stack/register return checked; no proof of full private stack capacity, arbitrary nested IRQ, audio output or physical timing',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
