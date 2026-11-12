"""python verify_scheduler_capture.py IMAGE RELOCS CURRENT_MAP OUT WORK
Verify map initialization return and scheduler return endpoint after map initialization, not a rendered gameplay frame.
"""
import collections,csv,hashlib,json,re,struct,sys
from pathlib import Path
image,relocs,mapping,out,work=map(lambda x:Path(x).resolve(),sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest();s=json.loads((out/'summary.json').read_text());b=image.read_bytes()
assert s['success'] and s['newgame_map_runtime'] and s['runtime_tests']==1 and s['source_files_unchanged']
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
assert s['game_source_sha256']=='552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301' and s['exe_sha256']=='a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832'
inputs=list(csv.DictReader((out/'inputs.csv').open()));assert len(inputs)==23
for r in inputs:assert sha(Path(r['source']).read_bytes())==sha(Path(r['copy']).read_bytes())==r['sha256']
support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');harness=Path(__file__).with_name('runtime_watch_scheduler.py');assert sha(support.read_bytes())==s['support_sha256'] and sha(harness.read_bytes())==s['harness_sha256']
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
terminal=stops[-1]['registers'];assert stops[-1]['stage']=='scheduler_return' and (terminal['CS'],terminal['IP'])==(load+0xd29,0x16ea)
assert (terminal['DS'],terminal['SS'])==(load+0x2771,load+0x2771)
assert len(stops)==68
mapstop=next(x for x in stops if x['stage']=='map_load_return');assert (mapstop['registers']['CS'],mapstop['registers']['IP'])==(load+0xd29,0x9c4)
assert any(x['stage']=='pre_music_select_call' for x in stops) and any(x['stage']=='game_start_return' for x in stops)
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
map_source=Path(next(x['source'] for x in inputs if Path(x['source']).name.upper()=='MAP.1')).read_bytes();map_raw=tail[0x2570e-0x1bda2:0x2770e-0x1bda2];assert map_raw==map_source[514:514+8192]
assert len(s['capture_files'])==342
assert commands.count('EXEC RUN')==69
endpoint={0x11ee7+i:v for i,v in enumerate(gap)};endpoint.update({0x1bda2+i:v for i,v in enumerate(tail)});assert len(endpoint)==57295
for a in unknown:assert endpoint[a]==final[load*16+a]
delta=[a for a,v in endpoint.items() if v!=expected[a]]
for region in s['regions']:
 a,n=region['image_start'],region['length']
 for phase,values in [('initial',initial),('final',final)]:assert (work/(phase+'_%05x.bin'%a)).read_bytes()==bytes(values[load*16+a+j] for j in range(n))
assert len(s['capture_files'])==len(set(s['capture_files']))

seq=[x for x in stops if x['stage'].startswith('scheduler_')]
expected_stages=['entry','cached_t0','raw_r0','bucket8','after_tick8','bucket_config','world_begin','world_end','cached_t1','flip_sync','flip_return','deadlines_written','before_retf','return'];assert [x['stage'] for x in seq]==['scheduler_'+x for x in expected_stages]
ips=[0x3c8,0x3d0,0x3da,0x3eb,0x410,0x425,0x454,0x470,0x474,0x483,0x48f,0x4a6,0x4d5]
for x,ip in zip(seq,ips):assert (x['registers']['CS'],x['registers']['IP'])==(load+0xbde,ip)
for x in seq:assert x['registers']['DS']==x['registers']['SS']==load+0x2771
states={}
for x in seq:
 pref=x['prefix'];states[x['stage']]=dict(deadlines=struct.unpack('<III',(work/(pref+'scheduler_deadlines.bin')).read_bytes()),buckets=struct.unpack('<II',(work/(pref+'scheduler_buckets.bin')).read_bytes()),mode=(work/(pref+'scheduler_mode.bin')).read_bytes(),world=int.from_bytes((work/(pref+'world_counter.bin')).read_bytes(),'little'),pages=struct.unpack('<HH',(work/(pref+'vga_page_words.bin')).read_bytes()),stack=(work/(pref+'scheduler_stack.bin')).read_bytes(),registers=x['registers'])
def state(name):return states['scheduler_'+name]
def dword(name):q=state(name)['registers'];return q['AX']|(q['DX']<<16)
t0,r0,c8,cf,t1=[dword(n) for n in ('cached_t0','raw_r0','bucket8','bucket_config','cached_t1')];elapsed=(t1-t0)&0xffffffff
assert state('entry')['deadlines']==(0,0,0) and c8==cf==1 and elapsed<65
assert state('bucket_config')['deadlines'][1]==c8+1 and state('world_begin')['buckets']==(c8,cf)
assert struct.unpack_from('<H',state('world_begin')['mode'],5)[0]==0 and state('world_begin')['world']==1 and state('world_end')['world']==2
assert state('flip_sync')['registers']['AX']==elapsed and state('flip_sync')['registers']['DX']==0
assert state('world_begin')['pages']==(0xa400,0xa000) and state('flip_return')['pages']==(0xa000,0xa400)
assert state('deadlines_written')['deadlines']==state('return')['deadlines']==(r0,c8+1,cf+1)
assert state('entry')['stack']==state('before_retf')['stack']==struct.pack('<HH',0x16ea,load+0xd29)
assert state('entry')['registers']['SP']==state('before_retf')['registers']['SP'] and state('return')['registers']['SP']==state('entry')['registers']['SP']+4
assert state('return')['pages']==struct.unpack('<HH',(work/'vga_page_words.bin').read_bytes())
assert (r0-state('deadlines_written')['deadlines'][0])&0xffffffff==0
assert struct.unpack_from('<III',dg,0x1734)==(r0,c8+1,cf+1) and struct.unpack_from('<II',dg,0x3672)==(c8,cf) and struct.unpack_from('<I',dg,0x4540)[0]==2
before=json.loads((out/'vga_state.json').read_text());after=json.loads((out/'vga_state_restored.json').read_text())
for name in ('GC','SEQ','MODE','AC'):assert before[name][1:-1]==after[name][1:-1]
assert 'disp-start=0h real-start=0h' in '\n'.join(before['MODE']) and 'pel-pan=0' in '\n'.join(before['MODE'])
dac=json.loads((out/'menu_dac_readback.json').read_text());palette=bytearray()
for line in dac['DACPAL']:
 m=re.match(r'^([0-9A-Fa-f]{2}):\s+(.+)$',line)
 if m:assert int(m[1],16)*3==len(palette);palette.extend(bytes.fromhex(''.join(re.findall(r'[0-9A-Fa-f]{6}',m[2]))))
assert len(palette)==768 and max(palette)<=63
ram_palette=(work/'palette_buffer_runtime.bin').read_bytes();palette_differences=[n for n,(a,b) in enumerate(zip(palette,ram_palette)) if a!=b];assert palette_differences==[681,682,683,705,706,707] and palette[681:684]==palette[705:708]==bytes(3)
pages={}
for page in (0xa000,0xa400):
 planes=[(work/('menu_page_%04x_plane_%d.bin'%(page,n))).read_bytes() for n in range(4)];assert all(len(p)==16000 for p in planes);pixels=bytes(planes[n%4][n//4] for n in range(64000));pages[str(page)]=dict(pixel_sha256=sha(pixels),plane_sha256=[sha(p) for p in planes],used_colours=len(set(pixels)))
files=[Path(p) for p in s['capture_files']]+list(out.glob('*.json'))+[out/'inputs.csv',out/'runtime.conf',support,harness,Path(__file__),image,relocs,mapping]
files=[p for p in files if p.name!='independent_verification.json']
result=dict(runtime_image_sha256=sha((work/'unpacked_runtime.bin').read_bytes()),verified=True,summary_sha256=sha((out/'summary.json').read_bytes()),runtime_tests=1,new_deep_verified_bytes=0,scheduler_first_return_verified=True,scheduler_canonical_entry=[0xbde,0x3c8],scheduler_caller_return=[0xd29,0x16ea],cached_t0=t0,raw_r0=r0,bucket8=c8,bucket_config=cf,cached_t1=t1,elapsed=elapsed,flip='synchronized',final_deadlines=[r0,c8+1,cf+1],world_counter_before=1,world_counter_after=2,visible_page=0xa000,latched_display_start=0,pages=pages,dac_ram_component_differences=palette_differences,dac_changed_colour_indices=[227,235],map_payload_bytes_verified=8192,game_episode=1,game_level_index=0,difficulty=1,sound_directory_bytes_reconstructed=474,final_used_kib=1074,unknown_watch_bytes=28,value_change_events=0,all_noncode_endpoint_bytes=57295,endpoint_different_from_relocated_initial=len(delta),scope='original packed DOS2 plus explicit CDasset; first scheduler call from0D29:16E5 after map init returns to16EA; native due buckets, world-call group return, counter1to2, synchronized flip, deadlines and FAR stack checked; paused planes/DAC are derived snapshot, not host scanout or independent pixel golden; breakpoints perturb timing, no long-run cadence, AI/projectile/audio/DEMO/SAVE/Win16 closure; UNKNOWN28 cached-change only',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in files])
(out/'independent_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
