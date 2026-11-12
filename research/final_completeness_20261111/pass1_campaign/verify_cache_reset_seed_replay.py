"""IMAGE RELOCS RUNTIME WORK EMULATOR REPLAY_OUT: paused native RAM->controlled cleanup.
No natural/injected DOSBox reset call is claimed; native seed contributes0new runtime tests.
"""
import csv,hashlib,json,re,struct,sys
from pathlib import Path
image,relocs,runtime,work,emulator,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(emulator.resolve()));out.mkdir(exist_ok=True)
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ
from unicorn.x86_const import *
from cache_reset_model import CacheResetModel
sha=lambda b:hashlib.sha256(b).hexdigest();s=json.loads((runtime/'summary.json').read_text());assert s['success'] and s['runtime_tests']==0 and s['source_files_unchanged'];root=runtime.parent;harness=root/'runtime_watch_cache_reset_seed.py';support=root/'dosbox_watch_support_newgame_v1.py'
assert sha(harness.read_bytes())==s['harness_sha256']=='02034e6dc4c74fd72190744484c247cea0646ee239d506ed5a10f9640f3bc440';assert sha(support.read_bytes())==s['support_sha256']=='64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89'
inputs=list(csv.DictReader((runtime/'inputs.csv').open(encoding='utf-8')));assert len(inputs)==23
for r in inputs:
 for key in ('source','copy'):
  b=Path(r[key]).read_bytes();assert sha(b)==r['sha256'] and len(b)==int(r['bytes'])
canonical=image.read_bytes();assert sha(canonical)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';load=s['load_segment'];relocated=bytearray(canonical)
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',relocated,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==relocated
calls=json.loads((runtime/'cache_reset_seed_calls.json').read_text());assert len(calls)==1;c=calls[0];d=c['draw'];ds=d['post_registers']['DS'];assert ds==d['post_registers']['SS']==load+0x2771;base=ds*16;prefix=c['prefix'];seedpath=work/(prefix+'cache_reset_RAM_seed.bin');seed=seedpath.read_bytes();assert len(seed)==0xa0000
transcript=json.loads((runtime/'transcript.json').read_text());parts=[];first=None;last=None
for n,e in enumerate(transcript):
 m=re.fullmatch(r'EXEC MEMDUMPBIN ([0-9a-fA-F]+):([0-9a-fA-F]+) ([0-9a-fA-F]+) (.+)',e['command'])
 if m and Path(m[4]).name.lower().startswith(seedpath.name.lower()+'.part'):
  address=int(m[1],16)*16+int(m[2],16);size=int(m[3],16);data=Path(m[4]).read_bytes();assert len(data)==size;parts.append((address,data));first=n if first is None else first;last=n
assert len(parts)==20 and not any(e['command']=='EXEC RUN' for e in transcript[first:last+1]);position=0;joined=bytearray()
for address,data in parts:assert address==position;joined.extend(data);position+=len(data)
assert bytes(joined)==seed and position==0xa0000
# The lifecycle/cleanup/near-mark code in this live RAM must remain exactly the original relocated code.
for folder,name in [('cache_reset_replay','cache_lifecycle_dispatch_012.csv'),('cache_reset_replay','level_resource_cleanup.csv')]:
 for r in csv.DictReader((root/folder/name).open(encoding='utf-8')):
  p=int(r['image_offset']);n=len(bytes.fromhex(r['bytes']));assert seed[load*16+p:load*16+p+n]==relocated[p:p+n]
assert seed[load*16+0x15b8e:load*16+0x15baf]==relocated[0x15b8e:0x15baf]
for rname,start in [('DGROUP_after',0),('draw_DS64_after',0)]:
 captured=(work/(prefix+rname+'.bin')).read_bytes()
 # draw leaves DGROUP unchanged; fullDS64 additionally includes stack state at its return.
 assert seed[base:base+len(captured)]==captured
