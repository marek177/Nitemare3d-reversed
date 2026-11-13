"""IMAGE INVENTORY DECODER EMULATOR OUT: original pickup recordlookup,clear and15case dispatcher,plus pairedcell integration. Explicit HUD/weapon/specialitem/notification fixtures."""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={x['image_offset']:x for x in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);rows=[];functions=[];edges=[]
def save(n,rr):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
spec=[('pickup_record_find',0x6a8,0x701),('pickup_cell_clear',0x702,0x717),('pickup_apply',0x718,0x958)]
for name,a,e in spec:
 todo=[a];d={};cs=0xaea
 while todo:
  ip=todo.pop()
  if ip in d:continue
  assert a<=ip<e;p=cs*16+ip;i=Decoder(16,b[p:cs*16+e],ip=ip).decode();assert not i.is_invalid;d[ip]=i
  if i.flow_control==FlowControl.INDIRECT_BRANCH:
   assert ip==0x751
   for dst in struct.unpack_from('<15H',b,cs*16+0x756):todo.append(dst);edges.append(dict(function=name,source=ip,target=dst,kind='jump_table'))
  elif i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(function=name,source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH,FlowControl.INDIRECT_BRANCH):todo.append(i.next_ip);edges.append(dict(function=name,source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 rr=[]
 for ip,i in sorted(d.items()):
  p=cs*16+ip;raw=b[p:cs*16+i.next_ip];assert old[p]['bytes']==raw.hex();rr.append(dict(cs=cs,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rr);rows+=rr;functions.append(dict(name=name,start=cs*16+a,end_exclusive=cs*16+e,instructions=len(rr),instruction_bytes=sum(len(bytes.fromhex(x['bytes'])) for x in rr)))
save('CFG_edges',edges);allowed={x['image_offset'] for x in rows}
table=[dict(index=i,record_kind=47+i,target_cs=0xaea,target_ip=v,word_image=0xb5f6+2*i,original_hex=b[0xb5f6+2*i:0xb5f8+2*i].hex()) for i,v in enumerate(struct.unpack_from('<15H',b,0xb5f6))];save('pickup_jump_table',table);save('data_intervals',[dict(start=0xb5f6,end_exclusive=0xb614,length=30,type='CS-relative NEAR jump table,15WORDs indexed bykind47..61',status='PARTIAL',sha256=sha(b[0xb5f6:0xb614]))])
deps=[]
p=out.parent/'player_movement_collision_replay/paired_cell_step.csv';deps.append(p)
for x in csv.DictReader(p.open(encoding='utf-8')):
 q=int(x['image_offset']);raw=bytes.fromhex(x['bytes']);assert b[q:q+len(raw)]==raw;allowed.add(q)
configs=[]
for kind,sub,stat,reply in itertools.product(tuple(range(46,63)),(0,1,7,8,31,32,255),(0,99,100,127,128,255),(0,1,255)):
 # Return fixture matters only for kind57;other cases normalize its unused value.
 if kind!=57 and reply:continue
 configs.append(dict(body='pickup',kind=kind,sub=sub,stat=stat,reply=reply,mode='last'))
for body,mode,count in itertools.product(('lookup','pickup'),('first','last','offset_miss','segment_miss','type_miss'),(-1,0,1,3)):
 configs.append(dict(body=body,kind=47,sub=1,stat=0,reply=1,mode=mode,count=count))
for flags in (0,1,2,255):configs.append(dict(body='clear',flags=flags))
# Repeated calls exercise cleared-cell lookup rather than treating removal as a Boolean return.
for kind in (47,50,51,53,57,60,61):configs.append(dict(body='repeat',kind=kind,sub=1,stat=0,reply=1,mode='last'))
for kind,stat,flags,delta in itertools.product(range(47,62),(0,100,255),(4,6),(1,65535)):
 configs.append(dict(body='collision',kind=kind,sub=1,stat=stat,reply=1,mode='last',flagsObject=flags,delta=delta))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));templates={}
for load in (0x824,0x1000):
 raw=bytearray(b)
 for z in rel:struct.pack_into('<H',raw,int(z['image_offset']),(int(z['original_word'])+load)&65535)
 ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(raw)]=raw;templates[load]=bytes(ram)
