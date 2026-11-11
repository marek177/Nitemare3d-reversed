"""python compare_bit_reverse_versions.py CANONICAL_IMAGE OLD_OUTPUT_ROOT OUT_JSON"""
import hashlib,json,sys
from pathlib import Path
image,root,out=map(Path,sys.argv[1:]);b=image.read_bytes()
assert hashlib.sha256(b).hexdigest()=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
pattern=b[0xfc72:0xfcab];rows=[]
for label in ['10','11','12','15','17','18','19','20']:
    p=root/('N3D-'+label)/'unpacked_image.bin'
    if not p.exists():rows.append(dict(version_label=label,missing=True));continue
    v=p.read_bytes();hits=[];pos=v.find(pattern)
    while pos>=0:hits.append(pos);pos=v.find(pattern,pos+1)
    rows.append(dict(version_label=label,path=str(p),image_sha256=hashlib.sha256(v).hexdigest(),exact_byte_matches=hits))
out.write_text(json.dumps(rows,indent=2)+'\n');print('version labels:',len(rows),'unique image hashes:',len({r['image_sha256'] for r in rows if 'image_sha256' in r}))
