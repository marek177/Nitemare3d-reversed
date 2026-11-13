"""IMAGE INVENTORY DECODER EMULATOR OUT: two event-sound wrappers,original bearing/pan/angle/RNG,and frame-state writer. Only sound dispatch is a preserving RETF fixture."""
import bisect,csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={x['image_offset']:x for x in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);allrows=[];functions=[];tables=[];edges=[]
def save(n,rows):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
spec=[('death_sound_event',0x83d,0x1922,0x19e4,0x1944),('state7_sound_event',0x83d,0x1ae4,0x1bd0,0x1b06),('source_pan_sector',0x4c7,0x44,0xb0,None),('source_relative_bearing',0x4c7,6,0x43,None),('apply_frame_state',0x4c7,0x868,0x8a0,None)]
for name,cs,a,e,tp in spec:
 todo=[a];d={};targets=struct.unpack_from('<24H',b,cs*16+tp) if tp else []
 while todo:
  ip=todo.pop()
  if ip in d:continue
  assert a<=ip<e and not(tp is not None and tp<=ip<tp+48);p=cs*16+ip;i=Decoder(16,b[p:cs*16+e],ip=ip).decode();assert not i.is_invalid;d[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(function=name,source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control==FlowControl.INDIRECT_BRANCH:
   assert tp is not None
   for target in sorted(set(targets)):todo.append(target);edges.append(dict(function=name,source=ip,target=target,kind='table'))
  elif i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(function=name,source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 rows=[]
 for ip,i in sorted(d.items()):
  p=cs*16+ip;raw=b[p:cs*16+i.next_ip];assert old[p]['bytes']==raw.hex();rows.append(dict(cs=cs,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);allrows+=rows;functions.append(dict(name=name,start=cs*16+a,end_exclusive=cs*16+e,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(x['bytes'])) for x in rows)))
 tables.extend(dict(function=name,type=j+8,start=cs*16+tp+2*j,end_exclusive=cs*16+tp+2*j+2,target_cs=cs,target_ip=t) for j,t in enumerate(targets))
save('CFG_edges',edges);save('event_tables',tables);allowed={x['image_offset'] for x in allrows};deps=[]
for folder,name in [('angle_lookup','instructions'),('pass1_rng','game_rand_wrapper'),('pass1_rng','crt_rand_lcg'),('pass1_rng','compiler_mul32_low')]:
 p=out.parent/folder/(name+'.csv');deps.append(p)
 for x in csv.DictReader(p.open(encoding='utf-8')):
  pos=int(x['image_offset']);raw=bytes.fromhex(x['bytes']);assert b[pos:pos+len(raw)]==raw;allowed.add(pos)
T=list(struct.unpack_from('<91h',b,0x29064));assert T==sorted(T)
def signed(v):return ((v+32768)&65535)-32768
def bearing(x,y,facing):
 idx=90 if y==0 else bisect.bisect_left(T,abs(x*1024)//abs(y));angle=idx+180 if x<0 and y>=0 else 360-idx if x<0 else 180-idx if y>0 else idx;rel=signed(angle-facing)
 if rel>180:rel=signed(rel-360)
 elif signed(facing-angle)>180:rel=signed(rel+360)
 return rel
D={8:35,9:8,10:7,11:36,12:4,13:19,14:14,18:7,19:7,20:35,23:70,24:70,26:74,27:2,28:2,29:9,30:70,31:70};H={8:34,11:59,12:20,13:21,14:16,17:6,18:63,19:60,22:18,23:72,24:71,26:73,27:13,28:13,29:56,30:61,31:61}
configs=[]
for body in ('death','state7'):
 for typ in range(256):configs.append(dict(body=body,type=typ,seed=1,x=17,y=-31,facing=90))
 for typ,seed,x,y,facing in itertools.product((9,10,15,16),(0,0xffff,0xffffffff),(0,1,-1),(0,1,-1),(0,180)):
  configs.append(dict(body=body,type=typ,seed=seed,x=x,y=y,facing=facing))
for x,y,facing in itertools.product((-32768,-1,0,1,32767),(-32768,-1,0,1,32767),(0,35,36,90,144,145,179,180,181,215,216,270,324,325,359)):configs.append(dict(body='pan',x=x,y=y,facing=facing))
for x,y,facing in itertools.product((-32768,-1,0,1,32767),(-1,0,1),(0,180,359,0x7fff,0x8000,0xffff)):configs.append(dict(body='bearing',x=x,y=y,facing=facing))
for high,low,mlo,mhi in itertools.product((0,1,127,128,255),(0,1,255),(0,18,0x80ff),(0,9,0xffff)):configs.append(dict(body='frame',frame=(high<<8)|low,mlo=mlo,mhi=mhi))
for high in range(256):configs.append(dict(body='frame',frame=(high<<8)|0x34,mlo=0x1234,mhi=0x5678))
relocations=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];events=[];visited=set();Aoff,Aseg,Boff,Bseg=0x100,0x7000,0x200,0x7200;A=Aseg*16+Aoff;B=Bseg*16+Boff
for load,split,c in itertools.product((0x824,0x1000),(False,True),configs):
 raw=bytearray(b)
 for r in relocations:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 ds=load+0x2771;ss=0x6000 if split else ds;base=ds*16;sp=0xf000;sl,sh=ss*16+sp-160,ss*16+sp+24;ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(raw)]=raw;ram[A:A+26]=bytes(26);ram[B:B+28]=bytes(28);ram[B+6]=c.get('type',0);struct.pack_into('<hh',ram,B+0x10,c.get('x',0),c.get('y',0));struct.pack_into('<hh',ram,base+0x4162,0,0);struct.pack_into('<H',ram,base+0x4156,c.get('facing',0));struct.pack_into('<I',ram,base+0x24b8,c.get('seed',0));args=(Aoff,Aseg,Boff,Bseg)
 if c['body']=='frame':args+=(c['frame'],c['mlo'],c['mhi'])
 if c['body']=='bearing':args=(c['x']&65535,c['y']&65535)
 frame=struct.pack('<'+'H'*(2+len(args)),0x200,0x4e00,*args);ram[ss*16+sp:ss*16+sp+len(frame)]=frame;sound=(load+0xc2b)*16+0x3d6;ram[sound]=0xcb;expected=bytearray(ram);stores=[];want_calls=[];state=c.get('seed',0);rng_count=0
 def put(p,n,v):expected[p:p+n]=v.to_bytes(n,'little');stores.append((p,n,v))
 if c['body'] in ('death','state7','pan','bearing'):
  rel=bearing(c['x'],c['y'],c['facing']);pan=1 if 35<rel<145 else 2 if -145<rel<-35 else 0;result=rel&65535 if c['body']=='bearing' else pan
 if c['body'] in ('death','state7'):
  typ=c['type'];rng_count=int(typ in ((15,16) if c['body']=='death' else (9,10,15,16)))
  if rng_count:
   state=(state*214013+2531011)&0xffffffff;value=(state>>16)&32767;put(base+0x24b8,2,state&65535);put(base+0x24ba,2,state>>16)
   sid=11+value%3 if c['body']=='death' else 56+value%3 if typ in (9,10) else 54+value%2
  else:sid=(D if c['body']=='death' else H).get(typ,0)
  want_calls=[(sid,pan,2)];result=pan # preserving sound fixture leaves incoming AX direction unchanged
 elif c['body']=='frame':
  f=c['frame'];put(A,2,f);put(B+3,1,f&255);put(A+6,2,((f>>8)-1)&65535);put(A+0xc,1,c['mhi']&255);put(A+0xb,1,c['mlo']&255);result=(0xff00 if f>>8==0 else 0)|(c['mlo']&255)
 entry={'death':(0x83d,0x1922),'state7':(0x83d,0x1ae4),'pan':(0x4c7,0x44),'bearing':(0x4c7,6),'frame':(0x4c7,0x868)}[c['body']];u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));writes=[];calls=[];rng=[];stops=[]
 def code(e,a,n,data):
  if a==0x4e200:stops.append(True);e.emu_stop();return
  if a==sound:
   rsp=e.reg_read(UC_X86_REG_SP);v=struct.unpack('<3H',bytes(e.mem_read(ss*16+rsp+4,6)));calls.append(v);assert calls==want_calls;return
  if a==(load+0xfba)*16+0x1a0:rng.append(True)
  pos=a-load*16;assert pos in allowed,hex(pos);visited.add(pos)
 def write(e,access,a,n,v,data):
  if not(sl<=a and a+n<=sh):writes.append((a,n,v&((1<<(8*n))-1)))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 for reg,v in ((UC_X86_REG_CS,load+entry[0]),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,v)
 u.emu_start((load+entry[0])*16+entry[1],0x1fffff,count=3000);assert stops and calls==want_calls and len(rng)==rng_count and writes==stores,(c,calls,want_calls,writes,stores)
 assert u.reg_read(UC_X86_REG_AX)==result,(c,hex(u.reg_read(UC_X86_REG_AX)),hex(result))
 for reg,v in ((UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)):assert u.reg_read(reg)==v
 actual=bytes(u.mem_read(0,len(ram)));assert actual[:sl]==expected[:sl] and actual[sh:]==expected[sh:] and actual[ss*16+sp:ss*16+sp+len(frame)]==frame
 cid=len(cases)
 for sid,pan,priority in calls:events.append(dict(case=cid,sound_ID=sid,pan=pan,priority=priority,RNG_calls=rng_count,state_after=state))
 cases.append(dict(case=cid,load=load,split_SS_DS=split,config=json.dumps(c),result=result,nonstack_stores=len(writes),RNG_calls=rng_count,status='PASS'))
save('cases',cases);save('sound_arguments',events);save('execution_coverage',[dict(image_offset=x['image_offset'],executed=x['image_offset'] in visited) for x in allrows]);s=dict(functions=functions,tables=[dict(start=0x9d14,end_exclusive=0x9d44,sha256=sha(b[0x9d14:0x9d44])),dict(start=0x9ed6,end_exclusive=0x9f06,sha256=sha(b[0x9ed6:0x9f06]))],cases=len(cases),case_kinds={k:sum(json.loads(x['config'])['body']==k for x in cases) for k in ('death','state7','pan','bearing','frame')},failures=0,runtime_tests=0,new_deep_verified_bytes=0,unexecuted_starts=sorted({x['image_offset'] for x in allrows}-visited),scope='Original event wrappers/direction/relative-angle/angle/RNG/mul,one preserving sound-dispatch RETF fixture; frame writer nofixture. Full2MiB except184 controlstackB,exact ordered writes and frames. No actual sound output/natural record/angle domain proof.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in [image,inventory,image.parent/'relocations.csv',Path(__file__),*deps]]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