files={image.resolve(),relocs.resolve(),harness.resolve(),support.resolve(),Path(__file__).resolve(),Path(__file__).with_name('cache_reset_model.py').resolve()};files.update(Path(p).resolve() for p in s['capture_files']);files.update(p.resolve() for p in runtime.iterdir() if p.is_file() and p.name!='independent_verification.json')
proof=dict(verified=True,runtime_tests=0,data_only_native_capture=True,summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=sha(bytes(relocated)),RAM_bytes=len(seed),RAM_sha256=sha(seed),dump_parts=20,paused_address_reassembly_exact=True,source_files_unchanged=23,new_deep_verified_bytes=0,scope='Native conventionalRAM seed after same firstsprite prefix,not native cleanup/reset execution and not another accepted native scenario. Original cleanup code identity checked; source for controlled replay below.',files=[dict(path=str(p),sha256=sha(p.read_bytes())) for p in sorted(files)])
(runtime/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
registers={'CS':UC_X86_REG_CS,'IP':UC_X86_REG_IP,'DS':UC_X86_REG_DS,'ES':UC_X86_REG_ES,'SS':UC_X86_REG_SS,'SP':UC_X86_REG_SP,'AX':UC_X86_REG_AX,'BX':UC_X86_REG_BX,'CX':UC_X86_REG_CX,'DX':UC_X86_REG_DX,'SI':UC_X86_REG_SI,'DI':UC_X86_REG_DI,'BP':UC_X86_REG_BP}
mapping=root/'pass1_xms_move_request/noncode_intervals.csv';remaining=[(int(r['start']),int(r['end_exclusive'])) for r in csv.DictReader(mapping.open(encoding='utf-8')) if r['status'] in ('UNKNOWN','CLASSIFIED ONLY')]
cases=[];write_rows=[];mark_rows=[];owner_rows=[];delta_rows=[];read_rows=[]
for kind in ('cache_reset','level_cleanup'):
 ram=bytearray(seed);sp=d['post_registers']['SP'];lo,hi=base+sp-64,base+sp+8;frame=struct.pack('<3H',0x100,0x5000,2);ram[base+sp:base+sp+6]=frame;expected=CacheResetModel(ram,ds)
 if kind=='cache_reset':expected.reset()
 else:expected.cleanup()
 assert all(not (w['address']<hi and w['address']+w['size']>lo) for w in expected.writes)
 u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(0,bytes(ram));initial=dict(d['post_registers'],**d['post_extra']);initial.update(CS=load+(0x768 if kind=='cache_reset' else 0xd29),IP=0x24 if kind=='cache_reset' else 0x80e)
 for name,value in initial.items():u.reg_write(registers[name],value)
 u.reg_write(UC_X86_REG_EFLAGS,2);done=[];observed=[];trace=[]
 def code(emu,address,size,data):
  if address==0x50100:done.append(True);emu.emu_stop();return
  p=address-load*16;trace.append(p);assert 0x76a4<=p<0x7913 or 0xda9e<=p<0xdb39 or 0x15b8e<=p<0x15baf,hex(p)
 def write(emu,access,address,size,value,data):
  if lo<=address and address+size<=hi:return
  observed.append((address,size,value&((1<<(8*size))-1)))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(initial['CS']*16+initial['IP'],0xfffff,count=500000);assert done
 actual=bytes(u.mem_read(0,len(ram)));assert actual[:lo]==expected.ram[:lo] and actual[hi:]==expected.ram[hi:];assert observed==[(w['address'],w['size'],w['value']) for w in expected.writes]
 for name in ('DS','SS','BP','SI','DI'):assert u.reg_read(registers[name])==initial[name]
 assert u.reg_read(UC_X86_REG_SP)==sp+4 and bytes(u.mem_read(base+sp,6))==frame
 # Restricted read hooks avoid the known RETF-stack hook issue. Calibrate on the live vector.
 baseline_trace=list(trace);baseline_writes=list(observed);reads=[];done.clear();trace.clear();observed.clear()
 u2=Uc(UC_ARCH_X86,UC_MODE_16);u2.mem_map(0,0x100000);u2.mem_write(0,bytes(ram))
 for name,value in initial.items():u2.reg_write(registers[name],value)
 u2.reg_write(UC_X86_REG_EFLAGS,2)
 def read_event(emu,access,address,size,value,label):reads.append(dict(label=label,address=address,size=size,CS=emu.reg_read(UC_X86_REG_CS),IP=emu.reg_read(UC_X86_REG_IP)))
 u2.hook_add(UC_HOOK_CODE,code);u2.hook_add(UC_HOOK_MEM_WRITE,write)
 vector=(ds-0x2771+0x1be7)*16
 assert struct.unpack_from('<H',seed,base+0x2560)[0]*16==vector # Normal captured selector agrees with fixed reset binding.
 u2.hook_add(UC_HOOK_MEM_READ,read_event,user_data='vector',begin=vector,end=vector+511)
 for a,z in remaining:u2.hook_add(UC_HOOK_MEM_READ,read_event,user_data='remaining177',begin=load*16+a,end=load*16+z-1)
 u2.emu_start(initial['CS']*16+initial['IP'],0xfffff,count=500000)
 actual2=bytes(u2.mem_read(0,len(ram)));assert done and trace==baseline_trace and observed==baseline_writes and actual2[:lo]==actual[:lo] and actual2[hi:]==actual[hi:]
 for name in ('DS','SS','BP','SI','DI'):assert u2.reg_read(registers[name])==initial[name]
 assert u2.reg_read(UC_X86_REG_SP)==sp+4
 vector_union={p for e in reads if e['label']=='vector' for p in range(e['address'],e['address']+e['size'])};assert vector_union==set(range(vector,vector+62*4)) and not any(e['label']=='remaining177' for e in reads)
 read_rows.extend(dict(kind=kind,**e) for e in reads)
 count=struct.unpack_from('<H',seed,base+0x3504)[0];cursor=struct.unpack_from('<H',seed,base+0xc9c)[0];used=struct.unpack_from('<H',seed,base+0x350a)[0];assert count==62 and cursor==1 and used>0
 assert struct.unpack_from('<H',actual,base+0xc9c)[0]==cursor and struct.unpack_from('<H',actual,base+0x3504)[0]==count and struct.unpack_from('<H',actual,base+0x350a)[0]==0
 payloads=[]
 for n in range(10):payloads.append((expected.far(base+0x34cc+4*n)+6,8192))
 for n in range(4):payloads.append((expected.far(base+0x34f4+4*n)+6,8192))
 table=expected.word(base+0x2560)*16
 for n in range(count):payloads.append((expected.far(table+4*n)+2,3072))
 payload_positions=set()
 for a,n in payloads:
  assert actual[a:a+n]==seed[a:a+n];assert not payload_positions.intersection(range(a,a+n));payload_positions.update(range(a,a+n))
 changes=[i for i,(x,y) in enumerate(zip(ram,actual)) if x!=y and not lo<=i<hi];same_value=sum(bytes(ram[a:a+n])==value.to_bytes(n,'little') for a,n,value in observed)
 cases.append(dict(kind=kind,slot_count=count,cursor_before=cursor,cursor_after=cursor,XMS_used_before=used,XMS_used_after=0,whole_RAM_bytes_checked=len(seed)-(hi-lo),synthetic_stack_bytes_excluded=hi-lo,original_instruction_events=len(baseline_trace),unique_original_starts=len(set(baseline_trace)),nonstack_write_events=len(baseline_writes),initially_same_value_write_events=same_value,changed_byte_positions=len(changes),owner_refs_invalidated=len(expected.owners),mark_helper_calls=len(expected.marks),conventional_payload_bytes_unchanged=len(payload_positions),vector_read_byte_union=len(vector_union),remaining177_read_events=0,restricted_read_hooks_flow_equal=True,native_cleanup_executed=False,status='PASS'))
 write_rows.extend(dict(kind=kind,order=n,**w) for n,w in enumerate(expected.writes));mark_rows.extend(dict(kind=kind,order=n,**m) for n,m in enumerate(expected.marks));owner_rows.extend(dict(kind=kind,family=f,index=n,owner=owner) for f,n,owner in expected.owners);delta_rows.extend(dict(kind=kind,linear=i,before=ram[i],after=actual[i]) for i in changes)
for name,rows in [('cases',cases),('ordered_writes',write_rows),('mark_calls',mark_rows),('invalidated_owners',owner_rows),('byte_deltas',delta_rows),('restricted_reads',read_rows)]:
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary=dict(functions=[],cases=len(cases),failures=0,runtime_tests=0,new_deep_verified_bytes=0,results=cases,scope='Two controlled original-code replays seeded by paused native640KiB RAM. No stubs/OS. EntireRAM minus72B synthetic control stack and exact same-value/nonstack write order checked;305152B conventional cache payloads unchanged. Restricted read hooks reproduce exact baseline flow,read248B active vector and0remaining177events in these paths only. Not natural reset/cleanup execution,SAVELOAD/full lifecycle or global absence proof.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,relocs,mapping,seedpath,runtime/'independent_verification.json',Path(__file__).with_name('cache_reset_model.py'),Path(__file__))])
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
