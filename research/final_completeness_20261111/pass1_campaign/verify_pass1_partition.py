"""Independent membership/hash/overlap audit of any PASS1 interval map.
Usage: python verify_pass1_partition.py IMAGE MAP_CSV OUT_JSON
"""
import csv,hashlib,json,sys,collections
from pathlib import Path
image,mapping,out=map(Path,sys.argv[1:]);b=image.read_bytes()
assert hashlib.sha256(b).hexdigest()=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
expected=set(range(0x11ee7,0x11ef8))|set(range(0x1bda2,0x29d60));seen=set();counts=collections.Counter();rows=list(csv.DictReader(mapping.open(encoding='utf-8-sig')))
for r in rows:
    a,e,n=map(int,(r['start'],r['end_exclusive'],r['length']));assert 0<=a<e<=len(b) and e-a==n
    assert hashlib.sha256(b[a:e]).hexdigest()==r['range_sha256']
    points=set(range(a,e));assert not seen&points and points<=expected;seen|=points
    assert r['status'] in ['UNKNOWN','PARTIAL','CLASSIFIED ONLY','DEEP VERIFIED']
    counts[r['status']]+=n
assert seen==expected and len(seen)==57295
s=dict(map_sha256=hashlib.sha256(mapping.read_bytes()).hexdigest(),intervals=len(rows),baseline_membership_exact=True,overlapping_bytes=0,missing_bytes=0,outside_baseline_bytes=0,range_hashes_verified=len(rows),status_bytes=dict(counts),semantic_classifications_independently_proven=False)
out.write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
