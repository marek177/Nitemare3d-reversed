"""python audit_pass1_calendar.py IMAGE DECODER_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
entries=[]
for name,start,days,status in [('common',0x29b98,[31,28,31,30,31,30,31,31,30,31,30,31],'PARTIAL'),('leap_candidate',0x29b7e,[31,29,31,30,31,30,31,31,30,31,30,31],'CLASSIFIED ONLY')]:
    values=[-1]
    for n in days:values.append(values[-1]+n)
    actual=list(struct.unpack_from('<13h',b,start));assert actual==values
    for i,v in enumerate(values):entries.append(dict(table=name,index=i,image_offset=start+i*2,value=v,formula='sum(month_lengths[:index])-1',status=status))
fields=[dict(name='common_year_cumulative_days_minus_one',start=0x29b98,end_exclusive=0x29bb2,length=26,type='signed_WORD[13]',status='PARTIAL',range_sha256=sha(b[0x29b98:0x29bb2]))]
for p,h in {0x14a45:'8d77ff',0x14a4b:'03f6',0x14a4d:'03948824',0x14a54:'f6c103',0x14a59:'83fb02',0x14a5e:'42',0x14c25:'8b878824',0x14c35:'8b878a24'}.items():assert b[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
rows=[];fmt=Formatter(FormatterSyntax.INTEL)
for a,e in [(0x14a3d,0x14a62),(0x14c20,0x14c45)]:
    p=a
    for ins in Decoder(16,b[a:e],ip=a-0x11ee0):
        assert not ins.is_invalid;rows.append(dict(image_offset=p,cs=0x11ee,ip=ins.ip,bytes=b[p:p+ins.len].hex(),instruction=fmt.format(ins)));p+=ins.len
    assert p==e
out.mkdir(parents=True,exist_ok=True)
for name,data in [('data_fields',fields),('calendar_entries',entries),('instructions',rows)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
s=dict(image_sha256=sha(b),typed_bytes=26,formula_verified_words=26,leap_candidate_promoted=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
