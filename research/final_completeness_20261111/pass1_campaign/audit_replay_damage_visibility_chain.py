"""IMAGE INVENTORY DECODER EMULATOR OUT: original damage/event/frame/visibility/door chain; lateHUD AXfixture andsound/message preservingRETfixtures remain."""
import bisect,csv,hashlib,itertools,json,struct,sys
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
scoremap={8:25,9:75,10:50,11:100,12:250,13:150,14:200,15:100,16:100,17:0,18:150,19:150,20:200,21:-1000,22:1000,23:100,24:200,25:0,26:25,27:100,28:100,29:250,30:250,31:200,32:50}
def signed(v):return ((v+32768)&65535)-32768
def effect_formula(kind,selector,control,episode,delta,remainder):
 v=signed((delta<<3)+remainder)
 if kind in (12,29):v>>=3
 elif kind==13:v>>=1 if selector==1 else 3
 elif kind in (14,17,20):v>>=1 if selector==2 else 3
 elif kind in (15,16):v>>=8 if selector==1 else 1
 elif kind in (18,19):v>>=2
 elif kind in (21,25):v=0
 elif kind==22:v=3 if episode==3 else 0
 elif kind==23:v>>=8 if selector==1 else 2
 elif kind==24:v>>=8 if selector==1 else 4 if selector==2 else 3
 elif kind==26:v=v>>1 if selector==1 else 0
 elif kind in (27,28):v>>=1
 elif kind==30:v=0 if selector==1 else v>>3
 elif kind==31:v=0 if selector==1 else v>>2
 if control==2:v>>=1
 elif control==0:v=signed(v*2)
 return 255 if v>255 else v&65535
configs=[]
for typ,health,delta in itertools.product((8,12,13,14,15,21,22,24,25,26,30,31,32,255),(0,1,127,255),(-1,0,32)):
 configs.append(dict(type=typ,health=health,delta=delta,selector=1,control=1,episode=3,seed=1,mask=255,counter=0,kind=0,state=0,mode=0,sign=1,klass=1,score_before=0))
for selector,control,seed,mask,kind,state,counter in itertools.product((0,1,2),(0,2),(0,0xffffffff),(1,64),(0,2,4),(3,7,8,11,21,255),(0,8)):
 configs.append(dict(type=12,health=255,delta=1,selector=selector,control=control,episode=1,seed=seed,mask=mask,counter=counter,kind=kind,state=state,mode=1,sign=-128,klass=7,score_before=0xffffffff))
for sign,mode in itertools.product((-128,0),(0,1)):
 configs.append(dict(type=12,health=1,delta=32,selector=1,control=1,episode=1,seed=0xffffffff,mask=1,counter=8,kind=0,state=7,mode=mode,sign=sign,klass=7,score_before=0xffffffff))
configs.append(dict(type=21,health=0,delta=0,selector=1,control=1,episode=1,seed=0xffffffff,mask=64,counter=8,kind=0,state=7,mode=1,sign=0,klass=7,score_before=0xffffffff))
for typ,health,delta,control in itertools.product((8,12,13,15,16,24,32,255),(1,127,255),(-33,-4096),(0,1)):
 configs.append(dict(type=typ,health=health,delta=delta,selector=1,control=control,episode=1,seed=0,mask=127,counter=8,kind=0,state=7,mode=0,sign=0,klass=1,score_before=0))
