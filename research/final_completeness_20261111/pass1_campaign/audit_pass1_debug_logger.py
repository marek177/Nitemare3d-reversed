"""python audit_pass1_debug_logger.py IMAGE INVENTORY DECODER_DIR OUT"""
import csv,hashlib,json,sys
from pathlib import Path
image,inventory,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,OpKind
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());bykey={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL)
code=[];edges=[];decoded={};base=0x4760
for i in Decoder(16,b[base+0x78:base+0xcd],ip=0x78):
    assert not i.is_invalid
    raw=b[base+i.ip:base+i.next_ip];r=bykey[(0x476,i.ip)];assert raw.hex()==r['bytes']
    decoded[i.ip]=i;code.append(dict(cs=0x476,ip=i.ip,image_offset=base+i.ip,bytes=raw.hex(),instruction=fmt.format(i)))
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
        edges.append(dict(source=i.ip,target=i.near_branch_target,kind='branch'))
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):
        edges.append(dict(source=i.ip,target=i.next_ip,kind='fallthrough_or_returning_call'))
assert code[-1]['ip']==0xcc and decoded[0xcc].flow_control==FlowControl.RETURN
assert all(e['target'] in decoded for e in edges)
fields={};callers=[]
def field(off,name,typ='NUL_ASCII_string'):
    a=0x27710+off;e=b.index(0,a)+1
    assert all(c in (9,10,13) or 32<=c<127 for c in b[a:e-1])
    fields[a]=dict(name=name,start=a,end_exclusive=e,length=e-a,type=typ,status='PARTIAL',range_sha256=sha(b[a:e]))
    return b[a:e-1].decode('ascii')
for off,name in [(0x82e,'debug_first_open_mode'),(0x830,'debug_later_open_mode'),(0x832,'debug_filename')]:field(off,name)
assert b[0x27f3c:0x27f4c]==b'\0\0w\0a\0debug.txt\0'
fields[0x27f3c]=dict(name='debug_saved_stream_word',start=0x27f3c,end_exclusive=0x27f3e,length=2,type='mutable_WORD_stream_result_and_open_mode_state',status='PARTIAL',range_sha256=sha(b[0x27f3c:0x27f3e]))
for r in old:
    is_near=r['cs']==0x476 and r['mnemonic']=='call' and r['operands']=='0x78'
    is_far=r['mnemonic']=='lcall' and r['operands']=='0x476, 0x78'
    if not (is_near or is_far):continue
    p=r['image_offset'];raw=bytes.fromhex(r['bytes']);assert b[p:p+len(raw)]==raw
    ci=Decoder(16,raw,ip=r['ip']).decode();assert ci.len==len(raw) and not ci.is_invalid
    if is_near:assert ci.near_branch_target==0x78
    else:assert ci.far_branch16==0x78 and ci.far_branch_selector==0x476
    before=r['ip']-(1 if is_near else 0)
    if is_near:assert bykey[(r['cs'],before)]['bytes']=='0e'
    prev=[x for x in old if x['cs']==r['cs'] and x['ip']+len(bytes.fromhex(x['bytes']))==before]
    assert len(prev)==1
    q=prev[0];pi=Decoder(16,bytes.fromhex(q['bytes']),ip=q['ip']).decode()
    literal=pi.op0_kind in (OpKind.IMMEDIATE16,OpKind.IMMEDIATE8TO16) and q['mnemonic']=='push'
    off=pi.immediate16 if literal else None
    text=field(off,'debug_format_%04x'%off) if literal else ''
    callers.append(dict(cs=r['cs'],ip=r['ip'],image_offset=p,bytes=raw.hex(),call_kind='push_cs_near' if is_near else 'far',argument_instruction=q['bytes'],format_ds_offset=off if literal else '',literal=literal,text=text))
assert len(callers)==17 and sum(r['literal'] for r in callers)==16
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('instructions',code),('cfg_edges',edges),('callers',callers),('data_fields',sorted(fields.values(),key=lambda f:f['start']))]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),function_start=base+0x78,function_end_exclusive=base+0xcd,function_bytes=85,instructions=len(code),direct_callers=17,literal_callers=16,dynamic_callers=1,data_fields=len(fields),typed_bytes=sum(f['length'] for f in fields.values()),caller_ds_closed=False,crt_callee_semantics_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
