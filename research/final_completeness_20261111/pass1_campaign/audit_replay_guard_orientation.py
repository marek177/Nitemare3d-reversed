"""python audit_replay_guard_orientation.py IMAGE INVENTORY DECODER EMULATOR OUT
Original facing setter, relative-frame update and view octant; no substituted callees.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
defs=[('guard_facing_from_signed_vector',0x4c7,0xb0,0x129),('guard_relative_frame_update',0x4c7,0x12a,0x217),('actor_to_player_view_octant',0xaea,0xc0a,0xcc0)];functions=[];starts={};visited={}
for name,cs,start,end in defs:
 todo=[start];dec={};edges=[]
 while todo:
  ip=todo.pop()
  if ip in dec:continue
  assert start<=ip<end;i=Decoder(16,b[cs*16+ip:cs*16+end],ip=ip).decode();assert not i.is_invalid;dec[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 rows=[]
 for ip,i in sorted(dec.items()):
  pos=cs*16+ip;raw=b[pos:cs*16+i.next_ip];assert old[pos]['bytes']==raw.hex();rows.append(dict(cs=cs,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);save(name+'_cfg',edges);functions.append(dict(name=name,start=cs*16+start,end_exclusive=cs*16+end,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows)));starts[name]=set(cs*16+q for q in dec);visited[name]=set()
def signed(v):v&=65535;return v if v<32768 else v-65536
def absword(v):return abs(signed(v))&65535
def facing(dx,dy,previous):
 if dx==0:return 4 if dy>0 else 0 if dy<0 else previous
 if dx>0:return 3 if dy>0 else 1 if dy<0 else 2
 return 5 if dy>0 else 7 if dy<0 else 6
def view(dx,dy,flag):
 ax,ay=absword(dx),absword(dy)
 if flag:
  if ((ay*2)&65535)<ax:return 2 if dx>0 else 6
  if ((ax*2)&65535)<ay:return 4 if dy>0 else 0
  return (3 if dy>0 else 1) if dx>0 else (5 if dy>0 else 7)
 if dx<0:return (7 if ay>ax else 6) if dy<0 else (4 if ay>ax else 5)
 return (0 if ay>ax else 1) if dy<0 else (2 if ay<=ax else 3)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));runtimes={}
for load in (0x824,0x1000):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 runtimes[load]=bytes(raw)
cases=[]
def run(kind,load,dx,dy,flag=0,heading=5,mode=0,strategy=0,force=0,equal=0):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,runtimes[load]);ds=load+0x2771;seg=load+0x21fd;g=0x264e;a=6;world=bytearray([0x55]*0x573e);dg=bytearray([0x66]*0xe030);guard=bytearray(range(26));actor=bytearray(range(28));guard[11]=mode;guard[10]=strategy;guard[15]=flag;guard[17]=heading;struct.pack_into('<HH',actor,16,1000,2000);actor[4]=255 if heading&1 else 0;struct.pack_into('<HH',dg,0x4162,(1000+dx)&65535,(2000+dy)&65535)
 v=view(dx,dy,flag);relative=((4 if flag else 3)+heading-v)&7;guard[18]=relative if equal else relative^7;world[g:g+26]=guard;world[a:a+28]=actor;descriptor=0x7000;struct.pack_into('<H',dg,0x3d22+8*actor[4],descriptor)
 for row in range(3):
  for col in range(8):struct.pack_into('<H',dg,descriptor+4+16*row+2*col,0xa100+256*row+17*col)
 expected_w=bytearray(world);expected_d=bytes(dg)
 if kind=='facing':
  value=facing(dx,dy,heading);expected_w[g+17]=value;cs,ip=0x4c7,0xb0;args=[g,seg,dx&65535,dy&65535]
 elif kind=='view':value=v;cs,ip=0xaea,0xc0a;args=[flag|0xab00,a,seg]
 else:
  value=relative;cs,ip=0x4c7,0x12a;args=[g,seg,a,seg,force]
  if not equal or force&255:
   expected_w[g+18]=relative;row=1 if mode in (8,16,17) else 2 if mode==6 and strategy!=2 else 0;frame=0xa100+row*256+17*relative;struct.pack_into('<H',expected_w,g,frame);expected_w[a+3]=frame&255
 u.mem_write(seg*16,bytes(world));u.mem_write(ds*16,bytes(dg));frame=struct.pack('<'+'H'*(2+len(args)),0x100,0x5000,*args);u.mem_write(ds*16+0xf000,frame)
 for q,val in [(UC_X86_REG_CS,load+cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_AX,0xabcd),(UC_X86_REG_EFLAGS,2)]:u.reg_write(q,val)
 def hook(emu,address,size,data):
  if address==0x50100:return
  p=address-load*16
  for name,ps in starts.items():
   if p in ps:visited[name].add(p);return
  raise AssertionError(('unexpected',kind,hex(p)))
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start((load+cs)*16+ip,0x50100,count=1000)
 assert bytes(u.mem_read(seg*16,len(world)))==expected_w,(kind,load,dx,dy,flag,mode,strategy,heading,force,equal,'world')
 assert bytes(u.mem_read(ds*16,len(dg)))==expected_d and bytes(u.mem_read(ds*16+0xf000,len(frame)))==frame
 assert u.reg_read(UC_X86_REG_SP)==0xf004 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x2345 and u.reg_read(UC_X86_REG_DI)==0x3456 and u.reg_read(UC_X86_REG_DS)==u.reg_read(UC_X86_REG_SS)==ds
 if kind=='view':assert u.reg_read(UC_X86_REG_AL)==value,(dx,dy,flag,u.reg_read(UC_X86_REG_AL),value)
 cases.append(dict(kind=kind,load=load,dx=dx,dy=dy,flag_BYTE=flag,heading=heading,mode=mode,strategy=strategy,force_WORD=force,previous_relative_equal=equal,expected_value=value,status='PASS'))
for load,dx,dy in itertools.product((0x824,0x1000),(-32768,-1,0,1,32767),(-32768,-1,0,1,32767)):run('facing',load,dx,dy)
edges=(-32768,-32767,-16385,-16384,-16383,-2,-1,0,1,2,3,16383,16384,16385,32766,32767,8192)
for load,dx,dy,flag in itertools.product((0x824,0x1000),edges,edges,(0,1,2,255)):run('view',load,dx,dy,flag)
for load,flag,heading,mode,strategy,force,equal in itertools.product((0x824,0x1000),(0,255),range(8),(0,6,8,16,17,255),(0,2),(0,1,256),(0,1)):
 dx,dy=((200,0),(0,200),(-200,0),(0,-200),(200,200),(-200,200),(200,-200),(-200,-200))[heading];run('frame',load,dx,dy,flag,heading,mode,strategy,force,equal)
save('cases',cases);save('instruction_execution_coverage',[dict(function=n,image_offset=p,executed=p in visited[n]) for n in starts for p in sorted(starts[n])])
s=dict(functions=functions,cases=len(cases),by_kind={k:sum(x['kind']==k for x in cases) for k in ('facing','view','frame')},failures=0,runtime_tests=0,new_deep_verified_bytes=0,executed_instruction_starts=sum(len(x) for x in visited.values()),unexecuted_starts={n:sorted(starts[n]-visited[n]) for n in starts},scope='whole original3functions, frame updater uses original view helper; no stubs; signed16 differences/abs/twice overflow retained; full world/DGROUP/callerframe compared; DS=SS and valid headings0..7, synthetic nearDS descriptor banks; no natural descriptor producer/fullAI/Win16 parity',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
