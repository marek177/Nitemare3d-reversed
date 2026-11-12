"""IMAGE RELOCS RUNTIME WORK DECODER EMULATOR MAP OUT: whole native CRT clock replay."""
import csv,datetime,hashlib,json,struct,sys
from pathlib import Path
image,relocs,runtime,work,decoder,emulator,mapping,out=map(Path,sys.argv[1:]);sys.path[:0]=[str(decoder.resolve()),str(emulator.resolve())]
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
sha=lambda x:hashlib.sha256(x).hexdigest();s=json.loads((runtime/'summary.json').read_text());assert s['success'] and s['source_files_unchanged'];out.mkdir(exist_ok=True);root=runtime.parent
harness=root/'runtime_watch_ftime_v2.py';support=root/'dosbox_watch_support_newgame_v1.py'
assert sha(harness.read_bytes())==s['harness_sha256']=='d901b5cb19d1bc1497ef83b351ef7ebffc8a2036a9097afb95402cb196ed434e'
assert sha(support.read_bytes())==s['support_sha256']=='64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89'
inputs=list(csv.DictReader((runtime/'inputs.csv').open(encoding='utf-8')));assert len(inputs)==23
for r in inputs:
 for k in ('source','copy'):
  raw=Path(r[k]).read_bytes();assert sha(raw)==r['sha256'] and len(raw)==int(r['bytes'])
b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';load=s['load_segment'];relocated=bytearray(b)
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',relocated,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==relocated
calls=json.loads((runtime/'ftime_calls.json').read_text());calls=[c for c in calls if c['stage']=='clock_sample_entry'];assert len(calls)==1;c=calls[0];prefix=c['prefix'];pre=c['pre_registers'];post=c['post_registers'];ds=load+0x2771
def read(name):return (work/(prefix+name+'.bin')).read_bytes()
before=read('DS64_before');mid=read('DS64_ftime_return');after=read('DS64_after');assert len(before)==len(mid)==len(after)==65536
assert (pre['CS'],pre['IP'],pre['DS'],pre['SS'])==(load+0xbde,0x18,ds,ds);assert before[0x3cc7]!=0 or before[0x3ccf]==0
frame=read('frame_before');assert read('frame_after')==frame;retip,retcs=struct.unpack('<HH',frame);ftframe=read('ftime_frame');ftretip,ftretcs,ptr=struct.unpack('<3H',ftframe);assert ptr==c['timeb_offset'] and (ftretcs,ftretip)==(load+0xbde,0x75)
tb=read('timeb_after');assert mid[ptr:ptr+14]==tb and len(tb)==14 and tb[10:]==read('timeb_before')[10:]
seconds,milliseconds,minuteszone,daylight=struct.unpack('<IHhH',tb[:10]);date=c['date_return_registers'];time=c['time_return_registers'];year=date['CX'];month=date['DX']>>8;day=date['DX']&255;hour=time['CX']>>8;minute=time['CX']&255;second=time['DX']>>8;hundredths=time['DX']&255
assert hour!=0 or minute!=0;zone,enabled=struct.unpack_from('<iH',before,0x24a6);assert month==11 and year==2026 and zone==28800 and enabled==1 and daylight==0
epoch=int((datetime.datetime(year,month,day,hour,minute,second)-datetime.datetime(1970,1,1)).total_seconds())+zone
assert seconds==epoch&0xffffffff and milliseconds==10*hundredths and minuteszone==zone//60
clock=(seconds*1000+milliseconds)&0xffffffff;assert post['AX']|(post['DX']<<16)==clock
expected=bytearray(before[:0xe030]);assert struct.unpack_from('<H',expected,0x3ca8)[0]==0;struct.pack_into('<H',expected,0x3ca8,1);assert mid[:0xe030]==after[:0xe030]==expected
assert c['pre_extra']==c['post_extra'] and (post['CS'],post['IP'],post['DS'],post['SS'],post['SP'])==(retcs,retip,ds,ds,pre['SP']+4)
u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,0x100000);u.mem_write(load*16,bytes(relocated));u.mem_write(ds*16,before)
registers={'CS':UC_X86_REG_CS,'IP':UC_X86_REG_IP,'DS':UC_X86_REG_DS,'ES':UC_X86_REG_ES,'SS':UC_X86_REG_SS,'SP':UC_X86_REG_SP,'AX':UC_X86_REG_AX,'BX':UC_X86_REG_BX,'CX':UC_X86_REG_CX,'DX':UC_X86_REG_DX,'SI':UC_X86_REG_SI,'DI':UC_X86_REG_DI,'BP':UC_X86_REG_BP}
for name,value in dict(pre,**c['pre_extra']).items():u.reg_write(registers[name],value)
u.reg_write(UC_X86_REG_EFLAGS,2);done=[];executed=[];interrupts=[];ftime_checked=[];remaining=[(int(r['start']),int(r['end_exclusive'])) for r in csv.DictReader(mapping.open(encoding='utf-8')) if r['status'] in ('UNKNOWN','CLASSIFIED ONLY')];touches=[];getenv_returns=[];getenv_stop=[]
def code(emu,address,size,data):
 if address==retcs*16+retip:done.append(True);emu.emu_stop();return
 p=address-load*16
 assert 0<=p<len(b) and emu.reg_read(UC_X86_REG_CS) in (load+0xbde,load+0x11ee), (hex(p),hex(emu.reg_read(UC_X86_REG_CS)),hex(emu.reg_read(UC_X86_REG_IP)),[hex(q) for q in executed[-20:]]); executed.append(p)
 if address==ftretcs*16+ftretip:
  ftime_checked.append(True);assert bytes(emu.mem_read(ds*16+ptr,14))==tb
  for name,value in c['ftime_return_registers'].items():assert emu.reg_read(registers[name])==value,('ftime',name,emu.reg_read(registers[name]),value)
 if p==0x11ee0+0x248a:
  sp=emu.reg_read(UC_X86_REG_SP);ip,cs=struct.unpack('<HH',bytes(emu.mem_read(ds*16+sp,4)));getenv_stop.append(cs*16+ip)
 if getenv_stop and address==getenv_stop[-1]:getenv_returns.append(emu.reg_read(UC_X86_REG_AX));getenv_stop.pop()
