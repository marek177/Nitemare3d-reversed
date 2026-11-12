"""python audit_pass1_statistics_formats.py IMAGE INVENTORY DECODER OUT"""
import csv,hashlib,json,re,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,OpKind
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
lookup={(r['cs'],r['ip']):r for r in json.loads(inventory.read_text())};fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
def save(name,rows):
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
todo=[0x1d0];decoded={}
while todo:
    ip=todo.pop()
    if ip in decoded:continue
    assert 0x1d0<=ip<0x313;i=Decoder(16,b[0x4760+ip:0x4a73],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.near_branch_target)
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):todo.append(i.next_ip)
rows=[];calls=[]
for ip,i in sorted(decoded.items()):
    raw=b[0x4760+ip:0x4760+i.next_ip];assert lookup[(0x476,ip)]['bytes']==raw.hex();rows.append(dict(cs=0x476,ip=ip,image_offset=0x4760+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    if i.flow_control==FlowControl.CALL:calls.append(dict(cs=0x476,ip=ip,image_offset=0x4760+ip,instruction=fmt.format(i)))
save('statistics_exit_dispatch',rows);save('calls',calls)
spec=[('stats_vectors_objects_guards',0x27fe3,0x28012,0x22f,0x232,[16]*6),('stats_frame_rate',0x28012,0x28037,0x246,0x249,[16]*4),('stats_near_heap',0x28037,0x28067,0x25d,0x260,[16]*3),('stats_far_heap',0x28067,0x2809a,0x274,0x277,[16]*3),('stats_extended_memory',0x2809a,0x280c8,0x292,0x295,[16]*3),('stats_tile_slots',0x280c8,0x2810e,0x2b4,0x2b7,[16,32,32,16,16]),('stats_object_slots',0x2810e,0x28154,0x2d6,0x2d9,[16,32,32,16,16]),('stats_sound_slots',0x28154,0x2819a,0x2f8,0x2fb,[16,32,32,16,16])]
fields=[];formats=[]
for name,a,e,push,call,widths in spec:
    raw=b[a:e];assert raw[-1]==0 and b'\0' not in raw[:-1];text=raw[:-1].decode('ascii');tokens=re.findall(r'%(?:l)?[ud]',text);assert len(tokens)==text.count('%') and [32 if x.startswith('%l') else 16 for x in tokens]==widths
    i=decoded[push];assert i.op0_kind==OpKind.IMMEDIATE16 and i.immediate16==a-0x27710
    j=decoded[call];assert j.op0_kind==OpKind.FAR_BRANCH16 and (j.far_branch_selector,j.far_branch16)==(0x11ee,0x7e0) and i.next_ip==call
    fields.append(dict(name=name,start=a,end_exclusive=e,length=e-a,type='NUL_ASCII_variadic_statistics_format',status='PARTIAL',range_sha256=sha(raw)))
    formats.append(dict(name=name,start=a,end_exclusive=e,format=text,push_cs=0x476,push_ip=push,call_ip=call,target_cs=0x11ee,target_ip=0x7e0,conversion_tokens=';'.join(tokens),argument_bits=';'.join(map(str,widths)),variadic_payload_bytes=sum(widths)//8,scope='format grammar and exact caller operands; formatter body not executed'))
assert sum(f['length'] for f in fields)==439 and fields[0]['start']==163811 and fields[-1]['end_exclusive']==164250
save('data_fields',fields);save('format_catalog',formats)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),functions=[dict(name='statistics_exit_dispatch',start=0x4930,end_exclusive=0x4a73,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in rows),instructions=len(rows))],typed_bytes=439,fields=len(fields),format_calls=8,scope='full static local CFG and eight exact format PUSH/FAR CALL sites; no formatter, game statistics or termination executed',formatter_closed=False,natural_statistics_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
