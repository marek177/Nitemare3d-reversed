"""Verify sparse native return tails; never imply complete validator entry snapshots.
Usage: python verify_validator_branch_capture.py IMAGE RELOCS RUNTIME WORK
"""
import csv, hashlib, json, struct, sys
from pathlib import Path
image,relocs,runtime,work=map(Path,sys.argv[1:])
sha=lambda b:hashlib.sha256(b).hexdigest()
s=json.loads((runtime/'summary.json').read_text(encoding='utf-8'))
assert s['success'] and s['source_files_unchanged'] and s['runtime_tests']==1
assert s['observed_AL_results']==[0,1] and s['branch_returns']==2
load=s['load_segment'];original=image.read_bytes();expected=bytearray(original)
assert sha(original)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
for r in csv.DictReader(relocs.open()):struct.pack_into('<H',expected,int(r['image_offset']),(int(r['original_word'])+load)&65535)
assert (work/'unpacked_runtime.bin').read_bytes()==expected
inputs=list(csv.DictReader((runtime/'inputs.csv').open()));assert len(inputs)==23
for r in inputs:assert sha(Path(r['source']).read_bytes())==sha(Path(r['copy']).read_bytes())==r['sha256']
support=Path(__file__).with_name('dosbox_watch_support_newgame_v1.py');harness=Path(__file__).with_name('runtime_watch_validator_branches.py')
assert sha(support.read_bytes())==s['support_sha256'] and sha(harness.read_bytes())==s['harness_sha256']
calls=json.loads((runtime/'branch_returns.json').read_text(encoding='utf-8'));rows=[]
signed=lambda v:v if v<32768 else v-65536
def absword(v):
 v=signed(v&65535);return signed(abs(v)&65535)
for c in calls:
 p=c['prefix'];pre=c['pre_registers'];post=c['post_registers'];ex=c['pre_extra'];px=c['post_extra'];al=c['result_AL']
 frame=(work/(p+'frame_before.bin')).read_bytes();assert len(frame)==48 and frame==(work/(p+'frame_after.bin')).read_bytes()
 si,di=struct.unpack_from('<HH',frame);bp=struct.unpack_from('<H',frame,16)[0]
 ret,retcs,g,gs,a,aseg,x,y=struct.unpack_from('<8H',frame,18)
 assert (pre['CS'],pre['IP'])==(load+0x4c7,0x27e if al else 0x41c)
 assert (post['CS'],post['IP'])==(retcs,ret) and post['SP']==ex['BP']+6
 assert (px['SI'],px['DI'],px['BP'])==(si,di,bp)
 assert pre['DS']==pre['SS']==post['DS']==post['SS']==load+0x2771
 assert post['AX']&255==al
 data={}
 for name,n in [('world',0x573e),('flags',512),('player',4)]:
  b=(work/(p+name+'_before.bin')).read_bytes();assert len(b)==n and b==(work/(p+name+'_after.bin')).read_bytes();data[name]=b
 world,flags,player=data['world'],data['flags'],data['player'];seg=struct.unpack('<H',(work/(p+'map_segment_before.bin')).read_bytes())[0]
 assert seg==gs==aseg==load+0x21fd
 u,v=struct.unpack('<HH',player);assert not(absword(x-u)<42 and absword(y-v)<42)
 cell=(0x373e+2*(y&0xffc0)+(signed(x&0xffdf)>>5))&65535;assert 0x373e<=cell<0x573e
 t,o=world[cell:cell+2];f0,f1=flags[t],flags[256+o]
 row=dict(result_AL=al,guard_offset=g,actor_offset=a,x=x,y=y,cell_offset=cell,tile=t,occupancy=o,tile_flags=f0,occupancy_flags=f1,tail_world_frame_flags_player_unchanged=True)
 if al:
  assert (t,o,f0,f1)==(0x71,0,0x0b,0)
  count=struct.unpack_from('<H',world)[0];matches=[q for q in range(count) if struct.unpack_from('<HH',world,0x3076+18*q+4)==(cell,seg)]
  assert matches==[7];door=0x3076+18*7;state=struct.unpack_from('<H',world,door+8)[0];assert state==2
  assert struct.unpack_from('<HH',frame,12)==(door,seg)
  desc=struct.unpack_from('<H',world,door)[0];dgroup=(work/'dgroup_final.bin').read_bytes();assert dgroup[desc+6]==0x40
  row.update(door_index=7,door_offset=door,door_state_at_branch=state,descriptor=desc,descriptor_kind_final=dgroup[desc+6])
 else:assert f0==f1==0
 rows.append(row)
assert sorted(r['result_AL'] for r in rows)==[0,1]
(runtime/'verified_branch_context.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
paths=[Path(p) for p in s['capture_files']]+[runtime/'summary.json',runtime/'branch_returns.json',runtime/'verified_branch_context.json',runtime/'inputs.csv',runtime/'runtime.conf',image,relocs,support,harness,Path(__file__)]
proof=dict(verified=True,runtime_tests=1,new_deep_verified_bytes=0,summary_sha256=sha((runtime/'summary.json').read_bytes()),runtime_image_sha256=sha(expected),native_return_tails=2,observed_AL_results=[0,1],scope='Sparse original0254 allowed/blocked decision-to-return tails and caller frames verified; blocked snapshot contains door7 state2, not a pre/post interaction transition; no complete validator entry-to-return blocked capture; no full gameplay or Win16 parity',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in dict.fromkeys(paths)])
(runtime/'independent_verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in proof.items() if k!='files'},indent=2))