def interrupt(emu,number,data):
 assert number==0x21;ah=emu.reg_read(UC_X86_REG_AH);native=date if ah==0x2a else time if ah==0x2c else None;assert native is not None;interrupts.append(ah)
 for name in ('AX','CX','DX'):emu.reg_write(registers[name],native[name])
u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,interrupt);u.emu_start(pre['CS']*16+pre['IP'],0xfffff,count=20000)
assert done and len(ftime_checked)==1 and interrupts==[0x2a,0x2c] and getenv_returns==[0]
assert bytes(u.mem_read(ds*16,0xe030))==after[:0xe030] and bytes(u.mem_read(ds*16+ptr,14))==tb and bytes(u.mem_read(ds*16+pre['SP'],4))==frame
for name,value in dict(post,**c['post_extra']).items():assert u.reg_read(registers[name])==value,(name,u.reg_read(registers[name]),value)
baseline_instructions=list(executed);baseline_unique=len(set(executed))
# Read callbacks on a RETF stack frame perturb this Unicorn build (separate probe).
# Restrict callbacks to the actual data regions, and require exact baseline control-flow parity.
u2=Uc(UC_ARCH_X86,UC_MODE_16);u2.mem_map(0,0x100000);u2.mem_write(load*16,bytes(relocated));u2.mem_write(ds*16,before)
for name,value in dict(pre,**c['pre_extra']).items():u2.reg_write(registers[name],value)
u2.reg_write(UC_X86_REG_EFLAGS,2);done.clear();executed.clear();interrupts.clear();ftime_checked.clear();getenv_returns.clear();getenv_stop.clear();trace=[]
def restricted_memory(emu,access,address,size,value,label):
 trace.append(dict(label=label,access=access,linear=address,size=size,CS=emu.reg_read(UC_X86_REG_CS),IP=emu.reg_read(UC_X86_REG_IP)))
