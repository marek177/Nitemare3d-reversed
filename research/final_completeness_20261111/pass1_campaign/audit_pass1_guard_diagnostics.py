"""python audit_pass1_guard_diagnostics.py IMAGE INVENTORY DECODER OUT"""
import csv,hashlib,json,re,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,OpKind
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
spec=[('guard_status_format',0x28b53,0x28bac,0x83d,0xd8b,0x83d,0xd93,0x11ee,0x278c),('guard_problem_format',0x281f4,0x2822c,0x4c7,0x15ba,0x4c7,0x15bd,0x11ee,0x7e0),('tile_width_label',0x27a8a,0x27a90,0x277,0x551,0x277,0x578,0xfba,0xc),('tile_shape_error_format',0x27a90,0x27aba,0x277,0x554,0x277,0x578,0xfba,0xc)]
fields=[];catalog=[]
for name,a,e,cs,push,callcs,call,targetcs,targetip in spec:
    raw=b[a:e];assert raw[-1]==0 and b'\0' not in raw[:-1];text=raw[:-1].decode('ascii');r=lookup[(cs,push)];i=Decoder(16,bytes.fromhex(r['bytes']),ip=push).decode();assert i.op0_kind==OpKind.IMMEDIATE16 and i.immediate16==a-0x27710
    r=lookup[(callcs,call)];j=Decoder(16,bytes.fromhex(r['bytes']),ip=call).decode();assert j.op0_kind==OpKind.FAR_BRANCH16 and (j.far_branch_selector,j.far_branch16)==(targetcs,targetip)
    fields.append(dict(name=name,start=a,end_exclusive=e,length=e-a,type='NUL_ASCII_diagnostic_literal',status='PARTIAL',range_sha256=sha(raw)))
    catalog.append(dict(name=name,start=a,end_exclusive=e,text=text,push_cs=cs,push_ip=push,call_cs=callcs,call_ip=call,target_cs=targetcs,target_ip=targetip,conversions=';'.join(re.findall(r'%[dsx]',text)),scope='static call/data evidence; diagnostics not executed'))
contexts=[]
for r in old:
    if any(r['cs']==cs and a<=r['ip']<e for cs,a,e in [(0x83d,0xd51,0xda9),(0x4c7,0x15a1,0x15d7),(0x277,0x53a,0x584)]):
        raw=bytes.fromhex(r['bytes']);assert b[r['image_offset']:r['image_offset']+len(raw)]==raw;i=Decoder(16,raw,ip=r['ip']).decode();assert not i.is_invalid and i.len==len(raw);contexts.append(dict(cs=r['cs'],ip=r['ip'],image_offset=r['image_offset'],bytes=raw.hex(),instruction=fmt.format(i)))
roles=[dict(record='record26',offset=off,width=width,role=role,consumer=consumer) for off,width,role,consumer in [(6,2,'WORD formatted as signed timer via diagnostic %d','083D:0D64'),(10,1,'zero-extended BYTE formatted as strategy','083D:0D72'),(11,1,'zero-extended BYTE formatted as state','083D:0D6D;04C7:15B5'),(12,1,'zero-extended BYTE formatted as nextstate','083D:0D68;04C7:15B0'),(13,1,'zero-extended BYTE formatted as o_id hexadecimal; distinct from linked-object WORD at +8','04C7:15A9'),(16,1,'zero-extended BYTE formatted as strength','083D:0D77'),(17,1,'zero-extended BYTE formatted as octant','083D:0D5F'),(18,1,'zero-extended BYTE formatted as resoct','083D:0D58')]]
assert sum(f['length'] for f in fields)==193
for name,rows in [('data_fields',fields),('format_catalog',catalog),('instruction_contexts',contexts),('consumer_field_roles',roles)]:save(name,rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=193,fields=len(fields),record_field_observations=len(roles),verified_context_instructions=len(contexts),scope='specific diagnostic literal operands and guarded caller contexts; record roles from format argument order and actual memory widths; no complete AI/renderer function or diagnostics execution',natural_guard_invariants_closed=False,tile_validator_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
