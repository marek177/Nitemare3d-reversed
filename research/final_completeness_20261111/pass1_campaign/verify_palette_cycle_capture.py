"""python verify_palette_cycle_capture.py IMAGE RELOCS CURRENT_MAP OUT WORK
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
support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');harness=Path(__file__).with_name('runtime_watch_palette_cycle_v2.py');assert sha(support.read_bytes())==s['support_sha256'] and sha(harness.read_bytes())==s['harness_sha256']
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
terminal=stops[-1]['registers'];assert stops[-1]['stage']=='palette_followup_return' and (terminal['CS'],terminal['IP'])==(load+0x83d,0x1d94)
assert (terminal['DS'],terminal['SS'])==(load+0x2771,load+0x2771)
assert len(stops)==94
assert any(x['stage']=='map_load_return' for x in stops) and any(x['stage']=='pre_music_select_call' for x in stops)
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
assert len(s['capture_files'])==582
assert commands.count('EXEC RUN')==95
endpoint={0x11ee7+i:v for i,v in enumerate(gap)};endpoint.update({0x1bda2+i:v for i,v in enumerate(tail)});assert len(endpoint)==57295
for a in unknown:assert endpoint[a]==final[load*16+a]
delta=[a for a,v in endpoint.items() if v!=expected[a]]
for region in s['regions']:
 a,n=region['image_start'],region['length']
 for phase,values in [('initial',initial),('final',final)]:assert (work/(phase+'_%05x.bin'%a)).read_bytes()==bytes(values[load*16+a+j] for j in range(n))
assert len(s['capture_files'])==len(set(s['capture_files']))

seq=[x for x in stops if x['stage'].startswith('palette_')];groupnames=['palette_colour_entry','palette_out_index','palette_out_red','palette_out_green','palette_out_blue','palette_colour_written']
assert [x['stage'] for x in seq]==['palette_reset_branch']+groupnames*2+['palette_flash_branch']+groupnames*2+['palette_dark_branch','palette_rng_return']+groupnames*2+['palette_followup_return']
points={'palette_reset_branch':(0x83d,0x1d21),'palette_flash_branch':(0x83d,0x1d96),'palette_dark_branch':(0x83d,0x1d56),'palette_rng_return':(0x83d,0x1d60),'palette_followup_return':(0x83d,0x1d94),'palette_colour_entry':(0x156,0x150),'palette_out_index':(0x156,0x15b),'palette_out_red':(0x156,0x162),'palette_out_green':(0x156,0x166),'palette_out_blue':(0x156,0x16a),'palette_colour_written':(0x156,0x16b)}
def state(x):return struct.unpack('<HB',(work/(x['prefix']+'palette_effect_state.bin')).read_bytes())
def rngstate(x):return int.from_bytes((work/(x['prefix']+'rng_state.bin')).read_bytes(),'little')
def palette(x):
 q=json.loads((out/(x['prefix']+'dac.json')).read_text());p=bytearray()
 for line in q['DACPAL']:
  m=re.match(r'^([0-9A-Fa-f]{2}):\s+(.+)$',line)
  if m:assert int(m[1],16)*3==len(p);p.extend(bytes.fromhex(''.join(re.findall(r'[0-9A-Fa-f]{6}',m[2]))))
 assert len(p)==768 and max(p)<=63;return bytes(p)
for x in seq:
 cs,ip=points[x['stage']];q=x['registers'];assert (q['CS'],q['IP'])==(load+cs,ip) and q['DS']==q['SS']==load+0x2771
 assert (work/(x['prefix']+'palette_scene_index.bin')).read_bytes()==bytes([227])
 assert struct.unpack_from('<HH',(work/(x['prefix']+'palette_context.bin')).read_bytes())==(1,0)
reset,bright,dark,rng,final=[seq[n] for n in (0,13,26,27,40)]
assert state(reset)==(0,0) and state(bright)==(65535,0) and state(dark)==(65535,1)
seed=rngstate(dark);next_seed=(seed*214013+2531011)&0xffffffff;rand=(next_seed>>16)&32767
assert rngstate(rng)==next_seed and rng['registers']['AX']==rand and state(rng)==(65535,0)
new_count=160+rand%240;assert state(final)==(new_count,0)
for start,index,rgb,expected_state,ret in [(1,235,0,(80,0),0x1d3a),(7,227,0,(80,0),0x1dc7),(14,235,255,(3,1),0x1db2),(20,227,255,(3,1),0x1dc7),(28,235,0,(new_count,0),0x1d7c),(34,227,0,(new_count,0),0x1d8d)]:
 group=seq[start:start+6];assert all(state(x)==expected_state for x in group)
 assert struct.unpack('<HHHHHH',(work/(group[0]['prefix']+'palette_stack.bin')).read_bytes())==(ret,load+0x83d,index,rgb,rgb,rgb)
 assert (group[1]['registers']['DX'],group[1]['registers']['AX']&255)==(0x3c8,index)
 for x in group[2:5]:assert (x['registers']['DX'],x['registers']['AX']&255)==(0x3c9,rgb)
 before=palette(group[0]);after=palette(group[5]);expected=bytearray(before);expected[index*3:index*3+3]=bytes([rgb&63])*3;assert after==expected
assert palette(reset)==(work/'palette_buffer_runtime.bin').read_bytes()
assert palette(bright)[681:684]==palette(bright)[705:708]==bytes(3)
assert palette(dark)[681:684]==palette(dark)[705:708]==bytes([63])*3
assert palette(final)[681:684]==palette(final)[705:708]==bytes(3)
assert struct.unpack_from('<HB',dg,0x3634)==(new_count,0)
for ip in (0x15b,0x162,0x166,0x16a):assert b[0x1560+ip]==0xee
files=[Path(p) for p in s['capture_files']]+list(out.glob('*.json'))+[out/'inputs.csv',out/'runtime.conf',support,harness,Path(__file__),image,relocs,mapping]
files=[p for p in files if p.name!='independent_verification.json']
result=dict(runtime_image_sha256=sha((work/'unpacked_runtime.bin').read_bytes()),verified=True,summary_sha256=sha((out/'summary.json').read_bytes()),runtime_tests=1,new_deep_verified_bytes=0,palette_cycle_verified=True,cycle_stages=['reset_black','flash_white','dark_black_followup_return'],palette_indices=[235,227],native_single_colour_calls=6,native_OUT_instructions=24,native_rng_seed_before=seed,native_rng_seed_after=next_seed,native_rng_AX=rand,next_dark_countdown=new_count,followup_return=[0x83d,0x1d94],map_endpoint_difference_bytes=map_delta,unknown_watch_bytes=28,value_change_events=0,all_noncode_endpoint_bytes=57295,endpoint_different_from_relocated_initial=len(delta),scope='original packedDOS2 plus explicitCDasset, natural reset and first white-to-dark cycle through original single-colour OUT helpers, actual6bit DAC black/white/black, original RNG state/return transition and nativeEA0 follow-up return; no per-tick call count/time/audio-output/wholeAI/Win16 closure; unknown28 cached-change only',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in files])
(out/'independent_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
