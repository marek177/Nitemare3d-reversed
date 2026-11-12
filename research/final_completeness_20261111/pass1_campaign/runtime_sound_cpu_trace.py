"""python runtime_watch_unknown.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK
Memory-change-only watch of44 historical UNKNOWN bytes plus4B candidate hook.
"""
from pathlib import Path
support=Path(__file__).with_name('dosbox_watch_support_v1.py');support_bytes=support.read_bytes();exec(compile(support_bytes,str(support),'exec'),globals())
regions=[(0x1bda2,14),(0x1c070,16),(0x1d0ec,4),(0x20b88,8),(0x2770e,2),(0x29a66,4)];events=[];watch_initial={};watch_final={};error=None;success=False;capture_files=[];calibrated=set();cache_initial={}
def watched(name):
 result={}
 for a,n in regions:
  raw=dump(load+(a>>4),a&15,n,name+'_%05x.bin'%a);capture_files.append(work/(name+'_%05x.bin'%a))
  result.update({load*16+a+j:val for j,val in enumerate(raw)})
 return result
def listed():
 response=request('EXEC BPLIST');values={}
 for line in response:
  m=re.search(r'\bBPLM\s+([0-9A-Fa-f]+)\s+\(([0-9A-Fa-f]{2})\)',line)
  if m:values[int(m[1],16)]=int(m[2],16)
 assert len(values)==44,(len(values),response)
 return values
try:
 conn,address=server.accept();conn.settimeout(8);request('PING');time.sleep(1);initial=regs();load=initial['DS']+16
 assert initial['CS']==load+entry_cs and initial['IP']==entry_ip
 crt=load+0x11ee;request('EXEC BP %04X:00000018'%crt);request('EXEC RUN');entry=wait_for(crt,0x18);snapshots.append(dict(stage='crt_entry',registers=entry,load_segment=load))
 image_runtime=dump(load,0,len(canonical),'unpacked_runtime.bin');capture_files.append(work/'unpacked_runtime.bin');expected=bytearray(canonical)
 for row in csv.DictReader(relocations.open()):struct.pack_into('<H',expected,int(row['image_offset']),(int(row['original_word'])+load)&65535)
 assert image_runtime==expected
 watch_initial=watched('initial');assert len(watch_initial)==48
 request('EXEC BPDEL *')
 watched_addresses={a for a in watch_initial if a<load*16+0x29a66};assert len(watched_addresses)==44
 for address in sorted(watched_addresses):request('EXEC BPLM %08X'%address)
 cache_initial=listed();assert cache_initial=={a:watch_initial[a] for a in watched_addresses};cached=dict(cache_initial);calibrated=set(watched_addresses);goalcs=load+0x476;request('EXEC BP %04X:0000017C'%goalcs);request('EXEC RUN');deadline=time.monotonic()+20
 while time.monotonic()<deadline:
  reg=regs();values=listed();changes=[]
  for a in cached:
   if cached[a]==values[a]:continue
   role='value_change_after_baseline' if a in calibrated else 'cache_baseline_initialization' if values[a]==watch_initial[a] else 'unresolved_before_cache_baseline'
   changes.append(dict(linear=a,old=cached[a],new=values[a],role=role))
   if values[a]==watch_initial[a]:calibrated.add(a)
  if changes:
   events.append(dict(index=len(events),registers=reg,changes=changes,scope='cached breakpoint value transitions; stop CS:IP is not automatically writer CS:IP'));cached=values;watched('event_%03d'%len(events));request('EXEC RUN')
  elif reg['CS']==goalcs and reg['IP']==0x17c:
   snapshots.append(dict(stage='after_startup_initialization',registers=reg));success=True;break
  else:time.sleep(.05)
 assert success,'final code breakpoint not reached'
 trace_start=regs();assert (trace_start['CS'],trace_start['IP'])==(load+0x476,0x17c)
 snapshots[-1]['stage']='trace_start_after_palette'
 listing=request('EXEC BPLIST');assert any(line.startswith('00. BP %04X:017C'%(load+0x476)) for line in listing)
 request('EXEC BPDEL 0');request('EXEC BP %04X:00000190'%(load+0x476));request('EXEC LOGL 00010000')
 trace_end=wait_for(load+0x476,0x190,12);snapshots.append(dict(stage='trace_end_after_sound_directory',registers=trace_end))
 watch_final=watched('final');assert {a:watch_final[a] for a in watched_addresses}==listed()
 trace_path=work/'LOGCPU.TXT';assert trace_path.exists() and trace_path.stat().st_size>0
 (out/'trace_manifest.json').write_text(json.dumps(dict(path=str(trace_path),bytes=trace_path.stat().st_size,sha256=sha(trace_path.read_bytes()),start_cs=load+0x476,start_ip=0x17c,end_cs=load+0x476,end_ip=0x190,scope='LOGL pre-instruction records; final breakpoint record may not execute'),indent=2)+'\n')
 sound_directory=dump(load+0x2771,0x3f64,474,'sound_directory_runtime.bin');capture_files.append(work/'sound_directory_runtime.bin');sound_source=(drive/'SND.DAT').read_bytes();assert sound_directory==sound_source[192:666]
 request('EXEC BPDEL *')
except Exception as e:error=repr(e);success=False
finally:
 if conn:conn.close()
 server.close()
 if p.poll() is None:p.terminate()
 try:p.communicate(timeout=5)
 except subprocess.TimeoutExpired:p.kill();p.communicate()
 (out/'transcript.json').write_text(json.dumps(transcript,indent=2)+'\n');(out/'snapshots.json').write_text(json.dumps(snapshots,indent=2)+'\n');(out/'watch_events.json').write_text(json.dumps(events,indent=2)+'\n')
 unchanged=all(sha(Path(i['source']).read_bytes())==i['sha256'] for i in inputs);assert unchanged
 result=dict(success=success,error=error,load_segment=load if watch_initial else None,game_source_sha256=sha(packed),exe_sha256=sha(exe.read_bytes()),source_files_unchanged=unchanged,support_sha256=sha(support_bytes),harness_sha256=sha(Path(__file__).read_bytes()),runtime_image_sha256=sha(image_runtime) if watch_initial else None,regions=[dict(image_start=a,length=n,category='UNKNOWN_baseline' if a!=0x29a66 else 'open_FAR_candidate_slot_dump_only') for a,n in regions],watched_bytes=44 if cache_initial else 0,unknown_baseline_bytes=44,open_hook_bytes=4,watch_events=len(events),cache_initial=cache_initial,calibrated_addresses=sorted(calibrated),initial=watch_initial,final=watch_final,snapshots=snapshots,capture_files=[str(f) for f in capture_files],runtime_tests=1 if success else 0,new_deep_verified_bytes=0,scope='original packedDOS2 under DOSBox-X; BPLM BYTE value changes for44UNKNOWN between CRTentry and main0190; hook4B dumps only; not read tracking, same-value-write tracking or full gameplay')
 (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('initial','final','capture_files','snapshots')},indent=2))




