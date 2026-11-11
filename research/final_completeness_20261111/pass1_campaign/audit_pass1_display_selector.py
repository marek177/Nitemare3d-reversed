"""python audit_pass1_display_selector.py IMAGE DECODER_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rel={int(r['image_offset']):int(r['original_word']) for r in csv.DictReader((image.parent/'relocations.csv').open())};fields=[];refs=[]
for off in [0xe1e,0xe22,0xe26,0xe2a,0x1378]:
    p=0x27710+off;o,s=struct.unpack_from('<HH',b,p);assert rel[p+2]==s==0x2771;t=s*16+o;e=b.index(0,t)+1;assert all(32<=x<127 for x in b[t:e-1])
    for name,a,z,typ in [('pointer',p,p+4,'FAR16_display_text_pointer'),('text',t,e,'NUL_terminated_ASCII')]:fields.append(dict(name=name+'_'+hex(a)[2:],start=a,end_exclusive=z,length=z-a,type=typ,status='PARTIAL',range_sha256=sha(b[a:z])))
    refs.append(dict(ds_ss_offset=off,pointer_start=p,text_start=t,text_end_exclusive=e,text=b[t:e-1].decode('ascii'),scope='DS demo or SS selector -> runtime display slot -> renderer; natural DS/SS equality open'))
for p,h in {0xa436:'a17813',0xa439:'8b167a13',0xa43d:'a3d83c',0xa440:'8916da3c',0xa47e:'807c0302',0xa482:'7219',0xa484:'807c0305',0xa488:'7713',0xa48f:'c1e302',0xa492:'66368b87160e',0xa498:'6636a3d83c',0x8d53:'66ff36d83c',0x8d5e:'9ae003290d'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
rows=[];fmt=Formatter(FormatterSyntax.INTEL)
for a,e in [(0xa429,0xa444),(0xa47e,0xa4a2),(0x8d3f,0x8d66)]:
    p=a
    for ins in Decoder(16,b[a:e],ip=a-0x83d0):
        assert not ins.is_invalid;rows.append(dict(image_offset=p,cs=0x83d,ip=ins.ip,bytes=b[p:p+ins.len].hex(),instruction=fmt.format(ins)));p+=ins.len
    assert p==e
out.mkdir(parents=True,exist_ok=True)
for name,data in [('data_fields',fields),('text_references',refs),('instructions',rows)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
s=dict(image_sha256=sha(b),fields=len(fields),typed_bytes=sum(f['length'] for f in fields),selector_index_min=2,selector_index_max=5,runtime_display_slot_image=0x2b3e8,runtime_display_slot_in_file=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
