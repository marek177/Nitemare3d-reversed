"""Recover 4096-byte working grid from explicit clear and coordinate writes.
Usage: python audit_pass1_flags_map_boundary.py IMAGE PRIOR_MAP DECODER_DIR OUT
"""
import csv,collections,hashlib,json,struct,sys
from pathlib import Path
image,prior,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
relocation_path=image.parent/'relocations.csv'
rel={int(r['image_offset']):int(r['original_word']) for r in csv.DictReader(relocation_path.open())}
assert rel[0x36cb]==0x21fd and rel[0x3832]==0x21fd
fields=[dict(name=name,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL') for name,a,e,t in [('runtime_flags',0x256ce,0x2570e,'BYTE_flags[64]'),('corrected_two_byte_map',0x2570e,0x2770e,'64_x_64_cells_stride_2_both_bytes_serialized')]]
assert b[0x256ce:0x2770e]==bytes(8256)
for f in fields:f['range_sha256']=sha(b[f['start']:f['end_exclusive']])
for p,h in {0x36c7:'680020',0x36cd:'683e37',0x36d3:'9ab800ba0f',0x382f:'6a40',0x3834:'68fe36',0x552b:'66b910000000',0x5531:'bffe36',0x5534:'f366ab'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
insns=[];fmt=Formatter(FormatterSyntax.INTEL)
for name,a,e,cs in [('serialize_map',0x36c7,0x36db,0x277),('serialize_flags',0x382f,0x3842,0x277),('clear_flags',0x5524,0x553b,0x4c7),('flags_access',0x553c,0x554f,0x4c7)]:
    pos=a
    for ins in Decoder(16,b[a:e],ip=a-cs*16):
        assert not ins.is_invalid;insns.append(dict(block=name,image_offset=pos,cs=cs,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)));pos+=ins.len
    assert pos==e

updated=[];added=0
for r in csv.DictReader(prior.open(encoding='utf-8-sig')):
    a,e=int(r['start']),int(r['end_exclusive']);assert sha(b[a:e])==r['range_sha256']
    cuts=sorted({a,e}|({0x2770e,0x2770f}&set(range(a+1,e)))|{p for f in fields for p in (f['start'],f['end_exclusive']) if a<p<e})
    for x,y in zip(cuts,cuts[1:]):
        n=dict(r);n.update(start=x,end_exclusive=y,length=y-x,range_sha256=sha(b[x:y]),map_grid_field='')
        for f in fields:
            if f['start']<=x<f['end_exclusive']:
                added+=y-x if r['status']!='PARTIAL' else 0;n.update(status='PARTIAL',map_grid_field=f['name'])
        if x==0x2770e and y==0x2770f:n.update(status='UNKNOWN',map_grid_field='former_grid_overhang_removed')
        updated.append(n)
out.mkdir(parents=True,exist_ok=True)
for name,data in [('data_fields',fields),('evidence_instructions',insns),('noncode_intervals',updated)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
(out/'noncode_intervals.json').write_text(json.dumps(updated,indent=2)+'\n')
c=collections.Counter()
for r in updated:c[r['status']]+=int(r['length'])
assert sum(c.values())==57295
s=dict(image_sha256=sha(b),prior_sha256=sha(prior.read_bytes()),flag_bytes=64,corrected_map_bytes=8192,typed_bytes=8256,demoted_partial_bytes=1,clear_requires_df_zero=True,new_partial_bytes=added,status_bytes=dict(c),all_fields_closed=False,all_grid_writers_closed=False,subcall_contracts_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