u2.hook_add(UC_HOOK_CODE,code);u2.hook_add(UC_HOOK_INTR,interrupt)
for lo,hi in remaining:u2.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,restricted_memory,user_data='remaining177',begin=load*16+lo,end=load*16+hi-1)
u2.hook_add(UC_HOOK_MEM_READ,restricted_memory,user_data='positive_TZ_read',begin=ds*16+0x24a2,end=ds*16+0x24a4)
u2.hook_add(UC_HOOK_MEM_WRITE,restricted_memory,user_data='positive_timeb_write',begin=ds*16+ptr,end=ds*16+ptr+13)
u2.emu_start(pre['CS']*16+pre['IP'],0xfffff,count=20000);assert done and executed==baseline_instructions and interrupts==[0x2a,0x2c] and getenv_returns==[0]
for name,value in dict(post,**c['post_extra']).items():assert u2.reg_read(registers[name])==value
assert bytes(u2.mem_read(ds*16,0xe030))==after[:0xe030] and bytes(u2.mem_read(ds*16+ptr,14))==tb and bytes(u2.mem_read(ds*16+pre['SP'],4))==frame
reads=[e for e in trace if e['label']=='positive_TZ_read'];writes=[e for e in trace if e['label']=='positive_timeb_write'];remaining_events=[e for e in trace if e['label']=='remaining177']
assert len(reads)==3 and {e['linear'] for e in reads}==set(range(ds*16+0x24a2,ds*16+0x24a5))
written={a for e in writes for a in range(e['linear'],e['linear']+e['size'])};assert written==set(range(ds*16+ptr,ds*16+ptr+10)) and not remaining_events
calibration=dict(baseline_instruction_sequence_matches=True,positive_TZ_read_events=reads,positive_timeb_write_events=writes,remaining177_events=remaining_events,scope='Restricted data-range hooks only; no read callbacks on RETF stack. Exact643-instruction sequence and native outputs/registers/DGROUP match baseline. Replay evidence,not direct native read tracing.')
(out/'memory_trace_calibration.json').write_text(json.dumps(calibration,indent=2)+'\n',encoding='utf-8')
files={image.resolve(),relocs.resolve(),mapping.resolve(),harness.resolve(),support.resolve(),Path(__file__).resolve()};files.update(Path(p).resolve() for p in s['capture_files']);files.update(p.resolve() for p in runtime.iterdir() if p.is_file() and p.name!='independent_verification.json')
proof=dict(verified=True,runtime_tests=1,status='PARTIAL',summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=sha(bytes(relocated)),date=[year,month,day],time=[hour,minute,second,hundredths],timezone_seconds=zone,timezone_minutes=minuteszone,DST_flag=daylight,epoch_hex='%08X'%seconds,milliseconds=milliseconds,clock_hex='%08X'%clock,timeb10_hex=tb[:10].hex(),untouched_tail4_hex=tb[10:].hex(),timezone_cache_before=0,timezone_cache_after=1,whole_DGROUP_bytes_compared=0xe030,DGROUP_changed_bytes=1,original_replay_instructions=len(baseline_instructions),unique_original_starts=baseline_unique,CRT_stubs=0,OS_interrupt_fixtures=interrupts,original_getenv_return_AX=getenv_returns,remaining_177_restricted_replay_memory_events=len(remaining_events),positive_read_calibration_events=len(reads),positive_write_calibration_byte_union=len(written),restricted_memory_hook_control_flow_matches_baseline=True,new_deep_verified_bytes=0,scope='Original whole gameclock sample->ftime->cold timezone/getenv->DOS date/time wrappers->calendar/DST. Native DOS responses retained; only those2INT21 responses supplied to original-instruction replay.10B output+4unchanged tail,all captured final andftime-return registers,frame/full57392B DGROUP match; only cache3CA8 BYTE0to1 changes. FullDS64 used for environment/scratch input,not claimed entirely matching after DOS kernel scratch. Restricted data-range hooks calibrated3TZreads/10outputwriteB,exact baseline flow,zero remaining177 events in this replay path only. Broad read hooks perturb RETF (separate probe),not used for nonuse claims.',files=[dict(path=str(p),sha256=sha(p.read_bytes())) for p in sorted(files)],asset_sources=[dict(path=r['source'],sha256=r['sha256']) for r in inputs])
(out/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in proof.items() if k not in ('files','asset_sources')},indent=2))
