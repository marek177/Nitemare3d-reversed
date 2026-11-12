"""IMAGE INVENTORY DECODER EMULATOR OUT: whole original2065 with original scan/grow-disabled/newblock helpers."""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,inventory,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
from crt_far_malloc_model import FarMallocModel
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(exist_ok=True);root=out.parent;old={x['image_offset']:x for x in json.loads(inventory.read_text(encoding='utf-8'))};sources=[root/'pass1_crt_allocator_state/allocator_instructions.csv',root/'near_heap_scan/near_heap_next_fit_scan.csv',root/'near_heap_grow/near_heap_grow.csv',root/'near_heap_grow/near_heap_last_block.csv',root/'pass1_near_heap_flags/near_heap_resize_or_accept.csv']+[root/'pass1_heap_root'/(x+'.csv') for x in ('heap_block_initialize','heap_root_append','heap_os_allocate')];allowed=set();owner={}
for p in sources:
 for x in csv.DictReader(p.open()):
  a=int(x['image_offset']);raw=bytes.fromhex(x['bytes']);assert b[a:a+len(raw)]==raw and old[a]['bytes']==raw.hex();allowed.add(a);owner[a]=p.stem
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));configs=[];cases=[];visited=set();write_rows=[];scan_rows=[]
# Every whole-caller case exercises a boundary between existing separately analyzed helpers.
for n in (1,2,3):
 for freebits in itertools.product((0,1),repeat=n):
  for cached,request in itertools.product(range(n),(0,1,7,8,15,16,31,63,128,8198)):
   configs.append(dict(heaps=n,freebits=freebits,cached=cached,request=request,replies=[[False,8]],cursor_tail=False))
for n,request in itertools.product((0,1,2),(0,1,15,16,8198,65512,65513,65535)):
 configs.append(dict(heaps=n,freebits=(0,)*n,cached=0,request=request,replies=[[True,0xb000]],cursor_tail=True))
for flags,free,quantum,request,policy in itertools.product((1,3),(0,1),(16,8192),(64,8198,32767),(0,1,2)):
 configs.append(dict(heaps=1,freebits=(free,),cached=0,request=request,replies=[[False,8]],cursor_tail=True,growth_flags=flags,quantum=quantum,resize_replies=([[True,0]] if policy==0 else [[False,8],[True,0]] if policy==1 else [[False,8],[False,8]])))
for load,c in itertools.product((0x824,0x1000),configs):
 raw=bytearray(b)
 for x in rel:struct.pack_into('<H',raw,int(x['image_offset']),(int(x['original_word'])+load)&65535)
 ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(raw)]=raw;ds=load+0x2771;base=ds*16;segments=[0x5000+0x2000*i for i in range(c['heaps'])];stack=0xf000;lo,hi=base+stack-64,base+stack+8
 for off in (0x2332,0x2334,0x20f6,0x20f8):struct.pack_into('<H',ram,base+off,0)
 head=segments[0] if segments else 0;last=segments[-1] if segments else 0;cached=segments[c['cached']] if segments else 0;struct.pack_into('<8H',ram,base+0x2336,0,head,0,cached,0,last,0,c.get('quantum',0x2000))
 for i,s in enumerate(segments):
  # Two adjacent blocks, free states force coalescing or cross-heap traversal.
  p=s*16;tail=56;struct.pack_into('<10H',ram,p,s,c.get('growth_flags',0),58,20,tail if c['cursor_tail'] else 20,tail,0,segments[i+1] if i+1<len(segments) else 0,0,segments[i-1] if i else 0);struct.pack_into('<H',ram,p+20,16+c['freebits'][i]);struct.pack_into('<H',ram,p+38,16+c['freebits'][i]);struct.pack_into('<H',ram,p+tail,0xfffe)
 frame=struct.pack('<3H',0x200,0x4e00,c['request']);ram[base+stack:base+stack+6]=frame;model=FarMallocModel(ram,ds);model.allocate(c['request'],c['replies'],c.get('resize_replies',[]));want=iter(model.writes);call=0;done=[];stores=[]
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram))
 for reg,v in [(UC_X86_REG_CS,load+0x11ee),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,stack),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,0x402)]:u.reg_write(reg,v)
 def code(e,a,n,d):
  if a==0x4e200:done.append(True);e.emu_stop();return
  q=a-load*16;assert q in allowed,hex(q);visited.add(q)
 def intr(e,n,d):
  global call
  assert n==0x21;x=model.calls[call];call+=1;assert e.reg_read(UC_X86_REG_AH)==(0x48 if x['kind']=='DOS48' else 0x4a);assert e.reg_read(UC_X86_REG_BX)==x['paragraphs'];
  if x['kind']=='DOS4A':assert e.reg_read(UC_X86_REG_ES)==x['ES']
  f=e.reg_read(UC_X86_REG_EFLAGS);e.reg_write(UC_X86_REG_AX,x['segment_or_error']);e.reg_write(UC_X86_REG_EFLAGS,(f&~1) if x['success'] else f|1)
 def write(e,access,a,n,v,d):
  if lo<=a and a+n<=hi:return
  expected=next(want,None);assert (a,n,v&((1<<(n*8))-1))==expected,(c,hex(a),n,v,expected);stores.append((a,n,v&((1<<(n*8))-1)))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((load+0x11ee)*16+0x2065,0x1fffff,count=20000);assert done and next(want,None) is None and call==len(model.calls);actual=bytes(u.mem_read(0,len(ram)));assert actual[:lo]==model.ram[:lo] and actual[hi:]==model.ram[hi:]
 assert (u.reg_read(UC_X86_REG_AX),u.reg_read(UC_X86_REG_DX))==model.result
 for reg,v in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,stack+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)]:assert u.reg_read(reg)==v
 assert bytes(u.mem_read(base+stack,6))==frame;cid=len(cases)
 for j,x in enumerate(stores):write_rows.append(dict(case=cid,index=j,address=x[0],size=x[1],value=x[2]))
 scan_rows.append(dict(case=cid,segments=';'.join('%04X'%s for s in model.scans)))
 cases.append(dict(case=cid,load=load,config=json.dumps(c),result_offset=model.result[0],result_segment=model.result[1],DOS48_calls=call,nonstack_stores=len(stores),whole_RAM_bytes_checked=len(ram)-(hi-lo),status='PASS'))
def save(name,rows):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save('cases',cases);save('ordered_writes',write_rows);save('heap_scan_order',scan_rows);save('instruction_execution_coverage',[dict(image_offset=a,function=owner[a],executed=a in visited) for a in sorted(allowed)])
s=dict(functions=[],cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,caller_starts_executed=sum(a in visited and owner[a]=='allocator_instructions' for a in allowed),caller_starts_unexecuted=sorted(a for a in allowed if owner[a]=='allocator_instructions' and a not in visited),scope='Whole original2065+scan+nonPSPgrow+OSblockinit/rootappend; two loads,one-to-threevalidheaps,cachedrotation,coalescing,secondscanpass,OSfailure/freshblocksuccess,oversize. Only DOS48/4Afixtures; callbacksnull,PSPflag4growth/corruptchains outsidecurrentdomain. Full2MiBRAMexcept72Bcontrolstack/exactorderedstores/frames/registers. Existingfunctionsreused.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in [image,inventory,image.parent/'relocations.csv',Path(__file__),Path(__file__).with_name('crt_far_malloc_model.py')]+sources])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
