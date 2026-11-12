"""python audit_bsf_callers.py IMAGE INVENTORY DECODER OUT"""
import csv,hashlib,json,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True);rows=[];calls=[]
for r in old:
    if r['mnemonic']!='lcall' or r['operands']!='0x83d, 0x29ca':continue
    assert bytes.fromhex(r['bytes'])==bytes.fromhex('9aca293d08')
    prior=[x for x in old if x['cs']==r['cs'] and x['ip']+len(bytes.fromhex(x['bytes']))==r['ip']];assert len(prior)==1
    calls.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],argument_instruction=prior[0]['mnemonic']+' '+prior[0]['operands']))
    for x in old:
        if x['cs']==r['cs'] and r['ip']-12<=x['ip']<r['ip']+18:
            raw=bytes.fromhex(x['bytes']);assert b[x['image_offset']:x['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=x['ip']).decode();assert not i.is_invalid and i.len==len(raw)
            rows.append(dict(caller_cs=r['cs'],caller_ip=r['ip'],cs=x['cs'],ip=x['ip'],image_offset=x['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
for name,rs in [('callers',calls),('caller_contexts',rows)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
(out/'caller_summary.json').write_text(json.dumps(dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),direct_callers=len(calls),context_rows=len(rows),scope='supplied inventory only; dynamic callers and calls outside inventory not excluded'),indent=2)+'\n');print(len(calls),len(rows))
