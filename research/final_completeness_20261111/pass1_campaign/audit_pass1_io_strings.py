"""python audit_pass1_io_strings.py IMAGE DECODER_DIR OUT"""
import csv,hashlib,json,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
spec=[(0x1ae,0x2807,'open_filename'),(0x1b6,0x2819,'error_filename'),(0x1be,0x281c,'error_format'),(0x1d4,0x284e,'error_filename'),(0x1dc,0x2851,'error_format'),(0x679,0x3ee9,'open_filename'),(0x681,0x3efb,'error_filename'),(0x689,0x3efe,'error_format'),(0x69f,0x3f20,'error_filename'),(0x6a7,0x3f23,'error_format'),(0x6f2,0x40e5,'open_filename'),(0x6fa,0x40f7,'error_filename'),(0x702,0x40fa,'error_format'),(0x718,0x4144,'error_filename'),(0x720,0x4147,'error_format')]
fields=[];refs=[];rows=[];fmt=Formatter(FormatterSyntax.INTEL)
for offset,p,role in spec:
    assert b[p:p+3]==b'\x68'+offset.to_bytes(2,'little')
    a=0x27710+offset;e=b.index(0,a)+1;assert all(32<=v<127 for v in b[a:e-1])
    fields.append(dict(name=role+'_'+hex(a)[2:],start=a,end_exclusive=e,length=e-a,type='NUL_terminated_ASCII_near_DS',status='PARTIAL',range_sha256=sha(b[a:e])))
    refs.append(dict(text_start=a,text_end_exclusive=e,text=b[a:e-1].decode('ascii'),role=role,push_image=p,near_ds_offset=offset))
    cs=0x277;ins=Decoder(16,b[p:p+3],ip=p-cs*16).decode();assert ins.len==3 and not ins.is_invalid
    rows.append(dict(image_offset=p,cs=cs,ip=ins.ip,bytes=b[p:p+3].hex(),instruction=fmt.format(ins)))
for p,h in {0x13b7b:'8b5606',0x13b82:'b43d',0x13b84:'cd21',0x280a:'9a721cee11',0x3eec:'9a721cee11',0x40e8:'9a721cee11'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
p=0x13b7b
for ins in Decoder(16,b[p:0x13b86],ip=p-0x11ee0):
    assert not ins.is_invalid;rows.append(dict(image_offset=p,cs=0x11ee,ip=ins.ip,bytes=b[p:p+ins.len].hex(),instruction=fmt.format(ins)));p+=ins.len
assert p==0x13b86
out.mkdir(parents=True,exist_ok=True)
for name,data in [('data_fields',fields),('text_references',refs),('instructions',rows)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
s=dict(image_sha256=sha(b),strings=len(fields),typed_bytes=sum(f['length'] for f in fields),runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