s8=lambda v:((v+128)&255)-128;cases=[];callrows=[];writerows=[];coverage=set()
for cfg in configs:
 for load,split in itertools.product((0x824,0x1000),(False,True)):
  ds=load+0x2771;ss=0x6000 if split else ds;db=ds*16;sb=ss*16;sp=0xf000;sl,sh=sb+sp-128,sb+sp+24;ram=bytearray(templates[load]);world=load+0x21fd;wb=world*16;cell=0x4000;ram[wb+cell:wb+cell+2]=bytes((0,33));stat=cfg.get('stat',0);count=cfg.get('count',3);match=0 if cfg.get('mode')=='first' else max(0,count-1)
  for seg in set((ds,ss)):
   base=seg*16;struct.pack_into('<h',ram,base+0x6270,count);struct.pack_into('<I',ram,base+0x4182,0xffffff80);ram[base+0x4189:base+0x4196]=bytes([stat])*13;ram[base+0x41ae:base+0x41b2]=bytes([stat])*4
  for j in range(max(count,1)):
   off=6+28*j;rec=bytearray(28);rec[0]=33;rec[1]=cfg.get('sub',0);rec[5]=cfg.get('flags',255);rec[6]=cfg.get('kind',47);struct.pack_into('<HH',rec,12,cell+2,world)
   if j==match and cfg.get('mode') not in ('offset_miss',):struct.pack_into('<H',rec,12,cell)
   if cfg.get('mode')=='segment_miss':struct.pack_into('<H',rec,14,world+1)
   if cfg.get('mode')=='type_miss':rec[0]=34
   ram[wb+off:wb+off+28]=rec
  fixtures={0x83d0+0x5d2:('hud',1),0x83d0+0xcac:('weapon_prepare',1),0x83d0+0xba6:('weapon_apply',2),0x83d0+0x2804:('special_item',1),0x83d0+0x1a7e:('pickup_notify',1)}
  for q in fixtures:ram[load*16+q]=0xcb
  for seg in set((ds,ss)):
   ram[seg*16+0xd00c:seg*16+0xd20c]=bytes(512);ram[seg*16+0xd10c+33]=cfg.get('flagsObject',4)
  expected=bytearray(ram);stores=[];calls=[];modelDS=ds;found=None;outAX=None;outDX=None
  def put(a,n,v):
   v&=(1<<(8*n))-1;expected[a:a+n]=v.to_bytes(n,'little');stores.append((a,n,v))
  def get(a,n):return int.from_bytes(expected[a:a+n],'little')
  def lookup():
   global modelDS
   n=get(modelDS*16+0x6270,2);n=((n+32768)&65535)-32768
   if n<=0:return None
   for j in range(n):
    off=6+28*j
    if get(wb+off+12,2)==cell and get(wb+off+14,2)==world and expected[wb+off]==expected[wb+cell+1]:modelDS=ss;return off
   modelDS=ss;return None
  def clear(off):put(wb+cell+1,1,0);put(wb+off+5,1,expected[wb+off+5]&254)
  def pickup():
   global found
   off=lookup();found=off
   if off is None:return
   base=modelDS*16;k=expected[wb+off+6];sub=expected[wb+off+1];remove=1;event=None;bit=(1<<(sub&31))&255
   def add(o,n,v):put(base+o,n,get(base+o,n)+v)
   def flag(o):put(base+o,1,expected[base+o]|bit)
   if k==47:flag(0x4192);event=13
   elif k==48:flag(0x4193);event=14
   elif k==49:add(0x4182,4,200);event=4
   elif k==50:
    remove=int(s8(expected[base+0x418e])<99)
    if remove:add(0x418e,1,bit);event=11
   elif k in (51,52):
    remove=int(expected[base+0x4189]<100)
    if remove:
     add(0x4189,1,(20>>(sub&31)) if k==51 else 30)
     if k==52:add(0x4182,4,250)
     calls.append(('hud',(5,)));event=4
   elif k==53:
    put(base+0x4189,1,100);put(base+0x418c,1,100);add(0x4182,4,500);add(0x418a,1,1);calls.extend([('hud',(5,)),('hud',(8,)),('hud',(6,))]);event=4
   elif k==54:flag(0x4194);calls.extend([('weapon_prepare',(sub,)),('weapon_apply',(sub,1))]);event=12
   elif k==55:flag(0x4195);event=15
   elif k==56:
    remove=int(s8(expected[base+0x418d])<100)
    if remove:add(0x418d,1,20);event=10
   elif k==57:calls.append(('weapon_apply',(sub,0)));remove=cfg['reply']
   elif k in (58,59):
    field=0x41ae if k==58 else 0x41af;remove=int(expected[base+field]<100)
    if remove:add(field,1,20);event=19 if k==58 else 20
   elif k==60:flag(0x41b1)
   elif k==61:calls.append(('special_item',(sub,)))
   if event is not None:calls.append(('hud',(event,)))
   if remove:clear(off);calls.append(('pickup_notify',(k,)))
  body=cfg['body'];steps=2 if body=='repeat' else 1
  if body=='clear':clear(6);stages=[(0x702,(cell,world,6,world))]
  elif body=='collision':
   pickup();pickup();outAX=0 if cfg['flagsObject']&2 else cfg['delta'];stages=[('collision',(cell,world,cell,world,cfg['delta']))]
  elif body=='lookup':found=lookup();outAX=found or 0;outDX=world if found is not None else 0;stages=[(0x6a8,(cell,world))]
  else:
   stages=[]
   for _ in range(steps):pickup();stages.append((0x718,(cell,world)))
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));actualWrites=[];actualCalls=[];done=[];lastframe=b''
  def code(e,a,n,data):
   if a==0x4e200:done.append(True);e.emu_stop();return
   p=a-load*16
   if p in fixtures:
    name,count=fixtures[p];rsp=e.reg_read(UC_X86_REG_SP);args=struct.unpack('<'+'H'*count,bytes(e.mem_read(sb+rsp+4,2*count)));actualCalls.append((name,args));assert actualCalls[-1]==calls[len(actualCalls)-1],(cfg,actualCalls[-1],calls)
    if name=='weapon_apply':e.reg_write(UC_X86_REG_AX,(e.reg_read(UC_X86_REG_AX)&0xff00)|cfg['reply'])
    return
   assert p in allowed,hex(p);coverage.add(p)
  def write(e,access,a,n,v,data):
   if not(sl<=a and a+n<=sh):actualWrites.append((a,n,v&((1<<(8*n))-1)))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  for j,(ip,args) in enumerate(stages):
   cs=0x637 if ip=='collision' else 0xaea;ip=8 if ip=='collision' else ip
   lastframe=struct.pack('<'+'H'*(2+len(args)),0x200,0x4e00,*args);u.mem_write(sb+sp,lastframe)
   for reg,v in ((UC_X86_REG_CS,load+cs),(UC_X86_REG_DS,ds if j==0 else modelDS),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,v)
   before=len(done);u.emu_start((load+cs)*16+ip,0x1fffff,count=20000);assert len(done)==before+1
   for reg,v in ((UC_X86_REG_DS,modelDS),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)):assert u.reg_read(reg)==v,(cfg,reg,u.reg_read(reg),v)
  if body=='collision':assert u.reg_read(UC_X86_REG_AX)==outAX
  if body=='lookup':assert u.reg_read(UC_X86_REG_AX)==outAX and u.reg_read(UC_X86_REG_DX)==outDX
  assert actualWrites==stores and actualCalls==calls,(cfg,actualWrites,stores,actualCalls,calls)
  actual=bytes(u.mem_read(0,len(ram)));assert actual[:sl]==expected[:sl] and actual[sh:]==expected[sh:] and actual[sb+sp:sb+sp+len(lastframe)]==lastframe,(cfg,'RAM')
  cid=len(cases);cases.append(dict(case=cid,load=load,split_SS_DS=split,config=json.dumps(cfg),calls=len(calls),original_nonstack_stores=len(stores),returnDS=modelDS,lookup_offset=found if found is not None else '',cell_object_BYTE=expected[wb+cell+1],status='PASS'))
  for j,(name,args) in enumerate(calls):callrows.append(dict(case=cid,index=j,name=name,args=json.dumps(args)))
  for j,(a,n,v) in enumerate(stores):writerows.append(dict(case=cid,index=j,address=a,width=n,value=v))
save('cases',cases);save('calls',callrows);save('stores',writerows);save('execution_coverage',[dict(image_offset=x['image_offset'],executed=x['image_offset'] in coverage) for x in rows]);summary=dict(functions=functions,cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,unexecuted_starts=sorted({x['image_offset'] for x in rows}-coverage),scope='Original lookup+clear+15case pickup dispatcher+pairedcell integration;HUD/weapon/specialitem/notification preservingRETfixtures,weaponreply ALcontrolled. Entire2MiB except152controlstackB,exactstores/calls/frames;two loads,splitDS/SS. Synthetic validrecord domains,not fullgameplayeffects.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in [image,inventory,image.parent/'relocations.csv',Path(__file__),*deps]]);(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
