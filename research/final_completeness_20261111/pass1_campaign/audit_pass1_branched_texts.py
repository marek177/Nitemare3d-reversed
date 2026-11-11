"""python audit_pass1_branched_texts.py IMAGE DECODER_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rel={int(r['image_offset']):int(r['original_word']) for r in csv.DictReader((image.parent/'relocations.csv').open())}
fields=[];refs=[]
for offset,push,target in [(0xe88,0xa74a,0xa757),(0xf52,0xa87d,0xa8cc),(0x114a,0x933f,0x9369),(0x10ee,0x92fe,0x9303)]:
    assert b[push:push+5]==b'\x66\xff\x36'+offset.to_bytes(2,'little')
    assert b[target:target+5]==(bytes.fromhex('9abc06290d') if offset==0x10ee else bytes.fromhex('9a2007290d'))
    a=0x27710+offset;o,s=struct.unpack_from('<HH',b,a);assert rel[a+2]==s==0x2771;t=s*16+o;e=b.index(0,t)+1
    assert all(v in (10,13) or 32<=v<127 for v in b[t:e-1])
    for name,x,y,typ in [('pointer',a,a+4,'FAR16_text_pointer'),('text',t,e,'NUL_terminated_ASCII')]:fields.append(dict(name=name+'_'+hex(x)[2:],start=x,end_exclusive=y,length=y-x,type=typ,status='PARTIAL',range_sha256=sha(b[x:y])))
    refs.append(dict(pointer_start=a,text_start=t,text_end_exclusive=e,text=b[t:e-1].decode('ascii'),push_image=push,call_image=target))
for p,h in {0xa74f:'eb06',0xa882:'eb48',0x9344:'eb23',0xd959:'66ff7606',0xd95e:'e85dfe'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
rows=[];fmt=Formatter(FormatterSyntax.INTEL)
for a,e,cs in [(0xa74a,0xa75e,0x83d),(0xa87d,0xa884,0x83d),(0xa8cc,0xa8d4,0x83d),(0x933f,0x9346,0x83d),(0x9364,0x9371,0x83d),(0x92f8,0x930b,0x83d),(0xd94c,0xd964,0xd29)]:
    p=a
    for ins in Decoder(16,b[a:e],ip=a-cs*16):
        assert not ins.is_invalid;rows.append(dict(image_offset=p,cs=cs,ip=ins.ip,bytes=b[p:p+ins.len].hex(),instruction=fmt.format(ins)));p+=ins.len
    assert p==e
out.mkdir(parents=True,exist_ok=True)
for name,data in [('data_fields',fields),('text_references',refs),('instructions',rows)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
s=dict(image_sha256=sha(b),fields=len(fields),typed_bytes=sum(f['length'] for f in fields),runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
