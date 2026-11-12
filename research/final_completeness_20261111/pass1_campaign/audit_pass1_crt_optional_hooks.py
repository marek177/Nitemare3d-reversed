"""python audit_pass1_crt_optional_hooks.py IMAGE INVENTORY DECODER OUT"""
import csv,hashlib,json,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
fields=[dict(name=n,start=a,end_exclusive=a+4,length=4,type=t,status='PARTIAL',range_sha256=sha(b[a:a+4])) for n,a,t in [('crt_optional_action0_value',0x29c56,'WORD_pair_initial_zero_loaded_AX_DX_for_callback_BX0_32bit_semantics_open'),('crt_optional_action3_value',0x29c5a,'WORD_pair_initial_zero_loaded_AX_DX_for_callback_BX3_32bit_semantics_open'),('crt_optional_tail_dispatch',0x29c62,'mutable_FAR16_pointer_initial_zero_segment_zero_disables')]]
for f in fields:assert not any(b[f['start']:f['end_exclusive']])
expected={0x13b:'8b0e4425',0x141:'8e061e21',0x145:'268b362c00',0x14a:'a14625',0x14d:'8b164825',0x151:'33db',0x153:'ff1e4225',0x15c:'a14a25',0x15f:'8b164c25',0x163:'bb0300',0x166:'ff1e4225',0x397a:'8b0e5425',0x3980:'ff2e5225',0x3984:'b8ffff',0x3987:'c70618211600'}
for ip,raw in expected.items():assert lookup[(0x11ee,ip)]['bytes']==raw and b[0x11ee0+ip:0x11ee0+ip+len(bytes.fromhex(raw))]==bytes.fromhex(raw)
contexts=[]
for r in old:
    if r['cs']==0x11ee and any(a<=r['ip']<e for a,e in [(0x13b,0x16a),(0x1d5,0x1e8),(0x215,0x249),(0x28b,0x29e),(0x397a,0x3990)]):
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);contexts.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i),scope='selected local hook consumer context; not complete startup/termination'))
save('data_fields',fields);save('instruction_contexts',contexts)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=12,fields=3,verified_context_instructions=len(contexts),scope='static exact operand widths and optional callback register arguments; two WORD pairs with higher-level meaning unresolved; no callback or startup executed',optional_callback_semantics_closed=False,startup_closed=False,tail_fallback_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))

