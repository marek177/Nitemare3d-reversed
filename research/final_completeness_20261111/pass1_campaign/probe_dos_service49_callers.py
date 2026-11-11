"""Bounded negative caller evidence, not a proof of unreachability.
Usage: python probe_dos_service49_callers.py IMAGE INSTRUCTIONS DECODER_DIR OUT_DIR
"""
import csv,hashlib,json,sys
from pathlib import Path
image,old,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,OpKind
b=image.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
fmt=Formatter(FormatterSyntax.INTEL);rows=json.loads(old.read_text(encoding='utf-8'));calls=[];constants=[]
for i,r in enumerate(rows):
    a=r['image_offset'];raw=bytes.fromhex(r['bytes']);assert b[a:a+len(raw)]==raw and r['cs']*16+r['ip']==a
    ins=Decoder(16,raw,ip=r['ip']).decode();assert not ins.is_invalid and ins.len==len(raw)
    if ins.flow_control==FlowControl.CALL:
        if ins.op_kind(0)==OpKind.FAR_BRANCH16:target=ins.far_branch_selector*16+ins.far_branch16
        else:target=r['cs']*16+ins.near_branch_target
        if target in (0x17f39,0x18cd6):calls.append(dict(image_offset=a,cs=r['cs'],ip=r['ip'],bytes=raw.hex(),instruction=fmt.format(ins),target_image=target,scope='direct encoded target in unrelocated image'))
    if raw==bytes.fromhex('b449') or (len(raw)==3 and raw[0]==0xb8 and raw[2]==0x49):
        nxt=rows[i+1] if i+1<len(rows) else None
        contiguous=nxt is not None and nxt['cs']==r['cs'] and nxt['image_offset']==a+len(raw)
        constants.append(dict(image_offset=a,cs=r['cs'],ip=r['ip'],bytes=raw.hex(),instruction=fmt.format(ins),contiguous_next_bytes=nxt['bytes'] if contiguous else '',scope='literal AH/AX selector candidate, not service49 proof'))
out.mkdir(parents=True,exist_ok=True)
for name,rs,fields in [('direct_call_candidates.csv',calls,['image_offset','cs','ip','bytes','instruction','target_image','scope']),('ah49_immediate_candidates.csv',constants,['image_offset','cs','ip','bytes','instruction','contiguous_next_bytes','scope'])]:
    with (out/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rs)
result=dict(image_sha256=h,instruction_inventory_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),validated_instruction_starts=len(rows),literal_cd63_offsets=[i for i in range(len(b)-1) if b[i:i+2]==bytes.fromhex('cd63')],direct_calls_to_service49_or_dispatcher=len(calls),literal_ah49_candidates=len(constants),service49_table_word_image=0x15bf0+0x2020+2*0x49,service49_table_initial_bytes=b[0x15bf0+0x2020+2*0x49:0x15bf0+0x2020+2*0x49+2].hex(),indirect_pointer_callers_resolved=False,external_or_generated_code_excluded=False,service49_unreachability_proven=False,counter_bound_proven=False,new_deep_verified_bytes=0,runtime_tests=0)
assert result['service49_table_initial_bytes']=='4923'
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
