"""Recover three nominal 1200-byte graphics blocks from constant callers and stride.
Usage: python audit_pass1_graphics_blocks.py IMAGE PRIOR_MAP DECODER_DIR OUT
"""
import csv,collections,hashlib,json,struct,sys
from pathlib import Path
image,prior,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
relocation_path=image.parent/'relocations.csv'
rel={int(r['image_offset']):int(r['original_word']) for r in csv.DictReader(relocation_path.open())}
assert rel[0xd41e]==0x20b9 and rel[0xd446]==0x20b9 and rel[0xd468]==0x20b9
fields=[dict(name='graphics_blocks',start=0x20b90,end_exclusive=0x219a0,length=3600,type='3_x_1200_BYTE_nominal_blocks',status='PARTIAL')]
assert b[0x20b90:0x219a0]==bytes(3600)
for f in fields:f['range_sha256']=sha(b[f['start']:f['end_exclusive']])
for p,h in {0x83ef:'6a02',0x841a:'6a01',0x84f2:'6a00',0xd416:'69c3b004',0xd41d:'68b920',0xd431:'69c8b004',0xd488:'83c107',0xd48b:'c1f903',0xd4d0:'81fe8000'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
insns=[];fmt=Formatter(FormatterSyntax.INTEL)
for name,a,e,cs in [('block_loader_and_parser',0xd3fa,0xd4dc,0xd29),('caller2',0x83ef,0x83f9,0x83d),('caller1',0x841a,0x8424,0x83d),('caller0',0x84f2,0x84fc,0x83d)]:
    pos=a
    for ins in Decoder(16,b[a:e],ip=a-cs*16):
        assert not ins.is_invalid;insns.append(dict(block=name,image_offset=pos,cs=cs,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)));pos+=ins.len
    assert pos==e

updated=[];added=0
for r in csv.DictReader(prior.open(encoding='utf-8-sig')):
    a,e=int(r['start']),int(r['end_exclusive']);assert sha(b[a:e])==r['range_sha256']
    cuts=sorted({a,e}|{p for f in fields for p in (f['start'],f['end_exclusive']) if a<p<e})
    for x,y in zip(cuts,cuts[1:]):
        n=dict(r);n.update(start=x,end_exclusive=y,length=y-x,range_sha256=sha(b[x:y]),graphics_block_field='')
        for f in fields:
            if f['start']<=x<f['end_exclusive']:
                added+=y-x if r['status']!='PARTIAL' else 0;n.update(status='PARTIAL',graphics_block_field=f['name'])
        updated.append(n)
out.mkdir(parents=True,exist_ok=True)
for name,data in [('data_fields',fields),('evidence_instructions',insns),('noncode_intervals',updated)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
(out/'noncode_intervals.json').write_text(json.dumps(updated,indent=2)+'\n')
c=collections.Counter()
for r in updated:c[r['status']]+=int(r['length'])
assert sum(c.values())==57295
s=dict(image_sha256=sha(b),prior_sha256=sha(prior.read_bytes()),nominal_blocks=3,block_stride=1200,typed_bytes=3600,new_partial_bytes=added,status_bytes=dict(c),all_fields_closed=False,all_block_writers_closed=False,subcall_contracts_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
