"""Exact install/restore windows for vector63; these are fragments, not functions.
Usage: python audit_dos_vector63.py IMAGE DECODER_DIR OUT_DIR
"""
import csv,hashlib,json,sys
from pathlib import Path
image,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax
b=image.read_bytes();sha=hashlib.sha256(b).hexdigest();assert sha=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
base=0x15bf0;fmt=Formatter(FormatterSyntax.INTEL);rows=[]
windows=[('save_and_install',0x18a87,0x18aac),('restore_far_exit_fragment',0x18b88,0x18b9e),('restore_near_exit_fragment',0x18bd4,0x18bea)]
for name,a,end in windows:
    pos=a
    for ins in Decoder(16,b[a:end],ip=a-base):
        assert not ins.is_invalid
        rows.append(dict(window=name,image_offset=pos,cs=0x15bf,ip=ins.ip,bytes=b[pos:pos+ins.len].hex(),instruction=fmt.format(ins),status='PARTIAL'))
        pos+=ins.len
    assert pos==end
expected={0x18a8c:'b435b063cd21',0x18a92:'2e891e112e',0x18a97:'2e8c06132e',0x18a9c:'b425b063bae6300e1fcd21',0x18b8b:'b425b063',0x18b8f:'2e8b16112e2e8e1e132ecd21',0x18bd7:'b425b063',0x18bdb:'2e8b16112e2e8e1e132ecd21'}
for a,s in expected.items():assert b[a:a+len(bytes.fromhex(s))]==bytes.fromhex(s)
data=[dict(name='saved_previous_INT63_vector',start=base+0x2e11,end_exclusive=base+0x2e15,cs=0x15bf,cs_offset=0x2e11,type='FAR16_offset_segment',range_sha256=hashlib.sha256(b[base+0x2e11:base+0x2e15]).hexdigest(),initial_bytes=b[base+0x2e11:base+0x2e15].hex(),status='PARTIAL',pass320_membership='UNKNOWN')]
out.mkdir(parents=True,exist_ok=True)
for name,rs in [('instructions.csv',rows),('data_intervals.csv',data)]:
    with (out/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
r=dict(image_sha256=sha,windows=[dict(name=n,start=a,end_exclusive=e) for n,a,e in windows],fragment_instruction_count=len(rows),fragment_instruction_bytes=sum(e-a for _,a,e in windows),vector_number=0x63,installed_handler_cs=0x15bf,installed_handler_ip=0x30e6,installed_handler_image=0x18cd6,saved_pointer_image=base+0x2e11,saved_pointer_bytes=4,restore_sites=[0x18b99,0x18be5],vector_install_runtime_reached=False,caller_graph_complete=False,new_deep_verified_bytes=0,runtime_tests=0)
(out/'summary.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps(r,indent=2))
