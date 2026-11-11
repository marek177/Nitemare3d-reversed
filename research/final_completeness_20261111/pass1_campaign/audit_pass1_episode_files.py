"""python audit_pass1_episode_files.py IMAGE INVENTORY DECODER_DIR GAME_DIR OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,game,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
b=image.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);pending=[0x336];decoded={};instructions=[];edges=[]
while pending:
    ip=pending.pop()
    if ip in decoded:continue
    assert 0x336<=ip<0x3ca
    i=Decoder(16,b[0x2770+ip:0x2b3a],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.near_branch_target)
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.next_ip)
for ip,i in sorted(decoded.items()):
    raw=b[0x2770+ip:0x2770+i.next_ip];assert lookup[(0x277,ip)]['bytes']==raw.hex()
    instructions.append(dict(cs=0x277,ip=ip,image_offset=0x2770+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_returning_call'))
assert instructions[-1]['ip']==0x3c9
fields=[];bindings=[]
for prefix_off,format_off,dest,ip in [(0x28c,0x291,0x627c,0x34c),(0x296,0x29b,0x628c,0x35e),(0x2a0,0x2a6,0x629c,0x370)]:
    for off,typ in [(prefix_off,'NUL_ASCII_filename_prefix'),(format_off,'NUL_ASCII_sprintf_format')]:
        a=0x27710+off;e=b.index(0,a)+1
        fields.append(dict(name='episode_literal_%04x'%off,start=a,end_exclusive=e,length=e-a,type=typ,status='PARTIAL',range_sha256=sha(b[a:e])))
    prefix=b[0x27710+prefix_off:b.index(0,0x27710+prefix_off)].decode('ascii')
    assert b[0x27710+format_off:0x27710+format_off+5]==b'%s%d\0'
    bindings.append(dict(prefix=prefix,prefix_ds=prefix_off,format_ds=format_off,destination_ds=dest,call_ip=ip,conventional_signed16_max_output_with_nul=len(prefix)+6+1))
assets=[];selections=[]
for episode in (1,2,3):
    p=game/('MAP.%d'%episode);data=p.read_bytes();count=struct.unpack_from('<H',data)[0]
    assert len(data)==514+count*8192
    assets.append(dict(episode=episode,path=str(p),length=len(data),sha256=sha(data),declared_levels=count,header_bytes=514,level_record_bytes=8192,header_sha256=sha(data[:514]),size_equation_verified=True))
    for level in range(count):
        a=0x27710+0x15be+10*episode+level
        selections.append(dict(episode=episode,level=level,selection_image=a,selected_id=b[a],outside_nominal_level_0_9=level>=10,source='static address expression plus actual MAP count; no natural execution'))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('instructions',instructions),('cfg_edges',edges),('data_fields',fields),('filename_bindings',bindings),('map_assets',assets),('music_index_crosscheck',selections)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),function_start=0x2aa6,function_end_exclusive=0x2b3a,function_span_bytes=148,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in instructions),instructions=len(instructions),typed_bytes=sum(f['length'] for f in fields),map_level_counts=[r['declared_levels'] for r in assets],music_address_cases=len(selections),music_nominal_row_overhang_cases=sum(r['outside_nominal_level_0_9'] for r in selections),runtime_tests=0,new_deep_verified_bytes=0,crt_format_contract_closed=False,natural_episode_level_domains_closed=False)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
