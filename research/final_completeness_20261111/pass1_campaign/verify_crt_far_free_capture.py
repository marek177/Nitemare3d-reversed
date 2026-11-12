"""IMAGE RELOCS RUNTIME WORK EMULATOR: verify whole natural2052 marker/exact BYTE store and SND bank.
Original no-fixture replay, full-RAM comparison and caller/asset binding; no DOS-free inference.
"""
import csv,hashlib,json,re,struct,sys
from pathlib import Path

image,relocs,runtime,work,emulator=map(lambda p:Path(p).resolve(),sys.argv[1:]);sys.path.insert(0,str(emulator))
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_CODE,UC_HOOK_INTR,UC_HOOK_MEM_WRITE
from unicorn.x86_const import *
r=runtime.parent;sha=lambda x:hashlib.sha256(x).hexdigest();summary=json.loads((runtime/'summary.json').read_text());assert summary['success'] and summary['source_files_unchanged'];load=summary['load_segment'];b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297';expected=bytearray(b)
for row in csv.DictReader(relocs.open()):struct.pack_into('<H',expected,int(row['image_offset']),(int(row['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==expected and sha(bytes(expected))==summary['runtime_image_sha256'];assert sha((r/'runtime_watch_crt_far_free.py').read_bytes())==summary['harness_sha256'];assert summary['exe_sha256']=='a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832'
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


a=s['free_entry'];z=s['free_return'];crt=load+0x11ee;assert (a['CS'],a['IP'])==(crt,0x2052);skipped=json.loads((runtime/'skipped_zero_segment_calls.json').read_text());assert not skipped
frame=dump('candidate_00_frame.bin',a['SS']*16+a['SP'],8,'free_entry');assert frame==(work/'free_entry_frame.bin').read_bytes();rip,rcs,off,seg=struct.unpack('<4H',frame);assert seg and off>=2 and (z['CS'],z['IP'],z['SP'])==(rcs,rip,a['SP']+4)
before=dump('free_before_RAM.bin',0,0xa0000,'free_entry');after=dump('free_after_RAM.bin',0,0xa0000,'free_return');pointer=seg*16+off;address=seg*16+((off-2)&65535)
t0=dump('tag_before_with_guards.bin',address-8,17,'before_tag_OR');t1=dump('tag_after_with_guards.bin',address-8,17,'after_tag_OR');assert t0[:8]==t1[:8] and t0[9:]==t1[9:] and t1[8]==t0[8]|1 and t0[8]!=t1[8]
pre,post=s['before_tag_OR'],s['after_tag_OR'];assert (pre['CS'],pre['IP'],post['CS'],post['IP'])==(crt,0x205d,crt,0x2062) and (pre['ES'],pre['SI'])==(seg,off)
for key in pre:
 if key not in ('IP','CF'):assert pre[key]==post[key]
assert before[address:address+2]==t0[8:10] and after[address:address+2]==t1[8:10]
raw=bytearray(before+b'\0'*(0x200000-len(before)));model=raw[:];model[address]|=1;u=Uc(UC_ARCH_X86,UC_MODE_16);u.mem_map(0,len(raw));u.mem_write(0,bytes(raw));regs={'CS':UC_X86_REG_CS,'IP':UC_X86_REG_IP,'DS':UC_X86_REG_DS,'ES':UC_X86_REG_ES,'SS':UC_X86_REG_SS,'SP':UC_X86_REG_SP,'AX':UC_X86_REG_AX,'BX':UC_X86_REG_BX,'CX':UC_X86_REG_CX,'DX':UC_X86_REG_DX,'SI':UC_X86_REG_SI,'DI':UC_X86_REG_DI,'BP':UC_X86_REG_BP}
for name,key in regs.items():u.reg_write(key,a[name])
u.reg_write(UC_X86_REG_EFLAGS,2|a['CF']|(a['DF']<<10));rows=list(csv.DictReader((r/'crt_far_free_replay/crt_far_free_mark.csv').open()));allowed={int(x['image_offset']) for x in rows};done=[];stores=[];executed=[];lo=a['SS']*16+a['SP']-64;hi=a['SS']*16+a['SP']+8

def code(e,at,n,d):
 if at==rcs*16+rip:done.append(True);e.emu_stop();return
 q=at-load*16;assert q in allowed;executed.append(q)
def intr(e,n,d):raise AssertionError('free marker must not call DOS or any external body')
def write(e,access,at,n,v,d):
 if lo<=at and at+n<=hi:return
 stores.append((at,n,v))
u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_INTR,intr);u.hook_add(UC_HOOK_MEM_WRITE,write);u.emu_start(crt*16+0x2052,0x1fffff,count=40);assert done and stores==[(address,1,t1[8])];actual=bytes(u.mem_read(0,len(raw)));assert actual[:lo]==model[:lo] and actual[hi:]==model[hi:]
for name,key in regs.items():assert u.reg_read(key)==z[name],(name,u.reg_read(key),z[name])
f=u.reg_read(UC_X86_REG_EFLAGS);assert (f&1,bool(f&0x400))==(z['CF'],bool(z['DF']))
code_bytes=0
for row in rows:
 q=int(row['image_offset']);n=len(bytes.fromhex(row['bytes']));at=load*16+q;assert before[at:at+n]==after[at:at+n]==expected[q:q+n];code_bytes+=n
# Bind actual caller PUSH DWORD[17D0] / FAR CALL2052 and the music-resource frame.
assert (rcs,rip)==(load+0xc2b,0x2c0);call_image=0xc2b0+0x2bb;assert b[call_image:call_image+5].hex()=='9a5220ee11';assert before[load*16+call_image:load*16+call_image+5]==expected[call_image:call_image+5];assert b[call_image-5:call_image].hex()=='66ff36d017';dg=(load+0x2771)*16;assert a['DS']==load+0x2771 and before[dg+0x17d0:dg+0x17d4]==after[dg+0x17d0:dg+0x17d4]==struct.pack('<HH',off,seg)
caller_ID=struct.unpack_from('<H',before,a['SS']*16+a['BP']+6)[0];music_enabled=before[dg+0x414d];assert music_enabled or caller_ID==0;extent=struct.unpack_from('<H',before,address)[0]&0xfffe;assert before[pointer:pointer+extent]==after[pointer:pointer+extent];bank=before[pointer:pointer+extent]
inputs=list(csv.DictReader((runtime/'inputs.csv').open(encoding='utf-8')));matches=[]
for x in inputs:
 data=Path(x['source']).read_bytes();at=data.find(bank)
 while at>=0:matches.append(dict(source=x['source'],offset=at,end_exclusive=at+extent,length=extent,sha256=sha(bank)));at=data.find(bank,at+1)
assert len(matches)==1 and Path(matches[0]['source']).name.upper()=='SND.DAT';snd=Path(matches[0]['source']).read_bytes();length,offset=struct.unpack_from('<Hi',snd);assert (length,offset)==(extent,matches[0]['offset'])==(3204,960);assert bank[:4]==b'IBK\x1a'
projection=b''.join(bank[4+16*j:4+16*j+11] for j in range(128));bank_image=0x18103;bank_physical=load*16+bank_image;live=before[bank_physical:bank_physical+1408];assert live==projection==after[bank_physical:bank_physical+1408];assert bank_physical+1408<pointer or pointer+extent<bank_physical
bank_rows=[]
for j in range(128):
 src=offset+4+16*j;dst=bank_physical+11*j;record_raw=projection[11*j:11*j+11];bank_rows.append(dict(record=j,SND_start=src,SND_end_exclusive=src+11,bank_image_start=bank_image+11*j,bank_physical_start=dst,length=11,range_sha256=sha(record_raw),native_before_matches=True,native_after_matches=True,copy_PC_trapped=False))
with (runtime/'WORX_live_bank_records.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=list(bank_rows[0]));w.writeheader();w.writerows(bank_rows)
loader_csv=r/'worx_register_bank_replay/worx_bank_load_128x11.csv';loader_code_bytes=0
for row in csv.DictReader(loader_csv.open()):
 q=int(row['image_offset']);n=len(bytes.fromhex(row['bytes']));at=load*16+q;assert before[at:at+n]==after[at:at+n]==expected[q:q+n];loader_code_bytes+=n
(runtime/'asset_matches.json').write_text(json.dumps(matches,indent=2)+'\n');clock=set(range(dg+0x81e,dg+0x822));assert all(after[q]==model[q] for q in range(dg,dg+0xe030) if q not in clock)
residuals=[dict(address=q,before=before[q],native_after=after[q],replay_after=actual[q],category='clockDWORD endpoint delta' if q in clock else 'outside original byte-store; IRQ/stack source not assigned') for q in range(len(before)) if after[q]!=actual[q]]
with (runtime/'RAM_replay_residuals.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=['address','before','native_after','replay_after','category']);w.writeheader();w.writerows(residuals)
metrics=dict(pointer_offset=off,pointer_segment=seg,physical_tag_byte=address,tag_WORD_before=int.from_bytes(t0[8:10],'little'),tag_WORD_after=int.from_bytes(t1[8:10],'little'),native_exact_writer_cs=crt,native_exact_writer_ip=0x205d,native_tag_changed_positions=1,native_guard_bytes_unchanged=16,allocated_payload_extent=extent,payload_bytes_unchanged=extent,SND_directory_id=0,SND_offset=offset,SND_end_exclusive=offset+extent,SND_payload_sha256=sha(bank),WORX_bank_records=128,WORX_bank_bytes_bound=1408,WORX_bank_SHA256=sha(projection),WORX_bank_changed_from_default_positions=sum(x!=y for x,y in zip(live,b[0x18103:0x18683])),WORX_bank_preserved_after_free=True,WORX_bank_copy_PC_trapped=False,WORX_loader_code_bytes_checked=loader_code_bytes,caller_cs=rcs,caller_return_ip=rip,caller_music_ID_WORD=caller_ID,native_music_enable_BYTE_414D=music_enabled,DS17D0_pointer_retained=True,original_replay_instruction_events=len(executed),replay_nonstack_stores=1,replay_RAM_bytes_checked=len(raw)-(hi-lo),native_DGROUP_bytes_checked=0xe030-4,native_replay_residual_positions=len(residuals),native_full_RAM_bytes_equal_replay=len(before) if not residuals else 0,code_bytes_before_after_checked=code_bytes)
assert metrics['replay_RAM_bytes_checked']==0x200000-72 and metrics['WORX_loader_code_bytes_checked']==37
(runtime/'verification_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
files=[image,relocs,Path(__file__),r/'runtime_watch_crt_far_free.py',r/'dosbox_watch_support_newgame_v1.py',r/'crt_far_free_replay/crt_far_free_mark.csv',loader_csv,work/'free_entry_frame.bin']+[runtime/n for n in ('summary.json','transcript.json','snapshots.json','skipped_zero_segment_calls.json','inputs.csv','launch_arguments.json','runtime.conf','asset_matches.json','WORX_live_bank_records.csv','verification_metrics.json','RAM_replay_residuals.csv')]+list(groups)+parts
for x in inputs:
 for key in ('source','copy'):
  q=Path(x[key]);assert sha(q.read_bytes())==x['sha256'];files.append(q)
exe=Path(json.loads((runtime/'launch_arguments.json').read_text())[0]);assert sha(exe.read_bytes())==summary['exe_sha256'];files.append(exe);files.extend(emulator.rglob('*.dll'));files.extend(emulator.rglob('*.pyd'))
proof=dict(verified=True,runtime_tests=1,new_deep_verified_bytes=0,summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=summary['runtime_image_sha256'],scope='Natural whole2052free marker,exactnativeORbyte205D pre/post tag0C84to0C85;freepointer3F96:0016 frommusiccaller0C2B02BB/DS17D0.3204Bpayload unchanged matchesSND.DAT[3C0,1044)ID0IBKbank;DS17D0 retainedatcallee return;nativeWORX128x11projection1408Bmatchesandpersistsafterfree,1181Bdiffdefault,copyPCnottrapped. Original10instruction nofixture replay/regsCFDF/fullRAMmodel match;nativefull640KiBRAMequalsreplayinthiscapture;DGROUP/payload/guards checked,separateresidualtablekept. NotDOSfree/coalescing/musiccallercompletion/audiooutput/Win16parity.',metrics=metrics,files=[dict(path=str(q.resolve()),sha256=sha(q.read_bytes())) for q in dict.fromkeys(files)])
(runtime/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(metrics,indent=2))
