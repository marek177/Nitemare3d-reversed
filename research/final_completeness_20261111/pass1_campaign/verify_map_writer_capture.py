"""python verify_map_writer_capture.py IMAGE RELOCS CURRENT_MAP OUT WORK
Verify map initialization return and pre-music-selection call endpoint, not a rendered gameplay frame.
"""
import collections,csv,hashlib,json,re,struct,sys
from pathlib import Path
image,relocs,mapping,out,work=map(lambda x:Path(x).resolve(),sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest();s=json.loads((out/'summary.json').read_text());b=image.read_bytes()
assert s['success'] and s['newgame_map_runtime'] and s['runtime_tests']==1 and s['source_files_unchanged']
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
assert s['game_source_sha256']=='552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301' and s['exe_sha256']=='a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832'
inputs=list(csv.DictReader((out/'inputs.csv').open()));assert len(inputs)==23
for r in inputs:assert sha(Path(r['source']).read_bytes())==sha(Path(r['copy']).read_bytes())==r['sha256']
support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');harness=Path(__file__).with_name('runtime_watch_map_writers.py');assert sha(support.read_bytes())==s['support_sha256'] and sha(harness.read_bytes())==s['harness_sha256']
load=s['load_segment'];expected=bytearray(b)
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',expected,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==expected
assert sha(mapping.read_bytes())=='497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe'
unknown=set()
for r in csv.DictReader(mapping.open(encoding='utf-8-sig')):
 if r['status']=='UNKNOWN':unknown.update(range(int(r['start']),int(r['end_exclusive'])))
physical={load*16+a for a in unknown};assert len(physical)==28
initial={int(k):v for k,v in s['initial'].items()};final={int(k):v for k,v in s['final'].items()};cache={int(k):v for k,v in s['cache_initial'].items()}
assert set(cache)==physical==set(s['calibrated_addresses']) and all(cache[a]==initial[a]==0 for a in physical)
t=json.loads((out/'transcript.json').read_text());commands=[r['command'] for r in t]
ports=['EXEC OUTP 03CE 0004']+['EXEC OUTP 03CF %04X'%n for n in range(4)]+['EXEC OUTP 03CF 0000','EXEC OUTP 03CE 0006'];queries=['EXEC VGA '+n for n in ('GC','SEQ','MODE','AC','DAC','DACPAL')]
allowed=('EXEC EV ','EXEC BP ','EXEC BPLM ','EXEC BPLIST','EXEC BPDEL ','EXEC RUN','EXEC MEMDUMPBIN ')
assert all(c=='PING' or c.startswith(allowed) or c in ports+queries for c in commands)
assert [c for c in commands if c.startswith('EXEC OUTP ')]==ports and commands[-1]=='EXEC BPDEL *' and commands.count('EXEC BPDEL *')==2
assert not any(c=='EXEC RUN' for c in commands[commands.index(ports[0]):])
assert {int(c.split()[-1],16) for c in commands if c.startswith('EXEC BPLM ')}==physical
for response in t:
 if response['command']=='EXEC BPLIST':
  found={}
  for line in response['response']:
   m=re.search(r'\bBPLM\s+([0-9A-Fa-f]+)\s+\(([0-9A-Fa-f]{2})\)',line)
   if m:found[int(m[1],16)]=int(m[2],16)
  assert found==cache

events=json.loads((out/'watch_events.json').read_text());assert len(events)==s['watch_events']==0
changed=collections.Counter()
for event in events:
 for change in event['changes']:
  a=change['linear'];assert a in physical and cache[a]==change['old'] and change['old']!=change['new'];cache[a]=change['new'];changed[a-load*16]+=1
assert cache=={a:final[a] for a in physical} and set(changed)<=set(range(0x1c070,0x1c080))
stops=json.loads((out/'input_stops.json').read_text());assert json.loads((out/'snapshots.json').read_text())[1:]==stops
assert len(stops)==53 and stops[-1]['stage']=='pre_music_select_call'
assert any(x['stage']=='map_load_return' for x in stops)
for stage,value in [('main_menu_return',1),('episode_menu_return',15),('episode_select_return',1),('difficulty_menu_return',19)]:
 hits=[r for r in stops if r['stage']==stage];assert len(hits)==1 and hits[0]['registers']['AX']==value
game=next(r for r in stops if r['stage']=='game_start_entry');assert struct.unpack('<HHHH',(work/(game['prefix']+'game_call_frame.bin')).read_bytes())==(0x281a,load+0xd29,0,1)
assert (work/(game['prefix']+'difficulty.bin')).read_bytes()==b'\1\0'
dg=(work/'dgroup_final.bin').read_bytes();assert len(dg)==57392
assert struct.unpack_from('<HH',dg,0x626a)==(1,0) and struct.unpack_from('<H',dg,0x4180)[0]==1
assert dg[0x1c9c]==0 and dg[0x3cd1]==0 and struct.unpack_from('<H',dg,0x3cd4)[0]==1
assert struct.unpack_from('<HHH',dg,0x3506)==(1,2048,1074) and struct.unpack_from('<HH',dg,0xe026)==(4,66)
sound=Path(next(x['source'] for x in inputs if Path(x['source']).name.upper()=='SND.DAT')).read_bytes();original=sound[192:666];actual=(work/'sound_directory_runtime.bin').read_bytes();assert actual==dg[0x3f64:0x413e] and len(actual)==474
expected_sound=bytearray(original);used=742;allocations=0;skipped_oversize=0
for index in range(79):
 length,offset=struct.unpack_from('<HI',expected_sound,index*6)
 if not length or any(struct.unpack_from('<HI',expected_sound,k*6)==(length,offset) for k in range(index)):continue
 if length>8192:skipped_oversize+=1;continue
 start=used*1024;used+=(length+1023)//1024;allocations+=1
 for k in range(index+1,79):
  if struct.unpack_from('<I',expected_sound,k*6+2)[0]==offset:struct.pack_into('<I',expected_sound,k*6+2,(-start)&0xffffffff)
 struct.pack_into('<I',expected_sound,index*6+2,(-start)&0xffffffff)
assert expected_sound==actual and (used,allocations,skipped_oversize)==(1074,66,4)
assert sum(a!=b for a,b in zip(original,actual))==272
gap=(work/'noncode_gap_final.bin').read_bytes();tail=(work/'noncode_tail_final.bin').read_bytes();dg=(work/'dgroup_final.bin').read_bytes();assert (len(gap),len(tail),len(dg))==(17,57278,57392)
assert dg[0x2560:0x2562]==struct.pack('<H',load+0x1be7)
map_source=Path(next(x['source'] for x in inputs if Path(x['source']).name.upper()=='MAP.1')).read_bytes();map_raw=tail[0x2570e-0x1bda2:0x2770e-0x1bda2];map_delta=sum(a!=b for a,b in zip(map_raw,map_source[514:514+8192]));assert len(map_raw)==8192
assert len(s['capture_files'])==801
assert commands.count('EXEC RUN')==492
endpoint={0x11ee7+i:v for i,v in enumerate(gap)};endpoint.update({0x1bda2+i:v for i,v in enumerate(tail)});assert len(endpoint)==57295
for a in unknown:assert endpoint[a]==final[load*16+a]
delta=[a for a,v in endpoint.items() if v!=expected[a]]
for region in s['regions']:
 a,n=region['image_start'],region['length']
 for phase,values in [('initial',initial),('final',final)]:assert (work/(phase+'_%05x.bin'%a)).read_bytes()==bytes(values[load*16+a+j] for j in range(n))
assert len(s['capture_files'])==len(set(s['capture_files']))

writer_events=json.loads((out/'writer_events.json').read_text());assert len(writer_events)==s['writer_events']==98 and s['candidate_stops']==340
wanted={0x2716f,0x27171,0x271a5,0x2723b};assert set(s['found_targets'])==wanted=={x['image_offset'] for x in writer_events}
counts=collections.Counter();pairs=set();caller_returns=set()
for x in writer_events:
 p=x['prefix'];pre=x['pre_registers'];post=x['post_registers'];extra=x['extra_registers'];off=x['image_offset'];meta=x['metadata'];ip=pre['IP'];assert pre['CS']==load+0x4c7 and ip in (0x44c,0x6a9) and meta==dict(canonical_cs=0x4c7,ip=ip,base='BX',value='AL',length=4)
 assert b[0x4c70+ip:0x4c70+ip+4]==bytes.fromhex('26884701') and post['CS']==pre['CS'] and post['IP']==ip+4
 for k in ('DS','ES','SS','SP','AX','BX','CX','DX'):assert pre[k]==post[k]
 assert pre['DS']==pre['SS']==load+0x2771 and pre['ES']==load+0x21fd
 assert x['linear']==pre['ES']*16+pre['BX']+1==load*16+off
 before=(work/(p+'map_before.bin')).read_bytes();after=(work/(p+'map_after.bin')).read_bytes();assert len(before)==len(after)==8192
 changes=[n for n,(a,z) in enumerate(zip(before,after)) if a!=z];assert changes==[off-0x2570e] and before[changes[0]]==x['old'] and after[changes[0]]==x['new']==pre['AX']&255
 frame=(work/(p+'frame_before.bin')).read_bytes();assert frame==(work/(p+'frame_after.bin')).read_bytes() and len(frame)==64
 block=(work/(p+'actor_block_before.bin')).read_bytes();assert block==(work/(p+'actor_block_after.bin')).read_bytes() and len(block)==0x373e
 oldbp,retip,retcs,g,gseg,actor,aseg=struct.unpack_from('<7H',frame,32);assert (g,gseg,actor,aseg)==(extra['SI'],load+0x21fd,extra['DI'],load+0x21fd)
 assert (g-9806)%26==0 and 0<=(g-9806)//26<100 and (actor-6)%28==0 and 0<=(actor-6)//28<350
 guard=block[g:g+26];record=block[actor:actor+28];assert len(guard)==26 and len(record)==28 and guard[0xb]==8
 assert struct.unpack_from('<H',guard,8)[0]==(actor-6)//28
 cell,cellseg=struct.unpack_from('<HH',record,0xc);assert (cell,cellseg)==(pre['BX'],pre['ES'])
 if ip==0x44c:assert x['new']==guard[0xd]
 else:
  assert x['new']==record[0] and guard[0xd]==x['old'];px,py=struct.unpack_from('<HH',record,0x10);signedx=(px&0xffdf);signedx=signedx if signedx<32768 else signedx-65536;computed=(0x373e+((py&0xffc0)*2)+(signedx>>5))&65535;assert cell==computed
 counts[hex(ip)]+=1;pairs.add(((g-9806)//26,(actor-6)//28,record[0]));caller_returns.add((retcs-load,retip))
assert counts=={'0x44c':49,'0x6a9':49} and pairs=={(24,168,0xa5),(25,174,0xa4)} and caller_returns=={(0x4c7,0xfba)}
files=[Path(p) for p in s['capture_files']]+list(out.glob('*.json'))+[out/'inputs.csv',out/'runtime.conf',support,harness,Path(__file__),image,relocs,mapping]
files=[p for p in files if p.name!='independent_verification.json']
result=dict(runtime_image_sha256=sha((work/'unpacked_runtime.bin').read_bytes()),verified=True,summary_sha256=sha((out/'summary.json').read_bytes()),runtime_tests=1,new_deep_verified_bytes=0,exact_native_BYTE_writes=98,candidate_code_stops=340,target_addresses=sorted(wanted),writer_counts=dict(counts),guard_actor_token_pairs=[list(x) for x in sorted(pairs)],caller_return=[0x4c7,0xfba],single_byte_map_delta_verified_events=98,unchanged_actor_block_per_MOV=True,unchanged_stack_frame_per_MOV=True,map_endpoint_difference_bytes=map_delta,unknown_watch_bytes=28,value_change_events=0,all_noncode_endpoint_bytes=57295,endpoint_different_from_relocated_initial=len(delta),scope='original packedDOS2 plus explicitCDasset; exact code-breakpoint before/after98MOVbyte ES:[BX+1],AL writes on four map targets, one-byte8192map delta each;49underlay restores044C and49token writes06A9, guard24/actor168/A5 andguard25/actor174/A4 from matched26/28record/frame evidence; final endpoint06AD is mid-function, not whole GUARD update return; eleven selected direct writer candidates are not an exhaustive alias/index/string/DMA write proof; unknown28 cached-change only',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in files])
(out/'independent_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
