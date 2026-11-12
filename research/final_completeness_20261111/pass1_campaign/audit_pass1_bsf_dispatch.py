"""python audit_pass1_bsf_dispatch.py IMAGE INVENTORY DECODER OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
out.mkdir(parents=True,exist_ok=True);old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
def save(name,rs):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
table=struct.unpack_from('<6H',b,0x83d0+0x29e0);assert table==(0x29f2,0x2a7c,0x2a90,0x2a9a,0x2aa8,0x2ab6)
save('switch_table',[dict(mode=k,table_image=0x83d0+0x29e0+2*k,target_cs=0x83d,target_ip=t,target_image=0x83d0+t) for k,t in enumerate(table)])
todo=[0x29ca];decoded={};edges=[]
while todo:
    ip=todo.pop()
    if ip in decoded:continue
    assert 0x29ca<=ip<0x2ad7 and not 0x29e0<=ip<0x29ec;i=Decoder(16,b[0x83d0+ip:0x83d0+0x2ad7],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control==FlowControl.INDIRECT_BRANCH:
        assert ip==0x29da
        for t in table:todo.append(t);edges.append(dict(source=ip,target=t,kind='switch'))
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target);edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH,FlowControl.INDIRECT_BRANCH):todo.append(i.next_ip);edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_call_return'))
rows=[]
for ip,i in sorted(decoded.items()):
    raw=b[0x83d0+ip:0x83d0+i.next_ip];assert lookup[(0x83d,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x83d,ip=ip,image_offset=0x83d0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
save('bsf_mode_dispatch',rows);save('cfg_edges',edges)
fields=[]
for off,expected,role in [(0x161c,b'rb\0','stream_mode'),(0x161f,b'nite3d.bsf\0','filename')]:
    a=0x27710+off;assert b[a:a+len(expected)]==expected
    fields.append(dict(name='bsf_'+role,start=a,end_exclusive=a+len(expected),length=len(expected),type='NUL_ASCII_'+role,status='PARTIAL',range_sha256=sha(expected)))
save('data_fields',fields)
covered={p for row in rows for p in range(row['image_offset'],row['image_offset']+len(bytes.fromhex(row['bytes'])))}
gaps=[dict(image_offset=p,byte=b[p],kind='switch_WORD_table' if 0x83d0+0x29e0<=p<0x83d0+0x29ec else 'unreached_in_this_CFG') for p in range(0x83d0+0x29ca,0x83d0+0x2ad7) if p not in covered]
save('noninstruction_bytes',gaps)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),typed_bytes=14,fields=2,functions=[dict(name='bsf_mode_dispatch',start=0x83d0+0x29ca,end_exclusive=0x83d0+0x2ad7,instruction_bytes=sum(len(bytes.fromhex(row['bytes'])) for row in rows),instructions=len(rows))],switch_entries=len(table),scope='static complete local CFG with explicit six-entry CS jump table; callee effects, file I/O, caller modes and natural reachability open',runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
