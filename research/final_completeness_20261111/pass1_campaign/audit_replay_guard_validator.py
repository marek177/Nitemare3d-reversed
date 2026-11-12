"""python audit_replay_guard_validator.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

functions=[]
for name,cs,start,end in [('guard_cell_probe',0x4c7,0x254,0x422),('door_record_for_cell',0,0,0x52),('door_state_zero_or_four',0,0x1e0,0x1fc),('door_state_one',0,0x1fc,0x212)]:
 todo=[start];decoded={};edges=[];rows=[]
 while todo:
  ip=todo.pop()
  if ip in decoded:continue
  assert start<=ip<end;i=Decoder(16,b[cs*16+ip:cs*16+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 for ip,i in sorted(decoded.items()):
  pos=cs*16+ip;raw=b[pos:cs*16+i.next_ip];assert lookup[pos]['bytes']==raw.hex();rows.append(dict(cs=cs,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);save(name+'_cfg',edges);functions.append(dict(name=name,start=cs*16+start,end_exclusive=cs*16+end,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows)))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
def signed(n):return n if n<32768 else n-65536
def abs16(n):n=signed(n&65535);return signed((-n if n<0 else n)&65535)
def mapoff(x,y):return (0x373e+(y&0xffc0)*2+(signed(x&0xffdf)>>5))&65535

def setup(load):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for x in rel:struct.pack_into('<H',runtime,int(x['image_offset']),(int(x['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));return u,load+0x2771,load+0x21fd

def regs(u,load,ds,cs,words,initial_ds=None,ah=0xab):
 for reg,value in [(UC_X86_REG_CS,load+cs),(UC_X86_REG_DS,ds if initial_ds is None else initial_ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_AX,ah<<8|0xcd),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,value)
 u.mem_write(ds*16+0xf000,struct.pack('<'+'H'*(2+len(words)),0x100,0x5000,*words))

def validator(load,tilecode,occcode,tileflags,occflags,delta0,delta1,doorstate=0,kind=0x32,mode=8,strategy=0,orientation=0,compare=0,command=0x77,doorbase=0xd00,group='flags'):
 u,ds,seg=setup(load);g=0x264e;a=6;door=0x3076;desc=0x7000;x=3104;y=3360;cell=mapoff(x,y)
 guard=bytearray(26);struct.pack_into('<H',guard,6,0x102);guard[10]=strategy;guard[11]=mode;guard[17]=command;guard[19]=3;guard[20]=252
 actor=bytearray(28);struct.pack_into('<HH',actor,16,x+compare,y+compare)
 d=bytearray(18);struct.pack_into('<H',d,0,desc);struct.pack_into('<HHH',d,4,cell,seg,doorstate);struct.pack_into('<HH',d,12,doorbase,doorbase)
 u.mem_write(seg*16+g,bytes(guard));u.mem_write(seg*16+a,bytes(actor));u.mem_write(seg*16+door,bytes(d));u.mem_write(seg*16,struct.pack('<H',1));u.mem_write(ds*16+desc+6,bytes([kind,orientation]));u.mem_write(seg*16+cell,bytes([tilecode,occcode]));flags=bytearray(512);flags[tilecode]=tileflags;flags[256+occcode]=occflags;u.mem_write(ds*16+0xd00c,bytes(flags));u.mem_write(ds*16+0x4162,struct.pack('<HH',(x-delta0)&65535,(y-delta1)&65535))
 expected_g=bytearray(guard);expected_a=bytearray(actor);expected_d=bytearray(d);expected_calls=[];near=abs16(delta0)<42 and abs16(delta1)<42;blocked=True;motion=None
 if not near and not occflags&2:
  if tileflags&8:
   expected_calls=['lookup','state1']
   if doorstate!=1 or 0x33<=kind<=0x3c:expected_calls.append('state04');blocked=doorstate not in (0,4)
   else:
    if mode==6:expected_d[16]=1
    if strategy==1:
     struct.pack_into('<H',expected_g,6,32);expected_g[19]=expected_g[20]=0
     delta=-8 if compare>0 else 8 if compare<0 else 0
     if orientation==2:expected_g[19]=delta&255;struct.pack_into('<H',expected_a,18,(doorbase+32)&65535);motion=(delta,0)
     else:expected_g[20]=delta&255;struct.pack_into('<H',expected_a,16,(doorbase+32)&65535);motion=(0,delta)
     expected_g[11]=17;expected_calls+=['motion','transition']
    expected_calls.append('command')
  else:blocked=bool(tileflags&2)
 addresses={(load+0)*16:'lookup',(load+0)*16+0x1fc:'state1',(load+0)*16+0x1e0:'state04',(load+0x4c7)*16+0xb0:'motion',(load+0x4c7)*16+0x12a:'transition',(load+0)*16+0x598:'command',(load+0xfba)*16+0xc:'error'}
 for address,name in addresses.items():
  if name in ('motion','transition','command'):u.mem_write(address,b'\xcb')
 observed=[];command_words=[]
 def hook(uc,address,size,user):
  if address not in addresses:return
  name=addresses[address];observed.append(name);sp=uc.reg_read(UC_X86_REG_SP)
  def args(n):return struct.unpack('<'+'H'*n,bytes(uc.mem_read(ds*16+sp+4,n*2)))
  if name=='lookup':assert args(2)==(cell,seg)
  elif name in ('state1','state04'):assert args(2)==(door,seg)
  elif name=='motion':assert args(4)==(g,seg,motion[0]&65535,motion[1]&65535);uc.reg_write(UC_X86_REG_AX,0xa6b7)
  elif name=='transition':assert args(5)==(g,seg,a,seg,1);uc.reg_write(UC_X86_REG_AX,0xd2e3)
  elif name=='command':
   values=args(3);assert values[:2]==(door,seg) and values[2]&255==command;command_words.append(values[2]);uc.reg_write(UC_X86_REG_AX,0xbcde)
  elif name=='error':raise AssertionError('unexpected missing-door lookup')
 u.hook_add(UC_HOOK_CODE,hook);regs(u,load,ds,0x4c7,[g,seg,a,seg,x,y]);u.emu_start((load+0x4c7)*16+0x254,0x50100,count=4000)
 assert observed==expected_calls and (u.reg_read(UC_X86_REG_AX)&255)==int(blocked)
 assert bytes(u.mem_read(seg*16+g,26))==expected_g and bytes(u.mem_read(seg*16+a,28))==expected_a and bytes(u.mem_read(seg*16+door,18))==expected_d and bytes(u.mem_read(seg*16+cell,2))==bytes([tilecode,occcode])
 assert bytes(u.mem_read(ds*16+0xd00c,512))==flags
 assert u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SP)==0xf004 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x2345 and u.reg_read(UC_X86_REG_DI)==0x3456
 if command_words:assert command_words==[((0xd2 if strategy==1 else 0x30)<<8)|command]
 cases.append(dict(group=group,load=load,tile_code=tilecode,occupancy_code=occcode,tile_flags=tileflags,occupancy_flags=occflags,player_delta0=delta0,player_delta1=delta1,door_state=doorstate,descriptor_kind=kind,guard_mode=mode,guard_strategy=strategy,orientation=orientation,comparison=compare,command_BYTE=command,command_pushed_WORD=command_words[0] if command_words else None,result_AL=int(blocked),returned_AX=u.reg_read(UC_X86_REG_AX),passed=True))
for load,tile,occ,tf,of,deltas in itertools.product((0,0x1000),(0,1,255),(0,164,255),(0,2,8,10,255),(0,2,255),((0,0),(1000,1000),(32768,32768))):validator(load,tile,occ,tf,of,*deltas)
flag_cases=len(cases)
for load,state,kind,mode,strategy,orient,compare,command in itertools.product((0,0x1000),(0,1,2,3,4,65535),(0x32,0x33,0x3c,0x3d,255),(0,6,8),(0,1),(0,2),(-1,0,1),(0,255)):validator(load,7,164,8,0,1000,1000,state,kind,mode,strategy,orient,compare,command,group='door')
door_cases=len(cases)-flag_cases
for load,deltas in itertools.product((0,0x1000),((-43,0),(-42,0),(-41,0),(0,41),(0,42),(41,41),(41,42),(32768,0),(0,32768),(32767,0),(65535,65535))):validator(load,1,164,0,0,*deltas,group='distance_edges')
for load,orient,base in itertools.product((0,0x1000),(0,2),(0xfff0,0x8000)):validator(load,1,164,8,0,1000,1000,1,0x32,6,1,orient,0,255,base,'coordinate_wrap')
edge_cases=len(cases)-flag_cases-door_cases
save('cases',cases)
helper_cases=[]
for load,count,query,initialds in itertools.product((0,0x1000),(0,1,2,64,65535),('first','last','absent','alias'),(0,1)):
 u,ds,seg=setup(load);u.mem_write(seg*16,struct.pack('<H',count));n=count if count<32768 else 0
 for k in range(n):u.mem_write(seg*16+0x3076+18*k+4,struct.pack('<HH',0x373e+2*k,seg))
 if query=='first':off,qseg=0x373e,seg;found=n>0;which=0
 elif query=='last':off,qseg=0x373e+2*(n-1 if n else 0),seg;found=n>0;which=n-1
 elif query=='alias':off,qseg=0x372e,seg+1;found=False;which=None
 else:off,qseg=0x573c,seg;found=False;which=None
 diagnostic=[]
 def error(uc,address,size,user):
  if address==(load+0xfba)*16+0xc:
   sp=uc.reg_read(UC_X86_REG_SP);assert struct.unpack('<H',bytes(uc.mem_read(ds*16+sp+4,2)))[0]==0x42;assert bytes(uc.mem_read(ds*16+0x42,16))==b'Door not in map\0';diagnostic.append(True);uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,error);regs(u,load,ds,0,[off,qseg],initial_ds=0x1234 if initialds else ds);u.emu_start(load*16,0x50100,count=4000)
 assert bool(diagnostic)==(not found)
 if found:assert (u.reg_read(UC_X86_REG_AX),u.reg_read(UC_X86_REG_DX))==(0x3076+18*which,seg) and u.reg_read(UC_X86_REG_SP)==0xf004
 assert u.reg_read(UC_X86_REG_DS)==ds
 helper_cases.append(dict(kind='lookup',load=load,state_or_count=count,query=query,initial_DS_differs=initialds,result=int(found),passed=True))
for load,state,ah,(ip,kind) in itertools.product((0,0x1000),(0,1,2,3,4,65535),(0,0xab),((0x1e0,'state04'),(0x1fc,'state1'))):
 u,ds,seg=setup(load);u.mem_write(seg*16+0x3076+8,struct.pack('<H',state));regs(u,load,ds,0,[0x3076,seg],ah=ah);u.emu_start(load*16+ip,0x50100,count=100);expected=(state in (0,4)) if kind=='state04' else state==1;assert u.reg_read(UC_X86_REG_AL)==expected and u.reg_read(UC_X86_REG_AH)==ah and u.reg_read(UC_X86_REG_SP)==0xf004
 helper_cases.append(dict(kind=kind,load=load,state_or_count=state,query='',initial_DS_differs=0,result=int(expected),passed=True))
save('helper_cases',helper_cases)
s=dict(functions=functions,cases=len(cases)+len(helper_cases),validator_cases=len(cases),flag_cases=flag_cases,door_cases=door_cases,edge_cases=edge_cases,helper_cases=len(helper_cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='whole original0254 plus original door lookup/state predicates; motion00B0/transition012A/interaction00000598 stubbed; missing-door lookup tests stop at diagnostic entry, no nonreturn/error closure; normal validator DS=SS, lookup separately proves DS restored fromSS; ALonly boolean, command WORD highBYTE residual retained',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
