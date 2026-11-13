"""IMAGE INVENTORY DECODER EMULATOR GAME OUT: original heading/trig,paired-cell collision andmovement/commit. Terrain/pickup/HUD preservingRETfixtures explicit;soundoriginaldisabled. Conditional NONCODE loads are not promotions."""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,game,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={x['image_offset']:x for x in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);rows=[];functions=[];edges=[]
def save(n,rr):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
for name,cs,a,e in [('paired_cell_step',0x637,8,0x117),('movement_resolve',0x637,0x118,0x2c6),('player_heading_prepare',0xc7d,0x68,0x127),('player_move_wrapper',0x637,0x5a4,0x5d2)]:
 todo=[a];d={}
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
save('CFG_edges',edges);allowed={x['image_offset'] for x in rows};depfiles=[]
for folder,name in [('pass1_trig','sin_instructions'),('pass1_trig','cos_instructions'),('guard_validator_replay','door_record_for_cell'),('guard_validator_replay','door_state_zero_or_four'),('sound_priority_replay','sound_priority_dispatch'),('player_position_commit_replay','player_near_geometry_cursors'),('player_position_commit_replay','player_far_actor_cursors'),('player_position_commit_replay','player_position_commit'),('player_position_commit_replay','terrain_kind_search'),('player_position_commit_replay','terrain_kind44_variant'),('player_position_commit_replay','selector8_dependency_path')]:
 p=out.parent/folder/(name+'.csv');depfiles.append(p)
 for x in csv.DictReader(p.open(encoding='utf-8')):
  pos=int(x['image_offset']);raw=bytes.fromhex(x['bytes']);assert b[pos:pos+len(raw)]==raw;allowed.add(pos)
truth=list(csv.DictReader((out.parent/'classification_producers_replay/value_flag_truth_table.csv').open()));TF={int(x['input_BYTE']):int(x['output_low7']) for x in truth if x['function']=='tile_flags_generate'};OF={int(x['input_BYTE']):int(x['output_low7']) for x in truth if x['function']=='occupancy_flags_generate'};assets={}
for ep in (1,2,3):
 p=game/('MAP.%d'%ep);raw=p.read_bytes();n=struct.unpack_from('<H',raw)[0];assert len(raw)==514+8192*n;assets[ep]=raw
configs=[]
for a in range(360):configs.append(dict(body='heading',angle=a))
for a in (-360,-1,360,719,720):configs.append(dict(body='heading',angle=a))
for priority,pad in itertools.product((0,41),(0,17)):configs.append(dict(body='heading',angle=-361,priority=priority,pad=pad))
for fa,fb in ((0,0),(4,0),(0,4),(8,0),(0,8),(8,8),(64,0),(0,64),(64,64),(4,64),(64,4),(8,64)):
 for oa,state,step in itertools.product(((0,0),(2,0),(0,2),(4,0),(0,4),(6,4),(4,6)),(0,1,4),(1,65535)):
  configs.append(dict(body='collision',fa=fa,fb=fb,oa=oa[0],ob=oa[1],doorstate=state,step=step))
configs.append(dict(body='collision',fa=8,fb=0,oa=0,ob=0,doorstate=0,step=1,missing=True))
for ep,data in assets.items():
 n=struct.unpack_from('<H',data)[0]
 for level in range(n):
  for side in ('W','E','N','S'):
   for k in range(1,63):configs.append(dict(body='border',episode=ep,level=level,side=side,k=k))
