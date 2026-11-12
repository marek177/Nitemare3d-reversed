"""python audit_replay_palette_load.py IMAGE INVENTORY DECODER EMULATOR PALETTE OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,emu,palette,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(dep.resolve()),str(emu.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INSN
from unicorn.x86_const import *
sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();asset=palette.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';assert len(asset)==1924 and sha(asset)=='efd52442cbee3327d8cec045b31559049e8767b298c25674a557eb6e096a759f'
out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={r['image_offset']:r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
functions=[]
for name,cs,start,end in [('game_palette_load_tail',0x277,0x2a6,0x336),('vga_palette_upload_768',0x156,0x12a,0x14f)]:
 todo=[start];decoded={};rows=[]
 while todo:
  ip=todo.pop()
  if ip in decoded:continue
  assert start<=ip<end;i=Decoder(16,b[cs*16+ip:cs*16+end],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
 for ip,i in sorted(decoded.items()):
  pos=cs*16+ip;raw=b[pos:cs*16+i.next_ip];assert lookup[pos]['bytes']==raw.hex();rows.append(dict(cs=cs,ip=ip,image_offset=pos,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);functions.append(dict(name=name,start=cs*16+start,end_exclusive=cs*16+end,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows)))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];observed_actual=[];patterns=[('real_asset',asset[-768:]),('ramp',bytes(range(256))*3)]+[('constant_%d'%n,bytes([n])*768) for n in (0,1,3,4,127,128,252,255)]
for load in (0,0x1000):
 for name,raw_palette in patterns:
  u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);runtime=bytearray(b)
  for r in rel:struct.pack_into('<H',runtime,int(r['image_offset']),(int(r['original_word'])+load)&65535)
  u.mem_write(load*16,bytes(runtime));ds=load+0x2771;cs=load+0x277;crt=(load+0x11ee)*16
  targets={crt+0x1c72:'open',crt+0x1bd6:'seek',crt+0x1e14:'read',crt+0x1bb6:'close',(load+0xfba)*16+0xc:'fatal',cs*16+0x188:'query'}
  for addr in targets:u.mem_write(addr,b'\xcb')
  state={'reads':0,'calls':[]};ports=[]
  def code(uc,address,size,user):
   if address not in targets:return
   op=targets[address];ss=uc.reg_read(UC_X86_REG_SS);sp=uc.reg_read(UC_X86_REG_SP);args=lambda n:struct.unpack('<'+'H'*n,bytes(uc.mem_read(ss*16+sp+4,n*2)))
   state['calls'].append(op)
   if op=='open':
    filename,flags=args(2);assert (filename,flags)==(0x245,0x8000);assert bytes(uc.mem_read(ds*16+filename,9))==b'game.pal\0';uc.reg_write(UC_X86_REG_AX,7)
   elif op=='seek':
    handle,lo,hi,origin=args(4);assert (handle,lo,hi,origin)==(7,0xfd00,0xffff,2);uc.reg_write(UC_X86_REG_AX,len(asset)-768);uc.reg_write(UC_X86_REG_DX,0)
   elif op=='read':
    handle,dest,count=args(3);n=state['reads'];assert handle==7 and count==1 and dest==0x4a64+n and n<768
    uc.mem_write(ds*16+dest,raw_palette[n:n+1]);uc.reg_write(UC_X86_REG_AX,1);state['reads']+=1
   elif op=='close':assert args(1)==(7,);uc.reg_write(UC_X86_REG_AX,0)
   elif op=='query':assert args(1)==(0,);uc.reg_write(UC_X86_REG_AX,0)
   else:raise AssertionError('unexpected fatal path')
  def port(uc,number,size,value,user):ports.append((number,size,value))
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INSN,port,None,1,0,UC_X86_INS_OUT)
  for reg,val in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,0xff00),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,val)
  u.mem_write(ds*16+0xff00,struct.pack('<HH',0x6000,cs));u.emu_start(cs*16+0x2a6,cs*16+0x6000,count=40000)
  expected=bytes(n>>2 for n in raw_palette);assert bytes(u.mem_read(ds*16+0x4a64,768))==expected
  assert ports==[(0x3c8,1,0)]+[(0x3c9,1,n) for n in expected]
  assert state['calls']==['open','seek']+['read']*768+['query','close']
  for reg,val in [(UC_X86_REG_DS,ds),(UC_X86_REG_SP,0xff04),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)]:assert u.reg_read(reg)==val
  cases.append(dict(load=load,pattern=name,source_offset=len(asset)-768,source_bytes=768,source_sha256=sha(raw_palette),converted_sha256=sha(expected),read_calls=state['reads'],port_writes=len(ports),passed=True))
  if load==0 and name=='real_asset':observed_actual=[dict(order=n,port=port,size=size,value=value) for n,(port,size,value) in enumerate(ports)]
save('cases',cases);save('real_asset_dac_writes',observed_actual)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),palette_path=str(palette.resolve()),palette_sha256=sha(asset),palette_size=len(asset),palette_tail_offset=len(asset)-768,palette_tail_sha256=sha(asset[-768:]),converted_palette_sha256=sha(bytes(n>>2 for n in asset[-768:])),functions=functions,cases=len(cases),failures=0,cases_sha256=sha((out/'cases.csv').read_bytes()),runtime_tests=0,new_deep_verified_bytes=0,scope='original loader and DAC upload bodies; modeled file open/seek/read/close and post-upload query, observed/modelled OUT; real asset tail plus synthetic BYTE patterns, not natural DOS I/O or hardware DAC readback')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
