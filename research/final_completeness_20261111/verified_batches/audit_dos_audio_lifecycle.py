"""Decode lifecycle candidates, direct callers and port-output helper.
Usage: python audit_dos_audio_lifecycle.py IMAGE INSTRUCTIONS DECODER_DIR OUT_DIR
"""
import csv,hashlib,json,sys
from pathlib import Path
image,old,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,OpKind
b=image.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
base=0x15bf0;fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
spec=[('audio_install',0x18a6d,0x18b0b,'cb'),('audio_uninstall',0x18b56,0x18bbf,'cb'),('port388_write',0x19497,0x194c2,'c3'),('port_callback_setter',0x1948a,0x19497,'c3'),('pit_divisor_setter',0x1a25a,0x1a28f,'c3'),('timer_base_setter',0x190ab,0x190b1,'c3')]
functions=[];callers=[];edges=[]
def save(p,rows,fields=None):
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
for name,a,end,last in spec:
    rows=[];pos=a
    for ins in Decoder(16,b[a:end],ip=a-base):
        assert not ins.is_invalid
        rows.append(dict(image_offset=pos,cs=0x15bf,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)))
        if ins.flow_control in (FlowControl.CALL,FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
            edges.append(dict(function=name,source=pos,flow_control=ins.flow_control,target=base+ins.near_branch_target,scope='direct encoded local control target'))
        elif ins.flow_control==FlowControl.INDIRECT_CALL:edges.append(dict(function=name,source=pos,flow_control=ins.flow_control,target='',scope='UNRESOLVED callback'))
        pos+=ins.len
    assert pos==end and rows[-1]['bytes']==last
    save(out/(name+'.csv'),rows)
    functions.append(dict(name=name,start=a,end_exclusive=end,instructions=len(rows),instruction_bytes=end-a,status='PARTIAL'))
for r in json.loads(old.read_text(encoding='utf-8')):
    raw=bytes.fromhex(r['bytes']);a=r['image_offset'];assert b[a:a+len(raw)]==raw
    ins=Decoder(16,raw,ip=r['ip']).decode();assert not ins.is_invalid and ins.len==len(raw)
    if ins.flow_control!=FlowControl.CALL:continue
    t=ins.far_branch_selector*16+ins.far_branch16 if ins.op_kind(0)==OpKind.FAR_BRANCH16 else r['cs']*16+ins.near_branch_target
    for name,start,_,_ in spec:
        if t==start:callers.append(dict(callee=name,image_offset=a,cs=r['cs'],ip=r['ip'],bytes=raw.hex(),instruction=fmt.format(ins),target_image=t,status='PARTIAL'))
save(out/'direct_callers.csv',callers);save(out/'control_edges.csv',edges)
data=[dict(name='port_output_callback',start=base+0x3896,end_exclusive=base+0x389a,type='FAR16_guarded_by_segment_word',range_sha256=hashlib.sha256(b[base+0x3896:base+0x389a]).hexdigest(),status='PARTIAL',pass320_membership='UNKNOWN'),dict(name='saved_previous_INT08_vector',start=base+0xa,end_exclusive=base+0xe,type='FAR16',range_sha256=hashlib.sha256(b[base+0xa:base+0xe]).hexdigest(),status='PARTIAL',pass320_membership='UNKNOWN')]

for name,start,end,typ in [('timer_base_rate',base+0x34b9,base+0x34bb,'WORD_initial_20000'),('pit_update_gate',base+0x201e,base+0x2020,'WORD'),('pit_ratio_pair',base+0x2db4,base+0x2db8,'two_WORD_quotient_copies')]:
    data.append(dict(name=name,start=start,end_exclusive=end,type=typ,range_sha256=hashlib.sha256(b[start:end]).hexdigest(),status='PARTIAL',pass320_membership='UNKNOWN'))
save(out/'data_intervals.csv',data)
result=dict(image_sha256=h,functions=functions,total_instruction_bytes=sum(f['instruction_bytes'] for f in functions),direct_callers=len(callers),init_callers=sum(r['callee']=='audio_install' for r in callers),shutdown_callers=sum(r['callee']=='audio_uninstall' for r in callers),port_helper_callers=sum(r['callee']=='port388_write' for r in callers),port_helper_callback_target_closed=False,initialization_loop_256_requires_callback_ax_preservation=True,runtime_reachability_proven=False,new_deep_verified_bytes=0,runtime_tests=0)
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
