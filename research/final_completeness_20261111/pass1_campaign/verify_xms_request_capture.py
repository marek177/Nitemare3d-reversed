"""python verify_xms_request_capture.py IMAGE RELOCS HISTORICAL_MAP OUT WORK
Verify a completed native XMS-call-return capture, not full map initialization.
"""
import collections,csv,hashlib,json,re,struct,sys
from pathlib import Path
image,relocs,mapping,out,work=map(lambda x:Path(x).resolve(),sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest();s=json.loads((out/'summary.json').read_text());b=image.read_bytes()
assert s['success'] and s['xms_request_runtime'] and s['runtime_tests']==1 and s['source_files_unchanged']
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
assert s['game_source_sha256']=='552d250ef773014a7f56ecdd7939559005fa990ebc7a6e435e6a7a49d372f301' and s['exe_sha256']=='a82adcfa7af2784566cfeff74c077cefed08505396db2948b7e6aa7d4cee0832'
inputs=list(csv.DictReader((out/'inputs.csv').open()));assert len(inputs)==23
for r in inputs:assert sha(Path(r['source']).read_bytes())==sha(Path(r['copy']).read_bytes())==r['sha256']
support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');harness=Path(__file__).with_name('runtime_watch_xms_request.py');assert sha(support.read_bytes())==s['support_sha256'] and sha(harness.read_bytes())==s['harness_sha256']
load=s['load_segment'];expected=bytearray(b)
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',expected,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==expected
assert sha(mapping.read_bytes())=='3021969d4e4348715816361fa387631e7d6cfd9fc9dcc136e26073f0f9984d1b'
unknown=set()
for r in csv.DictReader(mapping.open(encoding='utf-8-sig')):
 if r['status']=='UNKNOWN':unknown.update(range(int(r['start']),int(r['end_exclusive'])))
physical={load*16+a for a in unknown};assert len(physical)==44
initial={int(k):v for k,v in s['initial'].items()};final={int(k):v for k,v in s['final'].items()};cache={int(k):v for k,v in s['cache_initial'].items()}
assert set(cache)==physical==set(s['calibrated_addresses']) and all(cache[a]==initial[a]==0 for a in physical)
t=json.loads((out/'transcript.json').read_text());commands=[r['command'] for r in t]
ports=['EXEC OUTP 03CE 0004']+['EXEC OUTP 03CF %04X'%n for n in range(4)]+['EXEC OUTP 03CF 0000','EXEC OUTP 03CE 0006'];queries=['EXEC VGA '+n for n in ('GC','SEQ','MODE','AC','DAC','DACPAL')]
allowed=('EXEC EV ','EXEC BP ','EXEC BPLM ','EXEC BPLIST','EXEC BPDEL ','EXEC RUN','EXEC MEMDUMPBIN ')
assert all(c=='PING' or c.startswith(allowed) or c in ports+queries for c in commands)
assert [c for c in commands if c.startswith('EXEC OUTP ')]==ports and commands[-1]=='EXEC BPDEL *' and commands.count('EXEC BPDEL *')==2
assert not any(c=='EXEC RUN' for c in commands[commands.index(ports[0]):])
assert {int(c.split()[-1],16) for c in commands if c.startswith('EXEC BPLM ')}==physical
events=json.loads((out/'watch_events.json').read_text());assert len(events)==s['watch_events']==6
changed=collections.Counter()
for event in events:
 for change in event['changes']:
  a=change['linear'];assert a in physical and cache[a]==change['old'] and change['old']!=change['new'];cache[a]=change['new'];changed[a-load*16]+=1
assert cache=={a:final[a] for a in physical} and set(changed)<=set(range(0x1c070,0x1c080))
stops=json.loads((out/'input_stops.json').read_text());assert json.loads((out/'snapshots.json').read_text())[1:]==stops
terminal=stops[-1]['registers'];assert stops[-1]['stage']=='xms_transfer_return' and (terminal['CS'],terminal['IP'])==(load+0x768,0x32f)
assert (terminal['AX'],terminal['DX'],terminal['DS'],terminal['ES'],terminal['SS'])==(1,0,load+0x2771,load+0x2771,load+0x2771)
for stage,value in [('main_menu_return',1),('episode_menu_return',15),('episode_select_return',1),('difficulty_menu_return',19)]:
 hits=[r for r in stops if r['stage']==stage];assert len(hits)==1 and hits[0]['registers']['AX']==value
game=next(r for r in stops if r['stage']=='game_start_entry');assert struct.unpack('<HHHH',(work/(game['prefix']+'game_call_frame.bin')).read_bytes())==(0x281a,load+0xd29,0,1)
assert (work/(game['prefix']+'difficulty.bin')).read_bytes()==b'\1\0'
raw=(work/'xms_request_runtime.bin').read_bytes();assert len(raw)==16
length,source_handle,source,dest_handle,dest_offset=struct.unpack('<IHIHI',raw);assert (length,source_handle,dest_handle,dest_offset)==(8192,0,1,0) and source==0x8d9b65ca
assert (work/'xms_segment_pointer_runtime.bin').read_bytes()==struct.pack('<H',load+0x1be7)
frame=(work/'xms_call_frame_runtime.bin').read_bytes();assert struct.unpack_from('<HH',frame)==(0x200,load+0x1be7)
control=(work/'xms_driver_state_runtime.bin').read_bytes();assert struct.unpack_from('<HHH',control)==(1,0x800,0)
assert raw==bytes(final[load*16+0x1c070+n] for n in range(16))
gap=(work/'noncode_gap_final.bin').read_bytes();tail=(work/'noncode_tail_final.bin').read_bytes();dg=(work/'dgroup_final.bin').read_bytes();assert (len(gap),len(tail),len(dg))==(17,57278,57392)
assert tail[0x1c070-0x1bda2:0x1c080-0x1bda2]==raw and dg[0x2560:0x2562]==struct.pack('<H',load+0x1be7) and dg[0x3506:0x3512]==control
endpoint={0x11ee7+i:v for i,v in enumerate(gap)};endpoint.update({0x1bda2+i:v for i,v in enumerate(tail)});assert len(endpoint)==57295
for a in unknown:assert endpoint[a]==final[load*16+a]
delta=[a for a,v in endpoint.items() if v!=expected[a]]
for region in s['regions']:
 a,n=region['image_start'],region['length']
 for phase,values in [('initial',initial),('final',final)]:assert (work/(phase+'_%05x.bin'%a)).read_bytes()==bytes(values[load*16+a+j] for j in range(n))
assert len(s['capture_files'])==len(set(s['capture_files']))
files=[Path(p) for p in s['capture_files']]+list(out.glob('*.json'))+[out/'inputs.csv',out/'runtime.conf',support,harness,Path(__file__),image,relocs,mapping]
files=[p for p in files if p.name!='independent_verification.json']
result=dict(runtime_image_sha256=sha((work/'unpacked_runtime.bin').read_bytes()),verified=True,summary_sha256=sha((out/'summary.json').read_bytes()),runtime_tests=1,new_deep_verified_bytes=0,xms_move_request_bytes=16,xms_fields=dict(length=length,source_handle=source_handle,source_far=source,destination_handle=dest_handle,destination_offset=dest_offset),native_return=dict(AX=1,DX=0),historical_unknown_watch_bytes=44,value_change_events=6,changed_addresses={hex(a):n for a,n in sorted(changed.items())},all_noncode_endpoint_bytes=57295,endpoint_different_from_relocated_initial=len(delta),game_episode=1,game_level_index=0,difficulty=1,scope='original packed DOS2 with explicit CD asset; menu input reaches first XMS move return before map-load completion; cached byte-change events do not identify writer PCs or reads; final snapshot covers all baseline NONCODE bytes but does not prove all their uses; no full gameplay, error path, Win16 or physical hardware parity',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in files])
(out/'independent_verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='files'},indent=2))