for a in range(360):configs.append(dict(body='resolve',angle=a,steps=8,toggle=0,profile='flat'))
for a,steps,toggle in itertools.product((0,89,90,91,179,180,269,270,359),(-1,0,1,64),(0,1)):configs.append(dict(body='resolve',angle=a,steps=steps,toggle=toggle,profile='flat'))
for a,toggle,profile in itertools.product((0,45,90,135,180,225,270,315),(0,1),('wallV','wallH','door0','door1','trigger','pickup','object','pickup_solid')):configs.append(dict(body='resolve',angle=a,steps=64,toggle=toggle,profile=profile))
for a,steps,freeze,profile in itertools.product((0,45,90,180,270),(0,1,64),(0,1),('flat','wallV','door0','pickup_solid')):configs.append(dict(body='wrapper',angle=a,steps=steps,toggle=0,freeze=freeze,profile=profile))
configs.append(dict(body='resolve',angle=90,steps=8,toggle=0,profile='tail',x=4068,y=4064))
for k in range(34,40):configs.append(dict(body='resolve',angle=0,steps=1,toggle=0,profile='asset',episode=3,level=2,x=k*64+32,y=91))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));templates={}
for load in (0x824,0x1000):
 raw=bytearray(b)
 for z in rel:struct.pack_into('<H',raw,int(z['image_offset']),(int(z['original_word'])+load)&65535)
 rr=bytearray(b'\xa5'*0x200000);rr[load*16:load*16+len(raw)]=raw;templates[load]=bytes(rr)
