"""python audit_pass1_split_strings.py IMAGE DECODER_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rel={int(r['image_offset']):int(r['original_word']) for r in csv.DictReader((image.parent/'relocations.csv').open())}
fields=[];refs=[];instructions=[];fmt=Formatter(FormatterSyntax.INTEL)
for p,offset in [(0xa76c,0xf28),(0xa79e,0xd72),(0xa7d6,0xd8c),(0xa80e,0xda4),(0xa846,0xdbe)]:
    assert b[p:p+4]==b'\x8b\x1e'+offset.to_bytes(2,'little')
    assert b[p+4:p+8]==b'\x8b\x0e'+(offset+2).to_bytes(2,'little')
    assert b[p+8:p+16]==bytes.fromhex('8bfb8db6fefe8ec1')
    a=0x27710+offset;o,s=struct.unpack_from('<HH',b,a);assert rel[a+2]==s==0x2771
    t=s*16+o;e=b.index(0,t)+1;assert all(v in (10,13) or 32<=v<127 for v in b[t:e-1])
    for name,x,y,typ in [('split_pointer',a,a+4,'FAR16_text_pointer'),('split_text',t,e,'NUL_terminated_ASCII')]:
        fields.append(dict(name=name+'_'+hex(x)[2:],start=x,end_exclusive=y,length=y-x,type=typ,status='PARTIAL',range_sha256=sha(b[x:y])))
    end=p+(24 if p==0xa76c else 22);pos=p
    for ins in Decoder(16,b[p:end],ip=p-0x83d0):
        assert not ins.is_invalid;instructions.append(dict(image_offset=pos,cs=0x83d,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)));pos+=ins.len
    assert pos==end and b[end-2:end]==bytes.fromhex('f2ae')
    refs.append(dict(pointer_start=a,text_start=t,text_end_exclusive=e,text=b[t:e-1].decode('ascii'),window_start=p,window_end_exclusive=end,scope='split WORD loads -> ES:DI -> REPNE SCASB; natural DS/DF and buffer bounds open'))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('data_fields',fields),('text_references',refs),('instructions',instructions)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),pointer_fields=5,text_fields=5,typed_bytes=sum(f['length'] for f in fields),runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
