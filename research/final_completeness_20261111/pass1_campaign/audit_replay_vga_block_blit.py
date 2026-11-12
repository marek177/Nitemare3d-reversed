"""python audit_replay_vga_block_blit.py IMAGE INVENTORY DECODER EMULATOR CD_ASSET OUT
Whole original 0156:07DE; observed OUT/memory accesses, explicit VGA plane model.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,asset_path,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INSN,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();asset=asset_path.read_bytes()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297' and sha(asset)=='af574568089f1998ca50ceeba310ff068c728279ff470cd39f47a8919228b95a'
out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
todo=[0x7de];decoded={};edges=[];rows=[]
while todo:
 ip=todo.pop()
 if ip in decoded:continue
 assert 0x7de<=ip<0x88c;i=Decoder(16,b[0x1560+ip:0x1dec],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
 if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough'))
for ip,i in sorted(decoded.items()):
 p=0x1560+ip;raw=b[p:0x1560+i.next_ip];assert lookup[p]['bytes']==raw.hex();rows.append(dict(cs=0x156,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
save('vga_column_block_blit',rows);save('vga_column_block_blit_cfg',edges)
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];representative=[]
def make(load):
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
 for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 u.mem_write(load*16,bytes(runtime));return u
def registers(u,cs,ds,ss,sp,df):
 for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,sp),(UC_X86_REG_BP,0x3456),(UC_X86_REG_SI,0x4567),(UC_X86_REG_DI,0x5678),(UC_X86_REG_EFLAGS,2|df*1024)]:u.reg_write(reg,val)
def observe(u,source_start=None,limit=None):
 ports=[];writes=[];reads=[];state=dict(index=None,mask=0)
 def port(uc,number,size,value,user):
  ports.append((number,size,value));assert size==1
  if number==0x3c4:state['index']=value
  else:assert number==0x3c5 and state['index']==2;state['mask']=value&15
 def memwrite(uc,access,address,size,value,user):
  if 0xa0000<=address<0xb4000:
   writes.append((address,size,value,state['mask']))
   if limit and len(writes)>=limit:uc.emu_stop()
 def memread(uc,access,address,size,value,user):
  if source_start is not None and source_start<=address<source_start+65536:reads.append((address,size))
 u.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT);u.hook_add(UC_HOOK_MEM_WRITE,memwrite)
 # A global read hook in Unicorn2.1.4 can replay RETF with stale IP in this
 # fixture. Observe only the explicit source segment, excluding return stack.
 if source_start is not None:u.hook_add(UC_HOOK_MEM_READ,memread,None,source_start,source_start+65535)
 return ports,writes,reads
source=bytes((0,1,31,127,128,255,42,63)[n%8] for n in range(65536))
geometry=[(1,1,1,0x200,0),(3,4,3,0x201,0xffff),(0,9,5,2,320),(8,5,2,0xfffe,0x1234)]
for load,x,y,pagechoice,key,geo,df in itertools.product((0,0x1000),(0,1,2,3,319,65535),(0,199,256),(0,1),(0xffff,0x8000,31,1,0x101),geometry,(0,1)):
 stride,cols,height,offset,unused=geo;u=make(load);cs=load+0x156;ds=load+0x2771;ss=ds+(0x500 if load else 0);srcseg=0x7000+load;page=0xa000 if pagechoice==0 else 0xa400
 u.mem_write(srcseg*16,source);u.mem_write(ds*16+0x12c,struct.pack('<HH',0xa400,0xa000));ports,writes,reads=observe(u,srcseg*16)
 expected_ports=[(0x3c4,1,2)];expected_writes=[];expected_reads=[];mask=((0x11<<(x&3))|(0x11>>(8-(x&3))))&255
 expected_ports.append((0x3c5,1,mask));base=((y&255)*80+(x>>2))&65535;src=offset
 for col in range(cols):
  di=base;si=src
  for row in range(height):
   value=source[si];expected_reads.append((srcseg*16+si,1));si=(si+(-1 if df else 1))&65535
   if key&0x8000 or value!=(key&255):expected_writes.append((page*16+di,1,value,mask&15))
   di=(di+(78 if df and key&0x8000 else 80))&65535
  carry=mask>>7;mask=((mask<<1)|(mask>>7))&255;expected_ports.append((0x3c5,1,mask));base=(base+carry)&65535;src=(src+stride)&65535
 registers(u,cs,ds,ss,0xf000,df);args=(offset,srcseg,x,y,unused,stride,cols,height,pagechoice,key)
 u.mem_write(ss*16+0xf000,struct.pack('<'+'H'*12,0x6000,cs,*args));u.emu_start(cs*16+0x7de,cs*16+0x6000,count=10000)
 assert ports==expected_ports and writes==expected_writes and reads==expected_reads,(load,x,y,pagechoice,key,geo,df,ports[:5],writes[:5],expected_writes[:5])
 for reg,val in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,0xf004),(UC_X86_REG_BP,0x3456),(UC_X86_REG_SI,0x4567),(UC_X86_REG_DI,0x5678),(UC_X86_REG_ES,page)]:assert u.reg_read(reg)==val,(load,x,y,pagechoice,key,geo,df,reg,u.reg_read(reg),val,u.reg_read(UC_X86_REG_IP))
 assert bool(u.reg_read(UC_X86_REG_EFLAGS)&1024)==bool(df)
 case=len(cases);cases.append(dict(case=case,kind='whole_function',load=load,x=x,y=y,pagechoice=pagechoice,key=key,stride=stride,columns=cols,rows=height,source_offset=offset,unused_word=unused,df=df,ds_equals_ss=ds==ss,source_reads=len(reads),stores=len(writes),port_writes=len(ports),passed=True))
 if load==0 and x==319 and y==199 and key==31 and geo==geometry[1] and df==0:
  representative.extend(dict(case=case,order=n,address=a,size=z,value=value,mask=m) for n,(a,z,value,m) in enumerate(writes))

# Zero LOOP counters mean 65536 iterations, not an empty rectangle. Retain only
# a bounded first16-store witness, without claiming whole pathological calls.
bounded=[]
for load,cols,height in itertools.product((0,0x1000),(0,1),(0,1)):
 if cols and height:continue
 u=make(load);cs=load+0x156;ds=load+0x2771;u.mem_write(ds*16+0x12c,struct.pack('<HH',0xa400,0xa000));u.mem_write(0x70000,source)
 ports,writes,reads=observe(u,0x70000,16);registers(u,cs,ds,ds,0xf000,0);u.mem_write(ds*16+0xf000,struct.pack('<12H',0x6000,cs,0x200,0x7000,0,0,0,1,cols,height,0,0xffff))
 u.emu_start(cs*16+0x7de,cs*16+0x6000,count=10000);assert len(writes)==16 and u.reg_read(UC_X86_REG_IP)!=0x6000
 bounded.append(dict(load=load,columns=cols,rows=height,bounded_stores=16,returned=False,passed=True))
save('zero_counter_prefix_cases',bounded)

# Full real-asset integration: original PCX decoder calls original renderer.
# Only CRT file operations and fatal error handler are modelled.
q=128;pixels=bytearray()
while len(pixels)<64000:
 value=asset[q];q+=1;count=1
 if value&192==192:count=value&63;value=asset[q];q+=1
 pixels.extend(bytes([value])*count)
assert len(pixels)==64000
integration=[]
for load,page in itertools.product((0,0x1000),(0xa000,0xa400)):
 u=make(load);cs=load+0x277;ds=load+0x2771;crt=(load+0x11ee)*16;u.mem_write(ds*16+0x12c,struct.pack('<HH',0xa400,page))
 targets={crt+0x6e6:'open',crt+0x6fc:'read',crt+0x5fa:'close',(load+0xfba)*16+0xc:'fatal'}
 for a in targets:u.mem_write(a,b'\xcb')
 state=dict(position=0,row=0,closed=False);ports,writes,reads=observe(u)
 def code(uc,address,size,user):
  ss=uc.reg_read(UC_X86_REG_SS);sp=uc.reg_read(UC_X86_REG_SP)
  def args(n):return struct.unpack('<'+'H'*n,bytes(uc.mem_read(ss*16+sp+4,n*2)))
  if address==(load+0x156)*16+0x7de:
   a=args(10);row=state['row'];assert a[1:]==(ds,0,row,320,1,320,1,0,65535)
   assert bytes(uc.mem_read(ds*16+a[0],320))==pixels[row*320:(row+1)*320];state['row']+=1
  if address not in targets:return
  op=targets[address]
  if op=='open':assert args(2)==(0x1c87,0x64b);uc.reg_write(UC_X86_REG_AX,0x7000)
  elif op=='read':
   dest,size,count,stream=args(4);assert stream==0x7000 and count==1;chunk=asset[state['position']:state['position']+size];assert len(chunk)==size
   uc.mem_write(ds*16+dest,chunk);state['position']+=size;uc.reg_write(UC_X86_REG_AX,1)
  elif op=='close':assert args(1)==(0x7000,);state['closed']=True;uc.reg_write(UC_X86_REG_AX,0)
  else:raise AssertionError('unexpected fatal')
 u.hook_add(UC_HOOK_CODE,code);registers(u,cs,ds,ds,0xf000,0);u.mem_write(ds*16+0xf000,struct.pack('<HHH',0x6000,cs,0x1c87));u.emu_start(cs*16+0x1600,cs*16+0x6000,count=4000000)
 assert u.reg_read(UC_X86_REG_IP)==0x6000 and state['row']==200 and state['closed'] and state['position']==q
 expected_writes=[];expected_ports=[];planes=[bytearray(16000) for _ in range(4)]
 for y in range(200):
  mask=0x11;expected_ports.extend([(0x3c4,1,2),(0x3c5,1,mask)])
  for x in range(320):
   value=pixels[y*320+x];expected_writes.append((page*16+y*80+x//4,1,value,mask&15));planes[x%4][y*80+x//4]=value
   mask=((mask<<1)|(mask>>7))&255;expected_ports.append((0x3c5,1,mask))
 assert ports==expected_ports and writes==expected_writes
 observed=[bytearray(16000) for _ in range(4)]
 for a,z,value,mask in writes:
  assert z==1
  for p in range(4):
   if mask&(1<<p):observed[p][a-page*16]=value
 assert observed==planes
 integration.append(dict(load=load,page=page,rows=200,stores=len(writes),port_writes=len(ports),stream_end=q,plane0_sha256=sha(planes[0]),plane1_sha256=sha(planes[1]),plane2_sha256=sha(planes[2]),plane3_sha256=sha(planes[3]),passed=True))
save('cases',cases);save('representative_stores',representative);save('real_asset_integration_cases',integration)
summary=dict(image_sha256=sha(b),functions=[dict(name='vga_column_block_blit',start=0x1d3e,end_exclusive=0x1dec,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows))],cases=len(cases)+len(integration),standalone_cases=len(cases),integration_cases=len(integration),bounded_zero_counter_cases_separate=len(bounded),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='whole original0156:07DE observed port/memory events; matrix includes DF1 and coordinate/source wrapping; four real CD asset integrations with original PCX decoder and row renderer, only CRT/fatal mocked; VGA planes modelled, no natural DOSBox output or hardware parity; zero counter prefixes counted separately',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,asset_path,Path(__file__))])
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
