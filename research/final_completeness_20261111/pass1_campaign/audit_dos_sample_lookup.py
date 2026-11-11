"""Exact sample BYTE -> output BYTE lookup, bounded by original consumer bytes."""
import collections,csv,hashlib,json,sys
from pathlib import Path
image,out=map(Path,sys.argv[1:]);b=image.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
base=0x15bf0;start=base+0x33b9;end=start+256;raw=b[start:end]
assert b[0x19273:0x1927f]==bytes.fromhex('a0555532e405b9332ea39136')
assert b[0x1927f:0x19289]==bytes.fromhex('2ea05555e64232c0e642')
out.mkdir(parents=True,exist_ok=True)
rows=[dict(input_byte=n,cs_offset=0x33b9+n,image_offset=start+n,output_byte=value,status='PARTIAL',scope='initial canonical lookup byte; runtime immutability not proven') for n,value in enumerate(raw)]
with (out/'lookup.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
fields=[dict(name='sample_to_port42_lookup',start=start,end_exclusive=end,type='BYTE[256]',range_sha256=hashlib.sha256(raw).hexdigest(),status='PARTIAL',pass320_membership='UNKNOWN')]
with (out/'data_intervals.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(fields[0]));w.writeheader();w.writerows(fields)
r=dict(image_sha256=h,start=start,end_exclusive=end,bytes=256,cs_start=0x33b9,cs_end_exclusive=0x34b9,range_sha256=hashlib.sha256(raw).hexdigest(),min_output=min(raw),max_output=max(raw),distinct_outputs=len(set(raw)),nondecreasing=all(a<=c for a,c in zip(raw,raw[1:])),histogram=dict(sorted(collections.Counter(raw).items())),consumer_index='33B9h + zero_extended_sample_BYTE',address_wrap=False,mathematical_generation_formula_known=False,runtime_immutability_proven=False,original_pass320_membership='UNKNOWN',new_deep_verified_bytes=0,runtime_tests=0)
(out/'summary.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in r.items() if k!='histogram'},indent=2))
