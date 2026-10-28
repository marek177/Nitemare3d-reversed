from pathlib import Path
import csv,collections,json
root=Path(__file__).resolve().parent.parent
by={}
for v in ['10','11','12','15','17','18']:
 p=root/'audit'/('DOS'+v)/'functions.tsv';rows=list(csv.DictReader(p.open(),delimiter='\t'));idx=collections.defaultdict(list)
 for r in rows:
  if int(r['instructions'])>=6:idx[r['sha256']].append(r)
 by[v]=idx
out=[]
for sha,ref in by['18'].items():
 if len(ref)!=1:continue
 for v in ['10','11','12','15','17']:
  if len(by[v].get(sha,[]))==1:
   a=by[v][sha][0];out.append(dict(reference_build='V1.9',reference_entry=ref[0]['entry'],other_build=v,other_entry=a['entry'],instructions=a['instructions'],sha256=sha,status='identical_decoded_instruction_bytes_not_semantic_proof'))
with (root/'evidence/crossversion_exact_matches.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=out[0].keys(),delimiter='\t');w.writeheader();w.writerows(out)
print(dict(collections.Counter(r['other_build'] for r in out)))
