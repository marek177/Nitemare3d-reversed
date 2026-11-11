"""Verify initial timer base, setter slot and fixed CS operand references."""
import csv,hashlib,json,struct,sys
from pathlib import Path
image,old,dep,out=map(Path,sys.argv[1:]);sys.path.insert(0,str(dep.resolve()))
from iced_x86 import Decoder,Formatter,FormatterSyntax,InstructionInfoFactory,Register,MemorySizeExt
b=image.read_bytes();sha=hashlib.sha256(b).hexdigest();assert sha=='e2efde70af9637fb233bcf4a8cb1cec736ffd81fa90998cc47834b3f54f1f297'
base=0x15bf0;assert b[0x190ab:0x190b1]==bytes.fromhex('2e891eb934c3');assert b[0x190a9:0x190ab]==bytes.fromhex('204e')
slot=base+0x2020+2*0x43;assert struct.unpack_from('<H',b,slot)[0]==0x34bb
refs=[];factory=InstructionInfoFactory();fmt=Formatter(FormatterSyntax.INTEL)
for r in json.loads(old.read_text()):
    if r['cs']!=0x15bf:continue
    raw=bytes.fromhex(r['bytes']);a=r['image_offset'];assert b[a:a+len(raw)]==raw
    ins=Decoder(16,raw,ip=r['ip']).decode();assert not ins.is_invalid and ins.len==len(raw)
    for m in factory.info(ins).used_memory():
        if m.segment==Register.CS and m.base==Register.NONE and m.index==Register.NONE and m.displacement<=0x34ba and m.displacement+MemorySizeExt.size(m.memory_size)>0x34b9:
            refs.append(dict(image_offset=a,bytes=raw.hex(),instruction=fmt.format(ins),access_enum=m.access,width=MemorySizeExt.size(m.memory_size),status='PARTIAL'))
out.mkdir(parents=True,exist_ok=True)
with (out/'fixed_references.csv').open('w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(refs[0]));w.writeheader();w.writerows(refs)
result=dict(image_sha256=sha,field_image_start=0x190a9,field_image_end_exclusive=0x190ab,initial_word=20000,setter_image_start=0x190ab,setter_image_end_exclusive=0x190b1,setter_input='BX without local range validation',selector=0x43,selector_word_image=slot,fixed_references=len(refs),default_caller_quotient=1191180//20000,default_low8_helper_ax=(1191180//20000)&255,global_alias_writes_excluded=False,setter_natural_callers_closed=False,zero_input_natural_reachability_proven=False,new_deep_verified_bytes=0,runtime_tests=0)
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
