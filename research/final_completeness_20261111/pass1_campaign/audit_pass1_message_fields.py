"""python audit_pass1_message_fields.py IMAGE INVENTORY DECODER_DIR OUT"""
import csv,hashlib,json,re,struct,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,Register
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());rel={int(r['image_offset']):int(r['original_word']) for r in csv.DictReader((image.parent/'relocations.csv').open())}
fields={};refs=[];fmt=Formatter(FormatterSyntax.INTEL)
def add(name,a,e,t):
    if a in fields:assert fields[a]['end_exclusive']==e;return
    fields[a]=dict(name=name,start=a,end_exclusive=e,length=e-a,type=t,status='PARTIAL',range_sha256=sha(b[a:e]))
for i,r in enumerate(old[:-1]):
    match=re.fullmatch(r'dword ptr \[0x([0-9a-f]+)\]',r['operands'])
    if r['mnemonic']!='push' or not match:continue
    call=old[i+1]
    if call['mnemonic']!='lcall' or call['operands']!='0xd29, 0x750':continue
    offset=int(match.group(1),16);a=0x27710+offset;o,s=struct.unpack_from('<HH',b,a)
    assert s==0x2771 and rel[a+2]==s
    t=s*16+o;e=b.index(0,t)+1;assert all(v in (10,13) or 32<=v<127 for v in b[t:e-1])
    for x in [r,call]:
        p=x['image_offset'];code=bytes.fromhex(x['bytes']);assert p==x['cs']*16+x['ip'] and b[p:p+len(code)]==code
        ins=Decoder(16,code,ip=x['ip']).decode();assert not ins.is_invalid and ins.len==len(code)
    ins=Decoder(16,bytes.fromhex(r['bytes']),ip=r['ip']).decode();assert ins.memory_segment==Register.DS and ins.memory_base==Register.NONE and ins.memory_index==Register.NONE
    add('message_pointer_'+hex(a)[2:],a,a+4,'FAR16_text_pointer')
    add('message_text_'+hex(t)[2:],t,e,'NUL_terminated_ASCII_with_LF')
    refs.append(dict(pointer_start=a,text_start=t,text_end_exclusive=e,text=b[t:e-1].decode('ascii'),push_image=r['image_offset'],push_bytes=r['bytes'],call_image=call['image_offset'],call_bytes=call['bytes'],cs=r['cs'],ip=r['ip'],instruction=fmt.format(ins),scope='direct DWORD push to FAR message helper; inherited DS and full renderer ABI open'))
assert len(refs)==12
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('data_fields',sorted(fields.values(),key=lambda f:f['start'])),('message_references',refs)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),message_calls=len(refs),fields=len(fields),typed_bytes=sum(f['length'] for f in fields.values()),runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
