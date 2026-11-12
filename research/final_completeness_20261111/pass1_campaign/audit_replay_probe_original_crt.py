"""IMAGE RELOCS EMULATOR OUT: original probe+CRT2A16+CRT2A0A; only DOS48/49 fixtures."""
import csv,hashlib,itertools,json,struct,sys
from pathlib import Path
image,relocs,emulator,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(emulator.resolve()))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
from crt_large_allocation_model import LargeAllocationModel
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';out.mkdir(exist_ok=True);root=out.parent;allowed=set()
for folder,name in [('cache_memory_probe_replay','descending_memory_probe'),('crt_large_allocation_replay','existing_crt_zeroed_far_allocate'),('crt_large_allocation_replay','crt_DOS_free_far')]:allowed.update(int(x['image_offset']) for x in csv.DictReader((root/folder/(name+'.csv')).open()))
rel=list(csv.DictReader(relocs.open()));cases=[];callrows=[]
for load,limit,df in itertools.product((0x824,0x1000),(0,64,257,511),(0,1)):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 ram=bytearray(b'\xa5'*0x200000);ram[load*16:load*16+len(raw)]=raw;ds=load+0x2771;base=ds*16;stack=0xf000;lo,hi=base+stack-64,base+stack+8;frame=struct.pack('<HH',0x200,0x4e00);ram[base+stack:base+stack+4]=frame
 for o in (0x20f6,0x20f8,0x246a,0x246c):struct.pack_into('<H',ram,base+o,0)
 model=LargeAllocationModel(ram,ds,0,1,[],[])
 if limit:model.zero(0x5000,limit*64)
 expected=iter(model.expected_writes());u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(ram));u.mem_write(0,bytes(ram));stop=[];alloc_args=[];dos=[];frees=[];instructions=[];writes=[]
 for reg,v in [(UC_X86_REG_CS,load+0xfba),(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,stack),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456),(UC_X86_REG_EFLAGS,2|(df<<10))]:u.reg_write(reg,v)
 def code(e,a,n,d):
  if a==0x4e200:stop.append(True);e.emu_stop();return
  p=a-load*16;assert p in allowed;instructions.append(p)
  if p==0x148f6:
   sp=e.reg_read(UC_X86_REG_SP);count,size=struct.unpack('<IH',bytes(e.mem_read(base+sp+4,6)));candidate=1023-len(alloc_args);assert (count,size)==(candidate*1024,1);alloc_args.append(candidate)
 def intr(e,n,d):
  assert n==0x21;ah=e.reg_read(UC_X86_REG_AH);flags=e.reg_read(UC_X86_REG_EFLAGS)
  if ah==0x48:
   paragraphs=e.reg_read(UC_X86_REG_BX);candidate=alloc_args[-1];assert candidate>0 and paragraphs==candidate*64;success=candidate<=limit;dos.append((paragraphs,success));e.reg_write(UC_X86_REG_AX,0x5000 if success else 8);e.reg_write(UC_X86_REG_BX,paragraphs if success else limit*64);e.reg_write(UC_X86_REG_EFLAGS,(flags&~1) if success else flags|1)
  else:assert ah==0x49 and e.reg_read(UC_X86_REG_ES)==0x5000 and limit;frees.append(True);e.reg_write(UC_X86_REG_AX,0);e.reg_write(UC_X86_REG_EFLAGS,flags&~1)
 def write(e,access,a,n,v,d):
  if lo<=a and a+n<=hi:return
  want=next(expected,None);assert (a,n,v&((1<<(8*n))-1))==want;writes.append(1)
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start((load+0xfba)*16+0x58,0x1fffff,count=600000);assert stop and next(expected,None) is None;assert alloc_args==list(range(1023,(limit if limit else 0)-1,-1)) and len(frees)==bool(limit);assert len(dos)==len(alloc_args)-(not limit)
 actual=bytes(u.mem_read(0,len(ram)));assert actual[:lo]==model.ram[:lo] and actual[hi:]==model.ram[hi:];assert bytes(u.mem_read(base+stack,4))==frame and u.reg_read(UC_X86_REG_AX)==limit
 for reg,v in [(UC_X86_REG_DS,ds),(UC_X86_REG_SS,ds),(UC_X86_REG_SP,stack+4),(UC_X86_REG_BP,0x1234),(UC_X86_REG_SI,0x2345),(UC_X86_REG_DI,0x3456)]:assert u.reg_read(reg)==v
 assert bool(u.reg_read(UC_X86_REG_EFLAGS)&0x400)==(bool(df) if not limit else False)
 cid=len(cases)
 for j,(paragraphs,ok) in enumerate(dos):callrows.append(dict(case=cid,index=j,paragraphs=paragraphs,success=ok))
 cases.append(dict(case=cid,load=load,input_DF=df,DOS_capacity_fixture_KiB=limit,original_CRT_calls=len(alloc_args),DOS48_calls=len(dos),DOS49_calls=len(frees),zero_size_reached=not bool(limit),zero_size_DOS_calls=0,returned_AX=limit,original_instruction_events=len(instructions),nonstack_store_events=len(writes),whole_RAM_bytes_checked=len(ram)-(hi-lo),status='PASS'))
def save(name,rows):
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save('cases',cases);save('DOS_calls',callrows)
files=[image,relocs,Path(__file__),Path(__file__).with_name('crt_large_allocation_model.py')]+[root/folder/(name+'.csv') for folder,name in [('cache_memory_probe_replay','descending_memory_probe'),('crt_large_allocation_replay','existing_crt_zeroed_far_allocate'),('crt_large_allocation_replay','crt_DOS_free_far')]]
s=dict(functions=[],cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,scope='Whole original gameprobe+CRTlargeallocator+DOSfreewrapper; only DOS48/49 fixtures,callbacknull.16cases capacities0/64/257/511 andDF0/1,two loads. OriginalCRT rejectszero product beforeDOS; allfailed probe returns0,notzero-sizeallocation success. Full2MiBRAMexcept72controlstackB/exactorderedstores/frames/registers; not nativeDOSmemorymanagement.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in files])
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='files'},indent=2))
