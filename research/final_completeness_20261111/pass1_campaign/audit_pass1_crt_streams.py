"""Recover initial CRT stream extent from inclusive end pointer and stride.
Usage: python audit_pass1_crt_streams.py IMAGE PRIOR_MAP DECODER_DIR OUT
"""
import csv,collections,hashlib,json,struct,sys
from pathlib import Path
image,prior,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
last=struct.unpack_from('<H',b,0x299ca)[0];assert last==0x2212
count=(last-0x217a)//8+1;assert count==20 and (last-0x217a)%8==0
fields=[dict(name='initial_stream_records',start=0x2988a,end_exclusive=0x2992a,length=160,type='20_x_8_byte_CRT_records',status='PARTIAL'),dict(name='inclusive_last_stream_offset',start=0x299ca,end_exclusive=0x299cc,length=2,type='NEAR_offset_in_default_DS',status='PARTIAL')]
for f in fields:f['range_sha256']=sha(b[f['start']:f['end_exclusive']])
for p,h in {0x12bb4:'be7a21',0x12bdb:'83c608',0x12bde:'3936ba22',0x12be2:'721c',0x12bc4:'f6440602',0x12bea:'f6440683',0x12c12:'c20200'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
insns=[];fmt=Formatter(FormatterSyntax.INTEL)
for name,a,e in [('iterator',0x12bac,0x12c15),('record_consumer_prefix',0x12adc,0x12b2c)]:
    pos=a
    for ins in Decoder(16,b[a:e],ip=a-0x11ee0):
        assert not ins.is_invalid;insns.append(dict(block=name,image_offset=pos,cs=0x11ee,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)));pos+=ins.len
    assert pos==e
records=[]
for i in range(count):
    a=0x2988a+i*8
    records.append(dict(index=i,start=a,end_exclusive=a+8,initial_hex=b[a:a+8].hex(),word0=struct.unpack_from('<H',b,a)[0],word2=struct.unpack_from('<H',b,a+2)[0],word4=struct.unpack_from('<H',b,a+4)[0],flags_byte6=b[a+6],handle_byte7=b[a+7],status='PARTIAL'))
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
s=dict(image_sha256=sha(b),prior_sha256=sha(prior.read_bytes()),nominal_records=count,initial_inclusive_end_offset=last,typed_bytes=162,new_partial_bytes=added,status_bytes=dict(c),all_fields_closed=False,end_pointer_writers_closed=False,subcall_contracts_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
