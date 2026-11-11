"""python audit_pass1_comparison_strings.py IMAGE DECODER_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rel={int(r['image_offset']):int(r['original_word']) for r in csv.DictReader((image.parent/'relocations.csv').open())}
fields=[]
def add(name,a,e,t):fields.append(dict(name=name,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e])))
for name,offset,text in [('code0',0x110a,b'333\0'),('code1',0x110e,b'01532\0'),('code2',0x1112,b'080993\0'),('code3',0x1116,b'372535\0')]:
    a=0x27710+offset;o,s=struct.unpack_from('<HH',b,a);assert rel[a+2]==s==0x2771;t=s*16+o;assert b[t:t+len(text)]==text
    add(name+'_pointer',a,a+4,'FAR16_text_pointer');add(name+'_text',t,t+len(text),'NUL_terminated_ASCII')
for p,h in {0x9324:'2bd8',0x9326:'c1e302',0x9329:'66ffb70a11',0x9333:'9a683cee11',0x15b4e:'c5760a',0x15b51:'c45e06',0x15b63:'2c41',0x15b85:'1cff'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
rows=[];fmt=Formatter(FormatterSyntax.INTEL)
for name,a,e,cs in [('indexed_comparison_caller',0x931a,0x933f,0x83d),('case_insensitive_compare',0x15b48,0x15b8d,0x11ee)]:
    p=a
    for ins in Decoder(16,b[a:e],ip=a-cs*16):
        assert not ins.is_invalid;rows.append(dict(block=name,image_offset=p,cs=cs,ip=ins.ip,bytes=b[p:p+ins.len].hex(),instruction=fmt.format(ins)));p+=ins.len
    assert p==e
out.mkdir(parents=True,exist_ok=True)
for name,data in [('data_fields',fields),('instructions',rows)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
s=dict(image_sha256=sha(b),pointer_fields=4,text_fields=4,typed_bytes=sum(f['length'] for f in fields),selector_has_local_bounds_check=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
