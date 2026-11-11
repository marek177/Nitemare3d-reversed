"""Recover initial 64x64 strided map-cell extent from nested constructor loops.
Usage: python audit_pass1_map_grid.py IMAGE PRIOR_MAP DECODER_DIR OUT
"""
import csv,collections,hashlib,json,struct,sys
from pathlib import Path
image,prior,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
relocation_path=image.parent/'relocations.csv'
rel={int(r['image_offset']):int(r['original_word']) for r in csv.DictReader(relocation_path.open())}
assert rel[0x29c78]==0x21fd
fields=[dict(name='map_cell_grid',start=0x2570f,end_exclusive=0x2770f,length=8192,type='64_x_64_cells_stride_2_low_BYTE_observed',status='PARTIAL')]
assert b[0x2570f:0x2770f]==bytes(8192)
for f in fields:f['range_sha256']=sha(b[f['start']:f['end_exclusive']])
for p,h in {0xb809:'33f6',0xb812:'8976f0',0xb815:'bf3f37',0xb818:'c746f62000',0xb826:'8e066825',0xb82a:'268a1d',0xb982:'83c702',0xb985:'8346f640',0xb989:'817ef62010',0xb992:'8346f040',0xb996:'817ef00010',0xb98e:'0f8c94fe',0xb99b:'0f8c79fe'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
insns=[];fmt=Formatter(FormatterSyntax.INTEL)
for name,a,e,cs in [('grid_scan_and_object_constructor',0xb7f8,0xb9a3,0xaea)]:
    pos=a
    for ins in Decoder(16,b[a:e],ip=a-cs*16):
        assert not ins.is_invalid;insns.append(dict(block=name,image_offset=pos,cs=cs,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)));pos+=ins.len
    assert pos==e

updated=[];added=0
for r in csv.DictReader(prior.open(encoding='utf-8-sig')):
    a,e=int(r['start']),int(r['end_exclusive']);assert sha(b[a:e])==r['range_sha256']
    cuts=sorted({a,e}|{p for f in fields for p in (f['start'],f['end_exclusive']) if a<p<e})
    for x,y in zip(cuts,cuts[1:]):
        n=dict(r);n.update(start=x,end_exclusive=y,length=y-x,range_sha256=sha(b[x:y]),map_grid_field='')
        for f in fields:
            if f['start']<=x<f['end_exclusive']:
                added+=y-x if r['status']!='PARTIAL' else 0;n.update(status='PARTIAL',map_grid_field=f['name'])
        updated.append(n)
out.mkdir(parents=True,exist_ok=True)
for name,data in [('data_fields',fields),('evidence_instructions',insns),('noncode_intervals',updated)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
(out/'noncode_intervals.json').write_text(json.dumps(updated,indent=2)+'\n')
c=collections.Counter()
for r in updated:c[r['status']]+=int(r['length'])
assert sum(c.values())==57295
s=dict(image_sha256=sha(b),prior_sha256=sha(prior.read_bytes()),grid_rows=64,grid_columns=64,cell_stride=2,typed_bytes=8192,new_partial_bytes=added,status_bytes=dict(c),all_fields_closed=False,all_grid_writers_closed=False,subcall_contracts_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
