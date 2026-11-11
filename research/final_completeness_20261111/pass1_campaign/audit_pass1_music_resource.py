"""python audit_pass1_music_resource.py IMAGE INVENTORY DECODER_DIR SND_DAT OUT"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,inventory,dep,snd,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl
b=image.read_bytes();asset=snd.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest()
assert sha(b)=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
assert sha(asset)=='f3434984d315531602d32285cb8ff55990bba786f5fb37f53710e88379388614'
old=json.loads(inventory.read_text());lookup={(r['cs'],r['ip']):r for r in old};fmt=Formatter(FormatterSyntax.INTEL);pending=[0x298];decoded={};instructions=[];edges=[];calls=[]
while pending:
    ip=pending.pop()
    if ip in decoded:continue
    assert 0x298<=ip<0x39d
    i=Decoder(16,b[0xc2b0+ip:0xc64d],ip=ip).decode();assert not i.is_invalid;decoded[ip]=i
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.near_branch_target)
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):pending.append(i.next_ip)
for ip,i in sorted(decoded.items()):
    raw=b[0xc2b0+ip:0xc2b0+i.next_ip];assert lookup[(0xc2b,ip)]['bytes']==raw.hex()
    instructions.append(dict(cs=0xc2b,ip=ip,image_offset=0xc2b0+ip,bytes=raw.hex(),instruction=fmt.format(i)))
    if i.flow_control in (FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):edges.append(dict(source=ip,target=i.near_branch_target,kind='branch'))
    if i.flow_control not in (FlowControl.RETURN,FlowControl.UNCONDITIONAL_BRANCH):edges.append(dict(source=ip,target=i.next_ip,kind='fallthrough_or_returning_call'))
    if raw[0]==0x9a:calls.append(dict(ip=ip,target_segment=i.far_branch_selector,target_offset=i.far_branch16))
assert instructions[-1]['ip']==0x39c
assert b[0x278be:0x278c6]==b'snd.dat\0' and b[0x28ee0:0x28ee4]==b'\0'*4
records=[];tracks=[]
for n in range(32):
    length,offset=struct.unpack_from('<Hi',asset,n*6);a=abs(offset);e=a+length
    assert 0<=a<=e<=len(asset)
    payload=asset[a:e];kind='zero_length' if not length else 'MThd_signature' if payload.startswith(b'MThd') else 'IBK_signature' if payload.startswith(b'IBK\x1a') else 'unidentified'
    midi_format=track_count=division=''
    if kind=='MThd_signature':
        header_length=struct.unpack_from('>I',payload,4)[0];assert header_length==6
        midi_format,track_count,division=struct.unpack_from('>HHH',payload,8);p=14
        for t in range(track_count):
            assert payload[p:p+4]==b'MTrk';size=struct.unpack_from('>I',payload,p+4)[0];end=p+8+size;assert end<=len(payload)
            tracks.append(dict(resource_id=n,track=t,asset_start=a+p,asset_end_exclusive=a+end,length=size,sha256=sha(payload[p+8:end])));p=end
        assert p==len(payload)
    records.append(dict(id=n,directory_offset=6*n,length=length,signed_offset=offset,payload_start=a,payload_end_exclusive=e,kind=kind,sha256=sha(payload),midi_format=midi_format,declared_tracks=track_count,division=division))
field=dict(name='music_resource_buffer_pointer',start=0x28ee0,end_exclusive=0x28ee4,length=4,type='mutable_FAR16_buffer_pointer_initial_NULL',status='PARTIAL',range_sha256=sha(b[0x28ee0:0x28ee4]))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('instructions',instructions),('cfg_edges',edges),('far_calls',calls),('data_fields',[field]),('snd_directory_first32',records),('midi_track_chunks',tracks)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
s=dict(image_sha256=sha(b),inventory_sha256=sha(inventory.read_bytes()),snd_path=str(snd),snd_sha256=sha(asset),snd_bytes=len(asset),function_start=0xc548,function_end_exclusive=0xc64d,function_span_bytes=261,instruction_bytes=sum(len(bytes.fromhex(r['bytes'])) for r in instructions),instructions=len(instructions),typed_bytes=4,parsed_directory_records=32,midi_resources=sum(r['kind']=='MThd_signature' for r in records),midi_track_chunks=len(tracks),midi_event_streams_validated=False,all_asset_bytes_classified=False,callee_contracts_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
