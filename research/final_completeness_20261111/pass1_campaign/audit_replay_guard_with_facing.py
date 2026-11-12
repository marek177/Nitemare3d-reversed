"""python audit_replay_guard_with_validator.py IMAGE INVENTORY DECODER EMULATOR OUT"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};out.mkdir(parents=True,exist_ok=True);fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

todo=[0x422];decoded={};edges=[];rows=[]
while todo:
 ip=todo.pop()
 if ip in decoded:continue
 assert 0x422<=ip<0x6d1;i=Decoder(16,b[0x4c70+ip:0x5341],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
 if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
for ip,i in sorted(decoded.items()):
 pos=0x4c70+ip;raw=b[pos:0x4c70+i.next_ip];assert lookup[pos]['bytes']==raw.hex();rows.append(dict(cs=0x4c7,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
save('guard_axis_move_and_map_rebind',rows);save('guard_axis_move_and_map_rebind_cfg',edges)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
def s16(n):return n if n<32768 else n-65536
def mapoff(x,y):return (0x373e+(((y&0xffc0)*2)&65535)+((s16(x&0xffdf))>>5))&65535
for load,position,(dx,dy),mask,mode,rng,lookup_result in itertools.product((0,0x1000),(0,1,2),((0,0),(8,0),(-8,0),(0,8),(0,-8),(8,8),(-8,-8),(127,-128),(-128,127)),range(8),(0,6,8),(0,1),(65535,0x1234)):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for x in rel:struct.pack_into('<H',runtime,int(x['image_offset']),(int(x['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));ds=load+0x2771;seg=load+0x21fd;g=0x264e;actor=6;x,y=((3104,3360),(3073,3329),(3135,3391))[position];underlay=0 if position==0 else 0x52;token=0xa4+(position&1);old=mapoff(x,y);frame=(0,19,255)[mask%3]
 guard=bytearray(26);guard[0:2]=bytes([16,4]);guard[0xb]=mode;guard[0xd]=underlay;guard[0xe]=0x77;guard[0x13]=dx&255;guard[0x14]=dy&255
 record=bytearray(28);record[0]=token;record[3]=frame;struct.pack_into('<HHHH',record,0xc,old,seg,x,y)
 grid=bytearray(bytes([1,0x33])*4096);grid[old-0x373e+1]=token
 for row in range(64):
  for col in range(64):
   blocked_tile=(mask==1 and col>x//64) or (mask==2 and row>y//64) or (mask==3 and (row+col)&1) or mask==4 or (mask==7 and (row+col)&1)
   grid[(row*64+col)*2]=2 if blocked_tile else 1
 flags=bytearray(512);flags[2]=2;flags[256+token]=2
 if mask in (5,7):flags[256+0x33]=2
 if mask==7:flags[256+0x52]=2
 player=(x+32,y+32) if mask==6 else (0,0)
 u.mem_write(ds*16+0xd00c,bytes(flags));u.mem_write(ds*16+0x4162,struct.pack('<HH',*player))
 u.mem_write(seg*16+g,bytes(guard));u.mem_write(seg*16+actor,bytes(record));u.mem_write(seg*16+0x373e,bytes(grid));expected_grid=bytearray(grid);expected_grid[old-0x373e+1]=underlay;expected_guard=bytearray(guard);expected_record=bytearray(record)
 xprobe=(x+dx+(16 if dx>0 else -16 if dx<0 else 0))&65535;yprobe=(y+dy+(16 if dy>0 else -16 if dy<0 else 0))&65535;probes=[]
 def blocked_at(px,py):
  def absword(value):value=s16(value&65535);return s16((-value if value<0 else value)&65535)
  if absword(px-player[0])<42 and absword(py-player[1])<42:return True
  cell=mapoff(px,py)-0x373e;assert 0<=cell<8192
  return bool(flags[256+expected_grid[cell+1]]&2 or flags[expected_grid[cell]]&2)
 bx=False;by=False
 if dx:
  r=blocked_at(xprobe,(y-16)&65535);probes.append((xprobe,(y-16)&65535,r));bx=r
  if not r:r=blocked_at(xprobe,(y+16)&65535);probes.append((xprobe,(y+16)&65535,r));bx=r
 if dy:
  r=blocked_at((x-16)&65535,yprobe);probes.append(((x-16)&65535,yprobe,r));by=r
  if not r:r=blocked_at((x+16)&65535,yprobe);probes.append(((x+16)&65535,yprobe,r));by=r
 sx=0 if bx else dx;sy=0 if by else dy;move=mode!=8 or not(bx or by)
 calls=['pre']+['collision']*len(probes)
 if move:
  calls+=['vector','propagate'];struct.pack_into('<HH',expected_record,0x10,(x+sx)&65535,(y+sy)&65535)
 if mode==6 and bx and by:
  calls.append('rng')
  if rng&1:sx=-dx;expected_guard[0x13]=sx&255
  else:sy=-dy;expected_guard[0x14]=sy&255
 if sx or sy:
  f=(frame+1)&255;expected_record[3]=16 if 20<=f else f
 expected_guard[0x11]=(4 if sy>0 else 0 if sy<0 else expected_guard[0x11]) if sx==0 else (3 if sy>0 else 1 if sy<0 else 2) if sx>0 else (5 if sy>0 else 7 if sy<0 else 6)
 calls+=['motion','lookup'];nx,ny=struct.unpack_from('<HH',expected_record,0x10);new=mapoff(nx,ny);struct.pack_into('<HH',expected_record,0xc,new,seg);expected_guard[0xd]=expected_grid[new-0x373e+1];expected_grid[new-0x373e+1]=token
 if lookup_result!=65535:expected_guard[0xe]=lookup_result&255
 targets={(load+0x83d)*16+0x19e4:'pre',(load+0x4c7)*16+0x254:'collision',(load+0x637)*16+0x4b4:'vector',(load+0xaea)*16+0x15e:'propagate',(load+0xfba)*16+0x1a0:'rng',(load+0x4c7)*16+0xb0:'motion',(load+0xf7)*16+0x176:'lookup'}
 for addr,name in targets.items():
  if name not in ('collision','motion'):u.mem_write(addr,b'\xcb')
 assert bytes(u.mem_read((load+0x4c7)*16+0x254,0x1ce))==bytes(runtime[0x4ec4:0x5092])
 observed=[];probe_number=[0]
 def hook(uc,address,size,user):
  if address not in targets:return
  name=targets[address];observed.append(name);sp=uc.reg_read(UC_X86_REG_SP)
  def args(n):return struct.unpack('<'+'H'*n,bytes(uc.mem_read(ds*16+sp+4,n*2)))
  if name=='pre':assert args(4)==(g,seg,actor,seg)
  elif name=='collision':
   px,py,result=probes[probe_number[0]];probe_number[0]+=1;assert args(6)==(g,seg,actor,seg,px,py)
  elif name=='vector':assert args(4)==(x,y,dx if not bx else 0,dy if not by else 0) if dx>=0 and dy>=0 else args(4)==(x,y,(0 if bx else dx)&65535,(0 if by else dy)&65535)
  elif name=='propagate':assert args(4)==(actor,seg,(0 if bx else dx)&65535,(0 if by else dy)&65535)
  elif name=='rng':uc.reg_write(UC_X86_REG_AX,rng)
  elif name=='motion':assert args(4)==(g,seg,sx&65535,sy&65535)
  elif name=='lookup':assert args(2)==(new,seg);uc.reg_write(UC_X86_REG_AX,lookup_result)
 u.hook_add(UC_HOOK_CODE,hook)
 for reg,val in [(UC_X86_REG_CS,load+0x4c7),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,0xf000),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 u.mem_write(ds*16+0xf000,struct.pack('<6H',0x100,0x5000,g,seg,actor,seg));u.emu_start((load+0x4c7)*16+0x422,0x50100,count=3000)
 assert observed==calls and probe_number[0]==len(probes)
 assert bytes(u.mem_read(seg*16+g,26))==expected_guard and bytes(u.mem_read(seg*16+actor,28))==expected_record and bytes(u.mem_read(seg*16+0x373e,8192))==expected_grid
 assert u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SP)==0xf004 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_SI)==0x2345 and u.reg_read(UC_X86_REG_DI)==0x3456
 cases.append(dict(load=load,position_case=position,dx=dx,dy=dy,layout_case=mask,mode=mode,rng_bit=rng,lookup=lookup_result,blocked_x=bx,blocked_y=by,moved=move,new_map_offset=new,passed=True))
save('cases',cases)
s=dict(functions=[],cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='integrated original0422 plus original0254 validator and original00B0 facing setter; five other callees mocked, no-op mutation domain; eight shared grid/player/occupancy layouts exclude tilebit8 door interaction;512B flags, full8192B map and26/28records checked, normalDS=SS and safe position domain; no whole AI/door/path/runtime parity',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
