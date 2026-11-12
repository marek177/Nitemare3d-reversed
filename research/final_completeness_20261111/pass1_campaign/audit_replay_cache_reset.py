"""IMAGE INVENTORY DECODER EMULATOR OUT: full bounded dispatch ASM; reset/cleanup paths.
Modes0/1 are decoded but not claimed executed by these reset-only tests.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
from cache_reset_model import CacheResetModel
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(exist_ok=True);old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rows):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
functions=[];starts={};visited={}
for name,cs,lo,hi in [('cache_lifecycle_dispatch_012',0x768,0x24,0x293),('level_resource_cleanup',0xd29,0x80e,0x8a9)]:
 todo=[lo];dec={};edges=[]
 while todo:
  ip=todo.pop()
  if ip in dec:continue
  assert lo<=ip<hi;i=Decoder(16,b[cs*16+ip:cs*16+hi],ip=ip).decode();assert not i.is_invalid;dec[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 rows=[]
 for ip,i in sorted(dec.items()):
  p=cs*16+ip;raw=b[p:cs*16+i.next_ip];assert old[p]['bytes']==raw.hex();rows.append(dict(cs=cs,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);save(name+'_cfg',edges);functions.append(dict(name=name,start=cs*16+lo,end_exclusive=cs*16+hi,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows)));starts[name]=set(r['image_offset'] for r in rows);visited[name]=set()
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));runtime={};cases=[]
for load in (0x824,0x1000):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 runtime[load]=bytes(raw)
def run(load,kind,count,pattern,cursor,layout=0,mode=2,selector_override=False):
 ram=bytearray(0x100000);ram[load*16:load*16+len(b)]=runtime[load];ds=load+0x2771;base=ds*16;ram[base:base+0xe030]=b'\x66'*0xe030
 def word(off,value):struct.pack_into('<H',ram,base+off,value&65535)
 def far(off,address):struct.pack_into('<HH',ram,base+off,address&15,address>>4)
 word(0x3504,count);word(0xc9c,cursor);word(0x350a,0x345);word(0x3506,37);word(0x2560,load+0x1be7);word(0x256c,load+0x21fd);word(0x20e8,0x9000);word(0x20ea,0xf000)
 if selector_override:word(0x2560,load+0x1c08)
 ram[base+0x350c]=1;ram[base+0x3cce]=1
 for i in range(14):
  p=0x40000+i*0x3000;far((0x34cc+4*i) if i<10 else (0x34f4+4*(i-10)),p);ram[p:p+0x2006]=b'\x5a'*0x2006;struct.pack_into('<I',ram,p,0x12340000+i)
  owner=0 if pattern=='none' else 0x7000 if pattern=='shared' else 0x7000+10*i
  struct.pack_into('<H',ram,p+4,owner if i<10 else 0x3030+i)
  if i<10 and owner:struct.pack_into('<I',ram,base+owner+6,0xdeadbeef)
 for i in range(128):
  p=0x70000+i*0x1000;struct.pack_into('<HH',ram,(load+0x1be7)*16+4*i,0,p>>4);ram[p:p+0xc02]=b'\x5a'*0xc02;owner=0 if pattern=='none' else 0x7000 if pattern=='shared' else 0x7400+10*i;struct.pack_into('<H',ram,p,owner)
  if owner:struct.pack_into('<I',ram,base+owner+6,0xcafebabe)
 wc,oc,classes={0:(0,0,[]),1:(2,0,[]),2:(0,3,[1,1,2]),3:(2,3,[1,2,1,0,2])}[layout];word(0x6272,wc);word(0x6274,oc);word(0x6270,len(classes))
 for i in range(wc):word(0x4316+8*i,0xa002+0x100*i);ram[base+0xa000+0x100*i]=2
 for i in range(oc):word(0x3d24+8*i,0xa202+0x100*i);ram[base+0xa200+0x100*i]=2
 for cls in set(classes):word(0x3d22+8*cls,0xa502+0x100*cls);ram[base+0xa500+0x100*cls]=2
 for i,cls in enumerate(classes):ram[(load+0x21fd)*16+10+28*i]=cls
 stack=0xf000;lo,hi=base+stack-64,base+stack+8;cs=load+(0xd29 if kind=='cleanup' else 0x768);ip=0x80e if kind=='cleanup' else 0x24;frame=struct.pack('<3H',0x100,0x5000,mode);ram[base+stack:base+stack+6]=frame
 expected=CacheResetModel(ram,ds)
 if kind=='cleanup':expected.cleanup()
 elif mode==2:expected.reset()
 assert all(not (w['address']<hi and w['address']+w['size']>lo) for w in expected.writes)
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,bytes(ram));done=[];observed=[];executed=[]
 for reg,value in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_ES,0x7777),(UC_X86_REG_SP,stack),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,value)
 def hook(emu,address,size,data):
  if address==0x50100:done.append(True);emu.emu_stop();return
  p=address-load*16;executed.append(p)
  for name,ss in starts.items():
   if p in ss:visited[name].add(p)
  assert (0x76a4<=p<0x7913) or (0xda9e<=p<0xdb39) or (0x15b8e<=p<0x15baf),hex(p)
 def write(emu,access,address,size,value,data):
  if lo<=address and address+size<=hi:return
  observed.append((address,size,value&((1<<(8*size))-1)))
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(cs*16+ip,0xfffff,count=30000);assert done
 actual=bytes(u.mem_read(0,len(ram)));assert actual[:lo]==expected.ram[:lo] and actual[hi:]==expected.ram[hi:]
 assert observed==[(w['address'],w['size'],w['value']) for w in expected.writes],(kind,count,pattern,cursor,layout)
 for reg,value in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_SP,stack+4)]:assert u.reg_read(reg)==value
 assert bytes(u.mem_read(base+stack,6))==frame and struct.unpack_from('<H',actual,base+0xc9c)[0]==cursor
 cases.append(dict(load=load,kind=kind,mode=mode,signed_count=count,owner_pattern=pattern,cursor=cursor,metadata_layout=layout,mutable_selector_changed=selector_override,nonstack_write_events=len(observed),marked_pointer_calls=len(expected.marks),whole_RAM_bytes_checked=len(ram)-(hi-lo),instructions=len(executed),status='PASS'))
for args in itertools.product((0x824,0x1000),(0,1,2,5,62,128,-1),('none','all','shared'),(0,7)):run(args[0],'reset',*args[1:])
for args in itertools.product((0x824,0x1000),(1,5,128),('none','all','shared'),(0,7),range(4)):run(args[0],'cleanup',*args[1:4],layout=args[4])
for load,mode in itertools.product((0x824,0x1000),(3,0x100,0xffff)):run(load,'invalid_mode',2,'all',7,mode=mode)
for load,kind in itertools.product((0x824,0x1000),('reset','cleanup')):run(load,kind,5,'all',7,layout=3,selector_override=True)
save('cases',cases);save('instruction_execution_coverage',[dict(function=n,image_offset=p,executed=p in visited[n]) for n in starts for p in sorted(starts[n])])
s=dict(functions=functions,cases=len(cases),failures=0,executed_instruction_starts=sum(map(len,visited.values())),unexecuted_starts={n:sorted(starts[n]-visited[n]) for n in starts},runtime_tests=0,new_deep_verified_bytes=0,scope='Whole original lifecycle entry on mode2/invalidWORD modes and whole levelcleanup+original near-mark helper,no stubs/OS. Init0/shutdown1 CFG decoded but not exercised here. Full1MiBRAM except72B synthetic control stack and exact ordered nonstack write events including same-value stores compared;cursor retained,shared metadata/banks marked not physically freed.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',Path(__file__).with_name('cache_reset_model.py'),Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