D={8:35,9:8,10:7,11:36,12:4,13:19,14:14,18:7,19:7,20:35,23:70,24:70,26:74,27:2,28:2,29:9,30:70,31:70};H={8:34,11:59,12:20,13:21,14:16,17:6,18:63,19:60,22:18,23:72,24:71,26:73,27:13,28:13,29:56,30:61,31:61};T=list(struct.unpack_from('<91h',b,0x29064))
def expected_pan(x,y,facing):
 idx=90 if y==0 else bisect.bisect_left(T,abs(x*1024)//abs(y));angle=idx+180 if x<0 and y>=0 else 360-idx if x<0 else 180-idx if y>0 else idx;v=signed(angle-facing)
 if v>180:v=signed(v-360)
 elif signed(facing-angle)>180:v=signed(v+360)
 return 1 if 35<v<145 else 2 if -145<v<-35 else 0
for c in configs:
 c['effect_state']=(c['seed']*214013+2531011)&0xffffffff;c['raw_damage']=effect_formula(c['type'],c['selector'],c['control'],c['episode'],c['delta'],((c['effect_state']>>16)&32767)%25);c['score']=scoremap.get(c['type'],0);c['index_states']=[];c['event_states']=[];c['index']=0;c['x']=c['delta'];c['y']=c['selector']-1;c['facing']=c['control']*90;c['pan']=expected_pan(c['x'],c['y'],c['facing']);c['event_sid']=None
 d=c['raw_damage']&255;death=c['health']<=d;state=c['effect_state'];event='death' if death and c['mode']!=1 else 'state7' if not death and d and c['state']==7 else None
 if event=='state7':
  if c['type'] in (9,10,15,16):
   state=(state*214013+2531011)&0xffffffff;c['event_states'].append(state);value=(state>>16)&32767;c['event_sid']=56+value%3 if c['type'] in (9,10) else 54+value%2
  else:c['event_sid']=H.get(c['type'],0)
 if death or (d and c['kind']!=4):
  if death and c['counter']==0 and c['mask']&128:c['index']=7
  else:
   for j in range(10000):
    state=(state*214013+2531011)&0xffffffff;c['index_states'].append(state);index=((state>>16)&32767)%7
    if c['mask']&(1<<index):c['index']=index;break
   else:raise AssertionError('reference retry bound')
 if event=='death':
  if c['type'] in (15,16):
   state=(state*214013+2531011)&0xffffffff;c['event_states'].append(state);value=(state>>16)&32767;c['event_sid']=11+value%3
  else:c['event_sid']=D.get(c['type'],0)
for c in configs:
 tx,ty=signed(c['x'])>>6,signed(c['y'])>>6;c['visibility_AL']=int(0<max(abs(tx),abs(ty))<=8) # clear grid,target player tile0/0;zero-displacement ray returns0
allowed={x['image_offset'] for x in rows};return_pcs=set()
for folder,name in [('damage_effect_replay','instructions'),('reaction_selectors_replay','target_score_delta'),('reaction_selectors_replay','death_frame_index'),('reaction_selectors_replay','hurt_frame_index'),('pass1_rng','game_rand_wrapper'),('pass1_rng','crt_rand_lcg'),('pass1_rng','compiler_mul32_low'),('damage_sound_frame_replay','death_sound_event'),('damage_sound_frame_replay','state7_sound_event'),('damage_sound_frame_replay','source_pan_sector'),('damage_sound_frame_replay','source_relative_bearing'),('damage_sound_frame_replay','apply_frame_state'),('angle_lookup','instructions'),('visibility_gate_ray_replay','source_player_visibility_gate'),('visibility_gate_ray_replay','grid_visibility_ray'),('guard_validator_replay','door_record_for_cell'),('guard_validator_replay','door_state_zero_or_four')]:
 for x in csv.DictReader((out.parent/folder/(name+'.csv')).open(encoding='utf-8')):
  pos=int(x['image_offset']);raw=bytes.fromhex(x['bytes']);assert b[pos:pos+len(raw)]==raw;allowed.add(pos)
  if (folder in ('damage_effect_replay','reaction_selectors_replay') or name in ('death_sound_event','state7_sound_event','apply_frame_state','source_player_visibility_gate')) and raw==b'\xcb':return_pcs.add(pos)
original_names={'effect','death_index','hurt_index','score','death_extra','state7_extra','frame_dispatch','special'}
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];events=[];visited=set();Aoff,Aseg,Boff,Bseg,celloff,cellseg=0x100,0x7000,0x200,0x7200,0x300,0x7400;A=Aseg*16+Aoff;B=Bseg*16+Boff;cell=cellseg*16+celloff;pair=(Aoff,Aseg,Boff,Bseg)
for load,split,c in itertools.product((0x824,0x1000),(False,True),configs):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 ds=load+0x2771;ss=0x6000 if split else ds;base=ds*16;sp=0xf000;sl,sh=ss*16+sp-128,ss*16+sp+16;ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(raw)]=raw;ram[A:A+26]=bytes(26);ram[B:B+28]=bytes(28);ram[cell:cell+2]=b'\x66\x77';ram[A+0xa]=c['kind'];ram[A+0xb]=c['state'];ram[A+0xc]=0x55;ram[A+0xd]=0x9c;ram[A+0x10]=c['health'];ram[A+0x12]=c['counter'];ram[A+0x17]=0x44;ram[B+4]=c['klass'];ram[B+6]=c['type'];struct.pack_into('<hh',ram,B+0x10,c['x'],c['y']);struct.pack_into('<hh',ram,base+0x4162,0,0);struct.pack_into('<H',ram,base+0x4156,c['facing']);struct.pack_into('<H',ram,B+0x18,c['delta']&65535);struct.pack_into('<H',ram,base+0x4552,0);ram[base+0x418f]=c['selector'];struct.pack_into('<H',ram,base+0x4180,c['control']);struct.pack_into('<H',ram,base+0x626a,c['episode']);struct.pack_into('<I',ram,base+0x24b8,c['seed']);ram[B+0x1a]=c['sign']&255;struct.pack_into('<HH',ram,B+0xc,celloff,cellseg);struct.pack_into('<H',ram,base+0x4190,c['mode']);struct.pack_into('<I',ram,base+0x4182,c['score_before'])
 for seg,near,framebase in ((ds,0x5000,0x1100),(ss,0x5200 if split else 0x5000,0x2200 if split else 0x1100)):
  struct.pack_into('<H',ram,seg*16+0x3d22+c['klass']*8,near)
  for j in range(8):
   v=(framebase+j) if c['mask']&(1<<j) else j;struct.pack_into('<H',ram,seg*16+near+0x3a+2*j,v);struct.pack_into('<H',ram,seg*16+near+0x4a+2*j,v+0x100 if c['mask']&(1<<j) else j)
 recordseg=load+0x21fd;ram[recordseg*16+0x373e:recordseg*16+0x573e]=bytes(8192);struct.pack_into('<H',ram,ss*16+0x2568,recordseg);struct.pack_into('<hh',ram,ss*16+0x415e,0,0);ram[ss*16+0xd00c:ss*16+0xd20c]=bytes(512)
 frame=struct.pack('<6H',0x200,0x4e00,*pair);ram[ss*16+sp:ss*16+sp+12]=frame;expected=bytearray(ram);stores=[];want=[];damage=c['raw_damage']&255;death=c['health']<=damage;branch='death' if death else 'zero' if damage==0 else 'survive';finalDS=ds
 def put(p,n,v):expected[p:p+n]=v.to_bytes(n,'little');stores.append((p,n,v))
 def call(name,args,ax):
  if name in ('death_extra','state7_extra'):ax=c['pan']
  if name=='special':ax=c['visibility_AL']
  if name=='frame_dispatch':ax=(0xff00 if args[4]>>8==0 else 0)|(args[5]&255)
  want.append((name,tuple(args),ax&65535))
  if name=='effect':states=[c['effect_state']]
  elif name in ('death_index','hurt_index'):states=c['index_states']
  elif name in ('death_extra','state7_extra'):states=c['event_states']
  else:states=[]
  for state in states:put(base+0x24b8,2,state&65535);put(base+0x24ba,2,state>>16)
  if name in ('death_extra','state7_extra'):want.append(('sound_dispatch',(c['event_sid'],c['pan'],2),c['pan']))
  if name=='frame_dispatch':
   f=args[4];put(A,2,f);put(B+3,1,f&255);put(A+6,2,((f>>8)-1)&65535);put(A+0xc,1,args[6]&255);put(A+0xb,1,args[5]&255)
 call('effect',pair,c['raw_damage']);dframe=(0x1100 if c['mask']&(1<<c['index']) else 0)+c['index'];sframe=((0x2200 if split else 0x1100) if c['mask']&(1<<c['index']) else 0)+c['index']
 if death:
  put(A+0x10,1,0);call('death_index',pair,c['index'])
  if c['mode']!=1:call('death_extra',pair,0x1234)
  call('frame_dispatch',(*pair,dframe+0x100 if c['mask']&(1<<c['index']) else c['index'],18 if c['sign']>0 else 0,9),0x5678);call('score',pair,c['score']);put(base+0x4182,2,(c['score_before']+c['score'])&65535);put(base+0x4184,2,((c['score_before']+c['score'])&0xffffffff)>>16);call('refresh',(4,),0xbeef);put(cell+1,1,0x9c)
 elif damage:
  if c['state']==7:call('state7_extra',pair,0x1234)
  put(A+0x10,1,c['health']-damage);put(A+0x12,1,8)
  if c['kind']!=4:
   call('hurt_index',pair,c['index'])
   if c['kind']==2:call('frame_dispatch',(*pair,dframe,0,8),0x5678)
   elif c['state'] not in (3,4,11):
    if c['state'] in (7,8,21):call('special',(Aoff,Aseg,Boff,Bseg,0,1),c['visibility_AL']);put(A+0x17,1,c['visibility_AL']);call('frame_dispatch',(*pair,sframe,0,5),0x5678);finalDS=ss;branch='survive_special_DS_restore_SS'
    else:
     put(A,2,sframe);put(B+3,1,sframe&255)
     if c['state']:put(A+0xc,1,c['state'])
     put(A+0xb,1,21);finalDS=ss;branch='survive_DS_restore_SS'
 targets={(load+0x83d)*16+0x1c0:'effect',(load+0x83d)*16+0x1be4:'death_index',(load+0x83d)*16+0x1922:'death_extra',(load+0x4c7)*16+0x868:'frame_dispatch',(load+0x83d)*16+0x12e:'score',(load+0x83d)*16+0x5d2:'refresh',(load+0x83d)*16+0x1ae4:'state7_extra',(load+0x83d)*16+0x1c48:'hurt_index',(load+0x4c7)*16+0x6d2:'special'}
 targets[(load+0xc2b)*16+0x3d6]='sound_dispatch'
 for p,name in targets.items():
  if name not in original_names:ram[p]=expected[p]=0xcb
 callback=load*16+0xd9e0;ram[callback]=expected[callback]=0xcb
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));calls=[];writes=[];stopped=[];pending_original=[];messages=[]
 def code(e,a,n,data):
  if a==0x4e200:stopped.append(True);e.emu_stop();return
  if a==callback:
   assert c['type']==21;messages.append(True);return
  if a-load*16 in return_pcs:
   assert pending_original;name,wantAX,entrySP=pending_original.pop();assert (e.reg_read(UC_X86_REG_AX)&(255 if name=='special' else 65535))==wantAX and e.reg_read(UC_X86_REG_SP)==entrySP,(c,name,wantAX,e.reg_read(UC_X86_REG_AX));
  if a in targets:
   name=targets[a];w=want[len(calls)];assert name==w[0];rsp=e.reg_read(UC_X86_REG_SP);args=struct.unpack('<'+'H'*len(w[1]),bytes(e.mem_read(ss*16+rsp+4,len(w[1])*2)));assert args==w[1],(c,name,args,w);calls.append((name,args,w[2]));
   if name in original_names:pending_original.append((name,w[2],rsp))
   elif name=='sound_dispatch':assert e.reg_read(UC_X86_REG_AX)==w[2]
   else:e.reg_write(UC_X86_REG_AX,w[2])
   return
  p=a-load*16;assert p in allowed;visited.add(p)
 def write(e,access,a,n,v,data):
  if not(sl<=a and a+n<=sh):writes.append((a,n,v&((1<<(8*n))-1)))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 for reg,value in ((UC_X86_REG_CS,load+0x4c7),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
 u.emu_start((load+0x4c7)*16+0x1304,0x1fffff,count=4000+len(c['index_states'])*150);assert stopped and not pending_original and len(messages)==int(c['type']==21) and calls==want and writes==stores,(c,calls,want,writes,stores)
 for reg,value in ((UC_X86_REG_DS,finalDS),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)):assert u.reg_read(reg)==value,(c,reg,u.reg_read(reg),value)
 actual=bytes(u.mem_read(0,len(ram)));assert actual[:sl]==expected[:sl] and actual[sh:]==expected[sh:] and actual[ss*16+sp:ss*16+sp+12]==frame
 cid=len(cases)
 for j,(name,args,ax) in enumerate(calls):events.append(dict(case=cid,index=j,callee=name,args=json.dumps(args),expected_AX_or_AL=ax,return_width='AL' if name=='special' else 'AX',response_kind='original_return_checked' if name in original_names else 'preserving_RET_fixture' if name=='sound_dispatch' else 'AX_fixture'))
 cases.append(dict(case=cid,load=load,split_SS_DS=split,config=json.dumps(c),effective_damage=damage,branch=branch,final_DS=finalDS,nonstack_stores=len(writes),status='PASS'))
