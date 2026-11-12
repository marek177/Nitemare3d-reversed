"""IMAGE REPLAY_DIR OUT: exact instruction-byte unions and unowned span gaps."""
import csv,hashlib,json,sys
from pathlib import Path
image,replay,out=map(Path,sys.argv[1:]);out.mkdir(exist_ok=True);b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();s=json.loads((replay/'summary.json').read_text());rows=[]
for f in s['functions']:
 owned=set()
 for r in csv.DictReader((replay/(f['name']+'.csv')).open(encoding='utf-8')):
  p=int(r['image_offset']);raw=bytes.fromhex(r['bytes']);assert b[p:p+len(raw)]==raw;assert not owned.intersection(range(p,p+len(raw)));owned.update(range(p,p+len(raw)))
 assert len(owned)==f['instruction_bytes'];gaps=sorted(set(range(f['start'],f['end_exclusive']))-owned)
 for p in gaps:rows.append(dict(function=f['name'],start=p,end_exclusive=p+1,byte_hex='%02X'%b[p],status='Outside retained entryCFG instruction union;not globally proven padding/noncode'))
with (out/'span_gaps.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
proof=dict(bounded_functions=len(s['functions']),unowned_span_bytes=len(rows),status_changes=0,new_deep_verified_bytes=0,files=[dict(path=str(p.resolve()),sha256=sha(p.read_bytes())) for p in (image,replay/'summary.json',Path(__file__))]);(out/'summary.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(rows))
