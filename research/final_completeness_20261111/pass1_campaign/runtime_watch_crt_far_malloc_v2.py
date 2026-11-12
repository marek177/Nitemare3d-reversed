"""DOSBOX GAME IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG: whole natural first cache far-malloc.
Read-only capture of original2065 entry/return and possible DOS48/4A checkpoints.
"""
from pathlib import Path
support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');support_bytes=support.read_bytes();exec(compile(support_bytes,str(support),'exec'),globals())
extra=Path(sys.argv[8]).resolve();eraw=extra.read_bytes();assert sha(eraw)=='af574568089f1998ca50ceeba310ff068c728279ff470cd39f47a8919228b95a';target=drive/'DSTOPEN.IMG';target.write_bytes(eraw);inputs.append(dict(source=str(extra),copy=str(target),bytes=len(eraw),sha256=sha(eraw)))
with (out/'inputs.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(inputs[0]));w.writeheader();w.writerows(inputs)
stages=[];capture_files=[];load=None;image_runtime=b'';dos_events=[]
def fullregs():
 r=regs()
 for cmd,keys in [('EXEC EV SI DI BP',('SI','DI','BP')),('EXEC EV CF DF',('CF','DF'))]:
  response=request(cmd);v=next(x.split() for x in response if re.fullmatch(r'[0-9A-Fa-f]+(?: [0-9A-Fa-f]+){%d}'%(len(keys)-1),x));r.update(dict(zip(keys,[int(x,16) for x in v])))
 return r
def grab(seg,off,n,name):raw=dump(seg,off,n,name);capture_files.append(work/name);return raw
def stage(name,cs,ip):
 request('EXEC BP %04X:%08X'%(cs,ip));request('EXEC RUN');wait_for(cs,ip,20);reg=fullregs();stages.append(dict(stage=name,registers=reg));return reg
try:
 conn,address=server.accept();conn.settimeout(8);request('PING');time.sleep(1);initial=regs();load=initial['DS']+16;assert initial['CS']==load+entry_cs and initial['IP']==entry_ip;crt=load+0x11ee
 reg=stage('crt_entry',crt,0x18);image_runtime=grab(load,0,len(canonical),'unpacked_runtime.bin');expected=bytearray(canonical)
 for row in csv.DictReader(relocations.open()):struct.pack_into('<H',expected,int(row['image_offset']),(int(row['original_word'])+load)&65535)
 assert image_runtime==expected;request('EXEC BPDEL *');stage('cache_init_entry',load+0x768,0x24);request('EXEC BPDEL *');reg=stage('malloc_entry',crt,0x2065);assert reg['DS']==reg['SS']==load+0x2771
 frame=grab(reg['SS'],reg['SP'],6,'malloc_entry_frame.bin');rip,rcs,size=struct.unpack('<3H',frame);assert (rip,rcs,size)==(0x4b,load+0x768,8198);grab(0,0,0xa0000,'malloc_before_RAM.bin');request('EXEC BPDEL *');request('EXEC BP %04X:%08X'%(rcs,rip))
 # Capture DOS allocation and resize requests/responses; no response is inferred from final heap state.
 for ip in (0x22fb,0x22fd,0x22aa,0x22ac):request('EXEC BP %04X:%08X'%(crt,ip))
 request('EXEC RUN');deadline=time.monotonic()+30
 while time.monotonic()<deadline:
  reg=fullregs()
  if (reg['CS'],reg['IP'])==(rcs,rip):stages.append(dict(stage='malloc_return',registers=reg));grab(0,0,0xa0000,'malloc_after_RAM.bin');success=True;break
  if reg['CS']==crt and reg['IP'] in (0x22fb,0x22fd,0x22aa,0x22ac):dos_events.append(reg);request('EXEC RUN');continue
  time.sleep(.02)
 assert success,'malloc return not reached'
except Exception as e:error=repr(e);success=False
finally:
 if conn:conn.close()
 server.close()
 if p.poll() is None:p.terminate()
 try:p.communicate(timeout=5)
 except subprocess.TimeoutExpired:p.kill();p.communicate()
 unchanged=all(sha(Path(x['source']).read_bytes())==x['sha256'] for x in inputs)
 (out/'snapshots.json').write_text(json.dumps(stages,indent=2)+'\n');(out/'transcript.json').write_text(json.dumps(transcript,indent=2)+'\n');(out/'DOS_events.json').write_text(json.dumps(dos_events,indent=2)+'\n')
 result=dict(success=success,error=error,load_segment=load,runtime_tests=1 if success else 0,new_deep_verified_bytes=0,source_files_unchanged=unchanged,game_source_sha256=sha(packed),exe_sha256=sha(exe.read_bytes()),support_sha256=sha(support_bytes),harness_sha256=sha(Path(__file__).read_bytes()),runtime_image_sha256=sha(image_runtime),capture_files=[str(x) for x in capture_files],scope='Natural whole CRT2065 first cache8198B call; actual heap entry/return,CFDF,before/after640KiBRAM; read-onlydebugger,noCPU/RAMinjection. DOS checkpoints48/4A helpers,independentreplaymustrejectanyunmodeledinterrupt.')
 (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='capture_files'},indent=2))
