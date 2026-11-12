"""IMAGE INVENTORY DECODER EMULATOR OUT: extend existing CRT2A16 large successes, add DOS free wrapper.
DOS48/49 and optional retry callback responses are fixtures. No CRT allocation/free replacement.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
from crt_large_allocation_model import LargeAllocationModel
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(exist_ok=True);old={r['image_offset']:r for r in json.loads(inventory.read_text(encoding='utf-8'))};fmt=Formatter(FormatterSyntax.INTEL);starts={};functions=[]
def save(name,rows):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for name,lo,hi in [('crt_DOS_free_far',0x2a0a,0x2a16),('existing_crt_zeroed_far_allocate',0x2a16,0x2aea)]:
 todo=[lo];dec={};edges=[]
 while todo:
  ip=todo.pop()
  if ip in dec:continue
  assert lo<=ip<hi;i=Decoder(16,b[0x11ee0+ip:0x11ee0+hi],ip=ip).decode();assert not i.is_invalid;dec[ip]=i
  if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
  if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
 rows=[]
 for ip,i in sorted(dec.items()):
  p=0x11ee0+ip;raw=b[p:0x11ee0+i.next_ip];assert old[p]['bytes']==raw.hex();rows.append(dict(cs=0x11ee,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
 save(name,rows);save(name+'_cfg',edges);starts[name]=set(x['image_offset'] for x in rows)
 if not name.startswith('existing'):functions.append(dict(name=name,start=0x11ee0+lo,end_exclusive=0x11ee0+hi,instructions=len(rows),instruction_bytes=sum(len(bytes.fromhex(x['bytes'])) for x in rows)))
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[];events=[];coverage=set();layoutrows=[]
configs=[]
def config(count,size,**kw):
 c=dict(count=count,size=size,os_replies=[[True,0x5000]],callback_actions=[],callback_form='null',watermark=0,lower_limit=0);c.update(kw)
 if c not in configs:configs.append(c)
for p in (1,65520,65535,65536,65537,65552,131071,131072,131073,196608,262144,263168,327680,524288):config(p,1)
for n,size in ((21845,3),(21846,3),(43690,3),(43691,3),(2,65535),(3,65535),(0,1),(1,0),(0xffffffff,1),(0x100000,1),(0xffff0,1),(0xffff1,1),(0x80000000,2),(0xaaaaaaab,3)):
 layout=LargeAllocationModel.layout(n,size);config(n,size,os_replies=[[False,8]] if layout and layout[0]*16>524288 else [[True,0x5000]])
for size in (3,5,7):
 inv=pow(size,-1,1<<32)
 for p in (0x10000,0x1ffff,0x20000,0x20001):config((p*inv)&0xffffffff,size)
for n in (65552,131072,263168):
 for watermark in (0x1000,0xf000):config(n,1,watermark=watermark)
config(65552,1,os_replies=[[True,0xf000]])
config(65552,1,os_replies=[[True,0xf100]])
config(512,1,os_replies=[[True,0xfff0]])
config(65552,1,lower_limit=0x4800,os_replies=[[True,0x4700],[True,0x4800],[True,0x5000]])
config(65552,1,lower_limit=0x4800,os_replies=[[True,0x4700],[False,8]])
for form in ('offset_only','segment_only','both'):
 config(0,3,callback_form=form,callback_actions=[dict(AX=0)])
 config(0,3,callback_form=form,callback_actions=[dict(AX=0xffff,count=263168,size=1)])
 config(65552,1,callback_form=form,os_replies=[[False,8],[True,0x5000]],callback_actions=[dict(AX=1)])
 config(65552,1,callback_form=form,os_replies=[[False,8],[False,8]],callback_actions=[dict(AX=0xffff),dict(AX=0)])
for load,df,c in itertools.product((0x824,0x1000),(0,1),configs):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(raw)]=raw;ds=load+0x2771;base=ds*16;stack=0xf000;lo,hi=base+stack-64,base+stack+8
 off,seg={'null':(0,0),'offset_only':(0xf100,0),'segment_only':(0,0x4f10),'both':(0x100,0x4f00)}[c['callback_form']];callback=seg*16+off
 if callback:ram[callback]=0xcb
 for o,v in [(0x20f6,c['watermark']),(0x20f8,c['lower_limit']),(0x246a,off),(0x246c,seg)]:struct.pack_into('<H',ram,base+o,v)
 frame=struct.pack('<HHIH',0x200,0x4e00,c['count'],c['size']);ram[base+stack:base+stack+10]=frame;hi=base+stack+10
 model=LargeAllocationModel(ram,ds,c['count'],c['size'],c['os_replies'],c['callback_actions']);model.run();wanted=iter(model.expected_writes());observed=[];state=dict(call=0,writes=0);stop=[]
 for kind,a,n,value in model.operations:
  if kind=='zero_words':assert not(a<load*16+len(raw) and a+n>load*16) and not(a<hi and a+n>lo),(c,hex(a),n)
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram))
 for reg,v in [(UC_X86_REG_CS,load+0x11ee),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,stack),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2|(df<<10))]:u.reg_write(reg,v)
 def call():
  k=state['call'];assert k<len(model.calls);state['call']+=1;return model.calls[k]
 def interrupt(e,n,data):
  assert n==0x21 and e.reg_read(UC_X86_REG_AH)==0x48;x=call();assert x['kind']=='DOS48' and e.reg_read(UC_X86_REG_BX)==x['paragraphs'];flags=e.reg_read(UC_X86_REG_EFLAGS);e.reg_write(UC_X86_REG_AX,x['segment_or_error']);e.reg_write(UC_X86_REG_EFLAGS,(flags&~1) if x['success'] else flags|1)
 def hook(e,address,size,data):
  if address==0x4e200:stop.append(True);e.emu_stop();return
  if callback and address==callback:
   x=call();assert x['kind']=='callback';sp=e.reg_read(UC_X86_REG_SP);args=struct.unpack('<HI',bytes(e.mem_read(base+sp+4,6)));assert args==(x['size'],x['count']);e.reg_write(UC_X86_REG_AX,x['return_AX']);e.mem_write(base+stack+4,struct.pack('<IH',x['new_count'],x['new_size']));return
  p=address-load*16;assert p in starts['existing_crt_zeroed_far_allocate'];coverage.add(p)
 def write(e,access,address,size,value,data):
  if lo<=address and address+size<=hi:return
  want=next(wanted,None);assert (address,size,value&((1<<(8*size))-1))==want,(c,hex(address),size,value,want);state['writes']+=1
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_INTR,interrupt);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((load+0x11ee)*16+0x2a16,0x1fffff,count=400000);assert stop and state['call']==len(model.calls) and next(wanted,None) is None
 actual=bytes(u.mem_read(0,len(ram)));assert actual[:lo]==model.ram[:lo] and actual[hi:]==model.ram[hi:]
 assert (u.reg_read(UC_X86_REG_AX),u.reg_read(UC_X86_REG_DX))==model.result
 for reg,v in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,stack+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)]:assert u.reg_read(reg)==v
 assert bytes(u.mem_read(base+stack,4))==frame[:4] and bytes(u.mem_read(base+stack+4,6))==struct.pack('<IH',model.count,model.size)
 assert bool(u.reg_read(UC_X86_REG_EFLAGS)&0x400)==(False if model.df_cleared else bool(df))
 cid=len(cases)
 for j,x in enumerate(model.calls):events.append(dict(case=cid,index=j,detail=json.dumps(x,sort_keys=True)))
 for j,x in enumerate(model.operations):
  if x[0]=='zero_words':layoutrows.append(dict(case=cid,index=j,physical_start=x[1],end_exclusive=x[1]+x[2],length=x[2],role='segmented zero-fill span; synthetic DOS response'))
 cases.append(dict(case=cid,kind='large_allocate',load=load,input_DF=df,config=json.dumps(c,sort_keys=True),returned_offset=model.result[0],returned_segment=model.result[1],zeroed_bytes=sum(x[2] for x in model.operations if x[0]=='zero_words'),nonstack_store_events=state['writes'],whole_RAM_bytes_checked=len(ram)-(hi-lo),status='PASS'))
# Direct original DOS49 wrapper: FAR offset argument is ignored; ES receives segment WORD.
for load,offset,segment,cf in itertools.product((0x824,0x1000),(0,0x1234,0xffff),(0,1,0x5000,0xffff),(0,1)):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 ds=load+0x2771;base=ds*16;stack=0xf000;ram=bytearray(0x200000);ram[load*16:load*16+len(raw)]=raw;frame=struct.pack('<4H',0x200,0x4e00,offset,segment);ram[base+stack:base+stack+8]=frame;lo,hi=base+stack-64,base+stack+8;u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));done=[];seen=[];writes=[]
 for reg,v in [(UC_X86_REG_CS,load+0x11ee),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,stack),(UC_X86_REG_BP,0x1234),(UC_X86_REG_EFLAGS,0x402)]:u.reg_write(reg,v)
 def intr(e,n,data):
  assert n==0x21 and e.reg_read(UC_X86_REG_AH)==0x49 and e.reg_read(UC_X86_REG_ES)==segment;seen.append(True);e.reg_write(UC_X86_REG_AX,0x1234 if not cf else 7);flags=e.reg_read(UC_X86_REG_EFLAGS);e.reg_write(UC_X86_REG_EFLAGS,(flags|1) if cf else flags&~1)
 def code(e,a,n,d):
  if a==0x4e200:done.append(True);e.emu_stop();return
  p=a-load*16;assert p in starts['crt_DOS_free_far'];coverage.add(p)
 def wr(e,access,a,n,v,d):
  if not(lo<=a and a+n<=hi):writes.append((a,n,v))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_MEM_WRITE,wr);u.emu_start((load+0x11ee)*16+0x2a0a,0x1fffff,count=30);actual=bytes(u.mem_read(0,len(ram)));assert done and len(seen)==1 and not writes and actual[:lo]==ram[:lo] and actual[hi:]==ram[hi:];assert u.reg_read(UC_X86_REG_SP)==stack+4 and u.reg_read(UC_X86_REG_BP)==0x1234 and u.reg_read(UC_X86_REG_AX)==(0x1234 if not cf else 7) and u.reg_read(UC_X86_REG_ES)==segment and bool(u.reg_read(UC_X86_REG_EFLAGS)&1)==bool(cf) and u.reg_read(UC_X86_REG_EFLAGS)&0x400
 assert u.reg_read(UC_X86_REG_DS)==ds and u.reg_read(UC_X86_REG_SS)==ds and bytes(u.mem_read(base+stack,8))==frame
 cases.append(dict(case=len(cases),kind='DOS_free',load=load,input_DF=1,config=json.dumps(dict(offset=offset,segment=segment,fixture_CF=cf)),returned_offset=u.reg_read(UC_X86_REG_AX),returned_segment=segment,zeroed_bytes=0,nonstack_store_events=0,whole_RAM_bytes_checked=len(ram)-(hi-lo),status='PASS'))
save('cases',cases);save('dependency_events',events);save('zero_fill_spans',layoutrows);save('instruction_execution_coverage',[dict(function=name,image_offset=p,executed=p in coverage) for name in starts for p in sorted(starts[name])])
s=dict(functions=functions,cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,reused_allocator_starts=97,reused_allocator_executed_starts=len(coverage&starts['existing_crt_zeroed_far_allocate']),unexecuted_allocator_starts=sorted(starts['existing_crt_zeroed_far_allocate']-coverage),scope='Extend original CRT2A16 large-success/alignment/multichunk/wrap/retry domains; only DOS48/49 and callbackresponses fixtures. Existing212B allocator reused; add12B DOSfreewrapper. Full2MiBRAM except72or74controlstackB and exactorderednonstackstores; synthetic highsegments are not nativeDOScapacity/A20 proof. Callbackbody not closed.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,inventory,image.parent/'relocations.csv',Path(__file__).with_name('crt_large_allocation_model.py'),Path(__file__))])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
