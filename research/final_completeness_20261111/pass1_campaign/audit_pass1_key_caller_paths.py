"""Direct caller inventory and exact bounded guard/argument windows.
Usage: python audit_pass1_key_caller_paths.py IMAGE INVENTORY DECODER_DIR OUT_DIR
"""
import csv,hashlib,json,sys
from pathlib import Path
image,old,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,FlowControl,OpKind
b=image.read_bytes();h=hashlib.sha256(b).hexdigest();assert h=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
rawinv=old.read_bytes();assert hashlib.sha256(rawinv).hexdigest()=='a38777df45fc271149d6c8e45ce35ee1d254822007af7fdc1d56f109fa5b979a'
fmt=Formatter(FormatterSyntax.INTEL);calls=[]
for r in json.loads(rawinv):
    raw=bytes.fromhex(r['bytes']);a=r['image_offset'];assert b[a:a+len(raw)]==raw and r['cs']*16+r['ip']==a
    ins=Decoder(16,raw,ip=r['ip']).decode();assert not ins.is_invalid and ins.len==len(raw)
    if ins.flow_control!=FlowControl.CALL:continue
    target=ins.far_branch_selector*16+ins.far_branch16 if ins.op_kind(0)==OpKind.FAR_BRANCH16 else r['cs']*16+ins.near_branch_target
    if target in (0xa306,0xf0aa):calls.append(dict(source_image=a,cs=r['cs'],ip=r['ip'],bytes=raw.hex(),instruction=fmt.format(ins),target_image=target,scope='direct encoded call in pinned inventory; not complete runtime caller graph'))
assert {(r['source_image'],r['target_image']) for r in calls}=={(0x143d,0xf0aa),(0xf0b9,0xa306)}
windows=[]
for name,a,e,cs in [('dispatcher_prefix',0x13f4,0x1444,0xf7),('wrapper_to_selector',0xf0aa,0xf0be,0xd29)]:
    for ins in Decoder(16,b[a:e],ip=a-cs*16):
        assert not ins.is_invalid;p=cs*16+ins.ip;windows.append(dict(window=name,image_offset=p,cs=cs,ip=ins.ip,bytes=b[p:p+ins.len].hex(),instruction=fmt.format(ins),status='PARTIAL'))
out.mkdir(parents=True,exist_ok=True)
for name,rows in [('direct_calls',calls),('bounded_instructions',windows)]:
    with (out/(name+'.csv')).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
result=dict(image_sha256=h,inventory_sha256=hashlib.sha256(rawinv).hexdigest(),direct_calls=calls,key_route_item_bounds=[25,28],index_formula='(item_code-25) & FFFFh',index_bounds_on_this_route=[0,3],caller_argument_layout='dispatcher pushes item SI then zero-extended record BYTE; wrapper reads item at BP+8',DS_context='inherited; no default-DS establishment before selector on this route',global_caller_graph_complete=False,natural_dispatch_entry_DS_proven=False,byte_status_promotions=0,runtime_tests=0,new_deep_verified_bytes=0)
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(direct_call_edges=len(calls),key_route_item_bounds=[25,28],index_bounds=[0,3],global_DS_context_closed=False)))
