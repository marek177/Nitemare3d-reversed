"""python promote_pass1_fields.py IMAGE PRIOR_MAP DATA_FIELDS OUT"""
import csv,hashlib,json,collections,sys
from pathlib import Path
image,prior,fieldpath,out=map(Path,sys.argv[1:]);b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
fields=list(csv.DictReader(fieldpath.open(encoding='utf-8-sig')));covered=set()
for f in fields:
    a,e=int(f['start']),int(f['end_exclusive']);assert e-a==int(f['length']) and sha(b[a:e])==f['range_sha256'];covered.update(range(a,e))
rows=[];membership=set();changes=collections.Counter()
for r in csv.DictReader(prior.open(encoding='utf-8-sig')):
    a,e=int(r['start']),int(r['end_exclusive']);assert sha(b[a:e])==r['range_sha256'];membership.update(range(a,e))
    cuts=sorted({a,e}|{p for f in fields for p in [int(f['start']),int(f['end_exclusive'])] if a<p<e})
    for x,y in zip(cuts,cuts[1:]):
        n=dict(r);n.update(start=x,end_exclusive=y,length=y-x,range_sha256=sha(b[x:y]),new_fields_source='')
        if x in covered:
            assert set(range(x,y))<=covered
            if r['status']!='PARTIAL':changes[r['status']]+=y-x
            n.update(status='PARTIAL',new_fields_source=str(fieldpath))
        rows.append(n)
assert covered<=membership and len(membership)==57295
out.mkdir(parents=True,exist_ok=True)
with (out/'noncode_intervals.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'noncode_intervals.json').write_text(json.dumps(rows,indent=2)+'\n')
c=collections.Counter()
for r in rows:c[r['status']]+=int(r['length'])
assert sum(c.values())==57295
s=dict(prior_sha256=sha(prior.read_bytes()),fields_sha256=sha(fieldpath.read_bytes()),promoted_from=dict(changes),status_bytes=dict(c),new_deep_verified_bytes=0)
(out/'promotion_summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
