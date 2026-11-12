"""IMAGE INVENTORY DECODER EMULATOR OUT: original2052 BYTEfree marker and whole malloc reuse.
No DOS/API fixtures for marker; only DOS48failure when reused malloc cannot fit seeded heaps.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
from crt_far_malloc_model import FarMallocModel
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(exist_ok=True);old={x['image_offset']:x for x in json.loads(inventory.read_text(encoding='utf-8'))};fmt=Formatter(FormatterSyntax.INTEL);todo=[0x2052];dec={};edges=[]
while todo:
 ip=todo.pop()
 if ip in dec:continue
 assert 0x2052<=ip<0x2065;i=Decoder(16,b[0x11ee0+ip:0x13f45],ip=ip).decode();assert not i.is_invalid;dec[ip]=i
 if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
 if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
rows=[]
for ip,i in sorted(dec.items()):
 p=0x11ee0+ip;raw=b[p:0x11ee0+i.next_ip];assert old[p]['bytes']==raw.hex();rows.append(dict(cs=0x11ee,ip=ip,image_offset=p,bytes=raw.hex(),instruction=fmt.format(i)))
def save(name,data):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
save('crt_far_free_mark',rows);save('crt_far_free_mark_cfg',edges);starts={x['image_offset'] for x in rows};covered=set();rel=list(csv.DictReader((image.parent/'relocations.csv').open()));cases=[]
runtimes={}
for load in (0x824,0x1000):
 raw=bytearray(b)
 for x in rel:struct.pack_into('<H',raw,int(x['image_offset']),(int(x['original_word'])+load)&65535)
 runtimes[load]=bytes(raw)
configs=[(0x100,0x6000,tag) for tag in range(256)]+list(itertools.product((0,1,2,3,0xfffe,0xffff),(0,0x6000,0x8000,0xfff0),(0,0x7e,0x80,0xff)))
for load,split,(off,seg,tag) in itertools.product((0x824,0x1000),(False,True),configs):
 ds=0x1234 if split else load+0x2771;ss=0x4800 if split else ds;stack=0xf000;base=ss*16;lo,hi=base+stack-64,base+stack+8;ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(b)]=runtimes[load];frame=struct.pack('<4H',0x200,0x4e00,off,seg);ram[base+stack:base+stack+8]=frame;address=seg*16+((off-2)&65535);ram[address]=tag;ram[address+1]=0xa4;expected=bytearray(ram)
 if seg:expected[address]=tag|1
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));done=[];writes=[]
 seeds=[(UC_X86_REG_CS,load+0x11ee),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,stack),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_AX,0x4567),(UC_X86_REG_BX,0x5678),(UC_X86_REG_DX,0x6789),(UC_X86_REG_EFLAGS,0x403)]
 for reg,v in seeds:u.reg_write(reg,v)
 def code(e,a,n,d):
  if a==0x4e200:done.append(True);e.emu_stop();return
  p=a-load*16;assert p in starts;covered.add(p)
 def intr(e,n,d):raise AssertionError('marker has no OS/callee call')
 def write(e,access,a,n,v,d):
  if lo<=a and a+n<=hi:return
  writes.append((a,n,v))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((load+0x11ee)*16+0x2052,0x1fffff,count=40);assert done and writes==([(address,1,tag|1)] if seg else []);actual=bytes(u.mem_read(0,len(ram)));assert actual[:lo]==expected[:lo] and actual[hi:]==expected[hi:]
 for reg,v in seeds:
  if reg not in (UC_X86_REG_CS,UC_X86_REG_SP,UC_X86_REG_EFLAGS):assert u.reg_read(reg)==v
 assert u.reg_read(UC_X86_REG_SP)==stack+4 and u.reg_read(UC_X86_REG_ES)==seg and u.reg_read(UC_X86_REG_CX)==seg and bytes(u.mem_read(base+stack,8))==frame;flags=u.reg_read(UC_X86_REG_EFLAGS);assert bool(flags&1)==(not bool(seg)) and flags&0x400
 cases.append(dict(case=len(cases),kind='direct_marker',load=load,split_SS_DS=split,config=json.dumps(dict(offset=off,segment=seg,tag=tag)),marker_calls=1,malloc_request='',returned_offset='',returned_segment='',DOS_calls=0,nonstack_stores=len(writes),unchanged_value_store=bool(seg and tag&1),whole_RAM_bytes_checked=len(ram)-(hi-lo),status='PASS'))
# Valid allocated blocks: whole original free marker(s), then whole original malloc/helper chain.
root=out.parent;sources=[root/'pass1_crt_allocator_state/allocator_instructions.csv',root/'near_heap_scan/near_heap_next_fit_scan.csv',root/'near_heap_grow/near_heap_grow.csv',root/'near_heap_grow/near_heap_last_block.csv',root/'pass1_near_heap_flags/near_heap_resize_or_accept.csv']+[root/'pass1_heap_root'/(n+'.csv') for n in ('heap_block_initialize','heap_root_append','heap_os_allocate')];allowed=set(starts)
for source in sources:allowed.update(int(x['image_offset']) for x in csv.DictReader(source.open()))
for load,mask,duplicate,cursor,request in itertools.product((0x824,0x1000),range(8),(False,True),(20,30,48,74),(0,8,9,16,17,24,48,64)):
 if not mask and duplicate:continue
 ds=load+0x2771;base=ds*16;ss=ds;stack=0xf000;lo,hi=base+stack-64,base+stack+8;ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(b)]=runtimes[load]
 for o in (0x2332,0x2334,0x20f6,0x20f8):struct.pack_into('<H',ram,base+o,0)
 struct.pack_into('<8H',ram,base+0x2336,0,0x6000,0,0x6000,0,0x6000,0,0x2000);struct.pack_into('<10H',ram,0x60000,0x6000,0,76,20,cursor,74,0,0,0,0)
 for o,n in ((20,8),(30,16),(48,24),(74,0xfffe)):struct.pack_into('<H',ram,0x60000+o,n)
 freed=[p for j,p in enumerate((22,32,50)) if mask&(1<<j)]
 if duplicate and freed:freed.append(freed[0])
 expected=bytearray(ram);expected_writes=[]
 for off in freed:a=0x60000+off-2;expected[a]|=1;expected_writes.append((a,1,expected[a]))
 model=FarMallocModel(expected,ds);model.allocate(request,[[False,8]]);expected_writes+=model.writes;wanted=iter(expected_writes);u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));stores=[];state=dict(DOS=0);done=[]
 def code2(e,a,n,d):
  if a==0x4e200:done.append(True);e.emu_stop();return
  assert a-load*16 in allowed
 def write2(e,access,a,n,v,d):
  if lo<=a and a+n<=hi:return
  want=next(wanted,None);assert (a,n,v&((1<<(8*n))-1))==want;stores.append(want)
 def intr2(e,n,d):
  assert n==0x21 and e.reg_read(UC_X86_REG_AH)==0x48;x=model.calls[state['DOS']];state['DOS']+=1;assert not x['success'] and e.reg_read(UC_X86_REG_BX)==x['paragraphs'];e.reg_write(UC_X86_REG_AX,8);e.reg_write(UC_X86_REG_EFLAGS,e.reg_read(UC_X86_REG_EFLAGS)|1)
 u.hook_add(UC_HOOK_CODE,code2);u.hook_add(UC_HOOK_MEM_WRITE,write2);u.hook_add(UC_HOOK_INTR,intr2)
 for off in freed+[None]:
  f=struct.pack('<4H',0x200,0x4e00,off,0x6000) if off is not None else struct.pack('<3H',0x200,0x4e00,request);u.mem_write(base+stack,f)
  for reg,v in [(UC_X86_REG_CS,load+0x11ee),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ss),(UC_X86_REG_SP,stack),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,0x403)]:u.reg_write(reg,v)
  u.emu_start((load+0x11ee)*16+(0x2052 if off is not None else 0x2065),0x1fffff,count=20000)
  assert u.reg_read(UC_X86_REG_SP)==stack+4 and bytes(u.mem_read(base+stack,len(f)))==f
 assert len(done)==len(freed)+1 and state['DOS']==len(model.calls) and next(wanted,None) is None;actual=bytes(u.mem_read(0,len(ram)));assert actual[:lo]==model.ram[:lo] and actual[hi:]==model.ram[hi:] and (u.reg_read(UC_X86_REG_AX),u.reg_read(UC_X86_REG_DX))==model.result
 cases.append(dict(case=len(cases),kind='marker_then_original_malloc',load=load,split_SS_DS=False,config=json.dumps(dict(mask=mask,duplicate=duplicate,cursor=cursor,freed_offsets=freed)),marker_calls=len(freed),malloc_request=request,returned_offset=model.result[0],returned_segment=model.result[1],DOS_calls=state['DOS'],nonstack_stores=len(stores),unchanged_value_store=bool(duplicate),whole_RAM_bytes_checked=len(ram)-(hi-lo),status='PASS'))
assert covered==starts;save('cases',cases);save('instruction_execution_coverage',[dict(image_offset=p,executed=p in covered) for p in sorted(starts)])
s=dict(functions=[dict(name='crt_far_free_mark',start=0x13f32,end_exclusive=0x13f45,instructions=len(rows),instruction_bytes=19)],cases=len(cases),direct_marker_cases=sum(x['kind']=='direct_marker' for x in cases),whole_reuse_cases=sum(x['kind']!='direct_marker' for x in cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='Original2052mark BYTE atES:(offset-2)&FFFF iff segmentnonzero; no externalcalls. Directall256lowbytes/offsetwrap/zero-segment/splitSSDS plus wholeoriginalmallocreuse/coalescing,onlyDOS48failurefixture onexhaustion. Full2MiBRAMexcept72controlstackB/exactstores/frames; pointersnonaliascode/stack. Syntheticupperaddresses notDOSvalidity/A20proof.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in [image,inventory,image.parent/'relocations.csv',Path(__file__),Path(__file__).with_name('crt_far_malloc_model.py')]+sources])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
