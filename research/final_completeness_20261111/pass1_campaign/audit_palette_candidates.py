"""python audit_palette_candidates.py PATH_LIST CANONICAL_GAME_PAL OUT
Compare actual bytes; folder labels are not verified executable versions.
"""
import collections,csv,hashlib,json,sys
from pathlib import Path
manifest,canonical,out=map(Path,sys.argv[1:]);sha=lambda b:hashlib.sha256(b).hexdigest();base=canonical.read_bytes();assert sha(base)=='efd52442cbee3327d8cec045b31559049e8767b298c25674a557eb6e096a759f';paths=[Path(p) for p in manifest.read_text().splitlines() if p.strip()];assert len(paths)==len({str(p).lower() for p in paths});out.mkdir(parents=True,exist_ok=True);files=[];intervals=[];blocks=[];errors=[]
for path in paths:
 try:b=path.read_bytes()
 except OSError as e:errors.append(dict(path=str(path),error=repr(e)));continue
 if len(b)<768:errors.append(dict(path=str(path),error='shorter than768; cannot apply DOS loader tail contract'));continue
 n=len(b)-768;prefix=b[:n];tail=b[n:];converted=bytes(v>>2 for v in tail)
 files.append(dict(path=str(path.resolve()),bytes=len(b),sha256=sha(b),prefix_bytes=n,prefix_sha256=sha(prefix),tail_sha256=sha(tail),dos_shift2_sha256=sha(converted),byte_equal_canonical=b==base,prefix_equal_canonical=prefix==base[:-768],tail_equal_canonical=tail==base[-768:],header4_hex=b[:4].hex(),scope='actual file identity; directory label is not executable-version proof; DOS shift2 only'))
 intervals.extend([dict(path=str(path),start=0,end_exclusive=n,length=n,status='UNKNOWN',type='unconsumed_prefix_semantics_open',range_sha256=sha(prefix)),dict(path=str(path),start=n,end_exclusive=len(b),length=768,status='PARTIAL',type='BYTE768_tail_under_verified_DOS_loader_contract',range_sha256=sha(tail))])
 if len(prefix)==1156:
  for i in range(36):
   a=4+32*i;raw=prefix[a:a+32];blocks.append(dict(path=str(path),index=i,start=a,end_exclusive=a+32,all_bytes_equal=len(set(raw))==1,first_byte=raw[0],range_sha256=sha(raw),status='UNKNOWN_semantic_type; repeated32B_chunk_is_content_observation_only'))
def save(name,rows):
 if not rows:return
 with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
save('files',files);save('asset_intervals',intervals);save('prefix_32byte_chunks',blocks);save('errors',errors)
groups=[]
for digest in sorted({f['sha256'] for f in files}):
 members=[f for f in files if f['sha256']==digest];groups.append(dict(sha256=digest,count=len(members),bytes=members[0]['bytes'],prefix_bytes=members[0]['prefix_bytes'],tail_sha256=members[0]['tail_sha256'],paths=[f['path'] for f in members]))
(out/'groups.json').write_text(json.dumps(groups,indent=2)+'\n');(out/'asset_intervals.json').write_text(json.dumps(intervals,indent=2)+'\n')
s=dict(path_manifest_sha256=sha(manifest.read_bytes()),canonical_sha256=sha(base),candidate_paths=len(paths),files_read=len(files),errors=len(errors),unique_file_hashes=len(groups),unique_prefix_hashes=len({f['prefix_sha256'] for f in files}),unique_tail_hashes=len({f['tail_sha256'] for f in files}),canonical_equal_files=sum(f['byte_equal_canonical'] for f in files),prefix32_chunks_observed=len(blocks),constant32_chunks=sum(f['all_bytes_equal'] for f in blocks),status_changes=0,runtime_tests=0,new_deep_verified_bytes=0,scope='explicit local32file manifest, not complete archive inventory; shared asset hashes do not prove Win16 conversion or runtime parity; prefix remains UNKNOWN')
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
