"""python audit_pass1_dsp_status.py IMAGE INVENTORY DECODER_DIR OUT"""
import csv,hashlib,json,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};base=0xc2b0;fmt=Formatter(FormatterSyntax.INTEL);instructions=[];edges=[];starts=set();calls=[]
pending=[0x20];decoded={}
while pending:
    ip=pending.pop()
    if ip in decoded:continue
    assert 0x20<=ip<0xaa
    i=Decoder(16,b[base+ip:base+0xaa],ip=ip).decode();assert not i.is_invalid
    decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.near_branch_target)
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.next_ip)
for i in [decoded[ip] for ip in sorted(decoded)]:
    assert not i.is_invalid;raw=b[base+i.ip:base+i.next_ip];assert lookup[(0xc2b,i.ip)]['bytes']==raw.hex()
    starts.add(i.ip);instructions.append(dict(cs=0xc2b,ip=i.ip,image_offset=base+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):edges.append(dict(source=i.ip,target=i.near_branch_target,kind='branch'))
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):edges.append(dict(source=i.ip,target=i.next_ip,kind='fallthrough_or_returning_call'))
    if raw[0]==0x9a:calls.append(dict(ip=i.ip,target_segment=i.far_branch_selector,target_offset=i.far_branch16))
assert all(e['target'] in starts for e in edges) and instructions[-1]['ip']==0xa9
fields=[];formats=[]
for off,name in [(0x1740,'forced_DSP_status'),(0x1763,'forced_DSP_failure'),(0x1782,'auto_DSP_status'),(0x179d,'auto_DSP_fallback')]:
    a=0x27710+off;e=b.index(0,a)+1;text=b[a:e-1].decode('ascii')
    fields.append(dict(name=name,start=a,end_exclusive=e,length=e-a,type='NUL_ASCII_format_string',status='PARTIAL',range_sha256=sha(b[a:e])))
    rendered=text.replace('%x','ffff').replace('%d','-32768')
    formats.append(dict(name=name,ds_offset=off,text=text,conventional_16bit_max_bytes_including_nul=len(rendered)+1,local_buffer_bytes=64,crt_format_contract_closed=False))
for ip,target in [(0x5c,0x278c),(0x7f,0x278c),(0x91,0x278c)]:assert any(c['ip']==ip and c['target_segment']==0x11ee and c['target_offset']==target for c in calls)
assert any(c['ip']==0x9d and c['target_segment']==0x476 and c['target_offset']==0x78 for c in calls)
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('instructions',instructions),('cfg_edges',edges),('calls',calls),('data_fields',fields),('formats',formats)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),function_start=base+0x20,function_end_exclusive=base+0xaa,function_span_bytes=0x8a,decoded_code_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in instructions),instructions=len(instructions),unreached_bytes_in_span=[base+ip for ip in range(0x20,0xaa) if not any(i.ip<=ip<i.next_ip for i in decoded.values())],data_fields=len(fields),typed_bytes=sum(f['length'] for f in fields),natural_runtime_tests=0,new_deep_verified_bytes=0,hardware_detection_callee_contract_closed=False,crt_formatter_contract_closed=False)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
