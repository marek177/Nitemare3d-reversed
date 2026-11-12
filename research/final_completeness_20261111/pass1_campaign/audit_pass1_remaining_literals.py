"""python audit_pass1_remaining_literals.py IMAGE INVENTORY DECODER OUT"""
import csv,hashlib,json,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,OpKind
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
groups=[('order_ui',0x294f1,0x2953d,0xd29,[0x151d,0x1532,0x1535]),('slot_formats',0x293e5,0x29417,0xd29,[0xa95,0xac8,0xafc,0xb2e,0xb64,0xc20,0xc52,0xf76,0x1188]),('resource_filenames',0x28d73,0x28da2,0x83d,[0x2a56,0x2a6e,0x2aa3,0x2ab1,0x2abf]),('config_formats',0x281af,0x281d1,0x476,[0x342,0x3df,0x405,0x41d,0x426,0x42f,0x438,0x46c,0x486,0x4bf]),('hud_formats',0x28b2d,0x28b4d,0x83d,[0x659,0x6a2,0x71d,0x772,0x7c4,0x819,0xab6]),('ending_filename_mode',0x28cfb,0x28d09,0x83d,[0x28d8,0x28fb])]
fields=[];texts=[];anchors=[]
for role,start,end,cs,ips in groups:
    p=start;count=0
    while p<end:
        e=b.index(0,p)+1;assert e<=end and count<len(ips);raw=b[p:e];text=raw[:-1].decode('ascii');ip=ips[count];r=lookup[(cs,ip)];iraw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(iraw)]==iraw
        i=Decoder(16,iraw,ip=ip).decode();assert not i.is_invalid and i.len==len(iraw) and any(i.op_kind(k)==OpKind.IMMEDIATE16 for k in range(i.op_count)) and i.immediate16==p-0x27710
        fields.append(dict(name=role+'_'+format(p,'05x'),start=p,end_exclusive=e,length=e-p,type='NUL_ASCII_literal_with_specific_consumer',status='PARTIAL',range_sha256=sha(raw)))
        texts.append(dict(start=p,end_exclusive=e,group=role,text=text,reference_cs=cs,reference_ip=ip,instruction=fmt.format(i)))
        anchors.append((cs,ip));count+=1;p=e
    assert p==end and count==len(ips)
assert b[0x28b2c]==1
fields.append(dict(name='hud_initial_draw_flag',start=0x28b2c,end_exclusive=0x28b2d,length=1,type='mutable_BYTE_initial_one_test_and_clear',status='PARTIAL',range_sha256=sha(b[0x28b2c:0x28b2d])));anchors.extend([(0x83d,0x5d8),(0x83d,0x5e1)])
assert sum(f['length'] for f in fields)==254
contexts=[]
for r in old:
    if not any(r['cs']==cs and ip-8<=r['ip']<=ip+36 for cs,ip in anchors):continue
    raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);contexts.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i),scope='selected consumer context only; not full functions'))
for name,rows in [('data_fields',fields),('text_catalog',texts),('instruction_contexts',contexts)]:save(name,rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=254,fields=len(fields),strings=len(texts),verified_context_instructions=len(contexts),scope='exact NUL fields and specific operand/consumer contexts; one BYTE test/clear; no printing, shell execution, resource loading or UI execution',natural_callers_closed=False,file_formats_closed=False,padding_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
