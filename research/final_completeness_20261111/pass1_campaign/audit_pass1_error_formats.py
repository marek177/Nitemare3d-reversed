"""python audit_pass1_error_formats.py IMAGE INVENTORY DECODER_DIR OUT"""
import csv,hashlib,json,re,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());fields={};refs=[];skipped=[];fmt=Formatter(FormatterSyntax.INTEL)
for i,call in enumerate(old):
    if call['mnemonic']!='lcall' or call['operands']!='0xfba, 0xc':continue
    previous=old[i-1] if i else None
    if previous is None or previous['mnemonic']!='push' or not re.fullmatch('0x[0-9a-f]+',previous['operands']):
        skipped.append(dict(call_image=call['image_offset'],reason='not adjacent constant PUSH; needs stack-flow analysis'));continue
    p=previous['image_offset'];code=bytes.fromhex(previous['bytes']);assert p+len(code)==call['image_offset']
    for r in [previous,call]:
        a=r['image_offset'];raw=bytes.fromhex(r['bytes']);assert b[a:a+len(raw)]==raw and a==r['cs']*16+r['ip']
        ins=Decoder(16,raw,ip=r['ip']).decode();assert not ins.is_invalid and ins.len==len(raw)
    assert b[call['image_offset']:call['image_offset']+5]==bytes.fromhex('9a0c00ba0f')
    offset=int(previous['operands'],16);a=0x27710+offset;assert 0x27710<=a<len(b);e=b.index(0,a)+1
    assert all(v in (9,10,13) or 32<=v<127 for v in b[a:e-1])
    fields[a]=dict(name='error_format_'+hex(a)[2:],start=a,end_exclusive=e,length=e-a,type='NUL_ASCII_error_format_near_DS',status='PARTIAL',range_sha256=sha(b[a:e]))
    refs.append(dict(format_start=a,format_end_exclusive=e,text=b[a:e-1].decode('ascii'),push_image=p,push_bytes=previous['bytes'],call_image=call['image_offset'],call_bytes=call['bytes'],cs=previous['cs'],ip=previous['ip'],scope='adjacent final format PUSH to error helper; inherited DS remains conditional'))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('data_fields',sorted(fields.values(),key=lambda r:r['start'])),('format_references',refs)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),formats=len(fields),calls=len(refs),typed_bytes=sum(r['length'] for r in fields.values()),skipped_calls=skipped,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps({k:v for k,v in s.items() if k!='skipped_calls'},indent=2));print('skipped calls:',len(skipped))
