"""python audit_replay_episode_selector.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
todo=[0x260a];decoded={};edges=[];rows=[]
while todo:
 ip=todo.pop()
 if ip in decoded:continue
 assert 0x260a<=ip<0x2696;i=Decoder(16,b[0xd290+ip:0xf926],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
 if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
for ip,i in sorted(decoded.items()):
 pos=0xd290+ip;raw=b[pos:0xd290+i.next_ip];assert lookup[pos]['bytes']==raw.hex();rows.append(dict(cs=0xd29,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
save('episode_menu_available_select',rows);save('episode_menu_available_select_cfg',edges)
context=[]
for r in old:
 if r['cs']==0xd29 and (0x27ce<=r['ip']<0x2838 or 0x95a<=r['ip']<0x980):
  raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;context.append(r)
save('difficulty_and_game_call_context_not_whole_functions',context)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
for load,available,registered,initial_style,selected in itertools.product((0,0x1000),range(8),(0,1),(6,1),(6,15,16,17)):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));cs=load+0xd29;ds=load+0x2771;seg=load+0x20b9;crt=(load+0x11ee)*16
 for n in range(3):u.mem_write(seg*16+0xfae+18*n+5,bytes([initial_style]))
 expected=bytearray(u.mem_read(seg*16+0xfae,72));state=dict(format_calls=[],access_calls=[],query_calls=0,menu_calls=0)
 targets={crt+0x278c:'format',crt+0x3990:'access',(load+0x83d)*16+0x29ca:'query',cs*16+0x1946:'menu'}
 for addr in targets:u.mem_write(addr,b'\xcb')
 def hook(uc,address,size,user):
  if address not in targets:return
  sp=uc.reg_read(UC_X86_REG_SP)
  def args(n):return struct.unpack('<'+'H'*n,bytes(uc.mem_read(ds*16+sp+4,n*2)))
  op=targets[address]
  if op=='format':
   dest,fmtptr,base,n=args(4);assert (fmtptr,base)==(0x1ffb,0x1ff6) and n==len(state['format_calls'])+1
   assert bytes(uc.mem_read(ds*16+fmtptr,5))==b'%s%d\0' and bytes(uc.mem_read(ds*16+base,5))==b'map.\0';name=('map.%d'%n).encode()+b'\0';uc.mem_write(ds*16+dest,name);state['format_calls'].append(n);uc.reg_write(UC_X86_REG_AX,len(name)-1)
  elif op=='access':
   dest,mode=args(2);n=len(state['access_calls'])+1;assert mode==4 and bytes(uc.mem_read(ds*16+dest,6))==('map.%d\0'%n).encode();state['access_calls'].append(n);uc.reg_write(UC_X86_REG_AX,0 if available&(1<<(n-1)) else 65535)
  elif op=='query':
   assert args(1)==(1,);state['query_calls']+=1;uc.reg_write(UC_X86_REG_AX,0);uc.reg_write(UC_X86_REG_DX,0x1234 if registered else 0)
  else:
   assert args(2)==(0xfae,seg);state['menu_calls']+=1;uc.reg_write(UC_X86_REG_AX,selected)
 u.hook_add(UC_HOOK_CODE,hook)
 for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 u.mem_write(ds*16+0xf000,struct.pack('<HH',0x100,0x5000));u.emu_start(cs*16+0x260a,0x50100,count=3000)
 for n in range(3):
  if available&(1<<n) and (registered or n==0):expected[n*18+5]=1
 actual=bytes(u.mem_read(seg*16+0xfae,72));assert actual==expected and u.reg_read(UC_X86_REG_AX)==(0 if selected==6 else selected-14)
 assert state==dict(format_calls=[1,2,3],access_calls=[1,2,3],query_calls=bin(available).count('1'),menu_calls=1)
 assert u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SS)==ds and u.reg_read(UC_X86_REG_SP)==0xf004 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x2345 and u.reg_read(UC_X86_REG_DI)==0x3456
 cases.append(dict(load=load,available_mask=available,registered_nonnull=registered,initial_style=initial_style,menu_stub_id=selected,style1=actual[5],style2=actual[23],style3=actual[41],result=0 if selected==6 else selected-14,passed=True))
save('cases',cases)
s=dict(functions=[dict(name='episode_menu_available_select',start=0xf89a,end_exclusive=0xf926,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows))],cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='whole original episode selector over compiled3record table; formatter/access/registered-query/menu mocked; style1 assignment only, unavailable leaves old style; arbitrary menu stub choice does not prove real selection of unavailable items; normal DS=SS caller domain',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
