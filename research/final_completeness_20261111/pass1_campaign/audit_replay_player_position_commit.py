"""IMAGE INVENTORY DECODER EMULATOR OUT: original player-position commit/reindex,near/far ordered cursors andkind44 lookup/search. Original actionselector8 path;only lateHUD preservingRETfixture. Conditional UNKNOWN-tail loads remain UNKNOWN."""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={x['image_offset']:x for x in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);functions=[];rows=[];edges=[]
def save(n,rr):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rr[0]));w.writeheader();w.writerows(rr)
spec=[('player_near_geometry_cursors',0x637,0x2c6,0x3fd),('player_far_actor_cursors',0x637,0x3fe,0x4b4),('player_position_commit',0x637,0x51c,0x5a3),('player_position_reindex',0x637,0x5d2,0x5fb),('terrain_kind_search',0xf7,4,0x4d),('terrain_kind44_variant',0xf7,0x176,0x1b5)]
for name,cs,a,e in spec:
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
save('CFG_edges',edges);allowed={x['image_offset'] for x in rows};path=[]
for ip in (0x143c,0x1440,0x1441,0x1442,0x1446,0x1449,0x144c,0x1450,0x1452,0x1453,0x16fa,0x16fe,0x1702,0x1705,0x1709,0x170f,0x180b,0x180e,0x1811,0x1812,0x1813,0x1814):
 p=0x83d0+ip;x=old[p];raw=bytes.fromhex(x['bytes']);assert b[p:p+len(raw)]==raw;allowed.add(p);path.append(dict(cs=0x83d,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(Decoder(16,raw,ip=ip).decode())))
save('selector8_dependency_path',path);assert struct.unpack_from('<H',b,0x83d0+0x1458+16)[0]==0x16fa
configs=[]
for body in ('near','far'):
 for n in (0,1,3):
  for cur in range(n+1):
   for ox,oy,nx,ny in ((0,0,-100,-100),(0,0,100,100),(100,100,0,0),(-100,-100,0,0),(0,0,0,0),(0,0,-64,64),(0,0,64,-64),(-1,1,0,0),(0,0,32767,-32768)):
    configs.append(dict(body=body,n=n,cur=cur,ox=ox,oy=oy,nx=nx,ny=ny,cache=1,base=193,tile=0,episode=1))
for body in ('commit','reindex'):
 for n in (0,3):
  for cur in (0,n):
   for ox,oy,nx,ny in ((32,32,32,32),(32,32,4064,4064),(4064,4064,4128,4064),(4128,4064,4096,4064),(0,0,-1,-1),(2048,2048,-32768,32767),(2048,2048,4192,4064),(2048,2048,0,0),(4064,4064,4063,4063),(32,32,4095,4095)):
    for cache in (0,1):configs.append(dict(body=body,n=n,cur=cur,ox=ox,oy=oy,nx=nx,ny=ny,cache=cache,base=201,tile=0,episode=3))
for cache,tile in itertools.product((0,1),(0,193,201)):
 configs.append(dict(body='commit',n=0,cur=0,ox=4096,oy=4064,nx=4128,ny=4064,cache=cache,base=193,tile=tile,episode=1))
for wanted,start in itertools.product((0,68,255,256,65535),(0,1,192,193,194,200,201,202,255,256,65535)):configs.append(dict(body='search',wanted=wanted,start=start,n=0,cur=0,ox=0,oy=0,nx=0,ny=0,cache=1,base=193,tile=0,episode=1))
for cache,base,tile in itertools.product((0,1),(0,193,201,255),(0,192,193,200,201,255)):
 configs.append(dict(body='variant',n=0,cur=0,ox=0,oy=0,nx=0,ny=0,cache=cache,base=base,tile=tile,episode=3))
for body in ('search','variant'):configs.append(dict(body=body,wanted=68,start=0,n=0,cur=0,ox=0,oy=0,nx=0,ny=0,cache=0,base=99,tile=0,episode=1,missing=True))
unique={}
for c in configs:
 if c['body']=='reindex':c['nx'],c['ny']=c['ox'],c['oy'] # unused requestedcoordinates normalized toactual savedinput
 unique.setdefault(json.dumps(c,sort_keys=True),c)
