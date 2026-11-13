"""IMAGE INVENTORY DECODER EMULATOR OUT: whole04C7:1304 damage-result consumer; all callees explicit no-side-effect AX response fixtures."""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={x['image_offset']:x for x in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);table=struct.unpack('<19H',b[0x60b2:0x60d8]);todo=[0x1304];decoded={};edges=[]
while todo:
 ip=todo.pop()
 if ip in decoded:continue
 assert 0x1304<=ip<0x1510 and not 0x1442<=ip<0x1468;i=Decoder(16,b[0x4c70+ip:0x6180],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
 if i.flow_control==FlowControl.INDIRECT_BRANCH:
  assert ip==0x143d
  for target in sorted(set(table)):todo.append(target);edges.append(dict(source=ip,target=target,kind='jump_table'))
 elif i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
rows=[]
for ip,i in sorted(decoded.items()):
 p=0x4c70+ip;raw=b[p:0x4c70+i.next_ip];assert old[p]['bytes']==raw.hex();rows.append(dict(cs=0x4c7,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
def save(name,data):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
save('damage_result_consumer',rows);save('CFG_edges',edges);save('jump_table',[dict(state=i+3,start=0x60b2+2*i,end_exclusive=0x60b4+2*i,target_cs=0x4c7,target_ip=t) for i,t in enumerate(table)])
configs=[]
for health,damage,kind,state in itertools.product((0,1,127,128,255),(0,1,127,255,256,0xfff0,0xffff),(0,2,4),(0,3,4,7,8,11,21,22,255)):configs.append(dict(health=health,raw_damage=damage,kind=kind,state=state,mode=0,sign=1,klass=1,index=2,score=-1,score_before=0))
for state in range(3,22):configs.append(dict(health=255,raw_damage=1,kind=0,state=state,mode=0,sign=0,klass=0,index=0,score=0,score_before=0))
for mode,sign,score,before in itertools.product((0,1),(-128,0,1,127),(-32768,0,32767),(0,0xffffffff)):
 configs.append(dict(health=1,raw_damage=1,kind=0,state=7,mode=mode,sign=sign,klass=7,index=3,score=score,score_before=before))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];events=[];visited=set();Aoff,Aseg,Boff,Bseg,celloff,cellseg=0x100,0x7000,0x200,0x7200,0x300,0x7400;A=Aseg*16+Aoff;B=Bseg*16+Boff;cell=cellseg*16+celloff;pair=(Aoff,Aseg,Boff,Bseg)
for load,split,c in itertools.product((0x824,0x1000),(False,True),configs):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 ds=load+0x2771;ss=0x6000 if split else ds;base=ds*16;sp=0xf000;sl,sh=ss*16+sp-64,ss*16+sp+16;ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(raw)]=raw;ram[A:A+26]=bytes(26);ram[B:B+28]=bytes(28);ram[cell:cell+2]=b'\x66\x77';ram[A+0xa]=c['kind'];ram[A+0xb]=c['state'];ram[A+0xc]=0x55;ram[A+0xd]=0x9c;ram[A+0x10]=c['health'];ram[A+0x12]=0x33;ram[A+0x17]=0x44;ram[B+4]=c['klass'];ram[B+0x1a]=c['sign']&255;struct.pack_into('<HH',ram,B+0xc,celloff,cellseg);struct.pack_into('<H',ram,base+0x4190,c['mode']);struct.pack_into('<I',ram,base+0x4182,c['score_before'])
 for seg,near,framebase in ((ds,0x5000,0x1100),(ss,0x5200 if split else 0x5000,0x2200 if split else 0x1100)):
  struct.pack_into('<H',ram,seg*16+0x3d22+c['klass']*8,near)
  for j in range(4):struct.pack_into('<H',ram,seg*16+near+0x3a+2*j,framebase+j);struct.pack_into('<H',ram,seg*16+near+0x4a+2*j,framebase+0x100+j)
 frame=struct.pack('<6H',0x200,0x4e00,*pair);ram[ss*16+sp:ss*16+sp+12]=frame;expected=bytearray(ram);stores=[];want=[];damage=c['raw_damage']&255;death=c['health']<=damage;branch='death' if death else 'zero' if damage==0 else 'survive';finalDS=ds
 def put(p,n,v):expected[p:p+n]=v.to_bytes(n,'little');stores.append((p,n,v))
 def call(name,args,ax):want.append((name,tuple(args),ax&65535))
 call('effect',pair,c['raw_damage']);dframe=0x1100+c['index'];sframe=(0x2200 if split else 0x1100)+c['index']
 if death:
  put(A+0x10,1,0);call('death_index',pair,c['index'])
  if c['mode']!=1:call('death_extra',pair,0x1234)
  call('frame_dispatch',(*pair,dframe+0x100,18 if c['sign']>0 else 0,9),0x5678);call('score',pair,c['score']);put(base+0x4182,2,(c['score_before']+c['score'])&65535);put(base+0x4184,2,((c['score_before']+c['score'])&0xffffffff)>>16);call('refresh',(4,),0xbeef);put(cell+1,1,0x9c)
 elif damage:
  if c['state']==7:call('state7_extra',pair,0x1234)
  put(A+0x10,1,c['health']-damage);put(A+0x12,1,8)
  if c['kind']!=4:
   call('hurt_index',pair,c['index'])
   if c['kind']==2:call('frame_dispatch',(*pair,dframe,0,8),0x5678)
   elif c['state'] not in (3,4,11):
    if c['state'] in (7,8,21):call('special',(Aoff,Aseg,Boff,Bseg,0,1),0xabcd);put(A+0x17,1,0xcd);call('frame_dispatch',(*pair,dframe,0,5),0x5678)
    else:
     put(A,2,sframe);put(B+3,1,sframe&255)
     if c['state']:put(A+0xc,1,c['state'])
     put(A+0xb,1,21);finalDS=ss;branch='survive_DS_restore_SS'
 targets={(load+0x83d)*16+0x1c0:'effect',(load+0x83d)*16+0x1be4:'death_index',(load+0x83d)*16+0x1922:'death_extra',(load+0x4c7)*16+0x868:'frame_dispatch',(load+0x83d)*16+0x12e:'score',(load+0x83d)*16+0x5d2:'refresh',(load+0x83d)*16+0x1ae4:'state7_extra',(load+0x83d)*16+0x1c48:'hurt_index',(load+0x4c7)*16+0x6d2:'special'}
 for p in targets:ram[p]=expected[p]=0xcb
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));calls=[];writes=[];stopped=[]
 def code(e,a,n,data):
  if a==0x4e200:stopped.append(True);e.emu_stop();return
  if a in targets:
   name=targets[a];w=want[len(calls)];assert name==w[0];rsp=e.reg_read(UC_X86_REG_SP);args=struct.unpack('<'+'H'*len(w[1]),bytes(e.mem_read(ss*16+rsp+4,len(w[1])*2)));assert args==w[1],(c,name,args,w);calls.append((name,args,w[2]));e.reg_write(UC_X86_REG_AX,w[2]);return
  p=a-load*16;assert p in {x['image_offset'] for x in rows};visited.add(p)
 def write(e,access,a,n,v,data):
  if not(sl<=a and a+n<=sh):writes.append((a,n,v&((1<<(8*n))-1)))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 for reg,value in ((UC_X86_REG_CS,load+0x4c7),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
 u.emu_start((load+0x4c7)*16+0x1304,0x1fffff,count=500);assert stopped and calls==want and writes==stores,(c,calls,want,writes,stores)
 for reg,value in ((UC_X86_REG_DS,finalDS),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)):assert u.reg_read(reg)==value,(c,reg,u.reg_read(reg),value)
 actual=bytes(u.mem_read(0,len(ram)));assert actual[:sl]==expected[:sl] and actual[sh:]==expected[sh:] and actual[ss*16+sp:ss*16+sp+12]==frame
 cid=len(cases)
 for j,(name,args,ax) in enumerate(calls):events.append(dict(case=cid,index=j,callee=name,args=json.dumps(args),fixture_AX=ax))
 cases.append(dict(case=cid,load=load,split_SS_DS=split,config=json.dumps(c),effective_damage=damage,branch=branch,final_DS=finalDS,nonstack_stores=len(writes),status='PASS'))
save('cases',cases);save('dependency_events',events);save('execution_coverage',[dict(image_offset=x['image_offset'],executed=x['image_offset'] in visited) for x in rows]);s=dict(functions=[dict(name='damage_result_consumer',start=0x5f74,end_exclusive=0x6180,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(x['bytes'])) for x in rows))],jump_table_start=0x60b2,jump_table_end_exclusive=0x60d8,jump_table_sha256=sha(b[0x60b2:0x60d8]),cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,unexecuted_starts=sorted({x['image_offset'] for x in rows}-visited),scope='Whole original caller only; nine callees explicit AX-only preserving-state/no-memory-effects RETFfixtures. Original damage/RNG/death/state/score/dispatch algorithms not executed here. Full2MiB except80 controlstackB,orderedstores and frames matched. DS restored to SS in one branch; no native gameplay closure.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',Path(__file__))]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
