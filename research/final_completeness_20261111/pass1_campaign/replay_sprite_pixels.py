"""python replay_sprite_pixels.py IMAGE EMULATOR OUT
Original whole function; sequencer OUT and planar store effects observed in hooks.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,emu,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(emu.resolve()))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INSN,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';rel=list(csv.DictReader((image.parent/'relocations.csv').open()));out.mkdir(parents=True,exist_ok=True);cases=[];events=[]
for load,x,page,width,height,scale,pattern,depthmode,bypass in itertools.product((0,0x1000),range(4),(0xa000,0xa400),(2,5),(2,5),(1,2,3),(0,1,2),(0,1,2,3),(0,1)):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));ds=load+0x2771;cs=load+0x156;slot=0x50f2;resource=0x8000;y=3;rows=height*scale;cols=width*scale;step=(height<<16)//rows
 # No clipping: isolate the complete pixel/depth/mask loop from prefix edge domains.
 for off,val in {6:resource,8:x,10:x+cols-2,12:y,14:y+rows-1,16:0x1234}.items():u.mem_write(ds*16+slot+off,struct.pack('<H',val))
 u.mem_write(ds*16+slot+2,struct.pack('<HH',0x100,0x7000));u.mem_write(0x70105,bytes([0x10 if bypass else 0]));u.mem_write(ds*16+resource,bytes([width,height]));u.mem_write(ds*16+resource+6,struct.pack('<HH',0x2000,0x6000));u.mem_write(ds*16+0x12e,struct.pack('<H',page))
 for off,val in zip((0x4548,0x454a,0x454c,0x454e),(0,319,0,199)):u.mem_write(ds*16+off,struct.pack('<H',val))
 source=bytes(31 if pattern==0 or pattern==2 and n%3==0 else (n*17+pattern*37)&255 for n in range(width*height));u.mem_write(0x62000,source)
 depths=[0x1233,0x1234,0x1235,0x8000]
 for n in range(cols):u.mem_write(ds*16+0x47e4+2*(x+n),struct.pack('<H',depths[(n+depthmode)%4]))
 expected_pixels=[];expected_ports=[(0x3c4,1,2)];mask=((0x11<<x)|(0x11>>(8-x)))&255
 for col in range(cols):
  expected_ports.append((0x3c5,1,mask));sx=(col*step)>>16
  if bypass or depths[(col+depthmode)%4]<=0x1234:
   for row in range(rows):
    sy=(row*step)>>16;v=source[sx*height+sy]
    if v!=31:expected_pixels.append((page*16+(y+row)*80+(x+col)//4,1,v,mask&15))
  # Source-width exit occurs before writing next plane mask.
  if ((col+1)*step)>>16>=width:break
  if col+1==cols:
   expected_ports.append((0x3c5,1,((mask<<1)|(mask>>7))&255))
   break
  mask=((mask<<1)|(mask>>7))&255
 observed_ports=[];observed_pixels=[];state={'mask':0,'index':None}
 def port(uc,number,size,value,user):
  observed_ports.append((number,size,value));assert size==1
  if number==0x3c4:state['index']=value
  else:assert number==0x3c5 and state['index']==2;state['mask']=value&15
 def write(uc,access,address,size,value,user):
  if 0xa0000<=address<0xb0000:observed_pixels.append((address,size,value,state['mask']))
 u.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT);u.hook_add(UC_HOOK_MEM_WRITE,write)
 for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x4567),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x6789),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
 u.mem_write(ds*16+0xff00,struct.pack('<HHH',0x6000,cs,slot));u.emu_start(cs*16+0x5de,cs*16+0x6000,count=10000)
 assert observed_ports==expected_ports,(load,x,width,height,scale,observed_ports,expected_ports)
 assert observed_pixels==expected_pixels,(load,x,width,height,scale,pattern,depthmode,bypass,observed_pixels[:8],expected_pixels[:8])
 for reg,val in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xff04),(UC_X86_REG_BP,0x4567),(UC_X86_REG_SI,0x5678),(UC_X86_REG_DI,0x6789),(UC_X86_REG_ES,page)]:assert u.reg_read(reg)==val
 # A four-plane observational model: low sequencer bits select the planes changed by each CPU store.
 planes=[bytearray(b'\xa5'*0x10000) for _ in range(4)];expected_planes=[bytearray(b'\xa5'*0x10000) for _ in range(4)]
 for rs,ps in [(observed_pixels,planes),(expected_pixels,expected_planes)]:
  for address,size,value,maskbits in rs:
   assert size==1
   for plane in range(4):
    if maskbits&(1<<plane):ps[plane][address-page*16]=value
 assert planes==expected_planes
 case=len(cases);cases.append(dict(case=case,load=load,x=x,page=page,width=width,height=height,scale=scale,pattern=pattern,depthmode=depthmode,bypass=bypass,stores=len(observed_pixels),port_writes=len(observed_ports),planes_sha256=sha(b''.join(planes)),passed=True))
 # Retain representative exact events, not millions of redundant rows.
 if load==0 and width==5 and height==5 and pattern==2 and depthmode==0:
  events.extend(dict(case=case,order=n,address=a,size=z,value=v,plane_mask=m) for n,(a,z,v,m) in enumerate(observed_pixels))
def save(name,rs):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
save('cases',cases);save('representative_stores',events)
s=dict(image_sha256=sha(b),cases=len(cases),failures=0,cases_sha256=sha((out/'cases.csv').read_bytes()),runtime_tests=0,new_deep_verified_bytes=0,scope='whole native0156:05DE with unclipped positive dimensions and x alignment0..3; OUT observed/modelled sequencer, four-plane observational store model; no DOSBox hardware/output parity; prior prefix cases count separately')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
