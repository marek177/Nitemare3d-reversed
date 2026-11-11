"""Three far-segment tables: nominal extents, counters, writers and lookup strides.
Usage: python audit_pass1_record_tables.py IMAGE RELOCS PRIOR_PASS1_MAP DECODER_DIR OUT_DIR
"""
import collections,csv,hashlib,json,struct,sys
from pathlib import Path
image,relocs,prior,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda v:hashlib.sha256(v).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rel={int(r['image_offset']):r for r in csv.DictReader(relocs.open(encoding='utf-8-sig'))};base=0x21fd0;fmt=Formatter(FormatterSyntax.INTEL)
for pos in [5,0x57,0xaa,0x278,0x29c66]:assert pos in rel and int(rel[pos]['original_word'])==0x21fd
assert struct.unpack_from('<H',b,0x29c66)[0]==0x21fd
expected={0x255:'26833f40',0x26b:'266b0712',0x26f:'057630',0x275:'c746f6fd21',0x442:'26833f20',0x467:'05f634',0x548:'26833e04000c',0x56e:'05b636',0x2c:'83c312',0x7e:'83c30e',0xd5:'83c306'}
for a,s in expected.items():assert b[a:a+len(bytes.fromhex(s))]==bytes.fromhex(s)
blocks=[]
for name,start,end,cs in [('lookup18',0,0x43,0),('lookup14',0x52,0x95,0),('lookup6',0xa4,0xee,0),('writer18_prefix',0x212,0x28a,0),('writer14_prefix',0x3fe,0x489,0),('writer6_prefix',0x52a,0x582,0)]:
    pos=start
    for ins in Decoder(16,b[start:end],ip=start-cs*16):
        assert not ins.is_invalid;blocks.append(dict(block=name,image_offset=pos,cs=cs,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins),scope='bounded code window; not closed whole-function contract'));pos+=ins.len
    assert pos==end
tables=[];fields=[];records=[];covered={}
for i,offset,stride,capacity in [(0,0x3076,18,64),(1,0x34f6,14,32),(2,0x36b6,6,12)]:
    a=base+offset;e=a+stride*capacity;assert b[a:e]==bytes(e-a)
    tables.append(dict(table_id=i,segment=0x21fd,offset=offset,image_start=a,image_end_exclusive=e,record_bytes=stride,nominal_capacity=capacity,counter_offset=2*i,counter_image=base+2*i,status='PARTIAL',capacity_error_noreturn_proven=False))
    for name,x,y,typ in [('table'+str(i),a,e,'record_bytes[%d][%d]'%(capacity,stride)),('count'+str(i),base+2*i,base+2*i+2,'WORD_count_signed_comparison')]:
        fid=len(fields);fields.append(dict(field_id=fid,name=name,start=x,end_exclusive=y,length=y-x,type=typ,range_sha256=sha(b[x:y]),status='PARTIAL',scope='nominal array layout and producer/consumer strides; fields/lifetime not fully closed'))
        for p in range(x,y):assert p not in covered;covered[p]=fid
    for n in range(capacity):records.append(dict(table_id=i,index=n,start=a+n*stride,end_exclusive=a+(n+1)*stride,record_bytes=stride,initial_bytes=b[a+n*stride:a+(n+1)*stride].hex(),status='PARTIAL'))
assert tables[0]['image_end_exclusive']==tables[1]['image_start'] and tables[1]['image_end_exclusive']==tables[2]['image_start']
states={}
for r in csv.DictReader(prior.open(encoding='utf-8-sig')):
    a,e=int(r['start']),int(r['end_exclusive']);assert sha(b[a:e])==r['range_sha256']
    for p in range(a,e):assert p not in states;states[p]=r
assert len(states)==57295 and set(covered)<=set(states)
updated=[]
for a,e in [(0x11ee7,0x11ef8),(0x1bda2,0x29d60)]:
    def key(p):
        r=states[p];fid=covered.get(p)
        return ('PARTIAL' if fid is not None else r['status'],fid,r.get('key_label_field_id',''),r.get('relocation_field_id',''),r['structural_class'])
    start=a;previous=key(a)
    for p in range(a+1,e+1):
        current=key(p) if p<e else None
        if current!=previous:
            updated.append(dict(original_baseline_interval_id=states[start]['original_baseline_interval_id'],start=start,end_exclusive=p,length=p-start,status=previous[0],record_table_field_id=previous[1] if previous[1] is not None else '',key_label_field_id=previous[2],relocation_field_id=previous[3],structural_class=previous[4],range_sha256=sha(b[start:p]),deep_verified=False));start=p;previous=current
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('tables',tables),('data_fields',fields),('records',records),('evidence_instructions',blocks),('noncode_intervals',updated)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(out/'noncode_intervals.json').write_text(json.dumps(updated,indent=2)+'\n',encoding='utf-8')
counts=collections.Counter()
for r in updated:counts[r['status']]+=r['length']
result=dict(image_sha256=sha(b),prior_map_sha256=sha(prior.read_bytes()),table_segment=0x21fd,segment_source_global_image=0x29c66,tables=len(tables),nominal_records=len(records),table_and_counter_bytes=len(covered),new_partial_bytes=sum(states[p]['status']!='PARTIAL' for p in covered),status_bytes=dict(counts),partition_intervals=len(updated),partition_bytes=sum(r['length'] for r in updated),capacity_error_function_returns_excluded=False,all_record_fields_closed=False,all_writers_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
assert result['partition_bytes']==57295
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
