"""IMAGE DECODER EMULATOR OUT: eight DOS free-marker bodies and original DOS10 cleanup callee integration.
DOS10cache reset/near-mark remain explicit fixtures; original FAR-free bodies execute, no DOS interrupt.
"""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,decoder,emulator,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,Mnemonic,Register,OpKind
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_INTR
from unicorn.x86_const import *
sha=lambda x:hashlib.sha256(x).hexdigest();b=image.read_bytes();pattern=b[0x13f32:0x13f45];assert pattern.hex()=='558bec56c476068cc1e30526804cfe015e5dcb';out.mkdir(exist_ok=True);root=out.parent;versions=Path(r'C:\Users\Marek-Medved\Documents\Codex\2026-10-25\goal-x20-5\outputs');comparisons=[];files=[image,Path(__file__)];mapped={};fmt=Formatter(FormatterSyntax.INTEL)
for label in ('10','11','12','15','17','18','19','20'):
 invpath=versions/('N3D-'+label)/'instructions.json';vpath=invpath.with_name('unpacked_image.bin');v=vpath.read_bytes();inv=json.loads(invpath.read_text(encoding='utf-8'));lookup={x['image_offset']:x for x in inv};hits=[p for p in lookup if v.startswith(pattern,p)];assert len(hits)==1;start=hits[0];entry=lookup[start];cs,ip=entry['cs'],entry['ip'];rows=list(Decoder(16,v[start:start+19],ip=ip));assert len(rows)==10 and rows[-1].flow_control==FlowControl.RETURN
 for i in rows:assert lookup[cs*16+i.ip]['bytes']==v[cs*16+i.ip:cs*16+i.next_ip].hex()
 mapped[label]=dict(start=start,cs=cs,ip=ip,bytes=v,inventory=inv);comparisons.append(dict(version=label,cs=cs,ip=ip,start=start,end_exclusive=start+19,instructions=10,instruction_bytes=19,raw_equal_DOS20=True,CFG_equal_DOS20=True,image_sha256=sha(v),scope='same19B body/noabsoluteoperands; validpointer ABI/byte-mark semantics only,notentireheap/gameparity'));files.extend((vpath,invpath))
# Version10 cleanup's extra per-image FAR release calls this exact helper, not DOS49.
fpath=root/'cache_cleanup_versions/function_comparisons.csv';ipath=root/'cache_cleanup_versions/instructions.csv';files.extend((fpath,ipath));entry=next(x for x in csv.DictReader(fpath.open()) if x['version']=='10' and x['function']=='level_resource_cleanup');cs,ip,lo,hi=(int(entry[k]) for k in ('cs','ip','start','end_exclusive'));v=mapped['10']['bytes'];rows=[x for x in csv.DictReader(ipath.open()) if x['version']=='10' and x['function']=='level_resource_cleanup'];ins=[]
for row in rows:
 p=int(row['image_offset']);raw=bytes.fromhex(row['bytes']);assert v[p:p+len(raw)]==raw;i=Decoder(16,raw,ip=int(row['ip'])).decode();assert i.len==len(raw);ins.append(i)
calls=[i for i in ins if i.flow_control==FlowControl.CALL];assert len(calls)==5;reset=calls[0].far_branch_selector*16+calls[0].far_branch16;near=calls[1].far_branch_selector*16+calls[1].far_branch16;far=calls[2].far_branch_selector*16+calls[2].far_branch16;assert far==mapped['10']['start']
counts=[]
for i in ins:
 if i.mnemonic==Mnemonic.CMP and i.memory_base==Register.NONE and i.memory_index==Register.NONE and i.memory_displacement>0x1000 and i.memory_displacement not in counts:counts.append(i.memory_displacement)
