"""IMAGE MAP OUTPUTS OUT: hash-checked endpoint evidence for every PASS320 interval.
Reuses retained sessions; no new native tests/status promotions. capture_inputs freezes selection.
"""
import csv,hashlib,json,re,struct,sys
from pathlib import Path
image,mapping,root,out=map(Path,sys.argv[1:]);out.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest();b=image.read_bytes();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
assert sha(mapping.read_bytes())=='497d10a11959dbae3d17f495e803569e229c13434658ec94c231d29784f47efe';rows=list(csv.DictReader(mapping.open(encoding='utf-8')));assert len(rows)==892 and sum(int(r['length']) for r in rows)==57295
rel=list(csv.DictReader((image.parent/'relocations.csv').open()));snapshot=out/'capture_inputs.json'
if snapshot.exists():inputs=json.loads(snapshot.read_text(encoding='utf-8'))
else:
 inputs=[]
 for proofpath in sorted(root.glob('dosbox*/independent_verification.json')):
  proof=json.loads(proofpath.read_text(encoding='utf-8'));summarypath=proofpath.parent/'summary.json'
  if not proof.get('verified') or proof.get('runtime_tests')!=1 or not summarypath.exists():continue
  s=json.loads(summarypath.read_text(encoding='utf-8'));load=s.get('load_segment')
  if load is None or not s.get('success'):continue
  for f in proof['files']:
   p=Path(f['path']);raw=p.read_bytes();assert sha(raw)==f['sha256'],str(p)
   name=p.name.lower();start=None
   if 'dgroup' in name and len(raw)==0xe030:start=0x27710
   elif 'noncode' in name and 'tail' in name and len(raw)==57278:start=0x1bda2
   elif 'noncode' in name and 'gap' in name and len(raw)==17:start=0x11ee7
   if start is not None:
    inputs.append(dict(path=str(p.resolve()),sha256=sha(raw),start=start,end_exclusive=start+len(raw),load_segment=load,proof=str(proofpath.resolve()),proof_sha256=sha(proofpath.read_bytes()),summary=str(summarypath.resolve()),summary_sha256=sha(summarypath.read_bytes()),mapping_rule='retained named dgroup57392/noncode_tail57278/noncode_gap17 capture convention; pinned harness/verifier scope retained'))
 snapshot.write_text(json.dumps(inputs,indent=2)+'\n',encoding='utf-8')
captures=[];seen=set();address_proofs=[];transcript_files=set()
for item in inputs:
 for pathkey,hashkey in [('path','sha256'),('proof','proof_sha256'),('summary','summary_sha256')]:assert sha(Path(item[pathkey]).read_bytes())==item[hashkey]
 assert item['path'] not in seen;seen.add(item['path']);captures.append((item,Path(item['path']).read_bytes()))
 # Independently confirm origin/extent from actual debugger commands, not filenames alone.
 transcript=Path(item['proof']).parent/'transcript.json';proof=json.loads(Path(item['proof']).read_text(encoding='utf-8'))
 pinned={str(Path(f['path']).resolve()):f['sha256'] for f in proof['files']}
 prior_pinned=str(transcript.resolve()) in pinned
 if prior_pinned:assert pinned[str(transcript.resolve())]==sha(transcript.read_bytes())
 transcript_files.add(transcript.resolve())
 commands=[];p=Path(item['path'])
 for event in json.loads(transcript.read_text(encoding='utf-8')):
  m=re.fullmatch(r'EXEC MEMDUMPBIN ([0-9A-Fa-f]+):([0-9A-Fa-f]+) ([0-9A-Fa-f]+) (.+)',event['command'])
  if m and Path(m[4]).name.lower().startswith(p.name.lower()+'.part'):
   commands.append((int(m[1],16)*16+int(m[2],16),int(m[3],16),Path(m[4])))
 assert commands;position=item['load_segment']*16+item['start'];joined=bytearray()
 for address,n,part in commands:
  raw=part.read_bytes();assert address==position and len(raw)==n;joined.extend(raw);position+=n
 assert bytes(joined)==p.read_bytes() and position==item['load_segment']*16+item['end_exclusive']
 address_proofs.append(dict(path=item['path'],commands=len(commands),linear_start=item['load_segment']*16+item['start'],linear_end_exclusive=position,transcript=str(transcript.resolve()),transcript_sha256=sha(transcript.read_bytes()),transcript_pinned_by_prior_proof=prior_pinned,raw_reassembly_exact=True))
(out/'capture_address_verification.json').write_text(json.dumps(address_proofs,indent=2)+'\n',encoding='utf-8')
expected={}
for load in set(i['load_segment'] for i,_ in captures):
 raw=bytearray(b)
 for r in rel:struct.pack_into('<H',raw,int(r['image_offset']),(int(r['original_word'])+load)&65535)
 expected[load]=bytes(raw)
profiles=[];comparison_rows=[];covered=set();changed_union=set();remaining_changed=set()
for index,r in enumerate(rows):
 a,z=int(r['start']),int(r['end_exclusive']);assert sha(b[a:z])==r['range_sha256'];samples=[];changes=set();hashes=set()
 for capture_id,(item,raw) in enumerate(captures):
  if not item['start']<=a<z<=item['end_exclusive']:continue
  observed=raw[a-item['start']:z-item['start']];initial=expected[item['load_segment']][a:z];delta={a+j for j,(x,y) in enumerate(zip(initial,observed)) if x!=y};changes.update(delta);hashes.add(sha(observed));samples.append(capture_id)
  comparison_rows.append(dict(interval_id=index,capture_id=capture_id,changed_bytes=len(delta),observed_sha256=sha(observed)))
 if samples:covered.update(range(a,z))
 changed_union.update(changes)
 if r['status'] in ('UNKNOWN','CLASSIFIED ONLY'):remaining_changed.update(changes)
 profiles.append(dict(interval_id=index,start=a,end_exclusive=z,length=z-a,status=r['status'],original_sha256=r['range_sha256'],full_interval_samples=len(samples),distinct_observed_hashes=len(hashes),union_changed_byte_positions=len(changes),changed_positions_hex=' '.join('%05X'%p for p in sorted(changes)),capture_ids=','.join(map(str,samples)),classification_change=False,evidence_scope='Endpoint comparison only; no read/same-value-write/transient-write tracking or global nonuse proof'))
for name,rs in [('interval_runtime_profile',profiles),('interval_capture_comparisons',comparison_rows)]:
 with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
(out/'interval_runtime_profile.json').write_text(json.dumps(profiles,indent=2)+'\n',encoding='utf-8')
summary=dict(intervals=len(profiles),baseline_bytes=57295,captures=len(captures),sessions=len(set(i['proof'] for i,_ in captures)),capture_origins_independently_reassembled_from_debugger_commands=len(address_proofs),interval_capture_comparisons=len(comparison_rows),intervals_with_full_sample=sum(bool(p['full_interval_samples']) for p in profiles),baseline_byte_union_with_full_interval_samples=len(covered),baseline_changed_byte_position_union=len(changed_union),remaining_177_changed_byte_position_union=len(remaining_changed),remaining_changed_hex=['%05X'%p for p in sorted(remaining_changed)],new_runtime_tests=0,status_changes=0,new_deep_verified_bytes=0,scope='Frozen selection of previously verified native endpoints; observed byte changes are relative to exact per-session relocated initial image. Actual pinned debugger commands and part reassembly verify address origins. Not read tracking,temporal completeness,semantic closure or new scenarios.',files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in [image,mapping,image.parent/'relocations.csv',snapshot,Path(__file__)]+sorted(transcript_files)])
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k!='files'},indent=2))
