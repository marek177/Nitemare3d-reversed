"""IMAGE INVENTORY DECODER EMULATOR OUT: original player visibility gate+Bresenham ray+door helpers; no callee fixtures; fatal stops at entry. Includes conditional UNKNOWN trailing-map-byte load witnesses."""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={x['image_offset']:x for x in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);functions=[];rows=[];edges=[]
def save(name,data):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
for name,cs,a,e in [('source_player_visibility_gate',0x4c7,0x6d2,0x7d2),('grid_visibility_ray',0xaea,0xcc0,0xe22)]:
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
save('CFG_edges',edges);allowed={x['image_offset'] for x in rows};deps=[]
for name in ('door_record_for_cell','door_state_zero_or_four'):
 p=out.parent/'guard_validator_replay'/(name+'.csv');deps.append(p)
 for x in csv.DictReader(p.open(encoding='utf-8')):
  pos=int(x['image_offset']);raw=bytes.fromhex(x['bytes']);assert b[pos:pos+len(raw)]==raw;allowed.add(pos)
def s(v):return ((v+32768)&65535)-32768
def abs16(v):return s(-v) if v<0 else v
def points(x,y,dx,dy,limit):
 sx,sy=(1 if dx>0 else -1),(1 if dy>0 else -1);ax,ay=abs16(dx),abs16(dy);major=ay<ax;incN=s(2*(ay if major else ax));err=s(incN-(ax if major else ay));incP=s(2*((ay-ax) if major else (ax-ay)));ex,ey=s(x+dx),s(y+dy);r=[]
 for j in range(max(0,limit)):
  if major:x=s(x+sx)
  else:y=s(y+sy)
  if err<0:err=s(err+incN)
  else:
   err=s(err+incP)
   if major:y=s(y+sy)
   else:x=s(x+sx)
  end=x==ex and y==ey;r.append((x,y,end))
  if end:break
 return r
def gate(c):
 x,y=s(c['wx'])>>6,s(c['wy'])>>6;dx,dy=s(c['px']-x),s(c['py']-y);ax,ay=abs16(dx),abs16(dy)
 if ax>8 or ay>8:return None
 if not c['force']:
  f=c['facing'];mask=(1<<((f-1)&7))|(1<<((f+1)&7))|((1<<(f&31))&255);mask&=0x66 if ax>=ay else 0x99;mask&=0x3c if dy>=0 else 0xc3;mask&=0x0f if dx>=0 else 0xf0
  if not mask:return None
 return (x,y,dx,dy,8,(ay&0xff00)|int(c['mode']==1))
configs=[]
for dx,dy,mode in itertools.product(range(-8,9),range(-8,9),(0,1)):configs.append(dict(body='ray',args=(32,32,dx,dy,8,mode),profile='clear'))
for delta,mode,profile in itertools.product(((1,0),(2,0),(4,2),(-4,2),(2,-4),(0,4),(4,4),(-4,-4)),(0,1,0x100),('wall','bit4_only','bit2_only','door0','door1','door2','door4','missingdoor','object_block','object_pass','source_wall','endpoint_wall')):
 configs.append(dict(body='ray',args=(32,32,delta[0],delta[1],8,mode),profile=profile))
for dx,dy,facing,force,mode in itertools.product((-8,-1,0,1,8),(-8,-1,0,1,8),(0,1,2,3,4,5,6,7),(0,1),(0,1,2)):configs.append(dict(body='gate',wx=32*64,wy=32*64,px=32+dx,py=32+dy,facing=facing,force=force,mode=mode,profile='clear'))
for facing in (8,31,32,255):configs.append(dict(body='gate',wx=32*64,wy=32*64,px=33,py=32,facing=facing,force=0,mode=0,profile='clear'))
for dx,dy,limit in itertools.product((0,1,-1,-32768),(0,1,-1,-32768),(0,-1,1,2)):
 configs.append(dict(body='ray',args=(32,32,dx,dy,limit,1),profile='clear'))
for offset in (-9,9):configs.append(dict(body='gate',wx=32*64,wy=32*64,px=32+offset,py=32,facing=0,force=1,mode=0,profile='clear'))
configs.append(dict(body='gate',wx=0,wy=0,px=-32768,py=-32768,facing=255,force=0,mode=1,profile='clear'))
for low,high,mode in itertools.product((0,17),(0,34),(0,1)):
 configs.append(dict(body='ray',args=(63,63,2,0,2,mode),profile='UNKNOWN_gap',gap_low=low,gap_high=high))
 configs.append(dict(body='gate',wx=63*64,wy=63*64,px=65,py=63,facing=0,force=1,mode=mode,profile='UNKNOWN_gap',gap_low=low,gap_high=high))
