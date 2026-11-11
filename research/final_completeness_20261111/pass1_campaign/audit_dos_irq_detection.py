"""IRQ probe caller, backed tables and recovered vector-installed handler.
Usage: python audit_dos_irq_detection.py IMAGE OLD_INSTRUCTIONS DECODER_DIR OUT_DIR
"""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,old,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,OpKind
b=image.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
base=0x15bf0;fmt=Formatter(FormatterSyntax.INTEL);out.mkdir(parents=True,exist_ok=True)
inventory_bytes=old.read_bytes();inventory_sha=hashlib.sha256(inventory_bytes).hexdigest();assert inventory_sha=='a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a'
historical={(r['cs'],r['ip']) for r in json.loads(inventory_bytes)};functions=[];edges=[]
spec=[('device_init',0x1a37d,0x1a44a,'c3'),('temporary_irq_handler',0x1b5f2,0x1b60e,'cf'),('dsp_read_byte',0x1b60e,0x1b62f,'c3'),('dsp_write_byte',0x1b62f,0x1b65c,'c3'),('irq_candidate_probe',0x1b65c,0x1b768,'c3')]
def save(name,rows):
    with (out/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
for name,start,end,ending in spec:
    rows=[];new=[];pos=start
    for ins in Decoder(16,b[start:end],ip=start-base):
        assert not ins.is_invalid
        rows.append(dict(image_offset=pos,cs=0x15bf,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins)))
        if (0x15bf,ins.ip) not in historical:new.append(pos)
        if ins.flow_control in (FlowControl.CALL,FlowControl.CONDITIONAL_BRANCH,FlowControl.UNCONDITIONAL_BRANCH):
            assert ins.op_kind(0)!=OpKind.FAR_BRANCH16
            edges.append(dict(function=name,source=pos,flow_control=ins.flow_control,target=base+ins.near_branch_target))
        pos+=ins.len
    assert pos==end and rows[-1]['bytes']==ending
    save(name+'.csv',rows);functions.append(dict(name=name,start=start,end_exclusive=end,instructions=len(rows),instruction_bytes=end-start,starts_absent_from_historical_inventory=new,status='PARTIAL'))
profiles=[]
for i in range(5):
    profiles.append(dict(index=i,mask_port=b[base+0x4767+i],mask_bit=b[base+0x476d+i],ivt_byte_offset=struct.unpack_from('<H',b,base+0x4772+2*i)[0],device_irq_code=b[base+0x477c+i],status='PARTIAL'))
assert [r['device_irq_code'] for r in profiles]==[7,5,3,2,10]
assert [r['mask_port'] for r in profiles]==[0x21]*4+[0xa1]
assert [r['mask_bit'] for r in profiles]==[0x80,0x20,8,4,4]
assert [r['ivt_byte_offset'] for r in profiles]==[0x3c,0x34,0x2c,0x28,0x1c8]
assert b[base+0x4767+5]==0 and b[base+0x477c+5]==0
save('profiles.csv',profiles)
fields=[]
for name,off,size,typ in [('selected_profile_index',0x4765,2,'WORD'),('mask_ports_with_sentinel',0x4767,6,'BYTE[5]+zero_BYTE'),('mask_bits',0x476d,5,'BYTE[5]'),('ivt_byte_offsets',0x4772,10,'WORD[5]'),('irq_codes_with_sentinel',0x477c,6,'BYTE[5]+zero_BYTE'),('saved_irq_vector',0x4782,4,'FAR16'),('saved_mask_byte',0x4786,1,'BYTE'),('probe_irq_seen',0x4787,2,'WORD')]:
    a=base+off;fields.append(dict(name=name,start=a,end_exclusive=a+size,type=typ,initial_bytes=b[a:a+size].hex(),range_sha256=hashlib.sha256(b[a:a+size]).hexdigest(),status='PARTIAL',pass320_membership='UNKNOWN'))
save('data_intervals.csv',fields);save('control_edges.csv',edges)
assert b[0x1b6c4:0x1b6d0]==bytes.fromhex('b8025a2689058cc826894502')
assert b[0x1a3b6:0x1a3c7]==bytes.fromhex('2e833ef02d007509e8a7137304b8ffffc3')
r=dict(image_sha256=h,instruction_inventory_sha256=inventory_sha,functions=functions,total_instruction_bytes=sum(f['instruction_bytes'] for f in functions),data_bytes=sum(f['end_exclusive']-f['start'] for f in fields),profile_count=len(profiles),temporary_handler_installed_ip=0x5a02,temporary_handler_image=0x1b5f2,temporary_handler_prior_inventory_starts=0,caller_checks_probe_cf=True,base_reset_after_failure=False,hardware_irq_reachability_proven=False,new_deep_verified_bytes=0,runtime_tests=0)
r['temporary_handler_prior_inventory_starts']=next(f['instructions']-len(f['starts_absent_from_historical_inventory']) for f in functions if f['name']=='temporary_irq_handler')
(out/'summary.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
