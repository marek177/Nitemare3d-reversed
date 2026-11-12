"""DOSBOX GAME IMAGE RELOCS OUT WORK palette_init DSTOPEN_IMG: whole first ID0/ID1 music loads and actual WORX bank copy.
Read-only debugger; native dependencies unmodified. Full callers/readers/APIs and bank-loader boundaries.
"""
from pathlib import Path
support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');support_bytes=support.read_bytes();exec(compile(support_bytes,str(support),'exec'),globals())
extra=Path(sys.argv[8]).resolve();extra_raw=extra.read_bytes();assert sha(extra_raw)=='af574568089f1998ca50ceeba310ff068c728279ff470cd39f47a8919228b95a';extra_copy=drive/'DSTOPEN.IMG';extra_copy.write_bytes(extra_raw);inputs.append(dict(source=str(extra),copy=str(extra_copy),bytes=len(extra_raw),sha256=sha(extra_raw)))
with (out/'inputs.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(inputs[0]));w.writeheader();w.writerows(inputs)
music=[];readers=[];api_calls=[];banks=[];events=[];capture_files=[];active_music=None;active_reader=None;active_bank=None;pending_music={};pending_reader={};pending_api={};pending_bank={};bpkeys=set();load=None;image_runtime=b''
def fullregs():
 reg=regs()
 for command,keys in [('EXEC EV SI DI BP',('SI','DI','BP')),('EXEC EV CF DF',('CF','DF'))]:
  response=request(command);values=next(x.split() for x in response if re.fullmatch(r'[0-9A-Fa-f]+(?: [0-9A-Fa-f]+){%d}'%(len(keys)-1),x));reg.update(dict(zip(keys,[int(x,16) for x in values])))
 return reg
def grab(seg,off,n,name):raw=dump(seg,off,n,name);capture_files.append(work/name);return raw
def bp(cs,ip):
 if (cs,ip) not in bpkeys:request('EXEC BP %04X:%08X'%(cs,ip));bpkeys.add((cs,ip))
def ptr(reg):return struct.unpack('<HH',grab(reg['DS'],0x17d0,4,'pointer_event_%03d.bin'%len(events)))
def capture_payload(rec,reg,role):
 off,seg=ptr(reg);length=struct.unpack_from('<H',Path(rec['directory_path']).read_bytes(),6*rec['ID'])[0];assert seg and length
 name='music_%02d_%s_payload.bin'%(rec['index'],role);data=grab(seg,off,length,name);rec[role+'_payload']=dict(path=str(work/name),offset=off,segment=seg,length=length,sha256=sha(data))
try:
 conn,address=server.accept();conn.settimeout(8);request('PING');time.sleep(1);initial=regs();load=initial['DS']+16;assert initial['CS']==load+entry_cs and initial['IP']==entry_ip;crt=load+0x11ee;mc=load+0xc2b;rc=load+0x277;wc=load+0x15bf
 bp(crt,0x18);request('EXEC RUN');wait_for(crt,0x18);image_runtime=grab(load,0,len(canonical),'unpacked_runtime.bin');expected=bytearray(canonical)
 for row in csv.DictReader(relocations.open()):struct.pack_into('<H',expected,int(row['image_offset']),(int(row['original_word'])+load)&65535)
 assert image_runtime==expected;request('EXEC BPDEL *');bpkeys.clear()
 mpoints={0x2c0:'after_free',0x2c7:'after_stop',0x2da:'after_directory_read',0x334:'after_malloc',0x33e:'after_pointer_store',0x355:'after_payload_read',0x368:'before_IBK_driver',0x36d:'after_IBK_driver',0x381:'before_MIDI_driver',0x386:'after_MIDI_driver',0x38d:'before_negative_driver',0x392:'after_tune_driver',0x395:'before_start',0x399:'loader_epilogue'}
 for cs,ip in [(mc,0x298),(rc,0x8a),(rc,0x9f),(rc,0xc5),(rc,0xd7),(wc,0x5973),(wc,0x5997)]+[(mc,x) for x in mpoints]+[(crt,0x1c72),(crt,0x1bd6),(load+0xfba,0x9e)]:bp(cs,ip)
 api_targets={(crt,0x1c72):('open',4),(crt,0x1bd6):('seek',8),(load+0xfba,0x9e):('far_read',8)};request('EXEC RUN');deadline=time.monotonic()+105;iterations=0
 while time.monotonic()<deadline:
  reg=fullregs();key=(reg['CS'],reg['IP']);handled=False;iterations+=1;assert iterations<4096
  if key in pending_api:
   j=pending_api.pop(key);api_calls[j]['after']=reg;handled=True
  if key in pending_reader:
   j=pending_reader.pop(key);readers[j]['after']=reg;active_reader=None;handled=True
  if key in pending_bank:
   j=pending_bank.pop(key);banks[j]['returned']=reg;active_bank=None;handled=True
  if key in pending_music:
   j=pending_music.pop(key);assert active_music==j;rec=music[j];rec['returned']=reg;grab(0,0,0xa0000,'music_%02d_after_RAM.bin'%j);capture_payload(rec,reg,'returned');grab(wc,0x2513,1408,'music_%02d_returned_WORX_bank.bin'%j);active_music=None;events.append(dict(kind='music_return',index=j,registers=reg));handled=True
   if len(music)==2:success=True;break
  if key==(mc,0x298):
   assert active_music is None and len(music)<2;j=len(music);f=grab(reg['SS'],reg['SP'],6,'music_%02d_entry_frame.bin'%j);rip,rcs,ID=struct.unpack('<3H',f);assert ID in (0,1);rec=dict(index=j,ID=ID,entry=reg,entry_frame=f.hex(),checkpoints=[]);music.append(rec);active_music=j;pending_music[(rcs,rip)]=j;bp(rcs,rip);grab(0,0,0xa0000,'music_%02d_before_RAM.bin'%j);grab(wc,0x2513,1408,'music_%02d_entry_WORX_bank.bin'%j);events.append(dict(kind='music_entry',index=j,ID=ID,registers=reg));handled=True
  elif key==(rc,0x8a):
   if active_music is not None:
    assert active_reader is None;j=len(readers);f=grab(reg['SS'],reg['SP'],14,'reader_%02d_entry_frame.bin'%j);rip,rcs=struct.unpack_from('<HH',f);assert rcs==mc and rip in (0x2da,0x355);readers.append(dict(index=j,music=active_music,entry=reg,entry_frame=f.hex()));pending_reader[(rcs,rip)]=j;active_reader=j;bp(rcs,rip);grab(reg['DS'],0x1ae,8,'reader_%02d_filename.bin'%j);grab(reg['DS'],0x1ac,2,'reader_%02d_cached_handle.bin'%j);events.append(dict(kind='reader_entry',index=j,registers=reg))
   handled=True
  elif key in api_targets:
   if active_music is not None and active_reader is not None:
    name,n=api_targets[key];j=len(api_calls);f=grab(reg['SS'],reg['SP'],4+n,'API_%02d_entry_frame.bin'%j);rip,rcs=struct.unpack_from('<HH',f)
    if rcs==rc:
     api_calls.append(dict(index=j,reader=active_reader,name=name,entry=reg,entry_frame=f.hex()));pending_api[(rcs,rip)]=j;bp(rcs,rip);events.append(dict(kind='reader_API',index=j,name=name,registers=reg))
   handled=True
  elif key==(wc,0x5973):
   assert active_music is not None and active_bank is None;j=len(banks);f=grab(reg['SS'],reg['SP'],2,'bank_%02d_entry_frame.bin'%j);rip=struct.unpack('<H',f)[0];banks.append(dict(index=j,music=active_music,entry=reg,entry_frame=f.hex()));active_bank=j;pending_bank[(wc,rip)]=j;bp(wc,rip);grab(0,0,0xa0000,'bank_%02d_before_RAM.bin'%j);events.append(dict(kind='bank_entry',index=j,registers=reg));handled=True
  elif key==(wc,0x5997):
   assert active_bank is not None;banks[active_bank]['before_RET']=reg;grab(0,0,0xa0000,'bank_%02d_after_RAM.bin'%active_bank);events.append(dict(kind='bank_before_RET',index=active_bank,registers=reg));handled=True
  elif reg['CS']==mc and reg['IP'] in mpoints and active_music is not None:
   rec=music[active_music];name=mpoints[reg['IP']];record=dict(stage=name,registers=reg);rec['checkpoints'].append(record);events.append(dict(kind='music_checkpoint',music=active_music,stage=name,registers=reg));off,seg=ptr(reg);record['global_pointer']=[off,seg]
   if name=='after_directory_read':
    directory=grab(reg['SS'],reg['BP']-0xc4,192,'music_%02d_directory.bin'%active_music);rec['directory_path']=str(work/('music_%02d_directory.bin'%active_music));record['directory_sha256']=sha(directory)
   if name=='after_payload_read':capture_payload(rec,reg,'before_driver')
   if name in ('after_IBK_driver','after_MIDI_driver'):capture_payload(rec,reg,'after_driver')
   if name in ('before_IBK_driver','before_MIDI_driver','before_negative_driver'):
    n=10 if name=='before_IBK_driver' else 4;record['driver_args_hex']=grab(reg['SS'],reg['SP'],n,'music_%02d_%s_args.bin'%(active_music,name)).hex()
   handled=True
  elif reg['CS']==rc and reg['IP'] in (0x9f,0xc5,0xd7):handled=True
  if handled:request('EXEC RUN')
  else:time.sleep(.02)
 assert success and [x['ID'] for x in music]==[0,1] and all('after' in x for x in readers+api_calls) and all('returned' in x for x in banks),'whole native music pair incomplete'
except Exception as e:error=repr(e);success=False
finally:
 if conn:conn.close()
 server.close()
 if p.poll() is None:p.terminate()
 try:p.communicate(timeout=5)
 except subprocess.TimeoutExpired:p.kill();p.communicate()
 unchanged=all(sha(Path(x['source']).read_bytes())==x['sha256'] for x in inputs)
 for name,data in [('music_calls',music),('reader_calls',readers),('API_calls',api_calls),('bank_calls',banks),('events',events),('transcript',transcript)]: (out/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
 result=dict(success=success,error=error,load_segment=load,runtime_tests=1 if success else 0,new_deep_verified_bytes=0,source_files_unchanged=unchanged,game_source_sha256=sha(packed),exe_sha256=sha(exe.read_bytes()),support_sha256=sha(support_bytes),harness_sha256=sha(Path(__file__).read_bytes()),runtime_image_sha256=sha(image_runtime),music_calls=len(music),reader_calls=len(readers),reader_API_calls=len(api_calls),bank_calls=len(banks),capture_files=[str(x) for x in capture_files],scope='Natural first ID0bank/ID1tune wholemusicresource callers,originalSNDreader/CRTAPI/driverdependencies,andactualWORXbankloaderentry/RET. Read-onlybreakpoints/RAM/regsCFDF,noCPUinjection. Independentverificationrequired;notaudibleaudio/fullMIDIsemantics.')
 (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='capture_files'},indent=2))