configs=list(unique.values())
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];events=[];witness=[];visited=set();plane=0x8000;groups=[(0x416a,0x57fe,0x5d34,0xc,0),(0x416c,0x5800,0x5fce,0xc,1),(0x4166,0x57fa,0x5800,0xe,2),(0x4168,0x57fc,0x5a9a,0xe,3)]
def signed(v):return ((v+32768)&65535)-32768
for load,split,c in itertools.product((0x824,0x1000),(False,True),configs):
 raw=bytearray(b)
 for x in rel:struct.pack_into('<H',raw,int(x['image_offset']),(int(x['original_word'])+load)&65535)
 ds=load+0x2771;ss=0x6000 if split else ds;base=ds*16;recordseg=load+0x21fd;sp=0xf000;sl,sh=ss*16+sp-160,ss*16+sp+24;ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(raw)]=raw;ram[plane*16:plane*16+65536]=b'\x77'*65536;ram[recordseg*16+0x373e:recordseg*16+0x573e]=bytes(8192);struct.pack_into('<H',ram,base+0x2564,plane);struct.pack_into('<hh',ram,base+0x4162,c['ox'],c['oy']);struct.pack_into('<hh',ram,base+0x415e,c['ox']>>6,c['oy']>>6);struct.pack_into('<H',ram,base+0x626a,c['episode']);struct.pack_into('<H',ram,base+0x12a,c['episode'] if c['cache'] else 0);ram[base+0x2650]=c['base'];ram[base+0x4188]=0x5a;ram[base+0xd30e:base+0xd40e]=bytes(256)
 if not c.get('missing'):ram[base+0xd30e+193]=68;ram[base+0xd30e+201]=68
 ram[base+0xd30e+255]=255;thresholds={}
 for off,countoff,tb,field,g in groups:
  vals=[-64+g*8,0+g*8,64+g*8][:c['n']];thresholds[off]=vals;struct.pack_into('<H',ram,base+off,c['cur'] if g%2==0 else c['n']-c['cur']);struct.pack_into('<H',ram,base+countoff,c['n'])
  for j,v in enumerate(vals,1):
   near=0x8000+g*0x200+j*0x20;struct.pack_into('<H',ram,base+tb+2*j,near);struct.pack_into('<h',ram,base+near+field,v)
 struct.pack_into('<H',ram,base+0xd514,c['n']);struct.pack_into('<HH',ram,base+0x416e,c['cur'],c['n']-c['cur'])
 for j in range(1,c['n']+1):
  off=0x100+j*0x20;struct.pack_into('<hh',ram,0x70000+off+0x10,(-64,0,64)[j-1],(-54,10,74)[j-1]);struct.pack_into('<HH',ram,base+0xd512+j*4,off,0x7000);struct.pack_into('<HH',ram,base+0xda8a+j*4,off,0x7000)
 nx,ny=(c['ox'],c['oy']) if c['body']=='reindex' else (c['nx'],c['ny']);newx,newy=nx>>6,ny>>6;celloff=(0x373e+2*((newy<<6)+newx))&65535
 if c['body']=='variant':celloff=0x373e;ram[recordseg*16+celloff]=c['tile']
 elif c['body'] in ('commit','reindex') and ((0<=newx<64 and 0<=newy<64) or (newx,newy)==(64,63)):ram[recordseg*16+celloff]=c['tile']
 args=(c['nx']&65535,c['ny']&65535) if c['body'] in ('near','far','commit') else (c['wanted'],c['start']) if c['body']=='search' else (celloff,recordseg) if c['body']=='variant' else ()
 frame=struct.pack('<'+'H'*(2+len(args)),0x200,0x4e00,*args);ram[ss*16+sp:ss*16+sp+len(frame)]=frame;hud=(load+0x83d)*16+0x5d2;ram[hud]=0xcb;expected=bytearray(ram);stores=[];hudargs=[];selector=[];stop='return';result=None
 def put(off,n,v):
  v&=(1<<(8*n))-1;expected[off:off+n]=v.to_bytes(n,'little');stores.append((off,n,v))
 def word(off):return struct.unpack_from('<H',expected,base+off)[0]
 def update(off,vals,oldval,newval):
  cur=word(off)
  if oldval>newval:
   while cur>0 and vals[cur-1]>newval:cur-=1;put(base+off,2,cur)
  elif oldval<newval:
   while cur<len(vals) and vals[cur]<newval:cur+=1;put(base+off,2,cur)
 def near(oldx,oldy):
  for off,_,_,_,g in groups:update(off,thresholds[off],oldx if g<2 else oldy,nx if g<2 else ny)
 def far(oldx,oldy):
  update(0x416e,[-64,0,64][:c['n']],oldx,nx);update(0x4170,[-54,10,74][:c['n']],oldy,ny)
 def search(wanted,start):
  values=expected[base+0xd30e:base+0xd40e];matches=[j for j in range(start&255,256) if values[j]==wanted] or [j for j in range(256) if values[j]==wanted]
  return matches[0] if matches else None
 def variant():
  global stop
  if word(0x12a)!=word(0x626a):
   put(base+0x12a,2,word(0x626a));idx=search(68,0)
   if idx is None:stop='fatal';return None
   put(base+0x2650,1,idx)
  typ=expected[recordseg*16+celloff]
  return (typ-expected[base+0x2650])&65535 if expected[base+0xd30e+typ]==68 else 65535
 if c['body']=='near':near(c['ox'],c['oy'])
 elif c['body']=='far':far(c['ox'],c['oy'])
 elif c['body']=='search':
  result=search(c['wanted'],c['start']);stop='fatal' if result is None else 'return'
 elif c['body']=='variant':result=variant()
 else:
  oldx,oldy=c['ox'],c['oy']
  if c['body']=='reindex':
   for off in (0x4162,0x416a,0x4166,0x416e):put(base+off,4,0)
   oldx=oldy=0
  p=plane*16+(((c['ox']>>6)<<6)+(c['oy']>>6)&65535);put(p,1,0);selector=[8];near(oldx,oldy);far(oldx,oldy);put(base+0x4162,2,nx);put(base+0x4164,2,ny)
  if (newx,newy)!=(c['ox']>>6,c['oy']>>6):put(base+0x415e,2,newx);put(base+0x4160,2,newy);hudargs=[22]
  put(base+0x417c,2,celloff);put(base+0x417e,2,recordseg);result=variant()
  if stop=='return' and result!=65535:put(base+0x4188,1,result&255)
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));writes=[];hc=[];sc=[];stops=[];pending=[];cid=len(cases)
 def code(e,a,n,data):
  if a==0x4e200:stops.append('return');e.emu_stop();return
  if a==hud:
   rsp=e.reg_read(UC_X86_REG_SP);v=struct.unpack('<H',bytes(e.mem_read(ss*16+rsp+4,2)))[0];hc.append(v);assert hc==hudargs;return
  if a==(load+0x83d)*16+0x143c:
   rsp=e.reg_read(UC_X86_REG_SP);v=struct.unpack('<I',bytes(e.mem_read(ss*16+rsp+4,4)))[0];sc.append(v);assert sc==selector
  if a==(load+0xfba)*16+0xc:
   rsp=e.reg_read(UC_X86_REG_SP);assert struct.unpack('<H',bytes(e.mem_read(ss*16+rsp+4,2)))[0]==0xda;stops.append('fatal');e.emu_stop();return
  p=a-load*16
  if p==0xf70+0x196:
   es=e.reg_read(UC_X86_REG_ES);bx=e.reg_read(UC_X86_REG_BX);addr=es*16+bx;v=bytes(e.mem_read(addr,1))[0];pending.append((addr,v,es,bx))
  if p==0xf70+0x199:
   addr,v,es,bx=pending.pop();assert e.reg_read(UC_X86_REG_BX)&255==v
   if load*16+0x2770e<=addr<load*16+0x27710:witness.append(dict(case=cid,load=load,split_SS_DS=split,body=c['body'],instruction_image=0x1106,after_instruction_image=0x1109,original_image_address=addr-load*16,ES=es,BX_before=bx,linear_address=addr,loaded_BL=v,natural_runtime=False,status='UNKNOWN',scope='Controlled committedtile64/63,notnaturalbounds/type/paddingproof'))
  assert p in allowed,hex(p);visited.add(p)
 def write(e,access,a,n,v,data):
  if not(sl<=a and a+n<=sh):writes.append((a,n,v&((1<<(8*n))-1)))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);entry={'near':(0x637,0x2c6),'far':(0x637,0x3fe),'commit':(0x637,0x51c),'reindex':(0x637,0x5d2),'search':(0xf7,4),'variant':(0xf7,0x176)}[c['body']]
 for reg,v in ((UC_X86_REG_CS,load+entry[0]),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,v)
 u.emu_start((load+entry[0])*16+entry[1],0x1fffff,count=12000);assert stops==[stop] and hc==hudargs and sc==selector and writes==stores and not pending,(c,stops,stop,hc,hudargs,writes,stores)
 if stop=='return':
  if result is not None:assert u.reg_read(UC_X86_REG_AX)==result,(c,result,u.reg_read(UC_X86_REG_AX))
  for reg,v in ((UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)):assert u.reg_read(reg)==v,(c,reg,u.reg_read(reg),v)
 actual=bytes(u.mem_read(0,len(ram)));assert actual[:sl]==expected[:sl] and actual[sh:]==expected[sh:] and actual[ss*16+sp:ss*16+sp+len(frame)]==frame
 events.extend(dict(case=cid,callee='lateHUD',argument=v) for v in hc);cases.append(dict(case=cid,load=load,split_SS_DS=split,config=json.dumps(c),stop=stop,return_AX=result if result is not None else '',new_tileX=newx,new_tileY=newy,lateHUD_calls=len(hc),original_nonstack_stores=len(writes),status='PASS'))
save('cases',cases);save('dependency_events',events);save('UNKNOWN_tail_load_witnesses',witness);save('execution_coverage',[dict(image_offset=x['image_offset'],executed=x['image_offset'] in visited) for x in rows]);summary=dict(functions=functions[:4],reused_functions=[dict(f,existing_catalog_name='class_primary_search' if f['name']=='terrain_kind_search' else 'class44_relative_id') for f in functions[4:]],cases=len(cases),failures=0,fatal_entry_stops=sum(x['stop']=='fatal' for x in cases),runtime_tests=0,new_deep_verified_bytes=0,UNKNOWN_tail_load_witnesses=len(witness),unexecuted_starts=sorted({x['image_offset'] for x in rows}-visited),scope='Original six bodies+original selector8path only;lateHUD preservingRETfixture. Sortedvalidcursor0..count model,full2MiB except184controlstackB,orderedwrites/frames;fatalstopentry. Controlledunclamped position writes/OOBlookup not naturalmovement/bounds proof. Selector8path notwhole320instruction dispatcher closure andnotnewfunction count.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',Path(__file__),out.parent/'pass1_xms_move_request/noncode_intervals.csv')]);(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
