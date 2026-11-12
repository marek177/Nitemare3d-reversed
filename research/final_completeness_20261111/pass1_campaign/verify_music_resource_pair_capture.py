"""IMAGE RELOCS RUNTIME WORK EMULATOR: verify whole native music0/1+SNDreader/CRTcalls and original WORX bank-copy replay.
No full music-driver/MIDI/audio-output parity is implied by resource/call-frame verification.
"""
import csv,hashlib,json,re,struct,sys
from pathlib import Path
image,relocs,runtime,work,emulator=map(lambda p:Path(p).resolve(),sys.argv[1:]);sys.path.insert(0,str(emulator))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_INTR
from unicorn.x86_const import *
r=runtime.parent;sha=lambda x:hashlib.sha256(x).hexdigest();summary=json.loads((runtime/'summary.json').read_text());assert summary['success'] and summary['source_files_unchanged'];load=summary['load_segment'];b=image.read_bytes();expected=bytearray(b)
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
for x in csv.DictReader(relocs.open()):struct.pack_into('<H',expected,int(x['image_offset']),(int(x['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==expected and sha(bytes(expected))==summary['runtime_image_sha256'];assert sha((r/'runtime_watch_music_resource_pair_v2.py').read_bytes())==summary['harness_sha256'];assert sha((r/'dosbox_watch_support_newgame_v1.py').read_bytes())==summary['support_sha256']=='64675a5c918b22eb1d80e1d522efc1d459342a9ee04abf768a04b6a2e043fc89'
trace=json.loads((runtime/'transcript.json').read_text());music=json.loads((runtime/'music_calls.json').read_text());readers=json.loads((runtime/'reader_calls.json').read_text());apis=json.loads((runtime/'API_calls.json').read_text());banks=json.loads((runtime/'bank_calls.json').read_text());events=json.loads((runtime/'events.json').read_text());points=[];groups={};last=-10;reg={}
for index,t in enumerate(trace):
 cmd=t['command'];assert cmd in ('PING','EXEC EV CS EIP DS ES SS SP AX BX CX DX','EXEC EV SI DI BP','EXEC EV CF DF') or re.fullmatch(r'EXEC (?:BP [0-9A-F]+:[0-9A-F]+|BPDEL \*|RUN|MEMDUMPBIN .+)',cmd),cmd
 if cmd.startswith('EXEC EV '):
  keys={'EXEC EV CS EIP DS ES SS SP AX BX CX DX':('CS','IP','DS','ES','SS','SP','AX','BX','CX','DX'),'EXEC EV SI DI BP':('SI','DI','BP'),'EXEC EV CF DF':('CF','DF')}[cmd];vals=next(x.split() for x in t['response'] if re.fullmatch(r'[0-9A-Fa-f]+(?: [0-9A-Fa-f]+){%d}'%(len(keys)-1),x));d=dict(zip(keys,[int(x,16) for x in vals]))
  if len(keys)==10:reg=d
  elif len(keys)==3:assert index==last+1;reg.update(d)
  else:assert index==last+1;reg.update(d);points.append((index,dict(reg)))
  last=index
 if cmd.startswith('EXEC MEMDUMPBIN '):
  m=re.fullmatch(r'EXEC MEMDUMPBIN ([0-9A-F]+):([0-9A-F]+) ([0-9A-F]+) (.+)\.part(\d+)',cmd);assert m;seg,off,n=(int(m.group(j),16) for j in (1,2,3));path=Path(m.group(4));offset=int(m.group(5));part=Path(str(path)+'.part'+str(offset));raw_part=part.read_bytes();assert len(raw_part)==n;groups.setdefault(path,[]).append(dict(index=index,address=seg*16+off,offset=offset,path=part,raw=raw_part))
parts=[];origins={}
for path,rows in groups.items():
 payload=bytearray();origin=rows[0]['address']
 for x in rows:assert x['offset']==len(payload) and x['address']==origin+len(payload);payload.extend(x['raw']);parts.append(x['path'])
 assert path.read_bytes()==payload;origins[path.name]=dict(address=origin,length=len(payload),index=rows[0]['index'],last_index=rows[-1]['index'])
def pos(record,before_dump=None,after=-1):
 matches=[i for i,x in points if x==record and i>after and (before_dump is None or i<origins[before_dump]['index'])];assert matches,record;return max(matches) if before_dump else min(matches)
def dump(name,address,length,record):
 o=origins[name];assert (o['address'],o['length'])==(address,length);at=pos(record,before_dump=name);assert not any(x['command']=='EXEC RUN' for x in trace[at+1:o['last_index']+1]);return (work/name).read_bytes()
def frame_return(before,after,raw,n):
 rip,rcs=struct.unpack_from('<HH',raw);assert (after['CS'],after['IP'],after['SP'])==(rcs,rip,before['SP']+4)
 for key in ('BP','SI','DI','DS','SS'):assert before[key]==after[key]
inputs=list(csv.DictReader((runtime/'inputs.csv').open(encoding='utf-8')));snd_path=Path(next(x['source'] for x in inputs if Path(x['source']).name.upper()=='SND.DAT'));snd=snd_path.read_bytes();assert sha(snd)=='f3434984d315531602d32285cb8ff55990bba786f5fb37f53710e88379388614';mc=load+0xc2b;rc=load+0x277;wc=load+0x15bf;ds=load+0x2771;dg=ds*16;assert [x['ID'] for x in music]==[0,1] and len(readers)==4 and len(apis)==9 and len(banks)==1
payload_records=[];music_positions=[];all_ram=[]
for j,call in enumerate(music):
 entry,returned=call['entry'],call['returned'];assert (entry['CS'],entry['IP'],entry['DS'],entry['SS'])==(mc,0x298,ds,ds);f=dump('music_%02d_entry_frame.bin'%j,entry['SS']*16+entry['SP'],6,entry);assert f.hex()==call['entry_frame'] and struct.unpack_from('<H',f,4)[0]==j;frame_return(entry,returned,f,4);start_pos=pos(entry,before_dump='music_%02d_entry_frame.bin'%j);end_pos=pos(returned,after=start_pos);music_positions.append((start_pos,end_pos))
 before=dump('music_%02d_before_RAM.bin'%j,0,0xa0000,entry);after=dump('music_%02d_after_RAM.bin'%j,0,0xa0000,returned);all_ram.extend((before,after));assert before[entry['SS']*16+entry['SP']:entry['SS']*16+entry['SP']+6]==f
 checkpoints=call['checkpoints'];cp={x['stage']:x for x in checkpoints};assert 'after_directory_read' in cp and 'after_pointer_store' in cp and 'after_payload_read' in cp and 'before_start' in cp
 for checkpoint in checkpoints:
  at=pos(checkpoint['registers'],after=start_pos);assert at<end_pos;run=next((k for k in range(at+1,len(trace)) if trace[k]['command']=='EXEC RUN'),len(trace));ptr_dumps=[name for name,o in origins.items() if name.startswith('pointer_snapshot_') and at<o['index']<run];assert ptr_dumps
  for name in ptr_dumps:assert origins[name]['address']==dg+0x17d0 and (work/name).read_bytes()==struct.pack('<HH',*checkpoint['global_pointer'])
 directory_record=cp['after_directory_read']['registers'];directory=dump('music_%02d_directory.bin'%j,directory_record['SS']*16+directory_record['BP']-0xc4,192,directory_record);assert directory==snd[:192];length,signed_offset=struct.unpack_from('<Hi',directory,6*j);assert signed_offset>=0
 directory_path=Path(call['directory_path']);assert directory_path==work/('music_%02d_directory.bin'%j)
 for role,checkpoint in [('before_driver','after_payload_read'),('after_driver','after_IBK_driver' if not j else 'after_MIDI_driver'),('returned',None)]:
  record=call[role+'_payload'];assert record['length']==length;reg=returned if checkpoint is None else cp[checkpoint]['registers'];name='music_%02d_%s_payload.bin'%(j,role);data=dump(name,record['segment']*16+record['offset'],length,reg);assert sha(data)==record['sha256'] and data==snd[signed_offset:signed_offset+length];payload_records.append(dict(music_ID=j,role=role,offset=record['offset'],segment=record['segment'],length=length,SND_start=signed_offset,SND_end_exclusive=signed_offset+length,sha256=sha(data)))
 pointer=call['before_driver_payload'];newptr=(pointer['offset'],pointer['segment']);assert cp['after_pointer_store']['global_pointer']==list(newptr) and cp['after_payload_read']['global_pointer']==list(newptr) and after[dg+0x17d0:dg+0x17d4]==struct.pack('<HH',*newptr)
 malloc_ret=cp['after_malloc']['registers'];assert (malloc_ret['AX'],malloc_ret['DX'])==newptr
 oldptr=struct.unpack_from('<HH',before,dg+0x17d0);assert cp['after_malloc']['global_pointer']==list(oldptr)
 if j:
  assert 'after_free' in cp and cp['after_free']['global_pointer']==list(oldptr);oldphysical=oldptr[1]*16+oldptr[0];assert after[oldphysical-2]==before[oldphysical-2]|1 and after[oldphysical:oldphysical+3204]==before[oldphysical:oldphysical+3204]==snd[960:4164];assert oldptr!=newptr
 else:assert oldptr==(0,0) and 'after_free' not in cp
 driver=cp['before_IBK_driver' if not j else 'before_MIDI_driver'];args=bytes.fromhex(driver['driver_args_hex']);argsname='music_%02d_%s_args.bin'%(j,driver['stage']);assert dump(argsname,driver['registers']['SS']*16+driver['registers']['SP'],len(args),driver['registers'])==args
 assert struct.unpack('<5H',args)==(0x39,0,0,newptr[1],newptr[0]) if not j else struct.unpack('<2H',args)==newptr
# Every reader frame and CRT-call frame is bound to its native entry/return and expected resource transfer.
reader_rows=[];api_positions=[]
for k,call in enumerate(readers):
 entry,returned=call['entry'],call['after'];j=call['music'];f=dump('reader_%02d_entry_frame.bin'%k,entry['SS']*16+entry['SP'],14,entry);assert f.hex()==call['entry_frame'];frame_return(entry,returned,f,12);off,seg,offset,count=struct.unpack_from('<HHIH',f,4);assert dump('reader_%02d_filename.bin'%k,entry['DS']*16+0x1ae,8,entry)==b'snd.dat\0';cached=int.from_bytes(dump('reader_%02d_cached_handle.bin'%k,entry['DS']*16+0x1ac,2,entry),'little');assert cached==(0 if k==0 else 5)
 expected_offset,expected_count=(0,192) if k%2==0 else struct.unpack_from('<Hi',snd,6*j)[::-1];assert (offset,count)==(expected_offset,expected_count)
 if k%2==0:assert (off,seg)==((entry['BP']-0xc4)&65535,entry['SS'])
 else:assert (off,seg)==(music[j]['before_driver_payload']['offset'],music[j]['before_driver_payload']['segment'])
 assert returned['AX']==count and entry['DS']==ds;reader_rows.append(dict(reader=k,music_ID=j,cached_handle_before=cached,offset=offset,count=count,destination_offset=off,destination_segment=seg,returned_AX=returned['AX']))
 these=[x for x in apis if x['reader']==k];assert [x['name'] for x in these]==(['open'] if k==0 else [])+['seek','far_read']
 for call_api in these:
  h=call_api['index'];areg,breg=call_api['entry'],call_api['after'];name=call_api['name'];n=8 if name=='open' else 12;af=dump('API_%02d_entry_frame.bin'%h,areg['SS']*16+areg['SP'],n,areg);assert af.hex()==call_api['entry_frame'];rip,rcs=struct.unpack_from('<HH',af);assert rcs==rc and rip=={'open':0x9f,'seek':0xc5,'far_read':0xd7}[name];assert (breg['CS'],breg['IP'],breg['SP'])==(rcs,rip,areg['SP']+4);assert music_positions[j][0]<pos(areg,before_dump='API_%02d_entry_frame.bin'%h)<pos(breg,after=pos(areg))<music_positions[j][1]
  if name=='open':assert struct.unpack_from('<2H',af,4)==(0x1ae,0x8000) and breg['AX']==5
  elif name=='seek':assert struct.unpack_from('<HIH',af,4)==(5,offset,0) and ((breg['DX']<<16)|breg['AX'])==offset
  else:assert struct.unpack_from('<4H',af,4)==(5,off,seg,count) and breg['AX']==count
assert all(int.from_bytes(mem[dg+0x1ac:dg+0x1ae],'little')==5 for mem in all_ram[1:])
# Original whole bank loader + original normalizer; no API/resolver fixture in replay.
call=banks[0];entry,before_ret,returned=call['entry'],call['before_RET'],call['returned'];assert call['music']==0 and (entry['CS'],entry['IP'],entry['DS'])==(wc,0x5973,wc);nf=dump('bank_00_entry_frame.bin',entry['SS']*16+entry['SP'],2,entry);rip=struct.unpack('<H',nf)[0];assert (returned['CS'],returned['IP'],returned['SP'])==(wc,rip,entry['SP']+2)
bank_before=dump('bank_00_before_RAM.bin',0,0xa0000,entry);bank_after=dump('bank_00_after_RAM.bin',0,0xa0000,before_ret);bank_source=entry['ES']*16+entry['DI'];assert bank_before[bank_source:bank_source+3204]==snd[960:4164];dst=wc*16+0x2513;projection=b''.join(snd[960+4+16*j:960+4+16*j+11] for j in range(128));assert bank_after[dst:dst+1408]==projection;assert music_positions[0][0]<pos(entry,before_dump='bank_00_entry_frame.bin')<pos(before_ret)<pos(returned)<music_positions[0][1]
sources=[r/'worx_register_bank_replay/worx_bank_load_128x11.csv',r/'worx_leafs/normalize_es_di.csv'];allowed=set()
for source in sources:allowed.update(int(x['image_offset']) for x in csv.DictReader(source.open()))
initial=bank_before+b'\0'*(0x200000-len(bank_before));model=bytearray(initial);model[dst:dst+1408]=projection;u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(initial));u.mem_write(0,initial);regs={'CS':UC_X86_REG_CS,'IP':UC_X86_REG_IP,'DS':UC_X86_REG_DS,'ES':UC_X86_REG_ES,'SS':UC_X86_REG_SS,'SP':UC_X86_REG_SP,'AX':UC_X86_REG_AX,'BX':UC_X86_REG_BX,'CX':UC_X86_REG_CX,'DX':UC_X86_REG_DX,'SI':UC_X86_REG_SI,'DI':UC_X86_REG_DI,'BP':UC_X86_REG_BP}
for name,key in regs.items():u.reg_write(key,entry[name])
u.reg_write(UC_X86_REG_EFLAGS,2|entry['CF']|(entry['DF']<<10));lo=entry['SS']*16+entry['SP']-64;hi=entry['SS']*16+entry['SP']+8;done=[];stores=[];steps=[]
def code(e,address,n,d):
 if address==wc*16+rip:done.append(True);e.emu_stop();return
 q=address-load*16;assert q in allowed;steps.append(q)
def write(e,access,address,n,value,d):
 if not(lo<=address and address+n<=hi):stores.append((address,n,value))
def intr(e,n,d):raise AssertionError('bank and normalizer replay must not need API/resolver fixture')
u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write);u.hook_add(UC_HOOK_INTR,intr);u.emu_start(wc*16+0x5973,0x1fffff,count=20000);assert done and stores==[(dst+j,1,x) for j,x in enumerate(projection)];replay=bytes(u.mem_read(0,len(initial)));assert replay[:lo]==model[:lo] and replay[hi:]==model[hi:]
for name,key in regs.items():assert u.reg_read(key)==returned[name],(name,u.reg_read(key),returned[name])
f=u.reg_read(UC_X86_REG_EFLAGS);assert (f&1,bool(f&0x400))==(returned['CF'],bool(returned['DF']))
assert all_ram[1][dst:dst+1408]==all_ram[2][dst:dst+1408]==all_ram[3][dst:dst+1408]==projection;assert dump('music_00_entry_WORX_bank.bin',dst,1408,music[0]['entry'])==bank_before[dst:dst+1408]
residuals=[dict(address=q,native=bank_after[q],replay=replay[q],scope='outside copiedbank; IRQ/stack effects unassigned') for q in range(len(bank_after)) if bank_after[q]!=replay[q]];assert all(not dst<=x['address']<dst+1408 for x in residuals)
# Pinned original music/reader/bank/normalizer code before and after, not whole-driver closure.
code_sources=[r/'pass1_music_resource/instructions.csv',r/'music_snd_reader_replay/music_snd_reader.csv']+sources;code_bytes=0
for source in code_sources:
 for row in csv.DictReader(source.open()):
  q=int(row['image_offset']);n=len(bytes.fromhex(row['bytes']));at=load*16+q
  for mem in all_ram+[bank_before,bank_after]:assert mem[at:at+n]==expected[q:q+n]
  code_bytes+=n
with (runtime/'payload_bindings.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(payload_records[0]));w.writeheader();w.writerows(payload_records)
with (runtime/'reader_bindings.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(reader_rows[0]));w.writeheader();w.writerows(reader_rows)
with (runtime/'bank_RAM_residuals.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=['address','native','replay','scope']);w.writeheader();w.writerows(residuals)
metrics=dict(whole_music_call_IDs=[0,1],native_reader_calls=4,native_CRT_open_calls=1,native_CRT_seek_calls=4,native_CRT_farread_calls=4,cached_handle=5,total_requested_reader_bytes=sum(x['count'] for x in reader_rows),IBK_pointer_offset=music[0]['before_driver_payload']['offset'],IBK_pointer_segment=music[0]['before_driver_payload']['segment'],MIDI_pointer_offset=music[1]['before_driver_payload']['offset'],MIDI_pointer_segment=music[1]['before_driver_payload']['segment'],IBK_length=3204,MIDI_length=20290,MIDI_header_fields=list(struct.unpack_from('>HHH',snd,4164+8)),MIDI_payload_sha256=sha(snd[4164:24454]),payloads_unchanged_after_driver=True,native_bank_copy_calls=1,original_bank_replay_instruction_events=len(steps),original_bank_unique_starts=len(set(steps)),original_bank_replay_BYTE_stores=len(stores),bank_records=128,bank_bytes=1408,bank_changed_from_native_before_positions=sum(x!=y for x,y in zip(bank_before[dst:dst+1408],projection)),bank_sha256=sha(projection),bank_native_replay_residual_positions=len(residuals),bank_full_native_RAM_equal_replay=not bool(residuals),old_IBK_pointer_retained_until_new_pointer_stores=True,old_IBK_tag_marked_not_erased=True,code_bytes_before_after_checked=code_bytes)
assert metrics['total_requested_reader_bytes']==23878 and metrics['code_bytes_before_after_checked']==453
(runtime/'verification_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
files=[image,relocs,Path(__file__),r/'runtime_watch_music_resource_pair_v2.py',r/'dosbox_watch_support_newgame_v1.py']+code_sources+[runtime/n for n in ('summary.json','transcript.json','music_calls.json','reader_calls.json','API_calls.json','bank_calls.json','events.json','inputs.csv','launch_arguments.json','runtime.conf','payload_bindings.csv','reader_bindings.csv','bank_RAM_residuals.csv','verification_metrics.json')]+list(groups)+parts
for x in inputs:
 for key in ('source','copy'):
  q=Path(x[key]);assert sha(q.read_bytes())==x['sha256'];files.append(q)
exe=Path(json.loads((runtime/'launch_arguments.json').read_text())[0]);assert sha(exe.read_bytes())==summary['exe_sha256']=='a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832';files.append(exe);files.extend(emulator.rglob('*.dll'));files.extend(emulator.rglob('*.pyd'))
proof=dict(verified=True,runtime_tests=1,new_deep_verified_bytes=0,summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=summary['runtime_image_sha256'],scope='Natural wholemusicID0/1callerentry-return,4wholeSNDreadertransfers/1actualCRTopen+4seek+4farread,all23878requestedbytes/source/frames verified. ID1oldIBKpointerretaineduntilnewstores,oldbanktagmarked;newMIDI8D9B0016/20290Bexactsourceunchangedafterdriver/return. ActualWORXbankloaderentry/nearRET+originalnormalizerreplay,noresolverstub,1408orderedstores/regsCFDF match. Bankresiduals explicit;nofullmusic-driverRAM/MIDIevent/audiooutput/timing/Win16parity. v1partialstaleBPcaptureuncounted.',metrics=metrics,files=[dict(path=str(q.resolve()),sha256=sha(q.read_bytes())) for q in dict.fromkeys(files)])
(runtime/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(metrics,indent=2))
