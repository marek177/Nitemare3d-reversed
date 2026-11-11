"""Consumer-backed four label pointers; original selector code and PASS1 union.
Usage: python audit_pass1_key_labels.py IMAGE RELOCS PASS1_MAP DECODER_DIR OUT_DIR
"""
import collections,csv,hashlib,json,struct,sys
from pathlib import Path
image,relocs,prior,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda v:hashlib.sha256(v).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rel={int(r['image_offset']) for r in csv.DictReader(relocs.open(encoding='utf-8-sig'))};dsbase=0x27710;fmt=Formatter(FormatterSyntax.INTEL)
fields=[];labels=[];covered={};code=[]
for ins in Decoder(16,b[0xa306:0xa33a],ip=0x1f36):
    assert not ins.is_invalid;a=0x83d0+ins.ip;code.append(dict(image_offset=a,cs=0x83d,ip=ins.ip,bytes=b[a:a+ins.len].hex(),instruction=fmt.format(ins)))
assert code[-1]['bytes']=='cb'
for index,off,text,source in [(0,0xd0a,'Red key',0xa30b),(1,0xd18,'Green key',0xa313),(2,0xd26,'Blue key',0xa31b),(3,0xd36,'Yellow key',0xa323)]:
    p=dsbase+off;lo,seg=struct.unpack_from('<HH',b,p);assert seg==0x2771 and p+2 in rel and p not in rel
    target=seg*16+lo;raw=text.encode('ascii')+bytes([0]);assert b[target:target+len(raw)]==raw
    assert b[source:source+4]==bytes.fromhex('66a1')+struct.pack('<H',off)
    labels.append(dict(index=index,pointer_image=p,pointer_ds_offset=off,initial_far_offset=lo,initial_far_segment=seg,target_image=target,text=text,source_instruction_image=source,context='requires incoming DS=relocated2771h',status='PARTIAL'))
    for name,a,end,typ in [('key_label_pointer_'+str(index),p,p+4,'FAR16_offset_segment'),('key_label_text_'+str(index),target,target+len(raw),'ASCII_ASCIIZ')]:
        fid=len(fields);fields.append(dict(field_id=fid,name=name,start=a,end_exclusive=end,length=end-a,type=typ,range_sha256=sha(b[a:end]),status='PARTIAL',scope='initial object and selector use; global DS/writers/lifetime remain open'))
        for pos in range(a,end):assert pos not in covered;covered[pos]=fid
states={}
for r in csv.DictReader(prior.open(encoding='utf-8-sig')):
    a,e=int(r['start']),int(r['end_exclusive']);assert sha(b[a:e])==r['range_sha256']
    for pos in range(a,e):assert pos not in states;states[pos]=r
assert len(states)==57295 and set(covered)<=set(states)
updated=[]
for a,e in [(0x11ee7,0x11ef8),(0x1bda2,0x29d60)]:
    def key(p):
        r=states[p];fid=covered.get(p)
        return ('PARTIAL' if fid is not None else r['status'],fid,r.get('relocation_field_id',''),r['structural_class'])
    start=a;previous=key(a)
    for p in range(a+1,e+1):
        current=key(p) if p<e else None
        if current!=previous:
            updated.append(dict(original_baseline_interval_id=states[start]['original_baseline_interval_id'],start=start,end_exclusive=p,length=p-start,status=previous[0],key_label_field_id=previous[1] if previous[1] is not None else '',relocation_field_id=previous[2],structural_class=previous[3],range_sha256=sha(b[start:p]),deep_verified=False));start=p;previous=current
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('selector_instructions',code),('labels',labels),('data_fields',fields),('noncode_intervals',updated)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'noncode_intervals.json').write_text(json.dumps(updated,indent=2)+'\n',encoding='utf-8')
counts=collections.Counter()
for r in updated:counts[r['status']]+=r['length']
result=dict(image_sha256=sha(b),prior_map_sha256=sha(prior.read_bytes()),objects=len(fields),object_union_bytes=len(covered),already_partial_bytes=sum(states[p]['status']=='PARTIAL' for p in covered),new_partial_bytes=sum(states[p]['status']!='PARTIAL' for p in covered),status_bytes=dict(counts),partition_bytes=sum(r['length'] for r in updated),partition_intervals=len(updated),selector_start=0xa306,selector_end_exclusive=0xa33a,index_count=4,local_bounds_check_present=False,natural_DS_context_closed=False,new_deep_verified_bytes=0,runtime_tests=0)
assert result['partition_bytes']==57295
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
