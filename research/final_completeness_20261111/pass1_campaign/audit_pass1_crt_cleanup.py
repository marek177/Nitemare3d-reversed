"""Pinned CRT callback slots; initial values do not prove runtime immutability.
Usage: python audit_pass1_crt_cleanup.py IMAGE RELOCS PRIOR_MAP DECODER_DIR OUT
"""
import csv,collections,hashlib,json,struct,sys
from pathlib import Path
image,relocs,prior,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rel={int(r['image_offset']) for r in csv.DictReader(relocs.open())}
assert 0x29c60 in rel and b[0x29c5e:0x29c62]==bytes.fromhex('1e08ee11')
fields=[]
for name,o,n,t in [('callback_magic',0x2534,2,'WORD_magic_guard'),('optional_near_callback',0x253a,2,'NEAR_offset_in_CRT_CS'),('optional_far_callback',0x2542,4,'FAR16_pointer_segment_also_nonzero_guard'),('cleanup_entry',0x254e,4,'FAR16_cleanup_table_entry')]:
    a=0x27710+o
    fields.append(dict(name=name,start=a,end_exclusive=a+n,length=n,type=t,initial_hex=b[a:a+n].hex(),status='PARTIAL',range_sha256=sha(b[a:a+n]),condition='default DS and current slot contents; global writers unresolved'))
insns=[];fmt=Formatter(FormatterSyntax.INTEL)
for name,a,e in [('callback_guards',0x12107,0x12125),('cleanup_call_range',0x120fe,0x12107),('final_callback',0x12152,0x1216b),('reverse_far_iterator',0x1216b,0x1217e),('initial_cleanup_target',0x126fe,0x12714),('target_subcall_entry',0x12ba4,0x12bac)]:
    pos=a
    for ins in Decoder(16,b[a:e],ip=a-0x11ee0):
        assert not ins.is_invalid
        insns.append(dict(block=name,image_offset=pos,cs=0x11ee,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)));pos+=ins.len
    assert pos==e
for p,h in {0x120fe:'be4e25',0x12101:'bf5225',0x12107:'813e3425d6d6',0x1210f:'ff163a25',0x12152:'8b0e4425',0x1215b:'ff1e4225',0x1216f:'83ef04',0x12179:'ff1d'}.items():
    assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
rows=list(csv.DictReader(prior.open(encoding='utf-8-sig')));updated=[];added=0
for r in rows:
    a,e=int(r['start']),int(r['end_exclusive']);assert sha(b[a:e])==r['range_sha256']
    cuts=sorted({a,e}|{p for f in fields for p in (f['start'],f['end_exclusive']) if a<p<e})
    for x,y in zip(cuts,cuts[1:]):
        n=dict(r);n.update(start=x,end_exclusive=y,length=y-x,range_sha256=sha(b[x:y]),crt_cleanup_field='')
        for f in fields:
            if f['start']<=x<f['end_exclusive']:
                added+=y-x if r['status']!='PARTIAL' else 0;n.update(status='PARTIAL',crt_cleanup_field=f['name'])
        updated.append(n)
out.mkdir(parents=True,exist_ok=True)
for name,data in [('data_fields',fields),('evidence_instructions',insns),('noncode_intervals',updated)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
(out/'noncode_intervals.json').write_text(json.dumps(updated,indent=2)+'\n')
c=collections.Counter()
for r in updated:c[r['status']]+=int(r['length'])
assert sum(c.values())==57295
s=dict(image_sha256=sha(b),prior_sha256=sha(prior.read_bytes()),typed_bytes=12,new_partial_bytes=added,status_bytes=dict(c),initial_cleanup_pointer='11EE:081E',initial_cleanup_target_image=0x126fe,initial_magic=0,initial_near_callback=0xe4,initial_optional_far_pointer=0,initial_cleanup_entries=1,all_writers_closed=False,all_cleanup_targets_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
