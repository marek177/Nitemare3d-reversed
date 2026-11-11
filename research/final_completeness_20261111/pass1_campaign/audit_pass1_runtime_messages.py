"""python audit_pass1_runtime_messages.py IMAGE DECODER_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
records=[];p=0x29c86
while True:
    code=struct.unpack_from('<H',b,p)[0]
    if code==0xffff:break
    e=b.index(0,p+2)+1;records.append(dict(code=code,start=p,end_exclusive=e,text_start=p+2,text=b[p+2:e-1].decode('ascii'),length=e-p,status='PARTIAL'));p=e
assert [r['code'] for r in records]==[0,3,9,252,255,2,1] and p==0x29d5c
fields=[dict(name='crt_variable_error_records',start=0x29c86,end_exclusive=p+2,length=p+2-0x29c86,type='WORD_code_NUL_ASCII_records_with_FFFF_sentinel',status='PARTIAL',range_sha256=sha(b[0x29c86:p+2]))]
for a,h in {0x12404:'be7625',0x12407:'ad',0x12408:'3bc2',0x1240c:'40',0x1240d:'96',0x12416:'f2ae',0x12422:'ca0200',0x12450:'b440',0x12452:'cd21'}.items():assert b[a:a+len(bytes.fromhex(h))]==bytes.fromhex(h)
rows=[];fmt=Formatter(FormatterSyntax.INTEL)
for a,e in [(0x123fa,0x12425),(0x12425,0x1245b)]:
    pos=a
    for ins in Decoder(16,b[a:e],ip=a-0x11ee0):
        assert not ins.is_invalid;rows.append(dict(image_offset=pos,cs=0x11ee,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)));pos+=ins.len
    assert pos==e
out.mkdir(parents=True,exist_ok=True)
for name,data in [('data_fields',fields),('records',records),('instructions',rows),('lookup_instructions',[r for r in rows if r['image_offset']<0x12425])]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
s=dict(image_sha256=sha(b),typed_bytes=fields[0]['length'],records=len(records),sentinel_start=p,ffff_query_returns_after_sentinel=True,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