def s(v):return ((v+32768)&65535)-32768
def div0(a,d):return (abs(a)//d)*(-1 if a<0 else 1)
cases=[];callsCSV=[];readsCSV=[];nc=[];visited=set()
for c in configs:
 contexts=[(0x824,False)] if c['body']=='border' else list(itertools.product((0x824,0x1000),(False,True))) if c['body'] in ('heading','collision') else [(0x824,False),(0x1000,False)]
 for load,split in contexts:
  ds=load+0x2771;ss=0x6000 if split else ds;db=ds*16;sp=0xf000;sl,sh=ss*16+sp-160,ss*16+sp+24;ram=bytearray(templates[load]);worldseg=load+0x21fd;wb=worldseg*16;ep=c.get('episode',1);asset=assets[ep];kind=bytearray(asset[2:258]);objkind=asset[258:514];terrain=bytes(TF[k] for k in kind);objects=bytes(OF[k] for k in objkind);ram[wb+0x373e:wb+0x573e]=asset[514+8192*c.get('level',0):514+8192*(c.get('level',0)+1)] if c.get('profile')=='asset' or c['body']=='border' else bytes(8192)
  doors={};x,y=c.get('x',2080),c.get('y',2080)
  for seg in set((ds,ss)):
   ram[seg*16+0xd00c:seg*16+0xd10c]=terrain;ram[seg*16+0xd10c:seg*16+0xd20c]=objects;ram[seg*16+0xd30e:seg*16+0xd40e]=kind;ram[seg*16+0x414e]=0
  def celloff(tx,ty):return (0x373e+2*((ty<<6)+tx))&65535
  def stamp(tx,ty,t,o):
   off=celloff(tx,ty);ram[wb+off]=t;ram[wb+((off+1)&65535)]=o;return off
  if c['body'] in ('heading','resolve','wrapper') and c.get('profile','flat')!='asset':
   for seg in set((ds,ss)):
    ram[seg*16+0xd00c:seg*16+0xd20c]=bytes(512)
    for typ,f in ((17,4),(18,8),(19,64)):ram[seg*16+0xd00c+typ]=f
    for typ,f in ((33,4),(34,2),(35,6)):ram[seg*16+0xd10c+typ]=f
   profile=c.get('profile','flat')
   if profile=='wallV':
    for ty in range(64):stamp(33,ty,17,0)
   elif profile=='wallH':
    for tx in range(64):stamp(tx,31,17,0)
   elif profile in ('door0','door1'):doors[stamp(32,31,18,0)]=int(profile[-1])
   elif profile=='trigger':stamp(32,31,19,0)
   elif profile in ('pickup','object','pickup_solid'):stamp(32,31,0,{'pickup':33,'object':34,'pickup_solid':35}[profile])
  if c['body']=='collision':
   ca,cb=stamp(32,31,17,33),stamp(33,31,18,34)
   for seg in set((ds,ss)):
    ram[seg*16+0xd00c:seg*16+0xd20c]=bytes(512);ram[seg*16+0xd00c+17]=c['fa'];ram[seg*16+0xd00c+18]=c['fb'];ram[seg*16+0xd10c+33]=c['oa'];ram[seg*16+0xd10c+34]=c['ob']
   if not c.get('missing'):
    if c['fa']&8:doors[ca]=c['doorstate']
    if c['fb']&8:doors[cb]=c['doorstate']
  elif c['body']=='border':
   k=c['k'];side=c['side'];tx,ty=(0,k) if side=='W' else (63,k) if side=='E' else (k,0) if side=='N' else (k,63);ca=cb=celloff(tx,ty)
  struct.pack_into('<H',ram,wb,len(doors))
  for j,(off,state) in enumerate(doors.items()):struct.pack_into('<HHH',ram,wb+0x3076+18*j+4,off,worldseg,state)
  for off in (0x57fa,0x57fc,0x57fe,0x5800,0x4166,0x4168,0x416a,0x416c,0x416e,0x4170,0xd514):struct.pack_into('<H',ram,db+off,0)
  struct.pack_into('<hh',ram,db+0x4162,x,y);struct.pack_into('<hh',ram,db+0x415e,x>>6,y>>6);struct.pack_into('<H',ram,db+0x2564,0x8000);ram[0x80000:0x90000]=b'\x77'*65536;ram[db+0x4154]=c.get('freeze',0);struct.pack_into('<HH',ram,db+0x626a,ep,0);struct.pack_into('<H',ram,db+0x12a,ep);ram[db+0x2650]=next(i for i,k in enumerate(kind) if k==68);ram[db+0x4188]=0x5a;ram[db+0x17e6]=c.get('priority',0);ram[db+0x17e7]=c.get('pad',0)
  trigger=(load+0x83d)*16+0x2250;pickup=(load+0xaea)*16+0x718;hud=(load+0x83d)*16+0x5d2
  for a in (trigger,pickup,hud):ram[a]=0xcb
  expected=bytearray(ram);stores=[];modelDS=ds;wantCells=[];wantEffects=[];wantReads=[];fatal=False;result=None;cid=len(cases)
  def put(a,n,v):
   v&=(1<<(8*n))-1;expected[a:a+n]=v.to_bytes(n,'little')
   if not(sl<=a and a+n<=sh):stores.append((a,n,v))
  def w(off):return struct.unpack_from('<H',expected,db+off)[0]
  def rw(a):return struct.unpack_from('<H',expected,a)[0]
  def heading(a):
   angle=s(a);put(db+0x4156,2,angle)
   if angle<0:angle=s(angle+360);put(db+0x4156,2,angle)
   if angle>=360:angle=s(angle-360);put(db+0x4156,2,angle)
   q=div0(angle,45);put(db+0x4158,2,q);put(db+0x415c,2,((1<<(q&31))&65535)&0x99);q2=div0(s(2*angle),45)&65535;q2=(q2&0xff00)|((q2+1)&255);put(db+0x415a,2,(q2&14)>>1)
   def lookup(base,index):return s(rw(db+((base+2*index)&65535)))
   sn=lookup(0x17e8,angle) if angle<90 else lookup(0x17e8,180-angle) if angle<180 else s(-lookup(0x17e8,angle-180)) if angle<270 else s(-lookup(0x17e8,360-angle));co=lookup(0x189e,angle) if angle<90 else s(-lookup(0x189e,180-angle)) if angle<180 else s(-lookup(0x189e,angle-180)) if angle<270 else lookup(0x189e,360-angle);put(db+0x41b2,2,sn);put(db+0x41b4,2,co);aa=s(-sn) if sn<0 else sn;bb=s(-co) if co<0 else co
   primary=bb<aa;put(db+0x4172,2,int(primary));put(db+0x4174,2,2*(bb if primary else aa)-(aa if primary else bb));put(db+0x4176,2,2*(bb if primary else aa));put(db+0x4178,2,2*((bb-aa) if primary else (aa-bb)))
  def collide(a,b2,step):
   global modelDS,fatal
   oldDS=modelDS;t0=expected[wb+a];t1=expected[wb+b2];f0=expected[oldDS*16+0xd00c+t0];f1=expected[oldDS*16+0xd00c+t1];wantReads.extend([('terrain_A',wb+a,t0),('terrain_B',wb+b2,t1)]);res=step
   if f0&4 or f1&4:wantEffects.append(('sound',(1,0,0)));res=0
   else:
    for off,flag in ((a,f0),(b2,f1)):
     if flag&8:
      modelDS=ss
      if off not in doors:fatal=True;res=None;break
      if doors[off] not in (0,4):wantEffects.append(('sound',(1,0,0)));res=0;break
    if res is not None and res!=0:
     for off,typ,flag in ((a,t0,f0),(b2,t1,f1)):
      if flag&64:wantEffects.append(('trigger',(typ,)))
     o0=expected[wb+((a+1)&65535)];o1=expected[wb+((b2+1)&65535)];g0=expected[modelDS*16+0xd10c+o0];g1=expected[modelDS*16+0xd10c+o1];wantReads.extend([('object_A',wb+((a+1)&65535),o0),('object_B',wb+((b2+1)&65535),o1)])
     for off,flag in ((a,g0),(b2,g1)):
      if flag&4:wantEffects.append(('pickup',(off,worldseg)))
     if g0&2 or g1&2:res=0
   wantCells.append(((a,worldseg,b2,worldseg,step&65535),res,modelDS));return res
  def probe(axis,xx,yy,sx,sy):
   if axis=='X':return celloff(s(xx+28*sx)>>6,s(yy-27*sy)>>6),celloff(s(xx+28*sx)>>6,s(yy+27*sy)>>6)
   return celloff(s(xx-27*sx)>>6,s(yy+28*sy)>>6),celloff(s(xx+27*sx)>>6,s(yy+28*sy)>>6)
  def resolve(angle,toggle,steps,outx,outy):
   put(outx,2,x);put(outy,2,y);sx=1 if s(angle)<180 else -1;sy=1 if 90<s(angle)<270 else -1;major=expected[db+0x4172];major=int(major<1) if toggle&255 else major
   for j in range(max(0,s(steps))):
    xx,yy=s(rw(outx)),s(rw(outy));axis='X' if major else 'Y';aa,bb=probe(axis,xx,yy,sx,sy);delta=collide(aa,bb,sx if axis=='X' else sy)
    if fatal:break
    p=outx if axis=='X' else outy;put(p,2,s(rw(p))+delta)
    err=s(w(0x4174));put(db+0x4174,2,err+s(w(0x4176 if err<0 else 0x4178)))
    if err>=0:
     xx,yy=s(rw(outx)),s(rw(outy));axis='Y' if major else 'X';aa,bb=probe(axis,xx,yy,sx,sy);delta=collide(aa,bb,sy if axis=='Y' else sx)
     if fatal:break
     p=outx if axis=='X' else outy;put(p,2,s(rw(p))+delta)
  stages=[]
  if c['body']=='heading':heading(c['angle']);stages=[(0xc7d,0x68,(c['angle']&65535,))]
  elif c['body'] in ('collision','border'):
   step=c.get('step',65535 if c.get('side') in ('W','N') else 1);result=collide(ca,cb,step);stages=[(0x637,8,(ca,worldseg,cb,worldseg,step&65535))]
  else:
   heading(c['angle']);stages=[(0xc7d,0x68,(c['angle']&65535,))]
   if c['body']=='resolve':resolve(c['angle'],c['toggle'],c['steps'],db+0x9000,db+0x9002);stages.append((0x637,0x118,(c['angle']&65535,c['toggle'],c['steps']&65535,0x9000,0x9002)))
   else:
    if not c['freeze']:
     ox,oy=ss*16+sp-6,ss*16+sp-4;resolve(c['angle'],c['toggle'],c['steps'],ox,oy)
     if not fatal:
      nx,ny=s(rw(ox)),s(rw(oy));put(0x80000+(((x>>6)<<6)+(y>>6)&65535),1,0);put(db+0x4162,2,nx);put(db+0x4164,2,ny);tx,ty=nx>>6,ny>>6
      if (tx,ty)!=(x>>6,y>>6):put(db+0x415e,2,tx);put(db+0x4160,2,ty);wantEffects.append(('hud',(22,)))
      off=celloff(tx,ty);put(db+0x417c,2,off);put(db+0x417e,2,worldseg);t=expected[wb+off]
      if expected[db+0xd30e+t]==68:
       v=(t-expected[db+0x2650])&65535
       if v!=65535:put(db+0x4188,1,v&255)
    stages.append((0x637,0x5a4,(c['angle']&65535,c['toggle'],c['steps']&65535)))
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));actualWrites=[];seenCells=[];seenEffects=[];seenReads=[];pendingCell=[];pendingLoad=[];done=[];lastframe=None
  readPC={0x6370+0x17:('terrain_A',0x6370+0x1a,'DI'),0x6370+0x26:('terrain_B',0x6370+0x29,'SI'),0x6370+0xb1:('object_A',0x6370+0xb5,'DI'),0x6370+0xc1:('object_B',0x6370+0xc5,'SI')};post={v[1] for v in readPC.values()}
  def code(e,a,n,data):
   if a==0x4e200:done.append('return');e.emu_stop();return
   if a==(load+0xfba)*16+0xc:done.append('fatal');e.emu_stop();return
   if a in (trigger,pickup,hud):
    name='trigger' if a==trigger else 'pickup' if a==pickup else 'hud';rsp=e.reg_read(UC_X86_REG_SP);args=struct.unpack('<'+'H'*(2 if name=='pickup' else 1),bytes(e.mem_read(ss*16+rsp+4,4 if name=='pickup' else 2)));args=(args[0]&255,) if name=='trigger' else args;seenEffects.append((name,args));assert seenEffects[-1]==wantEffects[len(seenEffects)-1];return
   p=a-load*16
   if p==0xc2b0+0x3d6:
    rsp=e.reg_read(UC_X86_REG_SP);args=struct.unpack('<3H',bytes(e.mem_read(ss*16+rsp+4,6)));assert bytes(e.mem_read(e.reg_read(UC_X86_REG_DS)*16+0x414e,1))==b'\0';seenEffects.append(('sound',args));assert seenEffects[-1]==wantEffects[len(seenEffects)-1]
   if p==0x6378:
    rsp=e.reg_read(UC_X86_REG_SP);args=struct.unpack('<5H',bytes(e.mem_read(ss*16+rsp+4,10)));wcall=wantCells[len(seenCells)];assert args==wcall[0],(c,args,wcall);seenCells.append(wcall);pendingCell.append((wcall,rsp))
   if p in (0x6370+0x102,0x6370+0x116):
    wcall,rsp=pendingCell.pop();assert e.reg_read(UC_X86_REG_AX)==(wcall[1]&65535) and e.reg_read(UC_X86_REG_SP)==rsp and e.reg_read(UC_X86_REG_DS)==wcall[2]
   if p in readPC:
    kindname,npc,reg=readPC[p];off=e.reg_read(UC_X86_REG_DI if reg=='DI' else UC_X86_REG_SI);off=(off+int(kindname.startswith('object')))&65535;addr=e.reg_read(UC_X86_REG_ES)*16+off;v=bytes(e.mem_read(addr,1))[0];seenReads.append((kindname,addr,v));pendingLoad.append((npc,addr,v,'BL',p))
   if p==0xcfc2:
    si=e.reg_read(UC_X86_REG_SI);addr=e.reg_read(UC_X86_REG_DS)*16+((si+0x17e8)&65535);v=struct.unpack('<H',bytes(e.mem_read(addr,2)))[0];pendingLoad.append((0xcfc6,addr,v,'AX',p))
   if pendingLoad and p==pendingLoad[-1][0]:
    npc,addr,v,reg,pc=pendingLoad.pop();actual=e.reg_read(UC_X86_REG_AX) if reg=='AX' else e.reg_read(UC_X86_REG_BX)&255;assert actual==v
    lo,hi=addr-load*16,addr-load*16+(2 if reg=='AX' else 1)
    targets=[q for q in (0x2770e,0x2770f,0x28ef7) if lo<=q<hi]
    for q in targets:nc.append(dict(case=cid,body=c['body'],load=load,split_SS_DS=split,target_image=q,instruction_image=pc,after_instruction_image=npc,linear_address=addr,original_load_start=lo,width=2 if reg=='AX' else 1,loaded_value=v,natural_runtime=False,status='CLASSIFIED ONLY' if q==0x28ef7 else 'UNKNOWN',scope='Controlled input/domain oropen-flat-border read;intendedtype/naturalreachability unproven'))
   assert p in allowed,hex(p);visited.add(p)
  def write(e,access,a,n,v,data):
   if not(sl<=a and a+n<=sh):actualWrites.append((a,n,v&((1<<(8*n))-1)))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  for cs,ip,args in stages:
   frame=struct.pack('<'+'H'*(2+len(args)),0x200,0x4e00,*args);u.mem_write(ss*16+sp,frame);lastframe=frame
   for reg,v in ((UC_X86_REG_CS,load+cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,v)
   before=len(done);u.emu_start((load+cs)*16+ip,0x1fffff,count=50000);assert len(done)==before+1
   if done[-1]=='fatal':break
  assert done[-1]==('fatal' if fatal else 'return') and actualWrites==stores and seenCells==wantCells and seenEffects==wantEffects and seenReads==wantReads and not pendingLoad,(c,actualWrites,stores,seenCells,wantCells,seenEffects,wantEffects,seenReads,wantReads)
  if not fatal:
   if result is not None:assert u.reg_read(UC_X86_REG_AX)==(result&65535)
   for reg,v in ((UC_X86_REG_DS,modelDS),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)):assert u.reg_read(reg)==v,(c,reg,u.reg_read(reg),v)
  actual=bytes(u.mem_read(0,len(ram)));assert actual[:sl]==expected[:sl] and actual[sh:]==expected[sh:] and actual[ss*16+sp:ss*16+sp+len(lastframe)]==lastframe
  for j,z in enumerate(seenCells):callsCSV.append(dict(case=cid,index=j,args=json.dumps(z[0]),return_step=z[1]))
  for j,z in enumerate(seenReads):readsCSV.append(dict(case=cid,index=j,role=z[0],linear_address=z[1],value=z[2]))
  cases.append(dict(case=cid,load=load,split_SS_DS=split,config=json.dumps(c),stop=done[-1],helper_calls=len(seenCells),callbacks=len([z for z in seenEffects if z[0] in ('trigger','pickup','hud')]),result_step=result if result is not None else '',fineX=s(rw(db+0x4162)),fineY=s(rw(db+0x4164)),outX=s(rw(db+0x9000)) if c['body']=='resolve' else '',outY=s(rw(db+0x9002)) if c['body']=='resolve' else '',original_nonstack_stores=len(stores),status='PASS'))
