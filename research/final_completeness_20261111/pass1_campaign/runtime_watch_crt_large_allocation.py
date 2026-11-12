"""DOSBOX GAME IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG: natural large probe allocation/free.
Read-only debugger capture; no register/memory injection. Stop only first successful probe allocation.
"""
from pathlib import Path
support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');support_bytes=support.read_bytes();exec(compile(support_bytes,str(support),'exec'),globals())
extra=Path(sys.argv[8]).resolve();raw_extra=extra.read_bytes();assert sha(raw_extra)=='af574568089f1998ca50ceeba310ff068c728279ff470cd39f47a8919228b95a';extra_copy=drive/'DSTOPEN.IMG';extra_copy.write_bytes(raw_extra);inputs.append(dict(source=str(extra),copy=str(extra_copy),bytes=len(raw_extra),sha256=sha(raw_extra)))
with (out/'inputs.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(inputs[0]));w.writeheader();w.writerows(inputs)
stages=[];capture_files=[];load=None;image_runtime=b''
def fullregs():
 r=regs()
 for command,keys in [('EXEC EV SI DI BP',('SI','DI','BP')),('EXEC EV CF DF',('CF','DF'))]:
  response=request(command);v=next(x.split() for x in response if re.fullmatch(r'[0-9A-Fa-f]+(?: [0-9A-Fa-f]+){%d}'%(len(keys)-1),x));r.update(dict(zip(keys,[int(x,16) for x in v])))
 return r
def grab(seg,off,n,name):data=dump(seg,off,n,name);capture_files.append(work/name);return data
def stage(name,cs,ip):
 request('EXEC BP %04X:%08X'%(cs,ip));request('EXEC RUN');wait_for(cs,ip,20);r=fullregs();stages.append(dict(stage=name,registers=r));return r
try:
 conn,address=server.accept();conn.settimeout(8);request('PING');time.sleep(1);initial=regs();load=initial['DS']+16;assert initial['CS']==load+entry_cs and initial['IP']==entry_ip;crt=load+0x11ee
 reg=stage('crt_entry',crt,0x18);image_runtime=grab(load,0,len(canonical),'unpacked_runtime.bin');expected=bytearray(canonical)
 for x in csv.DictReader(relocations.open()):struct.pack_into('<H',expected,int(x['image_offset']),(int(x['original_word'])+load)&65535)
 assert image_runtime==expected;request('EXEC BPDEL *')
 reg=stage('probe_entry',load+0xfba,0x58);grab(reg['SS'],reg['SP'],4,'probe_entry_frame.bin');request('EXEC BPDEL *')
 reg=stage('large_allocation_accepted',crt,0x2a87);assert reg['SS']==reg['DS']==load+0x2771
 args=grab(reg['SS'],reg['BP'],12,'large_allocation_frame.bin');assert struct.unpack_from('<HH',args,2)==(0x82,load+0xfba)
 count,size=struct.unpack_from('<IH',args,6);segment=reg['AX'];paragraphs=reg['BX'];assert 0<count*size<=0xffff0 and segment*16+paragraphs*16+16<=0xa0000
 grab(0,0,0xa0000,'large_before_zero_RAM.bin');request('EXEC BPDEL *')
 reg=stage('large_zero_complete',crt,0x2ae6);grab(0,0,0xa0000,'large_after_zero_RAM.bin');request('EXEC BPDEL *')
 reg=stage('large_allocator_return',load+0xfba,0x82);assert (reg['AX'],reg['DX'])==(0,segment);request('EXEC BPDEL *')
 reg=stage('large_free_entry',crt,0x2a0a);grab(reg['SS'],reg['SP'],8,'large_free_frame.bin');grab(segment-1,0,paragraphs*16+32,'large_before_free_with_guards.bin');request('EXEC BPDEL *')
 reg=stage('large_free_before_DOS',crt,0x2a12);assert reg['AX']>>8==0x49 and reg['ES']==segment;request('EXEC BPDEL *')
 reg=stage('large_free_after_DOS',crt,0x2a14);grab(segment-1,0,paragraphs*16+32,'large_after_free_with_guards.bin');request('EXEC BPDEL *')
 reg=stage('probe_return',load+0xfba,0x9b);assert reg['AX']==count*size//1024;success=True
except Exception as e:error=repr(e);success=False
finally:
 if conn:conn.close()
 server.close()
 if p.poll() is None:p.terminate()
 try:p.communicate(timeout=5)
 except subprocess.TimeoutExpired:p.kill();p.communicate()
 unchanged=all(sha(Path(x['source']).read_bytes())==x['sha256'] for x in inputs)
 (out/'transcript.json').write_text(json.dumps(transcript,indent=2)+'\n');(out/'snapshots.json').write_text(json.dumps(stages,indent=2)+'\n')
 result=dict(success=success,error=error,load_segment=load,runtime_tests=1 if success else 0,new_deep_verified_bytes=0,source_files_unchanged=unchanged,game_source_sha256=sha(packed),exe_sha256=sha(exe.read_bytes()),support_sha256=sha(support_bytes),harness_sha256=sha(Path(__file__).read_bytes()),runtime_image_sha256=sha(image_runtime),capture_files=[str(x) for x in capture_files],scope='Natural original first successful large probe allocation and DOS AH49 free; before/after640KiBRAM/frames/CF/DF and allocationguards. Read-only debuggerpauses; independentverificationrequired. Failed predecessor allocations not individually trapped.')
 (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='capture_files'},indent=2))
