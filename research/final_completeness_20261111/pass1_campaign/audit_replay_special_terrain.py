"""IMAGE INVENTORY DECODER EMULATOR OUT: specialterrain dispatcher+six latch handlers+soundevent+bank selection. Original collision integration;only final text/screen/driver calls preserving RETF fixtures."""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={x['image_offset']:x for x in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);rows=[];functions=[];edges=[]
def save(n,rr):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
spec=[('special_terrain_dispatch',0x2250,0x2312),('terrain_ep1_level7',0x216e,0x2198),('terrain_ep1_level10_A',0x2198,0x21e7),('terrain_ep1_level10_B',0x21e8,0x2202),('terrain_ep3_level10',0x2202,0x221c),('terrain_ep2_level10',0x221c,0x2236),('terrain_ep3_level1',0x2236,0x2250),('sound_event42',0xea0,0xeb1),('sound_bank_selection',0x2830,0x288b)]
for name,a,e in spec:
 todo=[a];d={};cs=0x83d
 while todo:
  ip=todo.pop()
  if ip in d:continue
  assert a<=ip<e;p=cs*16+ip;i=Decoder(16,b[p:cs*16+e],ip=ip).decode();assert not i.is_invalid;d[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(function=name,source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(function=name,source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 rr=[]
 for ip,i in sorted(d.items()):
  p=cs*16+ip;raw=b[p:cs*16+i.next_ip];assert old[p]['bytes']==raw.hex();rr.append(dict(cs=cs,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rr);rows+=rr;functions.append(dict(name=name,start=cs*16+a,end_exclusive=cs*16+e,instructions=len(rr),instruction_bytes=sum(len(bytes.fromhex(x['bytes'])) for x in rr)))
save('CFG_edges',edges);allowed={x['image_offset'] for x in rows};deps=[]
for folder,name in [('sound_priority_replay','sound_priority_dispatch'),('player_movement_collision_replay','paired_cell_step')]:
 p=out.parent/folder/(name+'.csv');deps.append(p)
 for x in csv.DictReader(p.open(encoding='utf-8')):
  q=int(x['image_offset']);raw=bytes.fromhex(x['bytes']);assert b[q:q+len(raw)]==raw;allowed.add(q)
configs=[]
for ep,lev,kind,latch in itertools.product((0,1,2,3,4,65535),(0,5,6,7,8,9,10,65535,32767),(0,68,71,72,255),(0,1,255)):
 configs.append(dict(body='dispatch',episode=ep,level0=lev,kind=kind,latch=latch))
for name,ip,e in spec[1:7]:
 for latch in (0,1,255):configs.append(dict(body='handler',entry=ip,latch=latch))
for forced,bank,a,c in itertools.product((0,1),(0,2,32767,32768,65535),(0,255,256,65535),(-1,0,511)):
 configs.append(dict(body='bank',forced=forced,bank=bank,a=a,c=c))
configs.append(dict(body='sound'))
for ep,lev,k1,k2,latch in itertools.product((1,2,3),(0,6,8,9),(71,72),(71,72),(0,1)):
 configs.append(dict(body='collision',episode=ep,level0=lev,k1=k1,k2=k2,latch=latch))
# Stateful pairs verify one-shot latches, and the level9 71/72 toggle in sequence.
for ep,lev,seq in ((1,8,(71,71,72,72,71)),(1,6,(71,71)),(1,9,(71,71,72,72)),(2,9,(71,71)),(3,0,(71,71)),(3,9,(71,71))):configs.append(dict(body='sequence',episode=ep,level0=lev,kinds=seq,latch=0))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));templates={}
for load in (0x824,0x1000):
 raw=bytearray(b)
 for z in rel:struct.pack_into('<H',raw,int(z['image_offset']),(int(z['original_word'])+load)&65535)
 ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(raw)]=raw;templates[load]=bytes(ram)
s=lambda v:((v+32768)&65535)-32768;cases=[];callrows=[];writesrows=[];coverage=set()
for cfg in configs:
 for load,split in itertools.product((0x824,0x1000),(False,True)):
  ds=load+0x2771;ss=0x6000 if split else ds;db=ds*16;sp=0xf000;sl,sh=ss*16+sp-100,ss*16+sp+16;ram=bytearray(templates[load]);latch=cfg.get('latch',0);ram[db+0x414e]=0
  for off in (0x430a,0x430b,0x4198):ram[db+off]=latch
  ram[db+0x430c]=ram[db+0x430e]=0;ram[db+0x4154]=0;ram[db+0x4151]=0x71;struct.pack_into('<HH',ram,db+0x626a,cfg.get('episode',1),cfg.get('level0',0));ram[db+0xd00c:db+0xd20c]=bytes(512)
  for off,v in ((0x3cbc,cfg.get('bank',65535)),(0x3cbe,cfg.get('a',65535)),(0x3cc0,cfg.get('c',65535))):struct.pack_into('<H',ram,db+off,v&65535)
  if cfg['body']=='bank':ram[db+0x430e]=cfg['forced']
  for typ,kind in ((37,cfg.get('kind',0)),(38,cfg.get('k1',71)),(39,cfg.get('k2',72)),(40,71),(41,72)):
   ram[db+0xd30e+typ]=kind;ram[db+0xd00c+typ]=64 if kind in (71,72) else 0
  world=load+0x21fd;ca,cb=0x4000,0x4002;ram[world*16+ca:world*16+ca+4]=bytes((38,0,39,0))
  fixtures={0xd290+0x750:('text',4),0xbde0+0x18a:('screen',0),0x1560+0x16e:('driver',0)}
  for q in fixtures:ram[load*16+q]=0xcb
  expected=bytearray(ram);stores=[];calls=[];dispatches=[]
  def put(off,n,v):
   v&=(1<<(8*n))-1;expected[db+off:db+off+n]=v.to_bytes(n,'little');stores.append((db+off,n,v))
  def w(off):return struct.unpack_from('<H',expected,db+off)[0]
  def sound(code):calls.append(('sound',(code,0,2)))
  def text(off):calls.append(('text',struct.unpack_from('<HH',expected,db+off)))
  def bank():
   if expected[db+0x430e]:put(0x6278,2,6);put(0x627a,1,0);put(0x627b,1,0)
   else:
    put(0x6278,2,w(0x3cbc) if s(w(0x3cbc))>=0 else 2);put(0x627a,1,w(0x3cbe)&255 if s(w(0x3cbe))>=0 else 2);put(0x627b,1,w(0x3cc0)&255 if s(w(0x3cc0))>=0 else 7)
   calls.append(('driver',()))
  def handler(ip):
   if ip==0x21e8:
    if not expected[db+0x430b]:put(0x430b,1,1);text(0x103c)
   elif not expected[db+0x430a]:
    if ip==0x216e:sound(0x42);put(0x430a,1,1);put(0x430e,1,1);bank();calls.append(('screen',()));text(0xe62)
    elif ip==0x2198:
     sound(0x12)
     for off in (0x430a,0x430c,0x4154):put(off,1,1)
     put(0x4151,1,0)
     for off in (0xf74,0xfc8,0xffa):text(off)
    else:put(0x430a,1,1);text({0x2202:0x10b8,0x221c:0x11a2,0x2236:0x135a}[ip])
  def dispatch(kind,typ):
   dispatches.append(typ);ep=w(0x626a);lev=(w(0x626c)+1)&65535
   if ep==1:
    if lev==7 and kind==71:handler(0x216e)
    elif lev==9:
     if kind==71 and expected[db+0x4198]==0:put(0x4198,1,1);sound(0x44)
     elif kind==72 and expected[db+0x4198]!=0:put(0x4198,1,0);sound(0x44)
    elif lev==10 and kind in (71,72):handler(0x2198 if kind==71 else 0x21e8)
   elif ep==2 and lev==10 and kind==71:handler(0x221c)
   elif ep==3 and kind==71:
    if lev==1:handler(0x2236)
    elif lev==10:handler(0x2202)
  body=cfg['body'];stages=[]
  if body=='handler':handler(cfg['entry']);stages=[(cfg['entry'],())]
  elif body=='bank':bank();stages=[(0x2830,())]
  elif body=='sound':sound(0x42);stages=[(0xea0,())]
  elif body=='collision':
   dispatch(cfg['k1'],38);dispatch(cfg['k2'],39);stages=[('collision',(ca,world,cb,world,65535))]
  elif body=='sequence':
   for k in cfg['kinds']:typ=40 if k==71 else 41;dispatch(k,typ);stages.append((0x2250,(typ|0x4100,)))
  else:dispatch(cfg['kind'],37);stages=[(0x2250,(37|0x4100,))]
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));actualWrites=[];actualCalls=[];actualDispatch=[];done=[];lastframe=b''
  def code(e,a,n,data):
   if a==0x4e200:done.append(True);e.emu_stop();return
   p=a-load*16
   if p in fixtures:
    name,width=fixtures[p];rsp=e.reg_read(UC_X86_REG_SP);args=struct.unpack('<HH',bytes(e.mem_read(ss*16+rsp+4,4))) if width else ();actualCalls.append((name,args));assert actualCalls[-1]==calls[len(actualCalls)-1],(cfg,actualCalls[-1],calls);return
   if p==0xc2b0+0x3d6:
    rsp=e.reg_read(UC_X86_REG_SP);args=struct.unpack('<3H',bytes(e.mem_read(ss*16+rsp+4,6)));assert bytes(e.mem_read(db+0x414e,1))==b'\0';actualCalls.append(('sound',args));assert actualCalls[-1]==calls[len(actualCalls)-1],(cfg,actualCalls[-1],calls)
   if p==0x83d0+0x2250:
    rsp=e.reg_read(UC_X86_REG_SP);actualDispatch.append(bytes(e.mem_read(ss*16+rsp+4,1))[0])
   assert p in allowed,hex(p);coverage.add(p)
  def write(e,access,a,n,v,data):
   if not(sl<=a and a+n<=sh):actualWrites.append((a,n,v&((1<<(8*n))-1)))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  for ip,args in stages:
   cs=0x637 if ip=='collision' else 0x83d;ip=8 if ip=='collision' else ip;lastframe=struct.pack('<'+'H'*(2+len(args)),0x200,0x4e00,*args);u.mem_write(ss*16+sp,lastframe)
   for reg,v in ((UC_X86_REG_CS,load+cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,v)
   before=len(done);u.emu_start((load+cs)*16+ip,0x1fffff,count=20000);assert len(done)==before+1
   for reg,v in ((UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp+4),(UC_X86_REG_BP,0x1234)):
    assert u.reg_read(reg)==v,(cfg,reg,u.reg_read(reg),v)
   if body=='collision':assert u.reg_read(UC_X86_REG_AX)==65535 and u.reg_read(UC_X86_REG_SI)==0x2345 and u.reg_read(UC_X86_REG_DI)==0x3456
  assert actualWrites==stores and actualCalls==calls and actualDispatch==dispatches,(cfg,actualWrites,stores,actualCalls,calls,actualDispatch,dispatches)
  actual=bytes(u.mem_read(0,len(ram)));assert actual[:sl]==expected[:sl] and actual[sh:]==expected[sh:] and actual[ss*16+sp:ss*16+sp+len(lastframe)]==lastframe,(cfg,'RAM')
  cid=len(cases);cases.append(dict(case=cid,load=load,split_SS_DS=split,config=json.dumps(cfg),calls=len(calls),dispatches=len(dispatches),original_nonstack_stores=len(stores),latchA=expected[db+0x430a],latchB=expected[db+0x430b],toggle=expected[db+0x4198],freeze=expected[db+0x4154],status='PASS'))
  for j,(name,args) in enumerate(calls):callrows.append(dict(case=cid,index=j,name=name,args=json.dumps(args)))
  for j,(a,n,v) in enumerate(stores):writesrows.append(dict(case=cid,index=j,address=a,width=n,value=v))
save('cases',cases);save('calls',callrows);save('stores',writesrows);save('execution_coverage',[dict(image_offset=x['image_offset'],executed=x['image_offset'] in coverage) for x in rows]);summary=dict(functions=functions,cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,unexecuted_starts=sorted({x['image_offset'] for x in rows}-coverage),scope='Original dispatcher+six handlers+sound42+bankselect,original disabled sound andpairedcell integration. Text/screen/driver preserving RETF fixtures;not actual transition/UI/audio behavior. Entire2MiB except116controlstackB,exactstores/calls/frames;two loads,splitDS/SS.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in [image,inventory,image.parent/'relocations.csv',Path(__file__),*deps]]);(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