assert len(counts)==3;wc,oc,ac=counts;wall=next(i.immediate(1) for i in ins if i.mnemonic==Mnemonic.MOV and i.op0_register==Register.SI and i.op1_kind==OpKind.IMMEDIATE16 and i.immediate(1)>0x1000);bank=next(i.memory_displacement for i in ins if i.mnemonic==Mnemonic.MOV and i.op0_register==Register.AX and i.memory_base==Register.BX and i.memory_displacement>0x1000);obj=bank-4;world=next(i.memory_displacement for i in ins if i.mnemonic==Mnemonic.MOV and i.op0_register==Register.ES);allowed={int(x['image_offset']) for x in rows}|set(range(far,far+19));cases=[];eventrows=[]
for layout,tag,kind in itertools.product((-1,0,1,3),(0x24,0x25),('distinct','shared','zero_segment')):
 ram=bytearray(0x200000);ram[:len(v)]=v;ds=0x7000;base=ds*16;ram[base:base+0xe030]=b'\x66'*0xe030;populated=layout>=0
 for off,value in ((wc,2 if populated else 0),(oc,2 if populated else 0),(ac,3 if populated else 0),(world,0x6000)):struct.pack_into('<H',ram,base+off,value)
 expected_events=[('cache_reset',2)];marker_stores=[]
 if populated:
  for n in range(2):struct.pack_into('<H',ram,base+wall+8*n,0x9002+0x100*n);expected_events.append(('near_mark',0x9002+0x100*n))
  for n in range(2):
   ptr=0xa002+0x100*n;struct.pack_into('<4H',ram,base+obj+8*n,layout,0,0xb002+0x100*n,ptr)
   for k in range(layout):
    off=0x2000 if kind=='shared' else 0x2000+(n*4+k)*0x100;seg=0 if kind=='zero_segment' else 0x5000;pointer=(seg<<16)|off;struct.pack_into('<I',ram,base+ptr+10*k+6,pointer);expected_events.append(('far_marker',pointer))
    if seg:address=seg*16+off-2;ram[address]=tag;ram[address+1]=0xa4;marker_stores.append((address,1,tag|1))
   expected_events.append(('near_mark',ptr))
  expected_events.extend([('near_mark',0xb002),('near_mark',0xb102)])
  for n,cls in enumerate((0,0,1)):ram[0x60000+10+28*n]=cls
 stack=0xf000;lo_stack,hi_stack=base+stack-64,base+stack+8;frame=struct.pack('<HH',0x200,0x4e00);ram[base+stack:base+stack+4]=frame;expected=bytearray(ram)
 for address,n,value in marker_stores:expected[address]=value
 if populated:
  for off in (bank,bank+8):struct.pack_into('<H',expected,base+off,0)
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));events=[];done=[];writes=[]
 for reg,value in [(UC_X86_REG_CS,cs),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,stack),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2)]:u.reg_write(reg,value)
 def code(e,address,n,d):
  if address==0x4e200:done.append(True);e.emu_stop();return
  if address in (reset,near,far):
   sp=e.reg_read(UC_X86_REG_SP);rip,rcs=struct.unpack('<HH',bytes(e.mem_read(base+sp,4)));name='cache_reset' if address==reset else 'near_mark' if address==near else 'far_marker';n=4 if address==far else 2;value=int.from_bytes(bytes(e.mem_read(base+sp+4,n)),'little');events.append((name,value))
   if address!=far:e.reg_write(UC_X86_REG_SP,sp+4);e.reg_write(UC_X86_REG_CS,rcs);e.reg_write(UC_X86_REG_IP,rip)
   return
  assert address in allowed,hex(address)
 def write(e,access,address,n,value,d):
  if not(lo_stack<=address and address+n<=hi_stack):writes.append((address,n,value&((1<<(8*n))-1)))
 def interrupt(e,n,d):raise AssertionError('no DOS calls in original marker/caller')
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_INTR,interrupt);u.emu_start(cs*16+ip,0x1fffff,count=10000);assert done and events==expected_events;actual=bytes(u.mem_read(0,len(ram)));assert actual[:lo_stack]==expected[:lo_stack] and actual[hi_stack:]==expected[hi_stack:]
 expected_stores=marker_stores+([(base+bank,2,0),(base+bank+8,2,0)] if populated else []);assert writes==expected_stores
 for reg,value in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,stack+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)]:assert u.reg_read(reg)==value
 assert bytes(u.mem_read(base+stack,4))==frame;cid=len(cases)
 for j,(name,value) in enumerate(events):eventrows.append(dict(case=cid,index=j,callee=name,argument=value))
 cases.append(dict(case=cid,layout=layout,input_tag=tag,pointer_kind=kind,original_far_marker_calls=sum(name=='far_marker' for name,value in events),original_byte_stores=len(marker_stores),nonstack_store_events=len(writes),whole_RAM_bytes_checked=len(ram)-(hi_stack-lo_stack),status='PASS'))
def save(name,data):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
save('function_comparisons',comparisons);save('DOS10_caller_cases',cases);save('DOS10_caller_events',eventrows);s=dict(comparisons=len(comparisons),unique_images=len({x['image_sha256'] for x in comparisons}),raw_body_matches=8,CFG_matches=8,DOS10_caller_cases_separate=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,DOS10_cleanup_far_target=far,scope='EightDOSlabels/sevenimages haveidentical19Bmarker.24separateDOS10cleanupcases executeoriginalcaller+originalmarker; cacheReset/nearMarkfixtures preserved,notfullcleanupcalleeclosure. Per-image release marks BYTE notDOS49/physicaldeallocation; pointerfields/payload unchanged. Full2MiBRAMexcept72controlstack/exactorderedstores/frames checked. NoWin16parity.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in files]);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
