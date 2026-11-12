"""python runtime_watch_worx_stack_window.py DOSBOX_EXE GAME_DIR IMAGE RELOCS OUT WORK
Memory-change-only watch of44 historical UNKNOWN bytes plus4B candidate hook.
"""
from pathlib import Path
support=Path(__file__).with_name('dosbox_watch_support_autotype_v1.py');support_bytes=support.read_bytes();exec(compile(support_bytes,str(support),'exec'),globals())
probe_started=time.monotonic()
extra=Path(sys.argv[8]).resolve();extra_raw=extra.read_bytes();assert sha(extra_raw)=='af574568089f1998ca50ceeba310ff068c728279ff470cd39f47a8919228b95a';extra_copy=drive/'DSTOPEN.IMG';extra_copy.write_bytes(extra_raw);inputs.append(dict(source=str(extra),copy=str(extra_copy),bytes=len(extra_raw),sha256=sha(extra_raw)))
with (out/'inputs.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(inputs[0]));w.writeheader();w.writerows(inputs)
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
 cache_initial=listed();assert cache_initial=={a:watch_initial[a] for a in watched_addresses};cached=dict(cache_initial);calibrated=set(watched_addresses);points={(load+0xd29,0x424):'wait_entry',(load+0x6b0,0):'irq_entry',(load+0x6b0,0x12):'irq_after_port_read',(load+0x6b0,0x133):'irq_before_iret',(load+0xd29,0x7c5):'after_wait',(load+0x83d,0x54):'font1_ready',(load+0x15bf,0x40fd):'worx_stack_window'};input_stops=[]
 for cs,ip in points:
  if points[(cs,ip)]!='worx_stack_window':request('EXEC BP %04X:%08X'%(cs,ip))
 request('EXEC RUN');deadline=time.monotonic()+40
 while time.monotonic()<deadline:
  reg=regs();values=listed();assert values==cache_initial,'UNKNOWN changed; retain as unverified investigation'
  stage=points.get((reg['CS'],reg['IP']))
  if stage:
   index=len(input_stops);prefix='stop_%02d_'%index
   for name,seg,off,length in [('game_key_flags',load+0x2771,0x3f50,2),('previous_scan',load+0x2771,0x34ba,1),('bios_queue',0x40,0x1a,36)]:
    dump(seg,off,length,prefix+name+'.bin');capture_files.append(work/(prefix+name+'.bin'))
   if stage=='wait_entry':request('EXEC BP %04X:000040FD'%(load+0x15bf))
   if stage=='worx_stack_window':
    dump(load+0x15bf,0x3edd,8,prefix+'worx_stack_control.bin');capture_files.append(work/(prefix+'worx_stack_control.bin'))
    dump(load+0x15bf,0x3ee5,512,prefix+'worx_private_stack.bin');capture_files.append(work/(prefix+'worx_private_stack.bin'))
    hold_start=time.monotonic()
    while time.monotonic()-probe_started<17:time.sleep(.05)
    breaks=request('EXEC BPLIST');window_line=next(line for line in breaks if 'BP ' in line and ('%04X:40FD'%(load+0x15bf)) in line.upper());window_index=re.search(r'^\s*([0-9A-Fa-f]+)\.',window_line).group(1);request('EXEC BPDEL '+window_index)
   if stage in ('irq_entry','irq_before_iret'):
    dump(reg['SS'],reg['SP'],6,prefix+'interrupt_frame.bin');capture_files.append(work/(prefix+'interrupt_frame.bin'))
   if stage=='irq_entry':
    dump(reg['SS'],reg['SP'],128,prefix+'interrupt_stack.bin');capture_files.append(work/(prefix+'interrupt_stack.bin'))
   stop=dict(stage=stage,registers=reg,prefix=prefix);input_stops.append(stop);snapshots.append(stop)
   if stage=='font1_ready':success=True;break
   assert len(input_stops)<20,'unexpected breakpoint repetition'
   request('EXEC RUN')
  else:time.sleep(.02)
 assert any(s['stage']=='irq_after_port_read' and s['registers']['AX']&255==0x39 for s in input_stops)
 (out/'input_stops.json').write_text(json.dumps(input_stops,indent=2)+'\n')
 assert success,'final code breakpoint not reached'
 watch_final=watched('final');assert {a:watch_final[a] for a in watched_addresses}==listed()
 sound_directory=dump(load+0x2771,0x3f64,474,'sound_directory_runtime.bin');capture_files.append(work/'sound_directory_runtime.bin');sound_source=(drive/'SND.DAT').read_bytes();assert sound_directory==sound_source[192:666]
 uif_source=(drive/'UIF.DAT').read_bytes();uif_directory=dump(load+0x1bdb,0,192,'uif_directory_runtime.bin');capture_files.append(work/'uif_directory_runtime.bin');assert uif_directory==uif_source[:192]
 font_block=dump(load+0x20b9,0x960,1200,'font2_block_runtime.bin');capture_files.append(work/'font2_block_runtime.bin')
 font_ptrs=dump(load+0x2771,0x3a90,512,'font2_pointers_runtime.bin');capture_files.append(work/'font2_pointers_runtime.bin')
 font_flags=dump(load+0x2771,0x1c6c,3,'font_flags_runtime.bin');capture_files.append(work/'font_flags_runtime.bin');assert font_flags[2]==1
 font_selected=dump(load+0x2771,0x368e,1,'font_selected_runtime.bin');capture_files.append(work/'font_selected_runtime.bin');assert font_selected==b'\1'
 font0_block=dump(load+0x20b9,0,1200,'font0_block_runtime.bin');capture_files.append(work/'font0_block_runtime.bin')
 font0_pointers=dump(load+0x2771,0x3690,512,'font0_pointers_runtime.bin');capture_files.append(work/'font0_pointers_runtime.bin')
 assert font_flags[0]==1
 font1_block=dump(load+0x20b9,0x4b0,1200,'font1_block_runtime.bin');capture_files.append(work/'font1_block_runtime.bin')
 font1_pointers=dump(load+0x2771,0x3890,512,'font1_pointers_runtime.bin');capture_files.append(work/'font1_pointers_runtime.bin');assert font_flags[1]==1
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
 result=dict(worx_stack_window_probe=True,interrupt_stack_probe=True,keyboard_font1_runtime=True,autotype_command="autotype -w 15 -p 1 space",drive_filenames=sorted(p.name for p in drive.iterdir()),success=success,error=error,load_segment=load if watch_initial else None,game_source_sha256=sha(packed),exe_sha256=sha(exe.read_bytes()),source_files_unchanged=unchanged,support_sha256=sha(support_bytes),harness_sha256=sha(Path(__file__).read_bytes()),runtime_image_sha256=sha(image_runtime) if watch_initial else None,regions=[dict(image_start=a,length=n,category='UNKNOWN_baseline' if a!=0x29a66 else 'open_FAR_candidate_slot_dump_only') for a,n in regions],watched_bytes=44 if cache_initial else 0,unknown_baseline_bytes=44,open_hook_bytes=4,watch_events=len(events),cache_initial=cache_initial,calibrated_addresses=sorted(calibrated),initial=watch_initial,final=watch_final,snapshots=snapshots,capture_files=[str(f) for f in capture_files],runtime_tests=1 if success else 0,new_deep_verified_bytes=0,scope='original packedDOS2 under DOSBox-X; BPLM BYTE value changes for44UNKNOWN between CRTentry and font1 init083D0054; hook4B dumps only; not read tracking, same-value-write tracking or full gameplay')
 (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('initial','final','capture_files','snapshots')},indent=2))




