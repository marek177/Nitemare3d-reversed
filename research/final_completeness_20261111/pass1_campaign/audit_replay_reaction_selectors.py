"""IMAGE INVENTORY DECODER EMULATOR OUT: original reaction selectors+score; original RNG/mul; no callee fixtures."""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old={x['image_offset']:x for x in json.loads(inventory.read_text(encoding='utf-8'))};out.mkdir(exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL);score_targets=struct.unpack('<25H',b[0x851c:0x854e]);functions=[];allrows=[];edges=[]
def save(n,rows):
 with (out/(n+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for name,a,e in [('target_score_delta',0x12e,0x1bf),('death_frame_index',0x1be4,0x1c47),('hurt_frame_index',0x1c48,0x1cab)]:
 todo=[a];d={}
 while todo:
  ip=todo.pop()
  if ip in d:continue
  assert a<=ip<e;i=Decoder(16,b[0x83d0+ip:0x83d0+e],ip=ip).decode();assert not i.is_invalid;d[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(function=name,source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control==FlowControl.INDIRECT_BRANCH:
   assert ip==0x147
   for target in sorted(set(score_targets)):todo.append(target);edges.append(dict(function=name,source=ip,target=target,kind='table'))
  elif i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(function=name,source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 rows=[]
 for ip,i in sorted(d.items()):
  p=0x83d0+ip;raw=b[p:0x83d0+i.next_ip];assert old[p]['bytes']==raw.hex();rows.append(dict(cs=0x83d,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);allrows+=rows;functions.append(dict(name=name,start=0x83d0+a,end_exclusive=0x83d0+e,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(x['bytes'])) for x in rows)))
save('CFG_edges',edges);scoremap={8:25,9:75,10:50,11:100,12:250,13:150,14:200,15:100,16:100,17:0,18:150,19:150,20:200,21:-1000,22:1000,23:100,24:200,25:0,26:25,27:100,28:100,29:250,30:250,31:200,32:50};save('score_table',[dict(source_type=i+8,start=0x851c+2*i,end_exclusive=0x851e+2*i,target_ip=t,score=scoremap[i+8]) for i,t in enumerate(score_targets)])
allowed={x['image_offset'] for x in allrows}
for folder,name in [('pass1_rng','game_rand_wrapper'),('pass1_rng','crt_rand_lcg'),('pass1_rng','compiler_mul32_low')]:allowed.update(int(x['image_offset']) for x in csv.DictReader((out.parent/folder/(name+'.csv')).open()))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));configs=[dict(kind='score',type=t) for t in range(256)]
for name,entry,offset,fast in [('death',0x1be4,0x4a,0x59),('hurt',0x1c48,0x3a,0x49)]:
 for seed,mask,count in itertools.product((0,1,0xffff,0x80000000,0xffffffff,0x12345678,0x55555555,0xaaaaaaaa),(0xff,0x7f,1,2,4,8,16,32,64,0x80,0),(0,1,8,255)):configs.append(dict(kind=name,entry=entry,offset=offset,fast=fast,seed=seed,mask=mask,countdown=count))
for name,entry,offset,fast in [('death',0x1be4,0x4a,0x59),('hurt',0x1c48,0x3a,0x49)]:
 for high in (0x80,0xff):configs.append(dict(kind=name,entry=entry,offset=offset,fast=fast,seed=1,mask=0xff,countdown=0,high=high))
cases=[];rng_events=[];visited=set();Aoff,Aseg,Boff,Bseg=0x100,0x7000,0x200,0x7200;A=Aseg*16+Aoff;B=Bseg*16+Boff
for load,split,c in itertools.product((0x824,0x1000),(False,True),configs):
 raw=bytearray(b)
 for x in rel:struct.pack_into('<H',raw,int(x['image_offset']),(int(x['original_word'])+load)&65535)
 ds=load+0x2771;ss=0x6000 if split else ds;base=ds*16;sp=0xf000;sl,sh=ss*16+sp-96,ss*16+sp+16;ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(raw)]=raw;ram[A:A+26]=bytes(26);ram[B:B+28]=bytes(28);ram[B+4]=3;ram[B+6]=c.get('type',0);ram[A+0x12]=c.get('countdown',0);struct.pack_into('<H',ram,base+0x3d22+3*8,0x5000);struct.pack_into('<I',ram,base+0x24b8,c.get('seed',0));frame=struct.pack('<6H',0x200,0x4e00,Aoff,Aseg,Boff,Bseg);ram[ss*16+sp:ss*16+sp+12]=frame;states=[];stores=[];result=scoremap.get(c.get('type'),0);stop='return'
 if c['kind']!='score':
  for j in range(8):ram[base+0x5000+c['offset']+2*j]=0x34;ram[base+0x5000+c['offset']+2*j+1]=c.get('high',1) if c['mask']&(1<<j) else 0
 expected=bytearray(ram)
 if c['kind']!='score':
  if c['countdown']==0 and c['mask']&0x80:result=7
  else:
   state=c['seed'];stop='budget' if not(c['mask']&0x7f) else 'return'
   for iteration in range(10000):
    state=(state*214013+2531011)&0xffffffff;value=(state>>16)&32767;index=value%7;states.append((state,value,index));stores.extend([(base+0x24b8,2,state&65535),(base+0x24ba,2,state>>16)])
    if c['mask']&(1<<index):result=index;break
    if stop=='budget' and len(states)==32:break
   else:raise AssertionError('reference selection did not terminate')
   struct.pack_into('<I',expected,base+0x24b8,state)
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));writes=[];rng_calls=[];stops=[]
 def code(e,a,n,data):
  if a==0x4e200:stops.append('return');e.emu_stop();return
  if a==(load+0xfba)*16+0x1a0:
   if stop=='budget' and len(rng_calls)==32:stops.append('budget');e.emu_stop();return
   assert len(rng_calls)<len(states);rng_calls.append(True)
  p=a-load*16;assert p in allowed,hex(p);visited.add(p)
 def write(e,access,a,n,v,data):
  if not(sl<=a and a+n<=sh):writes.append((a,n,v&((1<<(8*n))-1)))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
 for reg,value in ((UC_X86_REG_CS,load+0x83d),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)):u.reg_write(reg,value)
 u.emu_start((load+0x83d)*16+c.get('entry',0x12e),0x1fffff,count=200+len(states)*100);assert stops==[stop] and len(rng_calls)==len(states) and writes==stores,(c,stops,len(rng_calls),len(states),writes,stores)
 if stop=='return':
  assert u.reg_read(UC_X86_REG_AX)==result&65535,(c,result,u.reg_read(UC_X86_REG_AX))
  for reg,value in ((UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)):assert u.reg_read(reg)==value
 actual=bytes(u.mem_read(0,len(ram)));assert actual[:sl]==expected[:sl] and actual[sh:]==expected[sh:] and actual[ss*16+sp:ss*16+sp+12]==frame
 cid=len(cases)
 for j,(state,value,index) in enumerate(states):rng_events.append(dict(case=cid,index=j,state_after=state,rand=value,remainder7=index))
 cases.append(dict(case=cid,load=load,split_SS_DS=split,config=json.dumps(c),stop=stop,expected_result=result if stop=='return' else '',RNG_calls=len(states),original_nonstack_stores=len(writes),status='PASS'))
save('cases',cases);save('RNG_events',rng_events);save('execution_coverage',[dict(image_offset=x['image_offset'],executed=x['image_offset'] in visited) for x in allrows]);s=dict(functions=functions,score_table_start=0x851c,score_table_end_exclusive=0x854e,score_table_sha256=sha(b[0x851c:0x854e]),cases=len(cases),failures=0,bounded_nonreturn_cases=sum(x['stop']=='budget' for x in cases),runtime_tests=0,new_deep_verified_bytes=0,unexecuted_starts=sorted({x['image_offset'] for x in allrows}-visited),scope='Original three bodies+originalRNG/mul,no callee fixtures. HighBYTE frame eligibility,fastindex7,RNG retries,all256 scoretypes. Emptylow7 eligibility budget-stopped before33rd RNGcall,notforcedreturn or nativehang. Full2MiB except112 controlstackB andexact original stores. Naturalbanks/asyncwrites/invalidpointers open.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',Path(__file__),out.parent/'pass1_rng/game_rand_wrapper.csv',out.parent/'pass1_rng/crt_rand_lcg.csv',out.parent/'pass1_rng/compiler_mul32_low.csv')]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
