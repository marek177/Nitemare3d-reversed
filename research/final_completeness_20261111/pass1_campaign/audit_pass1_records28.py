"""Reproduce the nominal 350 x 28 record extent; no runtime bounds claim.
Usage: python audit_pass1_records28.py IMAGE RELOCS PRIOR_MAP DECODER_DIR OUT
"""
import collections,csv,hashlib,json,struct,sys
from pathlib import Path
image,relocs,prior,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rel={int(r['image_offset']) for r in csv.DictReader(relocs.open())}
for p in [0x29c76,0x29c78,0xb8c3]:
    assert p in rel and struct.unpack_from('<H',b,p)[0]==0x21fd
for p,h in {0xb81d:'6bc61c',0xb820:'050600',0xb83b:'817ef84e26',0xb840:'720e',0xb856:'8e066625',0xb97d:'8346f81c',0xb981:'46',0xb99f:'89367062'}.items():
    assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h),(hex(p),b[p:p+8].hex())
start,end=0x21fd6,0x2461e
assert end-start==350*28 and b[start:end]==bytes(end-start)
rows=list(csv.DictReader(prior.open(encoding='utf-8-sig')));updated=[];added=0
for r in rows:
    a,e=int(r['start']),int(r['end_exclusive']);assert sha(b[a:e])==r['range_sha256']
    cuts=sorted({a,e}|{p for p in (start,end) if a<p<e})
    for x,y in zip(cuts,cuts[1:]):
        n=dict(r);n.update(start=x,end_exclusive=y,length=y-x,range_sha256=sha(b[x:y]),records28='')
        if start<=x<end:
            added+=y-x if r['status']!='PARTIAL' else 0
            n.update(status='PARTIAL',records28='nominal_350_x_28; fields and error-path lifetime open')
        updated.append(n)
fmt=Formatter(FormatterSyntax.INTEL);insns=[];pos=0xb7f8
for ins in Decoder(16,b[pos:0xb9a3],ip=0x958):
    assert not ins.is_invalid
    insns.append(dict(image_offset=pos,cs=0xaea,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)))
    pos+=ins.len
assert pos==0xb9a3
records=[dict(index=i,start=start+28*i,end_exclusive=start+28*(i+1),status='PARTIAL') for i in range(350)]
fields=[dict(name='nominal_records28',start=start,end_exclusive=end,length=end-start,type='record[350][28]',status='PARTIAL',range_sha256=sha(b[start:end]))]
out.mkdir(parents=True,exist_ok=True)
for name,data in [('noncode_intervals',updated),('evidence_instructions',insns),('records',records),('data_fields',fields)]:
    with (out/(name+'.csv')).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
(out/'noncode_intervals.json').write_text(json.dumps(updated,indent=2)+'\n')
counts=collections.Counter()
for r in updated:counts[r['status']]+=int(r['length'])
assert sum(counts.values())==57295
summary=dict(image_sha256=sha(b),prior_sha256=sha(prior.read_bytes()),nominal_start=start,nominal_end_exclusive=end,nominal_capacity=350,stride=28,new_partial_bytes=added,status_bytes=dict(counts),counter_default_ds_offset=0x6270,counter_image=0x2d980,counter_in_original_noncode=False,error_call_noreturn_proven=False,all_fields_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
