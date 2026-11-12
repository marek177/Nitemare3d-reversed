"""IMAGE RELOCS RUNTIME WORK EMULATOR: verify native large allocation/free and no-fixture original zero suffix.
Native whole-RAM parity is not claimed: IRQ/audio state outside the scoped DGROUP/buffer remains explicit.
"""
import csv,hashlib,json,re,struct,sys
from pathlib import Path
from crt_far_malloc_model import FarMallocModel
image,relocs,runtime,work,emulator=map(lambda p:Path(p).resolve(),sys.argv[1:]);sys.path.insert(0,str(emulator))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
r=runtime.parent;sha=lambda x:hashlib.sha256(x).hexdigest();summary=json.loads((runtime/'summary.json').read_text());assert summary['success'] and summary['source_files_unchanged'];load=summary['load_segment'];b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';expected=bytearray(b)
for row in csv.DictReader(relocs.open()):struct.pack_into('<H',expected,int(row['image_offset']),(int(row['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==expected and sha(bytes(expected))==summary['runtime_image_sha256'];assert sha((r/'runtime_watch_crt_far_malloc_v2.py').read_bytes())==summary['harness_sha256'];assert summary['exe_sha256']=='a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832'
assert sha((r/'dosbox_watch_support_newgame_v1.py').read_bytes())==summary['support_sha256']=='64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89'
trace=json.loads((runtime/'transcript.json').read_text());stages=json.loads((runtime/'snapshots.json').read_text());points=[];groups={};reg=None;last=-10
for index,t in enumerate(trace):
 cmd=t['command'];assert cmd in ('PING','EXEC EV CS EIP DS ES SS SP AX BX CX DX','EXEC EV SI DI BP','EXEC EV CF DF') or re.fullmatch(r'EXEC (?:BP [0-9A-F]+:[0-9A-F]+|BPDEL \*|RUN|MEMDUMPBIN .+)',cmd),cmd
 if cmd.startswith('EXEC EV '):
  keys={'EXEC EV CS EIP DS ES SS SP AX BX CX DX':('CS','IP','DS','ES','SS','SP','AX','BX','CX','DX'),'EXEC EV SI DI BP':('SI','DI','BP'),'EXEC EV CF DF':('CF','DF')}[cmd]
  vals=next(x.split() for x in t['response'] if re.fullmatch(r'[0-9A-Fa-f]+(?: [0-9A-Fa-f]+){%d}'%(len(keys)-1),x));d=dict(zip(keys,[int(x,16) for x in vals]))
  if len(keys)==10:reg=d
  elif len(keys)==3:assert index==last+1;reg.update(d)
  else:assert index==last+1;reg.update(d);points.append((index,dict(reg)))
  last=index
 if cmd.startswith('EXEC MEMDUMPBIN '):
  m=re.fullmatch(r'EXEC MEMDUMPBIN ([0-9A-F]+):([0-9A-F]+) ([0-9A-F]+) (.+)\.part(\d+)',cmd);assert m;seg,off,n=(int(m.group(j),16) for j in (1,2,3));path=Path(m.group(4));offset=int(m.group(5));part=Path(str(path)+'.part'+str(offset));raw=part.read_bytes();assert len(raw)==n;groups.setdefault(path,[]).append(dict(index=index,address=seg*16+off,offset=offset,length=n,path=part,raw=raw))
parts=[];origins={}
for path,rows in groups.items():
 raw=bytearray();origin=rows[0]['address']
 for x in rows:assert x['offset']==len(raw) and x['address']==origin+len(raw);raw.extend(x['raw']);parts.append(x['path'])
 assert path.read_bytes()==raw;origins[path.name]=dict(address=origin,length=len(raw),index=rows[0]['index'],last_index=rows[-1]['index'])
positions=[];previous=-1
for stage in stages:
 matches=[i for i,x in points if x==stage['registers'] and i>previous];assert matches;previous=min(matches);positions.append(previous)
s={x['stage']:x['registers'] for x in stages};p={x['stage']:positions[j] for j,x in enumerate(stages)}
def dump(name,address,length,stage):
 o=origins[name];assert o['address']==address and o['length']==length and o['index']>p[stage] and not any(t['command']=='EXEC RUN' for t in trace[p[stage]+1:o['last_index']+1]);return (work/name).read_bytes()

a=s['malloc_entry'];z=s['malloc_return'];ds=load+0x2771;base=ds*16;crt=load+0x11ee;assert (a['CS'],a['IP'],a['DS'],a['SS'])==(crt,0x2065,ds,ds)
frame=dump('malloc_entry_frame.bin',a['SS']*16+a['SP'],6,'malloc_entry');rip,rcs,request=struct.unpack('<3H',frame);assert (z['CS'],z['IP'],z['SP'])==(rcs,rip,a['SP']+4)
for key in ('DS','SS','BP','SI','DI'):assert a[key]==z[key]
before=dump('malloc_before_RAM.bin',0,0xa0000,'malloc_entry');after=dump('malloc_after_RAM.bin',0,0xa0000,'malloc_return');assert before[a['SS']*16+a['SP']:a['SS']*16+a['SP']+6]==frame
native_calls=json.loads((runtime/'DOS_events.json').read_text());assert len(native_calls)==2;pre,post=native_calls;assert (pre['CS'],pre['IP'],post['CS'],post['IP'])==(crt,0x22aa,crt,0x22ac);assert pre['AX']>>8==0x4a and post['CF']==0
for key in pre:
 if key not in ('AX','CF','IP'):assert pre[key]==post[key]
pos_pre=min(i for i,x in points if x==pre);pos_post=min(i for i,x in points if x==post);assert p['malloc_entry']<pos_pre<pos_post<p['malloc_return']
model=FarMallocModel(before+b'\0'*(0x200000-len(before)),ds);model.allocate(request,[],[(not post['CF'],post['AX'])]);assert model.result==(z['AX'],z['DX']);assert model.calls==[dict(kind='DOS4A',ES=pre['ES'],paragraphs=pre['BX'],success=True,segment_or_error=post['AX'])]
sources=[r/'pass1_crt_allocator_state/allocator_instructions.csv',r/'near_heap_scan/near_heap_next_fit_scan.csv',r/'near_heap_grow/near_heap_grow.csv',r/'near_heap_grow/near_heap_last_block.csv',r/'pass1_near_heap_flags/near_heap_resize_or_accept.csv']+[r/'pass1_heap_root'/(n+'.csv') for n in ('heap_block_initialize','heap_root_append','heap_os_allocate')];allowed=set();code_bytes=0
for source in sources:
 for row in csv.DictReader(source.open()):
  q=int(row['image_offset']);n=len(bytes.fromhex(row['bytes']));address=load*16+q;assert before[address:address+n]==after[address:address+n]==expected[q:q+n];allowed.add(q);code_bytes+=n
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(model.ram));u.mem_write(0,before+b'\0'*(len(model.ram)-len(before)));regs={'CS':UC_X86_REG_CS,'IP':UC_X86_REG_IP,'DS':UC_X86_REG_DS,'ES':UC_X86_REG_ES,'SS':UC_X86_REG_SS,'SP':UC_X86_REG_SP,'AX':UC_X86_REG_AX,'BX':UC_X86_REG_BX,'CX':UC_X86_REG_CX,'DX':UC_X86_REG_DX,'SI':UC_X86_REG_SI,'DI':UC_X86_REG_DI,'BP':UC_X86_REG_BP}
for name,key in regs.items():u.reg_write(key,a[name])
u.reg_write(UC_X86_REG_EFLAGS,2|a['CF']|(a['DF']<<10));writes=iter(model.writes);observed=[];executed=[];done=[];ints=[];stacklo=a['SS']*16+a['SP']-64;stackhi=a['SS']*16+a['SP']+8

def code(e,address,n,d):
 if address==rcs*16+rip:done.append(True);e.emu_stop();return
 q=address-load*16;assert q in allowed,hex(q);executed.append(q)
def interrupt(e,n,d):
 assert n==0x21 and not ints;ints.append(n)
 for name,key in regs.items():
  if name!='IP':assert e.reg_read(key)==pre[name],(name,e.reg_read(key),pre[name])
 flags=e.reg_read(UC_X86_REG_EFLAGS);assert (flags&1,bool(flags&0x400))==(pre['CF'],bool(pre['DF']));e.reg_write(UC_X86_REG_AX,post['AX']);e.reg_write(UC_X86_REG_EFLAGS,(flags&~1)|post['CF'])
def write(e,access,address,n,value,d):
 if stacklo<=address and address+n<=stackhi:return
 want=next(writes,None);assert (address,n,value&((1<<(8*n))-1))==want;observed.append(want)
u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,interrupt);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(crt*16+0x2065,0x1fffff,count=20000);assert done and len(ints)==1 and next(writes,None) is None;actual=bytes(u.mem_read(0,len(model.ram)));assert actual[:stacklo]==model.ram[:stacklo] and actual[stackhi:]==model.ram[stackhi:]
for name,key in regs.items():assert u.reg_read(key)==z[name],(name,u.reg_read(key),z[name])
f=u.reg_read(UC_X86_REG_EFLAGS);assert (f&1,bool(f&0x400))==(z['CF'],bool(z['DF']))
owned={}
for address,n,value in model.writes:
 for j,x in enumerate(value.to_bytes(n,'little')):owned[address+j]=x
assert all(after[q]==value for q,value in owned.items())
clock=set(range(base+0x81e,base+0x822));assert all(after[q]==model.ram[q] for q in range(base,base+0xe030) if q not in clock)
residuals=[dict(address=q,before=before[q],native_after=after[q],replay_after=model.ram[q],category='clockDWORD endpoint delta' if q in clock else 'outside original-store model; DOS memory manager/IRQ/stack source not assigned') for q in range(len(before)) if after[q]!=actual[q]]
with (runtime/'RAM_replay_residuals.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=['address','before','native_after','replay_after','category']);w.writeheader();w.writerows(residuals)
with (runtime/'ordered_original_writes.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=['index','address','size','value']);w.writeheader();w.writerows(dict(index=j,address=x[0],size=x[1],value=x[2]) for j,x in enumerate(observed))
heapseg=model.result[1];hp=heapseg*16;oldsize=struct.unpack_from('<H',before,hp+4)[0];newsize=struct.unpack_from('<H',after,hp+4)[0];metrics=dict(request_WORD=request,returned_segment=heapseg,returned_offset=model.result[0],old_heap_size_WORD=oldsize,new_heap_size_WORD=newsize,old_heap_cursor=struct.unpack_from('<H',before,hp+8)[0],new_heap_cursor=struct.unpack_from('<H',after,hp+8)[0],DOS4A_ES=pre['ES'],DOS4A_paragraphs=pre['BX'],DOS4A_CF=post['CF'],DOS4A_AX=post['AX'],original_instruction_events=len(executed),original_unique_starts=len(set(executed)),original_ordered_nonstack_stores=len(observed),original_store_target_bytes_checked=len(owned),replay_RAM_bytes_checked=len(model.ram)-(stackhi-stacklo),native_DGROUP_bytes_checked=0xe030-4,native_replay_residual_positions=len(residuals),code_bytes_before_after_checked=code_bytes,callback_2332_before=before[base+0x2332:base+0x2336].hex(),callback_246A_before=before[base+0x246a:base+0x246e].hex(),native_writer_PCs_directly_trapped=False)
(runtime/'verification_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
files=[image,relocs,Path(__file__),r/'crt_far_malloc_model.py',r/'runtime_watch_crt_far_malloc_v2.py',r/'dosbox_watch_support_newgame_v1.py']+[runtime/n for n in ('summary.json','transcript.json','snapshots.json','DOS_events.json','inputs.csv','launch_arguments.json','runtime.conf','verification_metrics.json','RAM_replay_residuals.csv','ordered_original_writes.csv')]+list(groups)+parts+sources
for x in csv.DictReader((runtime/'inputs.csv').open(encoding='utf-8')):
 for key in ('source','copy'):
  q=Path(x[key]);assert sha(q.read_bytes())==x['sha256'];files.append(q)
exe=Path(json.loads((runtime/'launch_arguments.json').read_text())[0]);assert sha(exe.read_bytes())==summary['exe_sha256'];files.append(exe);files.extend(emulator.rglob('*.dll'));files.extend(emulator.rglob('*.pyd'))
proof=dict(verified=True,runtime_tests=1,new_deep_verified_bytes=0,summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=summary['runtime_image_sha256'],scope='Natural whole CRT2065 cache8198B allocation,existingheap3F96 grows3232to16384 viaactualDOS4AES3F96/BX400/CF0; returned3F96:0C9C. Originalcaller/scan/grow/resize replay onlyinjects1capturedDOSregisterresponse; fullreplayRAMmodel/orderedstores/capturedregsCFDF match. Nativeoriginal-storetargets/DGROUPexceptclock match,residualDOS/IRQ/stack memoryexported; notwholeDOSmanagerclosure/callbackbody/Win16parity. v1capturelacked4Atrace,uncounted.',metrics=metrics,files=[dict(path=str(q.resolve()),sha256=sha(q.read_bytes())) for q in dict.fromkeys(files)])
(runtime/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(metrics,indent=2))
