"""IMAGE RELOCS RUNTIME WORK: independently verify natural whole mode0 capture.
Byte model checks cache-owned final fields only, not unmodeled CRT/IRQ memory effects.
"""
import csv,hashlib,json,re,struct,sys
from pathlib import Path
from cache_init_model import InitModel
image,relocs,runtime,work=map(lambda p:Path(p).resolve(),sys.argv[1:]);root=runtime.parent;sha=lambda x:hashlib.sha256(x).hexdigest();summary=json.loads((runtime/'summary.json').read_text());assert summary['success'] and summary['runtime_tests']==1 and summary['source_files_unchanged'];load=summary['load_segment'];b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
trace=json.loads((runtime/'transcript.json').read_text());calls=json.loads((runtime/'calls.json').read_text());snap=json.loads((runtime/'snapshots.json').read_text());expected=bytearray(b)
for row in csv.DictReader(relocs.open()):struct.pack_into('<H',expected,int(row['image_offset']),(int(row['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==expected and sha(bytes(expected))==summary['runtime_image_sha256']
assert sha((root/'runtime_watch_cache_initialization.py').read_bytes())==summary['harness_sha256'];assert summary['exe_sha256']=='a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832';assert summary['support_sha256']=='64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89'
groups={};regpoints=[];lastbase=None
for i,t in enumerate(trace):
 cmd=t['command'];assert cmd in ('PING','EXEC EV CS EIP DS ES SS SP AX BX CX DX','EXEC EV SI DI BP') or re.fullmatch(r'EXEC (?:BP [0-9A-F]+:[0-9A-F]+|BPDEL \*|RUN|MEMDUMPBIN .+)',cmd),cmd
 if cmd.startswith('EXEC MEMDUMPBIN '):
  m=re.fullmatch(r'EXEC MEMDUMPBIN ([0-9A-F]+):([0-9A-F]+) ([0-9A-F]+) (.+)\.part(\d+)',cmd);assert m
  seg,off,n=(int(m.group(j),16) for j in (1,2,3));path=Path(m.group(4));offset=int(m.group(5));part=Path(str(path)+'.part'+str(offset));raw=part.read_bytes();assert len(raw)==n
  groups.setdefault(path,[]).append(dict(index=i,offset=offset,address=seg*16+off,length=n,path=part,raw=raw))
 if cmd=='EXEC EV CS EIP DS ES SS SP AX BX CX DX':
  vals=next(x.split() for x in t['response'] if re.fullmatch(r'[0-9A-Fa-f]+(?: [0-9A-Fa-f]+){9}',x));lastbase=(i,dict(zip(('CS','IP','DS','ES','SS','SP','AX','BX','CX','DX'),[int(x,16) for x in vals])))
 elif cmd=='EXEC EV SI DI BP':
  assert lastbase and lastbase[0]==i-1;vals=next(x.split() for x in t['response'] if re.fullmatch(r'[0-9A-Fa-f]+(?: [0-9A-Fa-f]+){2}',x));regpoints.append((i,{**lastbase[1],**dict(zip(('SI','DI','BP'),[int(x,16) for x in vals]))}))
origins={};parts=[]
for path,rows in groups.items():
 data=bytearray();first=rows[0]['address']
 for x in rows:
  assert x['offset']==len(data) and x['address']==first+len(data);data.extend(x['raw']);parts.append(x['path'])
 assert path.read_bytes()==data;origins[path.name]=dict(address=first,length=len(data),transcript_index=rows[0]['index'],parts=len(rows))
def dump(name,address,length):
 assert origins[name]['address']==address and origins[name]['length']==length;return (work/name).read_bytes()
def bound_regs(record,before_dump=None,after_index=-1):
 matches=[i for i,r in regpoints if r==record and i>after_index and (before_dump is None or i<before_dump)]
 assert matches,record
 return max(matches) if before_dump is not None else min(matches)
entry=snap['entry']['registers'];returned=snap['returned']['registers'];ds=load+0x2771;base=ds*16;assert entry['CS']==load+0x768 and entry['IP']==0x24 and entry['DS']==entry['SS']==ds
frame=dump('init_entry_frame.bin',entry['SS']*16+entry['SP'],6);assert frame.hex()==snap['entry']['frame_hex'] and struct.unpack_from('<H',frame,4)[0]==0
assert (returned['IP'],returned['CS'])==struct.unpack_from('<HH',frame);assert returned['SP']==entry['SP']+4
for key in ('BP','SI','DI','DS','SS'):assert returned[key]==entry[key]
before=dump('init_before_RAM.bin',0,0xa0000);after=dump('init_after_RAM.bin',0,0xa0000);assert bound_regs(entry,before_dump=origins['init_entry_frame.bin']['transcript_index'])<origins['init_before_RAM.bin']['transcript_index'];assert bound_regs(returned,before_dump=origins['init_after_RAM.bin']['transcript_index'])>origins['init_before_RAM.bin']['transcript_index']
assert before[entry['SS']*16+entry['SP']:entry['SS']*16+entry['SP']+6]==frame
assert after[entry['SS']*16+entry['SP']:entry['SS']*16+entry['SP']+6]==frame
cachecs=load+0x768;outercalls=[];manager=[];call_positions=[]
for index,c in enumerate(calls):
 assert c['index']==index;breg,areg=c['before'],c['after'];name='call_%03d_frame.bin'%index;f=dump(name,breg['SS']*16+breg['SP'],8);assert f.hex()==c['frame_hex'];rip,rcs=struct.unpack_from('<HH',f);assert (rip,rcs)==(c['return_ip'],c['return_cs']);assert (areg['CS'],areg['IP'],areg['SP'])==(rcs,rip,breg['SP']+4)
 pos=bound_regs(breg,before_dump=origins[name]['transcript_index']);apos=bound_regs(areg,after_index=origins[name]['transcript_index']);assert not any(t['command']=='EXEC RUN' for t in trace[pos+1:origins[name]['transcript_index']]);assert breg['DS']==areg['DS']==ds;call_positions.append((pos,apos))
 assert rcs==cachecs
 assert pos>max(x['index'] for x in groups[work/'init_before_RAM.bin']) and apos<origins['init_after_RAM.bin']['transcript_index']
 if c['name']=='manager':
  ptr=(work/'init_manager_pointer.bin').read_bytes();mo,ms=struct.unpack('<HH',ptr);assert (breg['CS'],breg['IP'])==(ms,mo);manager.append(c)
 else:
  target={'far_allocate':(0x11ee,0x2065),'probe_kib':(0xfba,0x58),'crt_probe':(0x11ee,0x2990),'detect':(0x768,0x784),'query':(0x768,0x7aa),'allocate_xms':(0x768,0x7c2),'lock_xms':(0x768,0x826),'release_xms':(0x768,0x7e4),'warning':(0x476,0x78)}[c['name']];assert (breg['CS'],breg['IP'])==(load+target[0],target[1]);outercalls.append(c)
 # Every retained return IP is the end of an original direct or indirect CALL.
 previous=[]
 for row in csv.DictReader((root/('xms_lifecycle_wrappers_replay' if c['name']=='manager' else 'cache_reset_replay')/('cache_lifecycle_dispatch_012.csv' if c['name']!='manager' else ({8:'xms_query_capacity',9:'xms_allocate_handle',12:'xms_lock_handle',10:'xms_release_handle'}[breg['AX']>>8])+'.csv')).open()):
  ip=int(row['ip']);raw=bytes.fromhex(row['bytes'])
  if ip+len(raw)==rip and row['instruction'].startswith('call '):previous.append(row)
 assert len(previous)==1,(c['name'],rip)
for i in range(1,len(calls)):assert call_positions[i][0]>call_positions[i-1][0]
byname={}
for c in outercalls:byname.setdefault(c['name'],[]).append(c)
assert len(byname['far_allocate'])==76 and len(manager)==3
for c in manager:
 enclosing=[p for p,x in enumerate(calls) if x['name'] in ('query','allocate_xms','lock_xms','release_xms') and call_positions[p][0]<call_positions[c['index']][0]<call_positions[c['index']][1]<call_positions[p][1]];assert len(enclosing)==1
get=lambda raw,off,n=2:int.from_bytes(raw[base+off:base+off+n],'little')
mgr_by_ah={c['before']['AX']>>8:c for c in manager};assert set(mgr_by_ah)=={8,9,12}
reply=lambda ah:[mgr_by_ah[ah]['after']['AX'],mgr_by_ah[ah]['after']['BX']&255,mgr_by_ah[ah]['after']['DX']]
pointer=(work/'init_manager_pointer.bin').read_bytes();assert pointer==after[base+0x350e:base+0x3512];off,seg=struct.unpack('<HH',pointer);dump('init_manager_pointer.bin',base+0x350e,4)
# AL of the native detection interrupt was not directly captured: only its bit7 outcome follows from original wrapper AX1.
assert byname['detect'][0]['after']['AX']==1
cfg=dict(probe=byname['probe_kib'][0]['after']['AX'],crt_probe=byname['crt_probe'][0]['after']['AX'],enabled=get(before,0x3cce,1),detect_AL=0x80,capacity=mgr_by_ah[8]['after']['AX'],query_error=mgr_by_ah[8]['after']['BX']&255,query_DX=mgr_by_ah[8]['after']['DX'],allocate_reply=reply(9),lock_reply=reply(12),release_reply=[1,0,0],fail_allocation=-1,selector_override=False,manager_offset=off,manager_segment=seg,allocation_fars=[[c['after']['AX'],c['after']['DX']] for c in byname['far_allocate']])
model=InitModel(before+b'\0'*(0x100000-len(before)),ds,cfg);model.run();assert not model.fatal
# Verify every abstract dependency argument/response, independently of the final field check.
abstract=[]
for c in calls:
 name=c['name'];a=c['after'];f=bytes.fromhex(c['frame_hex']);args=[struct.unpack_from('<H',f,4)[0]] if name=='far_allocate' else []
 if name in ('far_allocate','probe_kib','crt_probe'):abstract.append((name,args,a['AX'],a['DX']))
 elif name=='detect':abstract.extend([('detect_4300',[],0x4300,0),('detect_4310',[],0x4310,0)])
 elif name=='manager':
  ah=c['before']['AX']>>8;abstract.append(('manager_%02X'%ah,[] if ah==8 else [c['before']['DX']],a['AX'],a['DX']))
assert len(abstract)==len(model.calls)
for actual,want in zip(abstract,model.calls):
 assert actual[:2]==(want['name'],want['args'])
 if actual[0].startswith('manager') or actual[0]=='far_allocate':assert actual[2:]==(want['AX'],want['DX'])
 else:assert actual[2]==want['AX']
owned={};write_rows=[]
for j,w in enumerate(model.writes):
 assert 0<=w['address'] and w['address']+w['size']<=len(after)
 for k,x in enumerate(w['value'].to_bytes(w['size'],'little')):owned[w['address']+k]=x
 write_rows.append(dict(index=j,**w,native_evidence='final target bytes; native same-value store events not directly traced'))
assert all(after[p]==x for p,x in owned.items())
assert get(before,0xc9c)==get(after,0xc9c)==0
alloc_rows=[];union=set()
for x in model.allocations:
 a=x['address'];size=x['size'];assert a>0 and a+size<=len(after);positions=set(range(a,a+size));assert not(union&positions);union.update(positions);alloc_rows.append(dict(**x,offset=cfg['allocation_fars'][x['index']][0],segment=cfg['allocation_fars'][x['index']][1],native_after_sha256=sha(after[a:a+size])))
code_count=0
for folder,names in [('cache_reset_replay',['cache_lifecycle_dispatch_012']),('xms_lifecycle_wrappers_replay',['xms_detect_entry','xms_query_capacity','xms_allocate_handle','xms_release_handle','xms_lock_handle','xms_unlock_handle']),('cache_memory_probe_replay',['descending_memory_probe'])]:
 for name in names:
  for row in csv.DictReader((root/folder/(name+'.csv')).open()):
   p=int(row['image_offset']);n=len(bytes.fromhex(row['bytes']));a=load*16+p;assert before[a:a+n]==after[a:a+n]==expected[p:p+n];code_count+=n
# Retain all endpoint deltas; unmodeled effects are not silently accepted as cache stores.
deltas=[dict(address=p,before=before[p],after=after[p],category='cache-owned final target' if p in owned else 'outside modeled cache stores; CRT/stack/IRQ effects not assigned') for p in range(len(before)) if before[p]!=after[p]]
def save(name,rows):
 with (runtime/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save('allocation_records',alloc_rows);save('modeled_cache_writes',write_rows);save('RAM_endpoint_deltas',deltas)
(runtime/'model_inputs.json').write_text(json.dumps(cfg,indent=2)+'\n')
metrics=dict(native_callee_records=len(calls),native_far_allocations=len(alloc_rows),wall_buffers=10,sound_buffers=4,object_slots=get(after,0x3504),requested_allocation_union_bytes=len(union),cache_owned_final_bytes_checked=len(owned),modeled_cache_store_events=len(model.writes),native_observed_same_value_store_events=None,all_modeled_final_bytes_match=True,code_bytes_before_after_checked=code_count,probe_KiB=cfg['probe'],second_probe_word=cfg['crt_probe'],queried_XMS_KiB=cfg['capacity'],capped_XMS_KiB=get(after,0x3508),handle=get(after,0x3506),XMS_used=get(after,0x350a),enabled=get(after,0x3cce,1),saved_enabled=get(after,0x350c,1),manager_pointer_offset=off,manager_pointer_segment=seg,lock_manager_AX=mgr_by_ah[12]['after']['AX'],lock_physical_high=mgr_by_ah[12]['after']['DX'],lock_physical_low=mgr_by_ah[12]['after']['BX'],RAM_endpoint_changed_bytes=len(deltas),outside_modeled_target_changed_bytes=sum(x['address'] not in owned for x in deltas))
(runtime/'verification_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
files=[image,relocs,Path(__file__),root/'cache_init_model.py',root/'runtime_watch_cache_initialization.py',root/'dosbox_watch_support_newgame_v1.py']+[runtime/n for n in ('summary.json','calls.json','snapshots.json','transcript.json','inputs.csv','launch_arguments.json','runtime.conf','allocation_records.csv','modeled_cache_writes.csv','RAM_endpoint_deltas.csv','model_inputs.json','verification_metrics.json')]+list(groups)+parts
for x in csv.DictReader((runtime/'inputs.csv').open(encoding='utf-8')):
 for key in ('source','copy'):
  p=Path(x[key]);assert sha(p.read_bytes())==x['sha256'];files.append(p)
exe=Path(json.loads((runtime/'launch_arguments.json').read_text())[0]);assert sha(exe.read_bytes())==summary['exe_sha256'];files.append(exe)
for folder,names in [('cache_reset_replay',['cache_lifecycle_dispatch_012']),('xms_lifecycle_wrappers_replay',['xms_detect_entry','xms_query_capacity','xms_allocate_handle','xms_release_handle','xms_lock_handle','xms_unlock_handle']),('cache_memory_probe_replay',['descending_memory_probe'])]:files.extend(root/folder/(n+'.csv') for n in names)
proof=dict(verified=True,runtime_tests=1,new_deep_verified_bytes=0,summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=summary['runtime_image_sha256'],scope='Natural original wholemode0 with76actualfarallocations,3actualXMSmanagercalls,realprobe257KiB/count62/query14912/cap2048/handle1/lockphysical00170000; independent byte-model checks cache-owned final fields,notfullRAMorCRTcalleeclosure. DirectINT2FAL notcaptured,bit7outcome inferredfromoriginaldetectAX1. All640KiBRAMdumps reassembledfromactualcommands;allcalleeentry/returnregs/frames boundtodebuggerresponses. Native timingpaused;nofailure/Win16parity.',metrics=metrics,files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in dict.fromkeys(files)])
(runtime/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(metrics,indent=2))
