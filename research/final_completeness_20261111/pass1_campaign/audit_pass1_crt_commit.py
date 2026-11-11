"""Recover DOS commit wrapper and initial handle globals.
Usage: python audit_pass1_crt_commit.py IMAGE PRIOR_MAP DECODER_DIR OUT
"""
import csv,collections,hashlib,json,struct,sys
from pathlib import Path
image,prior,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
last=struct.unpack_from('<H',b,0x299ca)[0];assert last==0x2212
count=(last-0x217a)//8+1;assert count==20 and (last-0x217a)%8==0
fields=[dict(name=name,start=0x27710+o,end_exclusive=0x27710+o+n,length=n,type=t,status='PARTIAL') for name,o,n,t in [('crt_error',0x2118,2,'WORD_error'),('version',0x2120,2,'BYTE_minor_BYTE_major'),('native_error',0x2126,2,'WORD_with_BYTE_alias'),('handle_limit',0x2128,2,'WORD_signed_limit'),('handle_flags',0x212a,20,'BYTE_flags[20]_initial_extent')]]
for f in fields:f['range_sha256']=sha(b[f['start']:f['end_exclusive']])
for p,h in {0x1479c:'39362821',0x147b5:'3d1e03',0x147be:'f6842a2101',0x158ba:'b468',0x158bc:'cd21',0x11f37:'86e0',0x11f39:'36a32021'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
insns=[];fmt=Formatter(FormatterSyntax.INTEL)
for name,a,e in [('commit_wrapper',0x14790,0x147e9),('dos_commit_primitive',0x158b4,0x158c1),('success_error_dispatch',0x12484,0x12497),('version_store',0x11f33,0x11f3d)]:
    pos=a
    for ins in Decoder(16,b[a:e],ip=a-0x11ee0):
        assert not ins.is_invalid;insns.append(dict(block=name,image_offset=pos,cs=0x11ee,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)));pos+=ins.len
    assert pos==e
records=[]
for i in range(count):
    a=0x2983a+i
    records.append(dict(index=i,start=a,end_exclusive=a+1,initial_flags=b[a],status='PARTIAL'))
updated=[];added=0
for r in csv.DictReader(prior.open(encoding='utf-8-sig')):
    a,e=int(r['start']),int(r['end_exclusive']);assert sha(b[a:e])==r['range_sha256']
    cuts=sorted({a,e}|{p for f in fields for p in (f['start'],f['end_exclusive']) if a<p<e})
    for x,y in zip(cuts,cuts[1:]):
        n=dict(r);n.update(start=x,end_exclusive=y,length=y-x,range_sha256=sha(b[x:y]),crt_stream_field='')
        for f in fields:
            if f['start']<=x<f['end_exclusive']:
                added+=y-x if r['status']!='PARTIAL' else 0;n.update(status='PARTIAL',crt_stream_field=f['name'])
        updated.append(n)
out.mkdir(parents=True,exist_ok=True)
for name,data in [('data_fields',fields),('records',records),('evidence_instructions',insns),('noncode_intervals',updated)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
(out/'noncode_intervals.json').write_text(json.dumps(updated,indent=2)+'\n')
c=collections.Counter()
for r in updated:c[r['status']]+=int(r['length'])
assert sum(c.values())==57295
s=dict(image_sha256=sha(b),prior_sha256=sha(prior.read_bytes()),nominal_records=count,typed_bytes=28,new_partial_bytes=added,status_bytes=dict(c),all_fields_closed=False,handle_limit_writers_closed=False,subcall_contracts_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
