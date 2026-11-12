"""python verify_guard_validator_partial.py IMAGE RELOCS RUNTIME WORK OUT
Retain successful individual calls from an experiment whose both-result gate failed.
This is deliberately not an independent_verification.json runtime-success proof.
"""
import collections,csv,hashlib,json,struct,sys
from pathlib import Path
image,relocs,runtime,work,out=map(Path,sys.argv[1:]);out.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest();s=json.loads((runtime/'summary.json').read_text());b=image.read_bytes();load=s['load_segment']
assert not s['success'] and s['runtime_tests']==0 and s['error']=="AssertionError('both validator results not reached')" and s['source_files_unchanged']
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
inputs=list(csv.DictReader((runtime/'inputs.csv').open()));assert len(inputs)==23
for x in inputs:assert sha(Path(x['source']).read_bytes())==sha(Path(x['copy']).read_bytes())==x['sha256']
support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');harness=Path(__file__).with_name('runtime_watch_guard_validator.py');assert sha(support.read_bytes())==s['support_sha256'] and sha(harness.read_bytes())==s['harness_sha256']
expected=bytearray(b)
for x in csv.DictReader(relocs.open()):struct.pack_into('<H',expected,int(x['image_offset']),(int(x['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==expected
calls=json.loads((runtime/'validator_calls.json').read_text());assert len(calls)==s['validator_calls']==128 and s['validator_AL_results']==[0]
rows=[];ah=collections.Counter();reference_flags=None
def signed(x):return x if x<32768 else x-65536
def absword(x):x=signed(x&65535);return signed((-x if x<0 else x)&65535)
for x in calls:
 p=x['prefix'];pre=x['pre_registers'];post=x['post_registers'];ex=x['pre_extra'];px=x['post_extra'];frame=(work/(p+'call_frame_before.bin')).read_bytes();assert len(frame)==16 and frame==(work/(p+'call_frame_after.bin')).read_bytes();ret,retcs,g,gseg,a,aseg,u,v=struct.unpack('<8H',frame)
 assert (pre['CS'],pre['IP'])==(load+0x4c7,0x254) and (post['CS'],post['IP'])==(retcs,ret) and retcs==load+0x4c7 and ret in (0x4db,0x4fa,0x52e,0x54d)
 assert post['SP']==pre['SP']+4 and pre['DS']==pre['SS']==post['DS']==post['SS']==load+0x2771 and ex==px
 assert (g,gseg,a,aseg,u,v)==(x['guard_offset'],x['guard_segment'],x['actor_offset'],x['actor_segment'],x['x'],x['y'])
 world=(work/(p+'world_before.bin')).read_bytes();flags=(work/(p+'flags_before.bin')).read_bytes();player=(work/(p+'player_before.bin')).read_bytes()
 assert len(world)==0x573e and len(flags)==512 and len(player)==4
 for name,value in [('world',world),('flags',flags),('player',player)]:assert value==(work/(p+name+'_after.bin')).read_bytes()
 assert (work/(p+'map_segment_before.bin')).read_bytes()==struct.pack('<H',load+0x21fd)
 if reference_flags is None:reference_flags=flags
 assert flags==reference_flags
 player0,player1=struct.unpack('<HH',player);near=absword(u-player0)<42 and absword(v-player1)<42;cell=(0x373e+(v&0xffc0)*2+(signed(u&0xffdf)>>5))&65535;assert 0x373e<=cell<0x573e
 t0,t1=world[cell:cell+2];f0,f1=flags[t0],flags[256+t1];assert not near and f0==f1==0 and post['AX']&255==x['result_AL']==0
 ah[post['AX']>>8]+=1;rows.append(dict(call=len(rows),caller_return_ip=ret,guard_offset=g,actor_offset=a,probe0=u,probe1=v,player0=player0,player1=player1,tile_code=t0,occupancy_code=t1,tile_flags=f0,occupancy_flags=f1,returned_AX=post['AX'],returned_AL=0,world_unchanged=True,record_frame_unchanged=True))
with (out/'native_allowed_calls.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
tables=[]
for n,name in enumerate(('collision_tile_flags256','collision_occupancy_flags256')):
 start=0xd00c+256*n;tables.append(dict(name=name,ds_start=start,ds_end_exclusive=start+256,image_start=0x27710+start,image_end_exclusive=0x27710+start+256,length=256,type='BYTE256 classification flags indexed by zero-extended map cell BYTE'+str(n)+'; consumed masks0x02/0x08 for tile or0x02 for occupancy',status='PARTIAL',runtime_sha256=sha(reference_flags[n*256:(n+1)*256]),outside_original_file_image=True,original_NONCODE_bytes_added=0))
with (out/'external_bss_tables.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(tables[0]));w.writeheader();w.writerows(tables)
files=[Path(x) for x in s['capture_files']]+list(runtime.glob('*.json'))+[runtime/'inputs.csv',runtime/'runtime.conf',image,relocs,support,harness,Path(__file__)]
proof=dict(verified_individual_calls=True,successful_native_allowed_calls=128,observed_AL_results=[0],returned_AH_counts=dict(ah),both_result_gate_satisfied=False,overall_experiment_success=False,runtime_tests=0,new_deep_verified_bytes=0,classification_table_bytes=512,table_sample_invariant_calls=128,scope='individual original0254 entry-to-return allowed calls checked with whole world/player/flags unchanged; overall both-AL experiment failed and is not counted as successful runtime scenario; blocked/stateful door paths remain unobserved here',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in files])
(out/'partial_verification.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items() if k!='files'},indent=2))
