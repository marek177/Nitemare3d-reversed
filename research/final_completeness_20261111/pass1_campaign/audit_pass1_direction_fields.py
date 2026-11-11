"""python audit_pass1_direction_fields.py IMAGE INVENTORY DECODER_DIR OUT"""
import csv,hashlib,json,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,Register
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());fmt=Formatter(FormatterSyntax.INTEL)
spec=[(0xca,0,0xe2c,'direction_step_first'),(0xd2,0,0xe3b,'direction_step_second'),(0xac2,0x4c7,0x238,'scaled_direction_first'),(0xaca,0x4c7,0x246,'scaled_direction_second'),(0xad4,0x4c7,0xc57,'object_direction_step_first'),(0xadc,0x4c7,0xc63,'object_direction_step_second'),(0x20a6,0xfd9,0x4a1,'renderer_direction_flag_0'),(0x20ae,0xfd9,0x4a8,'renderer_direction_flag_1'),(0x20b6,0xfd9,0x4af,'renderer_direction_flag_2'),(0x20be,0xfd9,0x4b6,'renderer_direction_flag_3')]
fields=[];refs=[];context=[]
for off,cs,ip,name in spec:
    a=0x27710+off;e=a+8;v=b[a:e]
    fields.append(dict(name=name,start=a,end_exclusive=e,length=8,type='BYTE_array_8_nominal_extent',status='PARTIAL',range_sha256=sha(v)))
    r=next(r for r in old if r['cs']==cs and r['ip']==ip);raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw
    i=Decoder(16,raw,ip=ip).decode();assert not i.is_invalid and i.len==len(raw) and i.memory_displacement==off and i.memory_segment==Register.DS and i.memory_base in (Register.BX,Register.SI)
    refs.append(dict(name=name,ds_offset=off,cs=cs,ip=ip,image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i),unsigned_values=' '.join(str(x) for x in v),signed_byte_interpretation=' '.join(str(x if x<128 else x-256) for x in v),index_bound_closed=False))
    ordered=sorted((r for r in old if r['cs']==cs),key=lambda r:r['ip']);n=next(n for n,r in enumerate(ordered) if r['ip']==ip)
    for r in ordered[max(0,n-3):n+4]:
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw
        i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw)
        context.append(dict(field=name,cs=cs,ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
assert b[0x277da:0x277ea]==b[0x281e4:0x281f4]
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('data_fields',fields),('consumers',refs),('consumer_context',context)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),nominal_fields=10,typed_bytes=80,verified_primary_consumers=10,index_bounds_closed=False,all_consumers_closed=False,natural_runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
