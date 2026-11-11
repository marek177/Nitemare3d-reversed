"""python audit_pass1_io_argument_strings.py IMAGE INVENTORY DECODER_DIR OUT"""
import csv,hashlib,json,re,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());fields={};refs=[]
def constant_push(r):return r['mnemonic']=='push' and re.fullmatch('0x[0-9a-f]+',r['operands'])
def verify(seq):
    for j,r in enumerate(seq):
        p=r['image_offset'];raw=bytes.fromhex(r['bytes']);assert b[p:p+len(raw)]==raw and p==r['cs']*16+r['ip'];ins=Decoder(16,raw,ip=r['ip']).decode();assert not ins.is_invalid and ins.len==len(raw)
        if j:assert seq[j-1]['image_offset']+len(bytes.fromhex(seq[j-1]['bytes']))==p
def add(r,call,role,fmt=''):
    offset=int(r['operands'],16);a=0x27710+offset;assert 0x27710<=a<len(b);e=b.index(0,a)+1;assert all(32<=v<127 for v in b[a:e-1])
    fields[a]=dict(name='io_argument_'+hex(a)[2:],start=a,end_exclusive=e,length=e-a,type='NUL_ASCII_near_DS_string',status='PARTIAL',range_sha256=sha(b[a:e]))
    refs.append(dict(text_start=a,text_end_exclusive=e,text=b[a:e-1].decode('ascii'),role=role,push_image=r['image_offset'],push_bytes=r['bytes'],call_image=call['image_offset'],call_bytes=call['bytes'],format=fmt))
for i,call in enumerate(old):
    if i<1 or call['mnemonic']!='lcall':continue
    last=old[i-1]
    if call['operands']=='0x11ee, 0x1c72' and constant_push(last):
        a=0x27710+int(last['operands'],16)
        if a>=len(b):continue # runtime filename buffer, not file-backed object
        assert b[call['image_offset']:call['image_offset']+5]==bytes.fromhex('9a721cee11')
        verify([last,call]);add(last,call,'CRT_open_filename')
    if call['operands']!='0xfba, 0xc' or i<2:continue
    value=old[i-2]
    if not constant_push(last) or not constant_push(value):continue
    a=0x27710+int(last['operands'],16);fmt=b[a:b.index(0,a)]
    if fmt.count(b'%')!=1 or b'%s' not in fmt:continue
    if 0x27710+int(value['operands'],16)>=len(b):continue
    assert b[call['image_offset']:call['image_offset']+5]==bytes.fromhex('9a0c00ba0f')
    verify([value,last,call]);add(value,call,'single_percent_s_error_argument',fmt.decode('ascii'))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('data_fields',sorted(fields.values(),key=lambda r:r['start'])),('argument_references',refs)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),strings=len(fields),references=len(refs),typed_bytes=sum(f['length'] for f in fields.values()),runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
