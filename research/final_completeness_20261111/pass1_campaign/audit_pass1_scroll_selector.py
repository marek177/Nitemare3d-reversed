"""python audit_pass1_scroll_selector.py IMAGE DECODER_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rel={int(r['image_offset']):int(r['original_word']) for r in csv.DictReader((image.parent/'relocations.csv').open())}
fields=[]
def add(name,a,e,t):fields.append(dict(name=name,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e])))
for name,offset,text in [('scroll0',0x1174,b'\n   \"01532\"\0'),('scroll1',0x1178,b'\n   \"080993\"\0'),('scroll2',0x117c,b'\n   \"372535\"\0')]:
    a=0x27710+offset;o,s=struct.unpack_from('<HH',b,a);assert rel[a+2]==s==0x2771;t=s*16+o;assert b[t:t+len(text)]==text
    add(name+'_pointer',a,a+4,'FAR16_text_pointer');add(name+'_text',t,t+len(text),'NUL_terminated_ASCII')
a=0x27710+0x15b4;text=b'The scroll says:\n%s\0';assert b[a:a+len(text)]==text;add('scroll_format',a,a+len(text),'NUL_terminated_ASCII_format')
for p,h in {0xabd8:'8b5e06',0xabdb:'c1e302',0xabde:'66ffb77411',0xabe3:'68b415',0xabeb:'9a8c27ee11'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
rows=[];fmt=Formatter(FormatterSyntax.INTEL);p=0xabd4
for ins in Decoder(16,b[p:0xac00],ip=p-0x83d0):
    assert not ins.is_invalid;rows.append(dict(image_offset=p,cs=0x83d,ip=ins.ip,bytes=b[p:p+ins.len].hex(),instruction=fmt.format(ins)));p+=ins.len
assert p==0xac00
out.mkdir(parents=True,exist_ok=True)
for name,data in [('data_fields',fields),('instructions',rows)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
s=dict(image_sha256=sha(b),pointer_fields=3,text_fields=4,typed_bytes=sum(f['length'] for f in fields),selector_has_local_bounds_check=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