relocations=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];read_events=[];unknown=[];visited=set();Aoff,Aseg,Boff,Bseg=0x100,0x7000,0x200,0x7200;A=Aseg*16+Aoff;B=Bseg*16+Boff
for load,split,c in itertools.product((0x824,0x1000),(False,True),configs):
 raw=bytearray(b)
 for r in relocations:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 ds=load+0x2771;ss=0x6000 if split else ds;base=ds*16;recordseg=load+0x21fd;mapseg=recordseg;sp=0xf000;sl,sh=ss*16+sp-160,ss*16+sp+24;ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(raw)]=raw;mapbase=mapseg*16;ram[mapbase+0x373e:mapbase+0x573e]=bytes(8192);struct.pack_into('<H',ram,recordseg*16,0)
 for seg in set((ds,ss)):
  struct.pack_into('<H',ram,seg*16+0x2568,mapseg);ram[seg*16+0xd00c:seg*16+0xd20c]=bytes(512)
  for typ,flag in ((17,6),(18,10),(19,2),(20,4)):ram[seg*16+0xd00c+typ]=flag
  ram[seg*16+0xd10c+33]=2;ram[seg*16+0xd10c+34]=0x22
 ram[A:A+26]=bytes(26);ram[B:B+28]=bytes(28)
 if c['body']=='gate':
  ram[A+0x11]=c['facing'];struct.pack_into('<hh',ram,B+0x10,c['wx'],c['wy']);struct.pack_into('<hh',ram,ss*16+0x415e,c['px'],c['py']);args=(Aoff,Aseg,Boff,Bseg,c['mode'],c['force']);ray=gate(c)
 else:args=c['args'];ray=tuple(s(x) if j<5 else x for j,x in enumerate(args))
 route=points(*ray[:5]) if ray else [];queries=[(x,y) for x,y,end in route if not end];profile=c['profile'];stamp=None
 if profile=='source_wall':stamp=(ray[0],ray[1])
 elif profile=='endpoint_wall':stamp=(s(ray[0]+ray[2]),s(ray[1]+ray[3]))
 elif profile not in ('clear','UNKNOWN_gap') and queries:stamp=queries[0]
 if stamp is not None:
  x,y=stamp;off=(0x373e+2*((y<<6)+x))&65535
  typ=17 if profile in ('wall','source_wall','endpoint_wall') else 20 if profile=='bit4_only' else 19 if profile=='bit2_only' else 18 if profile.startswith('door') or profile=='missingdoor' else 0
  ram[mapbase+off]=typ;ram[mapbase+((off+1)&65535)]=33 if profile=='object_block' else 34 if profile=='object_pass' else 0
  if profile.startswith('door'):
   struct.pack_into('<H',ram,recordseg*16,1);struct.pack_into('<HHH',ram,recordseg*16+0x3076+4,off,mapseg,int(profile[-1]))
 if profile=='UNKNOWN_gap':ram[load*16+0x2770e]=c['gap_low'];ram[load*16+0x2770f]=c['gap_high']
 frame=struct.pack('<'+'H'*(2+len(args)),0x200,0x4e00,*[x&65535 for x in args]);ram[ss*16+sp:ss*16+sp+len(frame)]=frame;expected=bytes(ram);result=0;stop='return';finalDS=ss if c['body']=='gate' else ds;modelDS=ss if c['body']=='gate' else ds;wantreads=[];doorlookups=0
 if ray:
  for x,y,end in route:
   if end:result=1;break
   seg=struct.unpack_from('<H',ram,modelDS*16+0x2568)[0];off=(0x373e+2*((y<<6)+x))&65535;addr=seg*16+off;typ=ram[addr];flag=ram[modelDS*16+0xd00c+typ];wantreads.append(('terrain',addr,typ,x&65535,y&65535))
   if flag&2:
    if flag&4:break
    if flag&8:
     doorlookups+=1;modelDS=ss;finalDS=ss;found=None
     count=struct.unpack_from('<h',ram,recordseg*16)[0]
     for j in range(max(0,count)):
      rec=recordseg*16+0x3076+18*j
      if struct.unpack_from('<HH',ram,rec+4)==(off,seg):found=struct.unpack_from('<H',ram,rec+8)[0];break
     if found is None:stop='fatal';break
     if found not in (0,4):break
   if ray[5]&255:
    a=seg*16+((off+1)&65535);obj=ram[a];of=ram[modelDS*16+0xd10c+obj];wantreads.append(('object',a,obj,x&65535,y&65535))
    if of&2 and not of&32:break
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));writes=[];reads=[];pending=[];stops=[];ray_calls=[];door_calls=[];cid=len(cases)
 def code(e,a,n,data):
  if a==0x4e200:stops.append('return');e.emu_stop();return
  if a==(load+0xfba)*16+0xc:
   rsp=e.reg_read(UC_X86_REG_SP);assert struct.unpack('<H',bytes(e.mem_read(ss*16+rsp+4,2)))[0]==0x42;stops.append('fatal');e.emu_stop();return
  if a==(load+0xaea)*16+0xcc0:
   rsp=e.reg_read(UC_X86_REG_SP);seen=struct.unpack('<6H',bytes(e.mem_read(ss*16+rsp+4,12)));assert ray is not None and seen==tuple(x&65535 for x in ray),(c,seen,ray);ray_calls.append(seen)
  if a==load*16:door_calls.append(True)
  pc=a-load*16
  if pc in (0xaea0+0xdac,0xaea0+0xded):
   kind='terrain' if pc==0xaea0+0xdac else 'object';es=e.reg_read(UC_X86_REG_ES);bx=e.reg_read(UC_X86_REG_BX);addr=es*16+((bx+(kind=='object'))&65535);v=bytes(e.mem_read(addr,1))[0];x=e.reg_read(UC_X86_REG_SI);y=e.reg_read(UC_X86_REG_DI);reads.append((kind,addr,v,x,y));pending.append((pc,addr,v,es,bx,kind,x,y))
  if pc in (0xaea0+0xdaf,0xaea0+0xdf1):
   prev,addr,v,es,bx,kind,x,y=pending.pop();assert e.reg_read(UC_X86_REG_BX)&255==v
   if load*16+0x2770e<=addr<load*16+0x27710:unknown.append(dict(case=cid,load=load,split_SS_DS=split,entry_body=c['body'],seeded_gap_hex=ram[load*16+0x2770e:load*16+0x27710].hex(),instruction_image=prev,after_instruction_image=pc,ES=es,BX_before=bx,linear_address=addr,original_image_address=addr-load*16,loaded_BL=v,field=kind,x=x,y=y,natural_runtime=False,status='UNKNOWN',scope='Controlled OOB x64/y63 map-cell load; doesnot prove semantic type/padding or natural reachability'))
  assert pc in allowed,hex(pc);visited.add(pc)
 def write(e,access,a,n,v,data):
  if not(sl<=a and a+n<=sh):writes.append((a,n,v))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 cs,ip=(0x4c7,0x6d2) if c['body']=='gate' else (0xaea,0xcc0)
 for reg,v in ((UC_X86_REG_CS,load+cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,v)
 u.emu_start((load+cs)*16+ip,0x1fffff,count=6000);assert stops==[stop] and not pending and not writes and reads==wantreads and len(door_calls)==doorlookups,(c,stops,stop,reads,wantreads)
 if c['body']=='gate':assert len(ray_calls)==int(ray is not None)
 if stop=='return':
  assert u.reg_read(UC_X86_REG_AX)&255==result,(c,result,u.reg_read(UC_X86_REG_AX))
  for reg,v in ((UC_X86_REG_DS,finalDS),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)):assert u.reg_read(reg)==v,(c,reg,u.reg_read(reg),v)
 actual=bytes(u.mem_read(0,len(ram)));assert actual[:sl]==expected[:sl] and actual[sh:]==expected[sh:] and actual[ss*16+sp:ss*16+sp+len(frame)]==frame
 for j,(kind,addr,v,x,y) in enumerate(reads):read_events.append(dict(case=cid,index=j,kind=kind,linear_address=addr,value=v,x=x,y=y))
 cases.append(dict(case=cid,load=load,split_SS_DS=split,config=json.dumps(c),stop=stop,result_AL=result if stop=='return' else '',final_DS=u.reg_read(UC_X86_REG_DS),ray_called=bool(ray_calls),door_calls=doorlookups,original_nonstack_stores=0,status='PASS'))
