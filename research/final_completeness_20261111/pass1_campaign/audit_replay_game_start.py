"""python audit_replay_game_start.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

todo=[0x95a];decoded={};edges=[];rows=[]
while todo:
 ip=todo.pop()
 if ip in decoded:continue
 assert 0x95a<=ip<0xa40;i=Decoder(16,b[0xd290+ip:0xdcd0],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
 if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
for ip,i in sorted(decoded.items()):
 pos=0xd290+ip;raw=b[pos:0xd290+i.next_ip];assert lookup[pos]['bytes']==raw.hex();rows.append(dict(cs=0xd29,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
save('game_start_orchestrator',rows);save('game_start_orchestrator_cfg',edges)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
# Callees are stubbed; mutations of episode and intro flag are explicit model inputs.
for load,initial_flag,intro_out,old_episode,episode,level,mode in itertools.product((0,0x1000),(0,1,255),(0,1),(0,2),(0,1,65535),(0,65535),(0,1)):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));cs=load+0xd29;ds=load+0x2771
 def put(off,raw):u.mem_write(ds*16+off,raw)
 def word(off):return struct.unpack('<H',bytes(u.mem_read(ds*16+off,2)))[0]
 put(0x1c9c,bytes([initial_flag]));put(0x626a,struct.pack('<H',old_episode));put(0x4152,bytes([mode]));put(0x4192,b'\xa5\x5a');put(0x3cd1,b'\xaa');put(0x3cd4,b'\xcc\xcc')
 targets={}
 for seg,ip,name in [(0xd29,0x80e,'intro'),(0x476,0,'progress_init'),(0xd29,0x400,'query'),(0xd29,0x8aa,'progress_args'),(0x277,0x336,'episode_init'),(0x277,0xb72,'map_init'),(0x476,0x78,'progress_text'),(0,0x212,'zero_0212'),(0,0x3fe,'zero_03fe'),(0,0x52a,'zero_052a'),(0x4c7,0x8a0,'audio_id'),(0x476,0x5e,'progress_finish'),(0x11ee,0x2990,'crt_sample'),(0xfba,0x58,'sample_fba'),(0x768,0x10,'sample_768'),(0x83d,0x143c,'preloop_143c'),(0xbde,0x19a,'clock_init'),(0x83d,0x288c,'music_select_288c')]:
  addr=(load+seg)*16+ip;targets[addr]=name;u.mem_write(addr,b'\xcb')
 calls=[];observed=[]
 def hook(uc,address,size,user):
  if address not in targets:return
  op=targets[address];sp=uc.reg_read(UC_X86_REG_SP)
  def args(n):return struct.unpack('<'+'H'*n,bytes(uc.mem_read(ds*16+sp+4,n*2)))
  calls.append(op)
  if op=='intro':put(0x1c9c,bytes([intro_out]))
  elif op=='query':assert args(1)==(4,)
  elif op=='progress_args':assert args(3)==(0,0,0)
  elif op=='episode_init':assert args(1)==(episode,);put(0x626a,struct.pack('<H',episode))
  elif op=='map_init':assert word(0x3cd4)==0 and word(0x626c)==level
  elif op=='progress_text':observed.append(args(1)[0])
  elif op=='audio_id':assert args(1)==(65535,)
  elif op=='crt_sample':uc.reg_write(UC_X86_REG_AX,0xbeef)
  elif op=='sample_fba':uc.reg_write(UC_X86_REG_AX,0xface)
  elif op=='sample_768':uc.reg_write(UC_X86_REG_AX,0x1234)
  elif op=='preloop_143c':assert args(2)==(2,0)
  elif op=='music_select_288c':assert word(0x3cd4)==1 and bytes(uc.mem_read(ds*16+0x3cd1,1))==b'\0'
 u.hook_add(UC_HOOK_CODE,hook)
 for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 u.mem_write(ds*16+0xf000,struct.pack('<HHHH',0x100,0x5000,level,episode));u.emu_start(cs*16+0x95a,0x50100,count=2000)
 effective_flag=initial_flag if initial_flag else intro_out;effective_episode=0 if effective_flag else old_episode;change=effective_episode!=episode
 expected=(['intro'] if initial_flag==0 else [])+['progress_init','query','progress_args']+(['episode_init'] if change else [])+['map_init','progress_text','zero_0212','zero_03fe','zero_052a','audio_id','progress_finish','crt_sample','sample_fba','sample_768','preloop_143c','progress_text','clock_init','progress_text','music_select_288c','progress_text']
 assert calls==expected and observed==[0x1c9d,0x1cab,0x1cb9,0x1cc7]
 assert bytes(u.mem_read(ds*16+0x1c9c,1))==b'\0' and word(0x626a)==episode and word(0x626c)==level
 assert bytes(u.mem_read(ds*16+0x4192,2))==(b'\xa5\x5a' if mode else b'\0\0')
 assert [word(o) for o in (0x3cb2,0x3cb6,0x3cba)]==[0xbeef,0xface,0x1234]
 assert u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SS)==ds and u.reg_read(UC_X86_REG_SP)==0xf004 and u.reg_read(UC_X86_REG_BP)==0x1234
 cases.append(dict(load=load,initial_flag=initial_flag,intro_stub_flag=intro_out,old_episode=old_episode,episode=episode,level=level,mode=mode,episode_init_called=change,passed=True))
save('cases',cases)
s=dict(functions=[dict(name='game_start_orchestrator',start=0xdbea,end_exclusive=0xdcd0,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows))],cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='whole original game-start caller; all18 callees stubbed with explicit intro/episode mutation models and three return seeds; call order, arguments, local data writes, DS=SS and stack checked; no callee closure, no claim of natural out-of-domain episode/level values',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
