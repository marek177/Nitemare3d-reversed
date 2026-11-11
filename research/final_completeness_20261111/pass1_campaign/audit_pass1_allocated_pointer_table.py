"""Recover nominal 128 FAR allocation pointers from clamp and producer stride.
Usage: python audit_pass1_allocated_pointer_table.py IMAGE PRIOR_MAP DECODER_DIR OUT
"""
import csv,collections,hashlib,json,struct,sys
from pathlib import Path
image,prior,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
relocation_path=image.parent/'relocations.csv'
rel={int(r['image_offset']):int(r['original_word']) for r in csv.DictReader(relocation_path.open())}
assert rel[0x29c70]==0x1be7
fields=[dict(name='allocated_pointer_table',start=0x1be70,end_exclusive=0x1c070,length=512,type='128_x_FAR16_pointer_nominal',status='PARTIAL')]
assert b[0x1be70:0x1c070]==bytes(512)
for f in fields:f['range_sha256']=sha(b[f['start']:f['end_exclusive']])
for p,h in {0x7783:'3d8000',0x7788:'b88000',0x778b:'a30435',0x779e:'33ff',0x77a6:'be0000',0x77b4:'8e066025',0x77b8:'268904',0x77bb:'26895402',0x77d8:'83c604',0x77e1:'3b3e0435'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
insns=[];fmt=Formatter(FormatterSyntax.INTEL)
for name,a,e,cs in [('clamp_and_pointer_producer',0x7780,0x77e7,0x768),('pointer_consumer',0x78b7,0x78ed,0x768)]:
    pos=a
    for ins in Decoder(16,b[a:e],ip=a-cs*16):
        assert not ins.is_invalid;insns.append(dict(block=name,image_offset=pos,cs=cs,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)));pos+=ins.len
    assert pos==e

updated=[];added=0
for r in csv.DictReader(prior.open(encoding='utf-8-sig')):
    a,e=int(r['start']),int(r['end_exclusive']);assert sha(b[a:e])==r['range_sha256']
    cuts=sorted({a,e}|{p for f in fields for p in (f['start'],f['end_exclusive']) if a<p<e})
    for x,y in zip(cuts,cuts[1:]):
        n=dict(r);n.update(start=x,end_exclusive=y,length=y-x,range_sha256=sha(b[x:y]),allocated_pointer_field='')
        for f in fields:
            if f['start']<=x<f['end_exclusive']:
                added+=y-x if r['status']!='PARTIAL' else 0;n.update(status='PARTIAL',allocated_pointer_field=f['name'])
        updated.append(n)
out.mkdir(parents=True,exist_ok=True)
records=[dict(index=i,start=0x1be70+4*i,end_exclusive=0x1be70+4*(i+1),status='PARTIAL') for i in range(128)]
for name,data in [('records',records),('data_fields',fields),('evidence_instructions',insns),('noncode_intervals',updated)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
(out/'noncode_intervals.json').write_text(json.dumps(updated,indent=2)+'\n')
c=collections.Counter()
for r in updated:c[r['status']]+=int(r['length'])
assert sum(c.values())==57295
s=dict(image_sha256=sha(b),prior_sha256=sha(prior.read_bytes()),nominal_records=128,record_stride=4,typed_bytes=512,new_partial_bytes=added,status_bytes=dict(c),all_fields_closed=False,all_pointer_writers_closed=False,subcall_contracts_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
