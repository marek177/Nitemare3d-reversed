"""python audit_pass1_crt_program_pointer.py IMAGE DECODER_DIR OUT"""
import csv,hashlib,json,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rel={int(r['image_offset']):int(r['original_word']) for r in csv.DictReader((image.parent/'relocations.csv').open())}
assert b[0x29854:0x29859]==bytes.fromhex('4821712700') and rel[0x29856]==0x2771
for p,h in {0x12204:'268e062c00',0x12209:'8c064621',0x1221c:'893e4421',0x122d2:'c5364421',0x122d6:'ac',0x122d7:'aa'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
fields=[dict(name=name,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e])) for name,a,e,t in [('crt_program_name_pointer',0x29854,0x29858,'mutable_FAR16_string_pointer'),('initial_empty_program_name',0x29858,0x29859,'NUL_empty_string')]]
rows=[];fmt=Formatter(FormatterSyntax.INTEL)
for name,a,e in [('initializer',0x121f6,0x12229),('pointer_consumer',0x122d2,0x122dc)]:
    pos=a
    for ins in Decoder(16,b[a:e],ip=a-0x11ee0):
        assert not ins.is_invalid;rows.append(dict(block=name,image_offset=pos,cs=0x11ee,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)));pos+=ins.len
    assert pos==e
out.mkdir(parents=True,exist_ok=True)
for name,data in [('data_fields',fields),('instructions',rows)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
s=dict(image_sha256=sha(b),typed_bytes=5,initial_pointer='2771:2148',runtime_pointer_writer=True,all_callers_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
