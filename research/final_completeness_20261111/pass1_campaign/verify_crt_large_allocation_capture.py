"""IMAGE RELOCS RUNTIME WORK EMULATOR: verify native large allocation/free and no-fixture original zero suffix.
Native whole-RAM parity is not claimed: IRQ/audio state outside the scoped DGROUP/buffer remains explicit.
"""
import csv,hashlib,json,re,struct,sys
from pathlib import Path
from crt_large_allocation_model import LargeAllocationModel
image,relocs,runtime,work,emulator=map(lambda p:Path(p).resolve(),sys.argv[1:]);sys.path.insert(0,str(emulator))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
r=runtime.parent;sha=lambda x:hashlib.sha256(x).hexdigest();summary=json.loads((runtime/'summary.json').read_text());assert summary['success'] and summary['source_files_unchanged'];load=summary['load_segment'];b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';expected=bytearray(b)
for row in csv.DictReader(relocs.open()):struct.pack_into('<H',expected,int(row['image_offset']),(int(row['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==expected and sha(bytes(expected))==summary['runtime_image_sha256'];assert sha((r/'runtime_watch_crt_large_allocation.py').read_bytes())==summary['harness_sha256'];assert summary['exe_sha256']=='a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832'
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
pe=s['probe_entry'];pf=dump('probe_entry_frame.bin',pe['SS']*16+pe['SP'],4,'probe_entry');assert (pe['CS'],pe['IP'])==(load+0xfba,0x58) and struct.unpack('<HH',pf)==(0xc3,load+0x768)
pr=s['probe_return'];assert (pr['CS'],pr['IP'],pr['SP'],pr['BP'])==(load+0xfba,0x9b,pe['SP']-10,pe['SP']-2)
for key in ('SI','DI','DS','SS'):assert pr[key]==pe[key]
a=s['large_allocation_accepted'];z=s['large_zero_complete'];crt=load+0x11ee;ds=load+0x2771;base=ds*16;assert (a['CS'],a['IP'],a['DS'],a['SS'],a['CF'])==(crt,0x2a87,ds,ds,0);assert (z['CS'],z['IP'])==(crt,0x2ae6)
frame=dump('large_allocation_frame.bin',a['SS']*16+a['BP'],12,'large_allocation_accepted');assert struct.unpack_from('<HH',frame,2)==(0x82,load+0xfba);count,size=struct.unpack_from('<IH',frame,6);layout=LargeAllocationModel.layout(count,size);assert layout;paragraphs,alignment,adjusted=layout;segment=a['AX'];assert (a['BX'],a['SI'])==(paragraphs,alignment);start=segment*16;end=start+paragraphs*16;assert end+16<=0xa0000
before=dump('large_before_zero_RAM.bin',0,0xa0000,'large_allocation_accepted');after=dump('large_after_zero_RAM.bin',0,0xa0000,'large_zero_complete');assert before[a['SS']*16+a['BP']:a['SS']*16+a['BP']+12]==frame
model=LargeAllocationModel(before+b'\0'*(0x200000-len(before)),ds,count,size,[],[]);model.zero(segment,paragraphs);wanted=iter(model.expected_writes());u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(model.ram));u.mem_write(0,before+b'\0'*(len(model.ram)-len(before)))
regs={'CS':UC_X86_REG_CS,'IP':UC_X86_REG_IP,'DS':UC_X86_REG_DS,'ES':UC_X86_REG_ES,'SS':UC_X86_REG_SS,'SP':UC_X86_REG_SP,'AX':UC_X86_REG_AX,'BX':UC_X86_REG_BX,'CX':UC_X86_REG_CX,'DX':UC_X86_REG_DX,'SI':UC_X86_REG_SI,'DI':UC_X86_REG_DI,'BP':UC_X86_REG_BP}
for name,key in regs.items():u.reg_write(key,a[name])
u.reg_write(UC_X86_REG_EFLAGS,2|a['CF']|(a['DF']<<10));executed=[];done=[];stores=[];allocator=list(csv.DictReader((r/'crt_large_allocation_replay/existing_crt_zeroed_far_allocate.csv').open()));allowed={int(x['image_offset']) for x in allocator}
def code(e,address,n,d):
 if address==crt*16+0x2ae6:done.append(True);e.emu_stop();return
 q=address-load*16;assert q in allowed;executed.append(q)
def intr(e,n,d):raise AssertionError('no interrupt fixture allowed in post-DOS suffix')
def write(e,access,address,n,value,d):
 want=next(wanted,None);assert (address,n,value&((1<<(8*n))-1))==want;stores.append(1)
u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(crt*16+0x2a87,0x1fffff,count=300000);assert done and next(wanted,None) is None;replay=bytes(u.mem_read(0,len(model.ram)));assert replay==model.ram
for name,key in regs.items():assert u.reg_read(key)==z[name],(name,u.reg_read(key),z[name])
flags=u.reg_read(UC_X86_REG_EFLAGS);assert (flags&1,bool(flags&0x400))==(z['CF'],bool(z['DF']))
# Only known clockDWORD081E is excluded from this native DGROUP comparison.
clock=set(range(base+0x81e,base+0x822));assert all(after[q]==model.ram[q] for q in range(base,base+0xe030) if q not in clock)
assert after[start:end]==bytes(end-start);assert before[start-16:start]==after[start-16:start] and before[end:end+16]==after[end:end+16]
ret=s['large_allocator_return'];assert (ret['CS'],ret['IP'],ret['AX'],ret['DX'],ret['SP'])==(load+0xfba,0x82,alignment,segment,a['BP']+6)
free=s['large_free_entry'];free_frame=dump('large_free_frame.bin',free['SS']*16+free['SP'],8,'large_free_entry');assert struct.unpack_from('<HH',free_frame)==(0x95,load+0xfba) and struct.unpack_from('<HH',free_frame,4)==(alignment,segment)
f0=s['large_free_before_DOS'];f1=s['large_free_after_DOS'];assert (f0['CS'],f0['IP'],f0['ES'],f0['AX']>>8)==(crt,0x2a12,segment,0x49);assert (f1['CS'],f1['IP'],f1['CF'],f1['SP'],f1['BP'])==(crt,0x2a14,0,f0['SP'],f0['BP'])
g0=dump('large_before_free_with_guards.bin',start-16,end-start+32,'large_free_entry');g1=dump('large_after_free_with_guards.bin',start-16,end-start+32,'large_free_after_DOS');assert g0[16:-16]==g1[16:-16]==bytes(end-start)
assert s['probe_return']['AX']==count*size//1024
code_bytes=0
for folder,name in [('cache_memory_probe_replay','descending_memory_probe'),('crt_large_allocation_replay','existing_crt_zeroed_far_allocate'),('crt_large_allocation_replay','crt_DOS_free_far')]:
 for row in csv.DictReader((r/folder/(name+'.csv')).open()):
  q=int(row['image_offset']);n=len(bytes.fromhex(row['bytes']));address=load*16+q;assert before[address:address+n]==after[address:address+n]==expected[q:q+n];code_bytes+=n
residuals=[dict(address=q,before=before[q],native_after=after[q],replay_after=model.ram[q],category='captured clockDWORD endpoint delta; native writerPC not traced' if q in clock else 'outside scoped cacheDGROUP/allocation; IRQ/audio/stack source not closed') for q in range(len(before)) if after[q]!=model.ram[q]]
assert all(q['address'] not in range(start,end) for q in residuals)
with (runtime/'RAM_replay_residuals.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(residuals[0]));w.writeheader();w.writerows(residuals)
metrics=dict(count_DWORD=count,element_size_WORD=size,paragraphs=paragraphs,returned_segment=segment,returned_offset=alignment,physical_start=start,physical_end_exclusive=end,zero_range_bytes_checked=end-start,native_buffer_changed_positions=sum(x!=y for x,y in zip(before[start:end],after[start:end])),native_buffer_initially_zero=not any(before[start:end]),native_store_events_directly_counted=False,replay_original_instruction_events=len(executed),replay_unique_starts=len(set(executed)),replay_ordered_nonstack_stores=len(stores),replay_full_RAM_bytes_checked=len(model.ram),native_DGROUP_bytes_checked=0xe030-4,native_guard_bytes_checked=32,native_replay_residual_positions=len(residuals),native_DOS_free_CF=f1['CF'],before_free_leading_guard=g0[:16].hex(),after_free_leading_guard=g1[:16].hex(),before_free_trailing_guard=g0[-16:].hex(),after_free_trailing_guard=g1[-16:].hex(),code_bytes_before_after_checked=code_bytes,probe_return_AX=s['probe_return']['AX'])
(runtime/'verification_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
files=[image,relocs,Path(__file__),r/'crt_large_allocation_model.py',r/'runtime_watch_crt_large_allocation.py',r/'dosbox_watch_support_newgame_v1.py']+[runtime/n for n in ('summary.json','transcript.json','snapshots.json','inputs.csv','launch_arguments.json','runtime.conf','verification_metrics.json','RAM_replay_residuals.csv')]+list(groups)+parts
for x in csv.DictReader((runtime/'inputs.csv').open(encoding='utf-8')):
 for key in ('source','copy'):
  q=Path(x[key]);assert sha(q.read_bytes())==x['sha256'];files.append(q)
exe=Path(json.loads((runtime/'launch_arguments.json').read_text())[0]);assert sha(exe.read_bytes())==summary['exe_sha256'];files.append(exe)
for folder,name in [('cache_memory_probe_replay','descending_memory_probe'),('crt_large_allocation_replay','existing_crt_zeroed_far_allocate'),('crt_large_allocation_replay','crt_DOS_free_far')]:files.append(r/folder/(name+'.csv'))
files.extend(emulator.rglob('*.dll'));files.extend(emulator.rglob('*.pyd'))
proof=dict(verified=True,runtime_tests=1,new_deep_verified_bytes=0,summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=summary['runtime_image_sha256'],scope='Natural original257KiB probe allocation: actual DOS48 acceptedsegment5F98/BX4040 and DOS49freeCF0. Nativebuffer alreadyzero beforeloop,zero endpointnotwritecount. Original postDOS suffix nofixtures matches captured all16bitregs/CF/DF,full2MiB replaymodel/orderedstores; native263168bufferB+32guards+57388DGROUPBmatch exceptcapturedclock4B. ResidualIRQ/audio/stackpositions retained,notfullnativeRAMclosure. Failedpredecessorallocations not individually trapped; noWin16parity.',metrics=metrics,files=[dict(path=str(q.resolve()),sha256=sha(q.read_bytes())) for q in dict.fromkeys(files)])
(runtime/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(metrics,indent=2))
