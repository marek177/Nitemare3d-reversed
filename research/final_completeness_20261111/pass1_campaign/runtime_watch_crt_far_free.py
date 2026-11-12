"""DOSBOX GAME IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG: first natural nonzero-segment CRT2052 free.
Read-only entry,exact OR-BYTE before/after and return captures; no game/register/memory injection.
"""
from pathlib import Path
support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');support_bytes=support.read_bytes();exec(compile(support_bytes,str(support),'exec'),globals())
extra=Path(sys.argv[8]).resolve();eraw=extra.read_bytes();assert sha(eraw)=='af574568089f1998ca50ceeba310ff068c728279ff470cd39f47a8919228b95a';target=drive/'DSTOPEN.IMG';target.write_bytes(eraw);inputs.append(dict(source=str(extra),copy=str(target),bytes=len(eraw),sha256=sha(eraw)))
with (out/'inputs.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(inputs[0]));w.writeheader();w.writerows(inputs)
stages=[];capture_files=[];load=None;image_runtime=b'';skipped=[]
def fullregs():
 reg=regs()
 for cmd,keys in [('EXEC EV SI DI BP',('SI','DI','BP')),('EXEC EV CF DF',('CF','DF'))]:
  response=request(cmd);v=next(x.split() for x in response if re.fullmatch(r'[0-9A-Fa-f]+(?: [0-9A-Fa-f]+){%d}'%(len(keys)-1),x));reg.update(dict(zip(keys,[int(x,16) for x in v])))
 return reg
def grab(seg,off,n,name):raw=dump(seg,off,n,name);capture_files.append(work/name);return raw
def stage(name,cs,ip,timeout=20):
 request('EXEC BP %04X:%08X'%(cs,ip));request('EXEC RUN');wait_for(cs,ip,timeout);reg=fullregs();stages.append(dict(stage=name,registers=reg));return reg
try:
 conn,address=server.accept();conn.settimeout(8);request('PING');time.sleep(1);initial=regs();load=initial['DS']+16;assert initial['CS']==load+entry_cs and initial['IP']==entry_ip;crt=load+0x11ee
 reg=stage('crt_entry',crt,0x18);image_runtime=grab(load,0,len(canonical),'unpacked_runtime.bin');expected=bytearray(canonical)
 for row in csv.DictReader(relocations.open()):struct.pack_into('<H',expected,int(row['image_offset']),(int(row['original_word'])+load)&65535)
 assert image_runtime==expected;request('EXEC BPDEL *');reg=stage('free_entry',crt,0x2052,90)
 while True:
  frame=grab(reg['SS'],reg['SP'],8,'candidate_%02d_frame.bin'%len(skipped));rip,rcs,off,seg=struct.unpack('<4H',frame)
  if seg:break
  skipped.append(dict(registers=reg,frame_hex=frame.hex()));stages.pop();request('EXEC RUN');wait_for(crt,0x2052,30);reg=fullregs();stages.append(dict(stage='free_entry',registers=reg));assert len(skipped)<16
 (work/'free_entry_frame.bin').write_bytes(frame);capture_files.append(work/'free_entry_frame.bin');physical=seg*16+((off-2)&65535);assert 16<=physical and physical+16<=0xa0000
 grab(0,0,0xa0000,'free_before_RAM.bin');request('EXEC BPDEL *');reg=stage('before_tag_OR',crt,0x205d);assert (reg['ES'],reg['SI'])==(seg,off);grab((physical-8)>>4,(physical-8)&15,17,'tag_before_with_guards.bin');request('EXEC BPDEL *')
 reg=stage('after_tag_OR',crt,0x2062);grab((physical-8)>>4,(physical-8)&15,17,'tag_after_with_guards.bin');request('EXEC BPDEL *');reg=stage('free_return',rcs,rip);grab(0,0,0xa0000,'free_after_RAM.bin');success=True
except Exception as e:error=repr(e);success=False
finally:
 if conn:conn.close()
 server.close()
 if p.poll() is None:p.terminate()
 try:p.communicate(timeout=5)
 except subprocess.TimeoutExpired:p.kill();p.communicate()
 unchanged=all(sha(Path(x['source']).read_bytes())==x['sha256'] for x in inputs)
 (out/'snapshots.json').write_text(json.dumps(stages,indent=2)+'\n');(out/'transcript.json').write_text(json.dumps(transcript,indent=2)+'\n');(out/'skipped_zero_segment_calls.json').write_text(json.dumps(skipped,indent=2)+'\n')
 result=dict(success=success,error=error,load_segment=load,runtime_tests=1 if success else 0,new_deep_verified_bytes=0,source_files_unchanged=unchanged,game_source_sha256=sha(packed),exe_sha256=sha(exe.read_bytes()),support_sha256=sha(support_bytes),harness_sha256=sha(Path(__file__).read_bytes()),runtime_image_sha256=sha(image_runtime),capture_files=[str(x) for x in capture_files],scope='Natural original first nonzero-segment CRT2052free: entry/ORpre/ORpost/return CFDFframes,2x640KiBRAM;read-only debugger. Exacttagchange requiresindependentverification; notDOSfree/coalescing/nativeallerrors.')
 (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='capture_files'},indent=2))