save('cases',cases);save('collision_calls',callsCSV);save('cell_reads',readsCSV);save('conditional_NONCODE_loads',nc);save('execution_coverage',[dict(image_offset=x['image_offset'],executed=x['image_offset'] in visited) for x in rows]);summary=dict(functions=functions,cases=len(cases),failures=0,fatal_entry_stops=sum(x['stop']=='fatal' for x in cases),runtime_tests=0,new_deep_verified_bytes=0,conditional_NONCODE_loads=len(nc),conditional_targets=sorted(set(x['target_image'] for x in nc)),unexecuted_starts=sorted({x['image_offset'] for x in rows}-visited),scope='Original fourbodies+originaltrig/door/sounddisabled/commit/cursor/kindhelpers. Trigger/pickup/HUD preservingRETfixtures explicit;asset-border probes execute nofixtures. Full2MiB except184controlstackB,exact originalstores/calls/loads andframes. No naturalmargin/transition/angle-domain proof;conditionalNONCODE bytes not promoted.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in [image,inventory,image.parent/'relocations.csv',Path(__file__),*depfiles,out.parent/'classification_producers_replay/value_flag_truth_table.csv',out.parent/'pass1_xms_move_request/noncode_intervals.csv',*[game/('MAP.%d'%ep) for ep in (1,2,3)]]]);(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