save('cases',cases);save('cell_reads',read_events);save('UNKNOWN_gap_load_witnesses',unknown);save('execution_coverage',[dict(image_offset=x['image_offset'],executed=x['image_offset'] in visited) for x in rows]);sout=dict(functions=functions,cases=len(cases),failures=0,fatal_entry_stops=sum(x['stop']=='fatal' for x in cases),runtime_tests=0,new_deep_verified_bytes=0,UNKNOWN_gap_load_witnesses=len(unknown),UNKNOWN_gap_bytes=sorted(set(x['original_image_address'] for x in unknown)),unexecuted_starts=sorted({x['image_offset'] for x in rows}-visited),scope='Original gate+ray+doorlookup/statepredicate; no callee fixtures. Fatalstop atentry,no forcedreturn. Full2MiB except184controlstackB,zero nonstackstores,exact cell-load order andpre/post loadedBL checks;no UC_HOOK_MEM_READ. Synthetic OOB trailing-map reads do not classify UNKNOWN bytes or prove naturalreachability.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in [image,inventory,image.parent/'relocations.csv',Path(__file__),*deps,out.parent/'pass1_xms_move_request/noncode_intervals.csv']]);(out/'summary.json').write_text(json.dumps(sout,indent=2)+'\n');print(json.dumps({k:v for k,v in sout.items() if k!='files'},indent=2))
