"""python audit_win110_trig_callers.py EXE ASM FIXUPS_DIR DECODER_DIR OUT"""
import collections,csv,hashlib,json,re,struct,sys
from pathlib import Path
exe,asm,fixups,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,OpKind
b=exe.read_bytes();sha=lambda x:hashlib.sha256(x).hexdigest();assert sha(b)=='12fe5168783446275802e0e947898261b5eca6b88288f3a895fc1faa4c544481'
ne=struct.unpack_from('<I',b,60)[0];w=lambda p:struct.unpack_from('<H',b,p)[0];segments={}
for i in range(1,w(ne+28)+1):
    sector,size,flags,_=struct.unpack_from('<4H',b,ne+w(ne+34)+(i-1)*8)
    if sector and not flags&1:
        a=sector<<w(ne+50);segments[i]=(a,b[a:a+(size or 65536)])
targets={0xecac:'sin',0xecf8:'cos',0xed44:'tangent_magnitude',0xed90:'angle_lookup'}
rx=re.compile(r'^([0-9A-Fa-f]{4}):([0-9A-Fa-f]{4})\s+((?:[0-9A-Fa-f]{2}\s+)+)');starts={};fmt=Formatter(FormatterSyntax.INTEL);near=[]
for lineno,line in enumerate(asm.read_text(encoding='utf-8-sig').splitlines(),1):
    m=rx.match(line)
    if not m:continue
    seg,ip=int(m[1],16),int(m[2],16);raw=bytes.fromhex(m[3]);assert seg in segments and segments[seg][1][ip:ip+len(raw)]==raw
    ins=Decoder(16,raw,ip=ip).decode();assert not ins.is_invalid and ins.len==len(raw)
    starts[(seg,ip)]=dict(segment=seg,offset=ip,bytes=raw.hex(),instruction=fmt.format(ins),asm_line=lineno)
    if seg==3 and ins.flow_control==FlowControl.CALL and ins.op0_kind==OpKind.NEAR_BRANCH16 and ins.near_branch16 in targets:near.append(dict(source=ip,target=ins.near_branch16))
sites={(int(r['segment']),int(r['source_offset'])):r for r in csv.DictReader((fixups/'expanded_sites.csv').open())};edges=[];context=[]
for r in csv.DictReader((fixups/'far_candidates.csv').open()):
    if r['effective_internal_segment']!='3' or not r['effective_internal_offset']:continue
    target=int(r['effective_internal_offset'])
    if target not in targets:continue
    seg,ip=int(r['segment']),int(r['instruction_offset']);raw=bytes.fromhex(r['raw_instruction']);assert raw[0]==0x9a and struct.unpack_from('<H',raw,1)[0]==target and segments[seg][1][ip:ip+5]==raw
    assert (seg,ip) in starts and int(r['fixup_source_offset'])==ip+3
    site=sites[(seg,ip+3)];assert site['source_type']=='2' and site['width']=='2' and site['target']=='internal_selector:3'
    edges.append(dict(function=targets[target],caller_segment=seg,call_offset=ip,file_offset=segments[seg][0]+ip,raw_instruction=raw.hex(),selector_fixup_offset=ip+3,fixup_record_index=site['record_index'],target_segment=3,target_offset=target,inventory_boundary_verified=True,runtime_selector='UNRESOLVED'))
    ordered=sorted(x for x in starts if x[0]==seg);index=ordered.index((seg,ip))
    for key in ordered[max(0,index-3):index+4]:context.append(dict(call_offset=ip,**starts[key]))
assert len(edges)==6
v=segments[3][1]
for p,h in {0xe567:'ff36ea4b',0xe573:'a3464c',0xe576:'ff36ea4b',0xe582:'a3484c',0x6dc0:'66ff7606',0x6dc9:'83c404'}.items():assert v[p:p+len(bytes.fromhex(h))]==bytes.fromhex(h)
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('far_callers',edges),('caller_instruction_context',context)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
s=dict(exe_sha256=sha(b),asm_sha256=sha(asm.read_bytes()),expanded_sites_sha256=sha((fixups/'expanded_sites.csv').read_bytes()),far_candidates_sha256=sha((fixups/'far_candidates.csv').read_bytes()),validated_inventory_starts=len(starts),relocation_backed_far_edges=len(edges),edges_by_target=dict(collections.Counter(r['function'] for r in edges)),near_call_candidates_in_inventory=near,runtime_ds_closed=False,global_indirect_call_inventory_closed=False,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s,indent=2))
