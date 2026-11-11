"""Recover three initial sentinel-terminated 18-byte UI record arrays.
Usage: python audit_pass1_grid_ui.py IMAGE PRIOR_MAP DECODER_DIR OUT
"""
import csv,collections,hashlib,json,struct,sys
from pathlib import Path
image,prior,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
relocation_path=image.parent/'relocations.csv'
rel={int(r['image_offset']):int(r['original_word']) for r in csv.DictReader(relocation_path.open())}
tables=[(0x1d080,5)]
for start,count in tables:
    for i in range(count):
        p=start+18*i;assert b[p]!=0 and rel[p+16]==0x2771
    assert b[start+18*count:start+18*(count+1)]==bytes(18)
fields=[dict(name='ui_records_after_byte_grid',start=0x1d080,end_exclusive=0x1d0ec,length=108,type='five_18_BYTE_UI_records_plus_sentinel',status='PARTIAL')]
assert sum((count+1)*18 for start,count in tables)==108
for f in fields:f['range_sha256']=sha(b[f['start']:f['end_exclusive']])
for p,h in {0x96b4:'68081c',0x96b7:'680010',0x96ba:'9a4619290d',0xebf8:'26803f00',0xec09:'6626ff740e',0xec2f:'83c612',0xec32:'26803c00'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
insns=[];fmt=Formatter(FormatterSyntax.INTEL)
for name,a,e,cs in [('ui_caller',0x96b4,0x96c2,0x83d),('ui_record_consumer_prefix',0xebd6,0xec38,0xd29)]:
    pos=a
    for ins in Decoder(16,b[a:e],ip=a-cs*16):
        assert not ins.is_invalid;insns.append(dict(block=name,image_offset=pos,cs=cs,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)));pos+=ins.len
    assert pos==e

updated=[];added=0
for r in csv.DictReader(prior.open(encoding='utf-8-sig')):
    a,e=int(r['start']),int(r['end_exclusive']);assert sha(b[a:e])==r['range_sha256']
    cuts=sorted({a,e}|{p for f in fields for p in (f['start'],f['end_exclusive']) if a<p<e})
    for x,y in zip(cuts,cuts[1:]):
        n=dict(r);n.update(start=x,end_exclusive=y,length=y-x,range_sha256=sha(b[x:y]),ui_record_field='')
        for f in fields:
            if f['start']<=x<f['end_exclusive']:
                added+=y-x if r['status']!='PARTIAL' else 0;n.update(status='PARTIAL',ui_record_field=f['name'])
        updated.append(n)
out.mkdir(parents=True,exist_ok=True)
records=[dict(table_start=start,index=i,start=start+18*i,end_exclusive=start+18*(i+1),sentinel=(i==count),status='PARTIAL') for start,count in tables for i in range(count+1)]
for name,data in [('records',records),('data_fields',fields),('evidence_instructions',insns),('noncode_intervals',updated)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
(out/'noncode_intervals.json').write_text(json.dumps(updated,indent=2)+'\n')
c=collections.Counter()
for r in updated:c[r['status']]+=int(r['length'])
assert sum(c.values())==57295
s=dict(image_sha256=sha(b),prior_sha256=sha(prior.read_bytes()),initial_nonzero_records=5,sentinels=1,record_stride=18,typed_bytes=108,new_partial_bytes=added,status_bytes=dict(c),all_fields_closed=False,all_ui_writers_closed=False,subcall_contracts_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
