"""python audit_pass1_ctype.py IMAGE INVENTORY DECODER_DIR OUT"""
import collections,csv,hashlib,json,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
start=0x27710+0x2369;table=b[start:start+256]
expected={1:set(range(65,91)),2:set(range(97,123)),4:set(range(48,58)),8:{9,10,11,12,13,32},16:set(range(33,48))|set(range(58,65))|set(range(91,97))|set(range(123,127)),32:set(range(32))|{127},64:{32},128:set(range(48,58))|set(range(65,71))|set(range(97,103))}
for mask,values in expected.items():assert {i for i,v in enumerate(table) if v&mask}==values,(mask,values)
assert b[0x12c3c:0x12c45]==bytes.fromhex('8a1f2afff687692308')
old=json.loads(inventory.read_text());refs=[];fmt=Formatter(FormatterSyntax.INTEL)
for r in old:
    if '0x2369' not in r['operands']:continue
    p=r['image_offset'];code=bytes.fromhex(r['bytes']);assert b[p:p+len(code)]==code and p==r['cs']*16+r['ip']
    ins=Decoder(16,code,ip=r['ip']).decode();assert not ins.is_invalid and ins.len==len(code) and ins.memory_displacement==0x2369
    refs.append(dict(image_offset=p,cs=r['cs'],ip=r['ip'],bytes=code.hex(),instruction=fmt.format(ins),scope='literal classification access; some callers sign extend and may index before table'))
fields=[dict(name='ascii_ctype_table',start=start,end_exclusive=start+256,length=256,type='BYTE_bitmask[256]',status='PARTIAL',range_sha256=sha(table))]
entries=[dict(index=i,image_offset=start+i,initial_value=v,bits=';'.join(hex(m) for m in expected if v&m)) for i,v in enumerate(table)]
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('data_fields',fields),('entries',entries),('references',refs)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=256,literal_references=len(refs),exact_mask_sets={hex(m):sorted(v) for m,v in expected.items()},runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(dict(typed_bytes=256,literal_references=len(refs),exact_mask_sets_verified=True)))