save('original_chain_instruction_coverage',[dict(image_offset=p,executed=p in visited) for p in sorted(allowed)]);save('cases',cases);save('dependency_events',events);save('execution_coverage',[dict(image_offset=x['image_offset'],executed=x['image_offset'] in visited) for x in rows]);s=dict(functions=[],jump_table_start=0x60b2,jump_table_end_exclusive=0x60d8,jump_table_sha256=sha(b[0x60b2:0x60d8]),cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,unexecuted_starts=sorted({x['image_offset'] for x in rows}-visited),scope='Original wholecaller+effect+score+death/hurtselectors+RNG/multiply. Original death/state7 event wrappers,relativebearing/pan/angle andframe writer additionally execute. Original visibility gate/ray additionally execute,AL-only special return andDS=SS verified. Cleargrid/no door in joined cases;originaldoor helpers in isolated matrix. OnlylateHUD preservingAX,sounddispatch andtype21message preservingRETfixtures remain. Complete2MiB except144 controlstackB,all original ordered stores,original callee returns checked. Valid nonemptylow7 framebanks; naturalcallee sideeffects/aliases/native gameplay open.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (out.parent/'visibility_gate_ray_replay/source_player_visibility_gate.csv',out.parent/'visibility_gate_ray_replay/grid_visibility_ray.csv',out.parent/'guard_validator_replay/door_record_for_cell.csv',out.parent/'guard_validator_replay/door_state_zero_or_four.csv',out.parent/'damage_sound_frame_replay/death_sound_event.csv',out.parent/'damage_sound_frame_replay/state7_sound_event.csv',out.parent/'damage_sound_frame_replay/source_pan_sector.csv',out.parent/'damage_sound_frame_replay/source_relative_bearing.csv',out.parent/'damage_sound_frame_replay/apply_frame_state.csv',out.parent/'angle_lookup/instructions.csv',image,inventory,image.parent/'relocations.csv',Path(__file__),out.parent/'damage_result_consumer_replay/damage_result_consumer.csv',out.parent/'damage_effect_replay/instructions.csv',out.parent/'reaction_selectors_replay/target_score_delta.csv',out.parent/'reaction_selectors_replay/death_frame_index.csv',out.parent/'reaction_selectors_replay/hurt_frame_index.csv',out.parent/'pass1_rng/game_rand_wrapper.csv',out.parent/'pass1_rng/crt_rand_lcg.csv',out.parent/'pass1_rng/compiler_mul32_low.csv')]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
