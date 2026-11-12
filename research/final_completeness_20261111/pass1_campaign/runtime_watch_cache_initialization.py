"""DOSBOX GAME IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG: natural first cache init.
Read-only debugger captures; no CPU/RAM injection or modified game assets.
"""
from pathlib import Path
support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');support_bytes=support.read_bytes();exec(compile(support_bytes,str(support),'exec'),globals())
extra=Path(sys.argv[8]).resolve();extra_raw=extra.read_bytes();assert sha(extra_raw)=='af574568089f1998ca50ceeba310ff068c728279ff470cd39f47a8919228b95a';extra_copy=drive/'DSTOPEN.IMG';extra_copy.write_bytes(extra_raw);inputs.append(dict(source=str(extra),copy=str(extra_copy),bytes=len(extra_raw),sha256=sha(extra_raw)))
with (out/'inputs.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(inputs[0]));w.writeheader();w.writerows(inputs)
calls=[];pending={};active=set();capture_files=[];entry_record=None;return_record=None;load=None;image_runtime=b''
def fullregs():
 r=regs();response=request('EXEC EV SI DI BP');v=next(x.split() for x in response if re.fullmatch(r'[0-9A-Fa-f]+(?: [0-9A-Fa-f]+){2}',x));r.update(dict(zip(('SI','DI','BP'),[int(x,16) for x in v])));return r
def grab(seg,off,n,name):raw=dump(seg,off,n,name);capture_files.append(work/name);return raw
def bp(cs,ip):
 if (cs,ip) not in active:request('EXEC BP %04X:%08X'%(cs,ip));active.add((cs,ip))
try:
 conn,address=server.accept();conn.settimeout(8);request('PING');time.sleep(1);initial=regs();load=initial['DS']+16;assert initial['CS']==load+entry_cs and initial['IP']==entry_ip
 bp(load+0x11ee,0x18);request('EXEC RUN');wait_for(load+0x11ee,0x18)
 image_runtime=grab(load,0,len(canonical),'unpacked_runtime.bin');expected=bytearray(canonical)
 for row in csv.DictReader(relocations.open()):struct.pack_into('<H',expected,int(row['image_offset']),(int(row['original_word'])+load)&65535)
 assert image_runtime==expected;request('EXEC BPDEL *');active.clear();cachecs=load+0x768;bp(cachecs,0x24);request('EXEC RUN');wait_for(cachecs,0x24,15)
 reg=fullregs();frame=grab(reg['SS'],reg['SP'],6,'init_entry_frame.bin');assert struct.unpack('<H',frame[4:])[0]==0;assert reg['DS']==reg['SS']==load+0x2771
 entry_record=dict(registers=reg,frame_hex=frame.hex());retip,retcs=struct.unpack('<HH',frame[:4]);bp(retcs,retip);grab(0,0,0xa0000,'init_before_RAM.bin')
 targets={(load+0x11ee,0x2065):'far_allocate',(load+0xfba,0x58):'probe_kib',(load+0x11ee,0x2990):'crt_probe',(cachecs,0x784):'detect',(cachecs,0x7aa):'query',(cachecs,0x7c2):'allocate_xms',(cachecs,0x826):'lock_xms',(cachecs,0x7e4):'release_xms',(load+0x476,0x78):'warning',(load+0xfba,0xc):'fatal'}
 for cs,ip in targets:bp(cs,ip)
 request('EXEC RUN');deadline=time.monotonic()+100
 while time.monotonic()<deadline:
  reg=fullregs();key=(reg['CS'],reg['IP'])
  if key==(retcs,retip):
   assert not pending;return_record=dict(registers=reg);grab(0,0,0xa0000,'init_after_RAM.bin');success=True;break
  if key in pending:
   index=pending.pop(key);record=calls[index];record['after']=reg
   if record['name']=='detect' and reg['AX']:
    pointer=grab(reg['DS'],0x350e,4,'init_manager_pointer.bin');off,seg=struct.unpack('<HH',pointer);targets[(seg,off)]='manager';bp(seg,off)
   request('EXEC RUN');continue
  if key in targets:
   name=targets[key]
   if name=='fatal':raise RuntimeError('native fatal init diagnostic')
   frame=grab(reg['SS'],reg['SP'],8,'call_%03d_frame.bin'%len(calls));rip,rcs=struct.unpack('<HH',frame[:4])
   if name!='manager' and rcs!=cachecs:request('EXEC RUN');continue
   assert (rcs,rip) not in pending;record=dict(index=len(calls),name=name,before=reg,frame_hex=frame.hex(),return_cs=rcs,return_ip=rip);calls.append(record);pending[(rcs,rip)]=record['index'];bp(rcs,rip);request('EXEC RUN');continue
  time.sleep(.02)
 assert success,'natural cache init return not reached'
 assert return_record['registers']['SP']==entry_record['registers']['SP']+4
except Exception as e:error=repr(e);success=False
finally:
 if conn:conn.close()
 server.close()
 if p.poll() is None:p.terminate()
 try:p.communicate(timeout=5)
 except subprocess.TimeoutExpired:p.kill();p.communicate()
 unchanged=all(sha(Path(i['source']).read_bytes())==i['sha256'] for i in inputs)
 (out/'calls.json').write_text(json.dumps(calls,indent=2)+'\n');(out/'transcript.json').write_text(json.dumps(transcript,indent=2)+'\n');(out/'snapshots.json').write_text(json.dumps(dict(entry=entry_record,returned=return_record),indent=2)+'\n')
 result=dict(success=success,error=error,load_segment=load,runtime_tests=1 if success else 0,new_deep_verified_bytes=0,source_files_unchanged=unchanged,game_source_sha256=sha(packed),exe_sha256=sha(exe.read_bytes()),support_sha256=sha(support_bytes),harness_sha256=sha(Path(__file__).read_bytes()),runtime_image_sha256=sha(image_runtime),calls=len(calls),capture_files=[str(f) for f in capture_files],scope='Natural original packedDOS2 first wholecachemode0; noCPU/RAMinjection; before/after640KiBRAM,calleeentry/returnregisters/frames. Debuggerpause timing,notuninterrupted execution; independentverificationrequired.')
 (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='capture_files'},indent=2))
